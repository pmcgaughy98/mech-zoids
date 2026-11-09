"""Tech themes for the MOBA arena's tiles and props. Map design lane, 2026-11-04.

Preston asked for a "cyber futuristic technology" look (2026-11-04). This draws three takes on it, all ours, seeded:
  python tools/map/make_theme_tiles.py
  circuit   clean daylight tech: light steel plates, cyan traces
  neon      night: dark plates, a glowing grid, violet and cyan light
  foundry   industrial dusk: diamond plate, corrugated walls, rust, amber light
The palette grows out of the approved minion drone (steel greys, team glows), so the world sits with the machines.

Each theme writes art/field/moba3d/arena/<theme>/ with the same tile names the nature tiles use, so the arena swaps a
folder and nothing else: jungle (outer floor), lane_grass (floor inside the lane walls), dirt (the lane road), paving
(plaza and bases), cliff (wall faces), grass_top (wall tops), pit_floor. 32 x 32, wrapping, 50 texels per metre.
Glow is carried in alpha: a pixel's glow is 1 - alpha, and the shaders turn it into light. Props (not tiles):
skyline_a and skyline_b stand past the cliffs where the nature theme has trees, cap sits on rock and cliff tops where
it has bushes, stud is a floor light where it has tufts.
"""
import os
import random

from PIL import Image

N = 32
ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "art", "field", "moba3d", "arena")


def hexc(s, a=255):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5)) + (a,)


STEEL = [hexc(c) for c in ("#141218", "#211e27", "#3d3a44", "#5c6170", "#8a8f9c", "#b8bcc6", "#d8dce4", "#f6fdff")]
GLOW = 110  # alpha for a glowing pixel: glow 0.57

THEMES = {
    "circuit": {"floor": (3, 2, 4), "lane": (5, 4, 6), "road": (2, 1, 3), "pave": (5, 4, 6), "wall": (4, 3, 5),
                "top": (3, 2, 4), "pit": (2, 1, 3), "glow": "#5fd8ff", "glow2": "#9ad0ff", "traces": 2, "grid": False,
                "rust": None},
    "neon": {"floor": (1, 0, 2), "lane": (2, 1, 3), "road": (0, 0, 1), "pave": (3, 2, 4), "wall": (2, 1, 3),
             "top": (1, 0, 2), "pit": (0, 0, 1), "glow": "#9a6aff", "glow2": "#5fd8ff", "traces": 1, "grid": True,
             "rust": None},
    "foundry": {"floor": (2, 1, 3), "lane": (5, 4, 6), "road": (1, 0, 2), "pave": (4, 3, 5), "wall": (3, 2, 4),
                "top": (2, 1, 3), "pit": (1, 0, 2), "glow": "#ffb030", "glow2": "#ffd890", "traces": 0, "grid": False,
                "rust": [hexc("#6a3a24"), hexc("#8a4a2a")]},
}


def put(img, x, y, c):
    img.putpixel((x % img.width, y % img.height), c)


def glow(c):
    return c[:3] + (GLOW,)


def plates(rng, mid, dark, light, step=32, speck=0.08):
    """Square plates `step` px across, 1 px seam on the bottom and right, lit along the top and left."""
    img = Image.new("RGBA", (N, N), mid)
    for y in range(N):
        for x in range(N):
            if x % step == step - 1 or y % step == step - 1:
                img.putpixel((x, y), dark)
            elif x % step == 0 or y % step == 0:
                img.putpixel((x, y), light)
            elif rng.random() < speck:
                img.putpixel((x, y), dark if rng.random() < 0.5 else light)
    return img


def rivets(img, step, c_hi, c_lo):
    for oy in range(0, N, step):
        for ox in range(0, N, step):
            for dx, dy in ((2, 2), (step - 4, 2), (2, step - 4), (step - 4, step - 4)):
                put(img, ox + dx, oy + dy, c_hi)
                put(img, ox + dx + 1, oy + dy + 1, c_lo)


