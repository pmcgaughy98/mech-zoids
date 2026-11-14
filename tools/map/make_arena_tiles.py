"""World tiles for the MOBA arena. Map design lane, 2026-11-04.

Draws the arena's surface tiles pixel by pixel, all ours, seeded so every run gives the same files:
  python tools/map/make_arena_tiles.py
Writes 32 x 32 tiles (0.64 m at the shared 50 texels per metre) that wrap on every side, into
art/field/moba3d/arena/. The colours come from the field_test tiles in art/field/moba3d/ (grass, dirt, stone,
water, the tree greens), so the arena sits with the field and the machines.

  lane_grass  bright grass inside the lane walls, beside the path
  jungle      darker grass with leaf litter, for the jungle floor (darker than the lane, so the lane reads)
  dirt        the worn path down the lane, with pebbles
  paving      flagstones for the plaza and the bases (tinted per base in the ground shader)
  cliff       layered rock for wall, rim, rock and cliff faces
  grass_top   mossy grass for the tops of walls, rocks and cliffs
  pit_floor   dark worn stone for the side pits
  banner      a 40 x 72 px cloth banner in greys, tinted with a team colour in the shader (not a tile)
"""
import os
import random

from PIL import Image

N = 32
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "art", "field", "moba3d", "arena")


def hexc(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


GRASS = [hexc(c) for c in ("#4e7a1c", "#6e9f27", "#86be35", "#9cd444", "#c4ee70")]
JUNGLE = [hexc(c) for c in ("#1f4024", "#2e5e33", "#3f7a40", "#4e7a1c", "#5e9c52")]
LITTER = [hexc(c) for c in ("#5e4028", "#7e5a38")]
DIRT = [hexc(c) for c in ("#7a5e36", "#9c7a44", "#b8955a", "#d2b47a")]
STONE = [hexc(c) for c in ("#2e2c36", "#4a4854", "#5e5c69", "#75737f", "#8c93a8")]
PAVE = [hexc(c) for c in ("#5a5248", "#857a6a", "#a3978a", "#bfb3a0", "#d8cdb8")]  # light, so paving reads apart from dirt
MOSS = [hexc(c) for c in ("#2f5418", "#4a7d22", "#6aa52e", "#8fcb3e")]


def noise(rng, cells=4):
    """Value noise that wraps: a cells x cells grid of randoms, smoothly blended up to N x N."""
    g = [[rng.random() for _ in range(cells)] for _ in range(cells)]
    out = [[0.0] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            fx, fy = x * cells / N, y * cells / N
            x0, y0 = int(fx), int(fy)
            tx, ty = fx - x0, fy - y0
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            a = g[y0 % cells][x0 % cells]
            b = g[y0 % cells][(x0 + 1) % cells]
            c = g[(y0 + 1) % cells][x0 % cells]
            d = g[(y0 + 1) % cells][(x0 + 1) % cells]
            out[y][x] = (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty
    return out


def put(img, x, y, c):
    img.putpixel((x % N, y % N), c)


def field(rng, pal, levels, cells=4, jitter=0.18):
    """Fill with palette steps chosen by noise plus a little per-pixel jitter (no flat areas, no gradients)."""
    img = Image.new("RGBA", (N, N))
    n = noise(rng, cells)
    for y in range(N):
        for x in range(N):
            v = n[y][x] + (rng.random() - 0.5) * jitter
            i = 0
            while i < len(levels) and v > levels[i]:
                i += 1
            img.putpixel((x, y), pal[i])
    return img


def blades(img, rng, count, body, tip):
    for _ in range(count):
        x, y = rng.randrange(N), rng.randrange(N)
        put(img, x, y, body)
        put(img, x, y - 1, tip)


def lane_grass(rng):
    img = field(rng, GRASS[0:3], [0.32, 0.7])
    blades(img, rng, 26, GRASS[3], GRASS[4])
    return img


def jungle(rng):
    img = field(rng, JUNGLE[0:4], [0.2, 0.5, 0.8])
    blades(img, rng, 18, JUNGLE[3], JUNGLE[4])
    for _ in range(7):  # fallen leaves: two pixels, light over dark
        x, y = rng.randrange(N), rng.randrange(N)
        put(img, x, y, LITTER[1])
        put(img, x + 1, y, LITTER[0])
    return img


def dirt(rng):
    img = field(rng, DIRT[0:3], [0.28, 0.72], cells=4, jitter=0.25)
    for _ in range(6):  # pebbles, lit from the top left
        x, y = rng.randrange(N), rng.randrange(N)
        put(img, x, y, DIRT[3])
        put(img, x + 1, y, DIRT[2])
        put(img, x, y + 1, DIRT[2])
        put(img, x + 1, y + 1, DIRT[0])
    for _ in range(3):  # short ruts along the path
        x, y = rng.randrange(N), rng.randrange(N)
        for k in range(rng.randint(3, 6)):
            put(img, x + k, y, DIRT[0])
    return img


def paving(rng):
    """Flagstones in three staggered rows, 1 px mortar, each stone lit top left and shaded bottom right."""
    img = Image.new("RGBA", (N, N), PAVE[0])
    rows = [(0, 10), (11, 10), (22, 9)]  # top, height (mortar rows at 10, 21, 31)
    offs = [0, 9, 4]
    for (top, h), off in zip(rows, offs):
        cuts, x = [], off
        while x < off + N:
            cuts.append(x)
            x += rng.choice([9, 11, 12, 14])
        for i, a in enumerate(cuts):
            b = cuts[i + 1] if i + 1 < len(cuts) else off + N
            base = rng.choice([PAVE[2], PAVE[2], PAVE[3]])
            for yy in range(top, top + h):
                for xx in range(a + 1, b):
                    c = base
                    if yy == top or xx == a + 1:
                        c = PAVE[4] if base == PAVE[3] else PAVE[3]
                    elif yy == top + h - 1 or xx == b - 1:
                        c = PAVE[1]
                    elif rng.random() < 0.06:
                        c = PAVE[1]
                    put(img, xx, yy, c)
    return img


def cliff(rng):
    """Layered rock: bands 3 to 6 px deep, broken into blocks; the top row of each block catches the light."""
    img = Image.new("RGBA", (N, N))
    y = 0
    while y < N:
        h = min(rng.choice([3, 4, 5, 6]), N - y)
        x = rng.randrange(N)
        end = x + N
        while x < end:
            w = rng.randint(5, 12)
            base = rng.choice([STONE[1], STONE[2], STONE[2], STONE[3]])
            for yy in range(y, y + h):
                for xx in range(x, min(x + w, end)):
                    c = base
                    if yy == y:
                        c = STONE[min(STONE.index(base) + 1, 4)]
                    elif yy == y + h - 1 or xx == x:
                        c = STONE[0]
                    elif rng.random() < 0.05:
                        c = STONE[max(STONE.index(base) - 1, 1)]
                    put(img, xx, yy, c)
            x += w
        y += h
    for _ in range(5):  # moss in the cracks
        x, y = rng.randrange(N), rng.randrange(N)
        put(img, x, y, MOSS[1])
        put(img, x + 1, y, MOSS[0])
    return img


def grass_top(rng):
    img = field(rng, MOSS[0:3], [0.25, 0.65])
    blades(img, rng, 20, MOSS[2], MOSS[3])
    return img


def pit_floor(rng):
    img = field(rng, [STONE[0], STONE[1], STONE[2]], [0.3, 0.75], cells=8, jitter=0.3)
    for _ in range(4):
        x, y = rng.randrange(N), rng.randrange(N)
        for k in range(rng.randint(2, 5)):
            put(img, x + k, y + (k // 2), STONE[0])
    return img


def banner(rng):
    """Greys only, so one image serves both teams: the shader multiplies it by the team colour."""
    w, h = 40, 72
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rod, edge, fold, body, mark = (70, 60, 50, 255), (110, 110, 110, 255), (165, 165, 165, 255), (205, 205, 205, 255), (255, 255, 255, 255)
    for y in range(h):
        for x in range(w):
            if y < 3:
                img.putpixel((x, y), rod)
                continue
            if y > 63 and abs(x - 19.5) < (y - 63) * 2.4:
                continue  # the swallowtail notch
            if x < 2 or x > 37:
                continue
            c = body
            if x < 4 or x > 35 or y < 5 or (y > 61 and abs(x - 19.5) < (y - 61) * 2.4 + 2):
                c = edge
            elif x in (11, 12) or x == 28:
                c = fold
            d = abs(x - 19.5) + abs(y - 30) * 0.8
            if 5 < d < 9 or d < 2:
                c = mark
            img.putpixel((x, y), c)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, make in enumerate([lane_grass, jungle, dirt, paving, cliff, grass_top, pit_floor, banner]):
        img = make(random.Random(4100 + i))
        path = os.path.join(OUT, make.__name__ + ".png")
        img.save(path)
        print("wrote", os.path.normpath(path), len(set(img.getdata())), "colours")


if __name__ == "__main__":
    main()
