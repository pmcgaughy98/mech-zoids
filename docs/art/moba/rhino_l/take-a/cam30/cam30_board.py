"""Board: the approved rhino views against the views drawn from the game camera (sprite factory lane, Claude, 2026-11-04).

Reads ../views and ../views_cam30 (s, se, e, ne, n), writes board_cam30.png here.
Sel-out is added for review only; the packer adds it in game.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
TAKE = HERE.parent
sys.path.insert(0, str(TAKE / "anim"))
from selout_rhino import selout  # noqa: E402

VIEWS = ["s", "se", "e", "ne", "n"]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


palset = {rgb(p["hex"]) for p in json.loads((TAKE / "palette.json").read_text())}
old = {v: load(TAKE / "views" / f"{v}.png") for v in VIEWS}
new = {v: load(TAKE / "views_cam30" / f"{v}.png") for v in VIEWS}
for v in VIEWS:
    left = {tuple(c) for c in new[v][new[v][..., 3] > 0][:, :3]} - palset
    assert not left, f"{v}: colours outside palette.json {left}"
    for tag, d in (("old", old), ("new", new)):
        ys, xs = np.nonzero(d[v][..., 3] > 0)
        print(v, tag, xs.max() - xs.min() + 1, "x", ys.max() - ys.min() + 1, "rows", ys.min(), "-", ys.max(), end=" | ")
    print()

# One crop box for every cell (union over all ten canvases), so the feet rows line up across old and new.
union = np.zeros(old["s"].shape[:2], bool)
for d in (old, new):
    for v in VIEWS:
        union |= d[v][..., 3] > 0
ys, xs = np.nonzero(union)
box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
K, BG = 3, (0x5A, 0x60, 0x58)
GS = 1.55  # game size: 1.55 screen px per texel at 1280 x 720 (3d_test: billboard 103-120 px for 67-77 texels)
cw, ch = (box[2] - box[0]) * K + 12, (box[3] - box[1]) * K + 12
gcw, gh = round((box[2] - box[0]) * GS) + 8, round((box[3] - box[1]) * GS) + 16
LBL = 150
W = max(LBL + 5 * cw + 10, LBL + 10 * gcw + 40)
H = 70 + 2 * (ch + 8) + 10 + gh + 40
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 10), "Rhino: approved views (drawn low, about 1 to 16 degrees) vs the game camera (34 degrees down)",
        font=fb, fill=(235, 235, 230))
dr.text((12, 38), "3x with sel-out on the map grey. Same 192 canvas, lowest foot on row 160, 0.020 m per texel, the 12 colours.",
        font=f, fill=(165, 170, 165))


def cell(arr, k):
    im = Image.fromarray(selout(arr)[0]).crop(box)
    return im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)


for r, (lab, d) in enumerate((("Approved", old), ("Game\ncamera", new))):
    y = 70 + r * (ch + 8)
    dr.text((12, y + 8), lab, font=fb, fill=(235, 235, 230))
    for i, v in enumerate(VIEWS):
        x = LBL + i * cw
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        im = cell(d[v], K)
        board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + 6))
        dr.text((x + 6, y + 4), v, font=fb, fill=(235, 235, 230))
y = 70 + 2 * (ch + 8) + 10
dr.text((12, y + 4), "Game size,\n1.55 px per\ntexel", font=f, fill=(235, 235, 230))
dr.rectangle([LBL, y, W - 10, y + gh], fill=BG)
x = LBL + 8
for d in (old, new):
    for v in VIEWS:
        im = cell(d[v], GS)
        board.alpha_composite(im, (x, y + 8))
        x += gcw
    x += 24
dr.text((12, H - 28), "Game size row: approved five, then game camera five. Files: views_cam30/. The approved views/ are unchanged.",
        font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "board_cam30.png")
print("board", board.size)
