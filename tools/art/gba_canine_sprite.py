"""A from-scratch 64x64 GBA-style canine mech sprite (Claude, 2026-10-13; Preston: "write a Python script using PIL
to generate a completely new, from-scratch 64x64 sprite in the exact visual style of Zoids Legacy ... a strict
16-color palette of metallic blues, gunmetal grays and clear transparent indexing ... an isometric profile view of a
canine-type Zoid with a heavy 1-pixel dark outline and distinct mechanical panel shading").

Style rules, from the synthesis:
- docs/reference/sprite-rules-legacy-2026-10-12.md (measured on the 93 Zoids Legacy battle sprites): long ramps per
  material, light from the upper left (top edges lit, undersides dark), panel lines as a dark line with a light line
  under it, round joint discs with a pale centre and a coloured ring, a tiny bright eye with its own ramp, no
  dithering.
- Hollowtide's pixel passes (D:/dev/hollowtide/docs/art/art-direction.md, tools/arena/selout.py): zero anti-aliased
  pixels, a deterministic outline pass, one strict palette, one strong angular silhouette, no stray pixels.
- Preston's brief overrides one measured rule: Legacy edges use a selective outline (only 4 % darkest); this sprite
  wears the heavy 1-pixel outline he asked for, in near-black navy rather than pure black.
Original design, nothing traced or copied: a canine frame with a tall crest of plates down the neck, a single pod on
the haunch (no back cannon), and a segmented tail ending in a blade.

Everything is drawn on an index grid (palette indices, 0 transparent), so the PNG is a true 16-colour indexed file.
    python tools/art/gba_canine_sprite.py [out_dir]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

W = H = 64

# ---- the strict 16-colour palette: index 0 is transparent ----------------------------------------------------
PALETTE = [
    (0, 0, 0),          # 0  transparent
    (14, 16, 30),       # 1  outline: near-black navy
    (24, 36, 74),       # 2  blue 1: deepest shadow, panel seams
    (34, 60, 128),      # 3  blue 2: shaded side
    (48, 92, 176),      # 4  blue 3: main side face
    (82, 136, 214),     # 5  blue 4: lit face
    (142, 190, 238),    # 6  blue 5: top face highlight
    (214, 234, 255),    # 7  blue 6: specular glint
    (30, 32, 40),       # 8  gunmetal 1: frame shadow
    (52, 56, 66),       # 9  gunmetal 2
    (76, 82, 94),       # 10 gunmetal 3: frame base
    (106, 114, 128),    # 11 gunmetal 4: lit frame
    (150, 158, 170),    # 12 gunmetal 5: frame highlight
    (200, 206, 214),    # 13 gunmetal 6: hub centre, bolt glint
    (90, 236, 255),     # 14 eye glow
    (64, 82, 112),      # 15 steel blue: joint rings, mid-tone bridge between the two materials
]
BLUE = [2, 3, 4, 5, 6, 7]     # dark to light
METAL = [8, 9, 10, 11, 12, 13]
RAMPS = [BLUE, METAL]

grid = np.zeros((H, W), np.uint8)


def poly(points, idx):
    """Fill a polygon with one palette index (no anti-aliasing: PIL's L-mode polygon on an index image)."""
    im = Image.fromarray(grid, "L")
    ImageDraw.Draw(im).polygon(points, fill=idx)
    grid[:] = np.array(im)


def line(points, idx, width=1):
    im = Image.fromarray(grid, "L")
    ImageDraw.Draw(im).line(points, fill=idx, width=width)
    grid[:] = np.array(im)


def px(x, y, idx):
    if 0 <= x < W and 0 <= y < H:
        grid[y, x] = idx


def box3(top, side, front, ramp, levels=(4, 2, 1)):
    """An isometric block: top face lit, side face mid, front face shaded (light from the upper left)."""
    poly(side, ramp[levels[1]])
    poly(top, ramp[levels[0]])
    if front:
        poly(front, ramp[levels[2]])


def hub(cx, cy, r=2):
    """A round joint disc: steel ring, gunmetal body, pale centre (Legacy's joint vocabulary)."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= r * r + 1:
                px(x, y, 15 if d >= (r - 1) ** 2 + 1 else 10)
    px(cx, cy, 13)
    px(cx - 1, cy - 1, 12)


def leg(pts, ramp, far=False):
    """A limb as a chain of tapered segments; far limbs one ramp step darker."""
    shift = -1 if far else 0
    for (x0, y0, w0), (x1, y1, w1) in zip(pts, pts[1:]):
        poly([(x0 - w0, y0), (x0 + w0, y0), (x1 + w1, y1), (x1 - w1, y1)], ramp[max(0, 2 + shift)])
        line([(x0 - w0, y0), (x1 - w1, y1)], ramp[max(0, 3 + shift)])   # lit front edge of the strut


# ---- the drawing, far to near -------------------------------------------------------------------------------
# far legs (gunmetal, darker), drawn first so the body overlaps them
leg([(39, 36, 1), (41, 45, 1), (40, 53, 1)], METAL, far=True)          # far front: thin strut, set back from the near one
poly([(38, 53), (43, 53), (43, 55), (37, 55)], METAL[1])              # far front paw
leg([(26, 37, 2), (23, 46, 1), (26, 53, 1)], METAL, far=True)          # far hind
poly([(24, 53), (29, 53), (29, 55), (23, 55)], METAL[1])

# tail: four plates stepping back and down from the rump to a blade
tail = [(14, 27), (10, 29), (7, 32), (5, 36)]
for i, (x, y) in enumerate(tail):
    box3([(x - 2, y - 2), (x + 3, y - 3), (x + 4, y - 1), (x - 1, y)], [(x - 1, y), (x + 4, y - 1), (x + 4, y + 2), (x - 1, y + 3)], None, BLUE, (4 - (i > 1), 2, 1))
poly([(2, 38), (6, 35), (7, 37), (3, 41), (1, 42)], METAL[4])           # tail blade
line([(2, 40), (6, 36)], METAL[2])

# body: an isometric block, blue armour over a gunmetal frame
poly([(17, 34), (44, 30), (43, 34), (19, 37)], METAL[2])                # the frame under the armour, belly tucked (deeper joined the legs into a block)
box3(top=[(15, 24), (40, 19), (47, 22), (21, 27)],
     side=[(21, 27), (47, 22), (46, 31), (19, 35)],
     front=[(47, 22), (50, 25), (49, 32), (46, 31)], ramp=BLUE)
for x0, x1 in ((26, 27), (35, 36)):                                     # armour panel seams: dark line, light line under
    line([(x0, 26 - (x0 - 21) // 5), (x0 - 1, 34 - (x0 - 21) // 6)], BLUE[0])
    line([(x1, 26 - (x1 - 21) // 5), (x1 - 1, 34 - (x1 - 21) // 6)], BLUE[3])
line([(22, 31), (45, 27)], BLUE[1])                                     # the side's horizontal seam
line([(22, 32), (45, 28)], BLUE[4])

# the crest: a row of tall plates down the back of the neck (this design's signature)
for i, (x, y, h) in enumerate(((44, 20, 5), (39, 20, 6), (34, 21, 5))):   # three chunky plates (four read as spikes)
    poly([(x - 1, y), (x + 2, y - h), (x + 4, y - h + 1), (x + 4, y)], BLUE[4] if i % 2 else BLUE[3])
    line([(x + 1, y - 1), (x + 3, y - h + 1)], BLUE[5])

# haunch pod: a single sealed launcher on the near hip (no back cannon)
box3(top=[(17, 25), (24, 23), (26, 25), (19, 27)], side=[(19, 27), (26, 25), (26, 30), (19, 32)], front=None, ramp=METAL, levels=(4, 2, 1))
for y in (28, 30):
    line([(20, y), (25, y - 2)], METAL[0])
px(25, 26, 14)                                                         # pod sensor

# neck and head: a long wedge skull, the snout reaching right and down
poly([(44, 22), (51, 18), (54, 22), (49, 28), (45, 29)], METAL[2])       # neck frame
box3(top=[(48, 14), (55, 12), (61, 17), (54, 19)],
     side=[(54, 19), (61, 17), (62, 21), (55, 24)],
     front=[(48, 14), (54, 19), (55, 24), (50, 24), (47, 19)], ramp=BLUE)
poly([(55, 24), (62, 21), (62, 23), (56, 26)], METAL[3])                # lower jaw
line([(55, 24), (62, 22)], BLUE[0])                                     # the mouth line
px(60, 23, 13); px(58, 24, 13)                                          # fangs, pale
poly([(49, 14), (50, 8), (52, 13)], BLUE[3])                            # ears: two angular plates
poly([(52, 13), (54, 7), (55, 12)], BLUE[4])
px(50, 10, BLUE[5]); px(54, 9, BLUE[5])
px(56, 17, 14); px(57, 17, 14); px(57, 16, 7)                          # the eye: glow and its glint

# near legs: blue armour on the upper leg, gunmetal struts below, joint hubs
poly([(41, 27), (48, 26), (47, 34), (42, 35)], BLUE[3])                 # near shoulder plate
line([(42, 27), (47, 26)], BLUE[5])
leg([(46, 34, 2), (49, 43, 1), (48, 53, 1)], METAL)                     # near front
poly([(46, 53), (52, 53), (53, 55), (45, 56)], METAL[2])                # near front paw
line([(47, 53), (51, 53)], METAL[4])
poly([(16, 28), (24, 27), (25, 36), (18, 37)], BLUE[3])                 # near thigh plate
line([(17, 28), (23, 27)], BLUE[5])
leg([(20, 36, 2), (15, 45, 1), (18, 53, 1)], METAL)                     # near hind, digitigrade
poly([(15, 53), (21, 53), (22, 55), (14, 56)], METAL[2])
line([(16, 53), (20, 53)], METAL[4])
for cx, cy, r in ((45, 31, 2), (49, 43, 1), (21, 33, 2), (15, 45, 1)):
    hub(cx, cy, r)

# ---- finishing passes (deterministic, Hollowtide-style) ------------------------------------------------------
def ramp_of(i):
    for r in RAMPS:
        if i in r:
            return r
    return None


def step(i, d):
    r = ramp_of(int(i))
    if r is None:
        return int(i)
    k = r.index(int(i))
    return r[max(0, min(len(r) - 1, k + d))]


solid = grid > 0
pad = np.pad(solid, 1)
up, down, left = ~pad[:-2, 1:-1], ~pad[2:, 1:-1], ~pad[1:-1, :-2]
out = grid.copy()
for y in range(H):
    for x in range(W):
        i = grid[y, x]
        if not solid[y, x] or i in (1, 14, 13):
            continue
        if up[y, x]:
            out[y, x] = step(i, +1)          # light from above: lit top rims only (left rims too read as fur)
        elif down[y, x]:
            out[y, x] = step(i, -1)          # undersides fall into the dark end of the ramp
grid[:] = out

# strays: a pixel unlike all four neighbours takes the most common neighbour (no noise)
g = grid.copy()
for y in range(1, H - 1):
    for x in range(1, W - 1):
        n = [g[y - 1, x], g[y + 1, x], g[y, x - 1], g[y, x + 1]]
        if g[y, x] not in n and g[y, x] not in (14, 13, 7) and all(v > 0 for v in n):
            grid[y, x] = max(set(n), key=n.count)

# the heavy outline: every transparent pixel touching the shape (4-way) becomes outline navy
solid = grid > 0
pad = np.pad(solid, 1)
touch = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
grid[(~solid) & touch] = 1

# ---- write the indexed PNG ------------------------------------------------------------------------------------
out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join("docs", "art", "2d", "gba_canine")
os.makedirs(out_dir, exist_ok=True)
img = Image.fromarray(grid, "P")
flat = [c for rgb in PALETTE for c in rgb] + [0] * (768 - 3 * len(PALETTE))
img.putpalette(flat)
path = os.path.join(out_dir, "gba_canine_64.png")
img.save(path, transparency=0)
img.convert("RGBA").resize((W * 6, H * 6), Image.NEAREST).save(os.path.join(out_dir, "gba_canine_64_x6.png"))

# checks: 16 palette entries, index 0 transparent, every pixel fully on or off, colours used
used = sorted(set(np.unique(grid).tolist()))
rgba = np.array(Image.open(path).convert("RGBA"))
alpha = set(np.unique(rgba[..., 3]).tolist())
print("wrote %s: %dx%d indexed, palette %d entries, %d indices used %s, alpha values %s" % (
    path, W, H, len(PALETTE), len(used), used, sorted(alpha)))
