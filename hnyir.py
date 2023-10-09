from parglare import Grammar, Parser
from pprint import pprint, pformat
import sys
import os.path

procs = {}


def parse(code):
	actions = {
		'def_func': lambda _, n: proc(n),
		'call': lambda _, n: ['call', n[0], n[2]],
		'import': lambda _, n: ['import', eval(n[1])]
	}
	return Parser(grammar=Grammar.from_file("grammar/hny.glr"), \
		actions=actions).parse(code)


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
	if n[0] == "call":
		return call(n[1:])
	elif n[0] == "return":
		return ["ret", n[1]]


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
	array = ("","<> ")[int(bool(n[1]))]
	return array+n[0]


def genhisp(procs):
	code = ""

	for p in tuple(procs.values()):
		# p = p[0] + [p[1]]
		# pprint(p)
		name = p[0]
		types = (i[0] for i in p[1])
		names = (i[1] for i in p[1])
		code += "\nfn %s %s "%(p[2], name)+" ".join(types)+", "
		code += " ".join(names)+";\n"
		for l in p[3]:
			if l[0] == "call":
				args = tuple(l[2])
				# print(args)
				code += "    call %s %s" % (l[1],
					" ".join(args))
				code += ",\n"
			if l[0] == "ret":
				code += "    ret %s,\n" % l[1]
		code = code[:-1] + ";\n"
	return code[1:]

def gen_write_hisp(filename: str, of: str = None):
    with open(filename, "rt", encoding="cp866") as f:
	    src = f.read()

    parse(src)

    code = genhisp(procs)

    with open(of or os.path.splitext(filename)[0] + ".hsp",
              "wt",
              encoding="cp866") as f:
	    f.write(code)
