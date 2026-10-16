# Eight-view contact sheet for one creature-factory round: python tools/art/creature_sheet.py <machine_id> <version>
import sys
from PIL import Image, ImageDraw
ID, V = sys.argv[1], sys.argv[2]; S = 3; O = f"docs/art/2d/{ID}"


def crop(p):
    im = Image.open(p).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())


tiles = [(f"{V} {v}", crop(f"{O}/{V}/{v}.png")) for v in ("e", "se", "s", "sw", "n", "ne", "nw", "w")]
cols = 4
cw = max(t.width for _, t in tiles) * S + 16
ch = max(t.height for _, t in tiles) * S + 26
sheet = Image.new("RGBA", (cols * cw + 16, 2 * ch + 16), (226, 226, 226, 255))
d = ImageDraw.Draw(sheet)
for i, (n, t) in enumerate(tiles):
    x, y = 16 + (i % cols) * cw, 8 + (i // cols) * ch
    sheet.alpha_composite(t.resize((t.width * S, t.height * S), Image.NEAREST), (x, y + 16))
    d.text((x, y), n, fill=(0, 0, 0, 255))
sheet.save(f"{O}/compare_{V}.png")
print("sheet", f"{O}/compare_{V}.png")
