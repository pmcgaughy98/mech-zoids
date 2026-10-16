"""The detail pixelizer (Claude, 2026-10-16; Preston: "better versions and more enhanced and detailed than zoids
sprites"). Same input and output as tools/art/pixelize_render.py (one render of a machine in, one sprite out, in the
machine's own palette from PIXEL_PALETTE, or the gorilla's built-in one), but it draws each part as its own shape, the
way Zoids Legacy's battle sprites are built, and it does automatically what Codex's hand finish did on all six machines
(docs/reference/sprite-detail-2026-10-16.md: the measurements, the shipped-game techniques and Codex's repeatable rules).

    python tools/art/pixelize_detail.py <render.png> <out.png> [xSCALE]      (default x4.4, as the factory)

Needs beside the render: <render>_piece.png and parts.json (render_sprite_views.py SPRITE_PIECES=1: one exact colour
per piece) and <render>_n.png (SPRITE_NORMALS=1). Per sprite pixel (a block of render pixels), then per part:
1. vote: the block's commonest colour family, an eye pixel winning its block; a thin piece (a barrel, an antenna, a
   blade edge: under THIN render px in all) wins a block it covers a fifth of, so thin parts survive the downscale;
2. tone: the block's commonest shade as pixelize_render.py picks it (the factory's tuned look), on the family ramp;
3. gentle cleanup: inside one part and family, a pixel one shade off its 5x5 neighbourhood's median takes the median;
4. form: a gradient within each part from the normals, light from the upper left and front (one clear light);
5. seams: where a plate meets another plate below or to its right, the upper plate's edge pixel drops two shades in its
   own colour (one-sided, never black); pieces under SEAM_MIN px (bolts) draw no seams;
6. rims: the top row of each part of RIM_MIN px or more, where it has a neighbour of its own part beside it, goes one
   shade lighter (the lit lip of every Legacy plate; Codex's commonest treatment);
7. glints: on metal (PIXEL_GLINT_FAMILIES) parts of 16+ px, the pixel facing the light's half vector most, if it does,
   takes the top highlight; strongest first, at most GLINT_CAP per 1000 px;
8. silhouette: a selective outline in the part's own colour from its local median (top a shade lighter, sides one
   darker, undersides two, never below the third darkest), as Codex's finish does;
9. noise: a lone pixel inside a uniform 4-neighbourhood takes that shade unless it is a rim, seam, glint or eye.
Settings (environment): PIXEL_LIGHT ("x,y,z" camera space, x right, y up, z toward the viewer; -0.55,0.6,0.6),
PIXEL_GRADIENT (0.25), PIXEL_SEAM_MIN (10), PIXEL_RIM_MIN (25), PIXEL_THIN (render px, 160), PIXEL_GLINT_MIN (0.92),
PIXEL_GLINT_FAMILIES (grey), PIXEL_GLINT_CAP (6), PIXEL_RAMP_STEPS (0 = the palette's ramps; N = resampled to N steps,
darks a little cooler and lights a little warmer).
"""
import colorsys
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixelize_render as pr   # noqa: E402  (loads PIXEL_PALETTE: ramps, families, gamma, extra shades)

