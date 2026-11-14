"""Part-built voxel drone, model B (Claude, 3D test lane, 2026-11-04; passes 2 and 3 the same day).

The silhouette carve (voxel_build.py) gets the outline but not the parts, so this builds the drone from simple
solids measured off the approved south and east views, one voxel per texel (0.016 m):
dome shell, hull, brow visor, round lens in a dark socket, twin barrels, two pods with blue caps and glow rings,
thruster nozzle, back plate with vents. Each part gets a material ramp from the prompt sheet. Its shades are cut
from one light above so that the part shows the same share of each shade as the drawn views do (measured per
part on the s, e and n views, pass 2). Where two parts meet, the outer voxel takes the seam colour 141218
(the sprite's overlap lines). The dome is shaded in flat facets, like the drawn shell.

Measurements (texels; a forward, b to the drone's right, c up from the nozzle bottom), read from the views and
corrected for the 9 degree drawing angle (a point 18 texels forward sits about 3 rows lower in the s view):
  nozzle   s rows 72-78, glow cols 41-56 at row 76; e cols 35-56 for the collar
  hull     s cols 29-66, rows 46-72; e back at col 19, face at col 59
  pods     s cols 15-28 and 67-80 (r 7.5, b +-27); e centre col 37 (a -7); cap rows 49-57, band 57-64,
           foot 64-66, glow 67-69 (r 5)
  dome     s top row 33, 35 wide at row 41, 43 wide at row 46; e back col 18, front edge a +6 at c 39
  lens     s cols 41-56, rows 48-62 (r 8, centre c 27); e bulges to col 68
  barrels  s bores at cols 41-47 and 50-56; e rows 61-71 (centre c 14.5), cols 58-74
  visor    e rows 39-44 reach col 70 (a +24). Pass 2 cuts it to a +15 so the lens is not hidden from the
           30 degree chase camera (a deliberate change from the e view).
Pass 2 shade shares, from the views: steel parts 5c6170 ~25%, 8a8f9c ~45%, b8bcc6 ~15%, e2e4ea none;
face 50% charcoal and seams; dome 3a8cff ~49%, 2258c8 ~25%, 9ad0ff ~23%; pod caps all four blues.
Run: python part_build.py  (after voxel_build.py, whose mesh and glb writers it reuses)
"""
import json
import os

import numpy as np
from scipy import ndimage

import voxel_build as vb

HERE = vb.HERE
N, NC = vb.N, vb.NC
I, J, K = np.meshgrid(np.arange(N), np.arange(N), np.arange(NC), indexing="ij")
A = I - 48 + 0.5
B = J - 48 + 0.5
C = K + 0.5

part = np.zeros((N, N, NC), np.int8)  # 0 empty; later parts overwrite earlier ones
MAT = {}  # part id -> material ramp name

# shade shares per part, darkest first, from the drawn views (pass 2)
STEEL = {"5c6170": 0.3, "8a8f9c": 0.5, "b8bcc6": 0.2}
STEEL_DARK = {"5c6170": 0.55, "8a8f9c": 0.4, "b8bcc6": 0.05}
CHAR = {"211e27": 0.45, "3d3a44": 0.55}
SHARES = {
    1: CHAR,  # hull
    2: STEEL_DARK,  # cheek plates
    3: CHAR,  # nozzle collar
    5: {"14306e": 0.05, "2258c8": 0.3, "3a8cff": 0.5, "9ad0ff": 0.15},  # dome (pass 3: the top shows more from 30 deg)
    6: STEEL,  # visor
    9: STEEL,  # barrels
    11: CHAR,  # barrel bands
    12: {"5c6170": 0.3, "8a8f9c": 0.45, "b8bcc6": 0.25},  # pod bands
    13: {"14306e": 0.2, "2258c8": 0.3, "3a8cff": 0.25, "9ad0ff": 0.25},  # pod caps
    14: CHAR,  # pod feet
    17: STEEL_DARK,  # back plate
}


def put(mask, pid, mat):
    part[mask] = pid
    MAT[pid] = mat


def ellipsoid(ca, cb, cc, ra, rb, rc):
    return ((A - ca) / ra) ** 2 + ((B - cb) / rb) ** 2 + ((C - cc) / rc) ** 2 <= 1.0


def rounded_box(a0, a1, b0, b1, c0, c1, r):
    qa = np.maximum(np.maximum(a0 + r - A, A - (a1 - r)), 0)
    qb = np.maximum(np.maximum(b0 + r - B, B - (b1 - r)), 0)
    qc = np.maximum(np.maximum(c0 + r - C, C - (c1 - r)), 0)
    inside = (A >= a0) & (A <= a1) & (B >= b0) & (B <= b1) & (C >= c0) & (C <= c1)
    return inside & (qa ** 2 + qb ** 2 + qc ** 2 <= r * r)


