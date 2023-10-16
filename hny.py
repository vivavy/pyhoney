import sys

from parglare import Grammar, Parser
from parser.hny.funcs import *
from analyze import check

data = {
    "format": "auto"
}

symbols: dict[str, Symbol] = {}


def parse(code):
    actions = {
        'root': f_root,
        'char': f_char,
        'string': f_string,
        'int': f_int,
        'name': f_name,
        'range': f_range,
        'assign': f_assign,
        'expr': [
            f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore,
            f_cast, f_ignore, f_binop, f_punop, f_sunop
        ],
        'geti': f_geti,
        'getv': f_getv,
        'ret': f_ret,
        'call': f_call,
        'liv': f_leave,
        'for_each': f_for,
        'for_ever': f_forever,
        'line': [
            f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore
        ],
        'type': f_type,
        'def_var': f_var,
        'def_def': f_def,
        'def_func': f_func,
        'def_import': f_import,
        'def_format': f_format,
        'comment': f_comment,
        'rline': f_ignore
    }

    return Parser(grammar=Grammar.from_file("grammar.antlr"), actions=actions).parse(code)


def gen(filename: str, _of: str):
    with open(filename, "rt") as f:
        src = f.read()

    if not src:
        print("Error: empty source")
        sys.exit(-2)

    prod = parse(src)

    check(prod, src)

    # code = generate(prod)

    # code = genhisp(procs, prod)

    # with open(of, "wt") as f:
        # f.write(code.strip() + "\n")


def get_format(filename: str):
    with open(filename, "rt") as f:
        src = f.read()

    prod = parse(src)

    form = 'auto'

    for n in prod:
        if Format == type(n):
            form = n.module.value

    return form
