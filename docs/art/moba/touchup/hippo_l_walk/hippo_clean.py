"""Hippo walk, touch-up step 1: clean the walk lane's listed defects (README in walk/hippo_l/final), before the sway.

Why they exist: Codex's body layer (run1/source/<v>_body.png) was painted solid under the still's legs. Where a leg
steps away, that hidden fill shows as a dark block hanging below the belly. So the rule, inside each listed box only:
  Codex cut the shadow side of the near leg into the body layer (a straight vertical edge, se x 61, ne x 68), so
  when the leg moves that strip hangs below the belly. A frame pixel in the box is cleared when it is body layer
  (shifted by the frame's dip), not covered by any of the frame's leg layers, and below the belly line (below_belly).
se specks box: loose pieces of 4 px or less that belong to no leg layer are cleared.
ne LH pad: where the LH leg layer is light (pad greys or lilac) and the frame shows a dark colour, the layer's colour
wins (the dark split line), within the listed box.
Then enclosed holes of 8 px or less are filled with their most common dark neighbour (as on the fennec trot).
Writes clean/<v>_f0-7.png for all five views (s, e, n copied unchanged) and clean_report.json.
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes, label

H = Path(r"D:/dev/new-mech-rpg/docs/art/moba/walk/hippo_l")
F = H / "final"
HERE = Path(__file__).parent
LEGS = ["LF", "LH", "RF", "RH"]
DARK = {"141218", "211e27", "2e1a6e", "3d3a44"}
BOX_FILL = {"se": (55, 124, 70, 142), "ne": (62, 145, 78, 162)}       # x0, y0, x1, y1 inclusive
BOX_SPECK = {"se": (41, 111, 50, 122)}
BOX_PAD = {"ne": (52, 144, 60, 160)}


def A(p):
    return np.asarray(Image.open(p).convert("RGBA"))


def hexc(p):
    return "%02x%02x%02x" % tuple(int(v) for v in p[:3])


def boxmask(b):
    m = np.zeros((192, 192), bool)
    m[b[1]:b[3] + 1, b[0]:b[2] + 1] = True
    return m


def shift(m, dy):
    return np.roll(m, dy, 0) if dy else m


def body_dip(fr, body):
    """Rows the body layer sits lower in this frame (0 or 1), from the upper body where no legs are."""
    top = np.zeros_like(body)
    top[:110] = True
    best = max((0, 1, 2), key=lambda d: int((shift(body, d) & top & (fr[..., 3] > 0)).sum())
               - int((shift(body, d) & top & (fr[..., 3] == 0)).sum()))
    return best


def below_belly(v, d):
    """The real belly line, judged at 8x against the still. Codex cut the shadow side of the near leg (se RH, ne LH)
    into the body layer, with a straight edge; whatever of it sits below this line and is not a leg is cleared.
    se: from (58, 127) down to (72, 135.5), the slope of the belly's own edge further right. ne: the belly bottom
    is row 145; only the column hanging under it goes."""
    y, x = np.mgrid[0:192, 0:192]
    if v == "se":
        return (x >= 59) & (y > 127 + (x - 58) * (8.5 / 14) + d)
    return y >= 146 + d


def fill_pinholes(a):
    m = a[..., 3] > 0
    lab, n = label(binary_fill_holes(m) & ~m)
    filled = 0
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) > 8:
            continue
        nb = Counter()
        for y, x in zip(ys, xs):
            for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                if m[y + dy, x + dx]:
                    nb[hexc(a[y + dy, x + dx])] += 1
        dk = [c for c in nb if c in DARK]
        c = max(dk, key=nb.get) if dk else nb.most_common(1)[0][0]
        for y, x in zip(ys, xs):
            a[y, x, :3] = [int(c[i:i + 2], 16) for i in (0, 2, 4)]
            a[y, x, 3] = 255
        filled += len(ys)
    return filled


def clean_view(v):
    run = H / "run1"
    still = A(F / f"stills/{v}.png")
    body = A(run / f"source/{v}_body.png")[..., 3] > 0
    sleg = np.zeros_like(body)
    for leg in LEGS:
        for part in ("knee", "lower"):
            sleg |= A(run / f"source/{v}_{leg}_{part}.png")[..., 3] > 0
    svis = (still[..., 3] > 0) & ~sleg
    out, rep = [], []
    for i in range(8):
        fr = A(F / f"frames/{v}_f{i}.png").copy()
        legs = {leg: A(run / f"walk/layers/{v}_{leg}_f{i}.png") for leg in LEGS}
        L = np.zeros_like(body)
        for la in legs.values():
            L |= la[..., 3] > 0
        d = body_dip(fr, body)
        r = {"dip": d, "cleared": 0, "specks": 0, "pad": 0}
        m = fr[..., 3] > 0
        if v in BOX_FILL:
            # a body pixel sitting directly on a leg pixel is the join between belly and leg: keep it (clearing it
            # left a 1 px slot over the ne LH pad, found by walk_tools seams)
            kill = boxmask(BOX_FILL[v]) & m & ~L & shift(body, d) & below_belly(v, d) & ~np.roll(L, -1, 0)
            fr[kill] = 0
            r["cleared"] = int(kill.sum())
        if v in BOX_SPECK:
            m = fr[..., 3] > 0
            lab, n = label(m & ~L & boxmask(BOX_SPECK[v]), np.ones((3, 3), int))
            for k in range(1, n + 1):
                pc = lab == k
                # loose: 4 px or less and not touching any leg pixel or the body outside the box
                if pc.sum() <= 4:
                    fr[pc] = 0
                    r["specks"] += int(pc.sum())
        if v in BOX_PAD:
            la = legs["LH"]
            bm = boxmask(BOX_PAD[v]) & (la[..., 3] > 0) & (fr[..., 3] > 0)
            for y, x in zip(*np.nonzero(bm)):
                if hexc(fr[y, x]) in DARK and hexc(la[y, x]) not in DARK:
                    fr[y, x] = la[y, x]
                    r["pad"] += 1
        r["pinholes_filled"] = fill_pinholes(fr)
        mm = fr[..., 3] > 0
        r["pieces"] = int(label(mm, np.ones((3, 3), int))[1])
        r["holes_left"] = int((binary_fill_holes(mm) & ~mm).sum())
        out.append(fr)
        rep.append(r)
    return out, rep


def main():
    (HERE / "clean").mkdir(exist_ok=True)
    rep = {}
    for v in ("s", "se", "e", "ne", "n"):
        if v in ("se", "ne"):
            fr, rep[v] = clean_view(v)
        else:
            fr = [A(F / f"frames/{v}_f{i}.png") for i in range(8)]
        for i, a in enumerate(fr):
            Image.fromarray(a).save(HERE / f"clean/{v}_f{i}.png")
    (HERE / "clean_report.json").write_text(json.dumps(rep, indent=1))
    for v, rs in rep.items():
        print(v, [(r["dip"], r["cleared"], r["specks"], r["pad"], r["pinholes_filled"], r["pieces"], r["holes_left"])
                  for r in rs])


if __name__ == "__main__":
    main()
