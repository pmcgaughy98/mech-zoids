"""Rhino cam35 touch-up (sprite touch-up lane, Claude, 2026-11-04).

Preston: "Make a session for touching up sprites using a synthesis of all we've learned all our tools etc.
Especially aseprite. Sel-out, Cap ink, and all the other professional terms or tasks they would use."

Input  (read only): ../views_cam35/{s,se,e,ne,n}.png   (approved by Preston, "Thats it looks good")
Ref    (read only): ../views/{...}.png                  (the original approved stills, the craft standard)
Output:             ../views_cam35_touchup/{...}.png    raw, no outline: the packer adds sel-out at pack time
                    ./board.png, ./metrics.json, ./views_selout_light/ (the light-following sel-out option)

The rule: recolour only. Alpha never changes, so canvas, feet row, offsets and silhouette stay exact.
Passes, in order (each counted separately in metrics.json):
  1. specks   cluster cleanup: yellow clusters of 1-2 px take the colour most of their neighbours have
  2. seams    capped ink on lit faces: a yellow pixel darker than both neighbours across it, with both
              neighbours lit (base or highlight), in a line of 3+ (one-pixel breaks closed), becomes the
              darkest colour #141218: a panel line between plates
  2b. rims    bevel rim: highlight kept on a RIM-deep band along each big highlight plate's lit (top left)
              edges, base yellow inside; ends the "whole plate filled with highlight" look
  3. gaps     charcoal frame: a shadow or deep yellow pixel with a dark line (accent or charcoal, 6+ px) on
              its left or above it sits in that plate's cast shadow (light from the top left) and becomes
              charcoal shadow; capped at CAP x the approved view's frame + seam share
Eyes and the ring around them are never touched.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

T = Path(r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a")
WORK = T / "cam35_touchup"
OUT = T / "views_cam35_touchup"
sys.path.insert(0, str(T / "anim"))
from selout_rhino import selout  # noqa: E402

V = ["s", "se", "e", "ne", "n"]
CAP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.80
RIM = int(sys.argv[2]) if len(sys.argv) > 2 else 3
SCRATCH = [0]
SEAM = "141218"   # capped ink: the machine's darkest colour
HEX = {k: tuple(int(k[i:i + 2], 16) for i in (0, 2, 4)) for k in
       ["fff4a8", "ffcf1f", "d18a0a", "7a4a06", "d6d6dc", "9d9ba2", "58555e", "3d3a44", "211e27", "ff3a2a",
        "ffe6d8", "141218"]}
YR = ["7a4a06", "d18a0a", "ffcf1f", "fff4a8"]          # yellow ramp, dark to light
SR = ["58555e", "9d9ba2", "d6d6dc"]                    # steel ramp
DARK = ["141218", "211e27", "3d3a44"]                  # accent, charcoal shadow, charcoal
EYE = ["ff3a2a", "ffe6d8"]
N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
N8 = N4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]
OPP = [((0, -1), (0, 1)), ((-1, 0), (1, 0)), ((-1, -1), (1, 1)), ((-1, 1), (1, -1))]


def codes(a):
    """Per-pixel hex code ('' for transparent)."""
    h = np.full(a.shape[:2], "", dtype=object)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        h[y, x] = "%02x%02x%02x" % tuple(a[y, x, :3])
    return h


def paint(a, h):
    out = a.copy()
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        out[y, x, :3] = HEX[h[y, x]]
    return out


def comps(mask, conn=N8):
    lab = np.zeros(mask.shape, int)
    n = 0
    sizes = {}
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        n += 1
        st = [(y, x)]
        lab[y, x] = n
        c = 0
        while st:
            cy, cx = st.pop()
            c += 1
            for dy, dx in conn:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    st.append((ny, nx))
        sizes[n] = c
    return lab, sizes


def nb(h, y, x, d):
    ny, nx = y + d[0], x + d[1]
    if 0 <= ny < h.shape[0] and 0 <= nx < h.shape[1]:
        return h[ny, nx].item() if hasattr(h[ny, nx], "item") else h[ny, nx]
    return ""


def rims(h, guard, depth, min_size=40):
    """Bevel rim: in each highlight region of min_size+ px, the highlight stays on a band `depth` px deep along
    its top edges and depth - 1 along its left edges (the edges that face the top-left light) and the rest of the
    plate becomes base yellow. Hard metal: a lit bevel, a flat plate, a hard edge between them."""
    hm = h == "fff4a8"
    lab, sizes = comps(hm, N4)
    H, W = h.shape

    def bfs(seed):
        dist = np.full(h.shape, 99)
        q = [(y, x) for y, x in zip(*np.nonzero(seed))]
        for y, x in q:
            dist[y, x] = 0
        i = 0
        while i < len(q):
            y, x = q[i]
            i += 1
            for dy, dx in N8:
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and hm[ny, nx] and dist[ny, nx] > dist[y, x] + 1:
                    dist[ny, nx] = dist[y, x] + 1
                    q.append((ny, nx))
        return dist
    up = np.zeros(h.shape, bool)
    left = np.zeros(h.shape, bool)
    up[1:] = ~hm[:-1]
    up[0] = True
    left[:, 1:] = ~hm[:, :-1]
    left[:, 0] = True
    d_top, d_left = bfs(hm & up), bfs(hm & left)
    # top edges face the light most: a deeper band there than on the left edges (also breaks equal-width
    # stacked runs, which PixelLab's lint counts as banding)
    n = 0
    for y, x in zip(*np.nonzero(hm)):
        if sizes[lab[y, x]] >= min_size and d_top[y, x] >= depth and d_left[y, x] >= depth - 1                 and not guard[y, x]:
            h[y, x] = "ffcf1f"
            n += 1
    return n


def eye_guard(h):
    g = np.isin(h, EYE)
    p = np.pad(g, 2)
    out = np.zeros_like(g)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            out |= p[2 + dy:2 + dy + g.shape[0], 2 + dx:2 + dx + g.shape[1]]
    return out


def specks(h, guard):
    changed = 0
    for col in YR:
        lab, sizes = comps(h == col)
        for y, x in zip(*np.nonzero(lab)):
            if sizes[lab[y, x]] > 2 or guard[y, x]:
                continue
            votes = {}
            for d in N8:
                c = nb(h, y, x, d)
                if c in YR and c != col:
                    votes[c] = votes.get(c, 0) + 1
            if votes:
                best = max(votes.items(), key=lambda kv: kv[1])
                if best[1] >= 4:
                    h[y, x] = best[0]
                    changed += 1
    return changed


def valleys(h):
    r = np.full(h.shape, -1)
    for i, c in enumerate(YR):
        r[h == c] = i
    v = np.zeros(h.shape, bool)
    for y, x in zip(*np.nonzero(r >= 0)):
        for d1, d2 in OPP:
            y1, x1, y2, x2 = y + d1[0], x + d1[1], y + d2[0], x + d2[1]
            if not (0 <= y1 < h.shape[0] and 0 <= y2 < h.shape[0] and 0 <= x1 < h.shape[1] and 0 <= x2 < h.shape[1]):
                continue
            a, b = r[y1, x1], r[y2, x2]
            if a >= 2 and b >= 2 and r[y, x] < min(a, b):
                v[y, x] = True
                break
    return v


def seams(h, guard):
    v = valleys(h) & ~guard
    lab, sizes = comps(v)
    keep = np.zeros(h.shape, bool)
    span = {}
    for y, x in zip(*np.nonzero(lab)):
        y0, x0, y1, x1 = span.get(lab[y, x], (y, x, y, x))
        span[lab[y, x]] = (min(y0, y), min(x0, x), max(y1, y), max(x1, x))
    for y, x in zip(*np.nonzero(lab)):
        y0, x0, y1, x1 = span[lab[y, x]]
        long = max(y1 - y0, x1 - x0) + 1
        keep[y, x] = sizes[lab[y, x]] >= 3 and sizes[lab[y, x]] <= 1.5 * long  # lines only, no blobs or rings
    # a seam has to reach a plate edge (a non-yellow pixel) or run 6+ px; a short floating mark mid-plate is a
    # scratch: it takes the colour around it instead of ink (cluster cleanup)
    reach = {}
    for y, x in zip(*np.nonzero(keep)):
        if any(nb(h, y, x, d) not in YR for d in N8):
            reach[lab[y, x]] = True
    scratch = [(y, x) for y, x in zip(*np.nonzero(keep)) if not reach.get(lab[y, x]) and sizes[lab[y, x]] < 6]
    for y, x in scratch:
        keep[y, x] = False
    for y, x in scratch:
        votes = {}
        for d in N8:
            c = nb(h, y, x, d)
            if c in YR and not nb(keep, y, x, d) is True and (y + d[0], x + d[1]) not in scratch:
                votes[c] = votes.get(c, 0) + 1
        if votes:
            h[y, x] = max(votes.items(), key=lambda kv: kv[1])[0]
    SCRATCH[0] += len(scratch)
    # close one-pixel breaks: a yellow pixel with seam on both sides across it joins the seam
    close = []
    for y, x in zip(*np.nonzero(np.isin(h, YR) & ~keep & ~guard)):
        for d1, d2 in OPP:
            if nb(keep, y, x, d1) is True and nb(keep, y, x, d2) is True:
                close.append((y, x))
                break
    for y, x in close:
        keep[y, x] = True
    n = 0
    for y, x in zip(*np.nonzero(keep)):
        if h[y, x] != SEAM:
            h[y, x] = SEAM
            n += 1
    return n, int(v.sum())


def dark_share(h):
    op = h != ""
    return float(np.isin(h, DARK).sum() / op.sum())


def gaps(h, guard, target):
    dark = np.isin(h, DARK)
    interior = h != ""
    for d in N4:  # interior = all 4 neighbours opaque
        interior &= np.roll(np.roll(h != "", -d[0], 0), -d[1], 1)
    lab, sizes = comps(dark & interior)
    line = np.zeros(h.shape, bool)
    for y, x in zip(*np.nonzero(lab)):
        line[y, x] = sizes[lab[y, x]] >= 6
    cand = []
    for y, x in zip(*np.nonzero(np.isin(h, YR[:2]) & ~guard)):
        if (x > 0 and line[y, x - 1]) or (y > 0 and line[y - 1, x]):
            score = (2 if h[y, x] == "7a4a06" else 1) + sum(line[y + dy, x + dx] for dy, dx in N8
                                                             if 0 <= y + dy < h.shape[0] and 0 <= x + dx < h.shape[1])
            cand.append((score, y, x))
    cand.sort(reverse=True)
    op = int((h != "").sum())
    have = int(dark.sum())
    need = max(0, int(target * op) - have)
    for _, y, x in cand[:need]:
        h[y, x] = "211e27"
    return min(need, len(cand)), len(cand)


def selout_light(a):
    """Light-following sel-out (option): like the packer's, but a new outline pixel whose inside neighbour lies
    below or right of it (an edge facing the light, top left) takes the deepest shade of that neighbour's ramp
    instead of #141218. Dark edges merge as before. Stays inside the 12 colours."""
    base, _, _ = selout(a)
    op = a[..., 3] > 127
    h = codes(a)
    out = base.copy()
    H, W = op.shape
    for y, x in zip(*np.nonzero(~op & (base[..., 3] > 0))):
        for dy, dx in ((1, 0), (0, 1)):  # inside neighbour below or to the right: lit edge
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and op[ny, nx]:
                c = h[ny, nx]
                deep = "7a4a06" if c in YR[1:] else "58555e" if c in SR[1:] else None
                if deep:
                    out[y, x, :3] = HEX[deep]
                break
    return out


