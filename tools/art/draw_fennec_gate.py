"""The fennec's small gate (Claude, 2026-11-05, game feel lane, effects spin-off).

Drawn by this script, no generator and no paid tool: a doorway of the fennec's own mint glow standing between two short
violet posts with gold bands (its plating colours), a swirl of its violets inside, and a ring on the floor under it.
The one gate behind abilities 1 (the gate the backward bolt fires from), 2 (pocket gates) and 3 (far gates).

Colours: only the fennec's palette (art/machines/fennec/fennec_cast_sheet.png), with its #141218 ink round the outside.
Texel: 0.016 m, the fennec's own (size class S), so the gate's pixels are the same size as the body's beside it.

door_fNN.png   64 x 100, standing on row 96 (the floor; SmallGate.FEET_EDGE). Played on the tilted quad, so it faces
               the camera from every side. The swirl inside is see-through (alpha 0.72-0.95), rim and posts solid.
floor_fNN.png  88 x 88, drawn from above and laid flat under the gate (1.41 m across).
Frames 0-5 open, 6-11 hold (loops), 12-17 close. Their timings are in scripts/moba3d/small_gate.gd.

Run from the project root:  python tools/art/draw_fennec_gate.py [--preview <dir>]
"""
import math
import sys
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parents[2] / "art/fx/moba3d/small_gate"

INK = (20, 18, 24)
MINT, MINT_P, MINT_W = (63, 232, 176), (200, 255, 240), (246, 255, 251)
VIO, VIO_D, VIO_DD, LILAC = (164, 107, 255), (106, 60, 200), (46, 26, 110), (224, 200, 255)
GOLD, GOLD_D = (240, 210, 122), (184, 146, 58)

W, H, GROUND = 64, 100, 96  # door canvas; rows 0-95 are drawn, the floor is the top edge of row 96
CX, CY, A, B = 32.0, 52.0, 21.0, 40.0  # the oval: centre and outer semi-axes, texels
FW = 88  # floor canvas
FR = 38.0  # floor ring outer radius at full size

ALPHA = {VIO_DD: 0.72, VIO_D: 0.82, VIO: 0.9, LILAC: 0.95}  # the swirl; everything else is solid


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = {}  # (x, y) -> (rgb, alpha)

    def put(self, x, y, c, a=1.0):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[(x, y)] = (c, a)

    def ink_edge(self, diag=False):
        """#141218 on every empty texel touching a drawn one: the outside edge (the interior is enclosed by the rim)."""
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else [])
        add = set()
        for (x, y) in self.px:
            for dx, dy in nb:
                q = (x + dx, y + dy)
                if q not in self.px and 0 <= q[0] < self.w and 0 <= q[1] < self.h:
                    add.add(q)
        for q in add:
            self.px[q] = (INK, 1.0)

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for (x, y), (c, a) in self.px.items():
            img.putpixel((x, y), c + (round(a * 255),))
        return img


def inside(x, y, a, b, cx=CX, cy=CY):
    if a <= 0 or b <= 0:
        return False
    u = (x + 0.5 - cx) / a
    v = (y + 0.5 - cy) / b
    return u * u + v * v <= 1.0


# ---- the posts ---------------------------------------------------------------------------------------------------
# 7 wide, 22 tall, drawn from the top: lamp (rows 0-2), gold collar (3), violet shaft with a gold band (4-17), plate
# (18-21). Lit from the top left, both posts alike.
SHAFT = [VIO, VIO, VIO_D, VIO_D, VIO_DD]


