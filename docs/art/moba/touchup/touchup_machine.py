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

import argparse
ROOT = Path(r"D:/dev/new-mech-rpg/docs/art/moba")
sys.path.insert(0, str(ROOT / "rhino_l" / "take-a" / "anim"))
from selout_rhino import selout  # noqa: E402
ap = argparse.ArgumentParser()
ap.add_argument("take")                      # e.g. fennec_s/take-b
ap.add_argument("--cap", type=float, default=0.80)
ap.add_argument("--rim", type=int, default=3)
ap.add_argument("--palette", default=None)   # default <take>/cam35/palette.json, else <take>/palette.json
ap.add_argument("--approved", default=None)  # default fixed/ if present, else views/
ap.add_argument("--out", default=None)       # default <take>/views_cam35_touchup (must end in _touchup)
ap.add_argument("--work", default=None)      # default <take>/cam35_touchup (must end in _touchup)
ap.add_argument("--title", default=None)
ap.add_argument("--seam-cap", action="store_true")    # capped ink: no seam ink when the view is already as dark as approved
ap.add_argument("--rim-min", type=int, default=40)  # smallest highlight plate that gets a bevel rim
A = ap.parse_args()
TITLE = A.title or A.take.split("/")[0].split("_")[0].capitalize()
T = ROOT / A.take
OUT = Path(A.out) if A.out else T / "views_cam35_touchup"
WORK = Path(A.work) if A.work else T / "cam35_touchup"
APPROVED = A.approved or ("fixed" if (T / "fixed").is_dir() else "views")
PALF = Path(A.palette) if A.palette else (T / "cam35" / "palette.json" if (T / "cam35" / "palette.json").exists()
                                          else T / "palette.json")
PAL = json.loads(PALF.read_text())

