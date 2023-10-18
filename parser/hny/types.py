from functions import *
from sugar import overload


class Node:
    def __init__(self):
        ...  # self.type = self.__class__  # allowed syntax: if n.type is Root: …


# Root node type
class Root(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.lines = n[0]

        while None in self.lines:
            self.lines.remove(None)

    def __repr__(self):
        return "\n\n".join(tuple(repr(i) for i in self.lines))


class Format(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.format = n[1].value

    def __repr__(self):
        return "Format " + self.format


class Import(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.module = n[1].value

    def __repr__(self):
        return "Import " + self.module


class FuncArgs(Node):
    names: list[str]
    types: list

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
        self.rtype = n[5][1] if n[5] else Type.new(Type.void, _, -1)
        self.lines = n[7]
        self.frame = None

    def __repr__(self):
        return "Function " + self.name + ";\n\t" + "\n\t".join(tuple(self.args.names)) + "\n\n\t" \
            + "\n\t".join(tuple(repr(i) for i in self.args.types)) + " returns " + repr(self.rtype) + \
            "\n\n\t" + "\n\t".join(tuple(repr(i) for i in self.lines))


class Def(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[0].value
        self.type = n[2]

    def __repr__(self):
        return "Def " + self.name + " " + repr(self.type)


class Var(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[0].name
        self.type = n[0].type
        self.value = n[2]

    def __repr__(self):
        return "Var " + self.name + " " + repr(self.type) + " = " + repr(self.value)


class Type(Node):
    # base types
    error, int, str, u8, i8, u16, i16, u32, i32, u64, i64, uint, char, wchar, wstr, c_str, c_wstr = tuple(range(17))
    void = int

    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.base = Type.to_base(n[0].value)
        self.array = (int(n[1][1].value) if n[1][1] else 0) if n[1] else -1

    def __repr__(self):
        return "Type " + Type.to_name(self.base) + \
            ("[]" if self.array == 0 else "[" + str(self.array) + "]" if self.array > 0 else "")

    def as_literal(self):
        return (IntLiteral(self.node, "") if self.array >= 0 or self.base not in "str wstr".split()
                else StringLiteral(self.node, ""))

    @staticmethod
    def new(base, node, array):
        return Type(node, [NameLiteral(node, Type.to_name(base)), [None, IntLiteral(node, str(array)), None]])

    @staticmethod
    def to_name(base: int):
        return "error int str u8 i8 u16 i16 u32 i32 u64 i64 uint char wchar wstr c_str c_wstr".split()[base]

    @staticmethod
    def to_base(name: str):
        if name == 'void':
            return 1
        return "error int str u8 i8 u16 i16 u32 i32 u64 i64 uint char wchar wstr c_str c_wstr".split().index(name)


class Forever(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.lines = n[2]

        while None in self.lines:
            self.lines.remove(None)

    def __repr__(self):
        return "Forever\n\t" + "\n\t".join(tuple(self.lines))


class Foreach(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[1].name
        self.type = n[1].type
        self.array = n[3]
        self.lines = n[5]

        while None in self.lines:
            self.lines.remove(None)

    def __repr__(self):
        return "For each " + self.name + " " + repr(self.type) + " " + repr(self.array) + "\n\n\t" + \
            "\n\t".join(repr(i) for i in self.lines)


class Forwhile(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.cond = n[1]
        self.lines = n[3]

        while None in self.lines:
            self.lines.remove(None)

    def __repr__(self):
        return "For while " + repr(self.cond) + "\n\n\t" + "\n\t".join(self.lines)


class Forclike(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.a = n[1]
        self.b = n[3]
        self.c = n[5]
        self.lines = n[7]

        while None in self.lines:
            self.lines.remove(None)

    def __repr__(self):
        return "For clike " + repr(self.a) + " " + repr(self.b) + " " + repr(self.c) + "\n\n\t\t" + \
            "\n\t\t".join(tuple(repr(i) for i in self.lines))


class Leave(Node):
    def __init__(self, _, _n):
        super().__init__()
        self.node = _

    def __repr__(self):
        return "Leave"


class Call(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[0].value
        self.args = unpack(n[2])
        self.type = None

    def __repr__(self):
        return "Call " + self.name + "(" + ", ".join(tuple(repr(i) for i in self.args)) + ")"


class Cast:
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.expr = n[0]
        self.type = n[2]

    def __repr__(self):
        return "Cast " + repr(self.expr) + " " + repr(self.type)


class Return(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.rvalue = n[1]

    def __repr__(self):
        return "Return " + repr(self.rvalue)


class Lvalue(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.name = n[0].value
        self.index = (n[1][1] if n[1][1] else 0) if n[1] else -1

    def __repr__(self):
        return "Lvalue " + self.name + \
            ("[" + str(self.index) + "]" if self.index else "@")


class Assign(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.lvalue = n[0]
        self.value = n[2]
        self.type = self.value.type

    def __repr__(self):
        return "Assign " + repr(self.lvalue) + " = " + repr(self.value)


class Range(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.start = n[0]
        self.end = n[2]
        self.type = Type(_, [NameLiteral(_, "int"), ["[", IntLiteral(_, "0"), "]"]])

    def __repr__(self):
        return "Range " + repr(self.start) + " " + repr(self.end)


class Binop(Node):
    ops = "+ - * / & @ % ^ | << >> < >".split()

    def __init__(self, _, op1, op2, opr: int):
        super().__init__()
        self.node = _
        self.op1 = op1
        self.op2 = op2
        self.opr = opr
        self.type = self.op1.type

    def __repr__(self):
        return "Binop " + Binop.ops[self.opr] + " " + repr(self.op1) + " " + repr(self.op2)


class Unop(Node):
    ops = "- ~ ! $ ++ --".split()

    prefix = 1
    suffix = 2

    def __init__(self, _, op, opr: int, pos: int):
        super().__init__()
        self.node = _
        self.op = op
        self.opr = opr
        self.pos = pos
        self.type = self.op.type

    def __repr__(self):
        return "Unop " + "error prefix suffix".split()[self.pos] + " " + repr(self.op)


class Literal(Node):
    def __init__(self, _, n):
        super().__init__()
        self.node = _
        self.value = n
        self.type = self

    def __repr__(self):
        return self.__class__.__name__.removesuffix("Literal" if not self.value else "") + \
            ("[" + self.value + "]" if self.value else "")

    def as_literal(self):
        return self.__class__(self.node, "")

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__

    def raw(self):
        return self.__class__.__name__


class CharLiteral(Literal):
    @overload
    def as_literal(self):
        return IntLiteral(self.node, self.value)


class StringLiteral(Literal):
    ...


class IntLiteral(Literal):
    ...


class NameLiteral(Literal):
    ...
