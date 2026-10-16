"""Compare our sprite views with Preston's reference views, number by number (Claude, 2026-10-12).

    python tools/art/compare_views.py <ours.png> <reference.png> <overlay_out.png>

Both are cropped to their outline and scaled to the same height. Prints:
  outline overlap (intersection over union),
  width at ten height bands, as a share of height (top of the sprite first), ours vs his,
  colour split (green / grey / orange) of the painted pixels, outline left out.
The overlay: grey = both, red = reference only (we are missing it), blue = ours only (we have extra).
"""
import colorsys, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadow_strip
import numpy as np
from PIL import Image

H = 120


def load(path):
    im = shadow_strip.strip(Image.open(path).convert("RGBA"))   # 2026-10-13: the ground-shadow line is not the creature
    im = im.crop(im.getchannel("A").point(lambda a: 255 if a > 128 else 0).getbbox())
    w = int(round(im.width * H / im.height))
    return np.array(im.resize((w, H), Image.NEAREST)).astype(int)


def split(a):
    g = gr = o = 0
    for px in a[a[..., 3] > 128][:, :3]:
        if px.sum() < 90:
            continue   # outline
        h, s, v = colorsys.rgb_to_hsv(*(px / 255.0))
        if s < 0.22: gr += 1
        elif 0.02 <= h <= 0.15: o += 1
        elif 0.15 < h < 0.45: g += 1
        else: gr += 1
    t = max(g + gr + o, 1)
    return 100 * g / t, 100 * gr / t, 100 * o / t


def main(ours, ref, out):
    a, b = load(ours), load(ref)
    W = max(a.shape[1], b.shape[1])
    pad = lambda m: np.pad(m, ((0, 0), ((W - m.shape[1]) // 2, W - m.shape[1] - (W - m.shape[1]) // 2), (0, 0)))
    a, b = pad(a), pad(b)
    ma, mb = a[..., 3] > 128, b[..., 3] > 128
    iou = (ma & mb).sum() / max((ma | mb).sum(), 1)
    print("outline overlap %.3f   width/height ours %.2f his %.2f" % (iou, ma.any(0).sum() / H, mb.any(0).sum() / H))
    print("width per height band (share of height), top first:")
    for k in range(10):
        rows = slice(k * H // 10, (k + 1) * H // 10)
        wa = ma[rows].any(0).sum() / H
        wb = mb[rows].any(0).sum() / H
        print("  band %d  ours %.2f  his %.2f  %s" % (k + 1, wa, wb, "wider" if wa > wb + 0.08 else "narrower" if wa < wb - 0.08 else ""))
    print("colour split ours %.0f / %.0f / %.0f   his %.0f / %.0f / %.0f  (green / grey / orange)" % (split(a) + split(b)))
    img = np.full(ma.shape + (3,), 240, np.uint8)
    img[ma & mb] = (150, 150, 150)
    img[mb & ~ma] = (215, 50, 50)
    img[ma & ~mb] = (50, 100, 215)
    Image.fromarray(img).resize((W * 3, H * 3), Image.NEAREST).save(out)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
