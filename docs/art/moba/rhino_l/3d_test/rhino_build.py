"""Rhino 3D test, part-built voxels (Claude, 3D test lane, 2026-11-04).

Built the way drone model B was: solids measured off the approved views (take-a/views, 192 x 192, feet on row 160),
one voxel per texel at 0.020 m (pass 2), shades cut per part to the shares the views use, seams where plates meet.
Coordinates in texels: a forward (to the head), b sideways, c up from the ground. The model stands on c = 0.

Pitch: the carve fit (rhino_pitch.py, pitch_fit.json) is flat from 6 to 16 degrees (best 12); the feet say about
1 to 4 (far feet drawn 1 to 3 rows above near ones). Pass 1 used 12 and read the armour's upper bevels as top faces,
which made a thin slab; pass 2 uses 6, the low end of the carve plateau, and tall bevelled sides.

Writes rhino_parts.glb, reproject_rhino.png, rhino_report.json.   Run: python rhino_build.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWS = os.path.join(HERE, "..", "take-a", "views")
sys.path.insert(0, os.path.join(HERE, "..", "..", "minion_s", "take-a", "3d_test"))
import voxel_build as vb  # noqa: E402  (greedy_quads, write_glb, palette_png)

PASS = 5
TEXEL = 0.020
PITCH = 6.0
# top-shape numbers (texels). Pass 5 values; pass 6 sets them from rhino_cam30.py's search against the game-camera views.
P5 = dict(rear_top=53, rear_flat=12, rear_bevel=0.5, rear_half=33, rear_back=-45, hump_top=68, hump_ha=7, hump_hb=10.5,
          hump_a=1, pa_top=58, head_top=54, head_w=16)
SHAPE = dict(P5)
DRAWN = {"s": 0, "se": 45, "e": 90, "ne": 135, "n": 180}
NA, NB, NC = 116, 84, 84
OA, OB = 58, 42
IA, IB, IC = np.meshgrid(np.arange(NA), np.arange(NB), np.arange(NC), indexing="ij")
A = IA - OA + 0.5
B = IB - OB + 0.5
C = IC + 0.5
AB = np.abs(B)

RAMPS = {
    "yellow": ["7a4a06", "d18a0a", "ffcf1f", "fff4a8"],
    "grey": ["58555e", "9d9ba2", "d6d6dc"],
    "char": ["211e27", "3d3a44"],
    "seam": ["141218"],
    "eye": ["ff3a2a", "ffe6d8"],
}
LIGHT = np.array([0.25, 0.0, 0.95])  # no sideways part: the drawn west views mirror the east ones
LIGHT = LIGHT / np.linalg.norm(LIGHT)


# ---------------------------------------------------------------- views and measured shade shares
def load_views():
    out = {}
    for n, yaw in DRAWN.items():
        im = np.array(Image.open(os.path.join(VIEWS, n + ".png")).convert("RGBA"))
        m = im[:, :, 3] > 0
        xs = np.nonzero(m)[1]
        key = (im[:, :, 0].astype(int) << 16) | (im[:, :, 1].astype(int) << 8) | im[:, :, 2].astype(int)
        out[n] = dict(yaw=yaw, rgba=im, mask=m, key=np.where(m, key, -1), axis=(xs.min() + xs.max()) / 2)
    return out


def shares(views, regions, ramp):
    keys = [int(h, 16) for h in ramp]
    cnt = np.zeros(len(ramp))
    for n, (x0, x1, y0, y1) in regions:
        k = views[n]["key"][y0:y1 + 1, x0:x1 + 1]
        for i, kk in enumerate(keys):
            cnt[i] += (k == kk).sum()
    return (cnt / max(cnt.sum(), 1)).round(3).tolist()


REGIONS = {
    "hump": [("s", (77, 113, 91, 103)), ("e", (79, 113, 94, 106))],
    "rear": [("e", (51, 88, 107, 133))],
    "pauldron": [("s", (60, 76, 104, 136)), ("s", (116, 132, 104, 136)), ("e", (88, 108, 108, 136))],
    "head": [("e", (108, 132, 107, 133)), ("s", (79, 112, 104, 134))],
    "boot": [("s", (61, 131, 145, 152)), ("e", (44, 117, 143, 152)), ("n", (60, 131, 145, 152))],
    "tail": [("e", (44, 50, 121, 132)), ("n", (88, 101, 121, 134))],
    "sole": [("s", (59, 133, 153, 160)), ("e", (44, 117, 153, 160))],
    "disc": [("s", (64, 77, 136, 146)), ("e", (53, 67, 134, 146)), ("e", (90, 103, 136, 146))],
    "horn": [("e", (123, 147, 101, 123)), ("s", (90, 102, 100, 128))],
    "jaw": [("e", (120, 141, 133, 143)), ("s", (82, 110, 135, 149))],
    "core": [("e", (51, 125, 133, 153)), ("s", (76, 116, 104, 160))],
}


# ---------------------------------------------------------------- parts (texels), measured off s and e at 12 deg
def box(a0, a1, b_half, c0, c1):
    return (A >= a0) & (A <= a1) & (AB <= b_half) & (C >= c0) & (C <= c1)


def build_parts(p=None):
    p = p or SHAPE
    P = {}  # name -> (mask, ramp, share-region key)
    # dark body and neck under the plates
    front_r = -11 + (53 - C) * 0.3                               # the rear armour's slanted front edge
    seamwall = (A >= front_r - 0.5) & (A <= front_r + 3.5) & (AB <= 31) & (C >= 27)
    seamwall &= C <= 51 - 0.8 * np.clip(AB - 20, 0, None)      # stays under the armour's outline
    P["core"] = (box(-36, 6, 30, 17, 40) | box(-43, 14, 17, 17, 40) | box(-30, 6, 20, 17, 50) | box(-8, 18, 17, 26, 50) | seamwall,
                 "char", "core")
    # rear armour: the hind body shell. Its upper bevel is the light band in e rows 107-122, its side the darker
    # band below (pass 2: pass 1 read the bevel as a top face and built a thin slab)
    rt, rh, rk = p["rear_top"], p["rear_half"], p["rear_back"]
    rear = (A >= rk) & (A <= -11 + (53 - C) * 0.3) & (AB <= rh) & (C >= 31) & (C <= rt)
    rear &= C <= rt - p["rear_bevel"] * np.clip(AB - p["rear_flat"], 0, None)  # upper side bevel
    rear &= C >= 31 + 2.0 * np.clip(AB - (rh - 4), 0, None)      # lower side bevel
    rear &= C <= rt - 0.8 * np.clip(rk + 14 - A, 0, None)        # rear-top chamfer (e view, rows 107 -> 119)
    rear &= C >= 31 + 1.0 * np.clip(rk + 4 - A, 0, None)         # rear-bottom chamfer
    P["rear"] = (rear, "yellow", "rear")
    # shoulder plates (pauldrons) either side of the head, hexagonal in the s view
    pt = p["pa_top"]
    pa = (AB >= 19) & (AB <= 36) & (A >= -11 + (53 - C) * 0.3 + 3) & (A <= 14) & (C >= 29) & (C <= pt)
    pa &= C <= pt - 0.9 * np.clip(AB - 24, 0, None)
    pa &= C >= 29 + 2.0 * np.clip(AB - 33, 0, None)
    pa &= C <= pt - 1.5 * np.clip(A - 8, 0, None)
    pa &= C <= pt - 1.5 * np.clip(-3 - A, 0, None)
    pa &= C >= 29 + 2.0 * np.clip(A - 10, 0, None)
    P["pauldron"] = (pa, "yellow", "pauldron")
    # hump: a low octagonal frustum on top of the front body, flat top at c 68
    ht, hc = p["hump_top"], p["hump_a"]
    ha = p["hump_ha"] + (ht - C) * 0.75
    hb = p["hump_hb"] + (ht - C) * 0.68
    hump = (C >= 50) & (C <= ht) & (np.abs(A - hc) <= ha) & (AB <= hb)
    hump &= (np.abs(A - hc) / ha + AB / hb) <= 1.45
    P["hump"] = (hump, "yellow", "hump")
    # head: a wedge, forehead at c 54 sloping to the snout at c 41, chamfered front corners
    top = p["head_top"] - 0.95 * np.clip(A - 22, 0, None)
    head = (A >= 12) & (A <= 38) & (C >= 29) & (C <= top)
    head &= AB <= p["head_w"] - 0.5 * np.clip(C - 44, 0, None)
    head &= AB <= p["head_w"] - 1.2 * np.clip(A - 31, 0, None)
    head &= C >= 29 + 1.5 * np.clip(A - 34, 0, None)
    P["head"] = (head, "yellow", "head")
    # jaw: grey U plate under the snout, sticking out in front (e x 120-141, s x 82-110)
    jaw = (A >= 22) & (A <= 46) & (AB <= 14) & (C >= 19) & (C <= 30)
    jaw &= ~((A > 36) & (((A - 36) / 10.5) ** 2 + (B / 14.5) ** 2 > 1))
    P["jaw"] = (jaw, "grey", "jaw")
    # nose plate on the snout front
    P["nose"] = (box(34, 39.5, 6, 31, 44), "grey", "horn")
    # big horn: front edge upright then curving back to the tip (e x 132-147, rows 101-123)
    front = np.where(C <= 47, 52, 52 - (C - 47) * 0.5)
    back = 37 + (C - 38) * 0.3
    rb = 6 - (C - 38) * 0.22
    horn = (C >= 37) & (C <= 61) & (A >= back) & (A <= front) & (AB <= rb)
    P["horn"] = (horn, "grey", "horn")
    # small horn behind it (e x 124-133, rows 106-120)
    rs = 4.5 - (C - 41) * 0.25
    small = (C >= 39) & (C <= 55) & (np.abs(A - 32.5) <= rs) & (AB <= rs * 0.8)
    P["small_horn"] = (small, "grey", "horn")
    # legs: sole, boot, shin, knee disc. Front pair at a +1, hind pair at a -39, both at b +-23.5
    legs = {"sole": None, "boot": None, "shin": None, "disc": None}
    for a0 in (1.0, -39.0):
        for sb in (-1, 1):
            b0 = 23.5 * sb
            da, db = np.abs(A - a0), np.abs(B - b0)
            sole = (da <= 9.5) & (db <= 11) & (C <= 7)
            sole &= C <= 7 - np.clip(np.maximum(da - 8, db - 9.5), 0, None)
            boot = (da <= 8) & (db <= 7.5) & (C >= 7) & (C <= 22)
            boot &= C <= 22 - 1.0 * np.clip(np.maximum(da - 6, db - 5.5), 0, None)
            shin = (da <= 5) & (db <= 5) & (C >= 20) & (C <= 36)
            disc = ((A - a0) ** 2 + (C - 24) ** 2 <= 6.6 ** 2) & (AB >= 19.5) & (AB <= 31.5)
            for k, m in (("sole", sole), ("boot", boot), ("shin", shin), ("disc", disc)):
                legs[k] = m if legs[k] is None else legs[k] | m
    P["shin"] = (legs["shin"], "char", "core")
    P["boot"] = (legs["boot"], "yellow", "boot")
    P["sole"] = (legs["sole"], "grey", "sole")
    P["disc"] = (legs["disc"], "grey", "disc")
    # tail stub at the back
    P["tail"] = (box(-52, -44, 5, 29, 40), "yellow", "tail")
    return P


ORDER = ["core", "shin", "rear", "pauldron", "hump", "head", "jaw", "nose", "small_horn", "horn",
         "sole", "boot", "disc", "tail"]


def colour(p=None):
    """Shaded, seamed voxel model: (views, occ, surf, grid, pal, shares). Split out of main() for rhino_cam30.py."""
    views = load_views()
    P = build_parts(p)
    sh = {k: shares(views, r, RAMPS[{"core": "char", "sole": "grey", "disc": "grey", "horn": "grey",
                                      "jaw": "grey"}.get(k, "yellow")]) for k, r in REGIONS.items()}
    part = np.full((NA, NB, NC), -1, np.int16)
    for i, name in enumerate(ORDER):
        part[P[name][0]] = i
    occ = part >= 0
    surf = occ & ~ndimage.binary_erosion(occ, iterations=1, border_value=0)

    pal = []
    def pidx(h):
        if h not in pal:
            pal.append(h)
        return pal.index(h)

    # normals per part (from that part's own solid, so a plate keeps its faces where others overlap it)
    si = np.argwhere(surf)
    pid = part[tuple(si.T)]
    nrm = np.zeros((len(si), 3))
    for i, name in enumerate(ORDER):
        sel = pid == i
        if not sel.any():
            continue
        g = ndimage.gaussian_filter(P[name][0].astype(np.float32), 2.0)
        gr = np.stack([np.gradient(g, axis=k)[tuple(si[sel].T)] for k in range(3)], -1)
        nrm[sel] = -gr / (np.linalg.norm(gr, axis=-1, keepdims=True) + 1e-6)
    # pass 3: which surface voxels the five drawn views actually see (z-buffer at the drawn pitch)
    ca, cb, cc = si[:, 0] - OA + 0.5, si[:, 1] - OB + 0.5, si[:, 2] + 0.5
    pr = np.radians(PITCH)
    vis = np.zeros(len(si))
    for v in views.values():
        f = np.radians(v["yaw"])
        x = ca * np.sin(f) - cb * np.cos(f)
        t = ca * np.cos(f) + cb * np.sin(f)
        key = np.floor(161 - (cc * np.cos(pr) - t * np.sin(pr))).astype(int) * 400 + np.floor(x + 200).astype(int)
        near = t * np.cos(pr) + cc * np.sin(pr)
        o = np.lexsort((near, key))
        last = np.r_[key[o][1:] != key[o][:-1], True]
        vis[o[last]] += 1
    # shades: one fixed light; per part, the light thresholds are set so the voxels the views see carry the
    # shade shares the views use (pass 2 ranked every voxel, hidden ones included, which left the seen faces too light)
    grid = np.full(occ.shape, -1, np.int32)
    kgrid = np.full(occ.shape, -1, np.int16)
    d = nrm @ LIGHT
    for i, name in enumerate(ORDER):
        mask, ramp_name, region = P[name]
        ramp = RAMPS[ramp_name]
        sel = np.nonzero(pid == i)[0]
        if not len(sel):
            continue
        share = np.array(sh[region])
        w = vis[sel] + 0.05
        o = np.argsort(d[sel])
        cw = np.cumsum(w[o]) / w.sum()
        th = [d[sel][o][min(np.searchsorted(cw, q), len(o) - 1)] for q in np.cumsum(share)[:-1]]
        cut = np.searchsorted(np.array(th), d[sel], side="right")
        kgrid[tuple(si[sel].T)] = cut
        grid[(part == i) & ~surf] = pidx(ramp[0])

    # pass 5: edge lines where one shade of a plate meets the next, the way the sprite draws its creases: the
    # lighter side of an upward-facing crease takes the top shade, the darker side of a downward one the darkest.
    # (Pass 4 found edges from local fill and drew a line on every voxel stair step of the bevels.)
    ncg = np.zeros(occ.shape, np.float32)
    ncg[tuple(si.T)] = nrm[:, 2]
    lit = np.isin(part, [i for i, nm in enumerate(ORDER) if P[nm][1] in ("yellow", "grey")]) & surf
    hi_edge = np.zeros(occ.shape, bool)
    lo_edge = np.zeros(occ.shape, bool)
    for ax in range(3):
        for sgn in (1, -1):
            nbk = np.roll(kgrid, sgn, axis=ax)
            same = (np.roll(part, sgn, axis=ax) == part) & np.roll(surf, sgn, axis=ax)
            hi_edge |= lit & same & (nbk >= 0) & (nbk < kgrid) & (ncg > 0.25)
            lo_edge |= lit & same & (nbk > kgrid) & (ncg < -0.15)
    for i, name in enumerate(ORDER):
        ramp = RAMPS[P[name][1]]
        mine = part == i
        if P[name][1] in ("yellow", "grey"):
            kgrid[mine & hi_edge] = len(ramp) - 1
            kgrid[mine & lo_edge] = 0
        sel = mine & surf
        grid[sel] = np.array([pidx(h) for h in ramp])[kgrid[sel]]

    # seams: plate surface voxels touching another part's surface
    seam = np.zeros(occ.shape, bool)
    yellowish = np.isin(part, [ORDER.index(k) for k in ("rear", "pauldron", "hump", "head", "boot", "tail")])
    for ax in range(3):
        for sgn in (1, -1):
            nb = np.roll(part, sgn, axis=ax)
            nbs = np.roll(surf, sgn, axis=ax)
            seam |= surf & nbs & (nb >= 0) & (nb != part) & yellowish
    grid[seam] = pidx(RAMPS["seam"][0])

    # eyes: black socket and red eye with a glint, on the chamfered front corners of the head (e x 123-129)
    hd = part == ORDER.index("head")
    sock = hd & surf & (A >= 29) & (A <= 34.5) & (C >= 34) & (C <= 41) & (AB >= 10)
    grid[sock] = pidx(RAMPS["seam"][0])
    eye = hd & surf & (A >= 31) & (A <= 33.5) & (C >= 36) & (C <= 38.5) & (AB >= 10.5)
    grid[eye] = pidx(RAMPS["eye"][0])
    glint = eye & (C >= 37.5) & (A <= 32)
    grid[glint] = pidx(RAMPS["eye"][1])
    return views, occ, surf, grid, pal, sh


def main():
    views, occ, surf, grid, pal, sh = colour()

    # ---------------------------------------------------------------- reproject at the drawn pitch and score
    si = np.argwhere(surf)
    cols_rgb = np.array([[int(pal[k][j:j + 2], 16) for j in (0, 2, 4)] for k in grid[tuple(si.T)]])
    sub = np.array([[dx, dy, dz] for dx in (-0.3, 0.3) for dy in (-0.3, 0.3) for dz in (-0.3, 0.3)])
    pts = (si[:, None, :] + 0.5 + sub[None]).reshape(-1, 3)
    prgb = np.repeat(cols_rgb, len(sub), axis=0)
    pa, pb, pc = pts[:, 0] - OA, pts[:, 1] - OB, pts[:, 2]
    pr = np.radians(PITCH)
    ramp_of = {}
    for rn, hs in RAMPS.items():
        for h in hs:
            ramp_of[int(h, 16)] = rn
    scores, imgs = {}, {}
    for nm, v in views.items():
        f = np.radians(v["yaw"])
        x = pa * np.sin(f) - pb * np.cos(f)
        t = pa * np.cos(f) + pb * np.sin(f)
        row0 = 161 - (pc * np.cos(pr) - t * np.sin(pr))
        near = t * np.cos(pr) + pc * np.sin(pr)
        best = None
        for dy in np.arange(-4, 1.5, 1.0):
            row = np.floor(row0 + dy).astype(int)
            for dx in np.arange(-8, 8.5, 1.0):
                col = np.floor(v["axis"] + 0.5 + dx + x).astype(int)
                ok = (col >= 0) & (col < 192) & (row >= 0) & (row < 192)
                m = np.zeros((192, 192), bool)
                m[row[ok], col[ok]] = True
                iou = (m & v["mask"]).sum() / (m | v["mask"]).sum()
                if best is None or iou > best[0]:
                    best = (iou, dx, dy)
        row = np.floor(row0 + best[2]).astype(int)
        col = np.floor(v["axis"] + 0.5 + best[1] + x).astype(int)
        order = np.argsort(near)
        img = np.zeros((192, 192, 4), np.uint8)
        ok = (col >= 0) & (col < 192) & (row >= 0) & (row < 192)
        o = order[ok[order]]
        img[row[o], col[o], :3] = prgb[o]
        img[row[o], col[o], 3] = 255
        imgs[nm] = img
        both = (img[:, :, 3] > 0) & v["mask"]
        mk = (img[:, :, 0].astype(int) << 16) | (img[:, :, 1].astype(int) << 8) | img[:, :, 2].astype(int)
        colour = (mk[both] == v["key"][both]).mean()
        mat = np.mean([ramp_of.get(int(p), "?") == ramp_of.get(int(q), "?") for p, q in zip(mk[both], v["key"][both])])
        h_model = np.nonzero((img[:, :, 3] > 0).any(1))[0]
        h_view = np.nonzero(v["mask"].any(1))[0]
        scores[nm] = dict(silhouette_iou=round(float(best[0]), 3), colour_match=round(float(colour), 3),
                          material_match=round(float(mat), 3), axis_nudge=float(best[1]), row_nudge=float(best[2]),
                          height_px_model=int(h_model.max() - h_model.min() + 1),
                          height_px_view=int(h_view.max() - h_view.min() + 1))

    # sheet: views over the model drawn back at the views' pitch (crop 36-156 x 78-166, x3)
    cw, ch = 120, 88
    sheet = Image.new("RGBA", (5 * cw * 3 + 40, 2 * ch * 3 + 10), (110, 110, 118, 255))
    for i, nm in enumerate(DRAWN):
        for r, src in enumerate((views[nm]["rgba"], imgs[nm])):
            im = Image.fromarray(src).crop((36, 78, 156, 166)).resize((cw * 3, ch * 3), Image.NEAREST)
            sheet.alpha_composite(im, (i * (cw * 3 + 10), r * (ch * 3 + 10)))
    sheet.save(os.path.join(HERE, "reproject_rhino.png"))

    # ---------------------------------------------------------------- mesh and glb
    quads = vb.greedy_quads(occ, grid)
    pos, nor, uv, idx = [], [], [], []
    npal = 16
    for axis, sign, layer, u, v_, h, w, k in quads:
        other = [ax for ax in range(3) if ax != axis]
        dpl = layer + (1 if sign > 0 else 0)
        base = len(pos)
        nvec = [0.0, 0.0, 0.0]
        nvec[axis] = float(sign)
        for du, dv in ((0, 0), (h, 0), (h, w), (0, w)):
            p = [0.0, 0.0, 0.0]
            p[axis] = dpl
            p[other[0]] = u + du
            p[other[1]] = v_ + dv
            a_, b_, c_ = p[0] - OA, p[1] - OB, p[2]
            pos.append((-b_ * TEXEL, c_ * TEXEL, a_ * TEXEL))
            nor.append((-nvec[1], nvec[2], nvec[0]))
            uv.append(((k + 0.5) / npal, 0.5))
        tri = [(0, 1, 2), (0, 2, 3)]
        e1 = np.subtract(pos[base + 1], pos[base])
        e2 = np.subtract(pos[base + 2], pos[base])
        if np.dot(np.cross(e1, e2), nor[base]) < 0:
            tri = [(0, 2, 1), (0, 3, 2)]
        for tt in tri:
            idx.extend(base + j for j in tt)
    mesh = (np.array(pos, np.float32), np.array(nor, np.float32), np.array(uv, np.float32), np.array(idx, np.uint32))
    assert len(pal) <= npal, pal
    png, pim = vb.palette_png([tuple(int(h[j:j + 2], 16) for j in (0, 2, 4)) for h in pal], npal)
    vb.write_glb(os.path.join(HERE, "rhino_parts.glb"), mesh, png, "rhino_parts")
    pim.save(os.path.join(HERE, "rhino_palette.png"))

    lo, hi = mesh[0].min(0), mesh[0].max(0)
    rep = dict(pass_=PASS, pitch_deg=PITCH, texel_m=TEXEL, triangles=len(idx) // 3, voxels=int(occ.sum()),
               size_m=dict(width=round(float(hi[0] - lo[0]), 3), height=round(float(hi[1] - lo[1]), 3),
                           length=round(float(hi[2] - lo[2]), 3)),
               palette=pal, shares=sh, scores=scores)
    json.dump(rep, open(os.path.join(HERE, "rhino_report.json"), "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("triangles", "voxels", "size_m")}))
    for nm, s in scores.items():
        print(nm, s)


if __name__ == "__main__":
    main()
