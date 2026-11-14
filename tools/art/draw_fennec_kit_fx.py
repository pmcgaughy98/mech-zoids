"""Effect art for the fennec's kit in the 3D slice (Claude, 2026-11-04, game feel lane).
Take 2 (same day): lines thickened and a faint fill added under the rings and the boom, because thin lines on the
ground vanished from the reveal's low cameras; the sand drawn lighter and coarser so it reads on the dirt lane.
All at 50 texels a metre with a one-texel #141218 ink edge (the sel-out colour), in the fennec's own colours: the sound
pieces in its eye cyan, the sand in its ear tan. Each is drawn for the kit's placeholder length; the kit stretches the
plane to its export, so a changed length only rescales the texels.
- sound_ring_f0..f5: ear burst and the passive's pings. Two rings swelling out and fading, drawn as the 2:1 ground
  ellipse the 30-degree chase camera sees (as silverback_ring), radius 2.0 m at the last frame.
- charge_ring_f0: one ring, 2:1, radius 1.2 m: sonic boom's charge draws it in to the ears.
- burst_core.png: the ear burst's centre, where it hits harder: a pale disc, 2:1, radius 0.8 m.
- sand_cone_f0..f3: sand kick. Grains thrown across a cone, true shape (the kit turns the plane to the facing), apex at
  the centre, opening toward the top edge (the plane's -z); 3.5 m reach, 35 degrees either side.
- boom_wave_f0..f5: sonic boom. Arcs of sound racing out across a cone, true shape like the sand; 7 m, 40 degrees.
- tunnel_hole.png: a burrow mouth, 2:1, 0.8 m across the hole: dark hole, its far wall lit, a sand rim, a few clods.
Run: python tools/art/draw_fennec_kit_fx.py
"""
import math
import random
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parents[2] / "art" / "fx" / "moba3d"
INK = (20, 18, 24)
CYAN, CYAN_D, CYAN_P = (120, 232, 226), (52, 160, 170), (214, 252, 246)
SAND, SAND_D, SAND_DK = (244, 218, 158), (204, 160, 96), (130, 94, 56)
HOLE, HOLE_WALL = (36, 26, 24), (82, 58, 42)
TX = 50  # texels a metre


def put(px, size, x, y, c, a=255):
    w, h = size
    if 0 <= x < w and 0 <= y < h:
        px[x, y] = c + (a,)


def ink_edge(img, a):
    """A one-texel ink edge on every side of what is drawn, into empty texels only."""
    w, h = img.size
    px = img.load()
    drawn = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 0}
    for (x, y) in drawn:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in drawn and 0 <= q[0] < w and 0 <= q[1] < h and px[q][3] == 0:
                px[q] = INK + (a,)


def ellipse_ring(img, r, col, a, width=1):
    """A ring of radius r texels on the ground, squashed 2:1 for the camera, centred on the canvas."""
    px = img.load()
    w, h = img.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    steps = int(r * 8) + 64
    for i in range(steps):
        t = math.tau * i / steps
        for k in range(width):
            rr = r - k
            put(px, img.size, round(cx + rr * math.cos(t)), round(cy + rr * 0.5 * math.sin(t)), col, a)


def fill_ellipse(img, r, col, a):
    """A faint disc under a ring, 2:1 like it, so the ring reads as an area from low cameras."""
    px = img.load()
    w, h = img.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for y in range(h):
        for x in range(w):
            if math.hypot((x - cx) / r, (y - cy) / (r * 0.5)) <= 1.0 and px[x, y][3] == 0:
                px[x, y] = col + (a,)


def fill_wedge(img, r0, r1, half_deg, col, a):
    """A faint band of a cone between radii r0 and r1, opening toward the top edge."""
    px = img.load()
    w, h = img.size
    c = (w - 1) / 2.0
    half = math.radians(half_deg)
    for y in range(h):
        for x in range(w):
            dx, dy = x - c, c - y
            r = math.hypot(dx, dy)
            if r0 <= r <= r1 and abs(math.atan2(dx, dy)) <= half and px[x, y][3] == 0:
                px[x, y] = col + (a,)


def arc(img, r, half_deg, col, a, width=1):
    """An arc of radius r texels around the canvas centre, opening toward the top edge, half_deg either side."""
    px = img.load()
    w, h = img.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    half = math.radians(half_deg)
    steps = int(r * 2 * half * 2) + 16
    for i in range(steps + 1):
        t = -half + 2 * half * i / steps
        for k in range(width):
            rr = r - k
            put(px, img.size, round(cx + rr * math.sin(t)), round(cy - rr * math.cos(t)), col, a)


# Sound rings: 2.0 m at the last frame.
R = 2 * TX
for f in range(6):
    img = Image.new("RGBA", (2 * R + 4, R + 4), (0, 0, 0, 0))
    a = [255, 255, 255, 210, 150, 80][f]
    outer = R * (0.3 + 0.7 * f / 5)
    ellipse_ring(img, outer, CYAN_P, a, 2)
    ellipse_ring(img, outer - 2, CYAN, a, 3)
    if outer * 0.7 > 6:
        ellipse_ring(img, outer * 0.7, CYAN_D, int(a * 0.8), 2)
    ink_edge(img, int(a * 0.6))
    fill_ellipse(img, outer - 5, CYAN, int(a * 0.25))
    img.save(OUT / f"sound_ring_f{f}.png")

