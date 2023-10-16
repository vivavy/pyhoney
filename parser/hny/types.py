from functions import *


class Node:
    def __init__(self):
        self.type = self.__class__  # allowed syntax: if n.type is Root: …


# Root node type
class Root(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.lines = n[0]


class Format(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.format = n[1].value


class Import(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.module = n[1].value


class FuncArgs(Node):
    def __init__(self):
        super().__init__()
        self.names = []
        self.types = []


class Function(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[1].value
        self.args = FuncArgs
        self.args.names, self.args.types = dearg(unpack(n[3]))
        self.rtype = n[5][1].base.value if n[5] else Type.new(Type.int, _, False)
        self.body = n[7]


class Def(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[0].value
        self.type = n[2]


class Var(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[0].name
        self.type = n[0].type
        self.value = n[2]


class Type(Node):
    # base types
    error, int, str, u8, i8, u16, i16, u32, i32, u64, i64, uint, char, wchar, wstr, c_str, c_wstr = tuple(range(17))
    void = int

    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.base = Type.to_base(n[0].value)
        self.array = n[1][2] if n[1] else -1

    @staticmethod
    def new(base, node, array):
        return Type(node, [NameLiteral(node, Type.to_name(base)), [None, IntLiteral(node, str(array)), None]])

    @staticmethod
    def to_name(base: int):
        return "error int str u8 i8 u16 i16 u32 i32 u64 i64 uint char wchar wstr c_str c_wstr".split()[base]

    @staticmethod
    def to_base(name: str):
        if name == 'void': return 1
        return "error int str u8 i8 u16 i16 u32 i32 u64 i64 uint char wchar wstr c_str c_wstr".split().index(name)


class Forever(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.lines = n[2]


class Foreach(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[1].name
        self.type = n[1].type
        self.array = n[3]
        self.lines = n[5]


class Forwhile(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.cond = n[1]
        self.lines = n[3]


class Forclike(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.a = n[1]
        self.b = n[3]
        self.c = n[5]
        self.lines = n[7]


class Leave(Node):
    def __init__(self, _, _n):
        super().__init__()
        self.node = _


class Call(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[0]
        self.args = unpack(n[2])


class Cast(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.expr = n[0]
        self.type = n[2]


class Return(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.rvalue = n[1]


class Lvalue(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.expr = n


class Assign(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.lvalue = n[0]
        self.value = n[2]


class Range(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.start = n[0]
        self.end = n[2]


class Literal(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.value = n


class CharLiteral(Literal):
    ...


class StringLiteral(Literal):
    ...


class IntLiteral(Literal):
    ...


class NameLiteral(Literal):
    ...
