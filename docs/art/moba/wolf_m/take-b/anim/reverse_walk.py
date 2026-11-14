"""Plays the wolf's walk cycle the other way round (Claude, animation lane, 2026-11-04).

Preston, after the numbered video: "Legs will need fixing as it looks like they are backpedaling", "For walking only".
Measured first: in the side, se and ne walks the planted feet drifted toward the facing (+x) by a median 0.6-0.8 px a
frame, which reads as walking backwards. Reversing time turns that into a forward walk, keeping every drawn frame:
the new order is f0, f7, f6, ... f1 (f0 stays first, so idle-to-walk is unchanged). All five views get the same
order so their leg pairs stay in step when the camera turns. The old frames are kept in <set>/walk/frames_pre_reverse/.
Run once: python reverse_walk.py (it refuses to run twice).
"""
import shutil
from pathlib import Path

ANIM = Path(__file__).resolve().parent
ROWS = [("codex-set-a", ("front", "side", "back")), ("codex-set-c", ("se", "ne"))]
N = 8


def main():
    for folder, views in ROWS:
        frames = ANIM / folder / "walk" / "frames"
        backup = ANIM / folder / "walk" / "frames_pre_reverse"
        if backup.exists():
            raise SystemExit(f"{backup} exists: already reversed")
        backup.mkdir()
        for v in views:
            for i in range(N):
                shutil.copy2(frames / f"{v}_f{i}.png", backup / f"{v}_f{i}.png")
            for i in range(N):
                shutil.copy2(backup / f"{v}_f{(-i) % N}.png", frames / f"{v}_f{i}.png")
        print(folder, views, "reversed; old frames in", backup.name)


if __name__ == "__main__":
    main()
