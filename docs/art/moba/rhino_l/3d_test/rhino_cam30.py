"""Rhino against the factory's game-camera drawing (Claude, 3D test lane, 2026-11-04).

Inputs: take-a/views_cam30 (s, se, e, ne, n; 192 canvas, lowest foot on row 160, 0.020 m per texel), the approved
views (take-a/views, drawn at about 6 degrees), and the part-built model (rhino_build.py).

  python rhino_cam30.py scan            1. the pitch each cam30 view was drawn at: the approved hull (6 degrees) cut by
                                           one cam30 view at a time at each pitch, nudged to fit; the pitch where the
                                           joint solid explains most of every silhouette is that view's angle.
  python rhino_cam30.py score LABEL     2. the current model (rhino_build.SHAPE) drawn at each view's pitch and at 34
                                           degrees, against the drawing; add "board" to also write the board.
  python rhino_cam30.py search W        3. coordinate search of the top-shape numbers (rear deck, hump, shoulder plates,
                                           head) against both targets, W on the cam30 views (e left out: the factory
                                           marks its camera check failed), 1 - W on the approved views.
Writes rhino_cam30.json (and board_rhino_cam30.png).
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

import rhino_build as rb

HERE = rb.HERE
TAKE = os.path.join(HERE, "..", "take-a")
JSON = os.path.join(HERE, "rhino_cam30.json")
A, B, C = rb.A, rb.B, rb.C
APP = {"s": 0, "se": 45, "e": 90, "ne": 135, "n": 180, "nw": 225, "w": 270, "sw": 315}
CAM = {"s": 0, "se": 45, "e": 90, "ne": 135, "n": 180}
PAD = 64
G = 192 + 2 * PAD
SUB = np.array([[x, y, z] for x in (-0.3, 0.3) for y in (-0.3, 0.3) for z in (-0.3, 0.3)])
ROLE = {}
for cl, ramps in ((1, ("yellow",)), (2, ("grey",)), (3, ("char", "seam", "eye"))):
    for r in ramps:
        for h in rb.RAMPS[r]:
            ROLE[int(h, 16)] = cl
KIND = {"yellow": 1, "grey": 2, "char": 3}


def classify(key, mask):
    cls = np.zeros(key.shape, np.int8)
    for k, c in ROLE.items():
        cls[key == k] = c
    cls[mask & (cls == 0)] = 3
    return cls


def view(im, yaw):
    m = im[:, :, 3] > 0
    xs = np.nonzero(m)[1]
    key = (im[:, :, 0].astype(int) << 16) | (im[:, :, 1].astype(int) << 8) | im[:, :, 2].astype(int)
    key = np.where(m, key, -1)
    return dict(yaw=yaw, rgba=im, mask=m, key=key, cls=classify(key, m), axis=(xs.min() + xs.max()) / 2)


def load(folder, names):
    return {n: view(np.array(Image.open(os.path.join(TAKE, folder, n + ".png")).convert("RGBA")), y)
            for n, y in names.items()}


def cam_views():
    cam = load("views_cam30", CAM)
    for n, yaw in (("se", 315), ("ne", 225)):  # the west side as the mirror, as the approved west views are drawn
        cam[n + "_m"] = view(cam[n]["rgba"][:, ::-1].copy(), yaw)
    return cam


def proj(a, b, c, yaw, pitch, axis):
    f, p = np.radians(yaw), np.radians(pitch)
    x = a * np.sin(f) - b * np.cos(f)
    t = a * np.cos(f) + b * np.sin(f)
    col = np.floor(axis + 0.5 + x).astype(int)
    row = np.floor(161 - (c * np.cos(p) - t * np.sin(p))).astype(int)
    return col, row, t * np.cos(p) + c * np.sin(p)


def canvas(col, row, val=None, near=None):
    """Padded canvas (shift 0); with val and near, a z-ordered paint of val."""
    r, c = row + PAD, col + PAD
    ok = (r >= 0) & (r < G) & (c >= 0) & (c < G)
    if val is None:
        cv = np.zeros((G, G), bool)
        cv[r[ok], c[ok]] = True
        return cv
    o = np.argsort(near)
    o = o[ok[o]]
    cv = np.zeros((G, G) + val.shape[1:], val.dtype)
    cv[r[o], c[o]] = val[o]
    return cv


def window(cv, dx, dy):
    return cv[PAD - dy:PAD - dy + 192, PAD - dx:PAD - dx + 192]


def fit(cv, mask, dxs, dys):
    msum = mask.sum()
    best = (-1.0, 0, 0)
    for dy in dys:
        for dx in dxs:
            w = window(cv, dx, dy)
            inter = (w & mask).sum()
            s = inter / (w.sum() + msum - inter)
            if s > best[0]:
                best = (float(s), int(dx), int(dy))
    return best


def inside(mask, col, row, dx, dy):
    r, c = row + dy, col + dx
    ok = (r >= 0) & (r < 192) & (c >= 0) & (c < 192)
    out = np.zeros(col.shape, bool)
    out[ok] = mask[r[ok], c[ok]]
    return out


def classes(p):
    P = rb.build_parts(p)
    cls = np.zeros(A.shape, np.int8)
    for name in rb.ORDER:
        m, ramp, _ = P[name]
        cls[m] = KIND[ramp]
    return cls


def load_json():
    return json.load(open(JSON)) if os.path.exists(JSON) else {}


def save_json(J):
    json.dump(J, open(JSON, "w"), indent=1)


# ---------------------------------------------------------------- 1. pitch per view
def scan():
    app, cam = load("views", APP), load("views_cam30", CAM)
    occ = classes(rb.P5) > 0
    shifts = {}
    for n, v in app.items():  # approved nudges: fitted to the pass 5 model at 6 degrees
        col, row, _ = proj(A[occ], B[occ], C[occ], v["yaw"], rb.PITCH, v["axis"])
        _, dx, dy = fit(canvas(col, row), v["mask"], range(-8, 9), range(-6, 5))
        shifts["app:" + n] = [dx, dy]
    hull = np.ones(A.shape, bool)
    for n, v in app.items():
        col, row, _ = proj(A, B, C, v["yaw"], rb.PITCH, v["axis"])
        hull &= inside(v["mask"], col, row, *shifts["app:" + n])
    a, b, c = A[hull], B[hull], C[hull]
    app_cols = {n: proj(a, b, c, v["yaw"], rb.PITCH, v["axis"])[:2] for n, v in app.items()}
    out = {}
    for n, v in cam.items():
        rows = []
        for p in np.arange(6, 62, 2.0):
            col, row, _ = proj(a, b, c, v["yaw"], p, v["axis"])
            s, dx, dy = fit(canvas(col, row), v["mask"], range(-14, 15), range(-50, 11))
            keep = inside(v["mask"], col, row, dx, dy)
            ex = []
            for m, w in app.items():
                cc, rr = app_cols[m]
                cv = window(canvas(cc[keep], rr[keep]), *shifts["app:" + m])
                ex.append((cv & w["mask"]).sum() / w["mask"].sum())
            own = (window(canvas(col[keep], row[keep]), dx, dy) & v["mask"]).sum() / v["mask"].sum()
            rows.append(dict(pitch=float(p), explained=round(float(np.mean(ex + [own])), 4),
                             approved=round(float(np.mean(ex)), 4), own=round(float(own), 4), fit_iou=round(s, 4),
                             nudge=[dx, dy]))
            print(n, p, rows[-1]["explained"], rows[-1]["approved"], rows[-1]["own"], flush=True)
        best = max(rows, key=lambda r: r["explained"])
        out[n] = dict(best_pitch=best["pitch"], scan=rows)
    J = load_json()
    J.update(pitch={n: r["best_pitch"] for n, r in out.items()}, pitch_scan=out, shifts=shifts,
             hull_voxels=int(hull.sum()))
    save_json(J)
    print({n: r["best_pitch"] for n, r in out.items()})


# ---------------------------------------------------------------- 2. score the current model
def coloured_points():
    _, occ, surf, grid, pal, _ = rb.colour()
    si = np.argwhere(surf)
    rgb = np.array([[int(pal[k][j:j + 2], 16) for j in (0, 2, 4)] for k in grid[tuple(si.T)]], np.uint8)
    pts = (si[:, None, :] + 0.5 + SUB[None]).reshape(-1, 3)
    return pts[:, 0] - rb.OA, pts[:, 1] - rb.OB, pts[:, 2], np.repeat(rgb, len(SUB), axis=0)


def draw(pa, pb, pc, rgb, v, pitch):
    col, row, near = proj(pa, pb, pc, v["yaw"], pitch, v["axis"])
    s, dx, dy = fit(canvas(col, row), v["mask"], range(-14, 15), range(-50, 11))
    rgba = np.concatenate([rgb, np.full((len(rgb), 1), 255, np.uint8)], 1)
    return window(canvas(col, row, rgba, near), dx, dy).copy(), [dx, dy]


def metrics(img, v):
    mm, mv = img[:, :, 3] > 0, v["mask"]
    both = mm & mv
    key = (img[:, :, 0].astype(int) << 16) | (img[:, :, 1].astype(int) << 8) | img[:, :, 2].astype(int)
    key = np.where(mm, key, -1)
    cls = classify(key, mm)
    ys_m, ys_v = np.nonzero(mm.any(1))[0], np.nonzero(mv.any(1))[0]
    xs_m, xs_v = np.nonzero(mm.any(0))[0], np.nonzero(mv.any(0))[0]
    return dict(silhouette_iou=round(float((both).sum() / (mm | mv).sum()), 3),
                colour_match=round(float((key[both] == v["key"][both]).mean()), 3),
                material_match=round(float((cls[both] == v["cls"][both]).mean()), 3),
                height_px=[int(np.ptp(ys_m) + 1), int(np.ptp(ys_v) + 1)],
                width_px=[int(np.ptp(xs_m) + 1), int(np.ptp(xs_v) + 1)],
                top_row=[int(ys_m.min()), int(ys_v.min())],
                yellow_px=[int((cls == 1).sum()), int((v["cls"] == 1).sum())])


def score(label, board=False):
    J = load_json()
    cam = cam_views()
    pa, pb, pc, rgb = coloured_points()
    res, imgs = {}, {}
    for n, v in cam.items():
        p = J["pitch"][n.replace("_m", "")]
        img, nud = draw(pa, pb, pc, rgb, v, p)
        imgs[n] = img
        res[n] = dict(metrics(img, v), pitch=p, nudge=nud)
        J.setdefault("shifts", {})["cam:" + n] = nud
        if not n.endswith("_m"):
            img34, nud34 = draw(pa, pb, pc, rgb, v, 34.0)
            imgs[n] = img34  # the board shows the game camera's angle
            res[n + "_at34"] = dict(metrics(img34, v), pitch=34.0, nudge=nud34)
        print(n, res[n], flush=True)
    J["model_" + label] = dict(shape=rb.SHAPE, views=res)
    save_json(J)
    if board:
        make_board(cam, imgs, label)


def make_board(cam, imgs, label):
    app = load("views", APP)
    names = ("s", "se", "ne", "n")
    cw, ch = 320, 250
    try:
        font = ImageFont.load_default(size=16)
    except TypeError:
        font = ImageFont.load_default()
    heads = ["approved (about 6 deg)", "game-camera drawing", f"rhino {label}, drawn at 34 deg",
             f"rhino {label} in Godot, chase cam", "pass 5 in Godot"]
    board = Image.new("RGBA", (5 * (cw + 8), 30 + 4 * (ch + 8)), (34, 34, 40, 255))
    d = ImageDraw.Draw(board)
    for i, t in enumerate(heads):
        d.text((i * (cw + 8) + 6, 8), t, fill=(235, 235, 240), font=font)
    J = load_json()
    for r, n in enumerate(names):
        y = 30 + r * (ch + 8)
        for i, src in enumerate((app[n]["rgba"], cam[n]["rgba"], imgs[n])):
            bg = Image.new("RGBA", (cw, ch), (110, 110, 118, 255))
            bg.alpha_composite(Image.fromarray(src).crop((16, 40, 176, 165)).resize((cw, ch), Image.NEAREST))
            board.alpha_composite(bg, (i * (cw + 8), y))
        d.text((6, y + 4), n, fill=(235, 235, 240), font=font)
        for i, folder in ((3, "godot_shots"), (4, os.path.join("_pass5", "godot_shots"))):
            f = os.path.join(HERE, folder, f"parts_{n}.png")
            if os.path.exists(f):
                g = Image.open(f).convert("RGBA").resize((cw, ch), Image.NEAREST)
                board.alpha_composite(g, (i * (cw + 8), y))
    board.convert("RGB").save(os.path.join(HERE, "board_rhino_cam30.png"))


# ---------------------------------------------------------------- 3. shape search
def search(W, at):
    """at: a pitch for every cam30 view (the game camera's 34), or 'fit' for each view's scanned pitch."""
    J = load_json()
    pit = J["pitch"] if at == "fit" else {n: float(at) for n in CAM}
    base = {}
    app = load("views", APP)
    cam = {n: v for n, v in cam_views().items() if n != "e"}

    def vscore(pa, pb, pc, pcl, v, pitch, key):
        col, row, near = proj(pa, pb, pc, v["yaw"], pitch, v["axis"])
        img = canvas(col, row, pcl, near)
        if key in base:  # later sets: search near the first fit
            b0 = base[key]
            s, dx, dy = fit(img > 0, v["mask"], range(b0[0] - 3, b0[0] + 4), range(b0[1] - 3, b0[1] + 4))
        else:
            s, dx, dy = fit(img > 0, v["mask"], range(-14, 15), range(-50, 11))
            base[key] = [dx, dy]
        w = window(img, dx, dy)
        ious = [((w == k) & (v["cls"] == k)).sum() / u for k in (1, 2, 3)
                if (u := ((w == k) | (v["cls"] == k)).sum())]
        return (s + np.mean(ious)) / 2

    def evaluate(p):
        cls = classes(p)
        occ = cls > 0
        surf = occ & ~ndimage.binary_erosion(occ, border_value=0)
        si = np.argwhere(surf)
        pts = (si[:, None, :] + 0.5 + SUB[None]).reshape(-1, 3)
        pa, pb, pc = pts[:, 0] - rb.OA, pts[:, 1] - rb.OB, pts[:, 2]
        pcl = np.repeat(cls[tuple(si.T)], len(SUB))
        s_app = np.mean([vscore(pa, pb, pc, pcl, v, rb.PITCH, "app:" + n) for n, v in app.items()])
        s_cam = np.mean([vscore(pa, pb, pc, pcl, v, pit[n.replace("_m", "")], "cam:" + n) for n, v in cam.items()])
        return [float((1 - W) * s_app + W * s_cam), float(s_app), float(s_cam)]

    grid = dict(rear_top=[49, 51, 53, 55, 57, 59, 61], rear_flat=[6, 9, 12, 15, 18, 21, 24],
                rear_bevel=[0.3, 0.5, 0.7, 0.9, 1.2], rear_half=[29, 31, 33, 35],
                rear_back=[-49, -47, -45, -43, -41], hump_top=[62, 65, 68, 71, 74, 77], hump_ha=[4, 7, 10, 13, 16],
                hump_hb=[7.5, 10.5, 13.5, 16.5, 19.5], hump_a=[-8, -5, -2, 1, 4, 7], pa_top=[54, 56, 58, 60, 62, 64],
                head_top=[50, 52, 54, 56, 58], head_w=[14, 15, 16, 17, 18])
    p = dict(rb.P5)
    start = evaluate(p)
    print("pass 5", [round(x, 4) for x in start], flush=True)
    log = [dict(params=dict(p), score=start)]
    for rnd in range(3):
        changed = False
        for k, vals in grid.items():
            cur = evaluate(p)
            best = (cur, p[k])
            for val in vals:
                if val == p[k]:
                    continue
                sc = evaluate(dict(p, **{k: val}))
                if sc[0] > best[0][0] + 1e-4:
                    best = (sc, val)
            changed |= best[1] != p[k]
            p[k] = best[1]
            log.append(dict(params=dict(p), score=best[0]))
            print(rnd, k, best[1], [round(x, 4) for x in best[0]], flush=True)
        if not changed:
            break
    J = load_json()
    J["search"] = dict(w_cam30=W, cam30_pitch=at, start=start, best=dict(params=p, score=evaluate(p)), log=log)
    save_json(J)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "scan":
        scan()
    elif mode == "score":
        score(sys.argv[2], board="board" in sys.argv[3:])
    elif mode == "search":
        search(float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "34")
