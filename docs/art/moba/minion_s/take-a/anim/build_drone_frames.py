"""Minion drone frames, built by script from the approved still (Claude, animation lane, 2026-11-04).

2026-11-05, Preston "Yes, rebuild drone": the frames are now built from views_cam35 (the drone drawn from the game
camera's 35 degrees, cam35/), so the packer tilts them toward the camera like the rhino's idle and walk. Same spec and
offsets as before; the old-angle frames are kept in anim/<action>/frames_pre_cam35 and frames_red_pre_cam35, the old
board in board_pre_cam35.png. The red frames still come from the swap table; they equal views_cam35_red on f0.
The 35-degree views have no thruster glows under the drone (the old views did); Preston on the review board
(anim/claude-drone-cam35-review.png), asked whether to keep it without them: "Keep as is".

Sprite factory handed the frames over (Preston approved the still: "Keep the drone"); Mech-Zoids cleared this route at
no cost ("Go ahead with route 1"). Every frame is the approved pixels moved, sheared or (death only) turned; nothing is
drawn new. The blue views/ are the master; the red frames are the same frames put through team_recolour.py's swap
table (only team and glow colours change).

Spec (ROSTER.md, "Minion drone (placeholder)"; game feel lane): 10 fps, all five views, names <action>_<view>.
  idle   4 frames, loop: a 1 px bob (0, -1, -1, 0). f0 is the still.
  walk   4 frames, loop: the bob plus a slight forward lean (the top half shifted 1 px toward the facing in se, e, ne;
         the lean is along the view axis in s and n, so those show the bob only). It glides: no planted pace.
  attack 5 frames, 500 ms: f0 still; f1 charge (glows one step brighter); f2 the shot as recoil, 2 px back from the
         facing, glows bright; f3 1 px back; f4 still. No muzzle flash or bolt (game feel's FX).
  hit    2 frames, 200 ms: f0 white flash (every pixel but the dark outline goes to the glint white), 2 px knock back;
         f1 normal colours, 1 px back.
  death  6 frames, 600 ms: glows die, it tips clockwise and drops; f5 is the wreck, glows dark, its lowest pixel on
         row 87 so its edge rests on the ground line, feet_edge_row 88 (directional_sprite_3d.gd: one below the foot
         row). The tilt is the one redrawn part: 4x nearest-neighbour, turned, then each 4x4 block takes its most
         common colour, so only palette colours appear.
Canvas 96x96; the still's lowest pixel is row 78. Writes anim/<action>/frames/<view>_f<i>.png (blue),
anim/<action>/frames_red/..., and anim/board.png. Run: python build_drone_frames.py
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

ANIM = Path(__file__).resolve().parent
TAKE = ANIM.parent
VIEWS = ["s", "se", "e", "ne", "n"]
C = 96
LUMA = np.array([0.2126, 0.7152, 0.0722])
# Screen direction the drone faces in each view (x right, y down); "back" is the opposite.
FACING = {"s": (0, 1), "se": (1, 1), "e": (1, 0), "ne": (1, -1), "n": (0, -1)}
LEAN = {"se": 1, "e": 1, "ne": 1, "s": 0, "n": 0}
RED = {"team": ["ffb4a0", "ff4a3a", "c42a2a", "6a1420"], "glow": ["fff8f2", "ffd8c4", "ff8a4a"]}  # team_recolour.py


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PAL = json.loads((TAKE / "palette.json").read_text())
ROLE = {rgb(p["hex"]): p["role"] for p in PAL}
GLOW = sorted((c for c, r in ROLE.items() if r == "glow"), key=lambda c: float(np.dot(c, LUMA)))  # glow, bright, glint
STEEL = sorted((c for c, r in ROLE.items() if r == "steel"), key=lambda c: float(np.dot(c, LUMA)))
CHAR = sorted((c for c, r in ROLE.items() if r == "charcoal"), key=lambda c: float(np.dot(c, LUMA)))
OUTLINE = min(ROLE, key=lambda c: float(np.dot(c, LUMA)))


def red_swap():
    swap = {}
    for role, ramp in RED.items():
        blues = sorted((c for c, r in ROLE.items() if r == role), key=lambda c: -float(np.dot(c, LUMA)))
        swap.update({b: rgb(r) for b, r in zip(blues, ramp)})
    return swap


STILLS = TAKE / "views_cam35"  # was TAKE / "views" (the old low angle) until 2026-11-05


def still(v):
    return np.asarray(Image.open(STILLS / f"{v}.png").convert("RGBA")).copy()


def recolour(a, table):
    b = a.copy()
    for k, val in table.items():
        m = np.all(a[..., :3] == k, -1) & (a[..., 3] > 0)
        b[m, :3] = val
    return b


def shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    ys, xs = slice(max(0, dy), min(h, h + dy)), slice(max(0, dx), min(w, w + dx))
    ys0, xs0 = slice(max(0, -dy), min(h, h - dy)), slice(max(0, -dx), min(w, w - dx))
    out[ys, xs] = a[ys0, xs0]
    return out


def lean(a, dx):
    """Shift the rows above the body's middle by dx toward the facing."""
    if not dx:
        return a
    ys = np.nonzero((a[..., 3] > 0).any(1))[0]
    mid = (ys.min() + ys.max()) // 2
    out = a.copy()
    out[:mid] = shift(a, dx, 0)[:mid]
    return out


