"""Underside shade pass (an option beside a kept touch-up). Recolour only.

The fleet light is top-left-front: tops and left faces lit, undersides and right faces dark. The rim pass in
touchup_machine.py gives each lit plate a bright bevel on its top and left edges. This pass does the other half:
it sinks the side of each plate that faces away from the light one step down its body ramp.

1. Shadow plates (shadow shade, MIN1+ px): a band d1 deep along their top edges and d1 - 1 along their left
   edges keeps the shadow shade (the turn into shadow); the rest becomes the deepest shade.
2. Base plates (base shade, MIN2+ px): a band d2 deep along their bottom edges and d2 - 1 along their right
   edges becomes the shadow shade (a dark bevel opposite the lit rim).

d1 is picked per view so the deepest-shade share lands closest to the approved views without passing them;
then d2 so the shadow-shade share lands closest to the approved views. Highlight, steel, frame, accent and
eye colours are never touched; pixels within 2 px of an eye are guarded. Alpha is asserted identical.

Lives in the session worktree because the session guard blocks writes to the main checkout; it reads and
writes the shared art folder by absolute path (ROOT), like touchup_machine.py.
Input (read only): <take>/<src>/ (default views_cam35_touchup), approved views fixed/ or views/.
Output: <take>/<src>_shade/ and <take>/cam35_touchup/shade/ (board.png, metrics.json).
Usage: python shade_pass.py hippo_l/take-b --title Hippo
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:/dev/new-mech-rpg/docs/art/moba")
ap = argparse.ArgumentParser()
ap.add_argument("take")
ap.add_argument("--src", default="views_cam35_touchup")
ap.add_argument("--approved", default=None)
ap.add_argument("--title", default=None)
ap.add_argument("--min1", type=int, default=20)   # smallest shadow plate that sinks
ap.add_argument("--min2", type=int, default=40)   # smallest base plate that gets a dark bevel
ap.add_argument("--d2-max", type=int, default=3)  # widest dark bevel allowed (1 keeps plates from ringing)
ap.add_argument("--tag", default="shade")         # output names: <src>_<tag>/ and cam35_touchup/<tag>/
ap.add_argument("--also", default=None)           # another output folder to show as an extra board row
A = ap.parse_args()
T = ROOT / A.take
SRC = T / A.src
OUT = T / (A.src + "_" + A.tag)
WORK = T / "cam35_touchup" / A.tag
APPROVED = A.approved or ("fixed" if (T / "fixed").is_dir() else "views")
TITLE = A.title or A.take.split("/")[0].split("_")[0].capitalize()
PALF = T / "cam35" / "palette.json" if (T / "cam35" / "palette.json").exists() else T / "palette.json"
PAL = json.loads(PALF.read_text())
HEX = {p["hex"].lstrip("#").lower(): tuple(int(p["hex"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) for p in PAL}


def luma(h):
    r, g, b = HEX[h]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


ROLES = {}
for p in PAL:
    ROLES.setdefault(p["role"].lower(), []).append(p["hex"].lstrip("#").lower())
GLOWY = ("eye", "lens", "glow", "visor")
EYE = [h for r, hs in ROLES.items() if any(k in r for k in GLOWY) for h in hs]
# body ramps with deep, shadow, base and highlight (4 shades), dark to light
RAMPS = [sorted(hs, key=luma) for r, hs in ROLES.items()
         if len(hs) >= 4 and not any(k in r for k in GLOWY + ("accent", "charcoal", "frame", "steel"))]
assert RAMPS, "no 4-shade body ramp in the palette"
V = ["s", "se", "e", "ne", "n"]
N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
N8 = N4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def codes(a):
    h = np.full(a.shape[:2], "", dtype=object)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        h[y, x] = "%02x%02x%02x" % tuple(a[y, x, :3])
    return h


def paint(a, h):
    out = a.copy()
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        out[y, x, :3] = HEX.get(h[y, x], a[y, x, :3])
    return out


def comps(mask):
    lab = np.zeros(mask.shape, int)
    sizes, n = {}, 0
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        n += 1
        st, lab[y, x], c = [(y, x)], n, 0
        while st:
            cy, cx = st.pop()
            c += 1
            for dy, dx in N4:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    st.append((ny, nx))
        sizes[n] = c
    return lab, sizes


def edge_dist(mask, d):
    """Distance (N8 steps through the region) from the region's edge on side d, e.g. (-1, 0) = top edge."""
    H, W = mask.shape
    dist = np.full(mask.shape, 99)
    q = []
    for y, x in zip(*np.nonzero(mask)):
        ny, nx = y + d[0], x + d[1]
        if not (0 <= ny < H and 0 <= nx < W and mask[ny, nx]):
            dist[y, x] = 0
            q.append((y, x))
    i = 0
    while i < len(q):
        y, x = q[i]
        i += 1
        for dy, dx in N8:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and dist[ny, nx] > dist[y, x] + 1:
                dist[ny, nx] = dist[y, x] + 1
                q.append((ny, nx))
    return dist


