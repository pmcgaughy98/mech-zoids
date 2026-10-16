"""Original procedural textures for the 3D machines (Claude, 2026-10-11; Preston: "can you at least use these to skill-up";
"use synthesis as well"). Lessons, not copies: finished low-poly mechs get their detail from painted textures, not
geometry. Armour plates are split into panels, each inset with a dark seam and a light top/left edge, with rivets
at some corners and the odd vent; the inner frame is a busy machinery sheet of pistons, cables, slats and bolts
under the clean armour (Polycount and SpringRTS texture-artist threads; FromSoftware on early Armored Core looking
"like dolls constructed from cardboard boxes" until the parts were given purpose). Nothing is traced from any game.
  python tools/blender/make_mech_textures.py [machine_id]
Writes art/machines/<id>/textures/<key>.png, 256x256, one per material key in machines.gd colours.
"""
import os, random, sys
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SIZE = 256
SCHEMES = {   # per machine: material key -> base hex (from scripts/data/machines.gd plus the shared frame)
    "ape_l": {"main": "5c804a", "trim": "3e5a33", "accent": "d98a40", "frame": "8a8d92", "frame_dark": "45474c"},
}


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def split_panels(rng, x0, y0, x1, y1, depth, out):
    """Recursive cuts: big calm panels, a few smaller ones, never slivers."""
    w, h = x1 - x0, y1 - y0
    if depth == 0 or (w < 56 and h < 56) or (depth < 3 and rng.random() < 0.3):
        out.append((x0, y0, x1, y1))
        return
    if w >= h and w >= 40:
        c = x0 + int(w * rng.uniform(0.35, 0.65))
        split_panels(rng, x0, y0, c, y1, depth - 1, out)
        split_panels(rng, c, y0, x1, y1, depth - 1, out)
    elif h >= 40:
        c = y0 + int(h * rng.uniform(0.35, 0.65))
        split_panels(rng, x0, y0, x1, c, depth - 1, out)
        split_panels(rng, x0, c, x1, y1, depth - 1, out)
    else:
        out.append((x0, y0, x1, y1))


def armour(base_hex, seed):
    rng = random.Random(seed)
    base = hexrgb(base_hex)
    img = Image.new("RGB", (SIZE, SIZE), base)
    d = ImageDraw.Draw(img)
    panels = []
    split_panels(rng, 0, 0, SIZE, SIZE, 4, panels)
    for (x0, y0, x1, y1) in panels:
        tone = shade(base, rng.uniform(0.93, 1.06))
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=tone)
        # soft painted shading: a little darker toward the bottom of each panel
        for y in range(y0, y1):
            t = (y - y0) / max(1, y1 - y0)
            if t > 0.6:
                d.line([x0, y, x1 - 1, y], fill=shade(tone, 1.0 - 0.10 * (t - 0.6) / 0.4))
        d.line([x0, y0, x1 - 1, y0], fill=shade(tone, 1.28))          # lit top edge
        d.line([x0, y0, x0, y1 - 1], fill=shade(tone, 1.18))          # lit left edge
        d.line([x0, y1 - 1, x1 - 1, y1 - 1], fill=shade(base, 0.45))  # dark seam
        d.line([x1 - 1, y0, x1 - 1, y1 - 1], fill=shade(base, 0.52))
        if rng.random() < 0.6 and x1 - x0 > 36 and y1 - y0 > 30:   # a recessed inner panel (Cybertron panel work)
            ix0, iy0, ix1, iy1 = x0 + 7, y0 + 7, x1 - 8, y1 - 8
            d.rectangle([ix0, iy0, ix1, iy1], fill=shade(tone, 0.86))
            d.line([ix0, iy0, ix1, iy0], fill=shade(base, 0.5))      # shadowed top and left inside the recess
            d.line([ix0, iy0, ix0, iy1], fill=shade(base, 0.55))
            d.line([ix0, iy1, ix1, iy1], fill=shade(tone, 1.2))      # lit bottom and right lip
            d.line([ix1, iy0, ix1, iy1], fill=shade(tone, 1.15))
        for _ in range(rng.randint(0, 2)):   # worn scratches showing steel
            sx, sy = rng.randint(x0 + 2, max(x0 + 3, x1 - 12)), rng.randint(y0 + 2, max(y0 + 3, y1 - 6))
            d.line([sx, sy, sx + rng.randint(4, 10), sy + rng.randint(-2, 3)], fill=(150, 152, 150))
        if rng.random() < 0.55:   # rivets at two corners
            for (cx, cy) in [(x0 + 4, y0 + 4), (x1 - 6, y1 - 6)]:
                d.rectangle([cx, cy, cx + 1, cy + 1], fill=shade(base, 0.55))
                d.point((cx, cy), fill=shade(base, 1.35))
        if rng.random() < 0.35 and x1 - x0 > 30 and y1 - y0 > 24:   # vents (more since the 2026-10-11 finish pass)
            vx, vy = x0 + 8, y0 + (y1 - y0) // 2 - 6
            for k in range(5):
                d.line([vx, vy + k * 3, vx + 18, vy + k * 3], fill=shade(base, 0.5))
                d.line([vx, vy + k * 3 + 1, vx + 18, vy + k * 3 + 1], fill=shade(base, 1.2))
    return img


