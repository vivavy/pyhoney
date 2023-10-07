from shutil import which

def detect_compiler_base(compiler_name: str,
                         version_range: tuple[int, int]
                        ) -> str | None:
    if compiler := which(compiler_name):
        return compiler

    for i in range(*version_range):
        if compiler := which(compiler_name + "-" + str(i)):
            return compiler

def detect_clang():
    return detect_compiler_base("clang", (9, 18))

def detect_gcc():
    return detect_compiler_base("gcc", (9, 16))

def detect_compiler():
    return detect_clang() or detect_gcc()

if __name__ == "__main__":
    print(detect_compiler())
