"""A from-scratch 64x64 GBA-style canine mech, built from 3D blocks and rendered down to pixels (Claude, Hollowtide
session, 2026-10-13; Preston: "a completely new, from-scratch 64x64 sprite in the exact visual style of Zoids Legacy
... a strict 16-color palette consisting of metallic blues, gunmetal grays, and clear transparent indexing ... an
isometric profile view of a canine-type Zoid with a heavy 1-pixel dark outline and distinct mechanical panel shading").

A second take beside tools/art/gba_canine_sprite.py (the mech session's, drawn flat on the index grid); this one
models the machine as tapered blocks, renders them through a three-quarter camera with a depth buffer at 6x, votes
each 64px cell down to one block face (so no colours ever mix), and then applies the pixel passes. Original design:
nothing is traced or copied from any Zoid.

What the synthesis contributed:
- docs/reference/sprite-rules-legacy-2026-10-12.md (the mech session, 93 Legacy sprites measured): light from the
  upper left, long ramps, round joint discs with a pale centre and a coloured ring, panel lines as dark seams, a tiny
  bright eye, no dithering, a flat violet ground shadow.
- Study of the two canine Legacy sprites (command_wolf, shadow_fox; technique only, measured 2026-10-13): they face
  left, stand low and long (width 1.37 to 1.54 times height), and are two-tone: pale armour plates over a dark inner
  frame (30 to 36 % dark interior), with highlights on only 6 to 9 % of pixels and the far legs a step darker.
- The mech session's 3D-to-pixel method (tools/blender/render_sprite_views.py, pixelize_render.py): shade per plane,
  never per pixel; a dark line where two parts meet.
- Hollowtide's pixel passes (tools/arena/selout.py, docs/art/art-direction.md, the dungeon sprite work): no
  anti-aliased pixels, a deterministic outline pass, stray-pixel cleanup, one strict palette.
- GBA hardware (OBJ tiles at 4 bits per pixel): 16 colours per palette with index 0 transparent, colours in 15-bit
  BGR555, so every channel here is snapped to the 32 levels the console can show; the PNG is written as a true
  4-bit indexed file.
- Preston's brief over one measured rule: Legacy outlines selectively; this sprite wears the heavy 1-pixel outline he
  asked for, in near-black navy.

    python tools/art/gba_canine_voxel.py [out_dir]       (default docs/art/2d/gba_canine_voxel)
"""
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

N = 64          # the sprite
SS = 6          # supersampling for the vote
YAW = math.radians(16)     # the head end turns toward the viewer: a three-quarter profile
PITCH = math.radians(26)   # looking down onto the back: the "isometric" top plane shows
ZS = 1.18                  # pass 2: legs longer, so the frame stands 1.4 to 1.5 times wider than tall like Legacy's canines


# ---- the palette: 16 entries, index 0 transparent, every colour on the GBA's 15-bit grid ---------------------------
def gba(c):
    out = []
    for v in c:
        c5 = min(31, max(0, int(round(v * 31 / 255))))
        out.append((c5 << 3) | (c5 >> 2))   # how the console expands 5 bits to 8
    return tuple(out)


RAW = [
    (0, 0, 0),          # 0  transparent
    (16, 16, 34),       # 1  outline: near-black navy
    (22, 30, 70),       # 2  blue 1: seams, deepest shadow (shifted toward indigo)
    (30, 54, 118),      # 3  blue 2: underside, far side
    (40, 86, 166),      # 4  blue 3: side plates
    (62, 126, 206),     # 5  blue 4: lit plates
    (108, 174, 232),    # 6  blue 5: top planes (shifted toward cyan)
    (202, 232, 248),    # 7  blue 6: rim glints
    (30, 34, 46),       # 8  gunmetal 1: frame seams
    (52, 60, 76),       # 9  gunmetal 2: frame shadow
    (82, 92, 110),      # 10 gunmetal 3: frame
    (124, 136, 154),    # 11 gunmetal 4: lit frame, paws
    (186, 196, 210),    # 12 gunmetal 5: joint centres, claw glints
    (60, 214, 246),     # 13 eye glow
    (234, 252, 255),    # 14 eye core
    (42, 34, 66),       # 15 ground shadow: violet navy
]
PALETTE = [gba(c) for c in RAW]
O = 1
BLUE = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
GUN = {1: 8, 2: 9, 3: 10, 4: 11, 5: 12}
EYE, EYE_CORE, SHADOW = 13, 14, 15


