"""Voxel drone from the approved minion views (Claude, 3D test lane, 2026-11-04).

What it does, in order:
1. Carves a solid from the five drawn views (s, se, e, ne, n) and their mirrors, seen at the pitch the views
   were drawn at (measured by voxel_measure in this file: the pitch where the carved solid explains the most of
   every silhouette). One voxel per sprite texel, 0.016 m (S size class).
2. Colours each surface voxel from the view pixels that see it, by a vote weighted by how squarely each view
   faces that voxel. Only the sprite's own palette colours are used.
3. Drops the interior and writes merged faces (greedy meshing) into .glb files that use a 16 x 1 palette
   texture, nearest filtered and unlit, so the painted shading of the sprite is the model's shading.
   Blue and red differ only in the palette texture.
4. Re-projects the model at the drawn pitch and scores it against each drawn view (silhouette IoU and
   colour match), and saves reproject.png.

Run: python voxel_build.py   (numpy, scipy, Pillow). Writes into this folder.
"""
import io
import json
import os
import struct

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
TAKE = os.path.dirname(HERE)
DRAWN = {"s": 0, "se": 45, "e": 90, "ne": 135, "n": 180}  # yaw: 0 = facing the viewer, 90 = facing screen right
TEXEL = 0.016  # metres per texel, S size class
HOVER = 10  # rows between the drone's bottom (row 78) and the ground row (88)
N = 96
NC = 64
GLOW = lambda a: (a[..., 2].astype(int) > 200) & (a[..., 1].astype(int) > 180)


def load_views(folder):
    views = {}
    for n, yaw in DRAWN.items():
        a = np.array(Image.open(os.path.join(TAKE, folder, n + ".png")).convert("RGBA"))
        m = a[:, :, 3] > 0
        gy, gx = np.nonzero((GLOW(a) & m)[74:, :])
        ax = gx.mean()  # the thruster nozzle under the drone marks its vertical axis in every view
        views[n] = dict(yaw=yaw, rgba=a, mask=m, axis=ax)
        if n not in ("s", "n"):
            views[n + "_m"] = dict(yaw=360 - yaw, rgba=a[:, ::-1].copy(), mask=m[:, ::-1].copy(), axis=95 - ax)
    return views


# voxel centres in the drone's frame: a forward, b to its right, c up (texels)
IA, IB, IC = np.meshgrid(np.arange(N), np.arange(N), np.arange(NC), indexing="ij")
A = IA.ravel() - 48 + 0.5
B = IB.ravel() - 48 + 0.5
C = IC.ravel() + 0.5


def project(a, b, c, yaw, pitch, axis, dx=0.0):
    f, p = np.radians(yaw), np.radians(pitch)
    x = a * np.sin(f) - b * np.cos(f)
    t = a * np.cos(f) + b * np.sin(f)  # toward the viewer
    col = np.floor(axis + 0.5 + dx + x).astype(int)
    row = np.floor(79 - (c * np.cos(p) - t * np.sin(p))).astype(int)
    near = t * np.cos(p) + c * np.sin(p)
    return col, row, near


def carve(views, pitch, offs):
    keep = np.ones(A.size, bool)
    for n, v in views.items():
        col, row, _ = project(A, B, C, v["yaw"], pitch, v["axis"], offs.get(n, 0.0))
        ok = (col >= 0) & (col < N) & (row >= 0) & (row < N)
        inside = np.zeros(A.size, bool)
        inside[ok] = v["mask"][row[ok], col[ok]]
        keep &= inside
    return keep.reshape(N, N, NC)


def explained(views, occ, pitch, offs):
    k = occ.ravel()
    out = {}
    for n, v in views.items():
        col, row, _ = project(A[k], B[k], C[k], v["yaw"], pitch, v["axis"], offs.get(n, 0.0))
        cov = np.zeros((N, N), bool)
        cov[row, col] = True
        out[n] = float((cov & v["mask"]).sum() / v["mask"].sum())
    return out


def measure_pitch(views):
    """Pitch where the carved solid explains the most of every silhouette, with per-view axis nudges."""
    best = None
    for p in range(4, 17):
        offs = {}
        for _ in range(2):
            for n in ("se", "e", "ne"):
                cands = []
                for dx in (-1.5, -1, -0.5, 0, 0.5, 1, 1.5):
                    o = dict(offs, **{n: dx, n + "_m": -dx})
                    cands.append((np.mean(list(explained(views, carve(views, p, o), p, o).values())), dx))
                s, dx = max(cands)
                offs[n], offs[n + "_m"] = dx, -dx
        s = np.mean(list(explained(views, carve(views, p, offs), p, offs).values()))
        if best is None or s > best[0]:
            best = (s, p, offs)
    return best