def checkers(h):
    n = 0
    for y in range(h.shape[0] - 1):
        for x in range(h.shape[1] - 1):
            a, b, c, d = h[y, x], h[y, x + 1], h[y + 1, x], h[y + 1, x + 1]
            if a in YR and b in YR and a == d and b == c and a != b:
                n += 1
    return n


def speck_count(h):
    n = 0
    for col in YR:
        lab, sizes = comps(h == col)
        n += sum(1 for s in sizes.values() if s <= 2)
    return n


def eye_largest(h):
    lab, sizes = comps(np.isin(h, EYE))
    return max(sizes.values()) if sizes else 0


def measure(a, h):
    op = h != ""
    n = int(op.sum())
    ys, xs = np.nonzero(op)
    return {"px": n, "size": f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}", "lowest_row": int(ys.max()),
            "highlight_pct": round(float(np.isin(h, ["fff4a8", "d6d6dc"]).sum() / n * 100), 1),
            "charcoal_pct": round(float(np.isin(h, DARK[1:]).sum() / n * 100), 1),
            "accent_pct": round(float((h == "141218").sum() / n * 100), 1),
            "frame_plus_seam_pct": round(dark_share(h) * 100, 1),
            "deep_yellow_pct": round(float((h == "7a4a06").sum() / n * 100), 1),
            "lit_face_valleys": int(valleys(h).sum()), "yellow_specks": speck_count(h),
            "checkers": checkers(h), "eye_largest": eye_largest(h),
            "off_palette": int(sum(1 for c in h[op] if c not in HEX))}


