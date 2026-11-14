"""35-degree cast pose, built by script from the approved views (Claude, animation lane, 2026-11-05).

Preston: "Keep working on our attack animations and kits", then took the fennec's portal kit ("Take it",
docs/plan/moba-kits.md). Every slot of that kit is a cast from the body, so the body needs one cast pose; the gates,
bolts and rings are separate effect sprites. Nothing is drawn new: the approved pixels are moved and recoloured,
the way the idle is (build_idle35.py), so it costs nothing and frame 0 is the still.

The cast, 6 frames: still; ears start up; ears up 2 px with the body risen 1 px and the glow on; the cast (glow at
its brightest, held longest); settle; still.
  - ears up: the rows above an ear cut rise and the row at the cut repeats, so the ears stretch taller;
  - body: the idle's breath (same cut as build_idle35.py), so the feet never move;
  - glow: the warm inner-ear colours go one step lighter in the ear rows, and the eye colours one or two steps.
Reads the newest approved views (build_idle35.source). Writes <take>/anim/cast35/: frames/, frames_selout/,
board.png, cast.gif, build_check.txt. Run: python tools/art/build_cast35.py [machine]
Fennec: Preston "Looks good" (2026-11-05); packed as cast_<view> by tools/art/pack_fennec_3d.py (its own sheet, tilted).
A rebuild here changes the game's frames on the next pack, so repack and recheck after one.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_idle35 as idle  # noqa: E402

NAMES = idle.NAMES
# per frame: ears up (px), body up (px), inner-ear glow level, eye glow level, ms
SEQ = [(0, 0, 0, 0, 80), (1, 0, 1, 0, 80), (2, 1, 1, 1, 100), (2, 1, 1, 2, 220), (1, 0, 1, 1, 100), (0, 0, 0, 0, 120)]
# The great gate's charge (the ultimate; the kit doc asks for "a charge loop for the ultimate"), 2026-11-05 after
# Preston's "lets redo all". It loops between the cast's f2 and its release (cast f3 onward): f0 is the cast's f2 pose,
# then the ears quiver between 2 and 3 px up and the eyes pulse. Writes <take>/anim/charge35/.
CHARGE = [(2, 1, 1, 1, 110), (3, 1, 1, 2, 110), (2, 1, 1, 2, 110), (3, 1, 1, 1, 110)]
MOVES = {"cast": (SEQ, False), "charge": (CHARGE, True)}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ear cut per view (rows above it are ears), glow rows (inner-ear glow only above this row), and colour steps.
# Fennec cuts chosen on a marked strip of the touch-up views, 2026-11-05: the ear bases meet the head about 90 (s),
# 88 (se, e), 84 (ne) and 80 (n); the warm inner ear runs down to about 104 (s), 108 (se), 103 (e), under the chest
# and snout gold.
MACHINES = {
    "fennec": {
        "ear_cut": {"s": 92, "se": 90, "e": 90, "ne": 85, "n": 81},
        "glow_to": {"s": 104, "se": 107, "e": 103, "ne": 95, "n": 95},
        "warm": {rgb("b8923a"): rgb("f0d27a"), rgb("f0d27a"): rgb("fff4d6")},
        "eyes": [{rgb("3fe8b0"): rgb("c8fff0"), rgb("c8fff0"): rgb("f6fffb")},
                 {rgb("3fe8b0"): rgb("f6fffb"), rgb("c8fff0"): rgb("f6fffb")}],
    },
}


def stretch(a, k, cut):
    """Rows above the cut rise k px; the row just above the cut repeats to fill."""
    return idle.breath(a, k, cut)


def recolour(a, table, rows=None):
    out = a.copy()
    lim = np.zeros(a.shape[:2], bool)
    lim[: (rows if rows is not None else a.shape[0])] = True
    src = a.copy()
    for k, v in table.items():
        m = lim & (src[..., 3] > 0) & np.all(src[..., :3] == k, -1)
        out[m, :3] = v
    return out


def build(machine, move="cast"):
    cfg = MACHINES[machine]
    seq, loop = MOVES[move]
    take, feet, body_cut = idle.MACHINES[machine]
    views = idle.source(take)
    out = idle.MOBA / take / f"anim/{move}35"
    for sub in ("frames", "frames_selout"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    idle.selout_rhino.OUTLINE = idle.darkest(np.asarray(Image.open(views / "s.png").convert("RGBA")))
    rows, lines = [], []
    for v, name in NAMES:
        still = np.asarray(Image.open(views / f"{v}.png").convert("RGBA")).copy()
        made, sel = [], []
        for i, (ears, body, warm, eyes, _) in enumerate(seq):
            f = stretch(still, ears, cfg["ear_cut"][v])
            if warm:
                f = recolour(f, cfg["warm"], cfg["glow_to"][v] - ears)
            if eyes:
                f = recolour(f, cfg["eyes"][eyes - 1])
            f = idle.breath(f, body, body_cut[v])
            assert (f[body_cut[v]:] == still[body_cut[v]:]).all(), f"{name} f{i}: rows from the body cut down moved"
            Image.fromarray(f).save(out / "frames" / f"{name}_f{i}.png")
            s = idle.selout_rhino.selout(f.copy())[0]
            Image.fromarray(s).save(out / "frames_selout" / f"{name}_f{i}.png")
            made.append(f)
            sel.append(s)
        lines.append(f"{name} ({v}): ear cut {cfg['ear_cut'][v]}, body cut {body_cut[v]}, f0 = still "
                     f"{(made[0] == still).all()}, last = still {(made[-1] == still).all()}, "
                     f"f3 changes {int((made[3] != still).any(2).sum())} px")
        rows.append((v, sel))
    txt = (f"{move}; source {views.name}; outline #{bytes(idle.selout_rhino.OUTLINE).hex()}; "
           f"ms {[s[-1] for s in seq]}; loop {loop}\n")
    (out / "build_check.txt").write_text(txt + "\n".join(lines) + "\n")
    board(machine, out, rows, feet, seq, move)
    gif(out, rows, feet, seq, loop, move)
    print(machine, txt.strip(), *lines, sep="\n  ")


def board(machine, out, rows, feet, seq=SEQ, move="cast"):
    k, font = 3, ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 16)
    top = min(int(np.nonzero(s[0][..., 3] > 0)[0].min()) for _, s in rows) - 4
    bot = feet + 3
    w = rows[0][1][0].shape[1]
    cw, ch = w * k, (bot - top) * k
    img = Image.new("RGB", (len(seq) * (cw + 6), 24 + len(rows) * (ch + 24)), (60, 66, 62))
    d = ImageDraw.Draw(img)
    for c, s in enumerate(seq):
        d.text((c * (cw + 6) + 6, 4), f"f{c}  {s[-1]} ms", fill=(240, 220, 120), font=font)
    for r, (v, sel) in enumerate(rows):
        y0 = 24 + r * (ch + 24)
        d.text((4, y0 + 2), f"{r + 1}  {machine} {move} {v}", fill=(255, 255, 255), font=font)
        for c, a in enumerate(sel):
            im = Image.fromarray(a).crop((0, top, w, bot)).resize((cw, ch), Image.NEAREST)
            img.paste(im, (c * (cw + 6), y0 + 22), im)
    img.save(out / "board.png")


def gif(out, rows, feet, seq=SEQ, loop=False, move="cast"):
    k = 3
    top = min(int(np.nonzero(s[0][..., 3] > 0)[0].min()) for _, s in rows) - 4
    bot = feet + 3
    w = rows[0][1][0].shape[1]
    frames, ms = [], []
    for i, s in enumerate(seq):
        img = Image.new("RGB", (len(rows) * w * k, (bot - top) * k), (78, 92, 84))
        for c, (_, sel) in enumerate(rows):
            im = Image.fromarray(sel[i]).crop((0, top, w, bot)).resize((w * k, (bot - top) * k), Image.NEAREST)
            img.paste(im, (c * w * k, 0), im)
        frames.append(img)
        ms.append(s[-1] + (500 if i == len(seq) - 1 and not loop else 0))  # a pause between casts
    frames[0].save(out / f"{move}.gif", save_all=True, append_images=frames[1:], duration=ms, loop=0)


if __name__ == "__main__":
    for m in sys.argv[1:] or list(MACHINES):
        for mv in MOVES:
            build(m, mv)
