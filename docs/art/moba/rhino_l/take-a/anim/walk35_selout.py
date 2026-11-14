"""Sel-out for the rhino walk at 35 degrees, ready for pack_rhino_3d.py (Claude, animation lane, 2026-11-04).

Preston: "Yes, pack it". Reads walk35/walk/frames/<s|se|e|ne|n>_f0-7.png (the approved walk: Codex run 1 cleaned,
run 2) and writes walk35/walk/frames_selout/<front|se|side|ne|back>_f0-7.png with selout_rhino.selout, the names the
packer's VIEWS use. Rerun after any fix to the frames, then repack (pack() only).
"""
from pathlib import Path

import numpy as np
from PIL import Image

from selout_rhino import selout

ANIM = Path(__file__).resolve().parent
SRC = ANIM / "walk35" / "walk" / "frames"
DST = ANIM / "walk35" / "walk" / "frames_selout"
NAMES = {"s": "front", "se": "se", "e": "side", "ne": "ne", "n": "back"}


def main():
    DST.mkdir(exist_ok=True)
    for v, name in NAMES.items():
        for i in range(8):
            a = np.asarray(Image.open(SRC / f"{v}_f{i}.png").convert("RGBA"))
            Image.fromarray(selout(a)[0]).save(DST / f"{name}_f{i}.png")
    print(len(list(DST.glob("*_f[0-7].png"))), "frames in", DST)


if __name__ == "__main__":
    main()
