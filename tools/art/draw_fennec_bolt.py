"""The fennec's bolt (Claude, 2026-11-05, game feel lane, effects spin-off; Preston: "Draw the bolt").

Drawn by this script, no generator and no paid tool, in the same palette, ink and texel (0.016 m) as the small gate
(draw_fennec_gate.py): a dart of the gate's energy with a mint head and a violet tail, plus a launch flash, an impact
burst and the sparks it leaves behind.

The bolt flies in the 3D world, but its sprite faces the camera, so it is drawn at 16 screen angles (22.5 degrees
apart) and FennecBolt picks the one nearest the way it is moving on screen. Each angle is rasterised from the shape
itself, never rotated from another drawing, so the pixels stay crisp.

bolt_sheet.png    16 rows (angle k x 22.5 degrees, 0 = pointing right, turning clockwise on screen) x 4 frames,
                  40 x 40 cells, the bolt's middle at the cell centre.
burst_sheet.png   rows: 0 launch flash (4 frames), 1 impact (6), 2 trail spark (4); 40 x 40 cells, centred.
dart_sheet.png    the basic attack's dart, laid out like bolt_sheet (2026-11-05, Preston: "we need basic attacks").
dart_hit_sheet.png  where the dart strikes: 5 frames in one row of 40 x 40 cells (6 cells wide, like burst_sheet).
Timings are in scripts/moba3d/fennec_bolt.gd.

Run from the project root:  python tools/art/draw_fennec_bolt.py [--preview <dir>]
"""
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_fennec_gate import LILAC, MINT, MINT_P, MINT_W, VIO, VIO_D, Canvas  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "art/fx/moba3d/fennec_bolt"
BC = 40  # bolt cell
FC = 40  # burst cell
ANGLES = 16


# ---- the bolt ----------------------------------------------------------------------------------------------------
def bolt_texel(u, v, f):
    """The colour and alpha at (u along the flight, v across), frame f, or None. A dart: the point at u 13, widest
    (about 10 texels) from u 1 to 6, the tail a violet ribbon tapering back to about u -15. Second take: the first was
    7 texels wide with a dark violet tail, a thin line at the game camera that the floor swallowed."""
    av = abs(v)
    if 6.0 <= u <= 13.0:
        half = 4.6 * ((13.0 - u) / 7.0) ** 0.6  # the point
    elif 1.0 <= u < 6.0:
        half = 4.6
    else:
        tail_end = -15.0 - (1.5 if f in (1, 3) else 0.0)
        if not tail_end <= u < 1.0:
            return None
        k = (u - tail_end) / (1.0 - tail_end)  # 0 at the tip of the tail, 1 by the head
        half = 1.0 + 3.6 * k
        if av > half:
            return None
        pulse = -1.5 - f * 3.5  # a bright band runs down the tail, one step a frame
        if abs(u - pulse) < 0.9 and av <= half - 0.6:
            return MINT_W, 1.0
        if av <= 0.5:
            return (MINT_P if k > 0.55 else LILAC), 1.0  # the bright line down the middle
        if k > 0.7:
            return MINT, 1.0
        return VIO, (1.0 if k > 0.25 else 0.8)
    if av > half:
        return None
    core = 1.9 if f % 2 == 0 else 1.5
    if 2.5 <= u <= 10.5 and av <= core:
        return MINT_W, 1.0
    if av <= half - 1.2:
        return MINT_P, 1.0
    return MINT, 1.0


def bolt_cell(angle_deg, f):
    cv = Canvas(BC, BC)
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    c0 = BC / 2.0
    for y in range(BC):
        for x in range(BC):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0  # screen, y down
            u = dx * ca + dy * sa
            v = -dx * sa + dy * ca
            t = bolt_texel(u, v, f)
            if t is not None:
                cv.put(x, y, t[0], t[1])
    cv.ink_edge()
    # a soft mint glow one texel round the outside of the head
    glow = set()
    for (x, y) in list(cv.px):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            q = (x + dx, y + dy)
            if q in cv.px or not (0 <= q[0] < BC and 0 <= q[1] < BC):
                continue
            qu = (q[0] + 0.5 - c0) * ca + (q[1] + 0.5 - c0) * sa
            if qu > -1.0:
                glow.add(q)
    for q in glow:
        cv.put(q[0], q[1], MINT, 0.4)
    # two sparks peel off the tail and slide back along it, a different pair each frame
    for j in range(2):
        u = -4.0 - ((f * 3 + j * 6) % 11)
        v = (3.6 if (f + j) % 2 else -3.6)
        x = int(c0 + u * ca - v * sa)
        y = int(c0 + u * sa + v * ca)
        cv.put(x, y, MINT_P if j == 0 else LILAC)
    return cv.image()


