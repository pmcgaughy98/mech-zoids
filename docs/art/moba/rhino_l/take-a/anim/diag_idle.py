"""The rhino's se and ne idle, built from the approved stills (Claude, animation lane, 2026-11-04).

Codex drew an se/ne idle in codex-set-d/idle, but its ne row drifts from the still (the rump plate and hip joints),
and an idle is the pose the machine rests in, so it must be the still. Here the breath is made from the still's own
pixels: the upper body (every row above CUT) rises by LIFT px, the row at the cut is repeated to close the gap, and
the feet never move. Codex's frames stay in codex-set-d/idle/frames_codex.
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ANIM = Path(__file__).parent
VIEWS = ANIM.parent / "views"
IDLE = ANIM / "codex-set-d/idle"
LIFT = [0, 1, 1, 1, 0]  # f0-f4 at 200 ms: in, hold, out
FEET = 160
CUT_ABOVE_FEET = 13  # the knee discs: legs below stay put, the body above rises


def breath(a, k):
    if k == 0:
        return a.copy()
    cut = FEET - CUT_ABOVE_FEET
    out = a.copy()
    out[:cut - k] = a[k:cut]  # upper body up by k rows
    out[cut - k:cut] = a[cut - 1]  # repeat the row at the cut to fill the gap
    return out


def build(idle_dir, backup_name, views):
    """views: [(still name in views/, frame name)]. Keeps the previous frames once in idle_dir/backup_name."""
    frames, backup = idle_dir / "frames", idle_dir / backup_name
    if not backup.exists():
        shutil.copytree(frames, backup)
    for v, name in views:
        still = np.asarray(Image.open(VIEWS / f"{v}.png").convert("RGBA"))
        for i, k in enumerate(LIFT):
            Image.fromarray(breath(still, k)).save(frames / f"{name}_f{i}.png")
    print(f"idle {[n for _, n in views]} rebuilt from the stills in {idle_dir.relative_to(ANIM)}, lift {LIFT}")


def main():
    import sys
    if "--set-a" in sys.argv:
        # 2026-11-04, sprite factory: the Codex idle (set A) lacks the approved stills' gear knee discs and ink, so the
        # rhino gained texture the moment it walked. Codex's idle stays in codex-set-a/idle/frames_pre_still.
        build(ANIM / "codex-set-a/idle", "frames_pre_still", [("s", "front"), ("e", "side"), ("n", "back")])
    else:
        build(IDLE, "frames_codex", [("se", "se"), ("ne", "ne")])


if __name__ == "__main__":
    main()
