from pprint import pprint
from generator import *
from parglare import Grammar, Parser
from parser.hny.funcs import *
from analyze import *
import sys


generators: dict[str, Generator.__class__] = {
    "multiboot": GeneratorMultiboot,
}


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
        'for_while': Forwhile,
        'for_clike': Forclike,
        'line': [
            f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore, f_ignore
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


def gen(filename: str, of: str, form: str):
    with open(filename, "rt") as f:
        src = f.read()

    if not src:
        print("Error: empty source")
        sys.exit(-2)

    prod = parse(src)

    analyzer = Analyzer(prod, src)

    status = analyzer.collect()

    if status:
        return status

    status = analyzer.check()

    if status:
        return status + 1

    generator = generators[form](analyzer, src, prod)

    generator.generate()

    code = generator.redy

    with open(of, "wt") as f:
        f.write(code.strip() + "\n")

    return 0


def get_format(filename: str):
    with open(filename, "rt") as f:
        src = f.read()

    prod = parse(src)

    form = 'auto'

    for n in prod.lines:
        if isinstance(n, Format):
            form = n.format

    return form
