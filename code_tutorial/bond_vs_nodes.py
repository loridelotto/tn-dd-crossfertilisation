"""One permutation, two numbers: decision-diagram node count AND tensor-train bond dimension.

Needs bdd.py in the same folder, plus numpy.   Run:   python3 bond_vs_nodes.py

The point: a permutation of the variables is ONE object. Read as a decision-diagram
variable order it gives a node count; read as a tensor-train site order it gives a
list of bond dimensions. This script computes both from the same permutation.

The function is the usual one:  (y1 AND y2) OR (y3 AND y4) OR (y5 AND y6) OR ...
"""

from itertools import product, permutations
import numpy as np
import bdd


# ---------------------------------------------------------------- the function
def amplitudes(order, n):
    """Full 2^n table of the pairs function, as an n-index tensor of shape (2,2,...,2).

    `order` is a permutation of 1..n; original variable order[i] is placed at
    tensor axis i. This is the ONLY place the permutation enters.
    """
    pos = {y: i for i, y in enumerate(order)}          # original variable -> axis
    T = np.zeros([2] * n)
    for a in product([0, 1], repeat=n):                # a[i] is the bit at axis i
        y = lambda j: a[pos[j]]                        # value of ORIGINAL variable y_j
        T[a] = float(any(y(j) and y(j + 1) for j in range(1, n + 1, 2)))
    return T


# ------------------------------------------------- reading it as a tensor train
def bond_dimensions(T, n, tol=1e-10):
    """Bond dimension at every cut = rank of the matricisation at that cut.

    Cut r splits axes 0..r-1 (rows) from axes r..n-1 (columns). The minimal bond
    dimension a tensor train needs there is exactly the rank of that matrix.
    """
    dims = []
    for r in range(1, n):
        M = T.reshape(2 ** r, 2 ** (n - r))
        s = np.linalg.svd(M, compute_uv=False)         # singular values
        dims.append(int((s > tol * s[0]).sum()))       # numerical rank
    return dims


# --------------------------------------------- reading it as a decision diagram
def dd_size(order, n):
    """Node count of the ROBDD of the same function under the same permutation."""
    bdd.reset()
    pos = {y: i + 1 for i, y in enumerate(order)}      # original variable -> level
    result = 0
    for j in range(1, n + 1, 2):
        pair = bdd.apply(bdd.AND, bdd.var(pos[j]), bdd.var(pos[j + 1]), n)
        result = bdd.apply(bdd.OR, result, pair, n)
    return bdd.size(result), bdd.width(result, n)


# ----------------------------------------------------------------- the two runs
print("One permutation in, two numbers out.  Read ACROSS the rows.\n")
print(f"{'n':>3}  {'order':>5}  {'DD nodes':>8}  {'max bond':>8}   bond dimensions at each cut")
for n in (6, 8, 10, 12):
    good = tuple(range(1, n + 1))
    bad = tuple(range(1, n + 1, 2)) + tuple(range(2, n + 1, 2))
    for name, o in (('good', good), ('bad', bad)):
        size, _ = dd_size(o, n)
        dims = bond_dimensions(amplitudes(o, n), n)
        print(f"{n:>3}  {name:>5}  {size:>8}  {max(dims):>8}   {dims}")

# ------------------------------------------- do the two objectives ever disagree?
print("\nAll 720 permutations at n=6, scored both ways:")
rows = []
for o in permutations(range(1, 7)):
    size, _ = dd_size(o, 6)
    rows.append((size, max(bond_dimensions(amplitudes(o, 6), 6)), o))
best_by_nodes = min(rows, key=lambda r: r[0])
best_by_bond = min(rows, key=lambda r: r[1])
print(f"  best by DD node count : {best_by_nodes[0]} nodes, max bond {best_by_nodes[1]}, order {best_by_nodes[2]}")
print(f"  best by bond dimension: {best_by_bond[0]} nodes, max bond {best_by_bond[1]}, order {best_by_bond[2]}")
pairs = sorted({(s, b) for s, b, _ in rows})
print(f"  distinct (nodes, max bond) pairs seen: {pairs}")
