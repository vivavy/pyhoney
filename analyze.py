from parser.hny.types import *
from analyzer.hny.consts import *
import sys

__all__ = ["check"]


def warn(text, node, src):
    print("Warning:", text, file=sys.stderr)


def err(text, node, src):
    print("Error:", text, file=sys.stderr)
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


class Analyzer:
    def __init__(self, prod):
        self.prod = prod
        self.funcs = {}
        self.globals = []
        self.imports = []
        self.format = None
        self.frames = Stack()

    # check is recursive function
    def check(self, node: list | Func | Expr | Format | Line | Import | None = None, src=""):
        n: list | Func | Expr | Format | Line | Import
        if node is None:
            node = self.prod

        print("[*] Analyzer.check:", node)

        try:
            # noinspection PyUnboundLocalVariable
            node[0]
        except TypeError:
            return

        for n in node:
            print("[*] Analyzer.check:", n)
            if Func == type(n):
                if n.name in list(self.funcs.keys()):
                    return ("function already defined", n.node,
                            self.funcs[n.name].node)  # compiler will handle it by selfs

                self.funcs[n.name] = n  # so we saved data about function

                # save the frame (`push' makes possible nested functions,
                # but for now they are not supported)
                self.frames.push({"vars": {}, "fname": n.name})

                # and we need to check it recursively
                for c in n.body:
                    status = self.check(c, src)

                    if status:
                        return status

                self.frames.pop()

            if Line == type(n):
                if n.op == Base.ignore:
                    continue  # it's a comment

            if Format == type(n):
                self.format = formats[n.module.value]

            if Import == type(n):
                self.imports.append(n.module.value)

            if Expr == type(n):
                if not self.frames:  # if we have not appeared in any context.
                    if n.op == Base.assign:  # Defining with initialized value? Ok!
                        # save this value as global variable
                        if isinstance(n.a.a, Symbol):
                            # suppression because linter got mad
                            # noinspection PyUnresolvedReferences
                            self.globals.append(n.a.a.value)
                        else:
                            return "assigning to non-constant lvalue out of function", n.node
                    else:
                        return "prohibited construction out of function", n.node
                else:  # if we are in any function's context
                    if n.op == Base.assign:  # Defining or assigning? Easy, b×tch!
                        if isinstance(n.a, Expr):  # Linter bulls this line without a reason
                            if n.a.op == Base.define:
                                if n.a.a.value in self.frames.get():
                                    if n.a.b == self.frames.get()["vars"]:
                                        warn("variable already defined", n.node, src)  # i can't invent sth better
                                    else:
                                        return "variable already defined with other type", n.node
                                else:
                                    self.frames.get()["vars"].append(n.a.b)  # register type of new local
                            else:
                                return "unknown error, perhaps bug in parser", n.node  # this situation is impossible
                        else:
                            return "unknown error, perhaps bug in parser", n.node  # this situation is impossible
                    elif n.op == Base.ret:
                        if isinstance(n.a, Symbol):
                            if n.a.type == Base.name:
                                # it is a symbol
                                if n.a.value not in self.frames.get()["vars"] and n.a.value not in self.globals:
                                    return "variable name used before reference", n.node
                                if self.frames.get()["vars"][n.a.value] != \
                                        self.funcs[self.frames.get()["fname"]].rtype.as_literal():
                                    return "return type don't match", n.node
                            # it is a literal
                            if n.a.type == self.funcs[self.frames.get()["fname"]].rtype.as_literal():
                                # types haven't matched
                                return "return type don't match", n.a.node
                        if isinstance(n.a, Expr):
                            if n.a.op == Base.call:
                                self.check(n.a, src)
                                if n.a.a in self.funcs:
                                    if self.funcs[n.a.a.value].rtype != self.funcs[self.frames.get()["fname"]].rtype:
                                        return "return type don't match", n.node
                                else:  # TODO: make 2-passes analyzer
                                    print("[*] analyzer: can't test for rtype function `" + n.a.a.value + "'")
                            if n.a.op == Base.ret:
                                return "nested returns are not allowed, perhaps you mean `leave'?", n.node
                            if Base.plus <= n.a.op <= Base.incs:
                                self.check(n.a, src)
                                if n.a.a.type.base != self.funcs[self.frames.get()["fname"]].rtype:
                                    return "return type don't match", n.node

        return