def palette_of(views):
    cols = set()
    for v in views.values():
        px = v["rgba"][v["mask"]][:, :3]
        cols.update(map(tuple, np.unique(px, axis=0)))
    return sorted((tuple(int(x) for x in c) for c in cols), key=lambda c: sum(c))


def colour_voxels(views, occ, pitch, offs, pal):
    """Vote each surface voxel's palette index from the views that see it, weighted by facing."""
    lut = {c: i for i, c in enumerate(pal)}
    pad = np.pad(occ, 1)
    surf = occ & ~(pad[2:, 1:-1, 1:-1] & pad[:-2, 1:-1, 1:-1] & pad[1:-1, 2:, 1:-1] & pad[1:-1, :-2, 1:-1]
                   & pad[1:-1, 1:-1, 2:] & pad[1:-1, 1:-1, :-2])
    si = np.argwhere(surf)
    a, b, c = si[:, 0] - 48 + 0.5, si[:, 1] - 48 + 0.5, si[:, 2] + 0.5
    blur = ndimage.gaussian_filter(occ.astype(float), 1.6)
    g = np.stack(np.gradient(blur), -1)[si[:, 0], si[:, 1], si[:, 2]]
    nrm = -g / (np.linalg.norm(g, axis=1, keepdims=True) + 1e-9)
    votes = np.zeros((len(si), len(pal)))
    pr = np.radians(pitch)
    for n, v in views.items():
        col, row, near = project(a, b, c, v["yaw"], pitch, v["axis"], offs.get(n, 0.0))
        zb = np.full((N, N), -1e9)
        np.maximum.at(zb, (row, col), near)
        vis = near >= zb[row, col] - 1.2
        f = np.radians(v["yaw"])
        face = nrm @ np.array([np.cos(f) * np.cos(pr), np.sin(f) * np.cos(pr), np.sin(pr)])
        use = vis & (face > 0.05) & v["mask"][row, col]
        idx = np.array([lut[tuple(p)] for p in v["rgba"][row[use], col[use], :3]])
        np.add.at(votes, (np.nonzero(use)[0], idx), face[use] ** 2)
    cidx = np.where(votes.sum(1) > 0, votes.argmax(1), -1)
    # voxels no view saw (underside pockets): copy the nearest coloured surface voxel
    unseen = cidx < 0
    if unseen.any():
        from scipy.spatial import cKDTree
        tree = cKDTree(si[~unseen])
        _, j = tree.query(si[unseen])
        cidx[unseen] = cidx[~unseen][j]
    grid = np.full(occ.shape, -1, int)
    grid[si[:, 0], si[:, 1], si[:, 2]] = cidx
    return grid, surf, int(unseen.sum())


# material ramps from the prompt sheet, darkest first; glow keeps its voted shade
RAMPS = {"blue": ["14306e", "2258c8", "3a8cff", "9ad0ff"], "steel": ["5c6170", "8a8f9c", "b8bcc6", "e2e4ea"],
         "charcoal": ["211e27", "3d3a44"], "seam": ["141218"], "glow": ["5fd8ff", "d0f4ff", "f6fdff"]}