# ---- the machine: tapered blocks ------------------------------------------------------------------------------------
def seg(a, b, wa, ha, wb=None, hb=None):
    """A block from point a to point b (x toward the tail, y toward the viewer, z up), wa x ha at a, wb x hb at b.
    Width runs along y (depth), height across the axis in the upright plane."""
    a, b = np.array(a, float), np.array(b, float)
    a[2] *= ZS
    b[2] *= ZS
    wb = wa if wb is None else wb
    hb = ha if hb is None else hb
    d = (b - a) / np.linalg.norm(b - a)
    s = np.array([0.0, 1.0, 0.0])
    s = s - d * s.dot(d)
    s /= np.linalg.norm(s)
    u = np.cross(d, s)
    if u[2] < 0:
        u = -u
    pts = []
    for p, w, h in ((a, wa, ha), (b, wb, hb)):
        for sy, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            pts.append(p + s * sy * w / 2 + u * sz * h / 2)
    return np.array(pts)


FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
parts = []      # each: corners, material, far
joints = []     # (point, size)


def add(corners, mat, far=False):
    parts.append({"c": corners, "mat": mat, "far": far})


def build():
    # body: a dark frame core under three blue armour shells, so the belly and the gaps read dark (two-tone)
    add(seg((18, 0, 19), (46, 0, 19.5), 7, 6), "frame")
    add(seg((15.5, 0, 20), (26, 0, 21), 10, 10, 9, 9), "armor")            # chest
    add(seg((26.6, 0, 23.6), (36, 0, 23.2), 9, 4, 8.6, 3.6), "armor")      # back plate
    add(seg((36.6, 0, 21.6), (46.5, 0, 22), 9.4, 6.5, 8.4, 6), "armor")    # haunch
    for i, x in enumerate((24.0, 29.5, 35.0)):                            # a low row of dorsal vanes
        add(seg((x, 0, 24.6), (x + 2.6, 0, 28.6 - 0.7 * i), 1.0, 2.4, 0.8, 1.2), "armor")
    # neck and head
    add(seg((18, 0, 21), (12, 0, 23.5), 5, 4.6), "frame")
    add(seg((19.5, 0, 24.6), (13.5, 0, 25.7), 6.8, 2.6, 6, 2.2), "armor")  # collar plates
    add(seg((14.5, 0, 24.2), (7.5, 0, 23.4), 6.8, 7, 6, 6), "armor")       # skull
    add(seg((8, 0, 23), (2.2, 0, 21.6), 4.6, 4.0, 3.2, 2.6), "armor")      # snout
    add(seg((11.5, 0, 20.2), (3.0, 0, 19.7), 3.8, 2.2, 2.6, 1.6), "frame")  # jaw
    add(seg((12.5, 2.0, 26.8), (18.5, 2.4, 32.5), 1.3, 3.4, 0.7, 1.2), "armor")             # near ear fin
    add(seg((12.5, -2.0, 26.8), (18.5, -2.4, 32.5), 1.3, 3.4, 0.7, 1.2), "armor", far=True)
    # tail: frame root, armoured middle, a blade tip
    add(seg((46, 0, 22.5), (51.5, 0, 25.5), 3.6, 3.4, 3, 3), "frame")
    add(seg((51.5, 0, 25.5), (55, 0, 28), 3, 3, 2.6, 2.6), "armor")
    add(seg((55, 0, 28), (59, 0, 29.5), 1.6, 3.6, 0.6, 0.9), "armor")
    # legs: near side y = +4, far side y = -4 (a step darker); a stride, near front forward, near rear back
    for y, far, fo, ro in ((-4.0, True, 3.5, -3.0), (4.0, False, -1.5, 2.0)):
        sgn = 1 if y > 0 else -1
        add(seg((19.5 + fo, y * 1.32, 22.5), (24.5 + fo, y * 1.32, 22.5), 2.2, 8.5, 2.0, 7.5), "armor", far)   # shoulder plate
        add(seg((22 + fo, y, 19), (19.5 + fo, y, 10.5), 2.8, 3.2, 2.4, 2.6), "frame", far)
        add(seg((19.5 + fo, y, 10.5), (20 + fo, y, 3), 2.2, 2.4, 2, 2.2), "frame", far)
        add(seg((19.2 + fo, y + 0.9 * sgn, 10), (19.9 + fo, y + 0.9 * sgn, 4.5), 0.8, 3, 0.8, 2.4), "armor", far)  # shin guard
        add(seg((16.5 + fo, y, 1.3), (22 + fo, y, 1.2), 3.6, 2.4, 3.4, 2.2), "metal", far)                       # paw
        add(seg((15 + fo, y, 0.7), (16.8 + fo, y, 0.9), 3.2, 1.4, 3.4, 1.6), "metal", far)                        # claws
        add(seg((38.5 + ro, y * 1.3, 21), (45 + ro, y * 1.3, 21), 2.2, 7.5, 2.0, 6.5), "armor", far)             # hip plate
        add(seg((42 + ro, y, 20), (38.5 + ro, y, 12), 3.6, 4, 3, 3), "frame", far)                                # thigh
        add(seg((38.5 + ro, y, 12), (43.5 + ro, y, 6), 2.6, 2.6, 2.2, 2.2), "frame", far)                         # shin
        add(seg((39 + ro, y + 0.9 * sgn, 11.4), (42.8 + ro, y + 0.9 * sgn, 7), 0.8, 2.6, 0.8, 2.2), "armor", far)
        add(seg((43.5 + ro, y, 6), (42.6 + ro, y, 1.6), 2.2, 2.2, 2, 2), "frame", far)                            # hock
        add(seg((39.5 + ro, y, 1.2), (45 + ro, y, 1.2), 3.4, 2.2, 3.2, 2), "metal", far)
        add(seg((38.2 + ro, y, 0.7), (39.8 + ro, y, 0.9), 3, 1.3, 3.2, 1.5), "metal", far)
        if not far:
            joints.extend([((22 + fo, 6.0, 19.5), "big"), ((19.5 + fo, 5.3, 10.5), "small"),
                           ((42 + ro, 6.0, 19.8), "big"), ((38.5 + ro, 5.3, 12), "small"), ((43.5 + ro, 5.3, 6), "small")])