def vcyl(ca, cb, r, c0, c1):
    return ((A - ca) ** 2 + (B - cb) ** 2 <= r * r) & (C >= c0) & (C <= c1)


def fcyl(cb, cc, r, a0, a1):  # cylinder along the forward axis
    return ((B - cb) ** 2 + (C - cc) ** 2 <= r * r) & (A >= a0) & (A <= a1)


# hull: rounded box, narrower toward the bottom
hull = rounded_box(-25, 13, -19, 19, 6, 34, 6) & (np.abs(B) <= 19 - np.clip(14 - C, 0, 8) * 0.6)
put(hull, 1, "charcoal")
# steel cheek plates on the lower front corners only (s view cols 29-37 and 58-66, rows 53-63)
put(hull & (A > 7) & (np.abs(B) > 11) & (C > 17) & (C < 28), 2, "steel")
# nozzle: charcoal collar, glow cone under it
put(vcyl(0, 0, 10.5, 3, 7) | vcyl(0, 0, 8.5, 6, 9), 3, "charcoal")
put((np.hypot(A, B) <= 4.5 + 1.4 * C) & (C <= 3.2) & (C >= 0), 4, "glow")
# dome shell (blue): ellipsoid cap; its front edge slopes back as it drops, down to c 24 at the back
dome = ellipsoid(-4, 0, 26, 25.4, 23.3, 21) & (C >= 24) & (A < -3 + (C - 32) * 1.4)  # pass 4 (refine_b.py): 2 taller, 6% wider
put(dome, 5, "blue")
# steel visor over the lens, narrower and shorter than pass 1
put(rounded_box(-3, 15, -10, 10, 33, 37.5, 2) & ~dome, 6, "steel")
# lens: dark socket ring on the face, glowing bulge that stands out past the visor
put(fcyl(0, 27, 10, 10, 15), 7, "seam")
put(ellipsoid(14, 0, 27, 8, 8, 8) & (A >= 13), 8, "glow")
# twin barrels under the lens, dark bores at the muzzle, a charcoal band round each
for sb in (-4.3, 4.3):
    put(fcyl(sb, 14.5, 3.8, 6, 26), 9, "steel")  # pass 4: 3 shorter, they hung like legs from the game camera
    put(fcyl(sb, 14.5, 1.9, 24, 27), 10, "seam")
    put(fcyl(sb, 14.5, 4.1, 17, 19), 11, "charcoal")
# pods: steel band, a flatter blue cap no wider than the band, charcoal foot, glow ring under
for sb in (-27, 27):
    put(vcyl(-7, sb, 7.5, 14.5, 25), 12, "steel")  # pass 4: pods 1.5 higher
    put(ellipsoid(-7, sb, 24.5, 7.5, 7.5, 6.3) & (C >= 24.5), 13, "blue")  # pass 3: a lid, not a ball
    put(vcyl(-7, sb, 7.0, 12.5, 14.5), 14, "charcoal")
    put(vcyl(-7, sb, 5.5, 10, 12.5), 15, "glow")
# back plate: dark steel under the shell, two vent slots
put(rounded_box(-26.5, -18, -11, 11, 11, 24, 2.5) & ~dome, 17, "steel")
for cc in (15, 20):
    put(rounded_box(-27, -23, -7, 7, cc, cc + 2, 0.5) & (part > 0), 16, "seam")

occ = part > 0
LIGHT = np.array([0.2, 0.25, 0.95])
LIGHT /= np.linalg.norm(LIGHT)


def facet(nrm):
    """Snap normals to 8 sides and 4 tiers so the dome shades in flat planes, like the drawn shell."""
    az = np.round(np.arctan2(nrm[:, 1], nrm[:, 0]) / (np.pi / 4)) * (np.pi / 4)
    el = np.arcsin(np.clip(nrm[:, 2], -1, 1))
    el = np.select([el > np.radians(72), el > np.radians(52), el > np.radians(30)],
                   [np.pi / 2, np.radians(62), np.radians(41)], np.radians(15))
    return np.stack([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)], -1)


