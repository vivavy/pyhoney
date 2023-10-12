from parglare import Grammar, Parser
from pprint import pprint, pformat
import sys
import random
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
		'root': root,
		'def_func': lambda _, n: proc(n),
		'call': pcall,
		'import': lambda _, n: 'import ' + eval(n[1]),
		'comment': lambda _, n: '',
		'def_format': formatp,
		'def_var': lambda _, n: "var " + n[0].split(None, 1)[1] + " " + n[2],
		'getv': lambda _, n: n[0]+n[1],
		'assign': lambda _, n: "set " + n[0] + " " + n[2],
		'ret': lambda _, n: "    ret %s" % n[1],
		'cast': castp,
		'geti': lambda _, n: '[%s]' % n[1],
		'liv': lambda _, n: '    ret 0',
		'for_loop': forl,
		'forever_loop': forevl,
		'line': lambda _, n: n[0],
		'type': typ,
		'def_def': lambda _, n: "def " + n[2] + " " + n[0],
		'range': lambda _, n: "range " + n[0] + " " + n[2],
		'expr': [
			lambda _, n: n[0],
			lambda _, n: n[0],
			lambda _, n: n[0],
			lambda _, n: n[0],
			lambda _, n: n[0],
			lambda _, n: n[0],
			ecall,
			lambda _, n: n[0],
			lambda _, n: n[0],
			lambda _, n: n[0] + " " + n[1][0] + " " + n[2],
			lambda _, n: n[0][0] + n[1],
			lambda _, n: n[0] + n[1][0]
		]
	}
	return Parser(grammar=Grammar.from_file("grammar/hny.glr"), \
		actions=actions).parse(code)


def root(_, n):
	n = n[0]
	print("[*] hny: root:", n)
	return "\n".join(tuple(n))


def forevl(_, n):
	p = "l"+hex(hash(random.random()))[2:]
	return "label " + p + "\n" + "\n".join(tuple(n[2])) + "    jump " + p


def forl(_, n):
	return "for %s\n    %s;\n" % (n[1], "\n".join(tuple(n[5])).replace("\n", "\n    "))


def castp(_, n):
	print("[*] hny: castp:", n)
	return "cast " + n[0] + " " + n[2]


def formatp(_, n):
	#if db:
	#print("[*] hny:", "format =", n[1])
	data["format"] = n[1]
	return ""

def pcall(_, n):
	#if db:
	args = [n[2][0], *n[2][1]]
	#print("[*] hny:", "call", "call " + n[0] + "(" + ", ".join(tuple(args)) + ")")
	return ["call", n[0], args]


def proc(n):
	global procs, procs_raw
	name = n[1]
	args = pargs(n[3]) if n[3] else []
	rtyp = n[5][1] if n[5] else "int"
	body = ",\n".join(tuple(n[7]))+","
	print("[*] hny: proc:", "fn " + rtyp + " " + name + " " + \
	" ".join((i[1] for i in args)) + " " + " ".join((i[0] for i in args)) + "\n" + body + ";")
	return "fn " + rtyp + " " + name + " " + \
	" ".join((i[1] for i in args)) + ", " + " ".join((i[0] for i in args)) + ",\n" + body + ";"


def pargs(n):
	print("[*] hny: pargs:", n)
	if n[1]:
		n = [n[0], *n[1][0]]
	else:
		n = [n[0]]
	print("[*] hny: pargs: 2:", n)
	while ',' in n:
		n.remove(',')
	print("[*] hny: pargs: 3:", n)
	return [arg(a) for a in n]


def arg(n):
	#if db:
	print("[*] hisp: arg:", n)
	m = n.split()[2]
	t = n.split()[1]
	return [t, m]


def pbody(n):
	return ",\n".join(tuple(n))+","


def call(n):
	#print("[*] hny: call:", n)
	name = n[0]
	args = n[1] or []
	args = flat(args)
	while ',' in n:
		del n[n.index(',')]
	# print(">>> B", args)
	# args = [i[1] for i in args]
	return 'call ' + name + " " + " ".join(tuple(args)) + ","


def ecall(_, n):
	#print("[*] hny: ecall:", n)
	n = n[0]
	name = n[1]
	args = n[2] or []
	args = flat(args)
	while ',' in n:
		del n[n.index(',')]
	# print(">>> B", args)
	# args = [i[1] for i in args]
	return 'call ' + name + " " + " ".join(tuple(args)) + ","

def flat(a):
	r = []

	for i in a:
		if type(i) == list:
			r += flat(i)
		elif i != ",":
			r += [i]
	return r.copy()


def typ(_, n):
	array = ("","<>")[int(bool(n[1]))]
	#print("[*] hny: typ:", array+n[0])
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
		#if db:
		#print("[*] hny:", p)
		name = p[0]
		types = (i[0] for i in p[1])
		names = (i[1] for i in p[1])
		# print(">>> V", name)
		# print(">>> W", types)
		# print(">>> X", names)
		code += "\nfn %s %s "%(p[2], name)+" ".join(types)+", "
		code += " ".join(names)+";\n"
		for l in p[3]:
			#if db:
			print("[*] hny: genhisp: l:", l)
			if not l:
				continue
			if l[0] == "call":
				print("[*] hny: line: call:", args)
				code += "	call %s %s" % (l[1],
					" ".join(args))
				code += ",\n"
			if l[0] == "ret":
				code += "	ret %s,\n" % l[1]
			if l[0] == "assign":
				code += "    set " + l[1] + " " + l[2] + ",\n"
			if l[0] in "label jump".split():
				code += "    " + " ".join(tuple(l)) + ",\n"
		code = code[:-1] + ";\n"
	return code[1:]

def gen_write_hisp(filename: str, of: str = None):
	with open(filename, "rt") as f:
		src = f.read()

	prod = code = parse(src)

	print("[*] hny: gen_write_hisp: ", end='')
	pprint(prod)

	# code = genhisp(procs, prod)

	with open(of or os.path.splitext(filename)[0] + ".hsp", "wt") as f:
		f.write(code.strip()+"\n")
