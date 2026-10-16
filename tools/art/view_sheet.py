"""One machine's S, SE, E and SW views side by side for Codex's reference images (Claude, 2026-10-14; the format of the
earlier docs/art/2d/sheets/*.png). Nearest-neighbour scale, light grey ground, the view name over each.
    python tools/art/view_sheet.py <machine_id> <version> [scale, default 3]
Writes docs/art/2d/sheets/<machine_id>_<version>.png."""
import os, sys
from PIL import Image, ImageDraw

mid, ver = sys.argv[1], sys.argv[2]
k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
views = [(v, Image.open(os.path.join(root, "docs", "art", "2d", mid, ver, v + ".png")).convert("RGBA")) for v in ("s", "se", "e", "sw")]
pw = max(im.width for _, im in views) * k + 24
ph = max(im.height for _, im in views) * k + 40
sheet = Image.new("RGBA", (pw * len(views), ph), (226, 226, 226, 255))
d = ImageDraw.Draw(sheet)
for i, (v, im) in enumerate(views):
    big = im.resize((im.width * k, im.height * k), Image.NEAREST)
    sheet.alpha_composite(big, (i * pw + (pw - big.width) // 2, ph - big.height - 8))
    d.text((i * pw + 8, 6), "%s  %s %s" % (v.upper(), mid, ver), fill=(60, 60, 60, 255))
out = os.path.join(root, "docs", "art", "2d", "sheets", "%s_%s.png" % (mid, ver))
sheet.save(out)
print(out, sheet.size)
