"""Comparison board for the drone 3D test (Claude, 2026-11-04). Run after drone_view.gd has written godot_shots/.
Rows: the approved views; then, from the game's chase camera in Godot at 1280 x 720 (crops at 3x, nearest):
the billboard the game draws today, the carved voxel model, the part-built voxel model, the Retro Diffusion Lite
model; last, the part-built model drawn back at the sprite's own 9 degree angle. Also anim_strip.png."""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, "godot_shots")
NAMES = ["s", "se", "e", "ne", "n"]
CW, CH, LW = 384, 288, 300
SCORES = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
try:
    FONT = ImageFont.load_default(size=19)
    SMALL = ImageFont.load_default(size=15)
except TypeError:
    FONT = SMALL = ImageFont.load_default()


def cell_view(name):
    im = Image.open(os.path.join(HERE, "..", "views", name + ".png")).convert("RGBA").resize((288, 288), Image.NEAREST)
    c = Image.new("RGBA", (CW, CH), (110, 110, 118, 255))
    c.alpha_composite(im, ((CW - 288) // 2, 0))
    return c


def cell_shot(kind, name):
    return Image.open(os.path.join(SH, f"{kind}_{name}.png")).convert("RGBA").resize((CW, CH), Image.NEAREST)


def cell_reproject(i):
    sheet = Image.open(os.path.join(HERE, "reproject_parts.png")).convert("RGBA")
    im = sheet.crop((i * 384, 384, i * 384 + 384, 768)).resize((288, 288), Image.NEAREST)
    c = Image.new("RGBA", (CW, CH), (110, 110, 118, 255))
    c.alpha_composite(im, ((CW - 288) // 2, 0))
    return c


rows = [
    ("Approved views (drawn at about 9 deg)", "views", lambda n, i: cell_view(n)),
    ("In game today: billboard, chase cam 30 deg", "sprite", lambda n, i: cell_shot("sprite", n)),
    ("A. Carved from the views (voxels)", "voxel", lambda n, i: cell_shot("voxel", n)),
    ("B. Part-built to the views (voxels)", "parts", lambda n, i: cell_shot("parts", n)),
    ("C. Retro Diffusion Lite ($0.10)", "lite", lambda n, i: cell_shot("lite", n)),
    ("B drawn back at the sprite's 9 deg", "parts9", lambda n, i: cell_reproject(i)),
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
board.convert("RGB").save(os.path.join(HERE, "board_3d_test.png"))

strip = Image.new("RGBA", (LW + CW * 4, 40 + CH * 2), (34, 34, 40, 255))
d = ImageDraw.Draw(strip)
for i, t in enumerate(["0.00 s", "0.75 s", "1.50 s", "2.25 s"]):
    d.text((LW + i * CW + 8, 10), t, fill=(230, 230, 235), font=FONT)
for r, (label, kind, pre) in enumerate([("Lite hover_idle (RD rig, $0.08)", "lite", "anim"), ("B with a code bob, no rig", "parts", "bob")]):
    d.text((12, 40 + r * CH + 14), label, fill=(235, 235, 240), font=SMALL)
    for i, t in enumerate(["0.00", "0.75", "1.50", "2.25"]):
        strip.alpha_composite(cell_shot(kind, f"{pre}_{t}"), (LW + i * CW, 40 + r * CH))
strip.convert("RGB").save(os.path.join(HERE, "anim_strip.png"))
print("ok")
