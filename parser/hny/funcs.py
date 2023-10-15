from pprint import pprint, pformat

from parser.hny.types import *
from functions import *


def f_char(_, n):
    return Symbol(_, "", n, Base.char)


def f_string(_, n):
    return Symbol(_, "", n, Base.string)


def f_int(_, n):
    return Symbol(_, "", n, Base.integer)


def f_name(_, n):
    return Symbol(_, "", n, Base.name)


def f_range(_, n):
    return Expr(_, n[0], n[2], Base.range)


def f_ignore(_, n):
    return n[0]


def f_cast(_, n):
    return Expr(_, n[0][0], n[0][2], Base.cast)


def f_assign(_, n):
    return Expr(_, n[0], n[2], Base.assign)


def f_binop(_, n):
    return Expr(_, n[0], n[2], Base.ops.index(n[1]))


def f_punop(_, n):
    return Expr(_, n[1], None, Base.ops.index(n[0] + "x"))


def f_sunop(_, n):
    return Expr(_, n[0], None, Base.ops.index("x" + n[1]))


def f_geti(_, n):
    return n[1]


def f_getv(_, n):
    if n[1]:
        return Expr(_, n[0], n[1], Base.index)
    return n[0]


def f_ret(_, n):
    return Expr(_, n[1], None, Base.ret)


def f_call(_, n):
    return Expr(_, n[1], Symbol(_, "", unpack(n[2]), Base.array), Base.call)


def f_leave(_, n):
    return f_ret(_, ["return", Symbol(_, "", "0", Base.integer)])


def f_for(_, n):
    return Line(_, Expr(_, n[1], n[3], Base.iter), Body(n[5]), Base.foreach)


def f_forever(_, n):
    return Line(_, Body(n[2]), None, Base.forever)


def f_remove(_, n):
    return Symbol(_, "", "0", Base.void)


def f_type(_, n):
    if n[1] and n[1][1]:
        return Type(Base.typs.index(n[0].value), {"len": n[1][1]}, True)
    if n[1] and not n[1][1]:
        return Type(Base.typs.index(n[0].value), Data(), True)
    return Symbol(_, "", n[0], Base.type)


def f_def(_, n):
    return Expr(_, n[0], n[2], Base.define)


def f_var(_, n):
    return Expr(_, n[0], n[2], Base.assign)


def f_func(_, n):
    # print("[*] parser: f_func:")
    # print("\tname:", n[1])
    # print("\targs:", pformat(unpack(n[3])).replace("\n", "\n\t\t\t"))
    return Func(_, n[0] or Type(Base.void, Data()), n[1], *dearg(unpack(n[3])), n[7])


def f_import(_, n):
    return Import(n[1])


def f_format(_, n):
    return Format(n[1])


def f_root(_, n):
    return n[0]
    # return ("\n\n".join(tuple(str(i) for i in n))) \
    #            .replace("}, ", "}\n\n") \
    #            .replace(", format", "\n\nFormat") \
    #            .replace(", Line", "\n\nLine") \
    #            .replace(", Expr", "\n\nExpr") \
    #            .replace(", fn", "\n\nfn")[1:][:-1]


def f_comment(_, n):
    return Line(_, n, None, Base.ignore)
