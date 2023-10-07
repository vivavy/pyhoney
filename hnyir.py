from parglare import Grammar, Parser
from pprint import pprint, pformat
import sys


procs = {}


def parse(code):
	actions = {
		'def_proc': lambda _, n: proc(n),
		'call': lambda _, n: ['call', n[0], n[2]],
		'string': lambda _, n: ['string', n],
		'name': lambda _, n: ['name', n],
		# 'int': lambda _, n: ['int', n],
		'ellipse': lambda _, n: ['ellipse', n],
		'import': lambda _, n: ['import', eval(n[1])]
	}
	return Parser(grammar=Grammar.from_file("hny.glr"), \
		actions=actions).parse(code)


def proc(n):
	global procs, procs_raw
	name = n[1][1]
	args = pargs(n[3]) if n[3] else []
	body = pbody(n[6])
	procs[name] = (name, args, body)
	return tuple(procs.values())[-1]


def pargs(n):
	n = [n[0], *n[1]]
	while ',' in n:
		n.remove(',')
	return [arg(a) for a in n]


def arg(n):
	m = n[0][1]
	t = typ(n[2])
	return [t, m]


def pbody(n):
	return [line(l) for l in n]


def line(n):
	if n[0] == "call":
		return call(n[1:])


def call(n):
	name = n[0][1]
	args = [n[1][0], *n[1][1]] if n[1] else []
	args = [i[1] for i in args]
	return ['call', name, args]


def typ(n):
	array = ("","array ")[int(bool(n[1]))]
	return array+n[0][1]


def genhisp(procs):
	code = ""

	for p in tuple(procs.values()):
		name = p[0]
		types = (i[0] for i in p[1])
		names = (i[1] for i in p[1])
		code += "\nfn void %s "%name+" ".join(types)+", "
		code += " ".join(names)+";\n"
		for l in p[2]:
			if l[0] == "call":
				args = tuple(l[2])
				print(args)
				code += "    call %s %s" % (l[1],
					" ".join(args))
				code += ",\n"
		code = code[:-1] + ";\n"
	return code[1:]


with open(sys.argv[-1], "rt", encoding="cp866") as f:
	src = f.read()

parse(src)

code = genhisp(procs)

with open(sys.argv[-1][::-1].split(".", 1)\
	[1][::-1]+".hsp", "wt", encoding="cp866") as f:
	f.write(code)
