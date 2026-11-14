"""Hippo walk handoff: look at the walk lane's listed defects at 8x, all 8 frames, the still first (raw, on grey)."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

F = Path(r"D:/dev/new-mech-rpg/docs/art/moba/walk/hippo_l/final")
HERE = Path(__file__).parent
SRC = Path(sys.argv[2]) if len(sys.argv) > 2 else F / "frames"
# (view, box x0, y0, x1, y1) on the 192 canvas, padded around the README's boxes
BOXES = {"se": (36, 104, 74, 146), "ne": (46, 136, 82, 164)}
K = 8


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "before"
    rows = []
    for v, box in BOXES.items():
        imgs = [("still", Image.open(F / f"stills/{v}.png").convert("RGBA"))]
        imgs += [(f"f{i}", Image.open(SRC / f"{v}_f{i}.png").convert("RGBA")) for i in range(8)]
        rows.append((v, box, imgs))
    w = max((b[2] - b[0]) for _, b, _ in rows) * K
    h = max((b[3] - b[1]) for _, b, _ in rows) * K
    B = Image.new("RGBA", (9 * (w + 6) + 10, len(rows) * (h + 22) + 6), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 18
    for v, box, imgs in rows:
        for j, (lab, im) in enumerate(imgs):
            x = 6 + j * (w + 6)
            c = im.crop(box)
            c = c.resize((c.width * K, c.height * K), Image.NEAREST)
            bg = Image.new("RGBA", c.size, (0x5A, 0x60, 0x58, 255))
            bg.alpha_composite(c)
            dd = ImageDraw.Draw(bg)
            for gx in range(0, c.width, 5 * K):          # grid every 5 px, labelled in canvas coords at the edges
                dd.line([(gx, 0), (gx, c.height)], fill=(255, 255, 255, 40))
            for gy in range(0, c.height, 5 * K):
                dd.line([(0, gy), (c.width, gy)], fill=(255, 255, 255, 40))
            B.alpha_composite(bg, (x, y))
            d.text((x, y - 14), f"{v} {lab}  x{box[0]} y{box[1]} (grid 5px)", fill=(235, 235, 230, 255))
        y += h + 22
    B.save(HERE / f"zoom_defects_{tag}.png")
    print(B.size)


if __name__ == "__main__":
    main()
