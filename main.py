import os, sys, pprint


nostdlib = " --no-stdlib" if "--no-stdlib" in sys.argv else ""

# os.system(["clear", "cls"][os.name == 'nt'])
os.system("python3 hnyir.py "+sys.argv[-1]+nostdlib)
os.system("python3 hisp.py "+sys.argv[-1][::-1].split(".", 1)\
	[1][::-1]+".hsp"+nostdlib)

inf = sys.argv[-1][::-1].split(".", 1)[1][::-1]+".c"

outf = sys.argv[-1][::-1].split(".", 1)[1][::-1]+".out"

for a in sys.argv:
	if a == "-o":
		outf = sys.argv[sys.argv.index(a)+1]

comp = "gcc"

for a in sys.argv:
	if a == "-c":
		comp = sys.argv[sys.argv.index(a)+1]

# print(comp+" "+inf+" -o "+outf)

os.system(comp+" "+inf+" -o "+outf)