def post_rows(lamp):
    lamp_c = {"off": (VIO_DD, VIO_D, VIO_D), "on": (MINT, MINT_P, MINT_W), "dim": (MINT, MINT, MINT_P),
              "flash": (MINT_W, MINT_W, MINT_W)}[lamp]
    e, m, c = lamp_c
    rows = [
        {2: m, 3: c, 4: m},
        {1: e, 2: m, 3: c, 4: m, 5: e},
        {1: e, 2: e, 3: m, 4: e, 5: e},
        {1: GOLD_D, 2: GOLD, 3: GOLD, 4: GOLD, 5: GOLD_D},
    ]
    for r in range(4, 18):
        if r in (10, 11):
            rows.append({1: GOLD, 2: GOLD, 3: GOLD, 4: GOLD_D, 5: GOLD_D} if r == 10 else
                        {1: GOLD_D, 2: GOLD_D, 3: GOLD_D, 4: GOLD_D, 5: VIO_DD})
        else:
            rows.append({i + 1: SHAFT[i] for i in range(5)})
    rows.append({0: VIO, 1: VIO, 2: VIO, 3: VIO, 4: VIO_D, 5: VIO_D, 6: VIO_DD})
    for _ in range(3):
        rows.append({0: VIO_D, 1: VIO_D, 2: VIO_D, 3: VIO_DD, 4: VIO_DD, 5: VIO_DD, 6: VIO_DD})
    return rows


def draw_posts(cv, rise, lamp):
    """rise 0..1: how much of each post has come up out of the floor (its top part shows first)."""
    rows = post_rows(lamp)
    vis = round(len(rows) * rise)
    for x0 in (6, W - 13):
        for i in range(vis):
            y = GROUND - vis + i
            for dx, c in rows[i].items():
                cv.put(x0 + dx, y, c)


# ---- the doorway -------------------------------------------------------------------------------------------------
def tone(r, s, bright):
    """The swirl's colour at radius r (0 centre, 1 inner rim) and spiral position s (0..1)."""
    if r > 0.84:
        t = LILAC if s < 0.5 else VIO
    elif r < 0.2:
        t = VIO_DD
    elif s < 0.24:
        t = VIO
    elif s < 0.52:
        t = VIO_D
    else:
        t = VIO_DD
    if bright:  # the opening flash: every tone a step up
        t = {VIO_DD: VIO_D, VIO_D: VIO, VIO: LILAC, LILAC: LILAC}[t]
    return t


def draw_oval(cv, sx, phase, rim="norm", shimmer=None, bright=False):
    """sx: width as a share of the full oval. rim: "norm", "bright" (core white all round) or "white" (all three
    layers lit). shimmer: the angle (degrees, 0 = right, -90 = top) of a travelling highlight on the rim."""
    a = A * sx
    swirl = {}
    for y in range(H):
        for x in range(W):
            if not inside(x, y, a, B):
                continue
            if not inside(x, y, a - 1, B - 1):
                layer = 0  # outer
            elif not inside(x, y, a - 2, B - 2):
                layer = 1  # core
            elif not inside(x, y, a - 3, B - 3):
                layer = 2  # inner
            else:
                ai, bi = a - 3, B - 3
                u, v = (x + 0.5 - CX) / ai, (y + 0.5 - CY) / bi
                r = math.hypot(u, v)
                th = math.atan2(v, u)
                s = (2.0 * th / (2 * math.pi) + 1.25 * r - phase) % 1.0
                swirl[(x, y)] = tone(r, s, bright)
                continue
            ang = math.degrees(math.atan2((y + 0.5 - CY) / B, (x + 0.5 - CX) / max(a, 0.01)))
            lit = -170 <= ang <= -80  # the top-left arc catches the light
            near = shimmer is not None and abs((ang - shimmer + 180) % 360 - 180) <= 24
            if rim == "white":
                c = MINT_W if layer == 1 else MINT_P
            elif layer == 1:
                c = MINT_W if (lit or near or rim == "bright") else MINT_P
            else:
                c = MINT_P if near else MINT
            cv.put(x, y, c)
    # one cleanup pass: a swirl texel with no same-tone neighbour takes its neighbours' most common tone
    for (x, y), t in list(swirl.items()):
        nb = [swirl.get(q) for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))]
        nb = [n for n in nb if n is not None]
        if nb and t not in nb:
            swirl[(x, y)] = max(set(nb), key=nb.count)
    return swirl


