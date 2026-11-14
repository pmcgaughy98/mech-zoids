"""Packs the minion drone's (minion_s, take A) frames into the sheets and SpriteFrames the 3D game plays
(Claude, animation lane, 2026-11-04).

Frames: docs/art/moba/minion_s/take-a/anim/<action>/frames/ (blue master) and frames_red/ (team_recolour.py's swap
table), built by anim/build_drone_frames.py from the approved still. Writes, in art/machines/minion/:
  minion_blue_sheet.png, minion_red_sheet.png   one row per action and view, 96 px cells
  minion_blue_frames.tres, minion_red_frames.tres   SpriteFrames: idle_<v>, walk_<v> (looping), attack_<v>, hit_<v>,
                                                    death_<v> (once), all at 10 fps, v in s, se, e, ne, n
The game's one-texel sel-out is added here (OUTLINE = the darkest colour, #141218). Canvas 96, feet_edge_row 88, the
drone hovers with its lowest pixel on row 78; the death's last frame rests with its lowest pixel on row 87.
Run: python tools/art/pack_minion_3d.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ANIM = ROOT / "docs/art/moba/minion_s/take-a/anim"
sys.path.insert(0, str(ROOT / "docs/art/moba/rhino_l/take-a/anim"))
import selout_rhino  # noqa: E402

OUT = ROOT / "art/machines/minion"
CELL = 96
VIEWS = ["s", "se", "e", "ne", "n"]
ACTIONS = [("idle", 4, True), ("walk", 4, True), ("attack", 5, False), ("hit", 2, False), ("death", 6, False)]
FPS = 10
selout_rhino.OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
# The drone's ground footprint in texels from the canvas centre column, from the camera lane (2026-11-04: it measured
# planting within 3.2 px with these). DirectionalSprite3D plants the drawing's ground centre on the machine's spot with
# it; without it the drone got the contact shadow but not the plant move. Re-measured 2026-11-05 on the tilted 35-degree
# frames: centre within 1.2 px, near edge within 4.1 px at 1280x720 (worst view se); other half widths gain nothing.
FEET ={"front": 16, "rear": -20, "half_width": 24}
# 2026-11-05, Preston "Yes, rebuild drone": every action is now built from views_cam35 (drawn from the game camera's
# 35 degrees), so DirectionalSprite3D tilts all of them toward the camera (game feel lane's tilt, as the rhino's idle
# and walk). The old-angle frames are in anim/<action>/frames_pre_cam35; the files packed before are in
# anim/backup_pre_cam35_pack.
TILT_ANIMS = [act for act, _, _ in ACTIONS]
STILLS = ANIM.parent / "views_cam35"


def entry(name, frames, loop):
    return (f'{{\n"frames": [{frames}],\n"loop": {"true" if loop else "false"},\n"name": &"{name}",\n'
            f'"speed": {float(FPS)}\n}}')


def pack(team, folder):
    rows = [(act, v, n, loop) for act, n, loop in ACTIONS for v in VIEWS]
    cols = max(n for _, n, _ in ACTIONS)
    sheet = Image.new("RGBA", (cols * CELL, len(rows) * CELL), (0, 0, 0, 0))
    subs, anims = [], []
    for r, (act, v, n, loop) in enumerate(rows):
        refs = []
        for i in range(n):
            a = np.asarray(Image.open(ANIM / act / folder / f"{v}_f{i}.png").convert("RGBA"))
            sheet.alpha_composite(Image.fromarray(selout_rhino.selout(a)[0]), (i * CELL, r * CELL))
            k = len(subs) + 1
            subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{k}"]\natlas = ExtResource("1_sheet")\n'
                        f"region = Rect2({i * CELL}, {r * CELL}, {CELL}, {CELL})\n")
            refs.append(f'{{\n"duration": 1.0,\n"texture": SubResource("AtlasTexture_{k}")\n}}')
        anims.append(entry(f"{act}_{v}", ", ".join(refs), loop))
    sheet.save(OUT / f"minion_{team}_sheet.png")
    tres = ('[gd_resource type="SpriteFrames" format=3]\n\n'
            f'[ext_resource type="Texture2D" path="res://art/machines/minion/minion_{team}_sheet.png" id="1_sheet"]\n\n'
            + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n"
            + "metadata/feet = {" + ", ".join(f'"{k}": {v}' for k, v in FEET.items()) + "}\n"
            + "metadata/tilt_anims = [" + ", ".join(f'"{a}"' for a in TILT_ANIMS) + "]\n")
    (OUT / f"minion_{team}_frames.tres").write_text(tres, encoding="utf8")
    print(f"{team}: sheet {sheet.size}, {len(subs)} frames, {len(anims)} animations")


def check():
    bad = []
    for act, n, _ in ACTIONS:
        for v in VIEWS:
            for folder in ("frames", "frames_red"):
                found = list((ANIM / act / folder).glob(f"{v}_f*.png"))
                if len(found) != n:
                    bad.append(f"{act}_{v} {folder}: {len(found)} frames, want {n}")
                for i in range(n):
                    a = np.asarray(Image.open(ANIM / act / folder / f"{v}_f{i}.png").convert("RGBA"))[..., 3] > 0
                    lo = int(np.nonzero(a.any(1))[0].max())
                    if lo > 87 or (act == "death" and i == n - 1 and lo != 87):
                        bad.append(f"{act}_{v} {folder} f{i}: lowest row {lo}")
            still = np.asarray(Image.open(STILLS / f"{v}.png").convert("RGBA"))
            for act0, i in (("idle", 0), ("attack", 0), ("attack", 4)):
                if not (np.asarray(Image.open(ANIM / act0 / "frames" / f"{v}_f{i}.png").convert("RGBA")) == still).all():
                    bad.append(f"{act0}_{v} f{i} is not the still")
    print("check:", "OK" if not bad else "; ".join(bad))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    pack("blue", "frames")
    pack("red", "frames_red")
    check()