# The charge ring: one ring, 1.2 m.
RC = int(1.2 * TX)
img = Image.new("RGBA", (2 * RC + 4, RC + 4), (0, 0, 0, 0))
ellipse_ring(img, RC, CYAN_P, 255, 2)
ellipse_ring(img, RC - 2, CYAN, 255, 3)
ink_edge(img, 150)
img.save(OUT / "charge_ring_f0.png")

# The burst's centre: a pale disc, 0.8 m.
RK = int(0.8 * TX)
img = Image.new("RGBA", (2 * RK + 4, RK + 4), (0, 0, 0, 0))
px = img.load()
cx, cy = (img.width - 1) / 2.0, (img.height - 1) / 2.0
for y in range(img.height):
    for x in range(img.width):
        d = math.hypot((x - cx) / RK, (y - cy) / (RK * 0.5))
        if d <= 1.0:
            put(px, img.size, x, y, CYAN if d > 0.86 else CYAN_P, 230 if d > 0.86 else 140)
ink_edge(img, 160)
img.save(OUT / "burst_core.png")

# Sand cone: 3.5 m, 35 degrees either side.
RS = int(3.5 * TX)
rng = random.Random(7)
grains = []
for i in range(380):
    t = math.radians(35) * (rng.random() - rng.random())  # thicker down the middle
    d = 0.18 + 0.82 * math.sqrt(rng.random())
    grains.append((t, d, rng.random() < 0.35))
for f, (reach, a) in enumerate([(0.38, 255), (0.68, 255), (0.9, 215), (1.0, 120)]):
    img = Image.new("RGBA", (2 * RS + 4, 2 * RS + 4), (0, 0, 0, 0))
    px = img.load()
    c = (img.width - 1) / 2.0
    for (t, d, big) in grains:
        r = RS * d * reach
        x, y = round(c + r * math.sin(t)), round(c - r * math.cos(t))
        if big:  # a 3x3 clod: lit top-left, dark bottom-right
            for dx in range(3):
                for dy in range(3):
                    put(px, img.size, x + dx, y + dy, SAND if dx + dy < 2 else (SAND_D if dx + dy < 4 else SAND_DK), a)
        else:
            for dx in range(2):
                for dy in range(2):
                    put(px, img.size, x + dx, y + dy, SAND if dy == 0 else SAND_D, a)
        if f < 2:  # the throw: a short streak behind each grain, pointing back at the paw
            for k in (2, 4):
                rr = max(r - k, 0)
                put(px, img.size, round(c + rr * math.sin(t)), round(c - rr * math.cos(t)), SAND_D, int(a * 0.5))
    ink_edge(img, int(a * 0.5))
    img.save(OUT / f"sand_cone_f{f}.png")

# Sonic boom: 7 m, 40 degrees either side.
RB = 7 * TX
for f in range(6):
    img = Image.new("RGBA", (2 * RB + 4, 2 * RB + 4), (0, 0, 0, 0))
    fade = [1.0, 1.0, 1.0, 0.9, 0.65, 0.35][f]
    lead = RB * (0.2 + 0.8 * f / 5)
    for i, (col, w, a) in enumerate([(CYAN_P, 4, 255), (CYAN, 6, 230), (CYAN, 5, 190), (CYAN_D, 4, 150)]):
        r = lead - (0 if i < 2 else (i - 1) * 0.13 * RB) - (4 if i == 1 else 0)
        if r > 0.08 * RB:
            arc(img, r, 40, col, int(a * fade), w)
    ink_edge(img, int(170 * fade))
    fill_wedge(img, 0.08 * RB, lead - 10, 40, CYAN, int(60 * fade))
    img.save(OUT / f"boom_wave_f{f}.png")

# The burrow mouth.
RH = int(0.8 * TX / 2)  # the hole's radius in texels
pad = 8
img = Image.new("RGBA", (2 * (RH + pad) + 2, RH + pad + 2), (0, 0, 0, 0))
px = img.load()
cx, cy = (img.width - 1) / 2.0, (img.height - 1) / 2.0
for y in range(img.height):
    for x in range(img.width):
        d = math.hypot((x - cx) / RH, (y - cy) / (RH * 0.5))
        if d <= 1.0:
            put(px, img.size, x, y, HOLE_WALL if (y - cy) < -RH * 0.18 else HOLE)  # the far wall catches light
        elif d <= 1.0 + 5.0 / RH:
            put(px, img.size, x, y, SAND if (y - cy) < 0 else SAND_D)  # the rim, lit on the far side
rng = random.Random(3)
for i in range(9):
    t = math.tau * i / 9 + rng.random() * 0.4
    r = RH + 6 + rng.random() * 2
    x, y = round(cx + r * math.cos(t)), round(cy + r * 0.5 * math.sin(t))
    for dx, dy, col in ((0, 0, SAND), (1, 0, SAND), (0, 1, SAND_D), (1, 1, SAND_DK)):
        put(px, img.size, x + dx, y + dy, col)
ink_edge(img, 200)
img.save(OUT / "tunnel_hole.png")
print("wrote sound_ring x6, charge_ring, burst_core, sand_cone x4, boom_wave x6, tunnel_hole to", OUT)
