# Stacked overlay of one region (Claude, 2026-10-13, for the kangaroo head detail work): our sprite's region over
# the reference's, both scaled to the same height, grey where both agree, red where only the reference has
# pixels, blue where only ours does; the reference's own art shown beside it for the detail read.
#   python tools/art/part_overlay.py <id> <ours.png> <x0,y0,x1,y1> <out.png>
import sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadow_strip
import numpy as np
from PIL import Image


def bbox_ref(p):
    im = Image.open(p).convert("RGBA"); a = np.array(im)
    keep = (a[..., 3] > 200) & (a[..., :3].min(2) < 235); ys, xs = keep.nonzero()
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def bbox_ours(p):
    return shadow_strip.strip(Image.open(p).convert("RGBA"))   # 2026-10-13: without the ground-shadow line


def region(im, fr):
    x0, y0, x1, y1 = fr
    return im.crop((int(im.width * x0), int(im.height * y0), int(im.width * x1), int(im.height * y1)))


mid, ours_p, fr, out = sys.argv[1], sys.argv[2], [float(v) for v in sys.argv[3].split(",")], sys.argv[4]
ro, rr = region(bbox_ours(ours_p), fr), region(bbox_ref("docs/art/reference/starters/%s.png" % mid), fr)
H = 360; size = (int(rr.width * H / rr.height), H)
mo = np.array(ro.resize(size, Image.NEAREST))[..., 3] > 128
ar = np.array(rr.resize(size, Image.LANCZOS)); mr = (ar[..., 3] > 128) & ~(ar[..., :3].min(2) > 235)
ov = np.full((H, size[0], 4), (226, 226, 226, 255), np.uint8)
ov[mr & ~mo] = (220, 40, 40, 255); ov[mo & ~mr] = (40, 80, 220, 255); ov[mr & mo] = (120, 120, 120, 255)
sheet = Image.new("RGBA", (size[0] * 3 + 40, H + 30), (226, 226, 226, 255))
sheet.alpha_composite(Image.fromarray(ov), (10, 20)); sheet.alpha_composite(rr.resize(size, Image.LANCZOS), (size[0] + 20, 20)); sheet.alpha_composite(ro.resize(size, Image.NEAREST), (size[0] * 2 + 30, 20))
sheet.save(out)
print("%s overlap %.3f  red (reference only) %.1f%%  blue (ours only) %.1f%%" % (mid, (mo & mr).sum() / max((mo | mr).sum(), 1), 100 * (mr & ~mo).sum() / max(mr.sum(), 1), 100 * (mo & ~mr).sum() / max(mo.sum(), 1)))
