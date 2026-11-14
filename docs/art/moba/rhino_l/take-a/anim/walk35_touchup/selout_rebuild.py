"""Sel-out for touch-up's rhino walk leg rebuild, ready for pack_rhino_3d.py (Claude, walk lane, 2026-11-05).

Preston, via the Rhino session: "Pack as is" (no sway). Reads walk35_touchup/frames/<se|e|ne>_f0-7.png (raw, from
views_cam35_touchup) and writes walk35_touchup/frames_selout/<se|side|ne>_f0-7.png with selout_rhino.selout, the same
uniform 141218 sel-out walk35_selout.py gives the packed walk.
2026-11-05, later: Preston "Yes, pack it" (via the Rhino session) for the s and n rebuild (walk_rebuild_sn.py), so s and
n are written too, as front and back.
Rerun after any fix to the rebuild frames, then repack.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from selout_rhino import selout  # noqa: E402

SRC = HERE / "frames"
DST = HERE / "frames_selout"
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
