"""Hippo frames for the 3D match (Claude, animation lane, 2026-11-05).

Preston, on the hippo's 35-degree idle (docs/art/moba/hippo_l/take-b/anim/idle35, built by tools/art/build_idle35.py
from views_cam35_touchup_shade1, kept "Keep 1 px version"): "Not yet", then "actually no it works". This is the first
hippo install: the 3D match had no hippo frames (scripts/moba3d/cam_angle_test.gd read its views from docs/).

Packs idle_<view> for s, se, e, ne, n: 5 frames at 200 ms, looping; f0 is the still. The views are drawn at 35 degrees,
so "idle" is in tilt_anims (DirectionalSprite3D tilts it toward the camera, as the rhino's and the fennec's idles).
Cells are 192 with the feet on row 160 raw and 161 with sel-out (feet_edge_row 161). The sel-out frames come from
idle35 (the machine's darkest colour) and are checked here against a fresh sel-out of the raw frames, so a stale
build fails the pack.

Feet meta: the camera lane's in-game measurement (FEET below). Not packed yet: a kit.

Walk (walk lane, 2026-11-05; Preston, via the Hippo session: "Approve, pack it"): walk_<view> for s, se, e, ne, n,
8 frames at 125 ms (8 fps), looping, from docs/art/moba/hippo_l/take-b/anim/walk35 (touch-up's cleaned walk with
1 px sway; sel-out by walk35/selout_walk.py, checked here). Rows 5-9 of the sheet; the idle rows 0-4 keep their
regions. Drawn at 35 degrees, so "walk" is in tilt_anims. Planted pace 0.48 m/s: the kit sets
full_speed_walk_rate = walk_speed / 0.48. Files packed before the walk: walk35/backup_pre_pack.
Writes art/machines/hippo/hippo_sheet.png and hippo_frames.tres. Run: python tools/art/pack_hippo_3d.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_idle35 as idle  # noqa: E402

TAKE = "hippo_l/take-b"
IDLE = idle.MOBA / TAKE / "anim/idle35"
WALK = idle.MOBA / TAKE / "anim/walk35"
WALK_N = 8
WALK_FPS = 8
OUT = ROOT / "art/machines/hippo"
CELL = 192
FEET_EDGE_ROW = 161
VIEWS = [("s", "front"), ("se", "se"), ("e", "side"), ("ne", "ne"), ("n", "back")]
TILT_ANIMS = ["idle", "walk"]
# Feet: the camera lane's in-game measurement (plant_test --machine=hippo_game, 2026-11-05): worst centre 2.2 px, near
# foot 2.7 px; shadow reach 7-19 px, 0.65-0.77 under the body in every view. front and rear are the leg groups' centres
# in the side view (front -3..20, rear -47..-23), the rear moved 4 texels forward so the back view's shadow stays within
# 20 px; the widths are the foot centres in the front and back views. The outer edges (20, -47, 38, 35) failed planting
# (near foot 5.6 px). No shadow_half_width needed. Renders: D:\dev\_scratch\camera-lane\hip_8_m31_25_22.
FEET = {"front": 8, "rear": -31, "front_half_width": 25, "rear_half_width": 22}


def pack():
    views = idle.source(TAKE)
    assert views.name == "views_cam35_touchup_shade1", f"newest approved hippo views are {views.name}; rebuild idle35"
    idle.selout_rhino.OUTLINE = idle.darkest(np.asarray(Image.open(views / "s.png").convert("RGBA")))
    n = len(idle.LIFT)
    sheet = Image.new("RGBA", (max(n, WALK_N) * CELL, 2 * len(VIEWS) * CELL), (0, 0, 0, 0))
    for r, (v, name) in enumerate(VIEWS):
        still = np.asarray(Image.open(views / f"{v}.png").convert("RGBA"))
        for i in range(n):
            raw = np.asarray(Image.open(IDLE / "frames" / f"{name}_f{i}.png").convert("RGBA"))
            sel = np.asarray(Image.open(IDLE / "frames_selout" / f"{name}_f{i}.png").convert("RGBA"))
            assert raw.shape == (CELL, CELL, 4), f"{name} f{i}: {raw.shape}"
            assert (idle.selout_rhino.selout(raw.copy())[0] == sel).all(), f"{name} f{i}: sel-out is stale"
            assert i or (raw == still).all(), f"{name}: f0 is not the still in {views.name}"
            assert np.nonzero(sel[..., 3] > 0)[0].max() == FEET_EDGE_ROW, f"{name} f{i}: feet off row {FEET_EDGE_ROW}"
            sheet.alpha_composite(Image.fromarray(sel), (i * CELL, r * CELL))
        for i in range(WALK_N):
            raw = np.asarray(Image.open(WALK / "frames" / f"{v}_f{i}.png").convert("RGBA"))
            sel = np.asarray(Image.open(WALK / "frames_selout" / f"{v}_f{i}.png").convert("RGBA"))
            assert raw.shape == (CELL, CELL, 4), f"walk {v} f{i}: {raw.shape}"
            assert (idle.selout_rhino.selout(raw.copy())[0] == sel).all(), f"walk {v} f{i}: sel-out is stale"
            assert np.nonzero(sel[..., 3] > 0)[0].max() <= CELL - 8, f"walk {v} f{i}: too near the cell edge"
            sheet.alpha_composite(Image.fromarray(sel), (i * CELL, (len(VIEWS) + r) * CELL))
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / "hippo_sheet.png")

    subs, anims, k = [], [], 0
    for r, (v, _) in enumerate(VIEWS):
        frames = []
        for i in range(n):
            k += 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{k}"]\natlas = ExtResource("1_sheet")\n'
                        f"region = Rect2({i * CELL}, {r * CELL}, {CELL}, {CELL})\n")
            frames.append(f'{{\n"duration": {idle.MS / 100},\n"texture": SubResource("AtlasTexture_{k}")\n}}')
        anims.append(f'{{\n"frames": [{", ".join(frames)}],\n"loop": true,\n"name": &"idle_{v}",\n"speed": 10.0\n}}')
    for r, (v, _) in enumerate(VIEWS):
        frames = []
        for i in range(WALK_N):
            k += 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{k}"]\natlas = ExtResource("1_sheet")\n'
                        f"region = Rect2({i * CELL}, {(len(VIEWS) + r) * CELL}, {CELL}, {CELL})\n")
            frames.append(f'{{\n"duration": 1.0,\n"texture": SubResource("AtlasTexture_{k}")\n}}')
        anims.append(f'{{\n"frames": [{", ".join(frames)}],\n"loop": true,\n"name": &"walk_{v}",\n"speed": {float(WALK_FPS)}\n}}')
    tres = ('[gd_resource type="SpriteFrames" format=3]\n\n'
            '[ext_resource type="Texture2D" path="res://art/machines/hippo/hippo_sheet.png" id="1_sheet"]\n\n'
            + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n"
            + "metadata/feet = {" + ", ".join(f'"{k}": {v}' for k, v in FEET.items()) + "}\n"
            + "metadata/tilt_anims = [" + ", ".join(f'"{a}"' for a in TILT_ANIMS) + "]\n")
    (OUT / "hippo_frames.tres").write_text(tres)
    print(f"source {views.name}; outline #{bytes(idle.selout_rhino.OUTLINE).hex()}; sheet {sheet.size}, "
          f"{len(anims)} animations, {k} frames")


if __name__ == "__main__":
    pack()
