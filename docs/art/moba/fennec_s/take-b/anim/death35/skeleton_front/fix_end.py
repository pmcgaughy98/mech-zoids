"""Fennec death front f5/f6, fix 3 (Preston: "Fix last 2 death animations btw, still flat. Eyes are grey.").

Start: finished2/front_f5.png. Recolour only (alpha never changes).
1. Relief: the lying body read flat because each plate is one tone top to bottom. Per plate (violet, gold, steel,
   15+ px) and per column, a pixel's place from the plate's top to its bottom picks a target shade (top lit, then
   base, shadow, deepest at the bottom: light from above, as the fleet); each pixel moves ONE step toward it, so
   PixelLab's own detail stays. Ink, charcoal and eyes are never touched.
2. Ground contact: body pixels on the bottom edge at rows 137-140 take their ramp's deepest shade (the weight on
   the floor).
3. Eyes: PixelLab drew them teal, the 15-colour snap made them grey. The raw teal pixels mark where they are; the
   grey (steel) pixels within 1 px of each become the still's eye colours. Listed in eyes.json for the hand pass in
   Aseprite (the eye colours are painted there).
Writes fixed/front_f5_relief.png and eyes.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import finish_death as F  # noqa: E402

M = F.M
OUT = HERE / "fixed"
RAMPS = {r: sorted(hs, key=M._luma) for r, hs in M.ROLES.items() if r in ("violet", "cream-gold", "steel")}
FAMOF = {h: r for r, hs in RAMPS.items() for h in hs}
CUTS = {4: (0.2, 0.5, 0.8), 3: (0.25, 0.65), 2: (0.4,)}


def target_idx(n, t):
    cuts = CUTS[n]
    k = sum(t >= c for c in cuts)      # 0 = top band
    return n - 1 - k                   # top band -> lightest


def relief(h, guard):
    out = h.copy()
    moved = 0
    for fam, rp in RAMPS.items():
        m = np.isin(h, rp) & ~guard
        lab, sizes = M.comps(m, M.N4)
        for k, sz in sizes.items():
            if sz < 15:
                continue
            ys, xs = np.nonzero(lab == k)
            for x in np.unique(xs):
                col = ys[xs == x]
                top, bot = col.min(), col.max()
                if bot - top + 1 < 4:
                    continue
                for y in col:
                    t = (y - top) / (bot - top + 1)
                    cur = rp.index(h[y, x])
                    tgt = target_idx(len(rp), t)
                    if tgt != cur:
                        out[y, x] = rp[cur + (1 if tgt > cur else -1)]
                        moved += 1
    return out, moved


def ground(h, guard):
    n = 0
    H = h.shape[0]
    for y, x in zip(*np.nonzero(h != "")):
        if 137 <= y <= 140 and (y + 1 >= H or h[y + 1, x] == "") and h[y, x] in FAMOF and not guard[y, x]:
            deep = RAMPS[FAMOF[h[y, x]]][0]
            if h[y, x] != deep:
                h[y, x] = deep
                n += 1
    return n


def eyes(h):
    raw = np.asarray(Image.open(HERE / "raw/f5.png").convert("RGBA")).astype(int)
    raw = np.roll(raw, -F.CLEANUP["f5"].get("lifted", 0), 0)
    r, g, b = raw[..., 0], raw[..., 1], raw[..., 2]
    teal = (raw[..., 3] > 0) & (g > r + 40) & (b > r + 20) & (g > 120)
    found = []
    for y, x in zip(*np.nonzero(teal)):
        for j in (-1, 0, 1):
            for i in (-1, 0, 1):
                yy, xx = y + j, x + i
                if h[yy, xx] in RAMPS["steel"] and (int(xx), int(yy)) not in found:
                    found.append((int(xx), int(yy)))
    return [(int(x), int(y)) for y, x in zip(*np.nonzero(teal))], found


def main():
    OUT.mkdir(exist_ok=True)
    a = np.asarray(Image.open(HERE / "finished2/front_f5.png").convert("RGBA"))
    h = M.codes(a)
    teal, grey_eye = eyes(h)
    guard = M.eye_guard(h)
    for x, y in grey_eye:                       # keep the eye pixels out of the relief
        guard[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = True
    h2, moved = relief(h, guard)
    gn = ground(h2, guard)
    b = M.paint(a, h2)
    assert np.array_equal(b[..., 3], a[..., 3])
    Image.fromarray(b).save(OUT / "front_f5_relief.png")
    L = lambda z: (0.2126 * z[..., 0] + 0.7152 * z[..., 1] + 0.0722 * z[..., 2])[z[..., 3] > 0].astype(float).std()
    print("relief moved", moved, "ground px", gn, "| luma spread: still", round(L(F.C.still.astype(float)), 1),
          "f5 before", round(L(a.astype(float)), 1), "after", round(L(b.astype(float)), 1))
    print("raw teal px", teal)
    print("grey eye px", grey_eye, [h[y, x] for x, y in grey_eye])
    (HERE / "eyes.json").write_text(json.dumps({"raw_teal": teal, "grey_eye_px": grey_eye}))


if __name__ == "__main__":
    main()
