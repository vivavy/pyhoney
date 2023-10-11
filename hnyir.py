from parglare import Grammar, Parser
from pprint import pprint, pformat
import sys
import os.path

procs = {}


allowed_formats = (
	"auto",
	"multiboot",
	"mbr"
	"exe",
	"exe64",
	"dll",
	"dll64",
	"kex",
	"hxe",
	"hxe16",
	"hxe64"
)

data = {
	"format": "auto"
}

globs = {
	# name: (type, None) or (type, value)
}


def parse(code):
	actions = {
		'def_func': lambda _, n: proc(n),
		'call': pcall,
		'import': lambda _, n: ['import', eval(n[1])],
		'comment': lambda _, n: ['comment', n],
		'def_format': formatp,
		'def_def': lambda _, n: ["def", n[2], n[0]],
		'def_var': lambda _, n: ["var", n[2], n[0]],
		'getv': lambda _, n: n[0]+(f"[{n[1][1]}]" if n[1] else ""),
		'assign': lambda _, n: ["assign", n[0], n[2]],
		'cast': lambda _, n: "cast " + n[0] + " " + typ(n[2])
	}
	return Parser(grammar=Grammar.from_file("grammar/hny.glr"), \
		actions=actions).parse(code)


def formatp(_, n):
	# print(n)
	data["format"] = n[1]
	return n

def pcall(_, n):
	# print(">>> N", n)
	return ['call', n[0], n[2]]


def proc(n):
	global procs, procs_raw
	name = n[1]
	args = pargs(n[3]) if n[3] else []
	rtyp = n[5][1][0] if n[5] else "int"
	body = pbody(n[7])
	procs[name] = (name, args, rtyp, body)
	return tuple(procs.values())[-1]


def pargs(n):
	n = [n[0], *n[1][0]]
	while ',' in n:
		n.remove(',')
	return [arg(a) for a in n]


def arg(n):
	m = n[0]
	t = typ(n[2])
	return [t, m]


def pbody(n):
	return [line(l) for l in n]


def line(n):
	# print(">>> O", n)
	if n[0] == "call":
		return call(n[1:])
	elif n == "leave":
		return ["ret", "0"]
	elif n[0] == "return":
		return ["ret", n[1]]
	return n


def call(n):
	# print("\n>>> C", n, end="\n\n")
	name = n[0]
	args = n[1] or []
	args = flat(args)
	while ',' in n:
		del n[n.index(',')]
	# print(">>> B", args)
	# args = [i[1] for i in args]
	return ['call', name, args]

def flat(a):
	r = []

	for i in a:
		if type(i) == list:
			r += flat(i)
		elif i != ",":
			r += [i]
	return r.copy()


def typ(n):
	array = ("","<>")[int(bool(n[1]))]
	# print("[*]", array+n[0])
	return array+n[0]


def genhisp(procs, prod):
	code = " "

	for n in prod:
		if n[0] == "def":
			code += "def " + typ(n[1]) + " " + n[2] + "\n"
		if n[0] == "var":
			# print(">>> H", n)
			code += "var " + typ(n[2][1]) + " " + n[2][2] + " " + n[1] + "\n"

	for p in tuple(procs.values()):
		# p = p[0] + [p[1]]
		# pprint(p)
		name = p[0]
		types = (i[0] for i in p[1])
		names = (i[1] for i in p[1])
		# print(">>> V", name)
		# print(">>> W", types)
		# print(">>> X", names)
		code += "\nfn %s %s "%(p[2], name)+" ".join(types)+", "
		code += " ".join(names)+";\n"
		for l in p[3]:
			# print(">>> L", l)
			if not l:
				continue
			if l[0] == "call":
				args = tuple(l[2])
				# print(args)
				code += "	call %s %s" % (l[1],
					" ".join(args))
				code += ",\n"
			if l[0] == "ret":
				code += "	ret %s,\n" % l[1]
			if l[0] == "assign":
				# print(">>> A", n)
				code += "    set " + l[1] + " " + l[2] + "\n"
		code = code[:-1] + ";\n"
	return code[1:]

def gen_write_hisp(filename: str, of: str = None):
	with open(filename, "rt") as f:
		src = f.read()

	prod = parse(src)

	code = genhisp(procs, prod)

	with open(of or os.path.splitext(filename)[0] + ".hsp", "wt") as f:
		f.write(code)
