"""Packs the fennec fox's (fennec_s, take B) Codex frames into the sheets and SpriteFrames the 3D game plays
(Claude, animation lane, 2026-11-04). Modelled on pack_ape_3d.py.

Writes into art/machines/fennec/:
  fennec_sheet.png      192x192 cells: rows 0-2 are the trot s, e, n (8 frames), then se and ne once drawn; the last
                        row is the stills s, se, e, ne, n. West views are the east ones mirrored in the engine.
  fennec_kit_sheet.png  192x192 cells: one row per animation and view (front s, side e, back n, then se and ne once
                        drawn): idle, sand_kick, ear_burst, sonic_boom (set A), dig, pop_out, death (set B).
  fennec_frames.tres    SpriteFrames: walk_<v> (10 fps, looping), idle_<v> (looping), the kit with Codex's timings.
se and ne (2026-11-04): every animation has its own se/ne row from codex-set-c (idle, walk, sand_kick, ear_burst,
sonic_boom; 125,599 tokens) and codex-set-d (dig, pop_out, death; 110,939 tokens), 40 animations in all.
The n and ne stills' new ink (2026-11-04) is carried onto the frames by anim/ink-carry/. A Retro redo of the back
and ne walk and sand kick was rejected (anim/retro/RUN.md), and so was a Codex redo (anim/codex-backviews/, kept, not
live): Preston, "bring it back to the animations it had for the most recent reveal". Live = the 14:52 pack's frames
(fennec-reveal.mp4, 14:56) plus the stills' ink; the exact reveal pixels are in <move>/frames_pre_ink/.
The stills are 160x160 with the feet on row 140, so they sit at +16,+20 in the 192 canvas, feet on row 160. The
approved pose is seated; the trot is the only animation that does not start on the still.
Every frame gets the sel-out outline (selout_rhino.selout with the fennec palette's darkest colour, #141218), because
the stills do not carry it. Rerun after any change to the frames.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TAKE = ROOT / "docs/art/moba/fennec_s/take-b"
sys.path.insert(0, str(ROOT / "docs/art/moba/rhino_l/take-a/anim"))
import selout_rhino  # noqa: E402

OUT = ROOT / "art/machines/fennec"
CELL = 192
STILL_AT = (16, 20)
WALK_VIEWS = [("s", "front"), ("e", "side"), ("n", "back")]
ALL_VIEWS = ["s", "se", "e", "ne", "n"]
WALK_FPS = 10  # Codex previewed the trot at 100 ms a frame
KIT_VIEWS = [("s", "front"), ("e", "side"), ("n", "back")]
# name, preview timing in ms per drawn frame, loop. Played at speed 10, so a frame lasts ms / 100 ticks.
# Key frames promised to the game feel lane: sand_kick release f3, ear_burst burst f3, sonic_boom charge f1-f3 and
# blast f4, dig gone by f5, pop_out clear of the ground f2 and landing f3.
KIT = [
    ("idle", [220] * 5, True),
    ("sand_kick", [260, 130, 130, 90, 160, 280], False),  # set A timings from Codex (124,616 tokens)
    ("ear_burst", [260, 130, 100, 100, 160, 280], False),
    ("sonic_boom", [300, 150, 230, 260, 100, 140, 180, 350], False),
    ("dig", [300, 120, 90, 100, 100, 180], False),  # set B timings from Codex (122,828 tokens)
    ("pop_out", [120, 90, 130, 110, 350], False),
    ("death", [300, 100, 130, 140, 160, 180, 1400], False),
]
SET_OF = {"dig": "codex-set-b", "pop_out": "codex-set-b", "death": "codex-set-b"}
NOT_FROM_STILL = {"walk", "pop_out"}  # the trot stands up; pop_out starts with only the ear tips above ground
ENDS_ON_STILL = {"idle", "sand_kick", "ear_burst", "sonic_boom", "pop_out"}
AIR = {("pop_out", 2): (140, 150)}  # drawn off the ground on purpose: allowed lowest rows
BELOW = {("dig", 3), ("dig", 4), ("dig", 5), ("pop_out", 0)}  # partly underground, cut at row 160
# se and ne rows (make_codex_diag_fennec.py, sets C and D). Packed once both views' frames exist; until then walk_se/ne
# show the side trot, idle_se/ne the still, and the engine falls back to the side view for actions.
DIAG_SET = {"idle": "codex-set-c", "walk": "codex-set-c", "sand_kick": "codex-set-c", "ear_burst": "codex-set-c",
            "sonic_boom": "codex-set-c", "dig": "codex-set-d", "pop_out": "codex-set-d", "death": "codex-set-d"}
DIAG_VIEWS = [("se", "se"), ("ne", "ne")]


def outline_colour():
    a = np.asarray(Image.open(TAKE / "views/s.png").convert("RGBA"))
    cols = np.unique(a[a[..., 3] > 127][:, :3], axis=0)
    luma = cols.astype(float) @ np.array([0.2126, 0.7152, 0.0722])
    return cols[int(np.argmin(luma))].astype(np.uint8)


def sel(im):
    return Image.fromarray(selout_rhino.selout(np.asarray(im.convert("RGBA")))[0])


def src(anim):
    return TAKE / "anim" / SET_OF.get(anim, "codex-set-a") / anim


def diag_dir(anim):
    return TAKE / "anim" / DIAG_SET[anim] / anim / "frames"


def has_diag(anim):
    return anim in DIAG_SET and all((diag_dir(anim) / f"{v}_f0.png").exists() for v in ("se", "ne"))


def frame_path(anim, vname, i):
    d = diag_dir(anim) if vname in ("se", "ne") else src(anim) / "frames"
    return d / f"{vname}_f{i}.png"


def frame(anim, vname, i):
    return sel(Image.open(frame_path(anim, vname, i)))


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
    sheet.save(OUT / "fennec_sheet.png")

    rows = [(name, view, vname, ms, loop) for name, ms, loop in KIT
            for view, vname in KIT_VIEWS + (DIAG_VIEWS if has_diag(name) else [])]
    cols = max(len(ms) for _, ms, _ in KIT)
    kit = Image.new("RGBA", (cols * CELL, len(rows) * CELL), (0, 0, 0, 0))
    for r, (name, _, vname, ms, _) in enumerate(rows):
        for i in range(len(ms)):
            kit.alpha_composite(frame(name, vname, i), (i * CELL, r * CELL))
    kit.save(OUT / "fennec_kit_sheet.png")

    subs, anims, n = [], [], 0

    def atlas(sheet_id, col, row, ticks=1.0):
        nonlocal n
        n += 1
        subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{n}"]\natlas = ExtResource("{sheet_id}")\n'
                    f"region = Rect2({col * CELL}, {row * CELL}, {CELL}, {CELL})\n")
        return f'{{\n"duration": {float(ticks)},\n"texture": SubResource("AtlasTexture_{n}")\n}}'

    walk_row = {view: r for r, (view, _) in enumerate(walk_views)}
    for view in ALL_VIEWS:  # se and ne show the side trot until they are drawn
        anims.append(entry(f"walk_{view}", ", ".join(atlas("1_sheet", i, walk_row.get(view, 1)) for i in range(8)),
                           True, WALK_FPS))
    drawn = {(name, view) for name, view, *_ in rows}
    for c, view in enumerate(ALL_VIEWS):
        if view in ("se", "ne") and ("idle", view) not in drawn:
            anims.append(entry(f"idle_{view}", atlas("1_sheet", c, still_row), True, 1))
    for r, (name, view, _, ms, loop) in enumerate(rows):
        anims.append(entry(f"{name}_{view}", ", ".join(atlas("2_kit", i, r, t / 100) for i, t in enumerate(ms)),
                           loop, 10))
    tres = ('[gd_resource type="SpriteFrames" format=3]\n\n'
            '[ext_resource type="Texture2D" path="res://art/machines/fennec/fennec_sheet.png" id="1_sheet"]\n'
            '[ext_resource type="Texture2D" path="res://art/machines/fennec/fennec_kit_sheet.png" id="2_kit"]\n\n'
            + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n")
    (OUT / "fennec_frames.tres").write_text(tres, encoding="utf8")
    print(f"outline #{bytes(selout_rhino.OUTLINE).hex()}; sheets {sheet.size} and {kit.size}, {n} atlas frames, "
          f"{len(anims)} animations")


def check():
    """Frame 0 (and the last frame of moves that end on the still) must equal the still; every frame's lowest opaque
    row is 160, except the air and underground frames named above. The frame counts must match KIT."""
    bad = []
    for name, ms, _ in [("walk", [0] * 8, True)] + KIT:
        for view, vname in KIT_VIEWS + (DIAG_VIEWS if has_diag(name) else []):
            d = frame_path(name, vname, 0).parent
            found = sorted(d.glob(f"{vname}_f*.png"), key=lambda p: int(p.stem.split("_f")[1]))
            if len(found) != len(ms):
                bad.append(f"{name}_{view}: {len(found)} frames, KIT says {len(ms)}")
            st = np.asarray(still(view))
            ends = ([] if name in NOT_FROM_STILL else [0]) + ([len(ms) - 1] if name in ENDS_ON_STILL else [])
            for i in ends:
                same = (np.asarray(frame(name, vname, i)) == st).all(axis=2).mean()
                if same < 1.0:
                    bad.append(f"{name}_{view} f{i} vs still {same:.4f}")
            for p in found:
                i = int(p.stem.split("_f")[1])
                a = np.asarray(Image.open(p).convert("RGBA"))[..., 3] > 127
                ys = np.nonzero(a.any(axis=1))[0]
                if not len(ys):
                    if (name, i) not in BELOW:
                        bad.append(f"{p.name} in {name}: empty")
                    continue
                if (name, i) in AIR:
                    lo, hi = AIR[(name, i)]
                    if not lo <= ys.max() <= hi:
                        bad.append(f"{p.name} in {name}: air frame lowest row {ys.max()}")
                elif (name, i) in BELOW:
                    if ys.max() > 160:
                        bad.append(f"{p.name} in {name}: below the ground, row {ys.max()}")
                elif ys.max() != 160:
                    bad.append(f"{p.name} in {name}: lowest row {ys.max()}")
    print("check:", "OK" if not bad else "; ".join(bad))


if __name__ == "__main__":
    pack()
    check()
