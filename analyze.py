from pprint import pformat

from parser.hny.types import *
import sys


allowed_ops: set[str] = {
    'IntLiteral IntLiteral',
    # 'StringLiteral StringLiteral', # not allowed yet
    'CharLiteral CharLiteral',
    'CharLiteral IntLiteral',
    'IntLiteral CharLiteral',
}


# noinspection DuplicatedCode
def warn(text, node, src):
    node = node.node
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
def err(text, node, src):
    node = node.node
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


class Stack(list):
    def push(self, value):
        self.append(value)
        return

    def get(self, i: int = 0):
        return self[-1 - i]


# I made ability of nested frames especially for namespaces and classes
class Frame:
    def __init__(self, fn: Function | None, globf, src: str):
        self.fn = fn
        self.locals = {}
        self.global_frame = globf
        self.src = src

    def add_global(self, *a, **k):
        return self.global_frame.add_local(*a, **k)

    def add_local(self, name, types):  # `types` instead of `type` because of shadowing
        self.locals[name] = types

    def is_present(self, name):
        return name in self.locals or name in self.global_frame.locals

    def is_local(self, name):
        return name in self.locals

    def check_present(self, name, _node):
        return name in self.locals or (name in self.global_frame.locals if self.global_frame else False)

    def check(self, node, name, types):
        types = types.as_literal() if isinstance(types, Type) else types
        try:
            return self.locals[name].as_literal() == types
        except KeyError:
            try:
                return self.global_frame.check(node, name, types)
            except KeyError:
                self.panic(node, name, self.src)
            except AttributeError:
                self.panic(node, name, self.src)

    def panic(self, node, name, src):
        err("variable name used before reference: %s\nLocals: %s\nGlobals: %s" %
            (name, pformat(self.locals).replace("\n", "\n    "),
             pformat(self.global_frame.locals).replace("\n", "\n    ") if self.global_frame else ""),
            node, src)

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
    funcs: dict
    globf: Frame
    imports: list[str]
    frame: Frame | None
    src: str

    def __init__(self, prod, src):
        self.prod = prod
        self.funcs: dict[str, Function] = {}
        self.globf = Frame(None, None, src)
        self.imports = []
        self.frame = None
        self.src = src

    def collect(self, node=None):
        if node is None:
            node = self.prod

        frame = self.frame or self.globf

        if isinstance(node, Root):  # it is root node

            status = 0

            for line in node.lines:  # collect all from its members
                status += self.collect(line)

            return status

        if isinstance(node, Var):  # it is a new variable definition with initialization
            if frame.check_present(node.name, node):
                if not frame.check(node, node.name, node.type):
                    err("Variable `%s` type don't match" % node.name, node, self.src)
                    return 1
                else:
                    warn("Variable `%s` already defined" % node.name, node, self.src)
            else:
                frame.add_local(node.name, node.type)  # we are not interested in value.
                #                                      # We need only check it later

        if isinstance(node, Def):  # it is a new variable definition without initialization
            if frame.check_present(node.name, node):
                if not frame.check(node, node.name, node.type):
                    err("Variable `%s` type don't match" % node.name, node, self.src)
                    return 1
                else:
                    warn("Variable `%s` already defined" % node.name, node, self.src)
            else:  # local scope
                self.frame.add_local(node.name, node.type)

        if isinstance(node, Function):  # it is a function definition
            if self.frame:
                err("Nested functions not allowed", node.node, self.src)
                return 1

            self.funcs[node.name] = node  # register new function
            self.frame = Frame(node, self.globf, self.src)  # setup new frame

            status = 0

            for line in node.lines:  # and check the body recursively
                status += self.collect(line)

            self.funcs[self.frame.fn.name].frame = self.frame
            self.frame = None  # clear frame

            return status

        if isinstance(node, Forever):  # it is forever loop

            status = 0

            # check the body recursively
            for line in node.lines:
                status += self.collect(line)

            return status

        if isinstance(node, Foreach):  # it is for each loop
            # register new variable
            if self.frame.is_present(node.name):
                if not self.frame.check(node, node.name, node.type):
                    err("Variable `%s` type don't match" % node.name, node.type, self.src)
                    return 1
                else:
                    warn("Variable `%s` already defined" % node.name, node, self.src)
            else:
                self.frame.add_local(node.name, node.type)

            status = 0

            # and check the body recursively
            for line in node.lines:
                status += self.collect(line)

            return status

        if isinstance(node, Forwhile):  # it is while loop

            status = 0

            # check the body recursively
            for line in node.lines:
                status += self.collect(line)

            return status

        if isinstance(node, Forclike):  # it is C for loop
            self.collect(node.a)  # check its header

            status = 0

            # and check the body recursively
            for line in node.lines:
                status += self.collect(line)

            return status

        return 0

    def check(self, node=None):
        if node is None:
            node = self.prod

        frame = self.frame or self.globf

        # print(">>>", node, "\b\n<<<\n\n")

        if isinstance(node, NameLiteral):
            frame.check_present(node.value, node.node)
            if not frame.is_present(node.value):
                return 1
            node.type = frame.get(node.value, node).as_literal()

        if isinstance(node, CharLiteral):
            node.value = repr(ord(eval(node.value)))
            node.type = IntLiteral(node.node, node.value)

        if isinstance(node, Call):
            if node.name not in self.funcs:
                frame.panic(node, node.name, self.src)
            node.type = self.funcs[node.name].rtype.as_literal()

        if isinstance(node, Binop):
            status = 0
            status += self.check(node.op1) or 0
            status += self.check(node.op2) or 0
            if status:
                return 1
            if (node.op1.type.as_literal().raw() + " " + node.op2.type.as_literal().raw()) not in allowed_ops:
                err("Operation types aren't allowed: `%s` and `%s`" %
                    (repr(node.op1.type.as_literal()), repr(node.op2.type.as_literal())),
                    node, self.src)
                return 1

        if isinstance(node, Return):
            self.check(node.rvalue)
            if self.frame.fn.rtype.as_literal() != node.rvalue.type.as_literal():
                err("Wrong return type: expected `%s`, got `%s" % (
                    repr(self.frame.fn.rtype), repr(node.rvalue.type)
                ), node.rvalue, self.src)
                return 1

        if isinstance(node, Root):  # it is root node
            status = 0

            for line in node.lines:  # collect all from its members
                status += self.check(line)

            return status

        if isinstance(node, Var):  # it is a new variable definition with initialization
            if self.frame:
                if not self.frame.check(node, node.name, node.type.as_literal()):
                    err("Variable type don't match", node.node, self.src)
                    return 1
            else:
                if not self.globf.check(node, node.name, node.type.as_literal()):
                    err("Variable type don't match", node.type.as_literal(), self.src)
                    return 1
            if isinstance(node.value, Call):
                node.value.type = self.funcs[node.value.name].rtype
            if not node.type.as_literal() == node.value.type.as_literal():
                err("Variable type and expression type don't match: `%s` and `%s`" % (
                    repr(node.type.as_literal()) + " " + repr(node.type),
                    repr(node.value.type.as_literal())
                ), node.value, self.src)
                return 1

        if isinstance(node, Def):  # it is a new variable definition without initialization
            if not self.frame.check(node, node.name, node.type):
                err("Variable type don't match", node.type, self.src)
                return 1

        if isinstance(node, Function):  # it is a function definition
            self.frame = self.funcs[node.name].frame

            status = 0

            for line in node.lines:  # and check the body recursively
                status += self.check(line)

            self.frame = None  # clear frame

            return status

        if isinstance(node, Forever):  # it is forever loop

            status = 0

            # check the body recursively
            for line in node.lines:
                status += self.check(line)

            return status

        if isinstance(node, Foreach):  # it is for each loop
            # register new variable
            if not self.frame.check(node, node.name, node.type):
                err("Variable type don't match", node.type, self.src)
                return 1

            status = 0

            # and check the body recursively
            for line in node.lines:
                status += self.check(line)

            return status

        if isinstance(node, Forwhile):  # it is while loop

            status = 0

            # check the body recursively
            for line in node.lines:
                status += self.check(line)

            return status

        if isinstance(node, Forclike):  # it is C for loop
            self.check(node.a)  # check its header

            status = 0

            # and check the body recursively
            for line in node.lines:
                status += self.check(line)

            return status

        if isinstance(node, Assign):
            self.check(node.value)
            node.lvalue.type = frame.get(node.lvalue.name, node.lvalue.node).as_literal()
            if not frame.is_present(node.lvalue.name):
                return 1
            if node.lvalue.type.as_literal() != node.value.type.as_literal():
                err("lvalue and rvalue types don't match: `%s` and `%s`" %
                    (node.lvalue.type.as_literal(), node.value.type.as_literal()), node, self.src)
                return 1

        return 0