# ---- camera ---------------------------------------------------------------------------------------------------------
def cam(p):
    """Model space to camera space: X right, Y up, Z toward the viewer."""
    p = np.asarray(p, float)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    cy, sy, cp, sp = math.cos(YAW), math.sin(YAW), math.cos(PITCH), math.sin(PITCH)
    x1 = x * cy + y * sy
    y1 = -x * sy + y * cy
    return np.stack([x1, -y1 * sp + z * cp, y1 * cp + z * sp], axis=-1)


LIGHT = np.array([-0.5, 0.7, 0.5]) / np.linalg.norm([-0.5, 0.7, 0.5])   # from the upper left, toward the viewer


def render():
    R = N * SS
    allc = cam(np.concatenate([p["c"] for p in parts]))
    minx, maxx = allc[:, 0].min(), allc[:, 0].max()
    miny, maxy = (-allc[:, 1]).min(), (-allc[:, 1]).max()
    scale = min(58.0 / (maxx - minx), 46.0 / (maxy - miny))
    ox = 32.0 - scale * (minx + maxx) / 2
    oy = 60.0 - scale * maxy               # the lowest foot ends on row 59; the outline and the shadow go under it
    zbuf = np.full((R, R), -1e9)
    fbuf = np.full((R, R), -1, int)
    faces = []
    for pi, part in enumerate(parts):
        cc = cam(part["c"])
        centre = cc.mean(0)
        for f in FACES:
            q = cc[list(f)]
            n = np.cross(q[1] - q[0], q[2] - q[0])
            if np.linalg.norm(n) < 1e-9:
                n = np.cross(q[2] - q[0], q[3] - q[0])
            n /= np.linalg.norm(n)
            if n.dot(q.mean(0) - centre) < 0:
                n = -n
            if n[2] <= 0.02:
                continue                     # facing away
            fid = len(faces)
            faces.append({"part": pi, "n": n})
            sx = (q[:, 0] * scale + ox) * SS
            sy = (-q[:, 1] * scale + oy) * SS
            for tri in ((0, 1, 2), (0, 2, 3)):
                _raster(zbuf, fbuf, sx[list(tri)], sy[list(tri)], q[list(tri), 2], fid)
    return zbuf, fbuf, faces, (scale, ox, oy)


