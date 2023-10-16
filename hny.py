from parglare import Grammar, Parser
from parser.hny.funcs import *
from analyze import *
import sys


def parse(code):
    actions = {
        'root': Root,
        'char': CharLiteral,
        'string': StringLiteral,
        'int': IntLiteral,
        'name': NameLiteral,
        'range': Range,
        'assign': Assign,
        'cast': Cast,
        'expr': [
            f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore,
            f_ignore, f_ignore, f_binop, f_punop, f_sunop
        ],
        'ret': Return,
        'call': Call,
        'liv': Leave,
        'for_each': Foreach,
        'for_ever': Forever,
        'line': [
            f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore
        ],
        'getv': Lvalue,
        'type': Type,
        'def_var': Var,
        'def_def': Def,
        'def_func': Function,
        'def_import': Import,
        'def_format': Format,
        'comment': f_comment,
        'rline': f_ignore
    }

    return Parser(grammar=Grammar.from_file("grammar.antlr"), actions=actions).parse(code)


def gen(filename: str, of: str):
    with open(filename, "rt") as f:
        src = f.read()

    if not src:
        print("Error: empty source")
        sys.exit(-2)

    prod = parse(src)

    # print(repr(prod))

    analyzer = Analyzer(prod, src)

    analyzer.collect()

    print("A.FNC:", analyzer.funcs)
    print("A.TYP:", tuple(type(i).__name__ for i in analyzer.funcs))
    print("A.FRM", tuple(i.frame.locals for i in analyzer.funcs.values()))
    print("A.GLB", analyzer.globf.locals)

    return

    status = analyzer.check()

    if status:
        sys.exit(status)

    code = analyzer.generate()

    with open(of, "wt") as f:
        f.write(code.strip() + "\n")


def get_format(filename: str):
    with open(filename, "rt") as f:
        src = f.read()

    prod = parse(src)

    form = 'auto'

    for n in prod.lines:
        if n.type is Format:
            form = n.format

    return form
