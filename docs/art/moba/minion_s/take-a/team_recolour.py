"""Red team version of the minion drone, plus a board with both teams (sprite factory lane, Claude, 2026-11-04).

The blue views in views/ are the master. Only palette entries whose role in palette.json is "team" or "glow" change;
steel, charcoal and the accent stay the same on both teams. Each ramp is matched by brightness order, so blue
highlight goes to red highlight, blue deep to red deep, and so on.
Writes views_red/ and team_board.png here. Sel-out is added on the board for review only; the packer adds it in game.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "rhino_l" / "take-a" / "anim"))
from selout_rhino import selout  # noqa: E402

RED = {"team": ["ffb4a0", "ff4a3a", "c42a2a", "6a1420"],  # highlight, base, shadow, deep
       "glow": ["fff8f2", "ffd8c4", "ff8a4a"]}             # glint, bright, glow
VIEWS = ["s", "se", "e", "ne", "n", "sw", "w", "nw"]
LUMA = np.array([0.2126, 0.7152, 0.0722])


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


pal = json.loads((HERE / "palette.json").read_text())
swap = {}
for role, ramp in RED.items():
    blues = sorted((rgb(p["hex"]) for p in pal if p["role"] == role), key=lambda c: -float(np.dot(c, LUMA)))
    assert len(blues) == len(ramp), (role, len(blues))
    swap.update({b: rgb(r) for b, r in zip(blues, ramp)})
print("swap:", {"%02x%02x%02x" % k: "%02x%02x%02x" % v for k, v in swap.items()})

(HERE / "views_red").mkdir(exist_ok=True)
blue, red = {}, {}
for v in VIEWS:
    a = np.asarray(Image.open(HERE / "views" / f"{v}.png").convert("RGBA")).copy()
    b = a.copy()
    for k, val in swap.items():
        m = np.all(a[..., :3] == k, -1) & (a[..., 3] > 0)
        b[m, :3] = val
    left = {tuple(c) for c in a[a[..., 3] > 0][:, :3]} - {rgb(p["hex"]) for p in pal}
    assert not left, f"{v}: colours outside palette.json {left}"
    Image.fromarray(b).save(HERE / "views_red" / f"{v}.png")
    blue[v], red[v] = a, b

# Board: blue row and red row at 4x with sel-out, then both at game size (about 2x of 26 px tall), on the map grey.
K, BG = 4, (0x5A, 0x60, 0x58)
SHOW = ["s", "se", "e", "ne", "n"]
box = {}
for v in SHOW:
    ys, xs = np.nonzero(blue[v][..., 3] > 0)
    box[v] = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
cw = max(b[2] - b[0] for b in box.values()) * K + 16
ch = max(b[3] - b[1] for b in box.values()) * K + 16
LBL = 150
W, H = LBL + cw * len(SHOW) + 10, 64 + 2 * (ch + 8) + 130 + 30
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 10), "Minion drone, take A (placeholder): blue and red team", font=fb, fill=(235, 235, 230))
dr.text((12, 36), "Shown at 4x with sel-out on the map grey. Red is a recolour of the blue: only the team plates and glows "
        "change.", font=f, fill=(165, 170, 165))
for r, (lab, src) in enumerate((("Blue team", blue), ("Red team", red))):
    y = 64 + r * (ch + 8)
    dr.text((12, y + 8), lab, font=fb, fill=(235, 235, 230))
    for i, v in enumerate(SHOW):
        x = LBL + i * cw
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        im = Image.fromarray(selout(src[v])[0]).crop(box[v])
        im = im.resize((im.width * K, im.height * K), Image.NEAREST)
        board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + (ch - im.height) // 2))
        if r == 0:
            dr.text((x + 6, y + 4), v, font=fb, fill=(235, 235, 230))
y = 64 + 2 * (ch + 8)
dr.text((12, y + 8), "Game size,\nabout 2x", font=f, fill=(235, 235, 230))
dr.rectangle([LBL, y, W - 10, y + 122], fill=BG)
x = LBL + 10
for src in (blue, red):
    for v in SHOW:
        im = Image.fromarray(selout(src[v])[0]).crop(box[v])
        k = 26 / (box[v][3] - box[v][1])
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        board.alpha_composite(im, (x, y + (122 - im.height) // 2))
        x += im.width + 12
    x += 30
dr.text((12, H - 26), "Files: views/ (blue master) and views_red/. Ground row 88, drone bottom row 78, 96 x 96 canvas.",
        font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "team_board.png")
print("board", board.size)
