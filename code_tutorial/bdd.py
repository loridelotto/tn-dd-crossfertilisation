"""A complete ROBDD package. Terminals are 0 and 1; every other node is an int id."""

T = {}   # id -> (var, low, high)          var is 1..n, low = branch for x=0
H = {}   # (var, low, high) -> id          the "unique table" / hash-consing

def reset():
    T.clear(); H.clear()

def mk(var, low, high):
    if low == high:                 # rule 1: this test is redundant
        return low
    key = (var, low, high)
    if key in H:                    # rule 2: this node already exists
        return H[key]
    u = len(T) + 2                  # 0 and 1 are taken by the terminals
    T[u] = key; H[key] = u
    return u

def var_of(u, n):
    return n + 1 if u in (0, 1) else T[u][0]

def apply(op, u1, u2, n, memo=None):
    if memo is None: memo = {}
    if (u1, u2) in memo: return memo[(u1, u2)]
    if u1 in (0, 1) and u2 in (0, 1):
        r = op(u1, u2)
    else:
        v = min(var_of(u1, n), var_of(u2, n))
        l1, h1 = (T[u1][1], T[u1][2]) if var_of(u1, n) == v else (u1, u1)
        l2, h2 = (T[u2][1], T[u2][2]) if var_of(u2, n) == v else (u2, u2)
        r = mk(v, apply(op, l1, l2, n, memo), apply(op, h1, h2, n, memo))
    memo[(u1, u2)] = r
    return r

AND = lambda a, b: a & b
OR  = lambda a, b: a | b
XOR = lambda a, b: a ^ b

def var(i):            return mk(i, 0, 1)
def neg(u, n):         return apply(lambda a, b: 1 - a, u, u, n)

def nodes(u):
    seen = set(); stack = [u]
    while stack:
        v = stack.pop()
        if v in (0, 1) or v in seen: continue
        seen.add(v); stack += [T[v][1], T[v][2]]
    return seen

def size(u):           return len(nodes(u))

def evaluate(u, assign):
    while u not in (0, 1):
        v, lo, hi = T[u]
        u = hi if assign[v - 1] else lo
    return u

def satcount(u, n, level=1):
    if u == 0: return 0
    if u == 1: return 2 ** (n - level + 1)
    v, lo, hi = T[u]
    return (satcount(lo, n, v + 1) + satcount(hi, n, v + 1)) * 2 ** (v - level)

def width(u, n):
    """Nodes per level -- this is the number the whole project cares about."""
    w = [0] * (n + 1)
    for v in nodes(u): w[T[v][0]] += 1
    return w[1:]
