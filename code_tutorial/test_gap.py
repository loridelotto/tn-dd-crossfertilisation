import numpy as np, evdd
from itertools import product

rows = {(0,0):[1,0,0,0], (0,1):[0,1,0,0], (1,0):[1,1,0,0], (1,1):[1,-1,0,0]}
f = {}
for (a,b),row in rows.items():
    for (c,d),v in zip(product([0,1],repeat=2), row):
        f[(a,b,c,d)] = float(v)

M = np.array([rows[k] for k in [(0,0),(0,1),(1,0),(1,1)]], float)
evdd.reset(); e = evdd.from_amplitudes(f, 4)
for a in product([0,1],repeat=4):
    assert abs(evdd.amplitude(e,a) - f[a]) < 1e-12
print("matricisation M (cut after x1x2):\n", M)
print("distinct rows (= EVDD width at level 3):", evdd.width(e,4)[2])
print("rank of M (= TT bond dimension there):", np.linalg.matrix_rank(M))
print("singular values:", np.round(np.linalg.svd(M, compute_uv=False), 4))