def colour():
    """Model B's coloured voxels: (grid of palette indices, surface mask, palette). Also used by cam30_score.py."""
    pal = vb.palette_of(vb.load_views("views"))
    hexp = ["%02x%02x%02x" % c for c in pal]
    lut = {h: i for i, h in enumerate(hexp)}
    pad = np.pad(occ, 1)
    surf = occ & ~(pad[2:, 1:-1, 1:-1] & pad[:-2, 1:-1, 1:-1] & pad[1:-1, 2:, 1:-1] & pad[1:-1, :-2, 1:-1]
                   & pad[1:-1, 1:-1, 2:] & pad[1:-1, 1:-1, :-2])
    si = np.argwhere(surf)
    pid = part[si[:, 0], si[:, 1], si[:, 2]]
    # each part lit from its own smooth surface, so neighbours never break up its shading bands
    nrm = np.zeros((len(si), 3))
    for p in np.unique(pid):
        blur = ndimage.gaussian_filter((part == p).astype(float), 2.2)
        sel = pid == p
        g = np.stack(np.gradient(blur), -1)[si[sel, 0], si[sel, 1], si[sel, 2]]
        nrm[sel] = -g / (np.linalg.norm(g, axis=1, keepdims=True) + 1e-9)
    nrm[pid == 5] = facet(nrm[pid == 5])
    lit = nrm @ LIGHT
    # seam: a surface voxel next to a later part (the overlap line), glow parts excepted
    seam = np.zeros(len(si), bool)
    pp = np.pad(part, 1)
    isglow = np.array([MAT.get(int(x), "") == "glow" for x in range(32)])
    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        nb = pp[si[:, 0] + 1 + d[0], si[:, 1] + 1 + d[1], si[:, 2] + 1 + d[2]]
        seam |= (nb > pid) & ~isglow[nb] & ~isglow[pid]
    out = np.zeros(len(si), int)
    for p in np.unique(pid):
        sel = pid == p
        mat = MAT[int(p)]
        if p in SHARES:
            shades = list(SHARES[p])
            share = np.array([SHARES[p][h] for h in shades])
            cuts = np.quantile(lit[sel], np.cumsum(share / share.sum())[:-1])
            out[sel] = [lut[shades[int(np.searchsorted(cuts, x))]] for x in lit[sel]]
        elif mat == "glow":
            out[sel] = np.where(lit[sel] < 0.2, lut["5fd8ff"], lut["d0f4ff"])
        else:
            out[sel] = lut[vb.RAMPS[mat][0]]
    out[seam] = lut["141218"]
    # lens: bright centre, white glint at upper left, cyan rim, like the drawn lens
    lp = pid == 8
    lb, lc = si[:, 1] - 48 + 0.5, si[:, 2] + 0.5
    r = np.hypot(lb, lc - 27)
    out[lp] = lut["5fd8ff"]
    out[lp & (r < 5.5)] = lut["d0f4ff"]
    out[lp & (np.hypot(lb + 2, lc - 29.5) < 1.8)] = lut["f6fdff"]
    grid = np.full(occ.shape, -1, int)
    grid[si[:, 0], si[:, 1], si[:, 2]] = out
    # despeckle: inside each ramp, a voxel takes its 3x3x3 neighbours' majority shade when it clearly wins
    for ramp in (vb.RAMPS["blue"], vb.RAMPS["steel"], vb.RAMPS["charcoal"]):
        ids = [lut[h] for h in ramp]
        cnt = np.stack([ndimage.uniform_filter((grid == k).astype(float), 3, mode="constant") for k in ids], -1)
        inr = np.isin(grid, ids)
        own = np.zeros(grid.shape)
        for j, k in enumerate(ids):
            own[grid == k] = cnt[..., j][grid == k]
        win = np.array(ids)[cnt.argmax(-1)]
        grid = np.where(inr & (cnt.max(-1) > own + 2.5 / 27), win, grid)
    return grid, surf, pal


def main():
    grid, surf, pal = colour()
    quads = vb.greedy_quads(occ, grid)
    mesh = vb.quads_to_mesh(quads, 16)
    red_pal = json.load(open(os.path.join(HERE, "voxel_report.json")))["palette_red"]
    for team, cols in (("blue", pal), ("red", [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in red_pal])):
        png, _ = vb.palette_png(cols, 16)
        vb.write_glb(os.path.join(HERE, f"drone_parts_{team}.glb"), mesh, png, f"minion_drone_parts_{team}")

    views = vb.load_views("views")
    offs = {"se": -0.5, "se_m": 0.5, "e": 0.5, "e_m": -0.5, "ne": 1, "ne_m": -1}
    imgs, scores = vb.reproject(views, grid, surf, 9, offs, pal)
    from PIL import Image
    S = 4
    sheet = Image.new("RGBA", (96 * S * 5, 96 * S * 2), (110, 110, 118, 255))
    for i, n in enumerate(vb.DRAWN):
        sheet.alpha_composite(Image.fromarray(views[n]["rgba"]).resize((96 * S, 96 * S), Image.NEAREST), (i * 96 * S, 0))
        sheet.alpha_composite(Image.fromarray(imgs[n]).resize((96 * S, 96 * S), Image.NEAREST), (i * 96 * S, 96 * S))
    sheet.save(os.path.join(HERE, "reproject_parts.png"))
    rep = {"pass": 4, "voxels_solid": int(occ.sum()), "voxels_surface": int(surf.sum()), "quads": len(quads),
           "triangles": int(len(mesh[3]) // 3),
           "size_m": [round(float(x), 3) for x in (mesh[0].max(0) - mesh[0].min(0))],
           "reproject_at_drawn_pitch": scores, "material_match_at_drawn_pitch": vb.material_match(views, imgs)}
    json.dump(rep, open(os.path.join(HERE, "parts_report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
