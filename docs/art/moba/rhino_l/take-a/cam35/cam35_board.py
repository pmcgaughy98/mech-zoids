"""Board: the approved rhino views, the first game-camera try (cam30) and the 35 degree redraw (cam35).

Rhino camera-angle lane, Claude, 2026-11-04. Adapted from ../cam30/cam30_board.py.
Reads ../views, ../views_cam30 and ../views_cam35 (s, se, e, ne, n), writes board_cam35.png here.
Sel-out is added for review only; the packer adds it in game. Nothing in the three views folders is written.
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
GUIDE_H = {"s": 108, "se": 100, "e": 90, "ne": 100, "n": 108}  # guide_sizes.txt, 35 degrees


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def size(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


palset = {rgb(p["hex"]) for p in json.loads((TAKE / "palette.json").read_text())}
def load_dir(d):
    return {v: load(TAKE / d / f"{v}.png") for v in VIEWS}


sets ={"Approved": load_dir("views"), "cam30\n(first try)": load_dir("views_cam30"), "cam35\n(this run)": load_dir("views_cam35")}
for v in VIEWS:
    left = {tuple(c) for c in sets["cam35\n(this run)"][v][sets["cam35\n(this run)"][v][..., 3] > 0][:, :3]} - palset
    assert not left, f"{v}: colours outside palette.json {left}"

# One crop box for every cell (union over all fifteen canvases), so the feet rows line up across the rows.
union = np.zeros(sets["Approved"]["s"].shape[:2], bool)
for d in sets.values():
    for v in VIEWS:
        union |= d[v][..., 3] > 0
ys, xs = np.nonzero(union)
box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
K, BG = 3, (0x5A, 0x60, 0x58)
GS = 1.55  # game size: 1.55 screen px per texel at 1280 x 720 (3d_test screen_sizes)
cw, ch = (box[2] - box[0]) * K + 12, (box[3] - box[1]) * K + 30
gcw, gh = round((box[2] - box[0]) * GS) + 8, round((box[3] - box[1]) * GS) + 16
LBL = 150
W = max(LBL + 5 * cw + 10, LBL + 15 * gcw + 70)
H = 70 + 3 * (ch + 8) + 10 + gh + 40
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 10), "Rhino: approved (drawn low) vs first game-camera try (cam30) vs the 35 degree redraw (cam35)",
        font=fb, fill=(235, 235, 230))
dr.text((12, 38), "3x with sel-out on the map grey. Same 192 canvas, lowest foot on row 160, 0.020 m per texel, the 12 colours. "
        "Numbers: W x H, and H over the 35 degree guide.", font=f, fill=(165, 170, 165))


def cell(arr, k):
    im = Image.fromarray(selout(arr)[0]).crop(box)
    return im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)


for r, (lab, d) in enumerate(sets.items()):
    y = 70 + r * (ch + 8)
    dr.text((12, y + 8), lab, font=fb, fill=(235, 235, 230))
    for i, v in enumerate(VIEWS):
        x = LBL + i * cw
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        im = cell(d[v], K)
        board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + 6))
        w, h = size(d[v])
        dr.text((x + 6, y + 4), v, font=fb, fill=(235, 235, 230))
        dr.text((x + 6, y + ch - 22), f"{w}x{h}  H/guide {h / GUIDE_H[v]:.2f}", font=f, fill=(235, 235, 230))
y = 70 + 3 * (ch + 8) + 10
dr.text((12, y + 4), "Game size,\n1.55 px per\ntexel", font=f, fill=(235, 235, 230))
dr.rectangle([LBL, y, W - 10, y + gh], fill=BG)
x = LBL + 8
for d in sets.values():
    for v in VIEWS:
        im = cell(d[v], GS)
        board.alpha_composite(im, (x, y + 8))
        x += gcw
    x += 24
dr.text((12, H - 28), "Game size row: approved five, then cam30 five, then cam35 five. Files: views_cam35/. views/ and views_cam30/ unchanged.",
        font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "board_cam35.png")
print("board", board.size)
