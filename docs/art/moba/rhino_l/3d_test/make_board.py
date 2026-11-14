"""Comparison board for the rhino 3D test (Claude, 2026-11-04). Run after rhino_view.gd has written godot_shots/.
Rows: the approved views; from the game's chase camera in Godot at 1280 x 720 (crops 256 x 200, shown at 1.5x,
nearest): the billboard the game would draw, the part-built voxel rhino; last, the model drawn back at the views'
own low angle (reproject_rhino.png). Optional argument: JSON of {row key: "score line|score line"}.
Also measures each subject's on-screen size against the empty frame."""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, "godot_shots")
NAMES = ["s", "se", "e", "ne", "n"]
CW, CH, LW = 384, 300, 300
SCORES = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
try:
    FONT = ImageFont.load_default(size=19)
    SMALL = ImageFont.load_default(size=15)
except TypeError:
    FONT = SMALL = ImageFont.load_default()
EMPTY = np.array(Image.open(os.path.join(SH, "empty_frame.png")).convert("RGB")).astype(int)


def cell_view(name):
    im = Image.open(os.path.join(HERE, "..", "take-a", "views", name + ".png")).convert("RGBA")
    im = im.crop((36, 70, 156, 166)).resize((360, 288), Image.NEAREST)
    c = Image.new("RGBA", (CW, CH), (110, 110, 118, 255))
    c.alpha_composite(im, ((CW - 360) // 2, 6))
    return c


def cell_shot(kind, name):
    return Image.open(os.path.join(SH, f"{kind}_{name}.png")).convert("RGBA").resize((CW, CH), Image.NEAREST)


def cell_reproject(i):
    sheet = Image.open(os.path.join(HERE, "reproject_rhino.png")).convert("RGBA")
    im = sheet.crop((i * 370, 274, i * 370 + 360, 274 + 264)).resize((360, 264), Image.NEAREST)
    c = Image.new("RGBA", (CW, CH), (110, 110, 118, 255))
    c.alpha_composite(im, ((CW - 360) // 2, 18))
    return c


def screen_size(kind, name):
    a = np.array(Image.open(os.path.join(SH, f"{kind}_{name}.png")).convert("RGB")).astype(int)
    m = np.abs(a - EMPTY).sum(-1) > 24
    ys, xs = np.nonzero(m)
    return (int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1), int(m.sum())) if len(ys) else (0, 0, 0)


rows = [
    ("Approved views (drawn from a low angle)", "views", lambda n, i: cell_view(n)),
    ("In game today: billboard, chase cam 30 deg", "sprite", lambda n, i: cell_shot("sprite", n)),
    ("Part-built voxel rhino, chase cam 30 deg", "parts", lambda n, i: cell_shot("parts", n)),
    ("The model drawn back at the views' angle", "parts6", lambda n, i: cell_reproject(i)),
]
board = Image.new("RGBA", (LW + CW * 5, 40 + CH * len(rows)), (34, 34, 40, 255))
d = ImageDraw.Draw(board)
for i, n in enumerate(NAMES):
    d.text((LW + i * CW + 8, 10), n, fill=(230, 230, 235), font=FONT)
for r, (label, key, fn) in enumerate(rows):
    y = 40 + r * CH
    words, line, lines = label.split(), "", []
    for w in words:
        if len(line + " " + w) > 24:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)
    for k, t in enumerate(lines):
        d.text((12, y + 14 + k * 24), t, fill=(235, 235, 240), font=FONT)
    if key in SCORES:
        for k, t in enumerate(SCORES[key].split("|")):
            d.text((12, y + 30 + len(lines) * 24 + k * 20), t, fill=(255, 214, 120), font=SMALL)
    for i, n in enumerate(NAMES):
        board.alpha_composite(fn(n, i), (LW + i * CW, y))
board.convert("RGB").save(os.path.join(HERE, "board_rhino_3d.png"))
sizes = {k: {n: screen_size(k, n) for n in NAMES} for k in ("sprite", "parts")}
json.dump(sizes, open(os.path.join(HERE, "screen_sizes.json"), "w"), indent=1)
for k, v in sizes.items():
    print(k, v)
