"""The proposed 8-direction walk from five drawn directions (Claude, 2026-11-04): front and back from
frontback_fluid.py (walk8f/), side, front three-quarter (se) and back three-quarter (ne) from Retro (frames/,
finished by finish_retro.py). West-facing directions (w, sw, nw) are the east ones mirrored in the engine.
Writes walk5/{view}_f0..f7.png (192, feet on 160, outline under light feet on 161), board-walk5.png and
preview-walk5.gif in compass order s, se, e, ne, n.
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
OUT = HERE / "walk5"
SRC = {"front": HERE / "walk8f", "se": HERE / "frames", "side": HERE / "frames", "ne": HERE / "frames",
       "back": HERE / "walk8f"}
ORDER = ("front", "se", "side", "ne", "back")


def main():
    OUT.mkdir(exist_ok=True)
    rows = {}
    for v in ORDER:
        rows[v] = []
        for i in range(8):
            shutil.copy(SRC[v] / f"{v}_f{i}.png", OUT / f"{v}_f{i}.png")
            rows[v].append(np.asarray(Image.open(OUT / f"{v}_f{i}.png").convert("RGBA")))
    k, crop = 3, (20, 70, 172, 166)
    w, h = (crop[2] - crop[0]) * k, (crop[3] - crop[1]) * k
    board = Image.new("RGBA", (8 * w, len(ORDER) * h), (0x3D, 0x43, 0x50, 255))
    dr = ImageDraw.Draw(board)
    for j, v in enumerate(ORDER):
        for i, a in enumerate(rows[v]):
            board.alpha_composite(Image.fromarray(a).crop(crop).resize((w, h), Image.NEAREST), (i * w, j * h))
            dr.text((i * w + 4, j * h + 2), f"{v} f{i}", fill=(235, 235, 240, 255))
    board.save(OUT / "board-walk5.png")
    gifs = []
    for i in list(range(8)) * 3:
        g = Image.new("RGBA", (len(ORDER) * w, h), (0x3D, 0x43, 0x50, 255))
        for j, v in enumerate(ORDER):
            g.alpha_composite(Image.fromarray(rows[v][i]).crop(crop).resize((w, h), Image.NEAREST), (j * w, 0))
        gifs.append(g.convert("RGB"))
    gifs[0].save(OUT / "preview-walk5.gif", save_all=True, append_images=gifs[1:], duration=125, loop=0)
    print("saved walk5/")


if __name__ == "__main__":
    main()
