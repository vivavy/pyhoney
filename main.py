import os, sys, pprint
import detect_c_compiler as comp_detector

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

comp = None
comp_opts = ""

for a in sys.argv:
	if a == "-c":
		comp = sys.argv[sys.argv.index(a)+1]
	elif a == "-cf":  # Compiler Flags
	    comp_opts += sys.argv[sys.argv.index(a)+1]

# If user don't provide compiler manually, then detect it automatically
if comp is None:
    comp = comp_detector.detect_compiler()

command = comp+" "+comp_opts+" "+inf+" -o "+outf

print(command)

os.system(command)