def eye_guard(h):
    g = np.isin(h, EYE)
    p = np.pad(g, 2)
    out = np.zeros_like(g)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            out |= p[2 + dy:2 + dy + g.shape[0], 2 + dx:2 + dx + g.shape[1]]
    return out


def big_mask(lab, sizes, m, min_size):
    keep = np.array([0] + [1 if sizes[i] >= min_size else 0 for i in range(1, len(sizes) + 1)], bool)
    return keep[lab] & m


def sink_shadow(h, guard, d1):
    """Step 1: shadow plates keep a lit-side band, the rest becomes the deepest shade."""
    out = h.copy()
    for rp in RAMPS:
        deep, shad = rp[0], rp[1]
        m = h == shad
        lab, sizes = comps(m)
        dt, dl = edge_dist(m, (-1, 0)), edge_dist(m, (0, -1))
        out[big_mask(lab, sizes, m, A.min1) & (dt >= d1) & (dl >= d1 - 1) & ~guard] = deep
    return out


def bevel_base(h, guard, d2):
    """Step 2: base plates get a shadow band along their bottom and right edges."""
    out = h.copy()
    if d2 <= 0:
        return out
    for rp in RAMPS:
        shad, base = rp[1], rp[-2]
        m = h == base
        lab, sizes = comps(m)
        db, dr = edge_dist(m, (1, 0)), edge_dist(m, (0, 1))
        out[big_mask(lab, sizes, m, A.min2) & ((db < d2) | (dr < d2 - 1)) & ~guard] = shad
    return out


def shares(h):
    n = int((h != "").sum())
    s = {}
    for k, j in (("deep", 0), ("shadow", 1), ("base", -2), ("highlight", -1)):
        s[k] = round(float(np.isin(h, [rp[j] for rp in RAMPS]).sum() / n * 100), 1)
    return s


def body_specks(h):
    """1-2 px clusters of one body colour (this script's own count, for before/after only)."""
    c = 0
    for rp in RAMPS:
        for col in rp:
            _, sizes = comps(h == col)
            c += sum(1 for v in sizes.values() if v <= 2)
    return c


def run():
    OUT.mkdir(exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    met, res = {"src": A.src, "min1": A.min1, "min2": A.min2, "d2_max": A.d2_max, "views": {}}, {}
    for v in V:
        a = np.asarray(Image.open(SRC / f"{v}.png").convert("RGBA"))
        ref = np.asarray(Image.open(T / APPROVED / f"{v}.png").convert("RGBA"))
        h0, href = codes(a), codes(ref)
        guard = eye_guard(h0)
        s0, sa = shares(h0), shares(href)
        # d1: deepest share closest to approved without passing it (None = leave shadow plates alone)
        grid1 = {d1: sink_shadow(h0, guard, d1) for d1 in (1, 2, 3, 4)}
        ok = {d1: hh for d1, hh in grid1.items() if shares(hh)["deep"] <= sa["deep"] + 0.5}
        if s0["deep"] >= sa["deep"] or not ok:
            d1, h1 = None, h0
        else:
            d1 = min(ok, key=lambda k: abs(shares(ok[k])["deep"] - sa["deep"]))
            h1 = ok[d1]
        # d2: shadow share closest to approved
        grid2 = {d2: bevel_base(h1, guard, d2) for d2 in range(0, A.d2_max + 1)}
        d2 = min(grid2, key=lambda k: abs(shares(grid2[k])["shadow"] - sa["shadow"]))
        h2 = grid2[d2]
        b = paint(a, h2)
        assert np.array_equal(b[..., 3], a[..., 3]), "alpha changed"
        off = int(sum(1 for c in h2[h2 != ""] if c not in HEX))
        m = {"d1": d1, "d2": d2, "before": s0, "after": shares(h2), "approved": sa,
             "grid_d1_deep": {k: shares(hh)["deep"] for k, hh in grid1.items()},
             "grid_d2_shadow": {k: shares(hh)["shadow"] for k, hh in grid2.items()},
             "changed_px": int(np.any(b != a, -1).sum()), "off_palette": off,
             "body_specks": [body_specks(h0), body_specks(h2)],
             "eye_px": [int(np.isin(h0, EYE).sum()), int(np.isin(h2, EYE).sum())]}
        Image.fromarray(b).save(OUT / f"{v}.png")
        met["views"][v] = m
        res[v] = (ref, a, b) + ((np.asarray(Image.open(T / A.also / f"{v}.png").convert("RGBA")),) if A.also else ())
        bf, af, apv = s0, m["after"], sa
        print(f"{v:3} d1 {d1} d2 {d2}  changed {m['changed_px']:4}  "
              + "  ".join(f"{k} {bf[k]}->{af[k]} ({apv[k]})" for k in ("deep", "shadow", "base", "highlight"))
              + f"  specks {m['body_specks'][0]}->{m['body_specks'][1]}  offpal {off}  eye {m['eye_px']}"
              + f"  grid1 {m['grid_d1_deep']}  grid2 {m['grid_d2_shadow']}")
    (WORK / "metrics.json").write_text(json.dumps(met, indent=1))
    board(res, met)


GREY, PAGE, TXT, DIM = (0x5A, 0x60, 0x58, 255), (34, 37, 41, 255), (235, 235, 230), (165, 170, 165)
FB = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
F = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return Image.fromarray(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def diff_img(a, b):
    g = a.copy()
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2])
    grey = (lum * 0.5 + 40).astype(np.uint8)
    g[..., 0], g[..., 1], g[..., 2] = grey, grey, grey
    g[np.any(a != b, -1)] = (255, 40, 220, 255)
    return g