V = ["s", "se", "e", "ne", "n"]
CAP, RIM = A.cap, A.rim
HEX = {p["hex"].lstrip("#").lower(): tuple(int(p["hex"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) for p in PAL}


def _luma(h):
    r, g, b = HEX[h]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


ROLES = {}
for p in PAL:
    ROLES.setdefault(p["role"].lower(), []).append(p["hex"].lstrip("#").lower())
GLOWY = ("eye", "lens", "glow", "visor")          # never recoloured (gorilla: "shield and visor glow")
EYE = [h for r, hs in ROLES.items() if any(k in r for k in GLOWY) for h in hs]
ACCENT = [h for r, hs in ROLES.items() if "accent" in r for h in hs]
CHAR = [h for r, hs in ROLES.items() if "charcoal" in r or "frame" in r for h in hs]
STEEL = [h for r, hs in ROLES.items() if "steel" in r for h in hs]
if not CHAR:                                       # no charcoal role (gorilla): the darkest steel is the frame
    _pool = STEEL or [h for r, hs in ROLES.items() if not any(g in r for g in GLOWY) and "accent" not in r for h in hs]
    CHAR = [min(_pool, key=lambda h: 0.2126 * int(h[:2], 16) + 0.7152 * int(h[2:4], 16) + 0.0722 * int(h[4:], 16))]
SEAM = min(ACCENT, key=_luma)                       # capped ink: the machine's darkest colour
GAPC = min(CHAR, key=_luma)                         # charcoal shadow for the gaps
DARK = ACCENT + CHAR
# body ramps: every other role with 3+ shades, dark to light (rhino: yellow; fennec: violet, cream-gold)
RAMPS = [sorted(hs, key=_luma) for r, hs in ROLES.items()
         if len(hs) >= 3 and r not in [k for k in ROLES if any(g in k for g in GLOWY) or "accent" in k
                                       or "charcoal" in k or "steel" in k]]
RAMP_OF = {h: i for i, rp in enumerate(RAMPS) for h in rp}
RIDX = {h: j for rp in RAMPS for j, h in enumerate(rp)}
BODY = list(RAMP_OF)
HILITE = [rp[-1] for rp in RAMPS] + [max(STEEL, key=_luma)] if STEEL else [rp[-1] for rp in RAMPS]
YR = BODY  # kept name: any body-ramp colour
SCRATCH = [0]


def base_idx(h):
    return len(RAMPS[RAMP_OF[h]]) - 2      # base shade index in its ramp (4-ramp: 2, 3-ramp: 1)


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
        out[y, x, :3] = HEX.get(h[y, x], a[y, x, :3])
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
    n = 0
    for rp in RAMPS:
        n += _rims(h, guard, depth, min_size, rp[-1], rp[-2])
    return n


def _rims(h, guard, depth, min_size, hi, base):
    hm = h == hi
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
            h[y, x] = base
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
    for col in BODY:
        lab, sizes = comps(h == col)
        for y, x in zip(*np.nonzero(lab)):
            if sizes[lab[y, x]] > 2 or guard[y, x]:
                continue
            votes = {}
            for d in N8:
                c = nb(h, y, x, d)
                if c in RAMP_OF and RAMP_OF[c] == RAMP_OF[col] and c != col:
                    votes[c] = votes.get(c, 0) + 1
            if votes:
                best = max(votes.items(), key=lambda kv: kv[1])
                if best[1] >= 4:
                    h[y, x] = best[0]
                    changed += 1
    return changed


def valleys(h):
    v = np.zeros(h.shape, bool)
    for y, x in zip(*np.nonzero(np.isin(h, BODY))):
        rp, ri, bi = RAMP_OF[h[y, x]], RIDX[h[y, x]], base_idx(h[y, x])
        for d1, d2 in OPP:
            c1, c2 = nb(h, y, x, d1), nb(h, y, x, d2)
            if c1 not in RAMP_OF or c2 not in RAMP_OF or RAMP_OF[c1] != rp or RAMP_OF[c2] != rp:
                continue
            a, b = RIDX[c1], RIDX[c2]
            if a >= bi and b >= bi and ri < min(a, b):
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
        if any(RAMP_OF.get(nb(h, y, x, d)) != RAMP_OF.get(h[y, x]) for d in N8):
            reach[lab[y, x]] = True
    scratch = [(y, x) for y, x in zip(*np.nonzero(keep)) if not reach.get(lab[y, x]) and sizes[lab[y, x]] < 6]
    for y, x in scratch:
        keep[y, x] = False
    for y, x in scratch:
        votes = {}
        for d in N8:
            c = nb(h, y, x, d)
            if c in RAMP_OF and RAMP_OF[c] == RAMP_OF.get(h[y, x]) and not nb(keep, y, x, d) is True                     and (y + d[0], x + d[1]) not in scratch:
                votes[c] = votes.get(c, 0) + 1
        if votes:
            h[y, x] = max(votes.items(), key=lambda kv: kv[1])[0]
    SCRATCH[0] += len(scratch)
    # close one-pixel breaks: a yellow pixel with seam on both sides across it joins the seam
    close = []
    for y, x in zip(*np.nonzero(np.isin(h, BODY) & ~keep & ~guard)):
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
    low = [c for c in BODY if RIDX[c] < base_idx(c)]   # shadow and deep shades of each ramp
    for y, x in zip(*np.nonzero(np.isin(h, low) & ~guard)):
        if (x > 0 and line[y, x - 1]) or (y > 0 and line[y - 1, x]):
            score = (2 if RIDX[h[y, x]] == 0 else 1) + sum(line[y + dy, x + dx] for dy, dx in N8
                                                             if 0 <= y + dy < h.shape[0] and 0 <= x + dx < h.shape[1])
            cand.append((score, y, x))
    cand.sort(reverse=True)
    op = int((h != "").sum())
    have = int(dark.sum())
    need = max(0, int(target * op) - have)
    for _, y, x in cand[:need]:
        h[y, x] = GAPC
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
                deep = (RAMPS[RAMP_OF[c]][0] if c in RAMP_OF and RIDX[c] > 0 else
                        min(STEEL, key=_luma) if c in STEEL and c != min(STEEL, key=_luma) else None)
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
            "highlight_pct": round(float(np.isin(h, HILITE).sum() / n * 100), 1),
            "charcoal_pct": round(float(np.isin(h, CHAR).sum() / n * 100), 1),
            "accent_pct": round(float(np.isin(h, ACCENT).sum() / n * 100), 1),
            "frame_plus_seam_pct": round(dark_share(h) * 100, 1),
            "deepest_shade_pct": round(float(np.isin(h, [rp[0] for rp in RAMPS]).sum() / n * 100), 1),
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
        ref = np.asarray(Image.open(T / APPROVED / f"{v}.png").convert("RGBA"))
        h0, href = codes(a), codes(ref)
        h = h0.copy()
        guard = eye_guard(h)
        m = {"before": measure(a, h0), "approved": measure(ref, href)}
        m["specks_fixed"] = specks(h, guard)
        SCRATCH[0] = 0
        if A.seam_cap and dark_share(h0) >= dark_share(href):
            m["seam_px"], m["valleys_found"] = 0, int(valleys(h).sum())
            m["seams_skipped"] = "dark share already at or above the approved views"
        else:
            m["seam_px"], m["valleys_found"] = seams(h, guard)
        m["scratches_cleaned_px"] = SCRATCH[0]
        m["rim_px"] = rims(h, guard, RIM, A.rim_min)
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
    dr.text((12, 12), f"{TITLE} cam35 touch-up: capped-ink plate seams, bevel rims, charcoal gaps, speck cleanup. Silhouette unchanged.",
            font=FB, fill=TXT)
    dr.text((12, 42), "4x on the map grey. Recolour only: alpha is identical to the approved cam35 views, so feet, "
            f"canvas and outline stay exact. {len(HEX)} colours.", font=F, fill=DIM)
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