# ---- the basic attack's dart (2026-11-05, Preston: "we need basic attacks") ------------------------------------------
def dart_texel(u, v, f):
    """The fennec's basic attack: half the two-faced shot's bolt and violet-led, so the two never read alike. The point
    at u 8, widest (about 6 texels) from u 0 to 3.5, a short lilac tail to about u -9, a white core that flickers.
    (One size up from the first take: the bolt's first take showed that about 5 texels is lost on the floor.)"""
    av = abs(v)
    if 3.5 <= u <= 8.0:
        half = 3.1 * ((8.0 - u) / 4.5) ** 0.6
    elif 0.0 <= u < 3.5:
        half = 3.1
    else:
        tail_end = -9.0 - (1.0 if f in (1, 3) else 0.0)
        if not tail_end <= u < 0.0:
            return None
        k = (u - tail_end) / (0.0 - tail_end)
        half = 0.6 + 2.2 * k
        if av > half:
            return None
        if av <= 0.5:
            return (LILAC if k > 0.4 else VIO), 1.0
        return VIO, (1.0 if k > 0.3 else 0.75)
    if av > half:
        return None
    core = 1.3 if f % 2 == 0 else 0.8
    if 0.5 <= u <= 6.0 and av <= core:
        return MINT_W, 1.0
    if av <= half - 1.0:
        return LILAC, 1.0
    return VIO, 1.0


def dart_cell(angle_deg, f):
    cv = Canvas(BC, BC)
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    c0 = BC / 2.0
    for y in range(BC):
        for x in range(BC):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0
            t = dart_texel(dx * ca + dy * sa, -dx * sa + dy * ca, f)
            if t is not None:
                cv.put(x, y, t[0], t[1])
    cv.ink_edge()
    glow = set()
    for (x, y) in list(cv.px):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in cv.px or not (0 <= q[0] < BC and 0 <= q[1] < BC):
                continue
            if (q[0] + 0.5 - c0) * ca + (q[1] + 0.5 - c0) * sa > 0.0:
                glow.add(q)
    for q in glow:
        cv.put(q[0], q[1], VIO, 0.35)
    return cv.image()


# ---- the bursts --------------------------------------------------------------------------------------------------
def ring(cv, r, w, c, gaps=0, rot=0.0):
    c0 = FC / 2.0
    for y in range(FC):
        for x in range(FC):
            d = math.hypot(x + 0.5 - c0, y + 0.5 - c0)
            if r - w <= d <= r:
                if gaps:
                    ang = (math.degrees(math.atan2(y + 0.5 - c0, x + 0.5 - c0)) - rot) % (360 / gaps)
                    if ang > 360 / gaps * 0.6:
                        continue
                cv.put(x, y, c)


def disc(cv, r, c):
    ring(cv, r, r + 1, c)


def star(cv, r, c_mid=MINT_W, c_tip=MINT_P):
    c0 = FC // 2
    for d in range(-r, r + 1):
        c = c_mid if abs(d) < r - 1 else c_tip
        cv.put(c0 + d, c0, c)
        cv.put(c0, c0 + d, c)


def spokes(cv, r, n, c, rot=0.0, length=2):
    c0 = FC / 2.0
    for k in range(n):
        a = math.radians(rot + k * 360 / n)
        for t in range(length):
            cv.put(int(c0 + (r + t) * math.cos(a)), int(c0 + (r + t) * math.sin(a)), c)


