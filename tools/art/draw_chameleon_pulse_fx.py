"""Effect art for the chameleon's basic attack, the eye pulse (Claude, 2026-11-06, chameleon lane). Preston picked
"Eye pulse" on 2026-11-05, then "Draw the pulse".
Laid out like the fennec's dart (art/fx/moba3d/fennec_bolt/, played by scripts/moba3d/fennec_bolt.gd), so the same
kind of code can play it:
- pulse_sheet.png: 160 x 640 in 40-texel cells.
  - 16 rows, one per screen angle: k x 22.5 degrees, 0 pointing right, turning clockwise.
  - 4 columns: a 4-frame loop at 50 ms a frame.
  - The shot: a pale gold-white core in the lens's own colours, a turquoise halo, a two-dot tail.
- pulse_burst_sheet.png: 240 x 80 in 40-texel cells.
  - Row 0: the flare at the eye turret as it fires, 4 frames (40, 50, 60, 60 ms).
  - Row 1: the hit, 5 frames (30, 40, 50, 60, 70 ms): a ring bursting out with sparks.
At the chameleon's texel, 0.020 m (50 texels a metre), with a one-texel #141218 ink edge, in its own colours only.
Sizes are placeholders, not balance numbers.
Run: python tools/art/draw_chameleon_pulse_fx.py [--out DIR]
"""
import argparse
import math
from pathlib import Path

from PIL import Image

INK = (0x14, 0x12, 0x18)    # the sel-out ink every machine and effect uses
OUTER = (0x1F, 0xC8, 0xB4)  # the chameleon's turquoise
HALO = (0x9F, 0xF5, 0xE6)   # its pale turquoise
INNER = (0xFF, 0xF1, 0xA0)  # its lens glow
CORE = (0xFF, 0xFB, 0xE6)   # its brightest lens tone
CELL = 40
ANGLES = 16
FRAMES = 4


def put(px, x, y, c, box):
    x0, y0, x1, y1 = box
    if x0 <= x < x1 and y0 <= y < y1:
        px[x, y] = c + (255,)


def ink_edge(img, box):
    """A one-texel ink edge on the four sides of what is drawn, into empty texels only, kept inside the cell."""
    px = img.load()
    x0, y0, x1, y1 = box
    drawn = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[x, y][3] > 0}
    for x, y in drawn:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in drawn and x0 <= nx < x1 and y0 <= ny < y1 and px[nx, ny][3] == 0:
                px[nx, ny] = INK + (255,)


def shot(img, ox, oy, k, f):
    """One cell of the pulse: a teardrop pointing along screen angle k, rounder in front, longer behind."""
    th = math.radians(k * 360.0 / ANGLES)
    dx, dy = math.cos(th), math.sin(th)  # screen y runs down, so a rising k turns clockwise
    cx, cy = ox + CELL / 2, oy + CELL / 2
    grow = [1.0, 1.12, 1.0, 0.9][f]  # the halo breathes over the loop
    box = (ox, oy, ox + CELL, oy + CELL)
    px = img.load()
    layers = [(OUTER, 4.4 * grow, 6.2 * grow, 3.0 * grow), (HALO, 3.4 * grow, 4.6 * grow, 2.1 * grow),
              (INNER, 2.3, 3.0, 1.4), (CORE, 1.6, 2.0, 0.9)]
    for y in range(oy, oy + CELL):
        for x in range(ox, ox + CELL):
            rx, ry = x + 0.5 - cx, y + 0.5 - cy
            s = rx * dx + ry * dy   # along the flight
            t = -rx * dy + ry * dx  # across it
            for col, front, back, half in layers:
                a = front if s >= 0 else back
                if (s / a) ** 2 + (t / half) ** 2 <= 1.0:
                    px[x, y] = col + (255,)
    for col, back in ((HALO, 8 + f % 2), (OUTER, 11 + f % 2)):  # the tail steps back and forth a texel
        put(px, math.floor(cx - dx * back), math.floor(cy - dy * back), col, box)
    ink_edge(img, box)


def disc(px, cx, cy, r, col, box):
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r:
                px[x, y] = col + (255,)


def ring(px, cx, cy, r, w, col, box, gaps=0):
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if abs(d - r) <= w / 2:
                if gaps and int((math.atan2(y + 0.5 - cy, x + 0.5 - cx) + math.pi) / (2 * math.pi) * gaps * 2) % 2:
                    continue
                px[x, y] = col + (255,)


def sparks(px, cx, cy, r, n, col, box, turn=0.0):
    for i in range(n):
        a = turn + i * 2 * math.pi / n
        put(px, math.floor(cx + r * math.cos(a)), math.floor(cy + r * math.sin(a)), col, box)


def burst(img, col_i, row, f):
    ox, oy = col_i * CELL, row * CELL
    box = (ox, oy, ox + CELL, oy + CELL)
    cx, cy = ox + CELL / 2, oy + CELL / 2
    px = img.load()
    if row == 0:  # the flare at the eye turret
        if f == 0:
            disc(px, cx, cy, 1.6, HALO, box)
            disc(px, cx, cy, 0.8, CORE, box)
        elif f == 1:
            for i in range(8):
                a = i * math.pi / 4
                for d in range(1, 5 if i % 2 == 0 else 3):
                    put(px, math.floor(cx + d * math.cos(a)), math.floor(cy + d * math.sin(a)), HALO, box)
            disc(px, cx, cy, 2.0, INNER, box)
            disc(px, cx, cy, 1.0, CORE, box)
        elif f == 2:
            ring(px, cx, cy, 3.6, 1.2, HALO, box)
            disc(px, cx, cy, 1.2, INNER, box)
        else:
            sparks(px, cx, cy, 4.6, 4, OUTER, box, math.pi / 4)
            put(px, math.floor(cx), math.floor(cy), HALO, box)
    else:  # the hit
        if f == 0:
            disc(px, cx, cy, 4.8, HALO, box)
            disc(px, cx, cy, 3.2, INNER, box)
            disc(px, cx, cy, 1.8, CORE, box)
        elif f == 1:
            ring(px, cx, cy, 5.6, 1.6, HALO, box)
            disc(px, cx, cy, 2.2, INNER, box)
        elif f == 2:
            ring(px, cx, cy, 6.8, 1.6, OUTER, box)
            ring(px, cx, cy, 5.7, 1.0, HALO, box)
            sparks(px, cx, cy, 8.6, 6, INNER, box)
        elif f == 3:
            ring(px, cx, cy, 8.0, 1.2, OUTER, box, gaps=8)
            sparks(px, cx, cy, 9.4, 6, HALO, box, math.pi / 6)
        else:
            sparks(px, cx, cy, 9.8, 6, OUTER, box, math.pi / 6)
    ink_edge(img, box)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[2] / "art/fx/moba3d/chameleon_pulse"))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (FRAMES * CELL, ANGLES * CELL), (0, 0, 0, 0))
    for k in range(ANGLES):
        for f in range(FRAMES):
            shot(sheet, f * CELL, k * CELL, k, f)
    sheet.save(out / "pulse_sheet.png")
    bursts = Image.new("RGBA", (6 * CELL, 2 * CELL), (0, 0, 0, 0))
    for f in range(4):
        burst(bursts, f, 0, f)
    for f in range(5):
        burst(bursts, f, 1, f)
    bursts.save(out / "pulse_burst_sheet.png")
    print("wrote", out / "pulse_sheet.png", "and", out / "pulse_burst_sheet.png")


if __name__ == "__main__":
    main()
