"""Pack the rhino's sprites and kit effects for the 3D slice (Claude, 2026-11-04). Preston: "yes go 3D", then
"build kit and then show me like its a smite ... god reveal".

Writes into art/machines/rhino/:
  rhino_sheet.png      192x192 cells: rows 0-4 are walk s, se, e, ne, n (8 frames); row 5 is the idle stills in the
                       same view order. West views are the east ones mirrored in the engine.
  rhino_kit_sheet.png  192x192 cells: one row per kit animation and view (front s, side e, back n, then se and ne
                       where Codex sets C and D have drawn them; see DIAG). brace_shuffle once set D lands.
  rhino_frames.tres    SpriteFrames: walk_<view> (8 fps, looping); idle_s, idle_e, idle_n animated (Codex's idle),
                       idle_se and idle_ne as stills; and <action>_<s|e|n> for horn_jab, horn_toss, brace, stampede,
                       death and ground_pound, with per-frame holds from the timings the 2D reels used.
Writes into art/fx/moba3d/:
  <effect>_f<i>.png    Codex's kit effects (codex-set-b/effects) and the ground pound ring (codex-ground-pound/clean/
                       effect), each padded so its anchor sits at the canvas centre. brace_ring keeps its canvas
                       because the engine lays it flat on the ground.
  fx_frames.tres       SpriteFrames for the billboard effects.
  training_dummy.png, cracks.png, slow_disc.png, bolt.png   our own art for trying the kit on.
Rerun after any change to the frames (and after selout_rhino.py).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ANIM = ROOT / "docs/art/moba/rhino_l/take-a/anim"
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402

# 2026-11-04, Preston "Yes, pack it": the walk drawn at 35 degrees from the approved views_cam35 (walk35/, Codex runs
# 1 and 2 plus a leg cleanup, 0.48 m/s planted at 8 fps; sel-out by walk35_selout.py). The old low-angle walk stays
# in codex-set-a/walk/frames_selout; the files packed before the swap are in walk35/backup_pre_pack.
WALK = ANIM / "walk35/walk/frames_selout"
# 2026-11-05, Preston "Pack as is" (via the Rhino session): se, side and ne play the touch-up lane's leg rebuild
# (walk35_touchup/, drawn from views_cam35_touchup; sel-out by walk35_touchup/selout_rebuild.py). Front and back stay
# walk35. The files packed before this change are in walk35_touchup/backup_pre_pack.
WALK_REBUILD = ANIM / "walk35_touchup/frames_selout"
WALK_BY_VIEW = {"se": WALK_REBUILD, "side": WALK_REBUILD, "ne": WALK_REBUILD}
GP = ANIM / "codex-ground-pound/clean"
VIEWS = [("s", "front"), ("se", "se"), ("e", "side"), ("ne", "ne"), ("n", "back")]
KIT_VIEWS = [("s", "front"), ("e", "side"), ("n", "back")]  # actions are drawn in three views
# name, folder, [(drawn frame, ticks at 10 per second)], loop. Holds follow the 2D reels (rhino_reel.py; composite.py
# for the ground pound: F0, F1 x2, F2, F3 x3, F4 slam x3, F5 x3).
KIT = [
    # 2026-11-04, Preston "Swap now" (via the hub): the idle is the approved 35-degree views (views_cam35) with the
    # diag_idle breath, built by cam35-idle/build_cam35_idle.py. The old idle stays in codex-set-a/idle and
    # codex-set-d/idle; the files packed before the swap are in cam35-idle/backup_pre_cam35.
    ("idle", ANIM / "cam35-idle", [(i, 2) for i in range(5)], True),
    ("horn_jab", ANIM / "codex-set-a/horn-jab", [(0, 2), (1, 2), (2, 1), (3, 2), (4, 1), (5, 1)], False),
    ("horn_toss", ANIM / "codex-set-a/horn-toss", [(0, 2), (1, 1), (2, 1), (3, 1), (4, 2), (5, 1), (6, 1)], False),
    ("brace", ANIM / "codex-set-b/brace", [(i, 1) for i in range(5)], False),
    ("stampede", ANIM / "codex-set-b/stampede", [(i, 1) for i in range(1, 7)], True),
    ("death", ANIM / "codex-set-b/death", [(i, 1) for i in range(6)] + [(6, 4)], False),
    ("ground_pound", GP, [(0, 1), (1, 2), (2, 1), (3, 3), (4, 3), (5, 3)], False),
    ("brace_shuffle", ANIM / "codex-set-d/brace-shuffle", [(i, 1) for i in range(6)], True),
]
# The se and ne rows of each action, drawn later by Codex (make_codex_diag.py, sets C and D). Packed only once their
# sel-out frames exist; until then the engine shows the side view for that action (directional_sprite_3d.gd).
DIAG = {"idle": "cam35-idle","horn_jab": "codex-set-c/horn-jab", "horn_toss": "codex-set-c/horn-toss",
        "brace": "codex-set-d/brace", "stampede": "codex-set-c/stampede", "death": "codex-set-d/death",
        "ground_pound": "codex-set-c/ground-pound"}
DIAG_VIEWS = [("se", "se"), ("ne", "ne")]


def kit_rows():
    """(name, view, frames folder, seq, loop) for every drawn action row, in sheet order."""
    rows = []
    for name, d, seq, loop in KIT:
        if not (d / "frames_selout").exists():
            continue
        rows += [(name, view, d / "frames_selout", vname, seq, loop) for view, vname in KIT_VIEWS]
        dd = ANIM / DIAG.get(name, "-") / "frames_selout"
        if dd.exists():
            rows += [(name, view, dd, vname, seq, loop) for view, vname in DIAG_VIEWS]
    return rows
FX_SPEED = {"hit_spark": 15, "deflect_spark": 15, "impact_puff": 12, "dust_trail": 12, "stun_loop": 10, "gp_ring": 10}
OUT = ROOT / "art/machines/rhino"
FX = ROOT / "art/fx/moba3d"
FIELD = ROOT / "art/field/moba3d"
CELL = 192
INK = (0x14, 0x12, 0x18)


def still(name):
    # The approved views for every facing (2026-11-04, sprite factory: the ground pound's f0 back carried half the
    # approved back still's ink and plain knee discs). name is front/se/side/ne/back; views/ uses s/se/e/ne/n.
    name = {"front": "s", "side": "e", "back": "n"}.get(name, name)
    a = np.asarray(Image.open(ANIM.parent / "views" / f"{name}.png").convert("RGBA"))
    return Image.fromarray(selout(a)[0])


# Animations drawn from the game camera's angle (35 degrees). DirectionalSprite3D tilts the quad back to face the camera
# only while one of these plays (game feel lane, 2026-11-04); no meta means no tilt. Names carry no view suffix.
# The walk is drawn at 35 degrees since 2026-11-04 (walk35/), so it tilts with the idle; the moves are still drawn at
# the old low angle and stay upright.
TILT_ANIMS = ["idle", "walk"]


# The rhino's feet in texels from the canvas centre column (camera lane, 2026-11-04, measured from the e and s views;
# the old and the 35-degree views agree). DirectionalSprite3D stands the drawing's ground centre on the machine's
# spot with it, and the contact shadow sits under the feet.
FEET = {"front": 7, "rear": -33, "half_width": 20}


def tilt_meta():
    return ("metadata/tilt_anims = [" + ", ".join(f'"{a}"' for a in TILT_ANIMS) + "]\n"
            + "metadata/feet = {" + ", ".join(f'"{k}": {v}' for k, v in FEET.items()) + "}\n")


def entry(name, frames, loop, speed):
    return (f'{{\n"frames": [{frames}],\n"loop": {"true" if loop else "false"},\n"name": &"{name}",\n'
            f'"speed": {float(speed)}\n}}')


def pack():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (8 * CELL, 6 * CELL), (0, 0, 0, 0))
    for r, (_, name) in enumerate(VIEWS):
        for i in range(8):
            sheet.alpha_composite(Image.open(WALK_BY_VIEW.get(name, WALK) / f"{name}_f{i}.png").convert("RGBA"), (i * CELL, r * CELL))
        sheet.alpha_composite(still(name), (r * CELL, 5 * CELL))
    sheet.save(OUT / "rhino_sheet.png")
    rows = kit_rows()
    kit = Image.new("RGBA", (7 * CELL, len(rows) * CELL), (0, 0, 0, 0))
    for r, (_, _, d, vname, seq, _) in enumerate(rows):
        for i in range(max(f for f, _ in seq) + 1):
            kit.alpha_composite(Image.open(d / f"{vname}_f{i}.png").convert("RGBA"), (i * CELL, r * CELL))
    kit.save(OUT / "rhino_kit_sheet.png")
    subs, anims, n = [], [], 0

    def atlas(sheet_id, col, row, ticks=1):
        nonlocal n
        n += 1
        subs.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{n}"]\natlas = ExtResource("{sheet_id}")\n'
                    f"region = Rect2({col * CELL}, {row * CELL}, {CELL}, {CELL})\n")
        return f'{{\n"duration": {float(ticks)},\n"texture": SubResource("AtlasTexture_{n}")\n}}'

    for r, (view, _) in enumerate(VIEWS):
        anims.append(entry(f"walk_{view}", ", ".join(atlas("1_sheet", i, r) for i in range(8)), True, 8))
    drawn = {(name, view) for name, view, *_ in rows}
    for r, (view, _) in enumerate(VIEWS):
        if view in ("se", "ne") and ("idle", view) not in drawn:  # still idle until the diagonal idle is drawn
            anims.append(entry(f"idle_{view}", atlas("1_sheet", r, 5), True, 1))
    for r, (name, view, _, _, seq, loop) in enumerate(rows):
        anims.append(entry(f"{name}_{view}", ", ".join(atlas("2_kit", f, r, t) for f, t in seq), loop, 10))
    tres = ('[gd_resource type="SpriteFrames" format=3]\n\n'
            '[ext_resource type="Texture2D" path="res://art/machines/rhino/rhino_sheet.png" id="1_sheet"]\n'
            '[ext_resource type="Texture2D" path="res://art/machines/rhino/rhino_kit_sheet.png" id="2_kit"]\n\n'
            + "\n".join(subs) + "\n[resource]\n" + tilt_meta() + "animations = [" + ", ".join(anims) + "]\n")
    (OUT / "rhino_frames.tres").write_text(tres, encoding="utf8")
    print(f"sheets {sheet.size} and {kit.size}, {n} atlas frames, {len(anims)} animations")


def fx():
    FX.mkdir(parents=True, exist_ok=True)
    eff = ANIM / "codex-set-b/effects"
    meta = json.loads((eff / "anchor.json").read_text())
    gp = json.loads((GP / "effect/anchor.json").read_text())
    sets = {k.replace("-", "_"): ([Image.open(eff / k / f"f{i}.png").convert("RGBA") for i in range(6)],
                                  meta[k]["anchor"]) for k in meta}
    sets["gp_ring"] = ([Image.open(GP / "effect" / f["file"]).convert("RGBA") for f in gp["frames"]], gp["anchor"])
    ext, anims = [], []
    for name, (ims, (ax, ay)) in sets.items():
        if name == "brace_ring":  # laid flat on the ground by Fx3D.spawn_flat, so it keeps its canvas
            for i, im in enumerate(ims):
                im.save(FX / f"{name}_f{i}.png")
            continue
        w = 2 * max(max(ax + 1, im.width - ax) for im in ims)
        h = 2 * max(max(ay + 1, im.height - ay) for im in ims)
        frames = []
        for i, im in enumerate(ims):
            out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            out.alpha_composite(im, (w // 2 - ax, h // 2 - ay))
            out.save(FX / f"{name}_f{i}.png")
            ext.append(f'[ext_resource type="Texture2D" path="res://art/fx/moba3d/{name}_f{i}.png" id="{len(ext) + 1}"]')
            frames.append(f'{{\n"duration": 1.0,\n"texture": ExtResource("{len(ext)}")\n}}')
        anims.append(entry(name, ", ".join(frames), name == "stun_loop", FX_SPEED[name]))
    (FX / "fx_frames.tres").write_text('[gd_resource type="SpriteFrames" format=3]\n\n' + "\n".join(ext)
                                       + "\n\n[resource]\nanimations = [" + ", ".join(anims) + "]\n", encoding="utf8")
    print(f"effects: {', '.join(sets)}")


def hx(*cs):
    return np.array([[int(c[i:i + 2], 16) for i in (0, 2, 4)] for c in cs], np.uint8)


def outline(a):
    op = a[..., 3] > 0
    ring = np.zeros_like(op)
    ring[1:] |= op[:-1]
    ring[:-1] |= op[1:]
    ring[:, 1:] |= op[:, :-1]
    ring[:, :-1] |= op[:, 1:]
    ring &= ~op
    a[ring, :3] = INK
    a[ring, 3] = 255
    return a


def shade_disc(a, cx, cy, rx, ry, ramp):
    """A lit ellipse in ramp steps, light from the top left like the machines."""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    dx, dy = (xx - cx) / rx, (yy - cy) / ry
    d2 = dx * dx + dy * dy
    m = d2 <= 1.0
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    s = -(dx * 0.55 + dy * 0.8) * 0.8 + nz * 0.5 - 0.15
    lv = np.clip(np.round((s + 0.7) / 1.5 * (len(ramp) - 1)), 0, len(ramp) - 1).astype(int)
    a[m, :3] = ramp[lv[m]]
    a[m, 3] = 255


def training_dummy():
    """A sack-and-post training dummy with a painted target, 48x88 (about 1.7 m)."""
    w, h = 48, 88
    a = np.zeros((h, w, 4), np.uint8)
    bark = hx("3E2A1A", "5E4028", "7E5A38", "9C7650")
    sack = hx("6E5530", "9C7E4A", "C4A468", "E2C98E")
    cx = w // 2
    a[h - 7:h - 3, cx - 15:cx + 15] = (*bark[1], 255)  # base plank
    a[h - 7, cx - 15:cx + 15, :3] = bark[3]
    for x in range(cx - 3, cx + 3):  # post, lit on the left
        a[18:h - 7, x] = (*(bark[3] if x < cx - 1 else bark[2] if x < cx + 1 else bark[1]), 255)
    a[33:37, cx - 21:cx + 21] = (*bark[2], 255)  # arms
    a[33, cx - 21:cx + 21, :3] = bark[3]
    a[36, cx - 21:cx + 21, :3] = bark[1]
    shade_disc(a, cx, 44, 13, 18, sack)  # body
    shade_disc(a, cx, 14, 9, 9, sack)  # head
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot(xx - cx, yy - 44)
    for rad, col in ((7, (0xFF, 0x3A, 0x2A)), (5, (0xFF, 0xF4, 0xA8)), (3, (0xFF, 0x3A, 0x2A)), (1, (0xFF, 0xF4, 0xA8))):
        a[r <= rad + 0.3, :3] = col
    for y in (26, 27, 59):  # rope ties at the neck and the waist
        a[y, a[y, :, 3] > 0, :3] = bark[0]
    return outline(a)


def cracks(n=160, seed=5):
    """Ground cracks radiating from the slam: dark splits with a lit lip, around a small crater."""
    rng = np.random.default_rng(seed)
    a = np.zeros((n, n, 4), np.uint8)
    c = n / 2

    def walk(x, y, ang, length, depth):
        for _ in range(int(length)):
            ang += rng.normal(0, 0.22)
            x, y = x + np.cos(ang), y + np.sin(ang)
            ix, iy = int(round(x)), int(round(y))
            if not (1 <= ix < n - 1 and 1 <= iy < n - 2) or np.hypot(x - c, y - c) > c - 3:
                return
            a[iy, ix] = (*INK, 255)
            if a[iy + 1, ix, 3] == 0:
                a[iy + 1, ix] = (0x8D, 0x71, 0x57, 255)
            if depth < 2 and rng.random() < 0.035:
                walk(x, y, ang + rng.choice([-0.9, 0.9]), length * 0.4, depth + 1)

    for k in range(9):
        a0 = k / 9 * 2 * np.pi + rng.normal(0, 0.2)
        walk(c + np.cos(a0) * 7, c + np.sin(a0) * 7, a0, rng.uniform(0.6, 0.95) * (c - 7), 0)
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx - c, yy - c)
    a[(d <= 9) & (a[..., 3] == 0)] = (0x75, 0x54, 0x3A, 255)
    a[d <= 6] = (0x3D, 0x3A, 0x44, 255)
    return a


def slow_disc(n=160):
    """The slow patch: a faint violet disc with a firmer rim (slows read violet in most MOBAs)."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2)
    a = np.zeros((n, n, 4), np.uint8)
    a[d <= n / 2 - 1] = (0x6B, 0x4F, 0xC8, 70)
    a[(d > n / 2 - 5) & (d <= n / 2 - 1)] = (0x9B, 0x7B, 0xF0, 190)
    return a


