from sugar import *

Symbol_t = Expr_t = object


class Data(object):
    ...


# consts
class Base:
    integer = 0
    string = 1
    name = 2
    char = 3
    array = 4
    void = 5
    type = 6


    plus = 0
    minus = 1
    mul = 2
    div = 3
    land = 4
    mmul = 5
    mod = 6
    xor = 7
    lor = 8
    shl = 9
    shr = 10
    lt = 11
    gt = 12
    dec = 13
    inc = 14
    decp = 15
    decs = 16
    incp = 17
    incs = 18
    index = 19
    iter = 20
    cast = 21
    range = 22
    assign = 23
    call = 24
    define = 25
    ret = 26
    foreach = 27
    forever = 28
    ignore = 29

    ops = "+ - * / & @ % ^ | << >> < > -- ++ --p --s ++p ++s <- # =? .. = !! . <? .* >< !@".split()
    tps = "INT STR SYM CHR ARR NIL TYP".split()
    typs = "int str symbol char array null type".split()


class VarData(Data):
    def __init__(self, dtype, readonly=False):
        self.type = dtype
        self.ro = readonly


class FuncData(Data):
    def __init__(self, rtype, argtypes):
        self.rtype = rtype
        self.atypes = argtypes


class Type:
    def __init__(self, base: int, data: Data | dict, array=False):
        self.base = base
        self.data = data
        self.array = array

    def as_literal(self):
        if self.array:
            return Base.integer
        if self.base in "u8 i8 u16 i16 u32 i32 u64 i64 int uint char wchar".split():
            return Base.integer
        if self.base in "str wstr bytes words".split():
            return Base.string

    def __str__(self):
        return Base.tps[self.base] + ("*" if self.array else "")

    def __eq__(self, other):
        return self.base == other.base and self.array == other.array


class Expr:
    def __init__(self, node, op1, op2, op: int):
        self.node = node
        self.op = op
        self.a = self.op1 = self.x = op1
        self.b = self.op2 = self.y = op2

    @overload
    def __str__(self):
        return "Expr " + Base.ops[self.op] + "\n\t" + str(self.a).replace("\n", "\n\t") + "\n\t" + \
            str(self.b).replace("\n", "\n\t")

    @overload
    def __repr__(self):
        return "Expr " + Base.ops[self.op] + "\n\t" + str(self.a).replace("\n", "\n\t") + "\n\t" + \
            str(self.b).replace("\n", "\n\t")


class Line:
    def __init__(self, node, op1: Symbol_t | Expr_t, op2: Symbol_t | Expr_t | None, op: int):
        self.node = node
        self.op = op
        self.a = self.op1 = self.x = op1
        self.b = self.op2 = self.y = op2

    @overload
    def __str__(self):
        return "Line " + Base.ops[self.op] + "\n\t" + str(self.a).replace("\n", "\n\t") + "\n\t" + \
            str(self.b).replace("\n", "\n\t")

    @overload
    def __repr__(self):
        return "Line " + Base.ops[self.op] + "\n\t" + str(self.a).replace("\n", "\n\t") + "\n\t" + \
            str(self.b).replace("\n", "\n\t")


class Func:
    def __init__(self, node, rtype, name, argnames, argtypes, body):
        self.node = node
        self.rtype = rtype
        self.name = name
        self.argtypes = argtypes
        self.argnames = argnames
        self.body = body

    @overload
    def __str__(self):
        # print("[*] parser: Func.__repr__:", self.argnames, self.argtypes)
        return "%s %s(%s) {\n    %s\n}" % (str(self.rtype), self.name.value,
                                           self.strargs(),
                                           ("\n".join(tuple(str(i) for i in self.body))).replace("\n", "\n\t"))

    @overload
    def __repr__(self):
        # print("[*] parser: Func.__repr__:", self.argnames, self.argtypes)
        return "%s %s(%s) {\n    %s\n}" % (str(self.rtype), self.name.value,
                                           self.strargs(),
                                           ("\n".join(tuple(str(i) for i in self.body))).replace("\n", "\n\t"))

    def strargs(self) -> str:
        r = ""

        for i in range(len(self.argtypes)):
            r += str(self.argtypes[i]) + " " + self.argnames[i].value + ", "

        return r[:-2]


class Body:
    def __init__(self, lines):
        self.lines = lines

    def __str__(self):
        return "{\n    %s\n}" % ("\n".join(tuple(str(i) for i in self.lines))).replace("\n", "\n\t")


class Import:
    def __init__(self, module):
        self.module = module

    @overload
    def __str__(self):
        return "import " + str(self.module)

    @overload
    def __repr__(self):
        return "import " + str(self.module)


class Format:
    def __init__(self, module):
        self.module = module

    @overload
    def __str__(self):
        return "format " + str(self.module)

    @overload
    def __repr__(self):
        return "format " + str(self.module)


class Symbol:
    def __init__(self, node, name: str, value: str, stype: int):
        self.node = node
        self.name = name
        self.value = value
        self.type = stype

    @overload
    def __str__(self):
        return "Symbol " + Base.tps[self.type] + " " + repr(self.value)

    @overload
    def __repr__(self):
        return "Symbol " + Base.tps[self.type] + " " + repr(self.value)
