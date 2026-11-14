"""Score drone model B against the factory's game-camera drawings (Claude, 3D test lane, 2026-11-04).

Inputs: views_cam30/s.png and se.png (96 x 96, bottom row 78, drawn for the 35 degree chase-cam view), the
approved views (drawn at about 9 degrees), and model B (part_build.colour()). Nothing here changes model B.

1. Pitch: at each pitch, carve the approved views at 9 degrees together with the two cam30 views (and se's mirror)
   at that pitch, each cam30 view nudged sideways and up/down to fit. The pitch where the joint solid explains
   most of every silhouette is the angle the cam30 drawing is consistent with.
2. Model B drawn at that pitch and at 35, against the drawings: silhouette IoU, exact colour, material, height.
Writes cam30_score.json and board_cam30_score.png.   Run: python cam30_score.py
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import part_build as pb
import voxel_build as vb

HERE = vb.HERE
A, B, C = vb.A, vb.B, vb.C
OFFS9 = {"se": -0.5, "se_m": 0.5, "e": 0.5, "e_m": -0.5, "ne": 1, "ne_m": -1}
LENS = {"5fd8ff", "d0f4ff", "f6fdff"}


def load_cam():
    out = {}
    for n, yaw in (("s", 0), ("se", 45)):
        a = np.array(Image.open(os.path.join(vb.TAKE, "views_cam30", n + ".png")).convert("RGBA"))
        m = a[:, :, 3] > 0
        xs = np.nonzero(m)[1]
        ax = (xs.min() + xs.max()) / 2
        out[n] = dict(yaw=yaw, rgba=a, mask=m, axis=ax)
        if n == "se":
            out["se_m"] = dict(yaw=315, rgba=a[:, ::-1].copy(), mask=m[:, ::-1].copy(), axis=95 - ax)
    return out


def proj(a, b, c, yaw, pitch, axis, dx, dy):
    f, p = np.radians(yaw), np.radians(pitch)
    x = a * np.sin(f) - b * np.cos(f)
    t = a * np.cos(f) + b * np.sin(f)
    col = np.floor(axis + 0.5 + dx + x).astype(int)
    row = np.floor(79 + dy - (c * np.cos(p) - t * np.sin(p))).astype(int)
    return col, row, t * np.cos(p) + c * np.sin(p)


def inside(mask, col, row):
    ok = (col >= 0) & (col < 96) & (row >= 0) & (row < 96)
    r = np.zeros(col.shape, bool)
    r[ok] = mask[row[ok], col[ok]]
    return r


def cover(col, row):
    m = np.zeros((96, 96), bool)
    ok = (col >= 0) & (col < 96) & (row >= 0) & (row < 96)
    m[row[ok], col[ok]] = True
    return m


def iou(m, v):
    return (m & v).sum() / max((m | v).sum(), 1)


def fit(a, b, c, v, pitch):
    best = (-1, 0, 0)
    for dy in np.arange(-24, 8.5, 1.0):
        for dx in np.arange(-5, 5.5, 0.5):
            col, row, _ = proj(a, b, c, v["yaw"], pitch, v["axis"], dx, dy)
            s = iou(cover(col, row), v["mask"])
            if s > best[0]:
                best = (s, dx, dy)
    return best


def joint(app, hull9, cam, pitch):
    """Approved hull (9 deg) cut further by the cam30 views at `pitch`; mean share of every silhouette explained."""
    k = hull9.ravel().copy()
    offs = {}
    for n, v in cam.items():
        _, dx, dy = fit(A[k], B[k], C[k], v, pitch)
        offs[n] = (dx, dy)
        col, row, _ = proj(A, B, C, v["yaw"], pitch, v["axis"], dx, dy)
        k &= inside(v["mask"], col, row)
    ex = {}
    for n, v in app.items():
        col, row, _ = vb.project(A[k], B[k], C[k], v["yaw"], 9, v["axis"], OFFS9.get(n, 0.0))
        ex[n] = (cover(col, row) & v["mask"]).sum() / v["mask"].sum()
    for n, v in cam.items():
        col, row, _ = proj(A[k], B[k], C[k], v["yaw"], pitch, v["axis"], *offs[n])
        ex["cam30_" + n] = (cover(col, row) & v["mask"]).sum() / v["mask"].sum()
    return float(np.mean(list(ex.values()))), {n: round(float(x), 3) for n, x in ex.items()}, offs


def draw(grid, surf, pal, v, pitch, dx, dy):
    si = np.argwhere(surf)
    sub = np.array([[x, y, z] for x in (-0.3, 0.3) for y in (-0.3, 0.3) for z in (-0.3, 0.3)])
    pts = (si[:, None, :] + 0.5 + sub[None]).reshape(-1, 3)
    cols = np.repeat(np.array(pal)[grid[tuple(si.T)]], len(sub), axis=0)
    col, row, near = proj(pts[:, 0] - 48, pts[:, 1] - 48, pts[:, 2], v["yaw"], pitch, v["axis"], dx, dy)
    ok = (col >= 0) & (col < 96) & (row >= 0) & (row < 96)
    o = np.argsort(near)
    o = o[ok[o]]
    img = np.zeros((96, 96, 4), np.uint8)
    img[row[o], col[o], :3] = cols[o]
    img[row[o], col[o], 3] = 255
    return img


def hexes(img):
    m = img[:, :, 3] > 0
    h = np.array(["%02x%02x%02x" % tuple(p) for p in img[:, :, :3].reshape(-1, 3)]).reshape(96, 96)
    return np.where(m, h, "")


def score(img, v):
    hm, hv = hexes(img), hexes(v["rgba"])
    mm, mv = img[:, :, 3] > 0, v["mask"]
    both = mm & mv
    ramp_of = {h: r for r, hs in vb.RAMPS.items() for h in hs}
    ys_m, ys_v = np.nonzero(mm.any(1))[0], np.nonzero(mv.any(1))[0]
    xs_m, xs_v = np.nonzero(mm.any(0))[0], np.nonzero(mv.any(0))[0]
    blue_top = lambda h, m: int(np.isin(h, vb.RAMPS["blue"]).any(1).nonzero()[0].min())
    return dict(silhouette_iou=round(float(iou(mm, mv)), 3),
                colour_match=round(float((hm[both] == hv[both]).mean()), 3),
                material_match=round(float(np.mean([ramp_of.get(a, a) == ramp_of.get(b, b)
                                                    for a, b in zip(hm[both], hv[both])])), 3),
                height_px=[int(np.ptp(ys_m) + 1), int(np.ptp(ys_v) + 1)], width_px=[int(np.ptp(xs_m) + 1), int(np.ptp(xs_v) + 1)],
                lens_px=[int(np.isin(hm, list(LENS)).sum()), int(np.isin(hv, list(LENS)).sum())],
                blue_shell_px=[int(np.isin(hm, vb.RAMPS["blue"]).sum()), int(np.isin(hv, vb.RAMPS["blue"]).sum())],
                shell_top_row=[blue_top(hm, mm), blue_top(hv, mv)], bottom_row=[int(ys_m.max()), int(ys_v.max())])


def main():
    app = vb.load_views("views")
    cam = load_cam()
    hull9 = vb.carve(app, 9, OFFS9)
    scan = []
    for p in np.arange(9, 47.5, 2.5):
        mean, ex, offs = joint(app, hull9, cam, p)
        scan.append(dict(pitch=float(p), explained=round(mean, 4), per_view=ex))
        print(p, round(mean, 4), ex["cam30_s"], ex["cam30_se"], ex["s"], ex["e"], flush=True)
    best = max(scan, key=lambda r: r["explained"])

    grid, surf, pal = pb.colour()
    pal = [tuple(int(x) for x in c) for c in pal]
    rows, res = {}, {}
    for p in (best["pitch"], 35.0):
        for n in ("s", "se"):
            v = cam[n]
            si = np.argwhere(surf)
            _, dx, dy = fit(si[:, 0] - 48 + 0.5, si[:, 1] - 48 + 0.5, si[:, 2] + 0.5, v, p)
            img = draw(grid, surf, pal, v, p, dx, dy)
            rows[(p, n)] = img
            res[f"B_at_{p:g}deg_{n}"] = dict(score(img, v), nudge=[float(dx), float(dy)])
    for k, r in res.items():
        print(k, r)
    json.dump(dict(pitch_scan=scan, best_pitch=best["pitch"], model_B=res,
                   note="pairs are [model B, cam30 drawing]; rows count down from the top of the 96 x 96 canvas"),
              open(os.path.join(HERE, "cam30_score.json"), "w"), indent=1)

    # board: per view, the approved drawing, the cam30 drawing, B at the fitted pitch, B at 35, B in Godot
    S, W = 3, 96 * 3
    try:
        font = ImageFont.load_default(size=16)
    except TypeError:
        font = ImageFont.load_default()
    labels = ["approved (about 9 deg)", "cam30 drawing", "B drawn at 35 deg", "B in Godot, chase cam",
              "pass 4 in Godot"]
    board = Image.new("RGBA", (W * 5 + 40, 30 + (W + 10) * 2), (34, 34, 40, 255))
    d = ImageDraw.Draw(board)
    for i, t in enumerate(labels):
        d.text((i * (W + 10) + 6, 8), t, fill=(235, 235, 240), font=font)
    for r, n in enumerate(("s", "se")):
        y = 30 + r * (W + 10)
        godot = Image.open(os.path.join(HERE, "godot_shots", f"parts_{n}.png")).convert("RGBA")
        cells = [app[n]["rgba"], cam[n]["rgba"], rows[(35.0, n)]]
        for i, src in enumerate(cells):
            bg = Image.new("RGBA", (W, W), (110, 110, 118, 255))
            bg.alpha_composite(Image.fromarray(src).resize((W, W), Image.NEAREST))
            board.alpha_composite(bg, (i * (W + 10), y))
        g = godot.crop((16, 0, 112, 96)).resize((W, W), Image.NEAREST)
        board.alpha_composite(g, (3 * (W + 10), y))
        old = Image.open(os.path.join(HERE, "_pass4", "godot_shots", f"parts_{n}.png")).convert("RGBA")
        board.alpha_composite(old.crop((16, 0, 112, 96)).resize((W, W), Image.NEAREST), (4 * (W + 10), y))
    board.convert("RGB").save(os.path.join(HERE, "board_cam30_score.png"))


if __name__ == "__main__":
    main()
