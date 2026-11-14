"""Puts the front and back walks in step with the approved side trot by reordering frames (Claude, animation lane, 2026-11-04).

The side trot (codex-walk3, installed in codex-set-a/walk) lands pair A (right fore + left hind) on f0 and pair B
(left fore + right hind) on f4, each pair on the ground 4 frames and lifted 2, 4, 4, 2 px on the other 4.
Measured in set A's front and back walks (after reverse_walk.py): they are already a diagonal trot, front and back in
step with each other. Pair A is lifted f2-f4 (5, 4, 3 px) and pair B f6, f7, f0. Front: the viewer's left fore paw is
the wolf's right. Back: the viewer's left hind paw is the wolf's left. Turning the cycle by 3 frames lands each pair on
the side view's beat (pair A lifted f5-f7, down on f0; pair B lifted f1-f3, down on f4), peak lift at f5 and f1,
one frame inside the side view's 4-frame swing. New f0 is old f5, all four paws down, so idle-to-walk stays clean.
Not covered: the front and back walks have no 1 px body dip (top row 89 in every frame), and the planted paws do not
travel back in depth; both would need a redraw and read little head-on.
Old frames are kept in codex-set-a/walk/frames_pre_retime/. Run once: python retime_walk.py (it refuses to run twice).
"""
import shutil
from pathlib import Path

ANIM = Path(__file__).resolve().parent
FRAMES = ANIM / "codex-set-a" / "walk" / "frames"
BACKUP = ANIM / "codex-set-a" / "walk" / "frames_pre_retime"
VIEWS, N, SHIFT = ("front", "back"), 8, 3


def main():
    if BACKUP.exists():
        raise SystemExit(f"{BACKUP} exists: already retimed")
    BACKUP.mkdir()
    for v in VIEWS:
        for i in range(N):
            shutil.copy2(FRAMES / f"{v}_f{i}.png", BACKUP / f"{v}_f{i}.png")
        for i in range(N):
            shutil.copy2(BACKUP / f"{v}_f{(i - SHIFT) % N}.png", FRAMES / f"{v}_f{i}.png")
    print(VIEWS, f"turned by {SHIFT} frames; old frames in", BACKUP.name)


if __name__ == "__main__":
    main()
