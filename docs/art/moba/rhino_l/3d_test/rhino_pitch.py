"""Measure the drawing pitch of the approved rhino views (Claude, 3D test lane, 2026-11-04).
Same method as the drone (minion_s/take-a/3d_test/voxel_build.py): carve the five views and their mirrors at
each pitch, with each turned view's axis nudged to fit, and keep the pitch where the solid explains most of
every silhouette. One voxel per texel; the feet row 160 is the ground. Writes pitch_fit.json."""
import json, os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "..", "take-a", "views")
DRAWN = {"s": 0, "se": 45, "e": 90, "ne": 135, "n": 180}
views = {}
for n, yaw in DRAWN.items():
    a = np.array(Image.open(os.path.join(V, n + ".png")).convert("RGBA"))
    m = a[:, :, 3] > 0
    xs = np.nonzero(m)[1]
    views[n] = dict(yaw=yaw, mask=m, axis=(xs.min() + xs.max()) / 2)
    if n not in ("s", "n"):
        views[n + "_m"] = dict(yaw=360 - yaw, mask=m[:, ::-1].copy(), axis=191 - (xs.min() + xs.max()) / 2)
S = 2  # coarse voxels (2 texels) for the scan
ga, gb, gc = np.meshgrid(np.arange(-70, 70, S) + S / 2, np.arange(-44, 44, S) + S / 2, np.arange(0, 84, S) + S / 2, indexing="ij")
A, B, C = ga.ravel(), gb.ravel(), gc.ravel()
def proj(v, p, dx):
    f, pr = np.radians(v["yaw"]), np.radians(p)
    x = A * np.sin(f) - B * np.cos(f); t = A * np.cos(f) + B * np.sin(f)
    return np.floor(v["axis"] + 0.5 + dx + x).astype(int), np.floor(161 - (C * np.cos(pr) - t * np.sin(pr))).astype(int)
def score(p, offs):
    keep = np.ones(A.size, bool); P = {}
    for n, v in views.items():
        col, row = proj(v, p, offs.get(n, 0)); P[n] = (col, row)
        ok = (col >= 0) & (col < 192) & (row >= 0) & (row < 192)
        ins = np.zeros(A.size, bool); ins[ok] = v["mask"][row[ok], col[ok]]; keep &= ins
    out = []
    for n, v in views.items():
        col, row = P[n]; cov = np.zeros((192, 192), bool)
        for dy in range(S):
            for dxx in range(S):
                r, c = np.clip(row[keep] - dy, 0, 191), np.clip(col[keep] + dxx, 0, 191)
                cov[r, c] = True
        out.append((cov & v["mask"]).sum() / v["mask"].sum())
    return float(np.mean(out))
res = []
for p in range(0, 21, 2):
    offs = {}
    for it in range(2):
        for n in ("se", "e", "ne"):
            rng = range(-14, 15, 2) if it == 0 else [offs.get(n, 0) + d for d in (-1, 0, 1)]
            best = max((score(p, dict(offs, **{n: d, n + "_m": -d})), d) for d in rng)
            offs[n], offs[n + "_m"] = best[1], -best[1]
    sc = score(p, offs)
    res.append({"pitch": p, "explained": round(sc, 4), "axis_nudges": {k: offs[k] for k in ("se", "e", "ne")}})
    print(res[-1], flush=True)
json.dump(res, open(os.path.join(HERE, "pitch_fit.json"), "w"), indent=1)
