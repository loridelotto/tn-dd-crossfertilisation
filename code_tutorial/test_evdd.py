from itertools import product, permutations
from math import sqrt
import evdd, bdd

def check(f, n, label):
    evdd.reset()
    e = evdd.from_amplitudes(f, n)
    for a in product([0, 1], repeat=n):
        got, want = evdd.amplitude(e, a), f.get(a, 0)
        assert abs(got - want) < 1e-12, (a, got, want)
    print(f"{label:<12} size={evdd.size(e):2d}  width={evdd.width(e, n)}")
    return e

n = 4
s = 1 / sqrt(2)
check({(0,)*n: s, (1,)*n: s}, n, "GHZ")
check({tuple(1 if j == i else 0 for j in range(n)): 1/2 for i in range(n)}, n, "W")
check({a: 1 / 4 for a in product([0, 1], repeat=n)}, n, "uniform")
check({a: (-1) ** (a[0]*a[1] + a[1]*a[2] + a[2]*a[3]) / 4 for a in product([0,1], repeat=n)}, n, "IQP-ish")

# a state whose EVDD size depends on the order
f = {a: float(a[0] == a[1]) * float(a[2] == a[3]) for a in product([0, 1], repeat=4)}

def permuted(f, order, n=4):
    return {tuple(a[order[i]] for i in range(n)): v for a, v in f.items()}

sizes = []
for o in permutations(range(4)):
    evdd.reset()
    sizes.append((evdd.size(evdd.from_amplitudes(permuted(f, o), 4)), o))
print("order-dependent state: min size", min(sizes)[0], "max size", max(sizes)[0])

# bigger BDD ordering gap
def build_pairs(order, n):
    pos = {y: i + 1 for i, y in enumerate(order)}
    r = 0
    for j in range(1, n + 1, 2):
        r = bdd.apply(bdd.OR, r, bdd.apply(bdd.AND, bdd.var(pos[j]), bdd.var(pos[j+1]), n), n)
    return r

for n in (6, 8, 10, 12):
    good = tuple(range(1, n + 1))
    bad = tuple(range(1, n + 1, 2)) + tuple(range(2, n + 1, 2))
    bdd.reset(); g = bdd.size(build_pairs(good, n))
    bdd.reset(); b = bdd.size(build_pairs(bad, n))
    print(f"n={n:2d}  good order: {g:3d} nodes   bad order: {b:4d} nodes")
print("all assertions passed")
