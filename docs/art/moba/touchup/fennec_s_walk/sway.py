"""Fennec trot, body sway and bob (Preston: "Add sway to ours", after the Retro test showed the stiffness is the body:
ours 0 px sway and a 1 px dip, legs fine).

Not cut-and-paste: every output pixel is a source pixel moved by a per-row offset that changes smoothly from the
feet up, so nothing is cut and nothing floats.
  rows at or below bottom-7 (the foot lock) : no move
  rows between the hip line and the foot lock: the move fades in linearly (the legs bend)
  rows at or above the hip line              : the frame's (dx, dy)
  ear rows (above the ear base)              : blend toward the previous frame's offset at the tips
                                               (full lag sideways, half lag up and down): follow-through
Motion (s view: screen-left front foot lands f0, right f4):
  sway dx: the body leans over the landing front leg, 2 px each side once per stride
  bob  dy: one per step, added to the walk lane's 1 px dip so the head top reads 98, 99, 98, 97 and repeats
Recolour never happens; colours, ink and eyes move with their rows. Writes frames/, report.json, board_sway.png,
trot_sway_compare.gif, trot_sway_2x.gif.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, label

HERE = Path(__file__).parent
SRC = Path(r"D:/dev/new-mech-rpg/docs/art/moba/touchup/fennec_s_walk/pre_sway/frames")  # the touch-up before sway; never point at frames/ (would sway twice)
sys.path.insert(0, r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim")
from selout_rhino import selout  # noqa: E402

VIEW = sys.argv[1] if len(sys.argv) > 1 else "s"
N = 8
# Walk lane README: RF+LH planted f1-f3, LF+RH planted f5-f7 (both pairs f0 and f4), same timeline in every view.
# The body leans over the planted front leg: toward the character's right on f0-f3, left on f4-f7.
R = [1, 2, 2, 1, -1, -2, -2, -1]
# Screen x of the character's right: s faces the camera (right = screen-left), n away (screen-right),
# ne faces up-right (right = down-right, +x), se faces down-right (right = down-left, -x), e side-on (right = toward
# the camera, no screen x).
SIGN = {"s": -1, "n": 1, "ne": 1, "se": -1, "e": 0}
# Measured per view on f0 (row extents): hip line = a few rows above where the legs split; ear base = where the
# two ears join the head (e: where the ear stops narrowing).
CFG = {"s": (142, 113), "n": (144, 101), "ne": (140, 100), "se": (132, 105), "e": (140, 110)}
DX = [SIGN[VIEW] * r for r in R]
DY = [0, 2, 1, 0, 0, 2, 1, 0]
HIP, EAR_BASE = CFG[VIEW]   # rows at or above HIP move fully; ears above EAR_BASE
LOCK = 8           # bottom rows kept exactly
EYES = {(0x3F, 0xE8, 0xB0), (0xC8, 0xFF, 0xF0), (0xF6, 0xFF, 0xFB)}


def offsets(i, top, bottom):
    """Per-row (ox, oy) for frame i as float arrays over all 192 rows."""
    y = np.arange(192, dtype=float)
    foot = bottom - LOCK              # last row that may move
    t = np.clip((foot - y) / max(foot - HIP, 1), 0, 1)
    ox, oy = DX[i] * t, DY[i] * t
    p = (i - 1) % N
    u = np.clip((EAR_BASE - y) / max(EAR_BASE - top, 1), 0, 1)     # 0 at the ear base, 1 at the tips
    ox = np.where(y < EAR_BASE, DX[i] * (1 - u) + DX[p] * u, ox)
    oy = np.where(y < EAR_BASE, DY[i] * (1 - u) + (DY[i] + DY[p]) / 2 * u, oy)
    return ox, oy


def warp(a, i):
    m = a[..., 3] > 0
    ys = np.nonzero(m.any(1))[0]
    ox, oy = offsets(i, int(ys.min()), int(ys.max()))
    out = np.zeros_like(a)
    for y in range(192):
        sy = int(np.floor(y - oy[y] + 0.5))
        if not 0 <= sy < 192:
            continue
        sx = int(np.floor(ox[y] + 0.5))
        row = a[sy]
        if sx > 0:
            out[y, sx:] = row[:-sx]
        elif sx < 0:
            out[y, :sx] = row[-sx:]
        else:
            out[y] = row
    return out


def check(a, src):
    m = a[..., 3] > 0
    lab, n = label(m, np.ones((3, 3), int))
    holes = int((binary_fill_holes(m) & ~m).sum())
    holes0 = int((binary_fill_holes(src[..., 3] > 0) & ~(src[..., 3] > 0)).sum())
    ys = np.nonzero(m.any(1))[0]
    b = int(ys.max())
    b0 = int(np.nonzero((src[..., 3] > 0).any(1))[0].max())
    eye = [int(((a[..., :3] == c).all(-1) & m).sum()) for c in sorted(EYES)]
    eye0 = [int(((src[..., :3] == c).all(-1) & (src[..., 3] > 0)).sum()) for c in sorted(EYES)]
    pal0 = {tuple(c) for c in src[src[..., 3] > 0][:, :3]}
    return {"pieces": int(n), "hole_px": holes, "hole_px_before": holes0,
            "alpha_binary": bool(set(np.unique(a[..., 3])) <= {0, 255}),
            "colours_subset": {tuple(c) for c in a[m][:, :3]} <= pal0,
            "foot_rows_same": bool(b == b0 and np.array_equal(a[b - LOCK + 1:b + 1], src[b0 - LOCK + 1:b0 + 1])),
            "eye_px": eye, "eye_px_before": eye0, "top": int(ys.min()), "bottom": b,
            "head_x": round(float(np.nonzero(m[ys.min():ys.min() + 30])[1].mean()), 1),
            "px": int(m.sum()), "px_before": int((src[..., 3] > 0).sum())}


def main():
    (HERE / "frames").mkdir(exist_ok=True)
    src = [np.asarray(Image.open(SRC / f"{VIEW}_f{i}.png").convert("RGBA")) for i in range(N)]
    new = [warp(a, i) for i, a in enumerate(src)]
    rep = {"view": VIEW, "dx": DX, "dy": DY, "hip": HIP, "ear_base": EAR_BASE, "lock": LOCK,
           "frames": [check(b, a) for a, b in zip(src, new)]}
    ok = all(r["pieces"] == 1 and r["hole_px"] <= r["hole_px_before"] and r["alpha_binary"] and r["colours_subset"]
             and r["foot_rows_same"] and r["eye_px"] == r["eye_px_before"] for r in rep["frames"])
    rep["all_pass"] = ok
    (HERE / f"report_{VIEW}.json").write_text(json.dumps(rep, indent=1))
    for i, r in enumerate(rep["frames"]):
        print(i, {k: r[k] for k in ("pieces", "hole_px", "foot_rows_same", "eye_px", "top", "bottom", "head_x", "px", "px_before")})
    print("ALL PASS", ok)
    for i, a in enumerate(new):
        Image.fromarray(a).save(HERE / f"frames/{VIEW}_f{i}.png")
    board(src, new)


def board(src, new):
    al = np.zeros((192, 192), bool)
    for a in src + new:
        al |= a[..., 3] > 0
    ys, xs = np.nonzero(al)
    box = (int(xs.min()) - 3, int(ys.min()) - 3, int(xs.max()) + 4, int(ys.max()) + 4)
    grey = (0x5A, 0x60, 0x58, 255)
    k = 4
    cw, ch = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    B = Image.new("RGBA", (230 + N * (cw + 6), 2 * (ch + 24) + 30), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 22
    for lab, fr in (("ours now", src), ("ours + sway and bob", new)):
        d.text((8, y + 6), lab, fill=(235, 235, 230, 255))
        for i, a in enumerate(fr):
            x = 230 + i * (cw + 6)
            d.rectangle([x, y, x + cw, y + ch], fill=grey)
            B.alpha_composite(Image.fromarray(selout(a)[0]).crop(box).resize((cw, ch), Image.NEAREST), (x, y))
            for gy in (int(np.nonzero(src[0][..., 3].any(1))[0].min()), int(np.nonzero(src[0][..., 3].any(1))[0].max())):
                d.line([x, y + (gy - box[1]) * k, x + cw, y + (gy - box[1]) * k], fill=(200, 80, 80, 255))
            if y == 22:
                d.text((x + 4, y - 16), f"f{i}  dx {DX[i]:+d} dy {DY[i]:+d}", fill=(235, 235, 230, 255))
        y += ch + 24
    B.save(HERE / f"board_sway_{VIEW}.png")
    k2 = 3
    bw, bh = (box[2] - box[0]) * k2, (box[3] - box[1]) * k2
    gif, g2 = [], []
    for a, b in zip(src, new):
        G = Image.new("RGBA", (2 * bw + 30, bh + 30), grey)
        dd = ImageDraw.Draw(G)
        dd.text((10, 4), "ours now", fill=(235, 235, 230, 255))
        dd.text((bw + 25, 4), "with sway and bob", fill=(235, 235, 230, 255))
        G.alpha_composite(Image.fromarray(selout(a)[0]).crop(box).resize((bw, bh), Image.NEAREST), (10, 20))
        G.alpha_composite(Image.fromarray(selout(b)[0]).crop(box).resize((bw, bh), Image.NEAREST), (bw + 20, 20))
        gif.append(G.convert("RGB"))
        H = Image.new("RGBA", ((box[2] - box[0]) * 2 + 20, (box[3] - box[1]) * 2 + 20), grey)
        H.alpha_composite(Image.fromarray(selout(b)[0]).crop(box).resize(((box[2] - box[0]) * 2, (box[3] - box[1]) * 2),
                                                                         Image.NEAREST), (10, 10))
        g2.append(H.convert("RGB"))
    gif[0].save(HERE / "trot_sway_compare.gif", save_all=True, append_images=gif[1:], duration=100, loop=0)
    g2[0].save(HERE / "trot_sway_2x.gif", save_all=True, append_images=g2[1:], duration=100, loop=0)


if __name__ == "__main__":
    main()