def burst(kind, f):
    cv = Canvas(FC, FC)
    sparks = []
    if kind == "flash":  # where a bolt leaves the fennec or the gate
        if f == 0:
            disc(cv, 4.2, MINT_P)
            disc(cv, 2.4, MINT_W)
            star(cv, 9)
        elif f == 1:
            ring(cv, 8, 2.4, MINT_P)
            disc(cv, 3.0, MINT_W)
        elif f == 2:
            ring(cv, 10.5, 1.4, MINT)
            sparks = [(11, 4, MINT_P, 45)]
        else:
            sparks = [(13.5, 4, MINT, 45)]
    elif kind == "impact":  # where it hits a target or a wall
        if f == 0:
            disc(cv, 6.0, MINT_P)
            disc(cv, 3.6, MINT_W)
            star(cv, 12)
        elif f == 1:
            ring(cv, 9.5, 2.6, MINT_P)
            disc(cv, 6.0, VIO)
            disc(cv, 3.0, MINT_W)
        elif f == 2:
            ring(cv, 13, 2.2, MINT)
            disc(cv, 4.4, VIO)
            disc(cv, 2.0, LILAC)
            sparks = [(15, 6, MINT_P, 15)]
        elif f == 3:
            ring(cv, 16, 1.4, MINT, gaps=6, rot=20)
            disc(cv, 1.8, VIO)
            sparks = [(17, 6, MINT_P, 15)]
        elif f == 4:
            sparks = [(17.5, 6, MINT, 15), (13, 3, VIO, 75)]
        else:
            sparks = [(18, 3, LILAC, 15)]
    elif kind == "dart_hit":  # where the basic attack's dart strikes: the impact's shape, two thirds the size, violet
        if f == 0:
            disc(cv, 4.0, LILAC)
            disc(cv, 2.2, MINT_W)
            star(cv, 8, MINT_W, LILAC)
        elif f == 1:
            ring(cv, 6.5, 2.2, LILAC)
            disc(cv, 4.0, VIO)
            disc(cv, 2.0, MINT_W)
            sparks = [(8, 4, LILAC, 45)]
        elif f == 2:
            ring(cv, 9, 1.8, LILAC)
            disc(cv, 2.2, VIO)
            sparks = [(10, 6, MINT_P, 15)]
        elif f == 3:
            ring(cv, 10.5, 1.2, VIO, gaps=6, rot=20)
            sparks = [(12, 6, LILAC, 15)]
        else:
            sparks = [(12.5, 3, VIO, 75)]
    else:  # trail spark
        c0 = FC // 2
        if f == 0:
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                cv.put(c0 + dx, c0 + dy, MINT_W if (dx, dy) == (0, 0) else MINT_P)
        elif f == 1:
            cv.put(c0, c0, MINT_P)
            cv.put(c0 + 1, c0 - 1, MINT)
        elif f == 2:
            cv.put(c0, c0, MINT)
        else:
            cv.put(c0, c0, VIO)
    if kind != "spark" and cv.px:
        cv.ink_edge()
    for r, n, c, rot in sparks:
        spokes(cv, r, n, c, rot)
    return cv.image()


FLASH, IMPACT, SPARK = 4, 6, 4
DART_HIT = 5


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (BC * 4, BC * ANGLES), (0, 0, 0, 0))
    for k in range(ANGLES):
        for f in range(4):
            sheet.alpha_composite(bolt_cell(k * 360.0 / ANGLES, f), (f * BC, k * BC))
    sheet.save(OUT / "bolt_sheet.png")
    darts = Image.new("RGBA", (BC * 4, BC * ANGLES), (0, 0, 0, 0))
    for k in range(ANGLES):
        for f in range(4):
            darts.alpha_composite(dart_cell(k * 360.0 / ANGLES, f), (f * BC, k * BC))
    darts.save(OUT / "dart_sheet.png")
    bursts = Image.new("RGBA", (FC * 6, FC * 3), (0, 0, 0, 0))
    for row, (kind, n) in enumerate((("flash", FLASH), ("impact", IMPACT), ("spark", SPARK))):
        for f in range(n):
            bursts.alpha_composite(burst(kind, f), (f * FC, row * FC))
    bursts.save(OUT / "burst_sheet.png")
    hits = Image.new("RGBA", (FC * 6, FC), (0, 0, 0, 0))
    for f in range(DART_HIT):
        hits.alpha_composite(burst("dart_hit", f), (f * FC, 0))
    hits.save(OUT / "dart_hit_sheet.png")
    print("wrote", OUT / "bolt_sheet.png", "and", OUT / "burst_sheet.png")
    if "--preview" in sys.argv:
        d = Path(sys.argv[sys.argv.index("--preview") + 1])
        for name, img in (("bolt_sheet", sheet), ("burst_sheet", bursts), ("dart_sheet", darts), ("dart_hit_sheet", hits)):
            bg = Image.new("RGBA", img.size, (30, 40, 80, 255))  # about the arena floor's blue
            bg.alpha_composite(img)
            bg.resize((img.width * 4, img.height * 4), Image.NEAREST).save(d / f"{name}_4x.png")


if __name__ == "__main__":
    main()
