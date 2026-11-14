"""Model B pass 4 search (Claude, 3D test lane, 2026-11-04). Preston on the cam30 board: "it looks good though
getting close keep refining".

Model B rebuilt from a few shape numbers (dome height, size, centre and front reach; lens radius; barrel length;
pod height), each scored against two targets at once:
- the approved views at their drawn 9 degrees (s, se, e, ne, n and mirrors);
- the factory's cam30 drawing at 35 degrees (s, se and se's mirror).
Score per view = mean of silhouette IoU and material IoU (blue, glow, steel, dark), averaged per target, then the two
targets weighted equally. Coordinate search from pass 3's numbers. Prints the best set; part_build.py takes them by hand.
"""
import json
import sys
import os

import numpy as np
from PIL import Image

import voxel_build as vb

HERE = vb.HERE
N, NC = vb.N, vb.NC
I, J, K = np.meshgrid(np.arange(N), np.arange(N), np.arange(NC), indexing="ij")
A, B, C = I - 48 + 0.5, J - 48 + 0.5, K + 0.5
OFFS9 = {"se": -0.5, "se_m": 0.5, "e": 0.5, "e_m": -0.5, "ne": 1, "ne_m": -1}
CAM35 = {"s": (-1.0, -7.0), "se": (2.0, -6.0), "se_m": (-2.0, -6.0)}  # nudges fitted in cam30_score.py
CLASS = {"blue": 1, "glow": 2, "steel": 3, "charcoal": 4, "seam": 4}
P3 = dict(dome_rc=19, dome_cc=26, dome_s=1.0, dome_front=-3, lens_r=8, barrel_a1=29, pod_dc=0)


def ellipsoid(ca, cb, cc, ra, rb, rc):
    return ((A - ca) / ra) ** 2 + ((B - cb) / rb) ** 2 + ((C - cc) / rc) ** 2 <= 1.0


def rounded_box(a0, a1, b0, b1, c0, c1, r):
    qa = np.maximum(np.maximum(a0 + r - A, A - (a1 - r)), 0)
    qb = np.maximum(np.maximum(b0 + r - B, B - (b1 - r)), 0)
    qc = np.maximum(np.maximum(c0 + r - C, C - (c1 - r)), 0)
    inside = (A >= a0) & (A <= a1) & (B >= b0) & (B <= b1) & (C >= c0) & (C <= c1)
    return inside & (qa ** 2 + qb ** 2 + qc ** 2 <= r * r)


def vcyl(ca, cb, r, c0, c1):
    return ((A - ca) ** 2 + (B - cb) ** 2 <= r * r) & (C >= c0) & (C <= c1)


def fcyl(cb, cc, r, a0, a1):
    return ((B - cb) ** 2 + (C - cc) ** 2 <= r * r) & (A >= a0) & (A <= a1)


def build(p):
    """Material class grid (0 empty) for model B with the shape numbers in p; same parts as part_build.py."""
    g = np.zeros((N, N, NC), np.int8)
    hull = rounded_box(-25, 13, -19, 19, 6, 34, 6) & (np.abs(B) <= 19 - np.clip(14 - C, 0, 8) * 0.6)
    g[hull] = 4
    g[hull & (A > 7) & (np.abs(B) > 11) & (C > 17) & (C < 28)] = 3
    if p.get("face_steel"):  # pass 5 option: steel face round the lens, as the cam30 drawing shows
        g[hull & (A > 7) & (np.abs(B) <= 16) & (C > 14) & (C < 34)] = 3
    g[vcyl(0, 0, 10.5, 3, 7) | vcyl(0, 0, 8.5, 6, 9)] = 4
    g[(np.hypot(A, B) <= 4.5 + 1.4 * C) & (C <= 3.2) & (C >= 0)] = 2
    s = p["dome_s"]
    dome = ellipsoid(-4, 0, p["dome_cc"], 24 * s, 22 * s, p["dome_rc"]) & (C >= 24) & \
        (A < p["dome_front"] + (C - 32) * 1.4)
    g[dome] = 1
    g[rounded_box(-3, 15, -10, 10, 33, 37.5, 2) & ~dome] = 3
    lr = p["lens_r"]
    lc = p.get("lens_c", 27)  # pass 5: lens height; the cam30 drawing sets it about 3 rows lower than B
    g[fcyl(0, lc, lr + 2, 10, 15)] = 4
    g[ellipsoid(14, 0, lc, lr, lr, lr) & (A >= 13)] = 2
    for sb in (-4.3, 4.3):
        g[fcyl(sb, 14.5, 3.8, 6, p["barrel_a1"])] = 3
        g[fcyl(sb, 14.5, 1.9, p["barrel_a1"] - 2, p["barrel_a1"] + 1)] = 4
        g[fcyl(sb, 14.5, 4.1, 17, 19)] = 4
    d = p["pod_dc"]
    for sb in (-27, 27):
        g[vcyl(-7, sb, 7.5, 13 + d, 23.5 + d)] = 3
        g[ellipsoid(-7, sb, 23 + d, 7.5, 7.5, 6.3) & (C >= 23 + d)] = 1
        g[vcyl(-7, sb, 7.0, 11 + d, 13 + d)] = 4
        g[vcyl(-7, sb, 5.5, 8.5 + d, 11 + d)] = 2
    g[rounded_box(-26.5, -18, -11, 11, 11, 24, 2.5) & ~dome] = 3
    return g


