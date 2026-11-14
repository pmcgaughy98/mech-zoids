#!/usr/bin/env python3
"""Rhino ground pound at 35: free prep (attack lane, 2026-11-05). Read ../ATTACK_PLAYBOOK.md and ../rhino_l/PLAN.md.

Builds, for the views of one run, from the approved touch-up stills only:
  targets.json        per view: soles (planted / lifted), the hip pivot, per-frame screen targets, holds, key frames
  still_metrics.json  per view: colours, ink share, eye pixels, 4-connected pieces, bbox (the gates' reference numbers)
  blocking/<v>_f<i>.png   a rough pose made by moving the still's pixels (NOT the art: guide and previz only)
  refs/look_35.png    the stills of the run, left to right, 6x, on magenta (the design and camera)
  refs/pose_guide.png flat grey silhouettes of the blocking, rows = views, columns = F0..F5 (the pose, for the image tool)
  guide_<v>.png       for Preston: per frame the still faint, the blocking silhouette, planted feet green, targets orange
  blocking.gif        all views at the planned holds, labelled "blocking, not the art"
Usage: python gp35_prep.py <out dir> <views...>     e.g. python gp35_prep.py .../gp35/prep e se ne
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw

STILLS = r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/views_cam35_touchup"
PAL = r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/palette.json"
COS, SIN = math.cos(math.radians(35)), math.sin(math.radians(35))  # vertical 0.819, depth 0.574
HOLDS = [1, 1, 1, 2, 3, 3]  # 100 ms ticks (game feel, 2026-11-05)
SLAM, RISE = 4, 5
PITCH = [0, 0, 15, 30, 0, 0]  # degrees about the hind hips
HIP_H = 34  # texels above the ground
SPAN = 40   # hind to front soles along the body (packer feet: front 7, rear -33)
# per view: body axis on screen (f x u), mid-plane hind ground point, visible leg soles (x, y, kind)
VIEW = {
    "e":  {"A": (1.0, 0.0), "M": (62.5, 148.5),
           "legs": [(62.5, 160, "hind", 24), (102.5, 160, "front_near", 24)]},
    "se": {"A": (0.707, 0.405), "M": (74.2, 135.8),
           "legs": [(65, 143, "hind", 20), (88.5, 160, "front_near", 22), (116.5, 155, "front", 10)]},
    "ne": {"A": (0.707, -0.405), "M": (75.0, 152.0),
           "legs": [(89, 160, "hind", 22), (65, 150, "hind", 16), (116, 141, "front_near", 12)]},
}
LEG_W, LEG_H = 11, 24


def load(v):
    return np.array(Image.open(f"{STILLS}/{v}.png").convert("RGBA"))


def pieces4(mask):
    seen = np.zeros_like(mask, bool); n = 0; sizes = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        n += 1; st = [(y, x)]; seen[y, x] = True; c = 0
        while st:
            cy, cx = st.pop(); c += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < mask.shape[0] and 0 <= xx < mask.shape[1] and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True; st.append((yy, xx))
        sizes.append(c)
    return n, sizes


def metrics(a):
    op = a[..., 3] > 0
    rgb = a[..., :3][op]
    hexes = ["%02x%02x%02x" % tuple(c) for c in rgb]
    total = len(hexes)
    count = {h: hexes.count(h) for h in set(hexes)}
    ys, xs = np.nonzero(op)
    # specks: 4-connected single-colour pieces of 1-2 px
    specks = 0
    for h in count:
        m = op & np.all(a[..., :3] == np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]), axis=2)
        specks += sum(1 for s in pieces4(m)[1] if s <= 2)
    return {"bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            "opaque": total, "colours": sorted(count, key=lambda h: -count[h]),
            "ink_share": round(count.get("141218", 0) / total, 4),
            "eye_px": count.get("ff3a2a", 0) + count.get("ffe6d8", 0),
            "pieces4": pieces4(op)[0], "specks_1_2px": specks}


def close_fill(m, r=2):
    """Silhouette for the pose guide: close gaps of up to 2r px, then fill holes not open to the border."""
    from numpy.lib.stride_tricks import sliding_window_view as sw
    p = np.pad(m, r); d = sw(p, (2 * r + 1, 2 * r + 1)).any(axis=(2, 3))
    p = np.pad(d, r, constant_values=True); e = sw(p, (2 * r + 1, 2 * r + 1)).all(axis=(2, 3))
    out = ~e; seen = np.zeros_like(e)
    st = [(y, x) for y in range(e.shape[0]) for x in (0, e.shape[1] - 1)] +          [(y, x) for x in range(e.shape[1]) for y in (0, e.shape[0] - 1)]
    while st:
        y, x = st.pop()
        if 0 <= y < e.shape[0] and 0 <= x < e.shape[1] and out[y, x] and not seen[y, x]:
            seen[y, x] = True; st += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    m2 = e | (out & ~seen)
    # keep only the main shape: drop loose pieces under 40 px (blocking leftovers)
    lab = np.zeros(m2.shape, int); n = 0; sizes = {}
    for y, x in zip(*np.nonzero(m2)):
        if lab[y, x]:
            continue
        n += 1; st = [(y, x)]; lab[y, x] = n; c = 0
        while st:
            cy, cx = st.pop(); c += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < m2.shape[0] and 0 <= xx < m2.shape[1] and m2[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n; st.append((yy, xx))
        sizes[n] = c
    keep = [k for k, c in sizes.items() if c >= 40]
    return np.isin(lab, keep)


def leg_of(v, x, y):
    for sx, sy, kind, lh in VIEW[v]["legs"]:
        if abs(x - sx) <= LEG_W and sy - lh <= y <= sy:
            return kind
    return None


def shoulder_shift(v, theta):
    t = math.radians(theta)
    da, dh = SPAN * (math.cos(t) - 1), SPAN * math.sin(t)
    A = VIEW[v]["A"]
    return da * A[0], da * A[1] - COS * dh  # screen dx, dy


def block(v, still, f):
    """A rough pose from the still's pixels: guide and previz only, never the art."""
    H, W = still.shape[:2]
    out = np.zeros_like(still)
    op = still[..., 3] > 0
    kinds = {}
    for y, x in zip(*np.nonzero(op)):
        kinds[(y, x)] = leg_of(v, x, y)
    A, M = VIEW[v]["A"], VIEW[v]["M"]
    t = math.radians(PITCH[f])

    def put(x, y, c):
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H:
            out[yi, xi] = c

    # hind legs: planted, never move
    for (y, x), k in kinds.items():
        if k == "hind":
            put(x, y, still[y, x])
    if PITCH[f]:
        # body: rotated about the hind hips (mid-plane assumption), sampled backward so it has no holes
        body = np.zeros(op.shape, bool)
        for (y, x), k in kinds.items():
            body[y, x] = k is None
        for yy in range(H):
            for xx in range(W):
                ah2 = (xx - M[0]) / A[0]
                h2 = (M[1] + A[1] * ah2 - yy) / COS
                ah = ah2 * math.cos(t) + (h2 - HIP_H) * math.sin(t)
                h = HIP_H - ah2 * math.sin(t) + (h2 - HIP_H) * math.cos(t)
                sx = M[0] + ah * A[0]; sy = M[1] + ah * A[1] - COS * h
                si, sj = int(round(sy)), int(round(sx))
                if 0 <= si < H and 0 <= sj < W and body[si, sj]:
                    out[yy, xx] = still[si, sj]
        dx, dy = shoulder_shift(v, PITCH[f])
        for (y, x), k in kinds.items():
            if k and k.startswith("front"):
                put(x + dx, y + dy, still[y, x])
    else:
        body_dx, body_dy = {1: (-2 * A[0], -2 * A[1] + 1), 4: (0, 2), 5: (0, 1)}.get(f, (0, 0))
        for (y, x), k in kinds.items():
            if k is None:
                put(x + body_dx, y + body_dy, still[y, x])
        for (y, x), k in kinds.items():
            if k and k.startswith("front"):
                lift = 2 if (f == RISE and k == "front_near") else 0
                put(x, y - lift, still[y, x])
    if f == 0:
        out = still.copy()
    return out


