# TODO: make test for binaries existance

import os
import hny
import argparse


#  format is a function makes file ready for use
def f_auto(i, o, _no_stdlib, _full_log, name, _module, rt, cf):
    hny.gen(i, name + ".fasm")

    os.system("fasm " + name + ".fasm " + cf)

    # linking
    os.system("ld -o" + o + " " + name + ".o")

    if rt:
        os.system("rm " + name + ".fasm")
        os.system("rm " + name + ".o")


def f_multiboot(i, o, _no_stdlib, _full_log, name, module, rt, cf):
    hny.gen(i, name + ".fasm")

    os.system("fasm " + name + ".fasm " + cf)

    # linking with trampoline
    os.system("i686-elf-gcc -T lds/multiboot.ld -ffreestanding -O3 -nostdlib " + cf + " -o " +
              (o or (module + ".elf")) + " objects/multiboot.o " +
              name + ".o")

    if rt:
        os.system("rm " + name + ".fasm")
        os.system("rm " + name + ".o")


forms = {
    "auto": f_auto,
    "multiboot": f_multiboot
}

argparser = argparse.ArgumentParser("hny")

argparser.add_argument("--no-stdlib", action="store_true", dest="no_stdlib")
argparser.add_argument("--full-log", action="store_true", dest="full_log")
argparser.add_argument("--save-temps", action="store_true", dest="save_temps")
argparser.add_argument("--c-flags", dest="c_flags")
argparser.add_argument("-f", dest="format")
argparser.add_argument("-o", dest="output")
argparser.add_argument("FILE")

args = argparser.parse_args()

module_name = os.path.splitext(args.FILE)[0]
name_hash = hex(hash(module_name))[2:]

form = args.format or hny.get_format(args.FILE)

forms[form](args.FILE, args.output, args.no_stdlib,
            args.full_log, name_hash, module_name, not args.save_temps, args.c_flags or "")
