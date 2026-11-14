"""Kangaroo frames for the 3D match (Claude, kangaroo session, 2026-11-05).

The first kangaroo install: the 3D match had no kangaroo frames (scripts/moba3d/cam_angle_test.gd read the approved
low-angle views from docs/). Source: the 35-degree views Preston accepted ("Yes, accept it", 2026-11-05),
docs/art/moba/kangaroo_m/take-a/cam35/take2/fixed/ (s, se, e, ne, n; sw, w and nw are mirrors in the sprite).

Packs one frame per view, copied as drawn, no recolour and no outline pass:
- idle_<view>: the still.
- walk_<view>: the same still, a STAND-IN so a moving kangaroo shows its picture (the sprite asks for walk_<view>
  whenever it moves). It glides until the hop is drawn (MECH_STATUS.md, slice 2). Replace it, don't keep it.
Both are drawn at 35 degrees, so both are in tilt_anims. Cells are 160 with the feet on row 140 (feet_edge_row 141, the
M canvas in directional_sprite_3d.gd).

Feet meta: the camera lane's in-game measurement (FEET below).
Writes art/machines/kangaroo/kangaroo_sheet.png and kangaroo_frames.tres. Run: python tools/art/pack_kangaroo_3d.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs/art/moba/kangaroo_m/take-a/cam35/take2/fixed"
OUT = ROOT / "art/machines/kangaroo"
CELL = 160
FEET_ROW = 140
VIEWS = ["s", "se", "e", "ne", "n"]
ANIMS = ["idle", "walk"]
TILT_ANIMS = ["idle", "walk"]
# Feet: the camera lane's in-game measurement (plant_test --machine=kangaroo_game, 2026-11-05): centre 0.2 px, near foot
# 2.6 px; shadow reach 7-15 px, 0.55-0.64 under the body in every view; the walk plants on the idle's spot. The rear is
# -18, not the art estimate's 3: the kangaroo stands on its tail too, and from behind the tail tip is the lowest drawn
# part, 8 rows below the hind feet (rear 3 planted but failed the shadow: under 0.43-0.48, ne reach -7 px). The half
# widths are the s and n foot centres (rear 4 fits the tail). Shadow width 12 and front 12 were tried and not better.
# Renders: D:/dev/_scratch/camera-lane/roo_20_m18_18_4.
FEET = {"front": 20, "rear": -18, "front_half_width": 18, "rear_half_width": 4}


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
    sheet.save(OUT / "kangaroo_sheet.png")

    subs, anims, k = [], [], 0
    for r, v in enumerate(VIEWS):
        for c, name in enumerate(ANIMS):
            k += 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{k}"]\natlas = ExtResource("1_sheet")\n'
                        f"region = Rect2({c * CELL}, {r * CELL}, {CELL}, {CELL})\n")
            anims.append(f'{{\n"frames": [{{\n"duration": 1.0,\n"texture": SubResource("AtlasTexture_{k}")\n}}],\n'
                         f'"loop": true,\n"name": &"{name}_{v}",\n"speed": 5.0\n}}')
    tres = ('[gd_resource type="SpriteFrames" format=3]\n\n'
            '[ext_resource type="Texture2D" path="res://art/machines/kangaroo/kangaroo_sheet.png" id="1_sheet"]\n\n'
            + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n"
            + "metadata/feet = {" + ", ".join(f'"{n}": {x}' for n, x in FEET.items()) + "}\n"
            + "metadata/tilt_anims = [" + ", ".join(f'"{a}"' for a in TILT_ANIMS) + "]\n")
    (OUT / "kangaroo_frames.tres").write_text(tres)
    print(f"source {SRC.relative_to(ROOT)}; sheet {sheet.size}; {len(anims)} animations, {k} frames; feet {FEET}")


if __name__ == "__main__":
    pack()