def run():
    assert OUT.name.endswith("_touchup") and WORK.name.endswith("_touchup")
    OUT.mkdir(exist_ok=True)
    (WORK / "views_selout_light").mkdir(parents=True, exist_ok=True)
    res, met = {}, {"cap": CAP, "rim": RIM, "views": {}}
    for v in V:
        a = np.asarray(Image.open(T / "views_cam35" / f"{v}.png").convert("RGBA"))
        ref = np.asarray(Image.open(T / "views" / f"{v}.png").convert("RGBA"))
        h0, href = codes(a), codes(ref)
        h = h0.copy()
        guard = eye_guard(h)
        m = {"before": measure(a, h0), "approved": measure(ref, href)}
        m["specks_fixed"] = specks(h, guard)
        SCRATCH[0] = 0
        m["seam_px"], m["valleys_found"] = seams(h, guard)
        m["scratches_cleaned_px"] = SCRATCH[0]
        m["rim_px"] = rims(h, guard, RIM)
        target = CAP * dark_share(href)
        m["gap_px"], m["gap_candidates"] = gaps(h, guard, target)
        m["gap_target_pct"] = round(target * 100, 1)
        b = paint(a, h)
        assert np.array_equal(b[..., 3], a[..., 3]), "alpha changed"
        m["after"] = measure(b, h)
        m["changed_px"] = int(np.any(b != a, -1).sum())
        Image.fromarray(b).save(OUT / f"{v}.png")
        Image.fromarray(selout_light(b)).save(WORK / "views_selout_light" / f"{v}.png")
        res[v] = (ref, a, b)
        met["views"][v] = m
    (WORK / "metrics.json").write_text(json.dumps(met, indent=1))
    board(res, met)
    for v in V:
        m = met["views"][v]
        bf, af, ap = m["before"], m["after"], m["approved"]
        print(f"{v:3} changed {m['changed_px']:4}  specks {m['specks_fixed']:3}  rim {m['rim_px']:4}  scratch {m['scratches_cleaned_px']:2}  seams {m['seam_px']:3}/"
              f"{m['valleys_found']:3}  gaps {m['gap_px']:3}/{m['gap_candidates']:3}  "
              f"frame+seam {bf['frame_plus_seam_pct']}->{af['frame_plus_seam_pct']} (appr {ap['frame_plus_seam_pct']}, "
              f"target {m['gap_target_pct']})  hi {bf['highlight_pct']}->{af['highlight_pct']} (appr "
              f"{ap['highlight_pct']})  specks {bf['yellow_specks']}->{af['yellow_specks']}  eye {af['eye_largest']}"
              f"  low {af['lowest_row']}")