def colour_banded(views, occ, pitch, offs, pal):
    """Clean version of colour_voxels: the views vote the MATERIAL of each surface voxel (blue shell, steel,
    charcoal, seam, glow), a mode filter tidies the material map, and the shade inside each material ramp comes
    from one light direction fitted to the voted shades, banded so each ramp keeps the share of shades the
    drawn views give it. Returns the grid and the fitted light."""
    hexp = ["%02x%02x%02x" % c for c in pal]
    cls_of = {h: k for k, ramp in RAMPS.items() for h in ramp}
    names = list(RAMPS)
    vgrid, surf, unseen = colour_voxels(views, occ, pitch, offs, pal)
    si = np.argwhere(surf)
    voted = vgrid[si[:, 0], si[:, 1], si[:, 2]]
    cls = np.array([names.index(cls_of[hexp[i]]) for i in voted])
    cgrid = np.full(occ.shape, -1, int)
    cgrid[si[:, 0], si[:, 1], si[:, 2]] = cls
    for _ in range(2):  # 3 x 3 x 3 majority over the surface, so thin mixed specks join their neighbours
        cnt = np.stack([ndimage.uniform_filter((cgrid == k).astype(float), 3, mode="constant") for k in range(len(names))], -1)
        best = cnt.argmax(-1)
        own = np.take_along_axis(cnt, np.clip(cgrid, 0, None)[..., None], -1)[..., 0]
        cgrid = np.where(surf & (cnt.max(-1) > own + 1.5 / 27), best, cgrid)
    cls = cgrid[si[:, 0], si[:, 1], si[:, 2]]
    blur = ndimage.gaussian_filter(occ.astype(float), 2.0)
    g = np.stack(np.gradient(blur), -1)[si[:, 0], si[:, 1], si[:, 2]]
    nrm = -g / (np.linalg.norm(g, axis=1, keepdims=True) + 1e-9)
    # light: least squares of the voted shade rank (0 dark .. 1 bright) on the normal, over the 4-shade ramps
    rows, ys = [], []
    for k in ("blue", "steel"):
        ramp = RAMPS[k]
        sel = np.array([hexp[i] in ramp for i in voted])
        rank = np.array([ramp.index(hexp[i]) / 3 if hexp[i] in ramp else 0 for i in voted])
        rows.append(nrm[sel])
        ys.append(rank[sel])
    X = np.concatenate(rows)
    coef, *_ = np.linalg.lstsq(np.c_[X, np.ones(len(X))], np.concatenate(ys), rcond=None)
    light = coef[:3] / np.linalg.norm(coef[:3])
    lit = nrm @ light
    lut = {h: i for i, h in enumerate(hexp)}
    out = voted.copy()
    for k, ramp in RAMPS.items():
        m = cls == names.index(k)
        if not m.any():
            continue
        if k == "glow":
            ok = m & np.array([hexp[i] in ramp for i in voted])
            out[m & ~ok] = lut[ramp[0]]
            continue
        # shade shares as voted inside this material, then cut the lit term at those quantiles
        shares = np.array([np.sum(m & (voted == lut[h])) for h in ramp], float) + 1e-6
        cuts = np.quantile(lit[m], np.cumsum(shares / shares.sum())[:-1]) if len(ramp) > 1 else []
        out[m] = [lut[ramp[int(np.searchsorted(cuts, x))]] for x in lit[m]]
    grid = np.full(occ.shape, -1, int)
    grid[si[:, 0], si[:, 1], si[:, 2]] = out
    return grid, surf, unseen, light, vgrid


def greedy_quads(occ, grid):
    """Merged rectangles of same-colour exposed faces. Returns list of (axis, sign, layer, u0, v0, du, dv, colour)."""
    quads = []
    pad = np.pad(occ, 1)
    for axis in range(3):
        for sign in (1, -1):
            sl = [slice(1, -1)] * 3
            sl[axis] = slice(2, None) if sign > 0 else slice(0, -2)
            exposed = occ & ~pad[tuple(sl)]
            col = np.where(exposed, grid, -1)
            col = np.moveaxis(col, axis, 0)
            for layer in range(col.shape[0]):
                m = col[layer].copy()
                if (m < 0).all():
                    continue
                used = np.zeros(m.shape, bool)
                for u, v in np.argwhere(m >= 0):
                    if used[u, v]:
                        continue
                    k = m[u, v]
                    w = 1
                    while v + w < m.shape[1] and m[u, v + w] == k and not used[u, v + w]:
                        w += 1
                    h = 1
                    while u + h < m.shape[0] and (m[u + h, v:v + w] == k).all() and not used[u + h, v:v + w].any():
                        h += 1
                    used[u:u + h, v:v + w] = True
                    quads.append((axis, sign, layer, u, v, h, w, k))
    return quads


