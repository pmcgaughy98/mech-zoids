"""The rhino's front and back walk, brought back to the approved stills (Claude, animation lane, 2026-11-04).

Preston: "fix em up with our tools as well", on the walk's drift from the stills. The live walk (the Codex
consistency frames) is a redraw that matches views/s.png and n.png on only 61-67% of pixels: the front chin plate is
smaller and the head sits differently, and the back has a round knob where the still has the square tail plate.

Method, the fix_front_shoulders.py one, per frame:
  - find the body's bob: the still's upper body (rows 95-130) matched against the frame, dx -3..3, dy -1..4;
  - take the still, moved by that bob, for everything above the legs: head, horn, chin plate, shoulder blocks,
    rump and tail plate;
  - keep the frame's own legs, from each front-leg band's knee-disc top down (the step Preston liked), and the
    frame's middle band below row 150 (belly shadow, hind feet).
The still has no painted outline; sel-out adds it at pack time, which also draws the line over the shoulder blocks'
tops (they are the silhouette in the still's geometry). Originals, including front_shoulder_ink.py's pre_shoulder/,
go to walk/frames_pre_still_body/, so a rerun of front_shoulder_ink.py cannot restore the drifted frames.
Usage: python walk_to_still.py [--apply]   (without --apply it only measures and writes the board)
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ANIM = Path(__file__).parent
VIEWS = ANIM.parent / "views"
WALK = ANIM / "codex-set-a/walk"
IDLE = ANIM / "codex-set-a/idle/frames"
KEEP = WALK / "frames_pre_still_body"
DISC = np.array([0x9D, 0x9B, 0xA2])
OUTL = np.array([0x14, 0x12, 0x18])
JOBS = [("s", "front"), ("n", "back")]
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402


def disc_top(a, x0, x1, y0=118):
    band = a[:, x0:x1]
    hits = (np.all(band[..., :3] == DISC, -1) & (band[..., 3] > 0)).sum(1)
    rows = [y for y in range(y0, 166) if hits[y] >= 3]
    return rows[0] if rows else None


def shift(a, dx, dy):
    return np.roll(a, (dy, dx), (0, 1))


def bob(still, f):
    body = (f[95:130, :, 3] > 0) & ~np.all(f[95:130, :, :3] == OUTL, -1)
    return max(((np.all(shift(still, dx, dy)[95:130] == f[95:130], -1) & body).sum(), dx, dy)
               for dy in range(-1, 5) for dx in range(-3, 4))


def fix(still, f):
    hits, dx, dy = bob(still, f)
    s = shift(still, dx, dy)
    ys, xs = np.nonzero(still[..., 3] > 0)
    cx = (xs.min() + xs.max()) // 2 + dx
    bands = [(xs.min() + dx - 4, cx - 14), (cx + 15, xs.max() + dx + 5)]
    out = s.copy()
    tops = []
    for x0, x1 in bands:
        st, t = disc_top(s, x0, x1), disc_top(f, x0, x1)
        cut = min(v for v in (st, t, 150) if v is not None)  # a lowered leg must not leave the still's knee showing
        out[cut:, x0:x1] = f[cut:, x0:x1]
        tops.append((st, t))
    out[150:, bands[0][1]:bands[1][0]] = f[150:, bands[0][1]:bands[1][0]]
    body = (f[..., 3] > 0) & ~np.all(f[..., :3] == OUTL, -1)
    before = (np.all(s == f, -1) & body).sum() / body.sum()
    return out, dict(dx=dx, dy=dy, upper_match=round(hits / max(1, body[95:130].sum()), 3),
                     disc_tops=tops, still_match_before=round(float(before), 3))


def main():
    apply = "--apply" in sys.argv
    src = KEEP if KEEP.exists() else WALK / "frames"
    rows = []
    for v, name in JOBS:
        still = np.asarray(Image.open(VIEWS / f"{v}.png").convert("RGBA"))
        idle0 = np.asarray(Image.open(IDLE / f"{name}_f0.png").convert("RGBA"))
        before, after = [], []
        for i in range(8):
            f = np.asarray(Image.open(src / f"{name}_f{i}.png").convert("RGBA"))
            out, info = fix(still, f)
            print(f"{name}_f{i}: {info}")
            before.append(f)
            after.append(out)
        rows.append((still, idle0, before, after))
        if apply:
            if not KEEP.exists():
                shutil.copytree(WALK / "frames", KEEP)
                if (WALK / "frames/pre_shoulder").exists():
                    shutil.rmtree(WALK / "frames/pre_shoulder")
            for i, out in enumerate(after):
                Image.fromarray(out).save(WALK / "frames" / f"{name}_f{i}.png")
    # board, everything with sel-out as the game shows it: per view, a before row and an after row, each starting
    # with the still and the idle's frame 0 (the idle-to-walk switch is columns 2 to 3)
    crop, k = (46, 72, 148, 170), 3
    w, h = (crop[2] - crop[0]) * k, (crop[3] - crop[1]) * k
    im = Image.new("RGBA", (w * 10, (h + 16) * 4), (0x3D, 0x43, 0x50, 255))
    d = ImageDraw.Draw(im)
    r = 0
    for (still, idle0, before, after), (_, name) in zip(rows, JOBS):
        for label, frames in (("before", before), ("after", after)):
            for c, a in enumerate([still, idle0] + frames):
                im.alpha_composite(Image.fromarray(selout(a)[0]).crop(crop).resize((w, h), Image.NEAREST),
                                   (c * w, 16 + r * (h + 16)))
                d.text((c * w + 4, r * (h + 16) + 2),
                       "still" if c == 0 else "idle f0" if c == 1 else f"{name} {label} f{c - 2}",
                       fill=(255, 230, 150, 255))
            r += 1
    im.save(ANIM / "walk-to-still-board.png")
    print("board walk-to-still-board.png;", "applied" if apply else "dry run")


if __name__ == "__main__":
    main()
