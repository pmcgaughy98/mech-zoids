"""Lengthen the visor in the gorilla's cam35 se view (gorilla camera-angle lane, Claude, 2026-11-04).

Preston: "Yes, fix visor". Game feel's turn test: the se visor "reads small at game size: a few green pixels at the head's
right edge". Codex drew 8 glow pixels in the slit (floor 12, expected 14 = approved 17 x cos 35 / cos 6).
The slit is the dark band on row 86 under the brow (x 94 to 105). The approved se has two lenses with a gap: a near lens
of 11 px and a far lens of 6. This fills the slit the same way, at the cam35 position:
  - row 86: near lens x 95 to 99 (green, two glow-highlight pixels at 96 and 97), gap at 100 and 101, far lens 102 to 104;
  - row 87: far lens gets one dark-glow pixel under it at x 103; the near lens row (96 to 99) is Codex's, kept;
  - row 88: Codex's single dark-glow pixel at x 98, kept.
Only the three glow colours already in the palette are used. The outline, brow and muzzle are untouched.
Works from Codex's original (se_codex_original.png), so it can be rerun. slices/ keeps Codex's output.
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
VIEW = HERE / "take1_views" / "se.png"  # take 1 is kept here; views_cam35 now holds take 2
ORIG = HERE / "se_codex_original.png"
if not ORIG.exists():
    ORIG.write_bytes(VIEW.read_bytes())
a = np.asarray(Image.open(ORIG).convert("RGBA")).copy()

G, H, I = (0x3F, 0xE0, 0x7F, 255), (0x1B, 0x9A, 0x52, 255), (0xD6, 0xFF, 0xE6, 255)
PAINT = {
    (86, 95): G, (86, 96): I, (86, 97): I, (86, 98): G, (86, 99): G,
    (86, 102): H, (86, 103): G, (86, 104): G,
    (87, 103): H,
}
for (y, x), c in PAINT.items():
    assert a[y, x, 3] == 255, (y, x)  # paint only inside the silhouette
    a[y, x] = c
Image.fromarray(a).save(VIEW)


def glow(arr):
    rgb = arr[..., :3].astype(int) @ [65536, 256, 1]
    return (arr[..., 3] > 0) & np.isin(rgb, [0x1B9A52, 0x3FE07F, 0xD6FFE6])


def visor(arr, box):
    x0, y0, x1, y1 = box
    g = glow(arr)[y0:y1, x0:x1]
    lab, n = ndimage.label(g, structure=np.ones((3, 3)))
    big = max((int((lab == k).sum()) for k in range(1, n + 1)), default=0)
    return int(g.sum()), big


appr = np.asarray(Image.open(HERE.parent / "views" / "se.png").convert("RGBA"))
before = np.asarray(Image.open(ORIG).convert("RGBA"))
at, ab = visor(appr, (91, 82, 104, 87))
bt, bb = visor(before, (94, 84, 105, 90))
nt, nb = visor(a, (94, 84, 105, 90))
exp_t, exp_b = at * 0.82, ab * 0.82
print(f"approved se visor: {at} px in the slit, largest lens {ab}")
print(f"expected at 35 deg: {exp_t:.1f} (floor {exp_t * 0.85:.1f}), largest lens {exp_b:.1f} (floor {exp_b * 0.85:.1f})")
print(f"cam35 se before: {bt} px, largest lens {bb}")
print(f"cam35 se after:  {nt} px, largest lens {nb} -> "
      f"{'PASS' if nt >= exp_t * 0.85 and nb >= exp_b * 0.85 else 'MISS'}")
changed = int(np.any(a != before, axis=2).sum())
print(f"pixels changed: {changed}; opaque count unchanged: {int((a[..., 3] > 0).sum()) == int((before[..., 3] > 0).sum())}")

# before / after, head crop at 8x, side by side
crop = (84, 72, 116, 100)
tiles = [Image.fromarray(x).crop(crop) for x in (appr, before, a)]
W, Hh = tiles[0].size
out = Image.new("RGBA", (W * 3 * 8 + 16, Hh * 8), (40, 40, 48, 255))
for i, t in enumerate(tiles):
    out.alpha_composite(t.resize((W * 8, Hh * 8), Image.NEAREST), (i * (W * 8 + 8), 0))
out.save(HERE / "se_visor_before_after.png")
print("wrote se_visor_before_after.png (approved | Codex | fixed)")
