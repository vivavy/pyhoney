from pprint import pformat

from parser.hny.types import *
from parglare.parser import LRStackNode
import sys


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

    def check_present(self, name, node):
        try:
            assert name in self.locals or (name in self.global_frame.locals if self.global_frame else False)
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
    funcs: dict
    globf: Frame
    imports: list[str]
    frame: Frame | None
    src: str

    def __init__(self, prod, src):
        self.prod = prod
        self.funcs = dict()
        self.globf = Frame(None, None, src)
        self.imports = []
        self.frame = None
        self.src = src

    def collect(self, node=None):
        if node is None:
            node = self.prod

        print(":::", node)
        print("\tFrame", ("don't", "")[bool(self.frame)], "present")

        if isinstance(node, Root):  # it is root node
            for line in node.lines:  # collect all from its members
                self.collect(line)

        if isinstance(node, Var):  # it is a new variable definition with initialization
            print("%", self.frame)
            if self.frame:  # check save target
                self.frame.add_local(node.name, node.type)  # we are not interested in value.
                #                                           # We need only check it later
                print("*", self.frame.locals)
            else:  # global scope
                self.globf.add_local(node.name, node.type)
                print("^", self.globf.locals)

        if isinstance(node, Def):  # it is a new variable definition without initialization
            if self.frame:  # local scope
                self.frame.add_local(node.name, node.type)
            else:  # global scope
                self.globf.add_local(node.name, node.type)

        if isinstance(node, Function):  # it is a function definition
            if self.frame:
                err("Nested functions not allowed", node.node, self.src)
            else:
                self.funcs[node.name] = node  # register new function
                self.frame = Frame(node, self.globf, self.src)  # setup new frame

                for line in node.lines:  # and check the body recursively
                    self.collect(line)

                self.funcs[self.frame.fn.name].frame = self.frame
                self.frame = None  # clear frame

        if isinstance(node, Forever):  # it is forever loop
            # check the body recursively
            for line in node.lines:
                self.collect(line)

        if isinstance(node, Foreach):  # it is for each loop
            # register new variable
            self.frame.add_local(node.name, node.type)
            # and check the body recursively
            for line in node.lines:
                self.collect(line)

        if isinstance(node, Forwhile):  # it is while loop
            # check the body recursively
            for line in node.lines:
                self.collect(line)

        if isinstance(node, Forclike):  # it is C for loop
            self.collect(node.a)  # check its header
            # and check the body recursively
            for line in node.lines:
                self.collect(line)
