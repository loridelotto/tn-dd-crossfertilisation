from itertools import product, permutations
from bdd import *

def build_pairs(order, n=6):
    """(y1&y2) | (y3&y4) | (y5&y6), where original variable y_j sits at level order.index(j)+1."""
    pos = {y: i + 1 for i, y in enumerate(order)}
    r = 0
    for j in range(1, n + 1, 2):
        r = apply(OR, r, apply(AND, var(pos[j]), var(pos[j + 1]), n), n)
    return r

def truth(u, n):
    return [evaluate(u, a) for a in product([0, 1], repeat=n)]

def ref(order, n=6):
    pos = {y: i for i, y in enumerate(order)}
    out = []
    for a in product([0, 1], repeat=n):
        y = lambda j: a[pos[j]]
        out.append(int((y(1) and y(2)) or (y(3) and y(4)) or (y(5) and y(6))))
    return out

# --- ordering experiment ---------------------------------------------------
good, bad = (1, 2, 3, 4, 5, 6), (1, 3, 5, 2, 4, 6)
for name, o in [("good 1,2,3,4,5,6", good), ("bad  1,3,5,2,4,6", bad)]:
    reset(); u = build_pairs(o)
    assert truth(u, 6) == ref(o), "oracle mismatch"
    print(f"{name}: size={size(u):2d}  width={width(u, 6)}  sat={satcount(u,6)}")

# --- best and worst over all 720 orders ------------------------------------
sizes = []
for o in permutations(range(1, 7)):
    reset(); sizes.append((size(build_pairs(o)), o))
print("min/max over all orders:", min(sizes)[0], max(sizes)[0], " worst order:", max(sizes)[1])

# --- other sanity checks ---------------------------------------------------
reset()
n = 4
x = [var(i) for i in range(1, n + 1)]
p = apply(XOR, apply(XOR, x[0], x[1], n), apply(XOR, x[2], x[3], n), n)
print("parity(4): size =", size(p), " width =", width(p, n), " sat =", satcount(p, n))
assert satcount(p, n) == 8
assert all(evaluate(p, a) == sum(a) % 2 for a in product([0, 1], repeat=n))

reset()
n = 3
x = [var(i) for i in range(1, 4)]
maj = apply(OR, apply(AND, x[0], x[1], n), apply(OR, apply(AND, x[0], x[2], n),
                                                 apply(AND, x[1], x[2], n), n), n)
print("majority(3): size =", size(maj), " sat =", satcount(maj, n))
assert all(evaluate(maj, a) == (sum(a) >= 2) for a in product([0, 1], repeat=3))
print("all assertions passed")
