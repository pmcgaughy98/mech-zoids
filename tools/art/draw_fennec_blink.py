"""The fennec's blink flash (Claude, 2026-11-05, game feel lane, effects spin-off; Preston: "Blink flash").

Drawn by this script, no generator and no paid tool, in the palette and texel (0.016 m) of the small gate and the bolt
(draw_fennec_gate.py). The blink is instant: the fennec leaves one spot and stands at another on the same frame. This
is the light at both ends. The fennec's own shape in light (its ghost) is not drawn here: BlinkFlash makes it in the
game from the frame the fennec is showing, so it matches every view and pose. This sheet is the rest:
  out (where it leaves): frames 0-1 are the ghost's (it flashes white, then squeezes); a slit of light with a star at
      chest height, the star bursting into sparks, the sparks and motes drifting and fading.
  in (where it lands): motes pulling in to a star, the star opening to a slit; frames 2-4 are the ghost's (the slit
      widens into the fennec's shape in white, which fades to show the body), with sparks and motes rising off it.
Each has a ring on the floor under it, drawn flat (the game lays it on the floor). A first take had a plain column of
light where the ghost is; it read as a pill, not as the fennec.

blink_sheet.png   the standing light: rows 0 out, 1 in; 6 frames each; 64 x 112 cells; the floor is the top edge of
                  row 108, the middle is column 32 (BlinkFlash stands it on the tilted quad, like the machines).
blink_floor.png   the ring: rows 0 out, 1 in; 6 frames each; 72 x 72 cells, centred.
Timings are in scripts/moba3d/blink_flash.gd.

Run from the project root:  python tools/art/draw_fennec_blink.py [--preview <dir>]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_fennec_gate import LILAC, MINT, MINT_P, MINT_W, VIO, VIO_D, Canvas  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "art/fx/moba3d/blink_flash"
W, H = 64, 112
FE = 108  # feet edge row
CX = 32
CHEST = 44  # texels above the floor: the middle of the fennec's body (the gate's doorway middle is the same height)
FW = 72  # floor cell
FRAMES = 6


def up(y):
    return FE - (y + 0.5)


# ---- the standing light ------------------------------------------------------------------------------------------
def column(cv, w, h, alpha=1.0, hollow=0.0, scan=False):
    """A rounded column from the floor up to h, w wide. Bands from the middle out: white, pale mint, mint.
    hollow: the middle fraction left empty (the column peeling open). scan: every third row dimmed (a shimmer)."""
    for y in range(H):
        yu = up(y)
        if not 0.0 <= yu <= h:
            continue
        for x in range(W):
            dx = abs(x + 0.5 - CX)
            n = (dx / (w / 2.0)) ** 2 + (abs(yu - h / 2.0) / (h / 2.0)) ** 6
            if n > 1.0 or dx / (w / 2.0) < hollow:
                continue
            a = alpha
            if scan and int(yu) % 3 == 0:
                a *= 0.55
            if n < 0.3 and hollow == 0.0:
                cv.put(x, y, MINT_W, a)
            elif n < 0.65:
                cv.put(x, y, MINT_P, a)
            else:
                cv.put(x, y, MINT, a * 0.85)


def star(cv, r, cy=CHEST, core=2.0):
    yc = FE - cy
    for d in range(-r, r + 1):
        c = MINT_W if abs(d) < r - 1 else MINT_P
        cv.put(CX + d, int(yc), c)
        cv.put(CX, int(yc) + d, c)
    for y in range(int(yc - core) - 1, int(yc + core) + 2):
        for x in range(CX - int(core) - 1, CX + int(core) + 2):
            if math.hypot(x + 0.5 - (CX + 0.5), y + 0.5 - (yc + 0.5)) <= core:
                cv.put(x, y, MINT_W)


def sparks(cv, r, n, rot=0.0, length=2, c=MINT_P, cy=CHEST, a=1.0):
    yc = FE - cy + 0.5
    for k in range(n):
        ang = math.radians(rot + k * 360.0 / n)
        for t in range(length):
            cv.put(int(CX + 0.5 + (r + t) * math.cos(ang)), int(yc + (r + t) * math.sin(ang)), c, a)


def motes(cv, seed, count, r_lo, r_hi, rise=0.0, a=1.0):
    """Single texels of lilac and violet round the chest, the same scatter for the same seed."""
    rnd = random.Random(seed)
    for _ in range(count):
        ang = rnd.uniform(0, math.tau)
        r = rnd.uniform(r_lo, r_hi)
        x = int(CX + r * math.cos(ang))
        y = int(FE - CHEST - rise + r * math.sin(ang) * 1.3)
        cv.put(x, y, rnd.choice((LILAC, VIO, MINT_P)), a)


def standing(kind, f):
    cv = Canvas(W, H)
    if kind == "out":
        if f <= 1:
            pass  # the ghost
        elif f == 2:
            column(cv, 8, 104)
            star(cv, 12)
        elif f == 3:
            star(cv, 9, core=3.0)
            sparks(cv, 12, 8, rot=22.5)
        elif f == 4:
            star(cv, 4, core=1.0)
            sparks(cv, 18, 8, rot=22.5, c=MINT)
            motes(cv, 7, 10, 8, 16, rise=4)
        else:
            sparks(cv, 23, 8, rot=22.5, length=1, c=VIO, a=0.8)
            motes(cv, 8, 8, 10, 20, rise=10, a=0.8)
    else:
        if f == 0:
            motes(cv, 3, 14, 18, 26)
            star(cv, 5, core=1.0)
        elif f == 1:
            column(cv, 8, 104)
            star(cv, 11)
        elif f == 2:
            sparks(cv, 20, 8, rot=22.5, length=3, c=MINT_P)  # the ghost flares inside them
        elif f == 3:
            sparks(cv, 26, 6, rot=-90, c=MINT_P, cy=CHEST + 18)
            motes(cv, 4, 8, 16, 24, rise=8)
        elif f == 4:
            motes(cv, 5, 10, 18, 26, rise=24, a=0.9)
        else:
            motes(cv, 6, 8, 20, 28, rise=36, a=0.7)
    return cv.image()


# ---- the floor ring ----------------------------------------------------------------------------------------------
def ring(cv, r, w, c, a=1.0, gaps=0, rot=0.0):
    c0 = FW / 2.0
    for y in range(FW):
        for x in range(FW):
            d = math.hypot(x + 0.5 - c0, y + 0.5 - c0)
            if r - w <= d <= r:
                if gaps:
                    ang = (math.degrees(math.atan2(y + 0.5 - c0, x + 0.5 - c0)) - rot) % (360.0 / gaps)
                    if ang > 360.0 / gaps * 0.55:
                        continue
                cv.put(x, y, c, a)


def floor(kind, f):
    cv = Canvas(FW, FW)
    if kind == "out":
        if f == 0:
            ring(cv, 22, 6, VIO, 0.5)
            ring(cv, 20, 3, MINT_P)
        elif f == 1:
            ring(cv, 25, 3, MINT)
            ring(cv, 22, 2, VIO, 0.6)
        elif f == 2:
            ring(cv, 28, 2, MINT)
        elif f == 3:
            ring(cv, 31, 2, MINT, 0.85, gaps=8, rot=10)
        elif f == 4:
            ring(cv, 33, 1.5, VIO, 0.7, gaps=8, rot=10)
        else:
            ring(cv, 35, 1.2, VIO_D, 0.5, gaps=8, rot=10)
    else:
        if f == 0:
            ring(cv, 34, 1.5, VIO, 0.7, gaps=8, rot=30)
        elif f == 1:
            ring(cv, 26, 2, MINT, 0.9)
        elif f == 2:
            ring(cv, 20, 20, MINT_P, 0.3)
            ring(cv, 21, 3, MINT_W)
        elif f == 3:
            ring(cv, 25, 3, MINT_P)
            ring(cv, 22, 3, VIO, 0.6)
        elif f == 4:
            ring(cv, 29, 2, MINT, 0.8, gaps=6, rot=0)
        else:
            ring(cv, 33, 1.5, VIO, 0.5, gaps=6, rot=0)
    return cv.image()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (W * FRAMES, H * 2), (0, 0, 0, 0))
    fl = Image.new("RGBA", (FW * FRAMES, FW * 2), (0, 0, 0, 0))
    for row, kind in enumerate(("out", "in")):
        for f in range(FRAMES):
            sheet.alpha_composite(standing(kind, f), (f * W, row * H))
            fl.alpha_composite(floor(kind, f), (f * FW, row * FW))
    sheet.save(OUT / "blink_sheet.png")
    fl.save(OUT / "blink_floor.png")
    print("wrote", OUT / "blink_sheet.png", "and", OUT / "blink_floor.png")
    if "--preview" in sys.argv:
        d = Path(sys.argv[sys.argv.index("--preview") + 1])
        for name, img in (("blink_sheet", sheet), ("blink_floor", fl)):
            bg = Image.new("RGBA", img.size, (30, 40, 80, 255))  # about the arena floor's blue
            bg.alpha_composite(img)
            bg.resize((img.width * 3, img.height * 3), Image.NEAREST).save(d / f"{name}_3x.png")


if __name__ == "__main__":
    main()