def bolt(n=18):
    """A hostile bolt for showing the plating at work."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2)
    a = np.zeros((n, n, 4), np.uint8)
    for r, col in ((7.6, INK), (6.4, (0xFF, 0x3A, 0x2A)), (4.4, (0xFF, 0xCF, 0x1F)), (2.2, (0xFF, 0xF4, 0xA8))):
        a[d <= r] = (*col, 255)
    return a


def kit_art():
    for name, a in (("training_dummy", training_dummy()), ("cracks", cracks()), ("slow_disc", slow_disc()),
                    ("bolt", bolt())):
        Image.fromarray(a).save(FX / f"{name}.png")
    print("kit art: training_dummy, cracks, slow_disc, bolt")


def hexes(*cs):
    return [tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,) for c in cs]


def world():
    """The first placeholder tiles. tools/art/make_moba3d_field.py owns the field art now; call this only to rebuild
    ring.png and stone_tile.png."""
    FIELD.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    s = hexes("2E2C36", "4A4854", "5E5C69", "75737F")
    b = np.zeros((32, 32, 4), np.uint8)
    b[...] = s[2]
    b[(rng.random((32, 32)) < 0.2)] = s[1]
    b[(rng.random((32, 32)) > 0.9)] = s[3]
    for y in (0, 15):
        b[y] = s[0]
    for y0, xs in ((1, (0, 16)), (16, (8, 24))):
        for x in xs:
            b[y0:y0 + 14, x] = s[0]
    Image.fromarray(b).save(FIELD / "stone_tile.png")
    yy, xx = np.mgrid[0:64, 0:64] - 31.5
    d = np.hypot(xx, yy)
    ring = np.zeros((64, 64, 4), np.uint8)
    ring[(d > 27) & (d <= 30)] = (0x3F, 0xA9, 0xFF, 220)
    ring[(d > 25.5) & (d <= 27)] = (0xA8, 0xDC, 0xFF, 140)
    Image.fromarray(ring).save(FIELD / "ring.png")


if __name__ == "__main__":
    pack()
    fx()
    kit_art()
