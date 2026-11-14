"""Our own pixel textures and billboard props for the 3D test field (Claude, 2026-11-04).

Preston: "make the world look like the reel next". The reel (Pokebonk) was measured, not copied: its open field
is lime grass at hue about 0.23 (85 degrees), saturation 0.54 to 0.68 and value 0.75 to 0.86 (median); its far
distance fades to a blue-grey haze (hue 0.57, saturation 0.26, value 0.6); shadows under things are purple-dark.
Everything here is drawn by code from those targets: seamless 32 px ground tiles and billboard props on the same
50 texels per metre grid as the machines, each prop with a one-texel dark outline like the machines' sel-out.
Writes art/field/moba3d/*.png. Seeded, so reruns give the same art.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "art/field/moba3d"
RNG = np.random.default_rng(23)


def hx(*cs):
    return np.array([[int(c[i:i + 2], 16) for i in (0, 2, 4)] for c in cs], np.uint8)


GRASS = hx("4E7A1C", "6E9F27", "86BE35", "9CD444", "C4EE70")
DIRT = hx("7A5E36", "9C7A44", "B8955A", "D2B47A")
WATER = hx("3A86C8", "4AA3E0", "7CC6F2", "E6F7FF")
LEAF = hx("2F5418", "4A7D22", "6AA52E", "8FCB3E", "BFE86A")
PINE = hx("1F4024", "2E5E33", "3F7A40", "5E9C52")
BARK = hx("3E2A1A", "5E4028", "7E5A38")
STONE = hx("4E5266", "6C7288", "8C93A8", "B8BED0")
OUTLINE_LEAF = (0x1A, 0x26, 0x12)
OUTLINE_STONE = (0x22, 0x24, 0x30)


def smooth_noise(n, cells, seed):
    """Tileable value noise in 0..1 on an n x n grid with `cells` lattice cells."""
    g = np.random.default_rng(seed).random((cells, cells))
    t = np.arange(n) * cells / n
    i0 = t.astype(int)
    f = t - i0
    f = f * f * (3 - 2 * f)
    i1 = (i0 + 1) % cells
    a = g[i0][:, i0] * (1 - f)[None, :] + g[i0][:, i1] * f[None, :]
    b = g[i1][:, i0] * (1 - f)[None, :] + g[i1][:, i1] * f[None, :]
    return a * (1 - f)[:, None] + b * f[:, None]


def tile(ramp, base, n=32, seed=0, cells=4, spread=0.22):
    """A seamless tile: low-frequency patches one step darker or lighter than the base colour."""
    v = smooth_noise(n, cells, seed) + (RNG.random((n, n)) - 0.5) * spread
    idx = np.clip(np.round(base + (v - 0.5) * 2.4), 0, len(ramp) - 1).astype(int)
    a = np.zeros((n, n, 4), np.uint8)
    a[..., :3] = ramp[idx]
    a[..., 3] = 255
    return a


def grass_tile():
    a = tile(GRASS, 2, seed=1)
    for _ in range(10):  # little tufts: a dark V with a light tip, wrapping across the edge
        x, y = RNG.integers(0, 32, 2)
        for dx, dy, c in ((-1, 0, 1), (1, 0, 1), (0, 1, 0), (0, -1, 4)):
            a[(y + dy) % 32, (x + dx) % 32, :3] = GRASS[c]
    return a


def dirt_tile():
    a = tile(DIRT, 2, seed=2, cells=8)
    for _ in range(14):
        x, y = RNG.integers(0, 32, 2)
        a[y, x, :3] = DIRT[0]
        a[y, (x + 1) % 32, :3] = DIRT[3]
    return a


def water_tile():
    a = tile(WATER, 1, seed=3, cells=2, spread=0.1)
    for _ in range(4):  # ripple dashes, few and short so the tiling does not read as stripes
        x, y = RNG.integers(0, 32, 2)
        for k in range(RNG.integers(2, 4)):
            a[y, (x + k) % 32, :3] = WATER[2]
        a[(y + 1) % 32, (x + 1) % 32, :3] = WATER[0]
    return a


def outline(a, colour):
    """One texel of outline outside the silhouette, like the machines' sel-out."""
    op = a[..., 3] > 0
    ring = np.zeros_like(op)
    ring[1:] |= op[:-1]
    ring[:-1] |= op[1:]
    ring[:, 1:] |= op[:, :-1]
    ring[:, :-1] |= op[:, 1:]
    ring &= ~op
    a[ring, :3] = colour
    a[ring, 3] = 255
    return a


def lobes_sprite(w, h, lobes, ramp, light=(-0.55, -0.8)):
    """Union of round lobes, each shaded by its own sphere normal against a top-left light, in ramp steps."""
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    shade = np.full((h, w), -9.0)
    for cx, cy, r in lobes:
        dx, dy = (xx - cx) / r, (yy - cy) / r
        d2 = dx * dx + dy * dy
        inside = d2 <= 1.0
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        s = -(dx * light[0] + dy * light[1]) * 0.8 + nz * 0.5 - 0.15
        # a later (front) lobe covers earlier ones
        shade = np.where(inside, s, shade)
    op = shade > -9
    lv = np.clip(np.round((shade + 0.7) / 1.5 * (len(ramp) - 1)), 0, len(ramp) - 1).astype(int)
    a[op, :3] = ramp[lv[op]]
    a[op, 3] = 255
    # sparkle highlights on the brightest step and dark speckles in the shade, so the mass is not a gradient
    hi = op & (lv == len(ramp) - 1) & (RNG.random((h, w)) < 0.12)
    a[hi, :3] = ramp[-1] // 2 + 128
    lo = op & (lv <= 1) & (RNG.random((h, w)) < 0.15)
    a[lo, :3] = ramp[0]
    return a


