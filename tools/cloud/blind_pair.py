# Blind A/B sheet for a judge (Claude, 2026-10-16, cloud model pass).
#   python tools/cloud/blind_pair.py <ref.png> <dir_1> <dir_2> <swap 0|1> <out.png> [views, default "e se ne s"]
# Puts the reference painting on top, then row A and row B, each the same views at whole-number scale on one grey.
# swap=0: A is dir_1; swap=1: A is dir_2. The caller keeps the key; the sheet carries no file names.
# Also writes <out>_e.png: the two e views alone at x4, side by side, for a closer look.
import sys
from PIL import Image, ImageDraw

ref, d1, d2, swap, out = sys.argv[1:6]
views = (sys.argv[6] if len(sys.argv) > 6 else "e se ne s").split()
a, b = (d2, d1) if swap == "1" else (d1, d2)
BG = (118, 122, 128, 255)


def row(d, k):
    ims = [Image.open("%s/%s.png" % (d, v)).convert("RGBA") for v in views]
    ims = [im.crop(im.getbbox()) for im in ims]
    ims = [im.resize((im.width * k, im.height * k), Image.NEAREST) for im in ims]
    w = sum(im.width for im in ims) + 24 * (len(ims) - 1)
    h = max(im.height for im in ims)
    r = Image.new("RGBA", (w, h), BG)
    x = 0
    for im in ims:
        r.alpha_composite(im, (x, h - im.height))
        x += im.width + 24
    return r


k = 4
ra, rb = row(a, k), row(b, k)
while max(ra.width, rb.width) > 1800 and k > 1:
    k -= 1
    ra, rb = row(a, k), row(b, k)
W = max(ra.width, rb.width) + 80
rim = Image.open(ref).convert("RGBA")
s = min(1.0, (W - 80) / rim.width, 360 / rim.height)
rim = rim.resize((max(1, int(rim.width * s)), max(1, int(rim.height * s))), Image.LANCZOS)
H = rim.height + ra.height + rb.height + 4 * 40
sheet = Image.new("RGBA", (W, H), BG)
dr = ImageDraw.Draw(sheet)
y = 20
dr.text((10, y), "REFERENCE (Preston's painting, the design target)", fill=(255, 255, 255, 255))
sheet.alpha_composite(rim, (60, y + 14)); y += rim.height + 40
dr.text((10, y), "A", fill=(255, 255, 0, 255)); sheet.alpha_composite(ra, (60, y)); y += ra.height + 40
dr.text((10, y), "B", fill=(255, 255, 0, 255)); sheet.alpha_composite(rb, (60, y))
sheet.convert("RGB").save(out)

ea = Image.open("%s/e.png" % a).convert("RGBA"); eb = Image.open("%s/e.png" % b).convert("RGBA")
ea, eb = ea.crop(ea.getbbox()), eb.crop(eb.getbbox())
k = max(1, min(4, 900 // max(ea.width, eb.width)))
ea = ea.resize((ea.width * k, ea.height * k), Image.NEAREST); eb = eb.resize((eb.width * k, eb.height * k), Image.NEAREST)
c = Image.new("RGBA", (ea.width + eb.width + 120, max(ea.height, eb.height) + 40), BG)
d = ImageDraw.Draw(c)
d.text((10, 10), "A", fill=(255, 255, 0, 255)); c.alpha_composite(ea, (30, 30))
d.text((ea.width + 70, 10), "B", fill=(255, 255, 0, 255)); c.alpha_composite(eb, (ea.width + 90, 30))
c.convert("RGB").save(out.replace(".png", "_e.png"))
print("BLIND_PAIR_DONE", out, "k=%d" % k)