def _raster(zbuf, fbuf, xs, ys, zs, fid):
    R = zbuf.shape[0]
    x0, x1, x2 = xs
    y0, y1, y2 = ys
    area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    if abs(area) < 1e-9:
        return
    lx, hx = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), R - 1)
    ly, hy = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), R - 1)
    if lx > hx or ly > hy:
        return
    X, Y = np.meshgrid(np.arange(lx, hx + 1) + 0.5, np.arange(ly, hy + 1) + 0.5)
    w0 = ((x1 - X) * (y2 - Y) - (x2 - X) * (y1 - Y)) / area
    w1 = ((x2 - X) * (y0 - Y) - (x0 - X) * (y2 - Y)) / area
    w2 = 1 - w0 - w1
    inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
    depth = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
    zb = zbuf[ly:hy + 1, lx:hx + 1]
    fb = fbuf[ly:hy + 1, lx:hx + 1]
    m = inside & (depth > zb)
    zb[m] = depth[m]
    fb[m] = fid


# ---- down to 64 px: one face per cell, by vote ----------------------------------------------------------------------
def vote(zbuf, fbuf):
    f = fbuf.reshape(N, SS, N, SS).transpose(0, 2, 1, 3).reshape(N, N, SS * SS)
    z = zbuf.reshape(N, SS, N, SS).transpose(0, 2, 1, 3).reshape(N, N, SS * SS)
    face = np.full((N, N), -1, int)
    depth = np.full((N, N), -1e9)
    for r in range(N):
        for c in range(N):
            v = f[r, c]
            hit = v >= 0
            if hit.mean() < 0.42:
                continue
            ids, counts = np.unique(v[hit], return_counts=True)
            face[r, c] = ids[counts.argmax()]
            depth[r, c] = z[r, c][v == face[r, c]].mean()
    return face, depth


# ---- the pixel passes -----------------------------------------------------------------------------------------------
def shade(face, depth, faces):
    part = np.where(face >= 0, np.vectorize(lambda i: faces[i]["part"] if i >= 0 else -1)(face), -1)
    idx = np.zeros((N, N), int)
    level = np.zeros((N, N), int)
    mats = np.empty((N, N), object)
    for r in range(N):
        for c in range(N):
            if face[r, c] < 0:
                continue
            fc = faces[face[r, c]]
            p = parts[fc["part"]]
            lam = max(0.0, float(fc["n"].dot(LIGHT)))
            s = 0.3 + 0.7 * lam
            if p["mat"] == "armor":
                lv = 1 + int(round(s * 4))          # 2..5, plane by plane
            elif p["mat"] == "frame":
                lv = 2 + int(round(s * 2.2))        # 2..4, lighter than pass 1 so the legs read
            else:
                lv = 2 + int(round(s * 3))          # paws and claws 3..5
            if p["far"]:
                lv -= 1
            level[r, c] = lv
            mats[r, c] = (p["mat"], lam)
    out = level.copy()
    for r in range(N):
        for c in range(N):
            if face[r, c] < 0:
                continue
            mat, lam = mats[r, c]
            lv = level[r, c]
            me, dz = part[r, c], depth[r, c]

            def nb(rr, cc):
                if not (0 <= rr < N and 0 <= cc < N) or face[rr, cc] < 0:
                    return "empty"
                if part[rr, cc] == me:
                    return "same"
                return "nearer" if depth[rr, cc] > dz + 1.0 else "farther"

            around = [nb(r - 1, c), nb(r + 1, c), nb(r, c - 1), nb(r, c + 1)]
            if "nearer" in around:
                lv = 1                                     # a seam: the part behind darkens where another covers it
            else:
                if around[0] in ("empty", "farther"):       # a top edge: the light rim
                    cap = (6 if lam > 0.45 else 5) if mat == "armor" else (4 if mat == "frame" else 5)
                    lv = min(cap, lv + 1)
                if around[1] in ("empty", "farther"):       # an underside edge
                    lv = max(1, lv - 1)
            out[r, c] = lv
            idx[r, c] = BLUE[max(1, min(6, lv))] if mat == "armor" else GUN[max(1, min(5, lv))]
    return idx, part


