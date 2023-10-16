from pprint import pformat

from parser.hny.types import *
from analyzer.hny.consts import *
from parglare.parser import LRStackNode
import sys

__all__ = ["check"]


# noinspection DuplicatedCode
def warn(text, node: LRStackNode, src):
    startsym = node.start_position
    lineno = len(src[:startsym].split("\n")) - 1
    line: str = src.split("\n")[lineno]
    linepos = len("\n".join(src.split("\n")[:lineno]))
    pos = startsym - linepos - 3
    # length = node.end_position - node.start_position
    print("\nWarning at line %d: %s\n│   %s" % (lineno + 1, text, line.lstrip()), file=sys.stderr)
    print("│   " + " " * pos + "▲", file=sys.stderr)
    print("╰───" + "─" * pos + "╯\n", file=sys.stderr)


# noinspection DuplicatedCode
def err(text, node: LRStackNode, src):
    startsym = node.start_position
    lineno = len(src[:startsym].split("\n")) - 1
    line: str = src.split("\n")[lineno]
    linepos = len("\n".join(src.split("\n")[:lineno]))
    pos = startsym - linepos - 3
    # length = node.end_position - node.start_position
    print("\nError at line %d: %s\n│   %s" % (lineno + 1, text, line.lstrip()), file=sys.stderr)
    print("│   " + " " * pos + "~" * (node.end_position - node.start_position), file=sys.stderr)
    print("│   " + " " * pos + "▲", file=sys.stderr)
    print("╰───" + "─" * pos + "╯", file=sys.stderr)
    sys.exit(2)


def check(prod, src):
    analyzer = Analyzer(prod, src)

    status = analyzer.check()

    if status:
        err(*status, src)  # i can't invent sth better

    # P.S.: it was a lie. I just invented a cool method without weird functions, but I too lazy to imlement it

    return


class Stack(list):
    def push(self, value):
        self.append(value)
        return

    def get(self, i: int = 0):
        return self[-1 - i]


class Frame:
    def __init__(self, fname, globf, src):
        self.fn = fname
        self.locals = {}
        self.global_frame = globf
        self.src = src

    def add_global(self, *a, **k):
        return self.global_frame.add_local(*a, **k)

    def add_local(self, definition, typ=None):
        print("[*] analyzer: add_local:", definition)
        if typ:
            self.locals[definition.value if isinstance(definition, Symbol) else definition] = typ
        if isinstance(definition.a.value, Symbol):
            # noinspection PyUnresolvedReferences
            definition.b.value = Type(definition.b.value.value, {}, False).as_literal()
        self.locals[definition.a.value] = Type(definition.b.base
                                               if isinstance(definition.b, Type) else definition.b.value, {},
                                               definition.b.array if isinstance(definition.b, Type) else False)

    def is_present(self, node):
        if node is Symbol:
            return node.value in self.locals or (self.global_frame.is_present(node.value) if
                                                 self.global_frame else False)
        else:
            return node in self.locals or (self.global_frame.is_present(node) if
                                           self.global_frame else False)

    def check_present(self, node):
        try:
            assert node.value in self.locals or \
                   (self.global_frame.is_present(node.value) if self.global_frame else False)
        except AssertionError:
            self.panic(node, self.src)

    def check(self, d):
        try:
            return self.locals[d.a] == d.b
        except KeyError:
            try:
                return self.global_frame.check(d)
            except KeyError:
                self.panic(d, self.src)
            except AttributeError:
                self.panic(d, self.src)

    def panic(self, d, src):
        err("variable name used before reference: %s\nLocals: %s\nGlobals: %s" %
            (d.value, pformat(self.locals).replace("\n", "\n    "),
             pformat(self.global_frame.locals).replace("\n", "\n    ")), d.node, src)

    def get(self, name, node):
        try:
            return self.locals[name]
        except KeyError:
            try:
                return self.global_frame.get(name, node)
            except KeyError:
                err("variable name used before reference: %s" % name, node, self.src)


