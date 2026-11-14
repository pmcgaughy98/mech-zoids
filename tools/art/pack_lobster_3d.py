"""Lobster frames for the 3D match (Claude, lobster session, 2026-11-06).

The first lobster install. Source: the 35-degree views Preston accepted ("Accept them", 2026-11-06),
docs/art/moba/lobster_l/take-g/views_cam35/ (s, se, e, ne, n; sw, w and nw are mirrors in the sprite).

Packs one frame per view, copied as drawn, no recolour and no outline pass:
- idle_<view>: the still.
- walk_<view>: the same still, a STAND-IN so a moving lobster shows its picture (the sprite asks for walk_<view>
  whenever it moves). It glides until a walk is drawn. Replace it, don't keep it.
Both are drawn at 35 degrees, so both are in tilt_anims. Cells are 192 with the feet on row 160 (feet_edge_row 161, the
L canvas, as the hippo).

Feet meta: the camera lane's in-game measurement (FEET below). The art estimate it replaced, in texels from the canvas centre column (96):
- front 50: the claw contact in the 35-degree side view (columns 140-152). The claws are the lowest drawn part from
  the front.
- rear -50: the tail fan's centre in the side view (columns 32-60). As with the kangaroo's tail, the fan is the lowest
  drawn part from behind (the n view's bottom rows are the fan, columns 73-117).
- front_half_width 17: the two claw contacts in the s view (centres 78.5 and 111.5).
- rear_half_width 6: the fan is one piece on the centre line.
Writes art/machines/lobster/lobster_sheet.png and lobster_frames.tres. Run: python tools/art/pack_lobster_3d.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs/art/moba/lobster_l/take-g/views_cam35"
OUT = ROOT / "art/machines/lobster"
CELL = 192
FEET_ROW = 160
VIEWS = ["s", "se", "e", "ne", "n"]
ANIMS = ["idle", "walk"]
TILT_ANIMS = ["idle", "walk"]
# Feet: the camera lane's in-game measurement (plant_test --machine=lobster_game, 2026-11-06). Front and rear 28: the
# art contacts (+-50) are right for the drawing, but in game the claw and fan edge landed 6 px short in s and n (bound
# 4 px); +-40 gave 4.5, +-34 gave 4.1, +-28 gave 3.3 (pass), centre within 0.3 px. Widths are the art estimate,
# kept. Shadow covers 0.51-0.79 of the body and reaches 23 px past claws and fan in s and n (bound 20), accepted as a
# soft band. The walk plants on the idle's spot. Renders: D:/dev/_scratch/camera-lane/lob_28_m28_17_6.
FEET = {"front": 28, "rear": -28, "front_half_width": 17, "rear_half_width": 6}


def pack():
    views = {}
    for v in VIEWS:
        a = np.asarray(Image.open(SRC / f"{v}.png").convert("RGBA"))
        assert a.shape == (CELL, CELL, 4), f"{v}: {a.shape}"
        assert np.nonzero(a[..., 3] > 0)[0].max() == FEET_ROW, f"{v}: feet off row {FEET_ROW}"
        views[v] = a
    sheet = Image.new("RGBA", (len(ANIMS) * CELL, len(VIEWS) * CELL), (0, 0, 0, 0))
    for r, v in enumerate(VIEWS):
        for c in range(len(ANIMS)):
            sheet.alpha_composite(Image.fromarray(views[v]), (c * CELL, r * CELL))
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / "lobster_sheet.png")

    subs, anims, k = [], [], 0
    for r, v in enumerate(VIEWS):
        for c, name in enumerate(ANIMS):
            k += 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{k}"]\natlas = ExtResource("1_sheet")\n'
                        f"region = Rect2({c * CELL}, {r * CELL}, {CELL}, {CELL})\n")
            anims.append(f'{{\n"frames": [{{\n"duration": 1.0,\n"texture": SubResource("AtlasTexture_{k}")\n}}],\n'
                         f'"loop": true,\n"name": &"{name}_{v}",\n"speed": 5.0\n}}')
    tres = ('[gd_resource type="SpriteFrames" format=3]\n\n'
            '[ext_resource type="Texture2D" path="res://art/machines/lobster/lobster_sheet.png" id="1_sheet"]\n\n'
            + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n"
            + "metadata/feet = {" + ", ".join(f'"{n}": {x}' for n, x in FEET.items()) + "}\n"
            + "metadata/tilt_anims = [" + ", ".join(f'"{a}"' for a in TILT_ANIMS) + "]\n")
    (OUT / "lobster_frames.tres").write_text(tres)
    print(f"source {SRC.relative_to(ROOT)}; sheet {sheet.size}; {len(anims)} animations, {k} frames; feet {FEET}")


if __name__ == "__main__":
    pack()
