from parser.hny.types import *


def f_ignore(_, n):
    return n[0]


def f_binop(_, n):
    return Binop(_, n[0], n[2], Binop.ops.index(n[1]))


def f_punop(_, n):
    return Unop(_, n[1], Unop.ops.index(n[0]), Unop.prefix)


def f_sunop(_, n):
    return Unop(_, n[0], Unop.ops.index(n[1]), Unop.suffix)


def f_root(_, n):
    return n[0]


def f_comment(_, _n):
    return
