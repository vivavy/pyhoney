import os

from parglare import Grammar, Parser
from pprint import pprint, pformat
import sys

stdlib_header = '''#include <stdio.h>
#include <stdlib.h>

'''

types = {
	"void": "int ",
	"u8": "unsigned char ",
	"i8": "signed char ",
	"u16": "unsigned short ",
	"i16": "signed short ",
	"u32": "unsigned long ",
	"i32": "signed long ",
	"u64": "unsigned long long ",
	"i64": "signed long long ",
	"uint": "unsigned int ",
	"int": "int ",
	"char": "char ",
	"str": "char *",
	"array u8": "unsigned char *",
	"array i8": "signed char *",
	"array u16": "unsigned short *",
	"array i16": "signed short *",
	"array u32": "unsigned long *",
	"array i32": "signed long",
	"array u64": "unsigned long long *",
	"array i64": "signed long long *",
	"array uint": "unsigned int *",
	"array int": "int *",
	"array char": "char *",
	"array str": "char **",
}

procs = {}
prots = {}


def parse(code):
	actions = {
		"proc": proc,
		"type": typ,
		"line": line
	}
	return Parser(grammar=Grammar.from_file("grammar/hisp.glr"),
				  actions=actions).parse(code)


def proc(_, n):
	rtype = types[n[1]]
	name = n[2]
	args = ", ".join((a + b for a, b in zip(n[3], n[5])))
	body = "".join(n[7])
	code = "%s%s(%s) {\n%s};\n" % (rtype, name, args, body)
	code = code.replace("{\n}", "{}")
	procs[name] = code
	prots[name] = code.split(" {")[0]+";"
	return code


def typ(_, n):
	if not n[0]:
		n[0] = ""
	return types[" ".join(tuple(n)).strip()]


def line(_, n):
	if n[0] == "call":
		return "    "+n[1]+"("+", ".join(tuple(n[2]))+");\n"
	if n[0] == "ret":
		return "    return %s;\n" % n[1]


def hisp_to_c(filename: str, no_stdlib: bool = False):
	with open(filename, "rt", encoding="cp866") as f:
		src = f.read()

	prod = parse(src)

	with open(os.path.splitext(filename)[0] + ".c", "wt", encoding="cp866") as f:
		code = ""

		if not no_stdlib:
			code += stdlib_header

		code += "\n".join(tuple(prots.values())) + "\n" * 3 + "\n".join(tuple(procs.values()))

		f.write(code)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("No input files.")
		exit(1)

	file = sys.argv[-1]

	hisp_to_c(file)
