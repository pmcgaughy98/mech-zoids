"""Red team copies of the camera-angle drone views, plus a board against the approved views (sprite factory lane, Claude, 2026-11-04).

Same swap as ../team_recolour.py: only palette entries with role team or glow change, matched by brightness order.
Reads ../views_cam30 (s, se), writes ../views_cam30_red and board_cam30.png here.
Sel-out is added on the board for review only; the packer adds it in game.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
TAKE = HERE.parent
sys.path.insert(0, str(HERE.parents[2] / "rhino_l" / "take-a" / "anim"))
from selout_rhino import selout  # noqa: E402

RED = {"team": ["ffb4a0", "ff4a3a", "c42a2a", "6a1420"],
       "glow": ["fff8f2", "ffd8c4", "ff8a4a"]}
LUMA = np.array([0.2126, 0.7152, 0.0722])
VIEWS = ["s", "se"]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


pal = json.loads((TAKE / "palette.json").read_text())
palset = {rgb(p["hex"]) for p in pal}
swap = {}
for role, ramp in RED.items():
    blues = sorted((rgb(p["hex"]) for p in pal if p["role"] == role), key=lambda c: -float(np.dot(c, LUMA)))
    assert len(blues) == len(ramp), (role, len(blues))
    swap.update({b: rgb(r) for b, r in zip(blues, ramp)})


def recolour(a):
    b = a.copy()
    for k, val in swap.items():
        b[np.all(a[..., :3] == k, -1) & (a[..., 3] > 0), :3] = val
    return b


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


(TAKE / "views_cam30_red").mkdir(exist_ok=True)
old_b = {v: load(TAKE / "views" / f"{v}.png") for v in VIEWS}
new_b = {v: load(TAKE / "views_cam30" / f"{v}.png") for v in VIEWS}
for v in VIEWS:
    left = {tuple(c) for c in new_b[v][new_b[v][..., 3] > 0][:, :3]} - palset
    assert not left, f"{v}: colours outside palette.json {left}"
old_r = {v: recolour(old_b[v]) for v in VIEWS}
new_r = {v: recolour(new_b[v]) for v in VIEWS}
for v in VIEWS:
    Image.fromarray(new_r[v]).save(TAKE / "views_cam30_red" / f"{v}.png")
    a = new_b[v][..., 3] > 0
    ys, xs = np.nonzero(a)
    print(v, "new", xs.max() - xs.min() + 1, "x", ys.max() - ys.min() + 1, "bottom row", ys.max(),
          "| old", *(lambda y, x: (x.max() - x.min() + 1, "x", y.max() - y.min() + 1))(*np.nonzero(old_b[v][..., 3] > 0)))

# One crop box for every cell (union over all four canvases), so baselines line up across old and new.
union = np.zeros((96, 96), bool)
for d in (old_b, new_b):
    for v in VIEWS:
        union |= d[v][..., 3] > 0
ys, xs = np.nonzero(union)
box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
K, BG = 4, (0x5A, 0x60, 0x58)
cw, ch = (box[2] - box[0]) * K + 16, (box[3] - box[1]) * K + 16
LBL, GAPMID = 130, 30
cols = [("approved s", "old", "s"), ("approved se", "old", "se"), ("game camera s", "new", "s"), ("game camera se", "new", "se")]
GS = 2.4  # game size: 1.2 screen px per texel at 1280 x 720 (3d_test measurement), shown at 2x
gh = int((box[3] - box[1]) * GS) + 16
gw = 8 * (round((box[2] - box[0]) * GS) + 10) + 2 * 24 + 20  # game-size row: 8 cells and two team gaps
W = max(LBL + 4 * cw + GAPMID + 10, LBL + gw)
H = 70 + 2 * (ch + 8) + 30 + gh + 40
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 10), "Minion drone: approved views (drawn about 9 degrees up) vs the game camera (35 degrees down)",
        font=fb, fill=(235, 235, 230))
dr.text((12, 38), "4x with sel-out on the map grey. Same canvas, same 0.016 m per texel, bottom row 78. Red is a recolour.",
        font=f, fill=(165, 170, 165))
src = {("old", "blue"): old_b, ("new", "blue"): new_b, ("old", "red"): old_r, ("new", "red"): new_r}


def cell(arr, k):
    im = Image.fromarray(selout(arr)[0]).crop(box)
    return im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)


for r, team in enumerate(("blue", "red")):
    y = 70 + r * (ch + 8)
    dr.text((12, y + 8), f"{team.title()} team", font=fb, fill=(235, 235, 230))
    for i, (lab, age, v) in enumerate(cols):
        x = LBL + i * cw + (GAPMID if i >= 2 else 0)
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        im = cell(src[(age, team)][v], K)
        board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + 8))
        if r == 0:
            dr.text((x + 6, y + ch - 24), lab, font=f, fill=(235, 235, 230))
y = 70 + 2 * (ch + 8) + 10
dr.text((12, y + 4), "Game size,\n2x of 1.2 px\nper texel", font=f, fill=(235, 235, 230))
dr.rectangle([LBL, y, W - 10, y + gh], fill=BG)
x = LBL + 10
for team in ("blue", "red"):
    for lab, age, v in cols:
        im = cell(src[(age, team)][v], GS)
        board.alpha_composite(im, (x, y + 8))
        x += im.width + 10
    x += 24
dr.text((12, H - 28), "Files: views_cam30/ and views_cam30_red/ (s, se). The approved views/ are unchanged and still used in game.",
        font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "board_cam30.png")
print("board", board.size)
