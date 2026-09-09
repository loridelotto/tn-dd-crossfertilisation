"""Edge-valued DD: weights multiply along the path. An edge is a pair (weight, node).
Weight 0 means "this branch is identically zero" and the node is ignored (we use ZERO)."""

ZERO, ONE = None, "1"      # ONE is the single terminal, meaning the constant 1
T, H = {}, {}              # id -> (var, (w0,n0), (w1,n1))  /  that tuple -> id

def reset(): T.clear(); H.clear()

def mknode(var, e0, e1):
    """Return a NORMALISED edge (c, node) for the node with children e0, e1."""
    (w0, n0), (w1, n1) = e0, e1
    if w0 == 0 and w1 == 0:
        return (0, ZERO)
    c = w0 if w0 != 0 else w1                 # normalisation: first non-zero weight -> 1
    e0, e1 = (w0 / c, n0), (w1 / c, n1)
    if e0 == e1:                              # rule 1: redundant test, f ignores this variable
        return (c, e0[1])
    return (c, _hash(var, e0, e1))            # rule 2 lives in _hash (sharing)

def _hash(var, e0, e1):
    key = (var, e0, e1)
    if key in H: return H[key]
    u = len(T) + 1
    T[u] = key; H[key] = u
    return u

def amplitude(edge, assign):
    """f(assign) = product of the weights along the selected path."""
    w, u = edge
    for b in assign:
        if u is ZERO or w == 0: return 0
        if u is ONE: break
        _, e0, e1 = T[u]
        wb, u = (e1 if b else e0)
        w *= wb
    return w

def nodes(edge):
    seen, stack = set(), [edge[1]]
    while stack:
        u = stack.pop()
        if u in (ZERO, ONE) or u in seen: continue
        seen.add(u); stack += [T[u][1][1], T[u][2][1]]
    return seen

def size(edge): return len(nodes(edge))

def width(edge, n):
    w = [0] * (n + 1)
    for u in nodes(edge): w[T[u][0]] += 1
    return w[1:]

def from_amplitudes(f, n):
    """Build the EVDD of a function given as a dict {bitstring tuple: amplitude}."""
    def rec(prefix):
        if len(prefix) == n:
            a = f.get(prefix, 0)
            return (a, ONE) if a != 0 else (0, ZERO)
        return mknode(len(prefix) + 1, rec(prefix + (0,)), rec(prefix + (1,)))
    return rec(())
