"""Touch-up of the fennec's se/ne walk and sonic boom (Claude, animation lane, 2026-11-04).

Preston: "Walks NE is off the top but lots of cutoff etc. Needs touching up", then "Sonic boom too and many others do
pass". What was wrong, measured on the frames (codex-set-c):
  - walk ne, every frame: a second chin left over from the generated head under the pasted native head. A dark bar
    and a gold sliver stick out right of the neck on rows 127-130 from x 114 (the native chin ends on row 125).
  - sonic_boom se f1-f6 and ne f1: one-pixel-thick dark spurs. The haunch's bottom edge runs 2 px past the body
    above it (se), and a 7 px bar sticks out of the neck (ne f1).
Fixes:
  - walk ne: rows 127-130, x >= 114 cleared in every frame.
  - spurs: a dark pixel (outline or shadow colour) whose pixels above and below are both transparent is cleared;
    repeated until none are left. The ne still has one such pixel; that position is never touched, so frames that
    equal the still stay equal. The approved stills have none, so nothing that
    belongs to the design matches.
Sel-out at pack time redraws the outline along the new edge. Originals are kept once in <move>/frames_pre_touchup/.
Usage: python touchup.py [--apply]   (without --apply it only counts and writes touchup-board.png)
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
SET_C = HERE.parent / "codex-set-c"
TAKE = HERE.parents[1]
DARK = [(0x14, 0x12, 0x18), (0x21, 0x1e, 0x27), (0x2e, 0x1a, 0x6e), (0x3d, 0x3a, 0x44)]
JOBS = [("walk", "ne", 8), ("sonic_boom", "se", 8), ("sonic_boom", "ne", 8)]
STILL_SPUR = {}
sys.path.insert(0, str(HERE.parents[3] / "rhino_l/take-a/anim"))


def spurs(a):
    op = a[..., 3] > 0
    up = np.zeros_like(op)
    up[1:] = op[:-1]
    down = np.zeros_like(op)
    down[:-1] = op[1:]
    dark = np.any([np.all(a[..., :3] == c, -1) for c in DARK], 0)
    return op & dark & ~up & ~down


def fix(a, move, view, keep_px):
    out = a.copy()
    n = 0
    if move == "walk" and view == "ne":
        box = out[127:131, 114:]
        n += int((box[..., 3] > 0).sum())
        box[...] = 0
    while True:
        s = spurs(out) & ~keep_px  # the ne still has one such pixel of its own; it stays
        if not s.any():
            break
        n += int(s.sum())
        out[s] = 0
    return out, n


def main():
    apply = "--apply" in sys.argv
    import selout_rhino
    selout_rhino.OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
    for v in ("se", "ne"):
        st = np.zeros((192, 192, 4), np.uint8)
        st[20:180, 16:176] = np.asarray(Image.open(TAKE / "views" / f"{v}.png").convert("RGBA"))
        STILL_SPUR[v] = spurs(st)
        print(f"still {v}: {int(STILL_SPUR[v].sum())} spur pixels")
    rows = []
    for move, view, n in JOBS:
        frames = SET_C / move / "frames"
        keep = SET_C / move / "frames_pre_touchup"
        before, after, counts = [], [], []
        for i in range(n):
            name = f"{view}_f{i}.png"
            a = np.asarray(Image.open(keep / name if (keep / name).exists() else frames / name).convert("RGBA"))
            out, k = fix(a, move, view, STILL_SPUR[view])
            before.append(a)
            after.append(out)
            counts.append(k)
        print(f"{move} {view}: pixels cleared per frame {counts}")
        rows += [before, after]
        if apply:
            keep.mkdir(exist_ok=True)
            for i in range(n):
                if not (keep / f"{view}_f{i}.png").exists():
                    shutil.copy(frames / f"{view}_f{i}.png", keep / f"{view}_f{i}.png")
                Image.fromarray(after[i]).save(frames / f"{view}_f{i}.png")
    box, z = (44, 76, 148, 164), 3
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    board = Image.new("RGBA", (8 * w, len(rows) * h), (0x3D, 0x43, 0x50, 255))
    for r, row in enumerate(rows):
        for c, a in enumerate(row):
            t = Image.fromarray(selout_rhino.selout(a)[0]).crop(box).resize((w, h), Image.NEAREST)
            board.alpha_composite(t, (c * w, r * h))
    board.save(HERE / "touchup-board.png")
    print("board touchup-board.png: walk ne before/after, sonic se before/after, sonic ne before/after;",
          "applied" if apply else "dry run")


if __name__ == "__main__":
    main()
