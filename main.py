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
def f_auto(i, o, no_stdlib, full_log, name, module, rt, cf, db):

    hnyir.gen_write_hisp(i, name + ".hl", _db=db)
    hisp.hisp_to_c(name + ".hl", no_stdlib, _db=db)

    c = comp_detector.detect_compiler()
    if not c:
        print("Please, install C language compiler (gcc or clang)!")
        exit(-1)
    os.system(c + " -Werror -Wall -Wextra -Wno-unused-value -Wno-return-type -O3 -o " + \
        (o or module) + " " + name + ".c")

    if rt:
        os.system("rm " + name + ".hl")
        os.system("rm " + name + ".c")

def f_multiboot(i, o, no_stdlib, full_log, name, module, rt, cf, db):

    hnyir.gen_write_hisp(i, name + ".hl", _db=db)
    hisp.hisp_to_c(name + ".hl", no_stdlib, _db=db)

    c = detect_c_compiler.detect_compiler_base("i686-elf-gcc", (9, 16))
    if not c:
        print("Please, install i686 elf tools!\n"
              "You can get it here: https://gith"
              "ub.com/lordmilko/i686-elf-tools/r"
              "eleases/tag/7.1.0")
        exit(-1)
    os.system(c + " -c -Werror -Wall -Wextra -Wno-unused-value " + cf + " " + \
        "-Wno-return-type -O3 -ffreestanding -o " + \
        name + ".o" + " " + name + ".c")

    # linuking with trampoline
    os.system(c + " -T lds/multiboot.ld -ffreestanding -O3 -nostdlib " + cf + " -o " + \
        (o or (module + ".elf")) + " objects/multiboot.o " + \
        name + ".o")

    if rt:
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
argparser.add_argument("--debug", action="store_true", dest="debug_mode")
argparser.add_argument("--full-log", action="store_true", dest="full_log")
argparser.add_argument("--save-temps", action="store_true", dest="save_temps")
argparser.add_argument("--c-flags", dest="c_flags")
argparser.add_argument("-f", dest="format")
argparser.add_argument("-o", dest="output")
argparser.add_argument("FILE")

args = argparser.parse_args()

# vivavy: compile time
# NDRAEY: refactored
# vivavy: added temp file names mangling

module_name = os.path.splitext(args.FILE)[0]

name_hash = hex(hash(hash(module_name) + 1))[2:]

# module_name += "." + name_hash  # vivavy: we need it for security: 
#                                 # if there was not mangling, file names could conflict,
#                                 # and it can cause a lot of problems.

# detect_format return 0 if all is fine, any non-zero value otherwise
form = args.format or detect_format(args.FILE)

forms[form](args.FILE, args.output, args.no_stdlib,
    args.full_log, name_hash, module_name, not args.save_temps, args.c_flags or "", args.debug_mode)
