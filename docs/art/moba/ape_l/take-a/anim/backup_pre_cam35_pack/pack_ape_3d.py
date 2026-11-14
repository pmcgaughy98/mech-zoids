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
# PENDING, not written yet: the gorilla's ground footprint for the 35-degree views (ape_l/take-a/views_cam35, take 2),
# from the camera lane 2026-11-04, in texels from the canvas centre column. Front = the knuckles (near fist +16 in the
# side view, fists at +-30 in the front view), rear = the feet (-26 in the side view, +-18 in the back view). Write it
# as metadata/feet (the way pack_rhino_3d.py's tilt_meta() does) only when the cam35 views are installed here; the
# hub said not before. directional_sprite_3d.gd reads front_half_width and rear_half_width.
FEET_CAM35 = {"front": 16, "rear": -26, "front_half_width": 30, "rear_half_width": 18}
WALK_VIEWS = [("s", "front"), ("e", "side"), ("n", "back")]
ALL_VIEWS = ["s", "se", "e", "ne", "n"]
KIT_VIEWS = [("s", "front"), ("e", "side"), ("n", "back")]
# name, Codex preview timing in ms per drawn frame, loop. Played at speed 10, so a frame lasts ms / 100 ticks.
KIT = [
    ("idle", [220] * 5, True),
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
    return all((diag_dir(anim) / f"{v}_f0.png").exists() for v in ("se", "ne"))


def frame(anim, vname, i):
    d = diag_dir(anim) if vname in ("se", "ne") else src(anim) / "frames"
    return sel(Image.open(d / f"{vname}_f{i}.png"))


def still(view):
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    canvas.alpha_composite(Image.open(TAKE / "views" / f"{view}.png").convert("RGBA"), STILL_AT)
    return sel(canvas)


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
            + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n")
    (OUT / "ape_frames.tres").write_text(tres, encoding="utf8")
    print(f"outline #{bytes(selout_rhino.OUTLINE).hex()}; sheets {sheet.size} and {kit.size}, {n} atlas frames, "
          f"{len(anims)} animations")


def check():
    """Frame 0 of every s/e/n animation must equal the still; every frame's lowest opaque row before sel-out is 160."""
    bad = []
    for name in ["walk"] + [k for k, _, _ in KIT]:
        for view, vname in KIT_VIEWS + (DIAG_VIEWS if has_diag(name) else []):
            f0 = np.asarray(frame(name, vname, 0))
            st = np.asarray(still(view))
            same = (f0 == st).all(axis=2).mean()
            if name != "walk" and same < 1.0:
                bad.append(f"{name}_{view} f0 vs still {same:.4f}")
            d = diag_dir(name) if vname in ("se", "ne") else src(name) / "frames"
            for p in sorted(d.glob(f"{vname}_f*.png")):
                a = np.asarray(Image.open(p).convert("RGBA"))[..., 3] > 127
                ys = np.nonzero(a.any(axis=1))[0]
                if (name, int(p.stem.split("_f")[1])) in AIR:
                    if not 132 <= ys.max() <= 148:
                        bad.append(f"{p.name} in {name}: air frame lowest row {ys.max()}")
                elif ys.max() != 160:
                    bad.append(f"{p.name} in {name}: lowest row {ys.max()}")
    print("check:", "OK" if not bad else "; ".join(bad))


if __name__ == "__main__":
    pack()
    check()