def quads_to_mesh(quads, npal):
    pos, nor, uv, idx = [], [], [], []
    for axis, sign, layer, u, v, h, w, k in quads:
        other = [ax for ax in range(3) if ax != axis]  # moveaxis keeps the other two in order
        d = layer + (1 if sign > 0 else 0)
        corners = []
        for du, dv in ((0, 0), (h, 0), (h, w), (0, w)):
            p = [0.0, 0.0, 0.0]
            p[axis] = d
            p[other[0]] = u + du
            p[other[1]] = v + dv
            corners.append(p)
        nvec = [0.0, 0.0, 0.0]
        nvec[axis] = float(sign)
        base = len(pos)
        for p in corners:
            # grid index (ia, ib, ic) -> glTF metres: x = -(b) right is -X, y = up (+hover), z = forward
            a_, b_, c_ = p[0] - 48, p[1] - 48, p[2]
            pos.append((-b_ * TEXEL, (c_ + HOVER) * TEXEL, a_ * TEXEL))
            nor.append((-nvec[1], nvec[2], nvec[0]))
            uv.append(((k + 0.5) / npal, 0.5))
        # winding: counter-clockwise seen from outside, after the handedness flip of x
        tri = [(0, 1, 2), (0, 2, 3)]
        e1 = np.subtract(pos[base + 1], pos[base])
        e2 = np.subtract(pos[base + 2], pos[base])
        if np.dot(np.cross(e1, e2), nor[base]) < 0:
            tri = [(0, 2, 1), (0, 3, 2)]
        for t in tri:
            idx.extend(base + i for i in t)
    return (np.array(pos, np.float32), np.array(nor, np.float32), np.array(uv, np.float32),
            np.array(idx, np.uint32))


def write_glb(path, mesh, pal_png, name):
    pos, nor, uv, idx = mesh
    blobs = [pos.tobytes(), nor.tobytes(), uv.tobytes(), idx.tobytes(), pal_png]
    views, off, bin_ = [], 0, b""
    for i, bl in enumerate(blobs):
        while len(bin_) % 4:
            bin_ += b"\0"
        off = len(bin_)
        bv = {"buffer": 0, "byteOffset": off, "byteLength": len(bl)}
        if i < 3:
            bv["target"] = 34962
        elif i == 3:
            bv["target"] = 34963
        views.append(bv)
        bin_ += bl
    while len(bin_) % 4:
        bin_ += b"\0"
    gl = {
        "asset": {"version": "2.0", "generator": "voxel_build.py (minion drone 3D test)"},
        "extensionsUsed": ["KHR_materials_unlit"],
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"name": name, "mesh": 0}],
        "meshes": [{"name": name, "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
                                                  "indices": 3, "material": 0}]}],
        "materials": [{"name": name + "_palette", "pbrMetallicRoughness": {
            "baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 1.0},
            "extensions": {"KHR_materials_unlit": {}}}],
        "textures": [{"source": 0, "sampler": 0}],
        "samplers": [{"magFilter": 9728, "minFilter": 9728, "wrapS": 33071, "wrapT": 33071}],
        "images": [{"bufferView": 4, "mimeType": "image/png"}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3",
             "min": pos.min(0).tolist(), "max": pos.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(nor), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(uv), "type": "VEC2"},
            {"bufferView": 3, "componentType": 5125, "count": len(idx), "type": "SCALAR"}],
        "bufferViews": views,
        "buffers": [{"byteLength": len(bin_)}],
    }
    js = json.dumps(gl, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_)))
        fh.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        fh.write(struct.pack("<II", len(bin_), 0x004E4942) + bin_)


def palette_png(cols, npal):
    im = Image.new("RGBA", (npal, 1), (255, 0, 255, 255))
    for i, c in enumerate(cols):
        im.putpixel((i, 0), tuple(c) + (255,))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue(), im


def reproject(views, grid, surf, pitch, offs, pal):
    """Model drawn back at the views' own pitch, orthographic, one voxel to one pixel."""
    si = np.argwhere(surf)
    a, b, c = si[:, 0] - 48 + 0.5, si[:, 1] - 48 + 0.5, si[:, 2] + 0.5
    cols = np.array(pal)[grid[si[:, 0], si[:, 1], si[:, 2]]]
    out, scores = {}, {}
    for n in DRAWN:
        v = views[n]
        col, row, near = project(a, b, c, v["yaw"], pitch, v["axis"], offs.get(n, 0.0))
        order = np.argsort(near)  # far first, near overwrites
        img = np.zeros((N, N, 4), np.uint8)
        img[row[order], col[order], :3] = cols[order]
        img[row[order], col[order], 3] = 255
        m = img[:, :, 3] > 0
        inter = m & v["mask"]
        same = inter & (img[:, :, :3] == v["rgba"][:, :, :3]).all(-1)
        scores[n] = {"silhouette_iou": round(float(inter.sum() / (m | v["mask"]).sum()), 3),
                     "colour_match": round(float(same.sum() / inter.sum()), 3)}
        out[n] = img
    return out, scores


