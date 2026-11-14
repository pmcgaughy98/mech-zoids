"""Sel-out for the hippo's 35-degree walk (walk lane, 2026-11-05).

Reads frames/<view>_f0-7.png (touch-up's cleaned walk with sway, approved by Preston: "Approve, pack it") and writes
frames_selout/ with the same outline colour as the hippo idle (build_idle35: the darkest colour of the approved views),
so walk and idle match. pack_hippo_3d.py checks these against a fresh sel-out, so a stale folder fails the pack.
Run: python docs/art/moba/hippo_l/take-b/anim/walk35/selout_walk.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
sys.path.insert(0, str(ROOT / "tools/art"))
import build_idle35 as idle  # noqa: E402

VIEWS = ["s", "se", "e", "ne", "n"]


def main():
    views = idle.source("hippo_l/take-b")
    idle.selout_rhino.OUTLINE = idle.darkest(np.asarray(Image.open(views / "s.png").convert("RGBA")))
    out = HERE / "frames_selout"
    out.mkdir(exist_ok=True)
    for v in VIEWS:
        for i in range(8):
            raw = np.asarray(Image.open(HERE / "frames" / f"{v}_f{i}.png").convert("RGBA"))
            Image.fromarray(idle.selout_rhino.selout(raw.copy())[0]).save(out / f"{v}_f{i}.png")
    print(f"source {views.name}; outline #{bytes(idle.selout_rhino.OUTLINE).hex()}; wrote {len(VIEWS) * 8} frames")


if __name__ == "__main__":
    main()
