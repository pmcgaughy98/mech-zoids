"""Swap the finished Retro frames (retro/frames/) into the live sets (Claude, animation lane, 2026-11-04).

walk_n -> codex-set-a/walk back_f*, walk_ne -> codex-set-c/walk ne_f*, kick_n -> codex-set-a/sand_kick back_f*,
kick_ne -> codex-set-c/sand_kick ne_f*. The frame count must match what is there. Originals go once to
<move>/frames_pre_retro/. Usage: python apply_retro.py walk_n [walk_ne kick_n kick_ne]
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
ANIM = HERE.parent
DEST = {"walk_n": ("codex-set-a/walk", "back"), "walk_ne": ("codex-set-c/walk", "ne"),
        "kick_n": ("codex-set-a/sand_kick", "back"), "kick_ne": ("codex-set-c/sand_kick", "ne")}

for name in sys.argv[1:]:
    move, view = DEST[name]
    d, keep = ANIM / move / "frames", ANIM / move / "frames_pre_retro"
    new = sorted(HERE.glob(f"frames/{name}_f*.png"), key=lambda p: int(p.stem.split("_f")[1]))
    old = sorted(d.glob(f"{view}_f*.png"))
    if len(new) != len(old):
        sys.exit(f"{name}: {len(new)} Retro frames, {len(old)} live; not applied")
    keep.mkdir(exist_ok=True)
    for p in old:
        if not (keep / p.name).exists():
            shutil.copy(p, keep / p.name)
    for i, p in enumerate(new):
        shutil.copy(p, d / f"{view}_f{i}.png")
    print(f"{name}: {len(new)} frames into {move}/frames ({view}), originals in frames_pre_retro/")
