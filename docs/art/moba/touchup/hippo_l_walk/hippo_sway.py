"""Hippo walk, touch-up step 2: body sway and bob, every foot pinned (walk lane hand-off, Preston: "Approve, to
touch-up"; the sway values were agreed with the walk lane, Preston judges).

Same idea as the fennec trot (fennec_s_walk/sway.py, kept by Preston), but the hippo's feet stand at very different
heights in the 3/4 views (se RH on row 135, ne RF on row 136), so a bottom-rows lock does not work. Instead every
visible foot is pinned by its own box, from walk/hippo_l/final/targets.json (per-frame sole centre) and feet.json
(sole width):
  weight w(y, x) = min over the visible feet of max(vertical, horizontal)
    vertical   : 0 at and below (sole row - LOCK), rising to 1 over the leg up to the hip line (8 rows for a foot
                 standing high above the ground)
    horizontal : 0 inside the foot's columns, rising to 1 over FEATHER px to either side
  each output pixel takes the source pixel at (y - dy*w, x - dx*w): nothing is cut, legs bend, feet stay put.
Lean R = -1 0 +1 +1 +1 0 -1 -1 (character's right +), screen x -R in s and se, +R in n and ne, 0 in e.
Bob 0 1 1 0 0 1 1 0 (down), on top of the walk lane's 1 px dip on f0 and f4.
Input: clean/ (hippo_clean.py). Writes sway/<v>_f0-7.png, sway_report.json, board_hippo_sway.png,
hippo_walk_sway_<v>.gif and hippo_walk_compare.gif (before | after, all five views).
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_fill_holes, distance_transform_edt, label

HERE = Path(__file__).parent
F = Path(r"D:/dev/new-mech-rpg/docs/art/moba/walk/hippo_l/final")
FEET = Path(r"D:/dev/new-mech-rpg/docs/art/moba/walk/hippo_l/feet.json")
LAYERS = Path(r"D:/dev/new-mech-rpg/docs/art/moba/walk/hippo_l")
RUN = {"s": "run2", "n": "run2", "se": "run1", "e": "run1", "ne": "run1"}   # README: which Codex run each view came from
FOOT_ROWS = 10  # the whole foot pad: the leg layer's pixels this many rows up from the sole are rigid
sys.path.insert(0, r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim")
import selout_rhino  # noqa: E402

VIEWS = ["s", "se", "e", "ne", "n"]
N, C = 8, 192
R = [-1, 0, 1, 1, 1, 0, -1, -1]
SIGN = {"s": -1, "se": -1, "e": 0, "ne": 1, "n": 1}
DY = [0, 1, 1, 0, 0, 1, 1, 0]
LOCK = 6        # rows of each foot kept exactly (the pad and ankle)
FEATHER = 4
HIGH_SPAN = 8   # fade length for a foot standing far above the ground
DARK = {"141218", "211e27", "2e1a6e", "3d3a44"}


def A(p):
    return np.asarray(Image.open(p).convert("RGBA"))


def hexc(p):
    return "%02x%02x%02x" % tuple(int(v) for v in p[:3])


def hip_row(a):
    """A couple of rows above the belly: going up from the feet, the first row whose opaque width reaches 60% of the
    widest row (the legs are narrow runs below it)."""
    m = a[..., 3] > 0
    width = m.sum(1)
    ys = np.nonzero(width)[0]
    for y in range(int(ys.max()), int(ys.min()), -1):
        if width[y] >= 0.6 * width.max():
            return y - 2
    return int(ys.max()) - 20


def weights(v, i, tg, feet, hip):
    y, x = np.mgrid[0:C, 0:C].astype(float)
    w = np.ones((C, C))
    pins = []
    for foot, d in tg["views"][v]["visible_feet"].items():
        cx, cy = d["frames"][i]["sole_centre"]
        x0, x1, _ = feet["views"][v][foot]
        hw = (x1 - x0) / 2
        top = cy - LOCK
        span = max(top - hip, 3) if cy >= 150 else HIGH_SPAN
        wv = np.clip((top - y) / span, 0, 1)
        wh = np.clip((np.abs(x - cx) - hw - 1) / FEATHER, 0, 1)
        w = np.minimum(w, np.maximum(wv, wh))
        # the foot itself: its leg layer's lowest FOOT_ROWS rows (plus 1 px) stay rigid, with a feather around them
        lp = LAYERS / RUN[v] / "walk/layers" / f"{v}_{foot}_f{i}.png"
        if lp.exists():
            pad = A(lp)[..., 3] > 0
            pad[:int(cy) - FOOT_ROWS] = False
            pad = binary_dilation(pad, iterations=1)
            w = np.minimum(w, np.clip(distance_transform_edt(~pad) / FEATHER, 0, 1))
        pins.append((foot, round(cx, 1), round(cy, 1), round(hw + 1, 1)))
    return w, pins


def warp(a, w, dx, dy):
    y, x = np.mgrid[0:C, 0:C]
    sy = np.clip(np.floor(y - dy * w + 0.5).astype(int), 0, C - 1)
    sx = np.clip(np.floor(x - dx * w + 0.5).astype(int), 0, C - 1)
    return a[sy, sx].copy()


def fill_pinholes(a, before_holes):
    m = a[..., 3] > 0
    lab, n = label(binary_fill_holes(m) & ~m)
    filled = 0
    for k in range(1, n + 1):
        pc = lab == k
        if pc.sum() > 8 or (pc & before_holes).any():
            continue
        nb = Counter()
        for yy, xx in zip(*np.nonzero(pc)):
            for oy, ox in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                if m[yy + oy, xx + ox]:
                    nb[hexc(a[yy + oy, xx + ox])] += 1
        dk = [c for c in nb if c in DARK]
        c = max(dk, key=nb.get) if dk else nb.most_common(1)[0][0]
        a[pc, :3] = [int(c[j:j + 2], 16) for j in (0, 2, 4)]
        a[pc, 3] = 255
        filled += int(pc.sum())
    return filled


def main():
    tg = json.loads((F / "targets.json").read_text())
    feet = json.loads(FEET.read_text())
    (HERE / "sway").mkdir(exist_ok=True)
    src = {v: [A(HERE / f"clean/{v}_f{i}.png") for i in range(N)] for v in VIEWS}
    new, rep = {}, {"R": R, "DY": DY, "lock": LOCK, "feather": FEATHER, "views": {}}
    for v in VIEWS:
        hip = hip_row(src[v][0])
        dx = [SIGN[v] * r for r in R]
        rows, fr = [], []
        for i in range(N):
            a = src[v][i]
            w, pins = weights(v, i, tg, feet, hip)
            b = warp(a, w, dx[i], DY[i])
            m0 = a[..., 3] > 0
            holes0 = binary_fill_holes(m0) & ~m0
            filled = fill_pinholes(b, holes0)
            m = b[..., 3] > 0
            locked = w == 0
            r = {"dx": dx[i], "dy": DY[i], "pins": pins, "pinholes_filled": filled,
                 "pieces": int(label(m, np.ones((3, 3), int))[1]),
                 "hole_px": int((binary_fill_holes(m) & ~m).sum()), "hole_px_before": int(holes0.sum()),
                 "alpha_binary": bool(set(np.unique(b[..., 3])) <= {0, 255}),
                 "colours_ok": {hexc(p) for p in b[m]} <= {hexc(p) for p in a[m0]},
                 "pinned_px_same": bool(np.array_equal(b[locked], a[locked])),
                 "bottom": int(np.nonzero(m.any(1))[0].max()), "bottom_before": int(np.nonzero(m0.any(1))[0].max()),
                 "px": int(m.sum()), "px_before": int(m0.sum())}
            r["pass"] = (r["pieces"] == 1 and r["hole_px"] <= r["hole_px_before"] and r["alpha_binary"]
                         and r["colours_ok"] and r["pinned_px_same"] and r["bottom"] == r["bottom_before"])
            rows.append(r)
            fr.append(b)
            Image.fromarray(b).save(HERE / f"sway/{v}_f{i}.png")
        new[v] = fr
        rep["views"][v] = {"hip": hip, "frames": rows}
        print(v, "hip", hip, "dx", dx, "pass", [r["pass"] for r in rows], "pieces", [r["pieces"] for r in rows],
              "holes", [(r["hole_px_before"], r["hole_px"]) for r in rows], "filled", [r["pinholes_filled"] for r in rows],
              "px", [r["px"] - r["px_before"] for r in rows])
    rep["all_pass"] = all(r["pass"] for v in VIEWS for r in rep["views"][v]["frames"])
    print("ALL PASS", rep["all_pass"])
    (HERE / "sway_report.json").write_text(json.dumps(rep, indent=1))
    pictures(src, new)


def pictures(src, new):
    still = A(F / "stills/s.png")
    ink = min({hexc(p) for p in still[still[..., 3] > 0]}, key=lambda c: sum(int(c[j:j + 2], 16) for j in (0, 2, 4)))
    selout_rhino.OUTLINE = np.array([int(ink[j:j + 2], 16) for j in (0, 2, 4)])
    grey = (0x5A, 0x60, 0x58, 255)
    k = 3
    boxes = {}
    for v in VIEWS:
        al = np.zeros((C, C), bool)
        for a in src[v] + new[v]:
            al |= a[..., 3] > 0
        ys, xs = np.nonzero(al)
        boxes[v] = (int(xs.min()) - 3, int(ys.min()) - 3, int(xs.max()) + 4, int(ys.max()) + 4)

    def tile(a, box, kk):
        c = Image.fromarray(selout_rhino.selout(a)[0]).crop(box)
        return c.resize((c.width * kk, c.height * kk), Image.NEAREST)

    W = max(b[2] - b[0] for b in boxes.values()) * k
    Hh = max(b[3] - b[1] for b in boxes.values()) * k
    B = Image.new("RGBA", (90 + 8 * (W + 6), 2 * len(VIEWS) * (Hh + 8) + 10), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 6
    for v in VIEWS:
        for lab, fr in (("before", src[v]), ("sway", new[v])):
            d.text((6, y + 6), f"{v} {lab}", fill=(235, 235, 230, 255))
            for i, a in enumerate(fr):
                x = 90 + i * (W + 6)
                d.rectangle([x, y, x + W, y + Hh], fill=grey)
                B.alpha_composite(tile(a, boxes[v], k), (x, y))
            y += Hh + 8
    B.save(HERE / "board_hippo_sway.png")
    gif = []
    k2 = 2
    for i in range(N):
        G = Image.new("RGBA", (len(VIEWS) * (W // k * k2 + 8) + 8, 2 * (Hh // k * k2 + 18) + 4), grey)
        dd = ImageDraw.Draw(G)
        for j, v in enumerate(VIEWS):
            x = 8 + j * (W // k * k2 + 8)
            for r, (lab, fr) in enumerate((("before", src[v]), ("sway", new[v]))):
                yy = 4 + r * (Hh // k * k2 + 18)
                dd.text((x, yy), f"{v} {lab}", fill=(235, 235, 230, 255))
                G.alpha_composite(tile(fr[i], boxes[v], k2), (x, yy + 14))
        gif.append(G.convert("RGB"))
    gif[0].save(HERE / "hippo_walk_compare.gif", save_all=True, append_images=gif[1:], duration=125, loop=0)
    for v in VIEWS:
        fr = []
        for a in new[v]:
            t = tile(a, boxes[v], k)
            G = Image.new("RGBA", (t.width + 10, t.height + 10), grey)
            G.alpha_composite(t, (5, 5))
            fr.append(G.convert("RGB"))
        fr[0].save(HERE / f"hippo_walk_sway_{v}.gif", save_all=True, append_images=fr[1:], duration=125, loop=0)


if __name__ == "__main__":
    main()
