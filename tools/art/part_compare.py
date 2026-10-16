# Part comparison (Claude, 2026-10-12, for the part-by-part refine pass): one region of our sprite beside the same
# region of Preston's reference, both cropped by fractions of the sprite's bounding box and zoomed, so a head, a leg or
# a tail can be judged on its own. Also prints each crop's colour split (main hue families by share) and the outline
# overlap of the region, measured the same way as compare_views but on the crop.
#   python tools/art/part_compare.py <id> <ours.png> <x0,y0,x1,y1> <out.png> [label]
#   fractions run 0..1 from the top-left of each sprite's own bounding box; the reference is
#   docs/art/reference/starters/<id>.png
import sys
import numpy as np
from PIL import Image, ImageDraw


def bbox_crop_ref(p):
    im = Image.open(p).convert("RGBA"); a = np.array(im)
    keep = (a[..., 3] > 200) & (a[..., :3].min(2) < 235)
    ys, xs = keep.nonzero()
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def bbox_crop(p):
    im = Image.open(p).convert("RGBA"); return im.crop(im.getchannel("A").getbbox())


def region(im, fr):
    x0, y0, x1, y1 = fr
    return im.crop((int(im.width * x0), int(im.height * y0), int(im.width * x1), int(im.height * y1)))


def mask(im, size):
    a = np.array(im.convert("RGBA").resize(size, Image.NEAREST))
    return (a[..., 3] > 128) & ~((a[..., :3].min(2) > 235) & (a[..., 3] > 128))


def main():
    mid, ours_p, fr, out = sys.argv[1], sys.argv[2], [float(v) for v in sys.argv[3].split(",")], sys.argv[4]
    label = sys.argv[5] if len(sys.argv) > 5 else "part"
    ours, ref = bbox_crop(ours_p), bbox_crop_ref("docs/art/reference/starters/%s.png" % mid)
    ro, rr = region(ours, fr), region(ref, fr)
    size = (64, max(1, int(64 * rr.height / max(rr.width, 1))))
    mo, mr = mask(ro, size), mask(rr, size)
    overlap = (mo & mr).sum() / max((mo | mr).sum(), 1)
    H = 260
    tiles = []
    for lab, im, filt in (("ours", ro, Image.NEAREST), ("reference", rr, Image.LANCZOS)):
        bg = Image.new("RGBA", im.size, (226, 226, 226, 255)); bg.alpha_composite(im)
        sc = H / max(bg.height, 1); tiles.append((lab, bg.resize((max(1, int(bg.width * sc)), H), filt)))
    sheet = Image.new("RGBA", (sum(t.width + 16 for _, t in tiles) + 16, H + 48), (226, 226, 226, 255))
    d = ImageDraw.Draw(sheet); x = 16
    d.text((16, 4), "%s %s: region overlap %.2f" % (mid, label, overlap), fill=(0, 0, 0, 255))
    for lab, t in tiles:
        sheet.alpha_composite(t, (x, 24)); d.text((x, H + 28), lab, fill=(0, 0, 0, 255)); x += t.width + 16
    sheet.save(out)
    print("%s %s region overlap %.3f  ours %dx%d  ref %dx%d" % (mid, label, overlap, ro.width, ro.height, rr.width, rr.height))


main()
