# Reference sheet (Claude, 2026-10-12): for each machine, the installed e view, a candidate round's e view and
# Preston's reference, all scaled to one height, one row per machine.
#   python tools/art/reference_sheet.py <out.png> <id>=<version> [<id>=<version> ...]
import sys
import numpy as np
from PIL import Image, ImageDraw

R = "docs/art/reference/starters"


def crop(p):
    im = Image.open(p).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())


def crop_ref(p):
    im = Image.open(p).convert("RGBA"); a = np.array(im)
    keep = (a[..., 3] > 200) & (a[..., :3].min(2) < 235)
    ys, xs = keep.nonzero()
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def on_grey(im):
    bg = Image.new("RGBA", im.size, (226, 226, 226, 255)); bg.alpha_composite(im); return bg


out, specs = sys.argv[1], [a.split("=") for a in sys.argv[2:]]
H = 250
rows = []
for m, v in specs:
    tiles = []
    for lab, im, filt in (("installed", crop(f"art/machines/{m}/views/e.png"), Image.NEAREST),
                          (v, crop(f"docs/art/2d/{m}/{v}/e.png"), Image.NEAREST),
                          ("reference", crop_ref(f"{R}/{m}.png"), Image.LANCZOS)):
        im = on_grey(im); sc = H / im.height
        tiles.append((lab, im.resize((max(1, int(im.width * sc)), H), filt)))
    rows.append((m, tiles))
W = max(sum(t.width + 14 for _, t in r) for _, r in rows) + 14
sheet = Image.new("RGBA", (W, len(rows) * (H + 44)), (226, 226, 226, 255)); d = ImageDraw.Draw(sheet)
for i, (m, tiles) in enumerate(rows):
    y = i * (H + 44); x = 14
    d.text((14, y + 4), m, fill=(0, 0, 0, 255))
    for lab, t in tiles:
        sheet.alpha_composite(t, (x, y + 20)); d.text((x, y + H + 24), lab, fill=(0, 0, 0, 255)); x += t.width + 14
sheet.save(out); print("sheet", out, sheet.size)
