"""Red team copies of the cam35 drone views, plus a board against the approved views (sprite factory lane, Claude, 2026-11-04).

Same swap as ../team_recolour.py: only palette entries with role team or glow change, matched by brightness order.
Reads ../views and ../views_cam35 (s, se, e, ne, n); writes ../views_cam35_red and board_cam35.png here.
Rows: approved (blue), game camera (blue), game camera (red), then everything at game size.
Sel-out is added for review only; the packer adds it in game.
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

RED = {"team": ["ffb4a0", "ff4a3a", "c42a2a", "6a1420"], "glow": ["fff8f2", "ffd8c4", "ff8a4a"]}
LUMA = np.array([0.2126, 0.7152, 0.0722])
VIEWS = ["s", "se", "e", "ne", "n"]
GUIDE_H = {"s": 64, "se": 67, "e": 70, "ne": 67, "n": 64}  # guide_sizes.txt, 35 degrees


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


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


old = {v: load(TAKE / "views" / f"{v}.png") for v in VIEWS}
new = {v: load(TAKE / "views_cam35" / f"{v}.png") for v in VIEWS}
(TAKE / "views_cam35_red").mkdir(exist_ok=True)
red = {}
for v in VIEWS:
    left = {tuple(c) for c in new[v][new[v][..., 3] > 0][:, :3]} - palset
    assert not left, f"{v}: colours outside palette.json {left}"
    red[v] = recolour(new[v])
    Image.fromarray(red[v]).save(TAKE / "views_cam35_red" / f"{v}.png")
    ys, xs = np.nonzero(new[v][..., 3] > 0)
    h = ys.max() - ys.min() + 1
    print(f"{v}: new {xs.max() - xs.min() + 1} x {h}, bottom row {ys.max()}, height / guide {h / GUIDE_H[v]:.2f}")

union = np.zeros(old["s"].shape[:2], bool)
for d in (old, new):
    for v in VIEWS:
        union |= d[v][..., 3] > 0
ys, xs = np.nonzero(union)
box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
K, BG, GS = 4, (0x5A, 0x60, 0x58), 2.4  # game size: 1.2 screen px per texel, shown at 2x
cw, ch = (box[2] - box[0]) * K + 12, (box[3] - box[1]) * K + 12
gcw, gh = round((box[2] - box[0]) * GS) + 8, round((box[3] - box[1]) * GS) + 16
LBL = 150
W = max(LBL + 5 * cw + 10, LBL + 15 * gcw + 60)
H = 70 + 3 * (ch + 8) + 10 + gh + 40
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 10), "Minion drone: approved views (drawn about 9 degrees up) vs the game camera (35 degrees down), all five",
        font=fb, fill=(235, 235, 230))
dr.text((12, 38), "4x with sel-out on the map grey. Same 96 canvas, bottom row 78, 0.016 m per texel, the 14 colours. Red is a recolour.",
        font=f, fill=(165, 170, 165))


def cell(arr, k):
    im = Image.fromarray(selout(arr)[0]).crop(box)
    return im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)


for r, (lab, d) in enumerate((("Approved", old), ("Game camera\nblue", new), ("Game camera\nred", red))):
    y = 70 + r * (ch + 8)
    dr.text((12, y + 8), lab, font=fb, fill=(235, 235, 230))
    for i, v in enumerate(VIEWS):
        x = LBL + i * cw
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        im = cell(d[v], K)
        board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + 6))
        dr.text((x + 6, y + 4), v, font=fb, fill=(235, 235, 230))
y = 70 + 3 * (ch + 8) + 10
dr.text((12, y + 4), "Game size,\n2x of 1.2 px\nper texel", font=f, fill=(235, 235, 230))
dr.rectangle([LBL, y, W - 10, y + gh], fill=BG)
x = LBL + 8
for d in (old, new, red):
    for v in VIEWS:
        board.alpha_composite(cell(d[v], GS), (x, y + 8))
        x += gcw
    x += 20
dr.text((12, H - 28), "Game size row: approved, game camera blue, game camera red. Files: views_cam35/ and views_cam35_red/. "
        "views/ and views_cam30/ are unchanged.", font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "board_cam35.png")
print("board", board.size)