def clean_strays(idx, protect):
    """A pixel matching none of its four neighbours takes the colour two or more of them share (Hollowtide's rule)."""
    out = idx.copy()
    for r in range(N):
        for c in range(N):
            if idx[r, c] == 0 or protect[r, c]:
                continue
            nbs = [idx[rr, cc] for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < N and 0 <= cc < N]
            if idx[r, c] in nbs:
                continue
            solid = [v for v in nbs if v != 0]
            if len(solid) < 2:
                continue
            vals, counts = np.unique(solid, return_counts=True)
            if counts.max() >= 2:
                out[r, c] = vals[counts.argmax()]
    return out


def to_px(p, fit):
    scale, ox, oy = fit
    p = (p[0], p[1], p[2] * ZS)
    q = cam(p)
    return int(math.floor(q[0] * scale + ox)), int(math.floor(-q[1] * scale + oy))


def stamp(idx, protect, x, y, size):
    """Legacy's joint disc: a pale centre in a blue ring, rounded by dark corners."""
    if size == "big":
        cells = {(0, 0): GUN[5], (1, 0): GUN[4], (0, 1): GUN[4], (1, 1): GUN[3],
                 (-1, 0): BLUE[2], (-1, 1): BLUE[2], (2, 0): BLUE[2], (2, 1): BLUE[2],
                 (0, -1): BLUE[2], (1, -1): BLUE[2], (0, 2): BLUE[2], (1, 2): BLUE[2]}
    else:
        cells = {(0, 0): GUN[5], (-1, 0): BLUE[3], (1, 0): BLUE[3], (0, -1): BLUE[3], (0, 1): BLUE[3]}
    for (dx, dy), v in cells.items():
        xx, yy = x + dx, y + dy
        if 0 <= xx < N and 0 <= yy < N and idx[yy, xx] != 0:
            idx[yy, xx] = v
            protect[yy, xx] = True


def outline(idx):
    out = idx.copy()
    solid = idx != 0
    for r in range(N):
        for c in range(N):
            if solid[r, c]:
                continue
            if any(0 <= rr < N and 0 <= cc < N and solid[rr, cc] for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))):
                out[r, c] = O
    return out


def ground_shadow(idx, fit):
    """Legacy's flat violet ground line, laid along the ground under the near feet. In a three-quarter view the ground
    recedes, so the line climbs from the front claws to the rear heel instead of staying on one row."""
    xa, ya = to_px((13.0, 4.0, 0.0), fit)
    xb, yb = to_px((48.0, 4.0, 0.0), fit)
    for c in range(max(0, xa), min(N, xb + 1)):
        r = int(round(ya + (yb - ya) * (c - xa) / max(1, xb - xa))) + 1
        for _ in range(4):
            if r >= N or idx[r, c] == 0:
                break
            r += 1
        if r < N and idx[r, c] == 0:
            idx[r, c] = SHADOW
    return idx


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "docs", "art", "2d", "gba_canine_voxel")
    os.makedirs(out_dir, exist_ok=True)
    build()
    zbuf, fbuf, faces, fit = render()
    face, depth = vote(zbuf, fbuf)
    idx, part = shade(face, depth, faces)
    protect = np.zeros((N, N), bool)
    idx = clean_strays(idx, protect)
    for p, size in joints:
        x, y = to_px(p, fit)
        stamp(idx, protect, x, y, size)
    ex, ey = to_px((9.6, 3.0, 24.0), fit)                   # the eye: a two-pixel slit, the core toward the snout
    for dx, v in ((0, EYE_CORE), (1, EYE)):
        if idx[ey, ex + dx] != 0:
            idx[ey, ex + dx] = v
    idx = outline(idx)
    idx = ground_shadow(idx, fit)

    img = Image.fromarray(idx.astype("uint8"), "P")
    flat = [v for c in PALETTE for v in c]
    img.putpalette(flat)
    path = os.path.join(out_dir, "gba_canine_voxel_64.png")
    img.save(path, transparency=0, bits=4, optimize=False)
    # a preview at 8x on a dark ground, for looking only
    big = img.convert("RGBA").resize((N * 8, N * 8), Image.NEAREST)
    bg = Image.new("RGBA", big.size, (40, 40, 46, 255))
    bg.alpha_composite(big)
    bg.save(os.path.join(out_dir, "gba_canine_voxel_64_x8.png"))
    used = sorted(set(idx.flatten().tolist()))
    print("wrote %s: %d palette entries, %d used (%s), %d opaque pixels" % (path, len(PALETTE), len(used), used, int((idx != 0).sum())))


if __name__ == "__main__":
    main()
