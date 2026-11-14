"""The fennec's arrival shield (Claude, 2026-11-05, game feel lane, effects spin-off; Preston: "Arrival shield").

Drawn by this script, no generator and no paid tool, in the palette of the small gate, the bolt and the blink flash
(draw_fennec_gate.py). The great gate (slot 4) carries the team to its far gate; every ally that arrives gets a short
shield and a burst of speed. This is the shield: a shell of the gate's violet light round the ally, standing on the
floor like a bell, with a mint glint at its top left. It is drawn in texels and laid on at the wearer's own texel, so
it stays as crisp as the machine inside it. It is violet and smooth on purpose: the gorilla's hex shield is a green
sphere of hexagons, and the two must not read alike.
The speed burst is not drawn here: ArrivalShield leaves mint afterimages of the machine's own frame behind it.

Four rows, one per part:
  0 form    6 frames: sparks at its base, the shell rising up both sides from the floor (its inside filling as it
            rises), closing at the top with a star, a bright frame, settling.
  1 hold    8 frames, a loop: the shell, a band of light rising through it (frames 0-5), twinkles on the rim.
  2 expire  5 frames: it flickers, the rim breaks into dashes, the dashes drift up as motes.
  3 break   5 frames, when a hit takes it: it cracks along eight lines, the pieces fly out and fade to motes.

Two sizes, each in its own texels: "s" for the S and M machines (the fennec), "l" for the L machines (rhino, gorilla).
The machines measured 2026-11-05 over every frame of their sheets (texels above the feet, half width):
  fennec  up 64-83 (median 69), half width 21-43 (31)
  rhino   up 68-107 (84), half width 33-53 (43)
  gorilla up 83-90 (86), half width 41-50 (46)

arrival_shield_<size>.png   the shell: 8 columns x 4 rows of cells; the floor is the top edge of row FE, the middle
                            is column W / 2 (ArrivalShield stands it on the tilted quad, like the machines).
arrival_floor_<size>.png    the ring on the floor under it: the same rows and columns, FW x FW cells, centred.
Timings are in scripts/moba3d/arrival_shield.gd.

Run from the project root:  python tools/art/draw_fennec_arrival_shield.py [--preview <dir>]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_fennec_gate import LILAC, MINT_P, MINT_W, VIO, VIO_D, Canvas  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "art/fx/moba3d/arrival_shield"
COLS = 8
ROWS = {"form": 6, "hold": 8, "expire": 5, "break": 5}
# rx: half width; cy: the shell's middle above the floor; ry: half height (the top is cy + ry); all in texels
SIZES = {
    "s": dict(rx=48, cy=38, ry=55, W=128, H=128, FE=120, FW=96),
    "l": dict(rx=58, cy=46, ry=65, W=152, H=144, FE=136, FW=112),
}


class Shell:
    def __init__(self, rx, cy, ry, W, H, FE, FW):
        self.rx, self.cy, self.ry, self.W, self.H, self.FE, self.FW = rx, cy, ry, W, H, FE, FW
        self.cx = W / 2.0
        self.top = cy + ry
        self.base = rx * math.sqrt(max(0.0, 1.0 - (cy / ry) ** 2))  # half width where it meets the floor
        self.phi0 = math.atan2(-cy / ry, self.base / rx)  # the base, as an angle on the unit ellipse

    def texels(self):
        """Every texel inside the shell: (x, y, u, dx, dv, d), d = texels in from the edge."""
        for y in range(self.H):
            u = self.FE - (y + 0.5)
            if u < 0.0:
                continue
            for x in range(self.W):
                dx, dv = x + 0.5 - self.cx, u - self.cy
                q = math.hypot(dx / self.rx, dv / self.ry)
                if q > 1.0:
                    continue
                g = math.hypot(dx / self.rx ** 2, dv / self.ry ** 2) / max(q, 1e-6)
                d = (1.0 - q) / max(g, 1e-6) if q > 1e-6 else 99.0
                yield x, y, u, dx, dv, d

    def angle(self, dx, dv):
        return math.degrees(math.atan2(dv / self.ry, dx / self.rx))

    def progress(self, dx, dv):
        """0 at the floor, 1 at the top, up either side."""
        phi = math.atan2(dv / self.ry, abs(dx) / self.rx)
        return (phi - self.phi0) / (math.pi / 2 - self.phi0)


def glint(sh, dx, dv, d):
    a = sh.angle(dx, dv)
    if 112.0 <= a <= 150.0 and d < 3.5:
        return MINT_W if d < 1.5 else MINT_P
    if -38.0 <= a <= -24.0 and d < 2.0:
        return MINT_P
    return None


def shell_texel(sh, cv, x, y, dx, dv, d, rim=LILAC, fill=0.10, glow=(0.45, 0.15), alpha=1.0, glints=True):
    """The shell as it holds: a lilac edge, a violet line inside it, a violet glow fading inward, a faint fill."""
    g = glint(sh, dx, dv, d) if glints else None
    a = sh.angle(dx, dv)
    if g is not None:
        cv.put(x, y, g, alpha)
    elif d < 2.0:
        cv.put(x, y, rim, alpha)
    elif d < 3.0:
        cv.put(x, y, VIO, 0.9 * alpha)
    elif glints and 5.0 <= d < 6.0 and 118.0 <= a <= 142.0:
        cv.put(x, y, MINT_W, 0.65 * alpha)  # the bubble's window highlight, in from the glint
    elif d < 6.0:
        k = (d - 3.0) / 3.0
        cv.put(x, y, VIO, (glow[0] + (glow[1] - glow[0]) * k) * alpha)
    elif fill > 0.0:
        cv.put(x, y, VIO, fill * alpha)


def star(cv, cx, y, r, c=MINT_W):
    for k in range(-r, r + 1):
        col = c if abs(k) < r - 1 else MINT_P
        cv.put(int(cx + k), int(y), col)
        cv.put(int(cx), int(y + k), col)
    for ox, oy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        cv.put(int(cx + ox), int(y + oy), MINT_P)


def form(sh, f):
    cv = Canvas(sh.W, sh.H)
    frac = [0.0, 0.42, 0.76, 1.0, 1.0, 1.0][f]
    for x, y, u, dx, dv, d in sh.texels():
        if f == 0:
            if d < 2.0 and u < 7.0:
                cv.put(x, y, MINT_W if u < 4.0 else MINT_P)
        elif f in (1, 2):
            s = sh.progress(dx, dv)
            tip = sh.cy + sh.ry * math.sin(sh.phi0 + frac * (math.pi / 2 - sh.phi0))
            if d < 3.0 and s <= frac:
                cv.put(x, y, MINT_W if s > frac - 0.07 else (LILAC if d < 2.0 else VIO))
            elif d >= 3.0 and abs(u - tip) < 1.0:
                cv.put(x, y, LILAC, 0.55)
            elif d >= 3.0 and u < tip:
                cv.put(x, y, VIO, 0.10 + 0.12 * (1.0 - (tip - u) / max(1.0, tip)))
        elif f == 3:
            shell_texel(sh, cv, x, y, dx, dv, d, rim=MINT_W, fill=0.20, glow=(0.6, 0.25), glints=False)
        elif f == 4:
            shell_texel(sh, cv, x, y, dx, dv, d, rim=MINT_W, fill=0.22, glow=(0.6, 0.25))
        else:
            shell_texel(sh, cv, x, y, dx, dv, d, fill=0.15, glow=(0.5, 0.18))
    yt = sh.FE - sh.top - 0.5
    if f == 3:
        star(cv, sh.cx, yt, 7)
    elif f == 4:
        for k in range(6):
            a = math.radians(30 + k * 60)
            cv.put(int(sh.cx + 9 * math.cos(a)), int(yt - 9 * math.sin(a)), MINT_P)
    return cv.image()


def hold(sh, f):
    cv = Canvas(sh.W, sh.H)
    band = -4.0 + (sh.top + 8.0) * f / 5.0 if f <= 5 else None
    rnd = random.Random(100 + f)
    rims = []
    for x, y, u, dx, dv, d in sh.texels():
        if band is not None and abs(u - band) < 1.5:
            if d < 3.0:
                cv.put(x, y, MINT_W)
            elif d < 6.0:
                cv.put(x, y, LILAC, 0.55)
            else:
                cv.put(x, y, LILAC, 0.2)
            continue
        shell_texel(sh, cv, x, y, dx, dv, d)
        if d < 2.0 and glint(sh, dx, dv, d) is None:
            rims.append((x, y))
    for x, y in rnd.sample(rims, 3):
        cv.put(x, y, MINT_W)
    return cv.image()


def expire(sh, f):
    cv = Canvas(sh.W, sh.H)
    rnd = random.Random(200 + f)
    for x, y, u, dx, dv, d in sh.texels():
        if f == 0:
            if d < 2.0:
                cv.put(x, y, VIO, 0.6)
        elif f == 1:
            shell_texel(sh, cv, x, y, dx, dv, d, fill=0.06, glow=(0.3, 0.08), alpha=0.85)
        elif d < 2.0:
            dash = int(sh.progress(dx, dv) * 40) % 2 == 0
            if f == 2 and dash:
                cv.put(x, y, LILAC)
            elif f >= 3 and dash and rnd.random() < (0.35 if f == 3 else 0.18):
                rise = (3 if f == 3 else 8) + rnd.randint(0, 3)
                cv.put(x, y - rise, rnd.choice((LILAC, VIO, MINT_P)), 0.8 if f == 3 else 0.5)
    return cv.image()


def shards(sh):
    """Fixed points inside the shell; each texel belongs to the nearest, so the pieces are glass-like polygons."""
    rnd = random.Random(7)
    pts = []
    while len(pts) < 12:
        dx, dv = rnd.uniform(-sh.rx, sh.rx), rnd.uniform(-sh.cy, sh.ry)
        if math.hypot(dx / sh.rx, dv / sh.ry) < 0.92 and all(math.hypot(dx - a, dv - b) > 14 for a, b in pts):
            pts.append((dx, dv))
    return pts


def broken(sh, f):
    """Cracks across it, then the pieces fly out from its middle, drop a little and fade to motes."""
    cv = Canvas(sh.W, sh.H)
    rnd = random.Random(300 + f)
    pts = shards(sh)
    off = [0, 3, 7, 11, 14][f]
    drop = [0, 0, 1, 3, 6][f]
    for x, y, u, dx, dv, d in sh.texels():
        ds = sorted((math.hypot(dx - a, dv - b), k) for k, (a, b) in enumerate(pts))
        gap = ds[1][0] - ds[0][0]
        k = ds[0][1]
        if f == 0:
            if gap < 1.2:
                cv.put(x, y, MINT_W)
            else:
                shell_texel(sh, cv, x, y, dx, dv, d, rim=MINT_W, fill=0.25, glow=(0.6, 0.3))
            continue
        if gap < 1.6:
            continue  # the gaps between the pieces
        a, b = pts[k]
        n = max(1e-6, math.hypot(a, b - sh.cy * 0.3))
        px = x + round(off * a / n)
        py = y - round(off * (b - sh.cy * 0.3) / n) + drop
        if sh.FE - (py + 0.5) < 0.0:
            continue
        edge = gap < 3.0  # a piece's own broken edge, lit
        if f == 1:
            if edge:
                cv.put(px, py, LILAC, 0.7)
            else:
                shell_texel(sh, cv, px, py, dx, dv, d, fill=0.16, glow=(0.5, 0.2))
        elif f == 2:
            if edge or d < 2.0:
                cv.put(px, py, LILAC, 0.7)
            else:
                cv.put(px, py, VIO, 0.14)
        elif f == 3 and (edge or d < 2.0) and (x + y) % 2 == 0:
            cv.put(px, py, LILAC if d < 2.0 else VIO, 0.55)
        elif f == 4 and (edge or d < 2.0) and rnd.random() < 0.1:
            cv.put(px, py, rnd.choice((LILAC, VIO, MINT_P)), 0.45)
    return cv.image()


# ---- the floor ring ----------------------------------------------------------------------------------------------
def ring(cv, fw, r, w, c, a=1.0, gaps=0, rot=0.0):
    c0 = fw / 2.0
    for y in range(fw):
        for x in range(fw):
            dd = math.hypot(x + 0.5 - c0, y + 0.5 - c0)
            if r - w <= dd <= r:
                if gaps:
                    ang = (math.degrees(math.atan2(y + 0.5 - c0, x + 0.5 - c0)) - rot) % (360.0 / gaps)
                    if ang > 360.0 / gaps * 0.55:
                        continue
                cv.put(x, y, c, a)


def floor(sh, part, f):
    fw = sh.FW
    cv = Canvas(fw, fw)
    r0 = round(sh.base) + 1

    def steady(bright=False):
        ring(cv, fw, r0, 1, MINT_P if bright else LILAC, 0.9)
        ring(cv, fw, r0 - 1, 1, VIO, 0.6)

    if part == "form":
        if f == 0:
            ring(cv, fw, r0 + 6, 3, MINT_W)
        elif f == 1:
            ring(cv, fw, r0 + 3, 2, MINT_P)
        elif f == 2:
            ring(cv, fw, r0, 2, LILAC)
            ring(cv, fw, r0 - 2, 2, VIO, 0.6)
        else:
            steady(f == 3)
    elif part == "hold":
        steady(f == 0)
    elif part == "expire":
        if f == 0:
            ring(cv, fw, r0, 2, VIO, 0.5)
        elif f == 1:
            steady()
        elif f == 2:
            ring(cv, fw, r0, 1, LILAC, 0.8, gaps=10, rot=9)
        elif f == 3:
            ring(cv, fw, r0 + 1, 1, VIO_D, 0.5, gaps=10, rot=9)
    else:
        if f == 0:
            ring(cv, fw, r0, 2, MINT_W)
        elif f < 4:
            ring(cv, fw, r0 + 4 * f - 1, 1 if f == 3 else 2, (LILAC, VIO, VIO_D)[f - 1], (0.9, 0.7, 0.5)[f - 1],
                 gaps=8, rot=22.5)
    return cv.image()


DRAW = {"form": form, "hold": hold, "expire": expire, "break": broken}


def sheets(size):
    sh = Shell(**SIZES[size])
    shell = Image.new("RGBA", (sh.W * COLS, sh.H * len(ROWS)), (0, 0, 0, 0))
    fl = Image.new("RGBA", (sh.FW * COLS, sh.FW * len(ROWS)), (0, 0, 0, 0))
    for row, (part, count) in enumerate(ROWS.items()):
        for f in range(count):
            shell.alpha_composite(DRAW[part](sh, f), (f * sh.W, row * sh.H))
            fl.alpha_composite(floor(sh, part, f), (f * sh.FW, row * sh.FW))
    return sh, shell, fl


def fit_preview(sh, shell, machine_sheet, d, name):
    """The hold frame round the machine's widest and tallest frames, on the arena floor's blue, at 3x."""
    src = Image.open(machine_sheet).convert("RGBA")
    a = src.split()[3]
    cells = []
    for y in range(0, src.height - 191, 192):
        for x in range(0, src.width - 191, 192):
            bb = a.crop((x, y, x + 192, y + 192)).point(lambda v: 255 if v > 40 else 0).getbbox()
            if bb:
                cells.append((max(96 - bb[0], bb[2] - 96), 161 - bb[1], (x, y)))
    picks = [max(cells)[2], max(cells, key=lambda c: c[1])[2], sorted(cells)[len(cells) // 2][2]]
    hold0 = shell.crop((0, sh.H, sh.W, 2 * sh.H))
    hold3 = shell.crop((3 * sh.W, sh.H, 4 * sh.W, 2 * sh.H))
    out = Image.new("RGBA", (sh.W * len(picks) * 2, sh.H), (30, 40, 80, 255))
    for i, (cx, cy) in enumerate(picks):
        for j, frame in enumerate((hold0, hold3)):
            cell = Image.new("RGBA", (sh.W, sh.H), (0, 0, 0, 0))
            body = src.crop((cx, cy, cx + 192, cy + 192))
            cell.alpha_composite(body, (round(sh.W / 2 - 96), sh.FE - 161))
            cell.alpha_composite(frame)
            out.alpha_composite(cell, ((i * 2 + j) * sh.W, 0))
    out.resize((out.width * 3, out.height * 3), Image.NEAREST).save(d / f"fit_{name}_3x.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = {}
    for size in SIZES:
        sh, shell, fl = sheets(size)
        shell.save(OUT / f"arrival_shield_{size}.png")
        fl.save(OUT / f"arrival_floor_{size}.png")
        made[size] = (sh, shell, fl)
        print("wrote", OUT / f"arrival_shield_{size}.png", "and the floor ring;", "base half width", round(sh.base, 1))
    if "--preview" in sys.argv:
        d = Path(sys.argv[sys.argv.index("--preview") + 1])
        d.mkdir(parents=True, exist_ok=True)
        art = Path(__file__).resolve().parents[2] / "art/machines"
        for size, (sh, shell, fl) in made.items():
            for name, img in ((f"arrival_shield_{size}", shell), (f"arrival_floor_{size}", fl)):
                bg = Image.new("RGBA", img.size, (30, 40, 80, 255))  # about the arena floor's blue
                bg.alpha_composite(img)
                bg.resize((img.width * 3, img.height * 3), Image.NEAREST).save(d / f"{name}_3x.png")
        fit_preview(made["s"][0], made["s"][1], art / "fennec/fennec_sheet.png", d, "fennec")
        fit_preview(made["l"][0], made["l"][1], art / "rhino/rhino_sheet.png", d, "rhino")
        fit_preview(made["l"][0], made["l"][1], art / "ape/ape_sheet.png", d, "gorilla")


if __name__ == "__main__":
    main()
