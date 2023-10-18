import random

from analyze import *
from parser.hny.types import *


class Prolog:
    multiboot = """

format ELF  ; multiboot kernel is an ELF
use32       ; and bitness is equal to 32

    """.strip() + "\n\n\n"


class Section:
    class Code:
        Multiboot = "section '.text' executable\n\n"


class Loop:
    class Foreach:
        class Multiboot:
            @staticmethod
            def begin(dst, src, lbl):
                return f"""
    mov edx, dword {src}   ; edx = &(dst)
    mov ecx, dword [edx+4] ; ecx = dst.data
    mov esi, edx           ; edx = &(dst)
    mov edx, dword [edx]   ; edx = dst.length
{lbl}:
        mov ebx, dword [ecx]
        mov {dst}, ebx
        sub ecx, dword [esi+4]
        cmp ecx, edx
        jge {lbl}_end
"""

            @staticmethod
            def end(dst, src, lbl):
                return f"""
        jmp {lbl}
{lbl}_end:
"""


class Generator:
    code = ""
    data = ""
    lcls = ""
    redy = ""
    cnts: dict[str, str] = None
    f: Function = None

    def __init__(self, anl: Analyzer, src: str, prod: Node):
        self.anl = anl
        self.src = src
        self.prod = prod
        self.cnts = {}


class GeneratorMultiboot(Generator):
    def generate(self):
        f: Function

        self.code = Section.Code.Multiboot

        for f in tuple(self.anl.funcs.values()):
            for n, lcl in enumerate(f.frame.locals):
                self.lcls += "%local_"+lcl+(f" equ [esp+{n}]\n" if n else " equ [esp]\n")
            self.f = f
            self.gen_func(f)

        self.redy = Prolog.multiboot + self.lcls + "\n\n" + self.code

    def gen_func(self, func: Line):
        line: Line

        self.code += func.name + ":\n"

        for line in func.lines:
            self.gen_line(line)

        self.code += "\tret\n"
        self.code += "\n"

    def gen_line(self, line: Forever, t: int = 1):
        if isinstance(line, Forever):
            line: Line

            self.code += (lbl := ".L" + hex(hash(random.random()))[2:]) + ":\n"

            for line in line.lines:
                self.code += "\t" * (t + 1)
                self.code += self.gen_line(line, t + 1)
                self.code += "\n"

            self.code += "\t" * t + "jmp " + lbl + "\n"

        if isinstance(line, Foreach):
            dst = line.name
            src = line.array

            if isinstance(src, NameLiteral):
                rsrc = ("%local_" if self.f.frame.is_local(src.value) else "%global_") + src.value
            else:
                self.cnts["%const_"+str(len(self.cnts))] = src
                rsrc = tuple(self.cnts.keys())[-1]

            rdst = ("%local_" if self.f.frame.is_local(dst) else "%global_") + dst

            self.code += Loop.Foreach.Multiboot.begin(rdst, rsrc, (lbl := ".L" + hex(hash(random.random()))[2:]))

            for line in line.lines:
                self.gen_line(line)

            self.code += Loop.Foreach.Multiboot.end(rdst, rsrc, lbl)