def draw_slit(cv, top, width, flare=0):
    """A vertical line of light from the oval's bottom up to row top: a white core with mint either side."""
    bottom = int(CY + B) - 1
    cx = int(CX)
    for y in range(top, bottom + 1):
        half = width // 2 + (flare if abs(y - CY) < 6 else 0)
        for dx in range(-half - 1, half + 2):
            edge = dx in (-half - 1, half + 1)
            cv.put(cx + dx, y, MINT if edge else (MINT_W if dx == 0 else MINT_P))


def sparks(cv, pts, c=MINT_P):
    for (x, y) in pts:
        cv.put(int(x), int(y), c)


def door(spec):
    cv = Canvas(W, H)
    draw_posts(cv, spec.get("rise", 1.0), spec.get("lamp", "on"))
    swirl = {}
    if "slit" in spec:
        draw_slit(cv, *spec["slit"])
    if "sx" in spec:
        swirl = draw_oval(cv, spec["sx"], spec.get("phase", 0.0), spec.get("rim", "norm"), spec.get("shimmer"),
                          spec.get("bright", False))
    if "star" in spec:  # the pinch: a four-point star at the oval's centre
        cx, cy, r = int(CX), int(CY), spec["star"]
        for d in range(-r, r + 1):
            c = MINT_W if abs(d) < r - 1 else MINT_P
            cv.put(cx + d, cy, c)
            cv.put(cx, cy + d, c)
        for d in (-1, 1):
            for e in (-1, 1):
                cv.put(cx + d, cy + e, MINT_P)
    cv.ink_edge()
    for q, t in swirl.items():
        cv.px[q] = (t, ALPHA[t])
    sparks(cv, spec.get("sparks", []))
    sparks(cv, spec.get("sparks_w", []), MINT_W)
    return cv.image()


# ---- the floor ring ----------------------------------------------------------------------------------------------
def floor(scale, rot=0.0, bright=False, alpha=1.0, pool=True):
    cv = Canvas(FW, FW)
    c0 = FW / 2.0
    R = FR * scale
    if R < 2:
        return cv.image()
    for y in range(FW):
        for x in range(FW):
            d = math.hypot(x + 0.5 - c0, y + 0.5 - c0)
            if R - 3 <= d <= R:
                core = R - 2 <= d < R - 1
                cv.put(x, y, (MINT_W if bright else MINT_P) if core else MINT, alpha)
    for k in range(8):  # ticks just inside the ring, turning while the gate holds
        th = math.radians(k * 45 + rot)
        for t in (R - 6, R - 5, R - 4.6):
            cv.put(int(c0 + t * math.cos(th)), int(c0 + t * math.sin(th)), MINT_P, alpha)
    cv.ink_edge()
    if alpha < 1.0:
        for q, (c, a) in list(cv.px.items()):
            cv.px[q] = (c, min(a, alpha))
    if pool:
        for y in range(FW):
            for x in range(FW):
                if (x, y) not in cv.px and math.hypot(x + 0.5 - c0, y + 0.5 - c0) < R - 3:
                    cv.put(x, y, VIO_D, 0.28 * alpha)
    return cv.image()


def rising(k, n=3):
    """Sparks drifting up inside the doorway while it holds: frame k of 6."""
    pts = []
    for j in range(n):
        base_x = CX - 9 + j * 9
        y = CY + 30 - ((k * 9 + j * 23) % 56)
        pts.append((base_x + (2 if (k + j) % 2 else -1), y))
    return pts


