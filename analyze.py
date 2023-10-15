from parser.hny.types import *
from analyzer.hny.consts import *
from parglare.parser import LRStackNode
import sys

__all__ = ["check"]


# noinspection DuplicatedCode
def warn(text, node: LRStackNode, src):
    startsym = node.start_position
    lineno = len(src[:startsym].split("\n")) - 1
    line = src.split("\n")[lineno]
    pos = startsym - len("\n".join(src.split("\n")[:lineno]))
    length = node.end_position - node.start_position
    print("Warning at line %d\n%s\n    %s" % (lineno, text, line), file=sys.stderr)
    print("    " + " " * pos + "~" * length, file=sys.stderr)


# noinspection DuplicatedCode
def err(text, node: LRStackNode, src):
    startsym = node.start_position
    lineno = len(src[:startsym].split("\n")) - 1
    line = src.split("\n")[lineno]
    pos = startsym - len(src[:startsym][::1].split("\n", 1)[0]) + 1
    length = node.end_position - node.start_position
    print("Error at line %d\n%s\n\t%s" % (lineno + 1, text, line), file=sys.stderr)
    print("\t" + " " * pos + "~" * length, file=sys.stderr)
    sys.exit(2)


def check(prod, src):
    analyzer = Analyzer(prod)

    status = analyzer.check(src=src)

    if status:
        err(*status, src)  # i can't invent sth better

    # P.S.: it was a lie. I just invented a cool method without weird functions, but i too lazy to imlement it

    return


class Stack(list):
    def push(self, value):
        self.append(value)
        return

    def get(self, i: int = 0):
        return self[-1 - i]


class Frame:
    def __init__(self, fname, globs, src):
        self.fn = fname
        self.locals = {}
        self.globals = globs
        self.src = src

    def add_local(self, definition, typ=None):
        if typ:
            self.locals[definition.value] = typ
        self.locals[definition.a] = definition.b

    def is_present(self, name):
        return name in self.locals or name in self.globals

    def check(self, d):
        try:
            return self.locals[d.a] == d.b
        except KeyError:
            try:
                return self.globals[d.a] == d.b
            except KeyError:
                err("variable name used before reference", d.node, self.src)

    def get(self, name, node):
        try:
            return self.locals[name]
        except KeyError:
            try:
                return self.globals[name]
            except KeyError:
                err("variable name used before reference", node, self.src)


class Analyzer:
    prod: list
    funcs: dict[str, Func]
    globals: dict[str, Type]
    imports: list[str]
    format: str | None
    frame: Frame | None

    def __init__(self, prod):
        self.prod = prod
        self.funcs = {}
        self.globals = {}
        self.imports = []
        self.format = None
        self.frame = None

    # check is recursive function
    def check(self, node: object | None = None, src=""):
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
                self.frame = Frame(n.name, self.globals, src)

                print("\tstack saved, checkin' body")

                # and we need to check it recursively
                status = self.check(n.body, src)

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
                            self.globals[n.a.a.value] = n.a.b

                            # checkin' expression
                            status = self.check(n.b, src)

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
                                self.globals[n.a.value] = n.b
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
                        status = self.check(n.b.lines, src)

                        if status:
                            return status

                    if n.op == Base.assign:  # Defining or assigning? Easy, b×tch!
                        print("\tassignment found:", n)
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
                                if self.frame.is_present(n.a.value):
                                    return "variable name used before reference", n.node
                                if self.frame.get(n.a.value, n.a) != self.funcs[self.frame.fn].rtype.as_literal():
                                    return "return type don't match", n.node
                            # it is a literal
                            if n.a.type == self.funcs[self.frame.fn].rtype:
                                # types haven't matched
                                return "return type don't match", n.a.node
                        else:
                            if n.a.op == Base.call:
                                self.check(n.a, src)
                                if n.a.a.value in self.funcs:
                                    if self.funcs[n.a.a.value].rtype.as_literal() != \
                                            self.funcs[self.frame.fn].rtype.as_literal():
                                        return "return type don't match", n.node
                                else:  # TODO: make 2-passes analyzer
                                    print("[*] analyzer: can't test for rtype function `" + n.a.a.value + "'")
                            if n.a.op == Base.ret:
                                return "nested returns not allowed, did you mean `leave'?", n.node
                            if Base.plus <= n.a.op <= Base.incs or n.a.op == Base.cast:
                                self.check(n.a, src)
                                if n.a.a.type != self.funcs[self.frame.fn].rtype.as_literal():
                                    return "return type don't match", n.node

        return