ENV = os.environ.get
LIGHT = np.array([float(v) for v in ENV("PIXEL_LIGHT", "-0.55,0.6,0.6").split(",")])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = (LIGHT + np.array([0.0, 0.0, 1.0])) / np.linalg.norm(LIGHT + np.array([0.0, 0.0, 1.0]))
GRADIENT = float(ENV("PIXEL_GRADIENT", "0.35"))
SEAM_MIN = int(ENV("PIXEL_SEAM_MIN", "16"))
RIM_MIN = int(ENV("PIXEL_RIM_MIN", "25"))
THIN = int(ENV("PIXEL_THIN", "160"))
GLINT_MIN = float(ENV("PIXEL_GLINT_MIN", "0.92"))
GLINT_FAMILIES = ENV("PIXEL_GLINT_FAMILIES", "grey").split(",")
GLINT_CAP = float(ENV("PIXEL_GLINT_CAP", "4"))
RAMP_STEPS = int(ENV("PIXEL_RAMP_STEPS", "0"))
DESINGLE8 = ENV("PIXEL_DESINGLE8", "1") == "1"   # also resolve pixels with no 8-connected twin (Legacy's single share)
FLATTEN = ENV("PIXEL_FLATTEN", "1") == "1"   # each plate at most three tones around its own median (blind judges: "flatten
# each plate to 2-3 tones in clear bands"; Codex's pangolin scale grouping)
PLATE_MODE = ENV("PIXEL_PLATE_MODE", "1") == "1"   # a 3x3 majority inside each plate after flattening: fills group into
# larger clean shapes (round 2 judges: "mottled fill", "puffy stone blocks", "random patchwork")
SPURS = ENV("PIXEL_SPURS", "1") == "1"   # silhouette cleanup: one-pixel spurs off, one-pixel notches filled (round 2:
# "a ragged fringe of loose pixels with no closed outline")
DARK_OUTLINE = ENV("PIXEL_DARK_OUTLINE", "1") == "1"   # the silhouette in each part's own darkest shade, the top edge one
# lighter, a lit row just inside it (all six blind judges: "no consistent dark outline, the silhouette fades")
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


ROUND = os.environ.get("PIXEL_ROUND") == "1"   # 6b. round parts as lit crescents (off by default)
ROUND_MIN = int(os.environ.get("PIXEL_ROUND_MIN", "12"))
ROUND_MAX = int(os.environ.get("PIXEL_ROUND_MAX", "260"))   # joints, not armour: big round plates went flat (v74)
ROUND_FAMILIES = set(os.environ.get("PIXEL_ROUND_FAMILIES", "grey").split(","))


def _hue_shift(rgb, dh):
    h, s, v = colorsys.rgb_to_hsv(*(np.array(rgb) / 255.0))
    r, g, b = colorsys.hsv_to_rgb((h + dh) % 1.0, s, v)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def family_ramp(f):
    """The family's shades, dark to light: its base ramp and extra highlights (or the same, resampled to RAMP_STEPS)."""
    full = list(pr.RAMPS[f]) + list(pr.EXTRA_TOP.get(f, []))
    if RAMP_STEPS and f != "teal" and len(full) >= 2:
        src = np.array(full, float)
        out = []
        for i, p in enumerate(np.linspace(0, len(src) - 1, RAMP_STEPS)):
            a, b = int(np.floor(p)), min(int(np.floor(p)) + 1, len(src) - 1)
            c = src[a] + (src[b] - src[a]) * (p - a)
            out.append(_hue_shift(tuple(int(round(v)) for v in c), (i / (RAMP_STEPS - 1) - 0.5) * 0.03))
        full = out
    return full


def families_of(rgb, opaque):
    """Family name and HSV value per render pixel (pixelize_render.family, vectorized)."""
    out = np.full(opaque.shape, "", object)
    val = np.zeros(opaque.shape)
    flat = rgb[opaque] / 255.0
    if not len(flat):
        return out, val
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in flat])
    h, s, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    names = np.full(len(flat), "grey", object)
    if hasattr(pr, "FAMILY_HUES"):
        done = np.zeros(len(flat), bool)
        if "teal" in pr.RAMPS:
            t = (h >= 0.42) & (h <= 0.53) & (s > 0.4) & (v > 0.5)
            names[t] = "teal"
            done |= t
        for f, h0, h1, ms in pr.FAMILY_HUES:
            inside = ((h >= h0) & (h <= h1)) if h0 <= h1 else ((h >= h0) | (h <= h1))
            m = ~done & (s >= ms) & inside
            names[m] = f
            done |= m
    else:   # the gorilla's built-in families
        grey = s < 0.22
        teal = ~grey & (h >= 0.42) & (h <= 0.56) & (v > (0.3 if pr.EYE_FLAT else 0.5))
        names[~grey & ~teal & (h >= 0.02) & (h <= 0.15)] = "orange"
        names[~grey & ~teal & (h > 0.15) & (h < 0.45)] = "green"
        names[teal] = "teal"
    out[opaque] = names
    val[opaque] = v
    return out, val


