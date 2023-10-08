import os
import sys
import pprint
import detect_c_compiler as comp_detector
import hisp
import hnyir
import argparse

argparser = argparse.ArgumentParser("hny")

argparser.add_argument("--no-stdlib", action="store_true")
argparser.add_argument("-c", dest="compiler")
argparser.add_argument("-cf", type=str, dest="compiler_flags")
argparser.add_argument("-o", dest="output")
argparser.add_argument("FILE")

args = argparser.parse_args()
module_name = os.path.splitext(args.FILE)[0]

# os.system(["clear", "cls"][os.name == 'nt'])

hnyir.gen_write_hisp(args.FILE)

# os.system("python3 hisp.py " + module_name + ".hsp" + (" --no-stdlib" if args.no_stdlib else ""))
hisp.hisp_to_c(module_name + ".hsp", args.no_stdlib)

inf = module_name + ".c"
outf = args.output if args.output else module_name + ".out"

comp = args.compiler
comp_opts = args.compiler_flags or ""

# If user don't provide compiler manually, then detect it automatically
if comp is None:
    comp = comp_detector.detect_compiler()

command = comp + " " + comp_opts + " " + inf + " -o " + outf

print("Executing:", command)

os.system(command)