def machinery(base_hex, seed):
    """The inner frame: pistons, cables, slats, bolts and a few teal indicator pips, tiling sideways."""
    rng = random.Random(seed)
    base = hexrgb(base_hex)
    img = Image.new("RGB", (SIZE, SIZE), shade(base, 0.8))
    d = ImageDraw.Draw(img)
    x = 0
    while x < SIZE:
        kind = rng.choice(["piston", "cables", "slats", "plate"])
        w = rng.randint(18, 40)
        if kind == "piston":
            d.rectangle([x + 3, 0, x + w - 4, SIZE], fill=shade(base, 1.05))
            d.line([x + 5, 0, x + 5, SIZE], fill=shade(base, 1.45))
            d.line([x + w - 6, 0, x + w - 6, SIZE], fill=shade(base, 0.55))
            for y in range(rng.randint(0, 20), SIZE, rng.randint(40, 70)):
                d.rectangle([x + 2, y, x + w - 3, y + 5], fill=shade(base, 0.6))
                d.line([x + 2, y, x + w - 3, y], fill=shade(base, 1.3))
        elif kind == "cables":
            n = max(2, w // 7)
            for k in range(n):
                cx = x + 3 + k * 7
                d.rectangle([cx, 0, cx + 4, SIZE], fill=shade(base, 0.55))
                d.line([cx + 1, 0, cx + 1, SIZE], fill=shade(base, 0.95))
        elif kind == "slats":
            for y in range(0, SIZE, 4):
                d.line([x + 2, y, x + w - 3, y], fill=shade(base, 0.45))
                d.line([x + 2, y + 1, x + w - 3, y + 1], fill=shade(base, 1.15))
        else:
            d.rectangle([x + 1, 0, x + w - 2, SIZE], fill=base)
            for y in range(rng.randint(4, 12), SIZE, rng.randint(22, 36)):
                d.rectangle([x + 4, y, x + 5, y + 1], fill=shade(base, 0.5))
                d.rectangle([x + w - 7, y, x + w - 6, y + 1], fill=shade(base, 0.5))
                if rng.random() < 0.12:
                    d.rectangle([x + w // 2 - 1, y + 6, x + w // 2 + 1, y + 7], fill=(95, 225, 208))   # teal pip
        d.line([x, 0, x, SIZE], fill=shade(base, 0.35))
        x += w
    return img


def height(seed, dense=False, size=1024):
    """Height texture for the surface-detail bake (2026-10-11, pass 18: 1024 px, sharper). Grooves between plates,
    each plate bevelling down at its edges, recessed inner panels, domed bolts, vent slats. Feature sizes scale with
    the texture so the grooves survive being baked onto the whole machine."""
    k = size / 256.0
    rng = random.Random(seed)
    img = Image.new("L", (size, size), 200)
    d = ImageDraw.Draw(img)
    panels = []
    split_panels(rng, 0, 0, 256, 256, 5 if dense else 4, panels)
    for (x0, y0, x1, y1) in panels:
        X0, Y0, X1, Y1 = int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)
        for i in range(int(6 * k)):   # the plate's bevel: low at the edge, rising to the face
            d.rectangle([X0 + i, Y0 + i, X1 - 1 - i, Y1 - 1 - i], outline=int(110 + i * 105 / (6 * k)))
        d.rectangle([X0 + int(6 * k), Y0 + int(6 * k), X1 - int(7 * k), Y1 - int(7 * k)], fill=215)
        if x1 - x0 > 36 and y1 - y0 > 30 and rng.random() < 0.6:   # recessed inner panel with a soft step
            for i in range(int(3 * k)):
                d.rectangle([X0 + int(9 * k) + i, Y0 + int(9 * k) + i, X1 - int(10 * k) - i, Y1 - int(10 * k) - i], outline=150 + i * 6)
            d.rectangle([X0 + int(12 * k), Y0 + int(12 * k), X1 - int(13 * k), Y1 - int(13 * k)], fill=168)
        d.rectangle([X0, Y0, X1 - 1, Y1 - 1], outline=30)          # the groove between plates
        d.rectangle([X0 + 1, Y0 + 1, X1 - 2, Y1 - 2], outline=45)
        d.rectangle([X0 + 2, Y0 + 2, X1 - 3, Y1 - 3], outline=70)
        if rng.random() < 0.6:   # domed bolts in the corners
            for (cx, cy) in [(X0 + int(10 * k), Y0 + int(10 * k)), (X1 - int(11 * k), Y0 + int(10 * k)),
                             (X0 + int(10 * k), Y1 - int(11 * k)), (X1 - int(11 * k), Y1 - int(11 * k))]:
                for rr in range(int(2.5 * k), 0, -1):
                    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=int(255 - rr * 40 / (2.5 * k)))
        if rng.random() < 0.3 and x1 - x0 > 40 and y1 - y0 > 30:   # vent slats
            vx, vy = X0 + int(12 * k), Y0 + (Y1 - Y0) // 2 - int(8 * k)
            for i in range(4):
                d.rectangle([vx, vy + int(i * 5 * k), vx + int(22 * k), vy + int(i * 5 * k + 2 * k)], fill=70)
    return img


def main():
    mid = sys.argv[1] if len(sys.argv) > 1 else "ape_l"
    out = os.path.join(ROOT, "art", "machines", mid, "textures")
    os.makedirs(out, exist_ok=True)
    for i, (key, h) in enumerate(SCHEMES[mid].items()):
        img = machinery(h, 100 + i) if key.startswith("frame") else armour(h, 10 + i)
        img.save(os.path.join(out, key + ".png"))
        height(300 + i, dense=key.startswith("frame")).save(os.path.join(out, key + "_height.png"))
        print("wrote", key)


if __name__ == "__main__":
    main()