def main():
    out_dir, views = sys.argv[1], sys.argv[2:]
    os.makedirs(f"{out_dir}/blocking", exist_ok=True); os.makedirs(f"{out_dir}/refs", exist_ok=True)
    pal = [p["hex"] for p in json.load(open(PAL))]
    targets = {"holds_100ms": HOLDS, "slam_frame": SLAM, "rise_frame": RISE, "pitch_deg": PITCH,
               "hip_height_texels": HIP_H, "sole_span_texels": SPAN, "palette": pal, "views": {}}
    mets, frames = {}, {}
    for v in views:
        still = load(v)
        mets[v] = metrics(still)
        frames[v] = [block(v, still, f) for f in range(6)]
        for f, fr in enumerate(frames[v]):
            Image.fromarray(fr).save(f"{out_dir}/blocking/{v}_f{f}.png")
        A = VIEW[v]["A"]
        per = []
        for f in range(6):
            if PITCH[f]:
                fdx, fdy = shoulder_shift(v, PITCH[f])
            else:
                fdx, fdy = 0.0, 0.0
            body = {1: (-2 * A[0], -2 * A[1] + 1), 4: (0, 2), 5: (0, 1)}.get(f, (0, 0))
            per.append({"frame": f, "front_feet_shift_px": [round(fdx, 1), round(fdy, 1)],
                        "near_front_lift_px": 2 if f == RISE else (round(-fdy, 1) if PITCH[f] else 0),
                        "body_shift_px": [round(body[0], 1), round(body[1], 1)],
                        "head_extra_drop_px": 1 if f in (1, SLAM) else 0,
                        "hind_feet": "planted, 1 px or under"})
        targets["views"][v] = {"soles": [{"x": s[0], "y": s[1], "leg": s[2]} for s in VIEW[v]["legs"]],
                               "axis_on_screen": A, "hind_ground_mid": VIEW[v]["M"],
                               "hip_pivot": [VIEW[v]["M"][0], round(VIEW[v]["M"][1] - COS * HIP_H, 1)],
                               "frames": per}
    json.dump(targets, open(f"{out_dir}/targets.json", "w"), indent=1)
    json.dump(mets, open(f"{out_dir}/still_metrics.json", "w"), indent=1)
    box = (36, 40, 156, 166)  # holds every rhino view and its rear-up
    bw, bh = box[2] - box[0], box[3] - box[1]
    # look ref: the stills, 6x, magenta
    look = Image.new("RGB", (bw * 6 * len(views), bh * 6), (255, 0, 255))
    for i, v in enumerate(views):
        t = Image.fromarray(load(v)).crop(box).resize((bw * 6, bh * 6), Image.NEAREST)
        look.paste(t, (i * bw * 6, 0), t)
    look.save(f"{out_dir}/refs/look_35.png")
    # pose guide: flat grey silhouettes, rows = views, columns = F0..F5, 4x, magenta
    S = 4
    pg = Image.new("RGB", (bw * S * 6, bh * S * len(views)), (255, 0, 255))
    for r, v in enumerate(views):
        for f in range(6):
            m = close_fill(frames[v][f][box[1]:box[3], box[0]:box[2], 3] > 0)
            sil = np.zeros((bh, bw, 4), np.uint8); sil[m] = (110, 110, 118, 255)
            t = Image.fromarray(sil).resize((bw * S, bh * S), Image.NEAREST)
            pg.paste(t, (f * bw * S, r * bh * S), t)
    pg.save(f"{out_dir}/refs/pose_guide.png")
    # guides for Preston and the previz
    G = 3
    for v in views:
        strip = Image.new("RGB", (bw * G * 6, bh * G + 14), (40, 40, 46))
        d = ImageDraw.Draw(strip)
        st = load(v)
        for f in range(6):
            cell = np.full((bh, bw, 3), (40, 40, 46), np.uint8)
            sm = st[box[1]:box[3], box[0]:box[2], 3] > 0
            cell[sm] = (70, 70, 80)
            fm = frames[v][f][box[1]:box[3], box[0]:box[2], 3] > 0
            cell[fm] = (150, 150, 160)
            im = Image.fromarray(cell).resize((bw * G, bh * G), Image.NEAREST)
            dd = ImageDraw.Draw(im)
            for sx, sy, kind, _lh in VIEW[v]["legs"]:
                x0 = (sx - LEG_W + 4 - box[0]) * G; x1 = (sx + LEG_W - 4 - box[0]) * G
                if kind == "hind" or not PITCH[f]:
                    lift = 2 if (f == RISE and kind == "front_near") else 0
                    y = (sy - lift - box[1]) * G
                    dd.rectangle([x0, y, x1, y + G], fill=(60, 220, 90) if kind == "hind" or lift == 0 else (255, 160, 40))
                else:
                    dx, dy = shoulder_shift(v, PITCH[f])
                    y = (sy + dy - box[1]) * G
                    dd.rectangle([x0 + dx * G, y, x1 + dx * G, y + G], fill=(255, 160, 40))
            strip.paste(im, (f * bw * G, 14))
            d.text((f * bw * G + 4, 1), f"{v} F{f} x{HOLDS[f]}" + (" SLAM" if f == SLAM else ""), fill=(255, 255, 255))
        strip.save(f"{out_dir}/guide_{v}.png")
    gif = []
    for f in range(6):
        row = Image.new("RGB", (bw * G * len(views), bh * G + 14), (128, 128, 128))
        d = ImageDraw.Draw(row)
        for i, v in enumerate(views):
            t = Image.fromarray(frames[v][f]).crop(box).resize((bw * G, bh * G), Image.NEAREST)
            row.paste(t, (i * bw * G, 14), t)
        d.text((4, 1), f"BLOCKING, NOT THE ART   F{f}", fill=(255, 255, 0))
        gif += [row] * HOLDS[f]
    gif[0].save(f"{out_dir}/blocking.gif", save_all=True, append_images=gif[1:], duration=100, loop=0)
    print(json.dumps(mets, indent=0)[:900])


if __name__ == "__main__":
    main()