def round_tree():
    w, h = 170, 250
    a = np.zeros((h, w, 4), np.uint8)
    # trunk: three tones, lit on the left
    for y in range(150, h - 2):
        half = 9 + (y - 150) // 18
        for x in range(w // 2 - half, w // 2 + half):
            t = (x - (w // 2 - half)) / (2 * half)
            a[y, x, :3] = BARK[2] if t < 0.3 else BARK[1] if t < 0.75 else BARK[0]
            a[y, x, 3] = 255
    lobes = []
    for _ in range(16):
        ang = RNG.uniform(0, 2 * np.pi)
        rr = RNG.uniform(0, 42)
        lobes.append((w / 2 + np.cos(ang) * rr * 1.3, 92 + np.sin(ang) * rr * 0.9, RNG.uniform(26, 38)))
    lobes.sort(key=lambda l: l[1])  # lower lobes in front
    c = lobes_sprite(w, h, lobes, LEAF)
    m = c[..., 3] > 0
    a[m] = c[m]
    return outline(a, OUTLINE_LEAF)


def pine_tree():
    w, h = 120, 270
    a = np.zeros((h, w, 4), np.uint8)
    for y in range(225, h - 2):
        for x in range(w // 2 - 7, w // 2 + 7):
            a[y, x, :3] = BARK[2] if x < w // 2 - 2 else BARK[1]
            a[y, x, 3] = 255
    tiers = [(30, 26), (75, 38), (125, 48), (180, 56)]
    for top, half in tiers:
        tier_h = 70
        for y in range(top, top + tier_h):
            k = (y - top) / tier_h
            hw = int(half * (0.15 + 0.85 * k))
            for x in range(w // 2 - hw, w // 2 + hw):
                t = (x - (w // 2 - hw)) / max(1, 2 * hw)
                step = 3 if t < 0.25 else 2 if t < 0.55 else 1 if t < 0.85 else 0
                if k > 0.85 and RNG.random() < 0.5:  # ragged lower edge of each tier
                    continue
                a[y, x, :3] = PINE[step]
                a[y, x, 3] = 255
    return outline(a, OUTLINE_LEAF)


def bush():
    w, h = 84, 58
    lobes = [(20, 36, 18), (62, 36, 18), (42, 26, 22), (32, 40, 17), (52, 41, 17)]
    a = lobes_sprite(w, h, lobes, LEAF)
    a[-3:] = 0
    return outline(a, OUTLINE_LEAF)


def rock():
    w, h = 58, 40
    lobes = [(22, 24, 15), (36, 26, 14), (29, 18, 13)]
    a = lobes_sprite(w, h, lobes, STONE)
    a[-3:] = 0
    return outline(a, OUTLINE_STONE)


def flower(petal, centre):
    a = np.zeros((14, 16, 4), np.uint8)
    stem = GRASS[1]
    for y in range(7, 13):
        a[y, 7, :3] = stem
        a[y, 7, 3] = 255
    a[10, 8, :3], a[10, 8, 3] = GRASS[3], 255
    for dx, dy in ((0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        a[5 + dy, 7 + dx, :3], a[5 + dy, 7 + dx, 3] = petal, 255
    a[5, 7, :3] = centre
    return outline(a, OUTLINE_LEAF)


def tuft():
    a = np.zeros((16, 22, 4), np.uint8)
    for x0, hgt in ((5, 9), (9, 12), (12, 10), (16, 8)):
        for k in range(hgt):
            x = x0 + (k // 4) * (1 if x0 > 10 else -1)
            a[14 - k, x, :3] = GRASS[4] if k > hgt - 3 else GRASS[3] if k > hgt // 2 else GRASS[2]
            a[14 - k, x, 3] = 255
    return outline(a, OUTLINE_LEAF)


def shadow(w=64, h=64, alpha=(115, 150)):
    yy, xx = np.mgrid[0:h, 0:w]
    e = np.hypot((xx - (w - 1) / 2) / (w / 2), (yy - (h - 1) / 2) / (h / 2))
    a = np.zeros((h, w, 4), np.uint8)
    a[e <= 1.0] = (0x2B, 0x1D, 0x45, alpha[0])  # purple-dark, as the reel's shadows
    a[e <= 0.7] = (0x2B, 0x1D, 0x45, alpha[1])
    return a


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = {
        "grass_tile": grass_tile(), "dirt_tile": dirt_tile(), "water_tile": water_tile(),
        "tree_round": round_tree(), "tree_pine": pine_tree(), "bush": bush(), "rock": rock(),
        "flower_white": flower((0xF4, 0xF4, 0xFA), (0xFF, 0xD8, 0x4A)),
        "flower_pink": flower((0xF2, 0x7A, 0xB0), (0xFF, 0xF0, 0x9A)),
        "flower_violet": flower((0x9B, 0x6B, 0xDB), (0xFF, 0xF0, 0x9A)),
        "tuft": tuft(), "shadow": shadow(),
    }
    for name, a in out.items():
        Image.fromarray(a).save(OUT / f"{name}.png")
    g = out["grass_tile"][..., :3].reshape(-1, 3) / 255.0
    mx, mn = g.max(1), g.min(1)
    print("grass tile: value median %.2f, saturation median %.2f (reel field: value 0.75-0.86, saturation 0.54-0.68)"
          % (np.median(mx), np.median((mx - mn) / np.maximum(mx, 1e-6))))
    print("wrote", ", ".join(out))


if __name__ == "__main__":
    main()
