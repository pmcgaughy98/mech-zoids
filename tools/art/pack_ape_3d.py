"""Packs the gorilla's (ape_l) Codex frames into the sheets and SpriteFrames the 3D game plays
(Claude, animation lane, 2026-11-04). Modelled on pack_rhino_3d.py.

Writes into art/machines/ape/:
  ape_sheet.png      192x192 cells: rows 0-2 are the knuckle walk s, e, n (8 frames); row 3 is the idle stills
                     s, se, e, ne, n. West views are the east ones mirrored in the engine.
  ape_kit_sheet.png  192x192 cells: one row per animation and view (front s, side e, back n): idle, chest_beat,
                     hex_shield (set A), bound, hex_dome, death (set B).
  ape_frames.tres    SpriteFrames: walk_<s|se|e|ne|n> (8 fps, looping), idle_s/e/n animated, idle_se and idle_ne as
                     stills, chest_beat_<s|e|n> and hex_shield_<s|e|n> with Codex's preview timings.
se and ne (2026-11-04): every animation has its own se/ne row from codex-set-c (idle, walk, chest_beat, hex_shield)
and codex-set-d (bound, hex_dome, death), 35 animations in all. If a diagonal set is missing, walk_se/ne fall back
to the side walk, idle_se/ne to the still, and the engine plays the side view for actions.
Every frame gets the sel-out outline (selout_rhino.selout with the gorilla palette's darkest colour), because the
stills do not carry it. Rerun after any change to the frames.

2026-11-05, Preston "Yes, pack both" (the 35-degree idle and walk): the stills are the approved 35-degree touch-up
views (views_cam35_touchup), the idle is anim/idle35 (tools/art/build_idle35.py, built from them) and the walk is the
touch-up lane's cleaned 35-degree walk (docs/art/moba/touchup/ape_l_walk/frames, kept by Preston; the walk lane's
walk/ape_l/final is its read-only source), all five views drawn. Both tilt toward the camera (metadata/tilt_anims) and
the feet are metadata/feet. The kit (chest_beat to death) is still the low-camera Codex drawing and stays upright; its
start frames are checked against the old stills in views/. Files before the swap: anim/backup_pre_cam35_pack/.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TAKE = ROOT / "docs/art/moba/ape_l/take-a"
SET_A = TAKE / "anim/codex-set-a"
sys.path.insert(0, str(ROOT / "docs/art/moba/rhino_l/take-a/anim"))
import selout_rhino  # noqa: E402

OUT = ROOT / "art/machines/ape"
CELL = 192
STILL_AT = (16, 30)  # the 160x160 stills sit at +16,+30 in the 192 canvas, feet on row 160
# The gorilla's ground footprint for the 35-degree views, from the camera lane 2026-11-04, in texels from the canvas
# centre column. Front = the knuckles (near fist +16 in the side view, fists at +-30 in the front view), rear = the
# feet (-26 in the side view, +-18 in the back view). Written as metadata/feet since the 2026-11-05 install of the
# 35-degree views (the hub had said not before).
# In game, 2026-11-05 (camera lane, plant_test --machine=ape_game): the stills footprint planted (2.8 px worst) but the
# shadow reached 22 px past the feet from behind (limit 20). Rear -22 plants at 2.2 px worst; shadow_half_width 25
# (the knuckles' 30 was too wide; 22 passed only at the edges, 18 failed) passes every view, reach 4-20 px, 0.53-0.73
# under the body. The walk plants on the idle's spot in all five views (0.000 m). Renders:
# D:\dev\_scratch\camera-lane\ape_16_m22_30_18_25 and ape_baked.
FEET_CAM35 = {"front": 16, "rear": -22, "front_half_width": 30, "rear_half_width": 18, "shadow_half_width": 25}
STILLS = TAKE / "views_cam35_touchup"
OLD_STILLS = TAKE / "views"  # the low-camera stills the kit was drawn from
IDLE35 = TAKE / "anim/idle35/frames"  # 160x160 raw, placed at STILL_AT
WALK35 = ROOT / "docs/art/moba/touchup/ape_l_walk/frames"  # 192x192 raw, named by view (s, se, e, ne, n)
VIEW_OF = {"front": "s", "se": "se", "side": "e", "ne": "ne", "back": "n"}
# 2026-11-05, Preston "Yes, tilt now" (the gorilla session, a stopgap for the cast pop): the old-angle kit moves are
# tilted too, so they no longer pop against the tilted idle. It was set in ape_frames.tres by hand; keep it here so a
# repack doesn't drop it. Ask the gorilla session before changing it.
TILT_ANIMS = ["idle", "walk", "chest_beat", "hex_shield", "bound", "hex_dome", "death"]
WALK_VIEWS = [("s", "front"), ("e", "side"), ("n", "back")]
ALL_VIEWS = ["s", "se", "e", "ne", "n"]
KIT_VIEWS = [("s", "front"), ("e", "side"), ("n", "back")]
# name, Codex preview timing in ms per drawn frame, loop. Played at speed 10, so a frame lasts ms / 100 ticks.
KIT = [
    ("idle", [200] * 5, True),  # idle35's breath, 200 ms a frame (was the low-camera Codex idle at 220)
    ("chest_beat", [350, 130, 100, 100, 100, 150, 140, 350], False),
    ("hex_shield", [350, 130, 170, 100, 170, 350], False),
    # Set B (codex-set-b). bound: f2 push-off, f3-f5 in the air (lifted 16/28/12 px in the frame), f6 landing.
    ("bound", [300, 120, 80, 90, 200, 90, 80, 150, 250], False),
    ("hex_dome", [300, 150, 150, 300, 60, 350, 150, 300], False),  # f5: both fists hit the ground
    ("death", [80, 120, 120, 140, 160, 180, 250, 1000], False),
]
SET_OF = {"bound": "codex-set-b", "hex_dome": "codex-set-b", "death": "codex-set-b"}
AIR = {("bound", 3), ("bound", 4), ("bound", 5)}  # frames drawn off the ground on purpose


def outline_colour():
    a = np.asarray(Image.open(TAKE / "views/s.png").convert("RGBA"))
    cols = np.unique(a[a[..., 3] > 127][:, :3], axis=0)
    luma = cols.astype(float) @ np.array([0.2126, 0.7152, 0.0722])
    return cols[int(np.argmin(luma))].astype(np.uint8)


def sel(im):
    return Image.fromarray(selout_rhino.selout(np.asarray(im.convert("RGBA")))[0])


# The se and ne rows (make_codex_diag_ape.py, sets C and D). Packed once their frames exist; until then the walk shows
# the side frames, the idle the still, and the engine falls back to the side view for actions.
DIAG_SET = {"idle": "codex-set-c", "walk": "codex-set-c", "chest_beat": "codex-set-c", "hex_shield": "codex-set-c",
            "bound": "codex-set-d", "hex_dome": "codex-set-d", "death": "codex-set-d"}
DIAG_VIEWS = [("se", "se"), ("ne", "ne")]


def src(anim):
    return TAKE / "anim" / SET_OF.get(anim, "codex-set-a") / anim


def diag_dir(anim):
    return TAKE / "anim" / DIAG_SET[anim] / anim / "frames"


def has_diag(anim):
    if anim in ("idle", "walk"):  # the 35-degree idle and walk are drawn in all five views
        return True
    return all((diag_dir(anim) / f"{v}_f0.png").exists() for v in ("se", "ne"))


def placed(path):
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    canvas.alpha_composite(Image.open(path).convert("RGBA"), STILL_AT)
    return canvas


def raw_frame(anim, vname, i):
    """The frame before sel-out, on the 192 canvas."""
    if anim == "idle":
        return placed(IDLE35 / f"{vname}_f{i}.png")
    if anim == "walk":
        return Image.open(WALK35 / f"{VIEW_OF[vname]}_f{i}.png").convert("RGBA")
    d = diag_dir(anim) if vname in ("se", "ne") else src(anim) / "frames"
    return Image.open(d / f"{vname}_f{i}.png").convert("RGBA")


def frame(anim, vname, i):
    return sel(raw_frame(anim, vname, i))


def still(view, base=None):
    return sel(placed((base or STILLS) / f"{view}.png"))


def entry(name, frames, loop, speed):
    return (f'{{\n"frames": [{frames}],\n"loop": {"true" if loop else "false"},\n"name": &"{name}",\n'
            f'"speed": {float(speed)}\n}}')


def pack():
    selout_rhino.OUTLINE = outline_colour()
    OUT.mkdir(parents=True, exist_ok=True)
    walk_views = WALK_VIEWS + (DIAG_VIEWS if has_diag("walk") else [])
    still_row = len(walk_views)
    sheet = Image.new("RGBA", (8 * CELL, (still_row + 1) * CELL), (0, 0, 0, 0))
    for r, (_, vname) in enumerate(walk_views):
        for i in range(8):
            sheet.alpha_composite(frame("walk", vname, i), (i * CELL, r * CELL))
    for c, view in enumerate(ALL_VIEWS):
        sheet.alpha_composite(still(view), (c * CELL, still_row * CELL))
    sheet.save(OUT / "ape_sheet.png")

    rows = [(name, view, vname, ms, loop) for name, ms, loop in KIT
            for view, vname in KIT_VIEWS + (DIAG_VIEWS if has_diag(name) else [])]
    cols = max(len(ms) for _, ms, _ in KIT)
    kit = Image.new("RGBA", (cols * CELL, len(rows) * CELL), (0, 0, 0, 0))
    for r, (name, _, vname, ms, _) in enumerate(rows):
        for i in range(len(ms)):
            kit.alpha_composite(frame(name, vname, i), (i * CELL, r * CELL))
    kit.save(OUT / "ape_kit_sheet.png")

    subs, anims, n = [], [], 0

    def atlas(sheet_id, col, row, ticks=1.0):
        nonlocal n
        n += 1
        subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{n}"]\natlas = ExtResource("{sheet_id}")\n'
                    f"region = Rect2({col * CELL}, {row * CELL}, {CELL}, {CELL})\n")
        return f'{{\n"duration": {float(ticks)},\n"texture": SubResource("AtlasTexture_{n}")\n}}'

    walk_row = {view: r for r, (view, _) in enumerate(walk_views)}
    for view in ALL_VIEWS:  # se and ne show the side walk until they are drawn
        anims.append(entry(f"walk_{view}", ", ".join(atlas("1_sheet", i, walk_row.get(view, 1)) for i in range(8)),
                           True, 8))
    drawn = {(name, view) for name, view, *_ in rows}
    for c, view in enumerate(ALL_VIEWS):
        if view in ("se", "ne") and ("idle", view) not in drawn:
            anims.append(entry(f"idle_{view}", atlas("1_sheet", c, still_row), True, 1))
    for r, (name, view, _, ms, loop) in enumerate(rows):
        anims.append(entry(f"{name}_{view}", ", ".join(atlas("2_kit", i, r, t / 100) for i, t in enumerate(ms)),
                           loop, 10))
    tres = ('[gd_resource type="SpriteFrames" format=3]\n\n'
            '[ext_resource type="Texture2D" path="res://art/machines/ape/ape_sheet.png" id="1_sheet"]\n'
            '[ext_resource type="Texture2D" path="res://art/machines/ape/ape_kit_sheet.png" id="2_kit"]\n\n'
            + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n"
            + "metadata/feet = {" + ", ".join(f'"{k}": {v}' for k, v in FEET_CAM35.items()) + "}\n"
            + "metadata/tilt_anims = [" + ", ".join(f'"{a}"' for a in TILT_ANIMS) + "]\n")
    (OUT / "ape_frames.tres").write_text(tres, encoding="utf8")
    print(f"outline #{bytes(selout_rhino.OUTLINE).hex()}; sheets {sheet.size} and {kit.size}, {n} atlas frames, "
          f"{len(anims)} animations")


def check():
    """Frame 0 of every animation but the walk equals its still: the idle the 35-degree still, the kit the old
    low-camera still. Lowest opaque row before sel-out: 160, except the kit's air frames (132-148) and the 35-degree
    walk, whose planted near feet sit up to 3 rows lower at this angle (157-163, the walk lane's foot lock)."""
    bad = []
    lengths = dict([("walk", 8)] + [(k, len(ms)) for k, ms, _ in KIT])
    for name in ["walk"] + [k for k, _, _ in KIT]:
        for view, vname in KIT_VIEWS + (DIAG_VIEWS if has_diag(name) else []):
            f0 = np.asarray(frame(name, vname, 0))
            st = np.asarray(still(view, None if name == "idle" else OLD_STILLS))
            same = (f0 == st).all(axis=2).mean()
            if name != "walk" and same < 1.0:
                bad.append(f"{name}_{view} f0 vs still {same:.4f}")
            for i in range(lengths[name]):
                a = np.asarray(raw_frame(name, vname, i))[..., 3] > 127
                low = int(np.nonzero(a.any(axis=1))[0].max())
                if (name, i) in AIR:
                    ok = 132 <= low <= 148
                elif name == "walk":
                    ok = 157 <= low <= 163
                else:
                    ok = low == 160
                if not ok:
                    bad.append(f"{name}_{view} f{i}: lowest row {low}")
    print("check:", "OK" if not bad else "; ".join(bad))


if __name__ == "__main__":
    pack()
    check()
