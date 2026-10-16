"""Where is the sprite orange and the model not? (Claude, 2026-10-12, pass 25.)
Aligns the build's rear three-quarter colour render (docs/art/3d/silhouette/rear34_color.png) with Preston's sprite
the same way score_ape_vs_sprite.py does (crop to the outline, scale to the same height), then marks:
  red    = orange in the sprite, not in the model (orange to add)
  yellow = orange in both
  blue   = orange in the model only
over a grey outline of the sprite, and prints how the missing orange splits by body region.
  python tools/blender/orange_gap_map.py   ->  docs/art/3d/silhouette/orange_gap.png
"""
import colorsys, os
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPRITE = os.path.join(ROOT, "docs", "art", "ape-rd-2026-10-11", "source_preston_pick.webp")
MODEL = os.path.join(ROOT, "docs", "art", "3d", "silhouette", "rear34_color.png")
OUT = os.path.join(ROOT, "docs", "art", "3d", "silhouette", "orange_gap.png")
H = 300


def load(path):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    mask = a[..., 3] > 128
    ys, xs = np.where(mask)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    w = int(round(a.shape[1] * H / a.shape[0]))
    return np.array(Image.fromarray(a).resize((w, H), Image.NEAREST))


def orange(a):
    rgb = a[..., :3].astype(float) / 255
    out = np.zeros(a.shape[:2], bool)
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if a[y, x, 3] > 128:
                h, s, v = colorsys.rgb_to_hsv(*rgb[y, x])
                out[y, x] = 0.04 <= h <= 0.13 and s > 0.35 and v > 0.3
    return out


s, m = load(SPRITE), load(MODEL)
W = max(s.shape[1], m.shape[1])
pad = lambda a: np.pad(a, ((0, 0), (0, W - a.shape[1]), (0, 0)))
s, m = pad(s), pad(m)
so, mo = orange(s), orange(m)
img = np.full((H, W, 3), 245, np.uint8)
img[s[..., 3] > 128] = (190, 190, 190)
img[so & ~mo] = (220, 40, 40)
img[so & mo] = (240, 200, 30)
img[mo & ~so] = (40, 90, 220)
Image.fromarray(img).resize((W * 2, H * 2), Image.NEAREST).save(OUT)
miss = so & ~mo
regions = {"top third (back, blocks, head)": slice(0, H // 3), "middle third (arms, hips)": slice(H // 3, 2 * H // 3),
           "bottom third (fists, feet, toes)": slice(2 * H // 3, H)}
total = max(1, miss.sum())
print("sprite orange %d px, model orange %d px, both %d px" % (so.sum(), mo.sum(), (so & mo).sum()))
for name, sl in regions.items():
    left, right = miss[sl, :W // 2].sum(), miss[sl, W // 2:].sum()
    print("  missing in %-34s %3d%%  (left half %d, right half %d px)" % (name, 100 * miss[sl].sum() / total, left, right))
print("wrote", OUT)