FB = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
F = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
GREY, PAGE, TXT, DIM = (0x5A, 0x60, 0x58, 255), (34, 37, 41, 255), (235, 235, 230), (165, 170, 165)


def crop(im, box):
    return Image.fromarray(im).crop(box)


def board(res, met, k=4):
    boxes = {}
    for v in V:
        ys, xs = [], []
        for im in res[v]:
            yy, xx = np.nonzero(im[..., 3] > 0)
            ys += [yy.min(), yy.max()]
            xs += [xx.min(), xx.max()]
        boxes[v] = (min(xs) - 2, min(ys) - 2, max(xs) + 3, max(ys) + 3)
    cw = {v: (boxes[v][2] - boxes[v][0]) * k + 12 for v in V}
    ch = max(b[3] - b[1] for b in boxes.values()) * k + 12
    rows = [("Approved views\n(the craft standard)", lambda r: selout(r[0])[0]),
            ("cam35 as approved\n(before)", lambda r: selout(r[1])[0]),
            ("cam35 touch-up\n(after, game sel-out)", lambda r: selout(r[2])[0]),
            ("Option: touch-up with\nlight-following sel-out", lambda r: selout_light(r[2])),
            ("Changed pixels\n(magenta)", None)]
    lbl, small_h = 250, max(b[3] - b[1] for b in boxes.values()) * 2 + 16
    small_w = sum(sum((boxes[v][2] - boxes[v][0]) * kk + 8 for _ in js) + 10 for v in V
                  for kk, js in ((1, (0, 1, 2)), (2, (1, 2))))
    W = lbl + max(sum(cw.values()), max(sum(((boxes[v][2] - boxes[v][0]) * kk + 8) * len(js) + 10 for v in V)
                                        for kk, js in ((1, (0, 1, 2)), (2, (1, 2))))) + 10
    H = 74 + len(rows) * (ch + 8) + 2 * (small_h + 8) + 40
    B = Image.new("RGBA", (W, H), PAGE)
    dr = ImageDraw.Draw(B)
    dr.text((12, 12), "Rhino cam35 touch-up: capped-ink plate seams, bevel rims, charcoal gaps, speck cleanup. Silhouette unchanged.",
            font=FB, fill=TXT)
    dr.text((12, 42), "4x on the map grey. Recolour only: alpha is identical to the approved cam35 views, so feet, "
            "canvas and outline stay exact. 12 colours.", font=F, fill=DIM)
    y = 74
    for ri, (lab, fn) in enumerate(rows):
        dr.text((12, y + 8), lab, font=F, fill=TXT)
        x = lbl
        for v in V:
            dr.rectangle([x, y, x + cw[v] - 8, y + ch], fill=GREY)
            if fn:
                im = crop(fn(res[v]), boxes[v])
            else:
                a, b = res[v][1], res[v][2]
                g = selout(b)[0].copy()
                lum = (g[..., :3].astype(int) @ [77, 150, 29] >> 8).astype(np.uint8)
                g[..., :3] = (lum[..., None] * 0.45 + 60).astype(np.uint8)
                g[np.any(a != b, -1), :3] = (255, 40, 220)
                im = crop(g, boxes[v])
            im = im.resize((im.width * k, im.height * k), Image.NEAREST)
            B.alpha_composite(im, (x + (cw[v] - 8 - im.width) // 2, y + ch - 6 - im.height))
            if ri == 0:
                dr.text((x + 6, y + 4), v, font=FB, fill=TXT)
            if ri == 4:
                dr.text((x + 6, y + 4), f"{met['views'][v]['changed_px']} px", font=F, fill=TXT)
            x += cw[v]
        y += ch + 8
    for kk, lab, js in ((1, "Game size 1x\napproved | before | after", (0, 1, 2)),
                        (2, "2x\nbefore | after", (1, 2))):
        dr.text((12, y + 8), lab, font=F, fill=TXT)
        x = lbl
        for v in V:
            for j in js:
                im = crop(selout(res[v][j])[0], boxes[v])
                im = im.resize((im.width * kk, im.height * kk), Image.NEAREST)
                B.alpha_composite(Image.new("RGBA", (im.width + 4, small_h - 8), GREY), (x - 2, y))
                B.alpha_composite(im, (x, y + small_h - 12 - im.height))
                x += im.width + 8
            x += 10
        y += small_h + 8
    dr.text((12, H - 30), "Input views_cam35/ and views/ untouched. Output: views_cam35_touchup/ (raw, the packer "
            "adds sel-out). Numbers: cam35_touchup/metrics.json.", font=F, fill=DIM)
    B.convert("RGB").save(WORK / "board.png")


if __name__ == "__main__":
    run()