def classes_of(rgba):
    h = np.array(["%02x%02x%02x" % tuple(x) for x in rgba[:, :, :3].reshape(-1, 3)]).reshape(rgba.shape[:2])
    out = np.zeros(rgba.shape[:2], np.int8)
    for ramp, hs in vb.RAMPS.items():
        out[np.isin(h, hs)] = CLASS[ramp]
    out[(rgba[:, :, 3] > 0) & (out == 0)] = 4
    return out


def render(g, yaw, pitch, axis, dx, dy):
    occ = g > 0
    pad = np.pad(occ, 1)
    surf = occ & ~(pad[2:, 1:-1, 1:-1] & pad[:-2, 1:-1, 1:-1] & pad[1:-1, 2:, 1:-1] & pad[1:-1, :-2, 1:-1]
                   & pad[1:-1, 1:-1, 2:] & pad[1:-1, 1:-1, :-2])
    si = np.argwhere(surf)
    sub = np.array([[x, y, z] for x in (-0.25, 0.25) for y in (-0.25, 0.25) for z in (-0.25, 0.25)])
    pts = (si[:, None, :] + 0.5 + sub[None]).reshape(-1, 3)
    cl = np.repeat(g[tuple(si.T)], len(sub))
    f, pr = np.radians(yaw), np.radians(pitch)
    a, b, c = pts[:, 0] - 48, pts[:, 1] - 48, pts[:, 2]
    x = a * np.sin(f) - b * np.cos(f)
    t = a * np.cos(f) + b * np.sin(f)
    col = np.floor(axis + 0.5 + dx + x).astype(int)
    row = np.floor(79 + dy - (c * np.cos(pr) - t * np.sin(pr))).astype(int)
    near = t * np.cos(pr) + c * np.sin(pr)
    ok = (col >= 0) & (col < 96) & (row >= 0) & (row < 96)
    o = np.argsort(near)
    o = o[ok[o]]
    img = np.zeros((96, 96), np.int8)
    img[row[o], col[o]] = cl[o]
    return img


def view_score(img, ref):
    sil = ((img > 0) & (ref > 0)).sum() / max(((img > 0) | (ref > 0)).sum(), 1)
    ious = []
    for k in (1, 2, 3, 4):
        u = ((img == k) | (ref == k)).sum()
        if u:
            ious.append(((img == k) & (ref == k)).sum() / u)
    return (sil + np.mean(ious)) / 2


def targets():
    app = vb.load_views("views")
    t9 = {n: (v, classes_of(v["rgba"])) for n, v in app.items()}
    cam = {}
    for n, yaw in (("s", 0), ("se", 45)):
        a = np.array(Image.open(os.path.join(vb.TAKE, "views_cam30", n + ".png")).convert("RGBA"))
        xs = np.nonzero(a[:, :, 3] > 0)[1]
        ax = (xs.min() + xs.max()) / 2
        cam[n] = (dict(yaw=yaw, axis=ax), classes_of(a))
        if n == "se":
            cam["se_m"] = (dict(yaw=315, axis=95 - ax), classes_of(a[:, ::-1].copy()))
    return t9, cam


W35 = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5  # weight on the cam30 drawing (pass 4: 0.5, pass 5: 0.7)
OUT = sys.argv[2] if len(sys.argv) > 2 else "refine_b.json"
P4 = dict(P3, dome_rc=21, dome_s=1.06, barrel_a1=26, pod_dc=1.5, face_steel=0, lens_c=27)


def evaluate(p, t9, cam):
    g = build(p)
    s9 = np.mean([view_score(render(g, v["yaw"], 9, v["axis"], OFFS9.get(n, 0.0), 0.0), ref) for n, (v, ref) in t9.items()])
    s35 = np.mean([view_score(render(g, v["yaw"], 35, v["axis"], *CAM35[n]), ref) for n, (v, ref) in cam.items()])
    return (1 - W35) * s9 + W35 * s35, s9, s35


def main():
    t9, cam = targets()
    grid = dict(dome_rc=[17, 19, 21, 23, 25, 27, 29], dome_cc=[24, 26, 28, 30, 32], dome_s=[0.94, 1.0, 1.06, 1.12, 1.18],
                dome_front=[-6, -3, 0, 3, 6], lens_r=[4.5, 5, 5.5, 6.5, 7, 8], barrel_a1=[17, 20, 23, 26, 29],
                pod_dc=[0, 1.5, 3, 4.5, 6, 7.5], face_steel=[0, 1], lens_c=[21, 22.5, 24, 25.5, 27])
    p = dict(P3 if W35 == 0.5 else P4)
    base = evaluate(p, t9, cam)
    print("pass 3", [round(x, 4) for x in base], flush=True)
    log = [dict(params=dict(p), score=base)]
    for rnd in range(3):
        for k, vals in grid.items():
            best = (evaluate(p, t9, cam), p[k])
            for v in vals:
                if v == p[k]:
                    continue
                q = dict(p, **{k: v})
                sc = evaluate(q, t9, cam)
                if sc[0] > best[0][0] + 1e-4:
                    best = (sc, v)
            p[k] = best[1]
            log.append(dict(params=dict(p), score=best[0]))
            print(rnd, k, best[1], [round(x, 4) for x in best[0]], flush=True)
    json.dump(dict(start=dict(score=base), w35=W35, search=log, best=dict(params=p, score=evaluate(p, t9, cam))),
              open(os.path.join(HERE, OUT), "w"), indent=1)


if __name__ == "__main__":
    main()