def material_match(views, imgs):
    cls_of = {h: k for k, ramp in RAMPS.items() for h in ramp}
    out = {}
    for n in DRAWN:
        a, b = views[n]["rgba"], imgs[n]
        both = (a[:, :, 3] > 0) & (b[:, :, 3] > 0)
        ca = np.array([cls_of["%02x%02x%02x" % tuple(int(x) for x in p)] for p in a[both][:, :3]])
        cb = np.array([cls_of["%02x%02x%02x" % tuple(int(x) for x in p)] for p in b[both][:, :3]])
        out[n] = round(float((ca == cb).mean()), 3)
    return out


def main():
    import sys
    views = load_views("views")
    if "--fast" in sys.argv:  # reuse the measured result (python voxel_build.py measured it on 2026-11-04)
        score, pitch, offs = 0.9913, 9, {"se": -0.5, "se_m": 0.5, "e": 0.5, "e_m": -0.5, "ne": 1, "ne_m": -1}
    else:
        score, pitch, offs = measure_pitch(views)
    occ = carve(views, pitch, offs)
    # keep the largest connected piece only (loose voxels from silhouette noise)
    lab, nl = ndimage.label(occ)
    if nl > 1:
        sizes = ndimage.sum(occ, lab, range(1, nl + 1))
        occ = lab == (1 + int(np.argmax(sizes)))
    pal = palette_of(views)
    grid, surf, unseen, light, vgrid = colour_banded(views, occ, pitch, offs, pal)
    _, vote_scores = reproject(views, vgrid, surf, pitch, offs, pal)
    quads = greedy_quads(occ, grid)
    mesh = quads_to_mesh(quads, 16)

    # red team: same pixels in views_red give the colour swap
    red = load_views("views_red")
    swap = {}
    for n in DRAWN:
        bm, rm = views[n]["rgba"], red[n]["rgba"]
        both = views[n]["mask"] & red[n]["mask"]
        for pb, pr in zip(map(tuple, bm[both][:, :3]), map(tuple, rm[both][:, :3])):
            swap.setdefault(pb, {}).setdefault(pr, 0)
            swap[pb][pr] += 1
    red_pal = [max(swap[c].items(), key=lambda kv: kv[1])[0] if c in swap else c for c in pal]

    for team, cols in (("blue", pal), ("red", red_pal)):
        png, im = palette_png(cols, 16)
        im.save(os.path.join(HERE, f"drone_voxel_palette_{team}.png"))
        write_glb(os.path.join(HERE, f"drone_voxel_{team}.glb"), mesh, png, f"minion_drone_voxel_{team}")

    imgs, scores = reproject(views, grid, surf, pitch, offs, pal)
    S = 4
    sheet = Image.new("RGBA", (96 * S * 5, 96 * S * 2), (110, 110, 118, 255))
    for i, n in enumerate(DRAWN):
        sheet.alpha_composite(Image.fromarray(views[n]["rgba"]).resize((96 * S, 96 * S), Image.NEAREST), (i * 96 * S, 0))
        sheet.alpha_composite(Image.fromarray(imgs[n]).resize((96 * S, 96 * S), Image.NEAREST), (i * 96 * S, 96 * S))
    sheet.save(os.path.join(HERE, "reproject.png"))
    for n in DRAWN:
        Image.fromarray(imgs[n]).save(os.path.join(HERE, f"_reproject_{n}.png"))

    report = {
        "measured_pitch_deg": pitch, "mean_silhouette_explained": round(float(score), 4),
        "axis_nudges_px": {k: v for k, v in offs.items() if not k.endswith("_m")},
        "voxels_solid": int(occ.sum()), "voxels_surface": int(surf.sum()), "voxels_unseen_filled": unseen,
        "quads": len(quads), "triangles": int(len(mesh[3]) // 3), "vertices": int(len(mesh[0])),
        "size_m": [round(float(x), 3) for x in (mesh[0].max(0) - mesh[0].min(0))],
        "palette": ["%02x%02x%02x" % c for c in pal], "palette_red": ["%02x%02x%02x" % c for c in red_pal],
        "fitted_light_dir_drone_frame_fwd_right_up": [round(float(x), 3) for x in light],
        "reproject_at_drawn_pitch": scores,
        "reproject_raw_vote_before_banding": vote_scores,
        "material_match_at_drawn_pitch": material_match(views, imgs),
    }
    with open(os.path.join(HERE, "voxel_report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
