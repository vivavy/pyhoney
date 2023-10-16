def flat(a):
    r = []

    for i in a:
        if list == type(i):
            r += flat(i)
        elif i != ",":
            r += [i]
    return r.copy()


def unpack(n):

    if not n:
        return []

    if n[1]:
        n = [n[0], *n[1][0]]
    else:
        n = [n[0]]

    while "," in n:
        n.remove(",")

    return n.copy()


def dearg(n):
    # print(n)
    a = []
    b = []
    for i in n:
        a += [i.name]
        b += [i.type]
    return a, b