def brighten(a):
    return recolour(a, {GLOW[0]: GLOW[1], GLOW[1]: GLOW[2]})


def dark(a):
    return recolour(a, {GLOW[0]: CHAR[1], GLOW[1]: STEEL[0], GLOW[2]: STEEL[0]})


def flash(a):
    out = a.copy()
    op = a[..., 3] > 0
    keep = np.all(a[..., :3] == OUTLINE, -1)
    out[op & ~keep, :3] = GLOW[2]
    return out


def back(v, n):
    fx, fy = FACING[v]
    return -fx * n, -fy * n


def turn(a, deg):
    """Clockwise turn about the body's centre: 4x up, nearest turn, then the most common colour per 4x4 block."""
    if not deg:
        return a
    k = 4
    big = Image.fromarray(a).resize((C * k, C * k), Image.NEAREST)
    ys, xs = np.nonzero(a[..., 3] > 0)
    centre = ((xs.min() + xs.max() + 1) / 2 * k, (ys.min() + ys.max() + 1) / 2 * k)
    big = np.asarray(big.rotate(-deg, resample=Image.NEAREST, center=centre))
    out = np.zeros_like(a)
    for y in range(C):
        for x in range(C):
            blk = big[y * k:(y + 1) * k, x * k:(x + 1) * k].reshape(-1, 4)
            opq = blk[blk[:, 3] > 0]
            if len(opq) * 2 <= len(blk):
                continue
            col = Counter(map(tuple, opq[:, :3])).most_common(1)[0][0]
            out[y, x, :3], out[y, x, 3] = col, 255
    return despeck(out)


def despeck(a):
    op = a[..., 3] > 0
    p = np.pad(op, 1)
    nb = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    out = a.copy()
    out[op & (nb == 0)] = 0
    hole = ~op & (nb >= 3)
    if hole.any():  # fill one-pixel notches with the darkest neighbour colour (the outline)
        out[hole, :3], out[hole, 3] = OUTLINE, 255
    return out


def lowest(a):
    return int(np.nonzero((a[..., 3] > 0).any(1))[0].max())


def drop_to(a, row):
    return shift(a, 0, row - lowest(a))


def frames(v):
    s = still(v)
    f = {}
    f["idle"] = [shift(s, 0, dy) for dy in (0, -1, -1, 0)]
    ln = lean(s, LEAN[v] * FACING[v][0])
    f["walk"] = [shift(ln, 0, dy) for dy in (0, -1, -1, 0)]
    f["attack"] = [s, brighten(s), shift(brighten(s), *back(v, 2)), shift(s, *back(v, 1)), s]
    f["hit"] = [shift(flash(s), *back(v, 2)), shift(s, *back(v, 1))]
    d = dark(s)
    f["death"] = [drop_to(dark(s), 79), drop_to(turn(d, 8), 81), drop_to(turn(d, 16), 84),
                  drop_to(turn(d, 24), 87), drop_to(turn(d, 28), 86), drop_to(turn(d, 30), 87)]
    return f


def board(all_frames, red_frames):
    k, pad = 3, 6
    rows = [(v, act, team) for act in ("idle", "walk", "attack", "hit", "death") for team in ("blue", "red")
            for v in VIEWS]
    cols = 7
    top, bot = 18, 90  # the 35-degree views reach row 23; the ground line is 88
    hh = (bot - top) * k
    img = Image.new("RGB", (cols * (C * k + pad), len(rows) * (hh + pad)), (90, 96, 88))
    for r, (v, act, team) in enumerate(rows):
        src = all_frames if team == "blue" else red_frames
        seq = [still(v) if team == "blue" else recolour(still(v), red_swap())] + src[v][act]
        for c, a in enumerate(seq):
            im = Image.fromarray(a).crop((0, top, C, bot)).resize((C * k, hh), Image.NEAREST)
            img.paste(im, (c * (C * k + pad), r * (hh + pad)), im)
    img.save(ANIM / "board.png")


def main():
    swap = red_swap()
    blue, red = {}, {}
    for v in VIEWS:
        blue[v] = frames(v)
        red[v] = {act: [recolour(a, swap) for a in seq] for act, seq in blue[v].items()}
        for act, seq in blue[v].items():
            for team, src in (("frames", blue), ("frames_red", red)):
                d = ANIM / act / team
                d.mkdir(parents=True, exist_ok=True)
                for i, a in enumerate(src[v][act]):
                    Image.fromarray(a).save(d / f"{v}_f{i}.png")
    board(blue, red)
    pal = set(ROLE) | set(swap.values())
    bad = []
    for v in VIEWS:
        for act, seq in blue[v].items():
            for i, a in enumerate(seq):
                op = a[..., 3] > 0
                cols = {tuple(int(x) for x in c) for c in a[op][:, :3]}
                if cols - pal:
                    bad.append(f"{act}_{v} f{i}: off-palette {len(cols - pal)}")
                ys, xs = np.nonzero(op)
                if xs.min() == 0 or ys.min() == 0 or xs.max() == C - 1 or ys.max() >= 88:
                    bad.append(f"{act}_{v} f{i}: touches edge or ground ({xs.min()},{ys.min()})-({xs.max()},{ys.max()})")
            if act == "death":
                print(v, "death lowest rows", [lowest(a) for a in seq])
    print("swap", {"%02x%02x%02x" % k: "%02x%02x%02x" % val for k, val in swap.items()})
    print("check:", "OK" if not bad else bad)


if __name__ == "__main__":
    main()
