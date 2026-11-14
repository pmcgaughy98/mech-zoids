"""Prepare one machine's cam35 working folder (fleet redraw lane, Claude, 2026-11-04).

Usage: python prep_machine.py TAKE_DIR APPROVED_SUBDIR "hex:role:shade,hex:role:shade,..." EYE_HEXES ACCENT_HEX
Writes TAKE_DIR/cam35/refs/approved_views.png (s, se, e, ne, n on magenta at 4x, one baseline),
TAKE_DIR/cam35/palette.json, TAKE_DIR/cam35/refs/angle_guide.png and guide_sizes.txt (hull_guide.py, 6 and 35 degrees),
and prints the approved sizes, colours, accent share and eye groups per view. Reads the approved views; never writes them.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

TAKE, SUB, PAL, EYES, ACC = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
V = ["s", "se", "e", "ne", "n"]
OUT = TAKE / "cam35"
(OUT / "refs").mkdir(parents=True, exist_ok=True)
K, PAD, GAP = 4, 24, 48
ims = [Image.open(TAKE / SUB / f"{v}.png").convert("RGBA") for v in V]
crops = [i.crop(i.getbbox()) for i in ims]
H = max(c.height for c in crops) * K + 2 * PAD
W = sum(c.width * K for c in crops) + GAP * 4 + 2 * PAD
sheet = Image.new("RGB", (W, H), (255, 0, 255))
x = PAD
for c in crops:
    big = c.resize((c.width * K, c.height * K), Image.NEAREST)
    sheet.paste(big, (x, H - PAD - big.height), big)
    x += big.width + GAP
sheet.save(OUT / "refs" / "approved_views.png")
pal = [dict(zip(("hex", "role", "shade"), e.split(":"))) for e in PAL.split(",")]
(OUT / "palette.json").write_text("[\n" + ",\n".join(json.dumps(p) for p in pal) + "\n]\n")
palset = {p["hex"] for p in pal}
rgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
eyes = [rgb(h) for h in EYES.split(",")]
used = {}
for v, im in zip(V, ims):
    a = np.asarray(im)
    op = a[..., 3] > 0
    for c in a[op][:, :3]:
        k = "%02x%02x%02x" % tuple(c)
        used[k] = used.get(k, 0) + 1
    ys, xs = np.nonzero(op)
    acc = np.all(a[..., :3] == rgb(ACC), axis=2)[op].mean() * 100
    g = np.zeros(op.shape, bool)
    for e in eyes:
        g |= np.all(a[..., :3] == e, axis=2)
    g &= op
    lab, n = ndimage.label(g, structure=np.ones((3, 3)))
    comps = sorted((int((lab[sl] == i).sum()), sl[0].start, sl[0].stop - 1, sl[1].start, sl[1].stop - 1)
                   for i, sl in enumerate(ndimage.find_objects(lab), 1))[::-1]
    print(f"{v:>2} {xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1} rows {ys.min()}-{ys.max()} cols {xs.min()}-{xs.max()} "
          f"accent {acc:.1f}% eye px {int(g.sum())} groups (px,y0,y1,x0,x1) {comps[:5]}")
print("colours used", len(used), "not in palette:", {k: n for k, n in used.items() if k not in palset},
      "palette unused:", [h for h in palset if h not in used])
r = subprocess.run([sys.executable, str(Path(__file__).parent / "hull_guide.py"), "guide", str(TAKE / SUB),
                    str(OUT / "refs" / "angle_guide.png"), "6", "35"], capture_output=True, text=True)
(OUT / "guide_sizes.txt").write_text(r.stdout)
print(r.stdout.strip() or r.stderr.strip())
