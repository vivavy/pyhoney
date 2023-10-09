import os
import sys
import pprint
import detect_c_compiler, detect_c_compiler as comp_detector
import hisp
import hnyir
import argparse
import random
import traceback


# vivavy: formats

# format detection is very simple
def detect_format(i):
    with open(i, "rt") as f:
        hnyir.parse(f.read())
    return hnyir.data["format"]

#  format is a function makes file ready for use
def f_auto(i, o, no_stdlib, full_log, name):

    hnyir.gen_write_hisp(i, name + ".hl")
    hisp.hisp_to_c(name + ".hl", no_stdlib)

    c = comp_detector.detect_compiler()
    os.system(c + " -Werror -Wall -Wextra -Wno-unused-value -O3 -o " + \
        (o or os.path.splitext(name)[0]) + " " + name + ".c")

    os.system("rm " + name + ".hl")
    os.system("rm " + name + ".c")

def f_multiboot(i, o, no_stdlib, full_log, name):

    hnyir.gen_write_hisp(i, name + ".hl")
    hisp.hisp_to_c(name + ".hl", no_stdlib)

    c = detect_c_compiler.detect_compiler_base("i686-elf-gcc", (9, 16))
    os.system(c + " -c -Werror -Wall -Wextra -Wno-unused-value -O2 -ffreestanding -o " + \
        (o or name) + ".o" + " " + name + ".c")

    # building trampoline
    os.system(c + " -T lds/multiboot.ld -ffreestanding -O2 -nostdlib -o " + \
        (o or (os.path.splitext(name)[0] + ".elf")) + " objects/multiboot.o " + \
        (o or name) + ".o")

    os.system("rm " + name + ".hl")
    os.system("rm " + name + ".c")
    os.system("rm " + name + ".o")

forms = {
    "auto": f_auto,
    "multiboot": f_multiboot
}


# NDRAEY: arguments parsing
# vivavy: edited

argparser = argparse.ArgumentParser("hny")

argparser.add_argument("--no-stdlib", action="store_true", dest="no_stdlib")
argparser.add_argument("--full-log", action="store_true", dest="full_log")
argparser.add_argument("--save-temps", action="store_true", dest="save_temps")
argparser.add_argument("-f", dest="format")
argparser.add_argument("-o", dest="output")
argparser.add_argument("FILE")

args = argparser.parse_args()

# vivavy: compile time
# NDRAEY: refactored
# vivavy: added temp file names mangling

module_name = os.path.splitext(args.FILE)[0]

name_hash = hex(hash(hash(module_name) + 1))[2:]

module_name += "." + name_hash  # vivavy: we need it for security: 
                                # if there was not mangling, file names could conflict,
                                # and it can cause a lot of problems.

# detect_format return 0 if all is fine, any non-zero value otherwise
form = args.format or detect_format(args.FILE)

forms[form](args.FILE, args.output, args.no_stdlib, args.full_log, module_name)