def frames():
    out = []
    # open: posts rise, a line of light climbs between them, the oval swings open past full and settles
    out.append((dict(rise=0.45, lamp="dim", sparks_w=[(9, 86), (54, 86)]), dict(scale=0.45, bright=True)))
    out.append((dict(rise=1.0, lamp="flash", slit=(int(CY), 1)), dict(scale=0.8, bright=True)))
    out.append((dict(lamp="flash", slit=(int(CY - B) + 1, 1, 1)), dict(scale=1.0, bright=True)))
    out.append((dict(sx=0.45, rim="white", bright=True, phase=0.0), dict(scale=1.05, bright=True)))
    out.append((dict(sx=1.08, rim="bright", bright=True, phase=0.04), dict(scale=1.0)))
    out.append((dict(sx=1.0, phase=0.08), dict(scale=1.0)))
    # hold: the swirl turns, a highlight runs round the rim, the lamps pulse, sparks rise; frame 11 leads back into 6
    for k in range(6):
        out.append((dict(sx=1.0, phase=0.08 + (k + 1) / 6.0 * 0.5, shimmer=-90 + k * 60,
                         lamp="on" if k < 3 else "dim", sparks=rising(k)), dict(scale=1.0, rot=k * 7.5)))
    # close: the oval narrows to a line, the line pinches to a star, sparks burst, the posts sink
    out.append((dict(sx=0.7, rim="bright", phase=0.62), dict(scale=0.95)))
    out.append((dict(sx=0.32, rim="white", phase=0.66, bright=True), dict(scale=0.85, bright=True)))
    out.append((dict(lamp="flash", slit=(int(CY - B) + 1, 1)), dict(scale=0.7, bright=True)))
    out.append((dict(lamp="flash", slit=(int(CY) - 10, 1), star=6), dict(scale=0.55, bright=True)))
    burst = [(CX + 11 * math.cos(math.radians(a)), CY + 11 * math.sin(math.radians(a))) for a in range(0, 360, 45)]
    out.append((dict(rise=0.5, lamp="dim", sparks_w=burst), dict(scale=0.4, alpha=0.6, pool=False)))
    far = [(CX + 17 * math.cos(math.radians(a + 22)), CY + 17 * math.sin(math.radians(a + 22))) for a in range(0, 360, 90)]
    out.append((dict(rise=0.15, lamp="off", sparks=far), dict(scale=0.25, alpha=0.35, pool=False)))
    return out


def preview(dirpath, imgs):
    """A strip of every frame at 3x as the game camera roughly sees it: the floor ring squashed to the 35-degree
    ellipse under the door, on a dark arena grey, plus a gif at the game's timings."""
    from math import sin, radians
    sq = sin(radians(35))
    cell_w, cell_h = 96, 120
    strip = Image.new("RGBA", (cell_w * len(imgs), cell_h), (52, 56, 62, 255))
    gif = []
    ms = [60, 60, 60, 60, 80, 80] + [100] * 6 + [60, 60, 60, 60, 80, 80]
    for i, (d, f) in enumerate(imgs):
        cell = Image.new("RGBA", (cell_w, cell_h), (52, 56, 62, 255))
        fl = f.resize((FW, max(1, round(FW * sq))), Image.NEAREST)
        cell.alpha_composite(fl, ((cell_w - FW) // 2, 104 - fl.height // 2))
        cell.alpha_composite(d, ((cell_w - W) // 2, 104 - GROUND))
        strip.alpha_composite(cell, (i * cell_w, 0))
        gif.append(cell.resize((cell_w * 3, cell_h * 3), Image.NEAREST).convert("RGB"))
    strip.resize((strip.width * 3, strip.height * 3), Image.NEAREST).save(Path(dirpath) / "gate_strip_3x.png")
    loop = gif + gif[6:12] * 2 + gif[12:]
    loop_ms = ms + ms[6:12] * 2 + ms[12:]
    gif[0].save(Path(dirpath) / "gate_preview_3x.gif", save_all=True, append_images=loop[1:], duration=loop_ms, loop=0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    imgs = []
    for i, (d, f) in enumerate(frames()):
        di = door(d)
        fi = floor(**f)
        di.save(OUT / f"door_f{i:02d}.png")
        fi.save(OUT / f"floor_f{i:02d}.png")
        imgs.append((di, fi))
    print(f"wrote {len(imgs)} door and floor frames to {OUT}")
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1], imgs)


if __name__ == "__main__":
    main()
