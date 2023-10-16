def flat(a):
    r = []

    for i in a:
        if list == type(i):
            r += flat(i)
        elif i != ",":
            r += [i]
    return r.copy()


def unpack(n):
    # print("[*] parser: dearg:", n)
    # print("\tdecide:", "[]" if not n else "[n[0], *n[1][0]" if n[1] else "[n[0]]")

    if not n:
        # print("\treturn: []")
        return []

    if n[1]:
        n = [n[0], *n[1][0]]
    else:
        n = [n[0]]

    while "," in n:
        n.remove(",")

    # print("\treturn:", n)

    return n.copy()


def dearg(n):
    a = []
    b = []
    for i in n:
        a += [i.a]
        b += [i.b]
    return a, b