def pixel_index(fam, val, opaque):
    """Each render pixel's shade index exactly as pixelize_render.py's main() assigns it."""
    idx = np.full(fam.shape, -1)
    for f, r in pr.RAMPS.items():
        m = opaque & (fam == f)
        if not m.any():
            continue
        if f == "teal" and pr.EYE_FLAT:
            ranks = val[m].argsort().argsort() / max(m.sum() - 1, 1)
            idx[m] = np.where(val[m] < 0.45, 0, np.where(ranks > 0.97, min(2, len(r) - 1), min(1, len(r) - 1)))
            continue
        lo, hi = np.percentile(val[m], 2), np.percentile(val[m], 98)
        if f in pr.CDF and getattr(pr, "MATCH_STYLE", {}).get(f, True):
            ranks = val[m].argsort().argsort() / max(m.sum() - 1, 1)
            base = np.searchsorted(pr.CDF[f], ranks, side="left").clip(0, len(r) - 1)
            top = pr.EXTRA_TOP.get(f, [])
            if top:
                base = np.where(ranks > pr.HIGHLIGHT_RANK[0], len(r), base)
                if len(top) > 1:
                    base = np.where(ranks > pr.HIGHLIGHT_RANK[1], len(r) + 1, base)
            idx[m] = base
        else:
            t = np.clip((val[m] - lo) / max(hi - lo, 1e-6), 0, 1) ** getattr(pr, "GAMMA_BY_FAMILY", {}).get(f, pr.GAMMA)
            idx[m] = np.clip(np.round(t * (len(r) - 1)), 0, len(r) - 1)
    return idx