class Analyzer:
    prod: list
    funcs: dict[str, Func]
    globals: Frame
    imports: list[str]
    format: str | None
    frame: Frame | None
    src: str

    def __init__(self, prod, src):
        self.prod = prod
        self.funcs = {}
        self.global_frame = Frame(None, None, src)
        self.imports = []
        self.format = None
        self.frame = None
        self.src = src

    # check is recursive function
    def check(self, node: object | None = None):
        src = self.src

        if node is None:
            node = self.prod

        # print("[*] Analyzer.check:", node)

        if not isinstance(node, list):
            return

        for n in node:
            if Func == type(n):
                print("[*] analyzer: func found:", n)
                if n.name in self.funcs:
                    # compiler will handle it by self
                    return "function already defined", n.node, self.funcs[n.name].node

                self.funcs[n.name] = n  # so we saved data about function
                print("\tdata saved")

                # save the frame
                self.frame = Frame(n.name, self.global_frame, src)

                print("\tstack saved, checkin' body")

                # and we need to check it recursively
                status = self.check(n.body)

                if status:
                    return status

                self.frame = None  # clear frame

            # is it a comment?
            if isinstance(n, Line):
                if n.op == Base.ignore:
                    print("[%] analyzer: comment found")
                    continue  # skip

            if Format == type(n):
                print("[*] analyzer: format found:", n.module.value)
                self.format = formats[n.module.value]

            if Import == type(n):
                print("[*] analyzer: import found:", n.module.value)
                self.imports.append(n.module.value)

            if isinstance(n, Expr) or isinstance(n, Line):
                print("[^] analyzer: found evaluatable or executable structure")
                if not self.frame:  # if we have not appeared in any context.
                    print("\tframe does not present")
                    if n.op == Base.assign:  # Defining with initialized value? Ok!
                        print("[*] analyzer: initialized global")
                        # save this value as global variable
                        if isinstance(n.a.a, Symbol):
                            # suppression because linter got mad
                            # noinspection PyUnresolvedReferences
                            self.global_frame.add_local(n.a)

                            # checkin' expression
                            status = self.check(n.b)

                            if status:
                                return status
                        else:
                            return "assigning to non-constant lvalue out of function", n.node

                    elif n.op == Base.define:  # Without? Sure!
                        print("[*] analyzer: uninitialized global")
                        # save this value as global variable
                        if isinstance(n.a, Symbol):
                            # Suppression because linter got mad.
                            # This needed for a linter, always true
                            if isinstance(n.b, Type):
                                self.global_frame.add_local(n)
                        else:
                            return "assigning to non-constant lvalue out of function", n.node
                    else:
                        return "prohibited construction out of function", n.node

                else:  # if we are in any function's context
                    print("\tframe presents")
                    if n.op == Base.foreach:
                        print("[*] analyzer: foreach found: ", n.a)
                        # noinspection PyTypeChecker
                        self.frame.add_local(n.a.a)

                        # check the body
                        status = self.check(n.b.lines)

                        if status:
                            return status

                    if n.op == Base.assign:  # Defining or assigning? Easy, b×tch!
                        print("\tassignment found:", n)
                        # noinspection PyUnresolvedReferences
                        if n.a is Expr:
                            if self.frame.is_present(n.a.a.value):
                                if self.frame.check(n.a):
                                    warn("variable already defined", n.node, src)  # i can't invent sth better

                                else:
                                    return "variable already defined with other type", n.node
                            else:
                                self.frame.add_local(n.a)  # register new local
                        if n.a is Symbol:
                            if self.frame.is_present(n.a.a.value):
                                if self.frame.check(n.a):
                                    warn("variable already defined", n.node, src)  # i can't invent sth better

                                else:
                                    return "variable already defined with other type", n.node
                            else:
                                self.frame.add_local(n.a)  # register new local

                        if n.a.op == Base.index:
                            if isinstance(n.a.b, Symbol):
                                if n.a.b.type == Base.name:
                                    if self.frame.get(n.a.b.value, n.a.b).as_literal() != Base.integer:
                                        return "array index must be integer", n.node

                                elif n.a.b.type != Base.integer:
                                    return "array index must be integer", n.node

                    elif n.op == Base.ret:
                        print("[*] analyzer: return found:", n)
                        if isinstance(n.a, Symbol):
                            if n.a.type == Base.name:
                                # it is a symbol
                                self.frame.check(Expr(n.a, n.a.value,
                                                      Type(self.funcs[self.frame.fn].rtype.as_literal(),
                                                           {}, False), Base.define))
                                if self.frame.get(n.a.value, n.a) != self.funcs[self.frame.fn].rtype.as_literal():
                                    return "return type don't match", n.node
                            # it is a literal
                            if n.a.type == self.funcs[self.frame.fn].rtype:
                                # types haven't matched
                                return "return type don't match", n.a.node
                        else:
                            if n.a.op == Base.call:
                                self.check(n.a)
                                if n.a.a.value in self.funcs:
                                    if self.funcs[n.a.a.value].rtype.as_literal() != \
                                            self.funcs[self.frame.fn].rtype.as_literal():
                                        return "return type don't match", n.node
                                else:  # TODO: make 2-passes analyzer
                                    print("[*] analyzer: can't test for rtype function `" + n.a.a.value + "'")
                            if n.a.op == Base.ret:
                                return "nested returns not allowed, did you mean `leave'?", n.node
                            if Base.plus <= n.a.op <= Base.incs or n.a.op == Base.cast:
                                self.check(n.a)
                                if n.a.a.type != self.funcs[self.frame.fn].rtype.as_literal():
                                    return "return type don't match", n.node

        return