def board(res, met, k=4):
    rows = [("Approved views", "(the craft standard)", lambda r: r[0]),
            ("Kept touch-up", "(now, raw)", lambda r: r[1])]
    if A.also:
        rows.append(("Earlier option", f"({A.also.split('_')[-1]}, raw)", lambda r: r[3]))
    rows += [(f"This option", f"({A.tag}, bevel up to {A.d2_max} px)", lambda r: r[2]),
             ("Changed pixels", "(magenta, kept -> this)", lambda r: diff_img(r[1], r[2]))]
    new_row = len(rows) - 2
    crops = {v: [crop(f(res[v])) for _, _, f in rows] for v in V}
    cw = {v: max(c.width for c in crops[v]) * k + 16 for v in V}
    chh = max(c.height for v in V for c in crops[v]) * k + 16
    lab_w, top = 200, 76
    order = (0, 1, 3, 2) if A.also else (0, 1, 2)
    small = {v: [crop(res[v][i]) for i in order] for v in V}
    mh = max(c.height for v in V for c in small[v])
    s1h, s2h = mh + 30, mh * 2 + 30
    W = max(lab_w + sum(cw.values()) + 8 * len(V) + 20,
            lab_w + sum(sum(c.width * 2 + 12 for c in small[v]) + 16 for v in V) + 20)
    H = top + len(rows) * (chh + 8) + s1h + s2h + 60
    B = Image.new("RGBA", (W, H), PAGE)
    dr = ImageDraw.Draw(B)
    dr.text((12, 10), f"{TITLE} cam35 shade option ({A.tag}, dark bevel up to {A.d2_max} px): undersides and right "
            "faces one step darker. Silhouette unchanged.", font=FB, fill=TXT)
    dr.text((12, 42), "4x on the map grey. Recolour only: alpha identical to the kept touch-up. Shadow plates sink to "
            "the deepest shade except a band on their lit edges; base plates get a dark bevel on bottom and right edges.",
            font=F, fill=DIM)
    y = top
    for ri, (t1, t2, _) in enumerate(rows):
        dr.text((12, y + 8), t1, font=F, fill=TXT)
        dr.text((12, y + 28), t2, font=F, fill=DIM)
        x = lab_w
        for v in V:
            dr.rectangle([x, y, x + cw[v] - 8, y + chh], fill=GREY)
            c = crops[v][ri]
            im = c.resize((c.width * k, c.height * k), Image.NEAREST)
            B.alpha_composite(im, (x + (cw[v] - 8 - im.width) // 2, y + chh - 8 - im.height))
            m = met["views"][v]
            if ri == 0:
                dr.text((x + 6, y + 4), v, font=FB, fill=TXT)
            if ri == new_row:
                dr.text((x + 6, y + 4), f"d1 {m['d1']} d2 {m['d2']}", font=F, fill=TXT)
            if ri == new_row + 1:
                dr.text((x + 6, y + 4), f"{m['changed_px']} px  deep {m['before']['deep']}->{m['after']['deep']} "
                        f"({m['approved']['deep']})", font=F, fill=TXT)
            x += cw[v] + 8
        y += chh + 8
    for scale, label, hh in ((1, "Game size 1x", s1h), (2, "2x", s2h)):
        dr.text((12, y + 8), label, font=F, fill=TXT)
        dr.text((12, y + 28), "approved | kept | earlier | this" if A.also else "approved | kept | this",
                font=F, fill=DIM)
        x = lab_w
        for v in V:
            for c in small[v]:
                im = c.resize((c.width * scale, c.height * scale), Image.NEAREST)
                dr.rectangle([x, y, x + im.width + 8, y + hh - 6], fill=GREY)
                B.alpha_composite(im, (x + 4, y + hh - 10 - im.height))
                x += im.width + 12
            x += 16
        y += hh
    dr.text((12, y + 12), f"Input {A.src}/ untouched. Output {OUT.name}/ (raw, the packer adds sel-out). "
            f"Numbers: cam35_touchup/{A.tag}/metrics.json.", font=F, fill=DIM)
    B.save(WORK / "board.png")


if __name__ == "__main__":
    run()