def decode_pieces(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(int)
    lv = np.round(a[..., :3] / 255.0 * 15).astype(int)
    idx = (lv[..., 0] << 8) | (lv[..., 1] << 4) | lv[..., 2]
    idx[a[..., 3] < 128] = 0
    return idx


def block_mode(blk, keys, valid, nb):
    """Per block, the commonest key among the valid pixels (-1 for none)."""
    k = blk[valid].astype(np.int64) * (1 << 20) + keys[valid]
    uk, uc = np.unique(k, return_counts=True)
    out = np.full(nb, -1, np.int64)
    for j in np.lexsort((uc, uk >> 20)):   # within each block, the largest count last
        out[uk[j] >> 20] = uk[j] & ((1 << 20) - 1)
    return out


def main(src, dst, scale=4.4):
    im = np.array(Image.open(src).convert("RGBA")).astype(int)
    nrm = np.array(Image.open(src[:-4] + "_n.png").convert("RGB")).astype(float) / 127.5 - 1.0
    piece = decode_pieces(src[:-4] + "_piece.png")
    opaque = im[..., 3] > 128
    if ENV("PIXEL_NO_CROP") != "1":
        ys, xs = np.nonzero(opaque)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        im, nrm, piece, opaque = im[y0:y1, x0:x1], nrm[y0:y1, x0:x1], piece[y0:y1, x0:x1], opaque[y0:y1, x0:x1]
    H, W = opaque.shape
    fam, val = families_of(im[..., :3], opaque)
    names = sorted(set(fam[opaque]))
    fi = np.full((H, W), -1)
    for k, f in enumerate(names):
        fi[fam == f] = k
    pidx = pixel_index(fam, val, opaque)
    oh, ow = int(round(H / scale)), int(round(W / scale))
    by = np.minimum((np.arange(H) / scale).astype(int), oh - 1)
    bx = np.minimum((np.arange(W) / scale).astype(int), ow - 1)
    blk = by[:, None] * ow + bx[None, :]
    nb = oh * ow
    bsize = np.bincount(blk.ravel(), minlength=nb).astype(float)
    cover = np.bincount(blk.ravel(), weights=opaque.ravel().astype(float), minlength=nb) / np.maximum(1, bsize)
    solid = (cover >= 0.5).reshape(oh, ow)
    if SPURS:   # twice: spurs (a pixel with at most one solid 4-neighbour) off; notches (an empty pixel with three or four
        # solid 4-neighbours) filled
        for _ in range(2):
            pad = np.pad(solid, 1)
            n4 = pad[:-2, 1:-1].astype(int) + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]
            solid = (solid & (n4 >= 2)) | (~solid & (n4 >= 3))
    # 1. vote: family by count, an eye wins its block; a thin piece wins a block it covers a fifth of
    counts = np.zeros((nb, len(names)))
    np.add.at(counts, (blk[opaque], fi[opaque]), 1)
    win_f = counts.argmax(1)
    has_eye = counts[:, names.index("teal")] > 0 if "teal" in names else np.zeros(nb, bool)
    if "teal" in names:
        win_f = np.where(has_eye, names.index("teal"), win_f)
    area = np.bincount(piece[opaque], minlength=int(piece.max()) + 1)
    thin = (area > 0) & (area < THIN)
    thin_px = opaque & thin[piece]
    win_p = np.full(nb, -1, np.int64)
    if thin_px.any():
        k = blk[thin_px].astype(np.int64) * (1 << 20) + piece[thin_px]
        uk, uc = np.unique(k, return_counts=True)
        for j in np.lexsort((uc, uk >> 20)):
            b = int(uk[j] >> 20)
            if uc[j] >= 0.2 * bsize[b]:
                win_p[b] = uk[j] & ((1 << 20) - 1)
    win_p = np.where(has_eye, -1, win_p)
    if (win_p >= 0).any():   # a thin-piece block takes that piece's family
        pfam = block_mode(blk, fi, opaque & thin_px, nb)
        win_f = np.where((win_p >= 0) & (pfam >= 0), pfam, win_f)
    sel = opaque & (fi == win_f[blk]) & ((win_p[blk] < 0) | (piece == win_p[blk]))
    part = block_mode(blk, piece, sel, nb)
    part = np.where(win_p >= 0, win_p, part).reshape(oh, ow)
    part[~solid] = -1
    mode = (block_mode(blk, pidx + 8, sel, nb) - 8).reshape(oh, ow)
    nsum = np.zeros((nb, 3))
    np.add.at(nsum, blk[sel], nrm[sel])
    n_img = (nsum / np.maximum(1e-6, np.linalg.norm(nsum, axis=1))[:, None]).reshape(oh, ow, 3)
    winf = win_f.reshape(oh, ow)
    if SPURS:   # a filled notch takes its neighbours' family, part, shade and normal
        no_vote = solid & (counts.sum(1).reshape(oh, ow) == 0)
        for y, x in zip(*np.nonzero(no_vote)):
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < oh and 0 <= xx < ow and solid[yy, xx] and not no_vote[yy, xx]:
                    winf[y, x], part[y, x], mode[y, x], n_img[y, x] = winf[yy, xx], part[yy, xx], mode[yy, xx], n_img[yy, xx]
                    break
    famname = np.array(names, object)[winf]
    eye = solid & (famname == "teal")
    ramps = {f: family_ramp(f) for f in names}
    tops = {f: len(ramps[f]) - 1 for f in names}
    # 2. tone
    idx = np.zeros((oh, ow), int)
    for k, f in enumerate(names):
        m = solid & (winf == k)
        if not m.any():
            continue
        n_old = pr.full_len(f)
        base = np.clip(mode[m], 0, n_old - 1)
        if RAMP_STEPS and f != "teal":
            base = np.round(base / max(1, n_old - 1) * tops[f]).astype(int)
        idx[m] = base
    regions = []   # one mask per connected region of a part
    for pid in np.unique(part[solid]):
        pl, pn = ndimage.label(part == pid)
        for i in range(1, pn + 1):
            regions.append(pl == i)
    psize = np.zeros(part.shape, int)
    for m in regions:
        psize[m] = m.sum()
    # 3. gentle cleanup inside each part and family
    src_i = idx.copy()
    for y, x in zip(*np.nonzero(solid & ~eye)):
        if src_i[y, x] < 2:
            continue
        y0_, y1_, x0_, x1_ = max(0, y - 2), min(oh, y + 3), max(0, x - 2), min(ow, x + 3)
        win = (part[y0_:y1_, x0_:x1_] == part[y, x]) & (winf[y0_:y1_, x0_:x1_] == winf[y, x])
        if win.sum() >= 8:
            med = int(np.median(src_i[y0_:y1_, x0_:x1_][win]))
            if abs(med - src_i[y, x]) == 1:
                idx[y, x] = med
    # a piece can hold more than one colour family (the block vote), and eyes keep their own shades: the plate rules
    # below work on each family inside each region separately (2026-10-16: an eye pixel took a grey shade index)
    fam_regions = []
    for m in regions:
        for k in np.unique(winf[m]):
            sub = m & (winf == k) & ~eye
            if sub.any() and names[k] != "teal":
                fam_regions.append((sub, names[k]))
    if FLATTEN:
        for m, f in fam_regions:
            if m.sum() >= 6:
                med = int(np.median(idx[m]))
                idx[m] = np.clip(idx[m], med - 1, med + 1)
    if PLATE_MODE:
        src_m = idx.copy()
        for y, x in zip(*np.nonzero(solid & ~eye)):
            y0_, y1_, x0_, x1_ = max(0, y - 1), min(oh, y + 2), max(0, x - 1), min(ow, x + 2)
            win = (part[y0_:y1_, x0_:x1_] == part[y, x]) & (winf[y0_:y1_, x0_:x1_] == winf[y, x])
            if win.sum() >= 6:
                vals = src_m[y0_:y1_, x0_:x1_][win].tolist()
                best = max(set(vals), key=vals.count)
                if vals.count(best) >= 5:
                    idx[y, x] = best
    # 4. form: a gradient within each part from the normals
    lam = n_img @ LIGHT
    for m, f in fam_regions:
        if m.sum() >= 4:
            idx[m] = np.clip(idx[m] + np.round(GRADIENT * tops[f] * (lam[m] - lam[m].mean())).astype(int), 0, tops[f])
    # 5. seams and 6. rims
    seam = np.zeros((oh, ow), bool)
    rim = np.zeros((oh, ow), bool)
    for y, x in zip(*np.nonzero(solid & ~eye)):
        p = part[y, x]
        for dy, dx in ((1, 0), (0, 1)):
            yy, xx = y + dy, x + dx
            if yy < oh and xx < ow and solid[yy, xx] and part[yy, xx] != p and not eye[yy, xx] \
                    and psize[y, x] >= SEAM_MIN and psize[yy, xx] >= SEAM_MIN:
                seam[y, x] = True
        if not seam[y, x] and psize[y, x] >= RIM_MIN and y > 0 and solid[y - 1, x] and part[y - 1, x] != p:
            if (x > 0 and part[y, x - 1] == p) or (x + 1 < ow and part[y, x + 1] == p):
                rim[y, x] = True
    res = idx.copy()
    for k, f in enumerate(names):
        m = winf == k
        res[m & seam] = np.maximum(0, idx[m & seam] - 2)
        res[m & rim] = np.minimum(tops[f], idx[m & rim] + 1)
    # 6b. round parts (2026-10-16, gorilla model pass; blind judges: joints and guns "should read as cylinders with a
    # shine"). PIXEL_ROUND=1: a part whose outline fills its bounding ellipse is drawn the way Legacy draws a joint:
    # its outer band lit on the side toward the light, dark on the far side, one highlight pixel inside the lit edge.
    # Each concentric piece (disc, ring, hub) gets its own crescent, so a joint reads as nested lit rings.
    round_px = np.zeros((oh, ow), bool)
    if ROUND:
        ix, iy = LIGHT[0], -LIGHT[1]   # toward the light in image space (x right, y down)
        il = (ix * ix + iy * iy) ** 0.5
        ix, iy = ix / il, iy / il
        for m, f in fam_regions:
            ys, xs = np.nonzero(m)
            if not ROUND_MIN <= len(ys) <= ROUND_MAX or f not in ROUND_FAMILIES:
                continue
            h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
            fill = len(ys) / (np.pi / 4 * w * h)
            if min(w, h) < 4 or min(w, h) / max(w, h) < 0.55 or not 0.8 <= fill <= 1.12:
                continue
            cy, cx = (ys.max() + ys.min()) / 2, (xs.max() + xs.min()) / 2
            oy, ox = (ys - cy) / (h / 2), (xs - cx) / (w / 2)
            r = np.hypot(oy, ox) + 1e-6
            d = (ox * ix + oy * iy) / r   # +1 on the side toward the light
            base = int(np.median(idx[ys, xs]))
            band = r >= 0.55
            lit, dark = band & (d > 0.3), band & (d < -0.3)
            res[ys, xs] = base
            res[ys[lit], xs[lit]] = min(tops[f], base + 2)
            res[ys[dark], xs[dark]] = max(0, base - 2)
            if w >= 5 and h >= 5:   # the shine: just inside the lit edge
                hy, hx = int(round(cy + iy * h * 0.22)), int(round(cx + ix * w * 0.22))
                if m[hy, hx]:
                    res[hy, hx] = tops[f]
            round_px[ys, xs] = True
    # 7. glints on metal
    spec = n_img @ HALF
    glint = np.zeros((oh, ow), bool)
    cands = []
    for m in regions:
        if m.sum() < 16:
            continue
        ys, xs = np.nonzero(m & ~seam)
        if not len(ys):
            continue
        j = spec[ys, xs].argmax()
        y, x = ys[j], xs[j]
        if famname[y, x] in GLINT_FAMILIES and spec[y, x] >= GLINT_MIN:
            cands.append((spec[y, x], y, x))
    for _s, y, x in sorted(cands, reverse=True)[:int(GLINT_CAP * solid.sum() / 1000)]:
        res[y, x] = tops[famname[y, x]]
        glint[y, x] = True
    if eye.any():   # the eye's glint on its brightest pixel
        ys, xs = np.nonzero(eye)
        j = int(np.argmax(mode[eye]))
        res[ys[j], xs[j]] = tops["teal"]
    # 8. silhouette: a selective outline from the part's own local median (or, DARK_OUTLINE, the part's darkest shades)
    final = res.copy()
    if DARK_OUTLINE:
        def empty(yy, xx):
            return not (0 <= yy < oh and 0 <= xx < ow) or not solid[yy, xx]
        edge = np.zeros((oh, ow), bool)
        for y, x in zip(*np.nonzero(solid & ~eye)):
            if empty(y - 1, x):
                final[y, x] = min(1, tops[famname[y, x]])
                edge[y, x] = True
                if y + 1 < oh and solid[y + 1, x] and not eye[y + 1, x] and not empty(y + 1, x) and not seam[y + 1, x]:
                    final[y + 1, x] = min(tops[famname[y + 1, x]], res[y + 1, x] + 1)   # the lit row inside the top edge
            elif empty(y + 1, x) or empty(y, x - 1) or empty(y, x + 1):
                final[y, x] = 0
                edge[y, x] = True
        # the eyes sit in a dark recess: their non-eye neighbours take their family's darkest shade
        for y, x in zip(*np.nonzero(eye)):
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < oh and 0 <= xx < ow and solid[yy, xx] and not eye[yy, xx]:
                    final[yy, xx] = 0
    for y, x in zip(*np.nonzero(solid & ~eye)) if not DARK_OUTLINE else []:
        def empty(yy, xx):
            return not (0 <= yy < oh and 0 <= xx < ow) or not solid[yy, xx]
        if not (empty(y - 1, x) or empty(y + 1, x) or empty(y, x - 1) or empty(y, x + 1)):
            continue
        y0_, y1_, x0_, x1_ = max(0, y - 2), min(oh, y + 3), max(0, x - 2), min(ow, x + 3)
        win = (part[y0_:y1_, x0_:x1_] == part[y, x]) & (winf[y0_:y1_, x0_:x1_] == winf[y, x])
        med = int(np.median(res[y0_:y1_, x0_:x1_][win])) if win.sum() >= 3 else int(res[y, x])
        cur = int(res[y, x])
        if empty(y - 1, x):
            final[y, x] = max(cur, min(med + 1, cur + 1, tops[famname[y, x]]))
        elif empty(y + 1, x):
            final[y, x] = max(min(2, cur), min(cur, med - 2))
        else:
            final[y, x] = max(min(2, cur), min(cur, med - 1))
    # 9. noise
    keyimg = np.where(solid, winf * 64 + final, -1)
    for y in range(1, oh - 1):
        for x in range(1, ow - 1):
            if not solid[y, x] or eye[y, x] or glint[y, x] or seam[y, x] or rim[y, x]:
                continue
            nbk = {keyimg[y + dy, x + dx] for dy, dx in N4}
            if len(nbk) == 1 and -1 not in nbk and keyimg[y, x] not in nbk:
                v = nbk.pop()
                if v // 64 == winf[y, x]:
                    final[y, x] = v % 64
    if DESINGLE8:   # a pixel with no same-shade pixel among its 8 neighbours takes the commonest neighbour shade of its
        # own family (rims, seams, glints and eyes keep theirs: they are the designed single pixels)
        keyimg = np.where(solid, winf * 64 + final, -1)
        out = final.copy()
        for y in range(1, oh - 1):
            for x in range(1, ow - 1):
                if not solid[y, x] or eye[y, x] or glint[y, x] or seam[y, x] or rim[y, x]:
                    continue
                nbr = keyimg[y - 1:y + 2, x - 1:x + 2].ravel().tolist()
                me = nbr.pop(4)
                if me in nbr:
                    continue
                same = [v for v in nbr if v >= 0 and v // 64 == winf[y, x]]
                if len(same) >= 5:
                    out[y, x] = max(set(same), key=same.count) % 64
        final = out
    img = np.zeros((oh + 3, ow + 4, 4), np.uint8)
    over = 0
    for y, x in zip(*np.nonzero(solid)):
        if not 0 <= final[y, x] <= tops[famname[y, x]]:   # a rule above stepped out of its family's ramp: say so, clamp
            over += 1
            final[y, x] = min(max(0, final[y, x]), tops[famname[y, x]])
        img[y, x + 2, :3] = ramps[famname[y, x]][final[y, x]]
        img[y, x + 2, 3] = 255
    if ENV("PIXEL_NO_CROP") != "1":   # the ground line under the feet, as pixelize_render.py draws it
        y_low = int(np.where(solid.any(1))[0].max())
        span = max(2, int(round(oh * float(ENV("PIXEL_SHADOW_SPAN", "0")))))
        feet = [x for x in range(ow) if any(solid[y_low - r, x] for r in range(span) if y_low - r >= 0)]
        if feet:
            for x in range(min(feet), max(feet) + 5):
                for y, c in ((y_low + 1, pr.SHADOW[1]), (y_low + 2, pr.SHADOW[0])):
                    if img[y, x, 3] == 0:
                        img[y, x, :3] = c
                        img[y, x, 3] = 255
    Image.fromarray(img).save(dst)
    cols = len(set(map(tuple, img[img[..., 3] > 0][:, :3])))
    print(f"{dst}: {img.shape[1]}x{img.shape[0]} px, {cols} colours" + (f"  WARNING: {over} shades clamped" if over else ""))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    arg = sys.argv[3] if len(sys.argv) > 3 else "x4.4"
    main(sys.argv[1], sys.argv[2], float(arg[1:]))
