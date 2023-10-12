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
	"str": "str ",
	"<> u8": "unsigned char *",
	"<> i8": "signed char *",
	"<> u16": "unsigned short *",
	"<> i16": "signed short *",
	"<> u32": "unsigned long *",
	"<> i32": "signed long *",
	"<> u64": "unsigned long long *",
	"<> i64": "signed long long *",
	"<> uint": "unsigned int *",
	"<> int": "int *",
	"<> char": "char *",
	"<> str": "str *",
}

typec = {
	"int ": "int",
	"unsigned char ": "u8",
	"signed char ": "i8",
	"unsigned short ": "u16",
	"signed short ": "i16",
	"unsigned long ": "u32",
	"signed long ": "i32",
	"unsigned long long ": "u64",
	"signed long long ": "i64",
	"unsigned int ": "uint",
	"char ": "char",
	"char *": "charptr",
	"unsigned char *": "u8ptr",
	"signed char *": "i8ptr",
	"unsigned short *": "u16ptr",
	"signed short *": "i16ptr",
	"unsigned long *": "u32ptr",
	"signed long *": "i32ptr",
	"unsigned long long *": "u64ptr",
	"signed long long *": "i64ptr",
	"unsigned int *": "uintptr",
	"signed int *": "intptr",
	"char *": "charptr",
	"char **": "charptrptr",
}

procs = {}
prots = {}
globs = {}


c_predefined = """

#define hny$cast$int(a) ((int)a)
#define hny$cast$u8(a) ((unsigned char)a)
#define hny$cast$i8(a) ((signed char)a)
#define hny$cast$u16(a) ((unsigned short)a)
#define hny$cast$i16(a) ((signed short)a)
#define hny$cast$u32(a) ((unsigned long)a)
#define hny$cast$i32(a) ((signed long)a)
#define hny$cast$u64(a) ((unsigned long long)a)
#define hny$cast$i64(a) ((signed long long)a)
#define hny$cast$char(a) ((char)a)
#define hny$cast$intptr(a) ((int *)a)
#define hny$cast$u8ptr(a) ((unsigned char *)a)
#define hny$cast$i8ptr(a) ((signed char *)a)
#define hny$cast$u16ptr(a) ((unsigned short *)a)
#define hny$cast$i16ptr(a) ((signed short *)a)
#define hny$cast$u32ptr(a) ((unsigned long *)a)
#define hny$cast$i32ptr(a) ((signed long *)a)
#define hny$cast$u64ptr(a) ((unsigned long long *)a)
#define hny$cast$i64ptr(a) ((signed long long *)a)
#define hny$cast$charptr(a) ((char *)a)
#define hny$cast$charptrptr(a) ((char **)a)
#define __$call

int hny$internal$strlen(char *c_str) {
	int i;
	for (i = 0; c_str[i]; i++) {}
	return i;
}

void ignore(void *data) {data;}

typedef struct {
	int len;
	char *c_str;
} str;

str method$str$$new$charptr(char *c_str) {
	return (str){hny$internal$strlen(c_str), c_str};
}

"""

db = False


def parse(code):
	actions = {
		"proc": proc,
		"type": typ,
		"line": line,
		"def_def": def_def,
		"def_var": def_var,
		'getv': lambda _, n: n[0]+(f"[{n[1][1]}]" if n[1] else ""),
		'assign': lambda _, n: ["assign", n[0], n[2]],
		'castp': castp,
		'calle': line_1,
		'string': lambda _, n: "method$str$$new$charptr("+n+")",
		'line': [
			ret,
			line_2,
			lambda _, n: n[1] + ":",
			lambda _, n: "    goto " + n[1] + ";",
			lambda _, n: "    " + n[0] + ";"
		]
	}
	return Parser(grammar=Grammar.from_file("grammar/hisp.glr"),
				  actions=actions).parse(code)


def line_1(_, n):
	print("[*] hisp: line_1:", n)
	return n[1] + "(" + ", ".join(tuple(n[2])) + ")"


def ret(_, n):
	print("[*] hisp: ret:", n)
	return "    return " + n[1] + ";"


def line_2(_, n):
	print("[*] hisp: line_2:", n)
	return "    " + n[1] + " = " + n[2] + ";"


def castp(_, n):
	if db:
		print("[*] hisp:", n, "hny$cast$" + typec[n[2]] + "(" + n[1] + ")")
	return "hny$cast$" + typec[n[2]] + "(" + n[1] + ")"


def def_def(_, n):
	globs[n[2]] = "%s %s;" % (n[1], n[2])

def def_var(_, n):
	# print(n)
	globs[n[2]] = "%s %s = %s;" % (n[1], n[2], n[3])


def proc(_, n):
	print("[*] hisp: proc:", n)
	rtype = types[n[1]]
	name = n[2]
	args = ", ".join((a + b for a, b in zip(n[3], n[5])))
	body = "\n".join(n[7])
	code = "%s%s(%s) {\n%s\n};\n" % (rtype, name, args, body)
	code = code.replace("{\n}", "{}")
	procs[name] = code
	prots[name] = code.split(" {")[0]+";"
	return code


def typ(_, n):
	# print(">>> Y", n)
	if not n[0]:
		n[0] = ""
	return types[" ".join(tuple(n)).strip()]


def line(_, n):
	if db:
		print("[*] hisp:", n)
	if n[0] == "call":
		return "    "+n[1]+"("+", ".join(tuple(n[2]))+");\n"
	if n[0] == "ret":
		return "    return %s;\n" % n[1]
	if n[0] == "set":
		return "    " + n[1] + " = " + n[2] + ";\n"
	if n[0] == "label":
		return n[1] + ":\n"
	if n[0] == "jump":
		return "    goto " + n[1] + ";\n"


def hisp_to_c(filename: str, no_stdlib: bool = False, _db: bool = False):
	global db;db = _db
	with open(filename, "rt") as f:
		src = f.read()

	prod = parse(src)

	if db:
		print("[*] hisp:", end=" ")
		pprint(prod)

	with open(os.path.splitext(filename)[0] + ".c", "wt") as f:
		code = ""

		if not no_stdlib:
			code += stdlib_header

		code += c_predefined

		code += "\n".join(tuple(globs.values())) + "\n" * 2

		code += "\n".join(tuple(prots.values())) + "\n" * 3 + "\n".join(tuple(procs.values()))

		code = code.strip() + "\n"

		f.write(code)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("No input files.")
		exit(1)

	file = sys.argv[-1]

	hisp_to_c(file)