def traces(img, rng, count, col):
    """Circuit traces: a run from a plate edge that turns once and ends in a pad."""
    for _ in range(count):
        x, y = rng.randrange(3, N - 3), rng.randrange(3, N - 3)
        dx, dy = rng.choice([(1, 0), (0, 1)])
        for k in range(rng.randint(5, 10)):
            put(img, x + dx * k, y + dy * k, glow(col))
        ex, ey = x + dx * 10, y + dy * 10
        for k in range(rng.randint(3, 7)):
            put(img, ex + dy * k, ey + dx * k, glow(col))
        put(img, x - dx, y - dy, glow(col))
        put(img, x - dx + dy, y - dy + dx, glow(col))


def grid(img, col, every=32):
    for i in range(N):
        for j in range(0, N, every):
            put(img, i, j, glow(col))
            put(img, j, i, glow(col))


def rust(img, rng, pal, count):
    for _ in range(count):
        x, y = rng.randrange(N), rng.randrange(N)
        for k in range(rng.randint(3, 8)):
            put(img, x + rng.randint(-1, 1), y + k, pal[rng.randrange(2)])


def diamond(img, lo, hi):
    """Diamond-plate bumps every 4 px, offset each row."""
    for y in range(0, N, 4):
        for x in range((y // 4 % 2) * 2, N, 4):
            put(img, x, y, hi)
            put(img, x + 1, y + 1, lo)


def tiles(name, t, rng):
    g, g2 = hexc(t["glow"]), hexc(t["glow2"])
    out = {}
    m, d, l = (STEEL[i] for i in t["floor"])
    out["jungle"] = plates(rng, m, d, l, 32, 0.1)
    if t["grid"]:
        grid(out["jungle"], g)
    if name == "foundry":
        diamond(out["jungle"], d, l)
        rust(out["jungle"], rng, t["rust"], 3)
    traces(out["jungle"], rng, t["traces"], g)
    m, d, l = (STEEL[i] for i in t["lane"])
    out["lane_grass"] = plates(rng, m, d, l, 16, 0.05)
    if t["grid"]:
        grid(out["lane_grass"], g2)
    traces(out["lane_grass"], rng, t["traces"], g2)
    m, d, l = (STEEL[i] for i in t["road"])
    road = Image.new("RGBA", (N, N), m)
    for y in range(N):
        for x in range(N):
            r = rng.random()
            if r < 0.12:
                road.putpixel((x, y), d)
            elif r < 0.2:
                road.putpixel((x, y), l)
    out["dirt"] = road
    m, d, l = (STEEL[i] for i in t["pave"])
    out["paving"] = plates(rng, m, d, l, 16, 0.04)
    rivets(out["paving"], 16, l, d)
    if name == "neon":
        for k in (7, 23):
            put(out["paving"], k, k, glow(g))
    m, d, l = (STEEL[i] for i in t["wall"])
    wall = Image.new("RGBA", (N, N), m)
    for y in range(N):
        for x in range(N):
            c = m
            if name == "foundry":
                c = (l if x % 4 in (0, 1) else m) if x % 4 != 3 else d  # corrugated ribs
            if y % 16 == 15:
                c = d
            elif y % 16 == 0:
                c = l
            wall.putpixel((x, y), c)
    if name == "circuit":
        for x in range(N):
            put(wall, x, 8, glow(g))  # a lit seam across each plate
        rivets(wall, 16, l, d)
    elif name == "neon":
        for y in range(3, 13):
            for x in (6, 7, 22, 23):
                put(wall, x, y + (16 if x > 16 else 0), glow(g))  # vent slits
    else:
        rust(wall, rng, t["rust"], 4)
    out["cliff"] = wall
    m, d, l = (STEEL[i] for i in t["top"])
    out["grass_top"] = plates(rng, m, d, l, 16, 0.05)
    m, d, l = (STEEL[i] for i in t["pit"])
    pit = Image.new("RGBA", (N, N), m)
    for y in range(N):
        for x in range(N):
            if (x + y) % 8 in (0, 1) or (x - y) % 8 in (0, 1):
                pit.putpixel((x, y), l if name != "foundry" else glow(g))  # grate bars; foundry glows from below
            elif rng.random() < 0.05:
                pit.putpixel((x, y), d)
    out["pit_floor"] = pit
    return out


def skyline_a(name, t, rng):
    """A tall mast or stack, 60 x 240 px (1.2 x 4.8 m), windows lit in the theme's glow."""
    w, h = 60, 240
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    body, edge, lit = STEEL[2] if name != "circuit" else STEEL[5], STEEL[1] if name != "circuit" else STEEL[3], hexc(t["glow2"])
    top = 30
    for y in range(top, h):
        half = 14 if name != "foundry" else 12 + (y - top) // 40
        for x in range(w // 2 - half, w // 2 + half):
            c = edge if x in (w // 2 - half, w // 2 + half - 1) else body
            if name == "foundry" and (y // 14) % 4 == 0:
                c = hexc("#f0c020") if (x + y) % 8 < 4 else STEEL[1]  # hazard bands on the stack
            elif name != "foundry" and y % 10 in (3, 4) and (x - (w // 2 - half)) % 6 in (2, 3) and rng.random() < 0.7:
                c = lit
            img.putpixel((x, y), c)
    for y in range(0, top):  # antenna and its light
        img.putpixel((w // 2, y), edge)
    for dy in range(3):
        for dx in range(-1, 2):
            img.putpixel((w // 2 + dx, dy), hexc("#ff4a3a") if name != "circuit" else lit)
    return img


def skyline_b(name, t, rng):
    """A wide block, 140 x 180 px (2.8 x 3.6 m), rows of lit windows."""
    w, h = 140, 180
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    body = STEEL[1] if name == "neon" else (STEEL[5] if name == "circuit" else STEEL[3])
    edge = STEEL[0] if name == "neon" else STEEL[2]
    lit = hexc(t["glow"])
    roof = rng.randint(20, 40)
    for y in range(roof, h):
        for x in range(4, w - 4):
            c = edge if x in (4, w - 5) or y == roof else body
            if y > roof + 6 and (y - roof) % 14 in (5, 6, 7) and (x % 10) in (3, 4, 5, 6) and rng.random() < 0.6:
                c = lit
            img.putpixel((x, y), c)
    for x in range(20, 50):  # a rooftop unit
        for y in range(roof - 10, roof):
            img.putpixel((x, y), edge)
    return img


def cap(name, t, rng):
    """A small console on rock and cliff tops, 40 x 28 px (0.8 x 0.56 m), with one light."""
    w, h = 40, 28
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(10, h):
        for x in range(6, w - 6):
            img.putpixel((x, y), STEEL[1] if x in (6, w - 7) or y == 10 else STEEL[3])
    for y in range(2, 10):
        img.putpixel((w // 2, y), STEEL[2])
    for dx in range(-2, 3):
        for dy in range(-1, 2):
            img.putpixel((w // 2 + dx, 2 + dy), hexc(t["glow"]))
    for x in range(10, w - 10, 4):
        img.putpixel((x, 18), hexc(t["glow2"]))
    return img


def banner(name, t, rng):
    """A hanging team sign, 40 x 72 px (0.8 x 1.44 m): a hanger bar, a panel with three chevrons pointing at the floor,
    a striped foot. Greys only; the shader tints it the team's colour."""
    w, h = 40, 72
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for x in range(2, w - 2):
        for y in range(4):
            img.putpixel((x, y), STEEL[4] if y == 0 else STEEL[2])
    for y in range(4, h - 6):
        for x in range(5, w - 5):
            img.putpixel((x, y), STEEL[1] if x in (5, w - 6) or y in (4, h - 7) else STEEL[6])
    for k in range(3):
        top = 12 + k * 16
        for i in range(10):
            for d in range(3):
                for x in (w // 2 - 10 + i, w // 2 + 9 - i):
                    img.putpixel((x, top + i + d), STEEL[2])
    for y in range(h - 6, h):
        for x in range(5, w - 5):
            img.putpixel((x, y), STEEL[1] if (x + y) % 8 < 4 else STEEL[5])
    return img


def stud(name, t, rng):
    """A floor light, 8 x 6 px (0.16 x 0.12 m)."""
    img = Image.new("RGBA", (8, 6), (0, 0, 0, 0))
    for y in range(2, 6):
        for x in range(1, 7):
            img.putpixel((x, y), STEEL[2])
    for x in range(2, 6):
        img.putpixel((x, 1), hexc(t["glow"]))
        img.putpixel((x, 2), hexc(t["glow2"]))
    return img


# ---- Foundry quality pass, 2026-11-04 (Preston: "making map look higher quality") ----
# The foundry floor and wall tiles go from 32 px (a 0.64 m repeat, which read as graph paper from the chase camera)
# to 128 px (2.56 m) with plates of mixed sizes, tread, stains, rust and scuffs; the wall ribs go from every 4 px to
# every 8 px, which also stops them shimmering at a distance. Adds the posts' lamp tile and the floor marks atlas.
S = 128
FONT = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
        "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
        "4": ["101", "101", "111", "001", "001"], "7": ["111", "001", "010", "010", "010"]}


def mixc(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (a[3],)


def split(rng, x, y, w, h, minp, out):
    can_w, can_h = w >= 2 * minp, h >= 2 * minp
    if (can_w or can_h) and (max(w, h) > 64 or rng.random() < 0.55):
        if can_w and (w >= h or not can_h):
            k = rng.randrange(minp, w - minp + 1, 16)
            split(rng, x, y, k, h, minp, out)
            split(rng, x + k, y, w - k, h, minp, out)
        else:
            k = rng.randrange(minp, h - minp + 1, 16)
            split(rng, x, y, w, k, minp, out)
            split(rng, x, y + k, w, h - k, minp, out)
    else:
        out.append((x, y, w, h))


def blob(img, rng, cx, cy, r, cols, density=1.0):
    for y in range(int(cy - r - 3), int(cy + r + 4)):
        for x in range(int(cx - r - 3), int(cx + r + 4)):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / (r * (0.8 + 0.4 * rng.random()))
            if d < 1 and rng.random() < (1 - d) * 1.6 * density:
                put(img, x, y, rng.choice(cols))


def stain(img, rng, x0, y0, r, core, edge, sheen=()):
    """A floor stain in a 32 px cell: a solid core, a two-colour middle and a checker-dithered rim, so at range it
    averages into the floor instead of reading as a black speck. sheen: two short arcs of oily colour."""
    import math
    c0 = 15.5
    for y in range(32):
        for x in range(32):
            d = ((x - c0) ** 2 + (y - c0) ** 2) ** 0.5 / (r * (0.85 + 0.3 * rng.random()))
            if d >= 1:
                continue
            if d < 0.35:
                c = core
            elif d < 0.7:
                c = core if (x + y) % 2 else edge
            elif (x + y) % 2 == 0:
                c = edge
            else:
                continue
            img.putpixel((x0 + x, y0 + y), c)
    for k, c in enumerate(sheen):
        for i in range(6):
            th = math.radians(200 + k * 170 + i * 11)
            img.putpixel((x0 + int(c0 + 0.5 * r * math.cos(th)), y0 + int(c0 + 0.42 * r * math.sin(th))), c)


def deck(rng, base, dark, light, minp=32, tread=0.3, speck=0.03, stains=0, scuffs=6, rust_pal=None, rust_n=0,
         shade=0.14):
    img = Image.new("RGBA", (S, S), base)
    plates = []
    split(rng, 0, 0, S, S, minp, plates)
    for (x0, y0, w, h) in plates:
        s = rng.choice([-1, 0, 0, 1])
        pm = mixc(base, dark if s < 0 else light, shade) if s else base
        treaded = rng.random() < tread
        for ly in range(h):
            for lx in range(w):
                c = pm
                off = (ly // 4 % 2) * 2
                if lx == w - 1 or ly == h - 1:
                    c = dark
                elif lx == 0 or ly == 0:
                    c = mixc(pm, light, 0.55)
                elif treaded and ly % 4 == 1 and (lx - 1 - off) % 4 == 0:
                    c = mixc(pm, light, 0.45)
                elif treaded and ly % 4 == 2 and (lx - 2 - off) % 4 == 0:
                    c = mixc(pm, dark, 0.45)
                elif rng.random() < speck:
                    c = mixc(pm, dark if rng.random() < 0.6 else light, 0.3)
                img.putpixel((x0 + lx, y0 + ly), c)
        if min(w, h) >= 32:
            for bx, by in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)):
                put(img, x0 + bx, y0 + by, mixc(light, (255, 255, 255, 255), 0.2))
                put(img, x0 + bx + 1, y0 + by + 1, dark)
    for _ in range(scuffs):
        x, y = rng.randrange(S), rng.randrange(S)
        dx, dy = rng.choice([(1, 0), (0, 1), (1, 1)])
        for k in range(rng.randint(3, 8)):
            if rng.random() < 0.8:
                px, py = (x + dx * k) % S, (y + dy * k) % S
                img.putpixel((px, py), mixc(img.getpixel((px, py)), light, 0.35))
    for _ in range(stains):
        # grease, a step or so under the plate (2026-11-05: near-black, it read as specks every 2.56 m)
        blob(img, rng, rng.randrange(S), rng.randrange(S), rng.uniform(4, 9), [mixc(dark, STEEL[1], 0.4), mixc(dark, STEEL[2], 0.3)], 0.8)
    for _ in range(rust_n):
        blob(img, rng, rng.randrange(S), rng.randrange(S), rng.uniform(2.5, 5), rust_pal, 0.9)
    return img


def grit(rng):
    m, d, l = STEEL[1], STEEL[0], STEEL[2]
    img = Image.new("RGBA", (S, S), m)
    for y in range(S):
        for x in range(S):
            r = rng.random()
            if r < 0.11:
                img.putpixel((x, y), d)
            elif r < 0.17:
                img.putpixel((x, y), l)
            elif r < 0.175:
                img.putpixel((x, y), STEEL[3])
    for _ in range(5):
        blob(img, rng, rng.randrange(S), rng.randrange(S), rng.uniform(6, 12), [mixc(m, l, 0.35)], 0.5)
    for _ in range(4):  # hairline cracks
        x, y = rng.randrange(S), rng.randrange(S)
        for _k in range(rng.randint(6, 14)):
            put(img, x, y, d)
            x += rng.choice((1, 1, 0))
            y += rng.choice((1, 0, -1))
    return img


def corrugated(rng, m, d, l, rp):
    img = Image.new("RGBA", (S, S), m)
    shades = {}
    for y in range(S):
        for x in range(S):
            key = (x // 64, y // 64)
            if key not in shades:
                shades[key] = rng.choice([-0.12, 0.0, 0.0, 0.1])
            t = shades[key]
            pm = mixc(m, l if t > 0 else d, abs(t))
            r = x % 8
            c = mixc(pm, l, 0.45) if r in (0, 1) else (mixc(pm, d, 0.45) if r == 6 else (d if r == 7 else pm))
            ys = y % 64
            if ys == 0:
                c = mixc(pm, l, 0.7)
            elif ys in (59, 60, 61):
                c = mixc(pm, l, 0.2)  # a flat strap along the bottom of each panel
            elif ys == 62:
                c = mixc(pm, d, 0.3)
            elif ys == 63:
                c = d
            if x % 64 == 63:
                c = d
            img.putpixel((x, y), c)
    for sy in range(0, S, 64):
        for sx in range(4, S, 16):
            put(img, sx, sy + 60, mixc(l, (255, 255, 255, 255), 0.3))
            put(img, sx + 1, sy + 61, d)
            if rng.random() < 0.4:  # rust running down from the rivet
                for k in range(rng.randint(3, 11)):
                    put(img, sx + (1 if rng.random() < 0.2 else 0), sy + 64 + k, rp[k % 2])
    for y in range(14, 46, 4):  # a louvred vent in one panel of the four
        for x in range(76, 116):
            put(img, x, y, d)
            put(img, x, y + 1, mixc(d, m, 0.3))
            put(img, x, y + 2, mixc(m, l, 0.5))
    for _ in range(6):
        blob(img, rng, rng.randrange(S), rng.randrange(S), rng.uniform(1.5, 3), rp, 0.8)
    return img


def lamp_tile():
    img = Image.new("RGBA", (8, 8), glow(hexc("#ffb030")))
    for y in range(2, 6):
        for x in range(2, 6):
            img.putpixel((x, y), glow(hexc("#ffe0a0")))
    return img


def decal_atlas(rng, rp):
    """Floor marks, 256 x 128; the rects are DECALS in arena_blockout.gd. Paint is worn (pixels missing)."""
    img = Image.new("RGBA", (256, 128), (0, 0, 0, 0))
    paint, amber, ink = STEEL[6], hexc("#f0bf21"), STEEL[1]

    def dot(x, y, c, keep=0.85):
        if rng.random() < keep:
            img.putpixel((x, y), c)

    for y in range(1, 31):  # arrow: two chevrons, 52 x 32 at (0, 0)
        for x in range(1, 51):
            for ox in (6, 26):
                dd = (x - ox) - (11.5 - abs(y - 15.5))
                if 0 <= dd < 6 and abs(y - 15.5) <= 12:
                    dot(x, y, paint, 0.8)
    for v in (0, 16):  # hazard bands, 64 x 16, two wear patterns
        for y in range(16):
            for x in range(64):
                dot(64 + x, v + y, amber if ((x + y) // 6) % 2 == 0 else ink, 0.9)
    scrap = Image.new("RGBA", img.size)  # the old oil and soot draw here, so the seed runs on as before
    blob(scrap, rng, 144, 16, 10, [STEEL[0], mixc(STEEL[0], STEEL[1], 0.5)], 0.7)  # oil
    for gx, gy in ((141, 13), (146, 15), (143, 19)):
        img.putpixel((gx, gy), STEEL[3])
    for y in range(4, 28):  # drain
        for x in range(4, 28):
            edge = x in (4, 5, 26, 27) or y in (4, 5, 26, 27)
            slot = (y - 7) % 3 == 0 and 7 <= y <= 24 and 8 <= x <= 23
            img.putpixel((160 + x, y), STEEL[2] if edge else (STEEL[3] if slot else STEEL[0]))
    for bx, by in ((5, 5), (26, 5), (5, 26), (26, 26)):
        img.putpixel((160 + bx, by), STEEL[5])
    for y in range(4, 28):  # a bolted repair patch
        for x in range(4, 28):
            c = STEEL[3]
            if x == 4 or y == 4:
                c = STEEL[4]
            elif x == 27 or y == 27:
                c = STEEL[1]
            elif rng.random() < 0.04:
                c = STEEL[2]
            img.putpixel((192 + x, y), c)
    for bx, by in ((7, 7), (24, 7), (7, 24), (24, 24)):
        img.putpixel((192 + bx, by), STEEL[5])
        img.putpixel((193 + bx, by + 1), STEEL[1])
    blob(img, rng, 192 + 22, 21, 2.5, rp, 0.9)
    for y in range(32):  # scorch: a ring of soot
        for x in range(32):
            d = ((x - 15.5) ** 2 + (y - 15.5) ** 2) ** 0.5 / (13 * (0.85 + 0.3 * rng.random()))
            p = max(0.0, 1 - abs(d - 0.55) / 0.45) * 0.65 if d < 1 else 0.0
            if d < 0.25:
                p = 0.3
            if rng.random() < p:
                scrap.putpixel((224 + x, y), STEEL[0] if rng.random() < 0.6 else STEEL[1])
    srng = random.Random(9177)  # 2026-11-05: oil and scorch as dithered stains; they read as black specks
    stain(img, srng, 128, 0, 10, mixc(STEEL[1], STEEL[2], 0.35), STEEL[2], (hexc("#5d6f9e"), hexc("#7d6290")))
    stain(img, srng, 224, 0, 12, mixc(STEEL[1], hexc("#3b2b24"), 0.5), mixc(STEEL[2], hexc("#4a3a30"), 0.4))
    for cx, cy, txt in ((0, 32, "07"), (32, 32, "12"), (0, 48, "21"), (32, 48, "34")):  # bay numbers
        for gi, ch in enumerate(txt):
            for ry in range(5):
                for rx in range(3):
                    if FONT[ch][ry][rx] == "1":
                        for sy in range(2):
                            for sx in range(2):
                                dot(cx + 9 + gi * 8 + rx * 2 + sx, cy + 3 + ry * 2 + sy, paint, 0.88)
    for y in range(2, 14):  # floor vent, lit from below
        for x in range(2, 30):
            edge = x in (2, 29) or y in (2, 13)
            if edge:
                c = STEEL[2]
            elif y in (5, 8, 11) and 4 <= x <= 27:
                c = glow(hexc("#ffb030"))
            else:
                c = STEEL[0]
            img.putpixel((64 + x, 32 + y), c)
    return img


def armor(rng, rp):
    """Tower and core armour, 128 px: staggered plates with bevelled edges, worn paint along them, rivets, scratches,
    a stencilled chevron pair, a vent and two rust drips. Reads as a machine, apart from the corrugated walls."""
    m, d, l = STEEL[3], STEEL[1], STEEL[4]
    img = Image.new("RGBA", (S, S), m)
    for row in range(4):
        y0 = row * 32
        off = 32 if row % 2 else 0
        for col in range(2):
            x0 = col * 64 + off
            s = rng.choice([-1, 0, 0, 1])
            pm = mixc(m, d if s < 0 else l, 0.12) if s else m
            for ly in range(32):
                for lx in range(64):
                    c = pm
                    if ly == 31 or lx == 63:
                        c = d
                    elif ly == 30 or lx == 62:
                        c = mixc(pm, d, 0.4)
                    elif ly == 0 or lx == 0:
                        c = mixc(pm, STEEL[5], 0.55)
                    elif ly == 1 or lx == 1:
                        c = mixc(pm, l, 0.25)
                    elif min(lx, ly, 63 - lx, 31 - ly) <= 3 and rng.random() < 0.12:
                        c = mixc(pm, STEEL[5], 0.5)
                    elif rng.random() < 0.02:
                        c = mixc(pm, d, 0.3)
                    put(img, x0 + lx, y0 + ly, c)
            for bx, by in ((4, 4), (58, 4), (4, 26), (58, 26)):
                put(img, x0 + bx, y0 + by, STEEL[5])
                put(img, x0 + bx + 1, y0 + by + 1, d)
    for _ in range(6):
        x, y = rng.randrange(S), rng.randrange(S)
        dy = rng.choice((1, -1))
        for k in range(rng.randint(3, 6)):
            px, py = (x + k) % S, (y + dy * k) % S
            img.putpixel((px, py), mixc(img.getpixel((px, py)), STEEL[5], 0.45))
    amber = hexc("#f0bf21")
    for k in range(2):
        for y in range(7):
            for t in range(2):
                put(img, 12 + k * 6 + 3 - abs(y - 3) + t, 42 + y, amber)
    for y in range(74, 88, 3):
        for x in range(82, 112):
            put(img, x, y, d)
            put(img, x, y + 1, mixc(d, m, 0.4))
    for sx, sy in ((4, 27), (90, 59)):
        for k in range(rng.randint(4, 9)):
            put(img, sx, sy + 2 + k, rp[k % 2])
    return img


def slag(rng, rp):
    """Foundry's jungle (2026-11-06, floor zones; Preston: "quality and looking a legit moba map"). Every zone was
    steel plate in a different shade, so the built lane and the wild ground beside it read the same. This is a slag
    yard instead: warm dark ground with soft patches, gravel and pebbles, hairline cracks and rust. Everything wraps, so the 128 px tile repeats without a seam."""
    # a mid-tone between the light lane plates and the black path; the first, darker ramp read near black at dusk
    E = [(50, 44, 44, 255), (68, 60, 58, 255), (86, 77, 72, 255), (106, 95, 87, 255), (130, 117, 106, 255),
         (162, 148, 132, 255)]
    img = Image.new("RGBA", (S, S), E[2])
    px = img.load()

    def wput(x, y, c):
        px[x % S, y % S] = c

    for _ in range(9):  # soft patches a step up or down, with dithered rims
        cx, cy, r = rng.randrange(S), rng.randrange(S), rng.uniform(8, 18)
        c = E[1] if rng.random() < 0.5 else E[3]
        for y in range(-int(r) - 1, int(r) + 2):
            for x in range(-int(r) - 1, int(r) + 2):
                d = (x * x + y * y) ** 0.5 / r
                if d < 0.75 or (d < 1.0 and (x + y) % 2 == 0 and rng.random() < 0.8):
                    wput(cx + x, cy + y, c)
    for y in range(S):  # gravel
        for x in range(S):
            r = rng.random()
            if r < 0.06:
                wput(x, y, E[0] if px[x, y] == E[1] else E[1])
            elif r < 0.10:
                wput(x, y, E[3] if px[x, y] != E[3] else E[4])
            elif r < 0.115:
                wput(x, y, E[4])
            elif r < 0.118:
                wput(x, y, E[5])
    for _ in range(40):  # pebbles: lit top-left, shadow under
        x, y = rng.randrange(S), rng.randrange(S)
        wput(x, y, E[4]); wput(x + 1, y, E[3]); wput(x, y + 1, E[3]); wput(x + 1, y + 1, E[1]); wput(x + 1, y + 2, E[0])
    for _ in range(6):  # hairline cracks, some branching
        x, y = rng.randrange(S), rng.randrange(S)
        for k in range(rng.randint(8, 20)):
            wput(x, y, E[0])
            if k == 5 and rng.random() < 0.5:
                bx, by = x, y
                for _j in range(rng.randint(3, 7)):
                    bx += rng.choice((1, 0)); by += rng.choice((1, 1, -1))
                    wput(bx, by, E[0])
            x += rng.choice((1, 1, 0))
            y += rng.choice((1, 0, -1))
    for _ in range(0):  # half-sunk plates: off (2026-11-06), one per tile repeated every 2.56 m as a visible grid
        x0, y0 = rng.randrange(S), rng.randrange(S)
        w, h = rng.randint(18, 26), rng.randint(12, 18)
        for ly in range(h):
            for lx in range(w):
                c = STEEL[3]
                if lx == 0 or ly == 0:
                    c = STEEL[4]
                elif lx == w - 1 or ly == h - 1:
                    c = STEEL[2]
                edge = min(lx, ly, w - 1 - lx, h - 1 - ly)
                if edge < 3 and rng.random() < 0.55 - edge * 0.15:
                    continue
                wput(x0 + lx, y0 + ly, c)
        for rx, ry in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
            wput(x0 + rx, y0 + ry, STEEL[5])
            wput(x0 + rx + 1, y0 + ry + 1, STEEL[1])
        for _k in range(rng.randint(6, 12)):
            wput(x0 + rng.randrange(w), y0 + h - 1 - rng.randrange(4), rng.choice(rp))
    for _ in range(14):
        wput(rng.randrange(S), rng.randrange(S), rng.choice(rp))
    return img


def foundry_hq(t):
    rng = random.Random(9100)
    rp = t["rust"]
    made = {
        "paving": deck(rng, STEEL[4], STEEL[3], STEEL[5], 32, 0.2, 0.025, 1, 10, rp, 1),
        "jungle": deck(rng, STEEL[2], STEEL[1], STEEL[3], 32, 0.45, 0.03, 2, 6, rp, 3),
        "lane_grass": deck(rng, STEEL[5], STEEL[4], STEEL[6], 32, 0.15, 0.02, 1, 12, rp, 1, 0.1),
        "dirt": grit(rng),
        "cliff": corrugated(rng, STEEL[3], STEEL[2], STEEL[4], rp),
        "decals": decal_atlas(rng, rp),
        "lamp": lamp_tile(),
        "armor": armor(rng, rp),  # last, so the tiles above come out as before
    }
    made["jungle"] = slag(random.Random(9300), rp)  # 2026-11-06: its own seed, so every other tile is unchanged
    return made


def main():
    for i, (name, t) in enumerate(THEMES.items()):
        rng = random.Random(5200 + i)
        out_dir = os.path.join(ROOT, name)
        os.makedirs(out_dir, exist_ok=True)
        made = tiles(name, t, rng)
        if name == "foundry":
            made.update(foundry_hq(t))  # its own seed, so the other tiles come out as before
        for k, img in made.items():
            img.save(os.path.join(out_dir, k + ".png"))
        for make in (skyline_a, skyline_b, cap, stud, banner):
            make(name, t, rng).save(os.path.join(out_dir, make.__name__ + ".png"))
        print("wrote", name, sorted(made) + ["skyline_a", "skyline_b", "cap", "stud", "banner"])


if __name__ == "__main__":
    main()
