"""Turn a render of a 3D machine into a battle sprite by the rules measured from Zoids Legacy
(docs/reference/sprite-rules-legacy-2026-10-12.md). Claude, 2026-10-12.

    python tools/art/pixelize_render.py <render.png> <out.png> [height_px | xSCALE]

1. Every render pixel is sorted into a colour family (body green, metal grey, orange accent, teal eye) and given a
   shade from that family's own ramp by its brightness: long grey ramp, shorter green and orange, 3-step eye.
2. Downscale by taking the most common shade in each block (no blending, so no blur).
3. Edges take a darker shade of their own colour, never black (only 4% of Legacy edge pixels are the darkest
   colours); top edges get a one-shade light rim (light from above on all 93 sprites).
4. A flat violet-grey shadow line under the feet.
Palette: the gorilla's own colours from scripts/data/machines.gd, nothing from the references.
"""
import colorsys, os, sys
from collections import Counter
from PIL import Image
import numpy as np


def ramp(dark, light, n):
    d, l = np.array(dark, float), np.array(light, float)
    return [tuple(int(round(v)) for v in d + (l - d) * i / (n - 1)) for i in range(n)]


hexc = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
RAMPS = {   # dark -> light, measured from Preston's own picked sprite (docs/art/ape-rd-2026-10-11): his palette
    "green": [hexc(h) for h in ("1f2a1b", "303e29", "3b5a31", "4c713c", "598644", "6c9b4a", "79ac54", "8eb960")],
    "grey": [hexc(h) for h in ("181f1c", "2a2c31", "3f3e43", "4c4b52", "5a585f", "69686f", "828188", "9a9aa2", "b4b5bb")],
    "orange": [hexc(h) for h in ("4a2f17", "704c2b", "8c5626", "aa692c", "d4853b", "eba655")],
    "teal": [hexc(h) for h in ("1f6e66", "5fe1d0", "bff7ef")],
}
# Pass 43 (Preston: "refine it to look like a Zoids sprite, more competitive"). Measured on 8 Legacy battle sprites:
# light from above (top edges +50 to +107 brighter than bottom), only 9-23% of edges near-black (a light-following
# outline, not a black ring), ~15% highlights, 27-54 colours. Extra shades beyond Preston's ramps carry that:
EXTRA_TOP = {"green": [hexc("9fc96f"), hexc("b3d686")], "grey": [hexc("c9cbd2")], "orange": [hexc("f6c27c")]}
EXTRA_BOTTOM = {"grey": [hexc("1c2129"), hexc("272d38")]}   # cool shadows, as Legacy greys lean blue
HIGHLIGHT_RANK = tuple(float(v) for v in os.environ.get("PIXEL_HIGHLIGHT_RANK", "0.86,0.95").split(","))   # gorilla pass 39: his master is 7% highlights, ours were 14%; the gorilla round sets 0.93,0.975
# Flat eye mode (pass 38, the gorilla's visor, 2026-10-12): a one-line visor is dozens of teal pixels, and stretching
# them over the three-shade eye ramp painted its lit third near-white and dropped its shadowed middle to grey. With
# PIXEL_EYE_FLAT=1 the eye family is the middle shade, the dark shade only where the render is dim, the highlight
# only on the brightest 3% (a Legacy visor is one flat colour with a glint, not a gradient).
EYE_FLAT = os.environ.get("PIXEL_EYE_FLAT") == "1"   # brightness ranks above these get the first and second extra highlight
LEGACY_OUTLINE = True
GAMMA = 1.35   # > 1 pushes shades toward the dark end: the renders are lit brighter than the sprite reads
EDGE_DARKEN = 3
SEAM_SHARE = float(os.environ.get("PIXEL_SEAM_SHARE", "0.12"))   # Legacy look (2026-10-14) sets 0.35: plate lines only where a block is mostly seam. 
OUTLINE = hexc("181f1c")   # Preston's sprites outline the silhouette in near-black (Legacy does not; his look wins)
STYLE_REF = "docs/art/ape-rd-2026-10-11/ape_native.png"   # his master: how often each shade of each ramp is used


def style_cdf():
    """Per colour family, the cumulative share of each ramp shade in Preston's master (outline pixels left out)."""
    import os
    if not os.path.exists(STYLE_REF):
        return {}
    a = np.array(Image.open(STYLE_REF).convert("RGBA")).astype(int)
    counts = {f: np.zeros(len(r)) for f, r in RAMPS.items()}
    for px in a[a[..., 3] > 128][:, :3]:
        if np.abs(px - np.array(OUTLINE)).sum() < 30:
            continue
        f = family(px)
        r = np.array(RAMPS[f])
        counts[f][np.abs(r - px).sum(1).argmin()] += 1
    return {f: np.cumsum(c) / c.sum() for f, c in counts.items() if c.sum() > 0}   # share of a sprite pixel's block that must be a part boundary to draw a plate line
SHADOW = [hexc("2c2838"), hexc("403a52")]


def family(rgb):
    h, s, v = colorsys.rgb_to_hsv(*(np.array(rgb) / 255.0))
    if s < 0.22:
        return "grey"
    if 0.42 <= h <= 0.56 and v > (0.3 if EYE_FLAT else 0.5):   # flat-eye mode keeps a shadowed visor teal
        return "teal"
    if 0.02 <= h <= 0.15:
        return "orange"
    if 0.15 < h < 0.45:
        return "green"
    return "grey"


_DIRS = np.array([(0.0, 0.0, 1.0)] + [(np.sin(t) * np.cos(q), np.sin(t) * np.sin(q), np.cos(t))
                  for t in (np.radians(45), np.radians(70)) for q in np.radians(np.arange(0, 360, 45))])


def _snap_normal(vs):
    """The mean of a block's winning normals, renormalized and snapped to the nearest of 17 directions (facing, 8 at
    45 degrees, 8 at 70): flat faces stay flat and frames do not shimmer. Opposite normals that cancel out fall back
    to the most common snapped direction."""
    m = vs.mean(0)
    if np.linalg.norm(m) < 0.3:
        picks = (vs @ _DIRS.T).argmax(1)
        return _DIRS[np.bincount(picks).argmax()]
    return _DIRS[(_DIRS @ (m / np.linalg.norm(m))).argmax()]


def main(src, out, height=110, fixed_scale=None):
    im = Image.open(src).convert("RGBA")
    bb = im.getchannel("A").point(lambda a: 255 if a > 128 else 0).getbbox()
    if os.environ.get("PIXEL_NO_CROP") == "1":   # animation frames (pass 3): keep the whole fixed-camera canvas
        bb = (0, 0, im.width, im.height)
    im = im.crop(bb)
    # optional part-ID render next to it (<name>_id.png): where two parts meet becomes a dark plate line
    idp = src[:-4] + "_id.png"
    seam = None
    if os.path.exists(idp):
        ida = np.array(Image.open(idp).convert("RGB").crop(bb)).astype(int)
        diff = np.zeros(ida.shape[:2], bool)
        diff[:, 1:] |= np.abs(ida[:, 1:] - ida[:, :-1]).sum(2) > 40
        diff[1:, :] |= np.abs(ida[1:, :] - ida[:-1, :]).sum(2) > 40
        seam = diff
    # optional normal render next to it (<name>_n.png, render_sprite_views.py SPRITE_NORMALS=1): each sprite pixel's
    # normal comes only from the render pixels that won its colour, then snaps to 17 directions (lighting slice,
    # 2026-10-14; reports/Lit pixel sprites in Godot.md). Writes <out>_n.png and the eye pixels as <out>_e.png.
    nrm = None
    if os.path.exists(src[:-4] + "_n.png") and os.environ.get("PIXEL_NORMALS") != "0":
        nrm = np.array(Image.open(src[:-4] + "_n.png").convert("RGB").crop(bb)).astype(float) / 127.5 - 1.0
    a = np.array(im).astype(int)
    H, W = a.shape[:2]
    opaque = a[..., 3] > 128
    fam = np.empty((H, W), object)
    val = np.zeros((H, W))
    for y in range(H):
        for x in range(W):
            if opaque[y, x]:
                fam[y, x] = family(a[y, x, :3])
                val[y, x] = colorsys.rgb_to_hsv(*(a[y, x, :3] / 255.0))[2]
    # shade index per family, from that family's own brightness range in this render (keeps the 3D lighting)
    idx = np.full((H, W), -1)
    tc = np.zeros((H, W))   # the continuous shade position, kept for dithering at sprite resolution
    for f, r in RAMPS.items():
        m = opaque & (fam == f)
        if not m.any():
            continue
        if f == "teal" and EYE_FLAT:
            ranks = val[m].argsort().argsort() / max(m.sum() - 1, 1)
            idx[m] = np.where(val[m] < 0.45, 0, np.where(ranks > 0.97, min(2, len(r) - 1), min(1, len(r) - 1)))
            continue
        lo, hi = np.percentile(val[m], 2), np.percentile(val[m], 98)
        if f in CDF and globals().get("MATCH_STYLE", {}).get(f, True):   # match how often Preston's master uses each
            # shade (by brightness rank); a palette family can opt out ("match_style": false) when its colour must
            # keep its own darkness, e.g. a charcoal frame that the gorilla master's grey distribution lightened
            ranks = val[m].argsort().argsort() / max(m.sum() - 1, 1)
            base = np.searchsorted(CDF[f], ranks, side="left").clip(0, len(r) - 1)
            top = EXTRA_TOP.get(f, [])
            if top:   # highlights: the brightest ranks step past the top of his ramp
                base = np.where(ranks > HIGHLIGHT_RANK[0], len(r), base)
                if len(top) > 1:
                    base = np.where(ranks > HIGHLIGHT_RANK[1], len(r) + 1, base)
            idx[m] = base
        else:
            t = np.clip((val[m] - lo) / max(hi - lo, 1e-6), 0, 1) ** globals().get("GAMMA_BY_FAMILY", {}).get(f, GAMMA)
            idx[m] = np.clip(np.round(t * (len(r) - 1)), 0, len(r) - 1)
            tc[m] = t * (len(r) - 1)
    # downscale: the most common (family, shade) in each block; transparent if most of the block is empty
    scale = fixed_scale or H / float(height)   # a fixed scale keeps all eight views the same size
    oh, ow = int(round(H / scale)), int(round(W / scale))
    out_f = np.empty((oh, ow), object)
    out_i = np.full((oh, ow), -1)
    out_n = np.zeros((oh, ow, 3))
    seams = np.zeros((oh, ow), bool)
    for oy in range(oh):
        for ox in range(ow):
            y0, y1 = min(int(oy * scale), H - 1), min(max(int((oy + 1) * scale), int(oy * scale) + 1), H)
            x0, x1 = min(int(ox * scale), W - 1), min(max(int((ox + 1) * scale), int(ox * scale) + 1), W)
            blk = opaque[y0:y1, x0:x1]
            if blk.mean() < 0.5:
                continue
            c = Counter((fam[y, x], idx[y, x]) for y in range(y0, y1) for x in range(x0, x1) if opaque[y, x])
            # an eye pixel wins its block if present, so the small bright eye survives the downscale
            eye = [k for k in c if k[0] == "teal"]
            out_f[oy, ox], out_i[oy, ox] = eye[0] if eye else c.most_common(1)[0][0]
            if nrm is not None:
                win = (out_f[oy, ox], out_i[oy, ox])
                vs = [nrm[y, x] for y in range(y0, y1) for x in range(x0, x1) if opaque[y, x] and (fam[y, x], idx[y, x]) == win]
                out_n[oy, ox] = _snap_normal(np.array(vs)) if vs else (0.0, 0.0, 1.0)
            f = out_f[oy, ox]
            s_d = globals().get("DITHER", {}).get(f, 0)
            if s_d and not eye and out_i[oy, ox] < len(RAMPS[f]):
                # ordered dither (factory pass, 2026-10-12): the block's mean shade position, quantised against a 2x2
                # Bayer threshold scaled by the family's strength, so blocks between two shades mix them in a pattern
                # (Legacy's busier texture) and blocks near a shade stay flat
                blk = [(y, x) for y in range(y0, y1) for x in range(x0, x1) if opaque[y, x] and fam[y, x] == f]
                mean = float(np.mean([tc[y, x] for y, x in blk]))
                thr = 0.5 + (BAYER2[oy % 2][ox % 2] - 0.5) * s_d
                out_i[oy, ox] = int(np.clip(np.floor(mean + thr), 0, len(RAMPS[f]) - 1))
            if seam is not None and not eye and seam[y0:y1, x0:x1].mean() > globals().get("SEAM_SHARE_PAL", SEAM_SHARE):
                seams[oy, ox] = True
    solid = out_i >= 0
    if globals().get("DESPECKLE"):
        src = out_i.copy()
        for y in range(1, oh - 1):
            for x in range(1, ow - 1):
                f = out_f[y, x]
                if not solid[y, x] or f not in DESPECKLE:
                    continue
                nb = [src[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if out_f[y + dy, x + dx] == f]
                for v in set(nb):
                    if nb.count(v) >= 3 and abs(v - src[y, x]) == 1:
                        out_i[y, x] = v
    for y, x in zip(*np.where(seams & solid)):   # plate lines: the darkest shade of the part's own ramp (Preston's
        # sprites draw them near-black; one shade down read too faint, 2026-10-12). Inside the silhouette only: on the
        # outer edge the light-following edge rule wins, or every scale touching the top edge rings it in near-black.
        if all(0 <= y + dy < oh and 0 <= x + dx < ow and solid[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out_i[y, x] = globals().get("SEAM_SHADE", {}).get(out_f[y, x], int(os.environ.get("PIXEL_SEAM_SHADE", "0")))   # "seam_shade" in a palette (2026-10-14)
    # plate cleanup (2026-10-15; five blind reviewers against the Mechabeast V2 references all named it first: our plates
    # broke into 1-2 px speckle where his are large flat plates with dark seams): every patch of one shade smaller than
    # PIXEL_MIN_CLUSTER pixels (4-connected) takes the shade most of its neighbours have, same family first. The eye is
    # left alone; plate lines and the light edge rows are longer than the limit, so they stay.
    min_cluster = int(os.environ.get("PIXEL_MIN_CLUSTER", "0"))
    if min_cluster > 1:
        from scipy import ndimage
        for _round in range(2):
            keys = {}
            kid = np.full((oh, ow), -1)
            for y, x in zip(*np.where(solid)):
                kid[y, x] = keys.setdefault((out_f[y, x], int(out_i[y, x])), len(keys))
            inv = {v: k for k, v in keys.items()}
            changed = 0
            for k in range(len(keys)):
                if inv[k][0] == "teal":
                    continue
                lab, n = ndimage.label(kid == k)
                if n == 0:
                    continue
                sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
                for ci in np.where(sizes < min_cluster)[0]:
                    ys, xs = np.where(lab == ci + 1)
                    near = Counter()
                    for y, x in zip(ys, xs):
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < oh and 0 <= xx < ow and kid[yy, xx] >= 0 and kid[yy, xx] != k:
                                near[kid[yy, xx]] += 1
                    if not near:
                        continue
                    same = [(c, q) for q, c in near.items() if inv[q][0] == inv[k][0]]
                    best = max(same)[1] if same and max(same)[0] * 2 >= max(near.values()) else near.most_common(1)[0][0]
                    for y, x in zip(ys, xs):
                        out_f[y, x], out_i[y, x] = inv[best][0], inv[best][1]
                        kid[y, x] = best
                    changed += 1
            if not changed:
                break
    # edges: darker shade of their own colour; top edges a light rim instead
    res = out_i.copy()
    for y in range(oh):
        for x in range(ow):
            if not solid[y, x] or out_f[y, x] == "teal":
                continue
            empty = lambda yy, xx: not (0 <= yy < oh and 0 <= xx < ow) or not solid[yy, xx]
            n = len(RAMPS[out_f[y, x]])
            if LEGACY_OUTLINE and empty(y - 1, x):
                res[y, x] = min(full_len(out_f[y, x]) - 1, out_i[y, x] + globals().get("TOP_RIM", {}).get(out_f[y, x], 1))   # the light catches the top edge
            elif LEGACY_OUTLINE and (empty(y + 1, x) or empty(y, x - 1) or empty(y, x + 1)):
                res[y, x] = max(0, out_i[y, x] - globals().get("UNDER_DROP", {}).get(out_f[y, x], int(os.environ.get("PIXEL_UNDER_DROP", "3")))) if empty(y + 1, x) else max(-len(EXTRA_BOTTOM.get(out_f[y, x], [])), out_i[y, x] - globals().get("SIDE_DROP", {}).get(out_f[y, x], int(os.environ.get("PIXEL_SIDE_DROP", "4"))))
                floor = globals().get("EDGE_FLOOR", {}).get(out_f[y, x])
                if floor is not None:   # side edges never below the floor; undersides only if the render was lighter,
                    # so the deepest shadow under the body still anchors it (all edges floored measured 0-1%, under Legacy)
                    res[y, x] = max(res[y, x], min(floor, out_i[y, x]) if empty(y + 1, x) else floor)
            elif empty(y - 1, x) or empty(y + 1, x) or empty(y, x - 1) or empty(y, x + 1):
                res[y, x] = -2   # silhouette outline
            elif empty(y - 2, x):
                res[y, x] = min(full_len(out_f[y, x]) - 1, out_i[y, x] + 1)   # light rim just inside the top edge
    img = np.zeros((oh + 3, ow + 4, 4), np.uint8)
    for y in range(oh):
        for x in range(ow):
            if solid[y, x]:
                img[y, x + 2, :3] = OUTLINE if res[y, x] == -2 else shade(out_f[y, x], res[y, x])
                img[y, x + 2, 3] = 255
    # ground shadow under the lowest pixels, a little wider than the feet
    span = max(2, int(round(oh * float(os.environ.get("PIXEL_SHADOW_SPAN", "0")))))   # Legacy look: the line runs under every
    # foot in the bottom rows, not only the lowest (a raised, turned camera puts the far feet higher)
    # 2026-10-15 (Codex, gorilla finish report): animation frames (PIXEL_NO_CROP) get no ground line, as before the
    # 2026-10-14 span change. Their canvas ends below the feet; when the feet came within the span of the bottom (the
    # gorilla's camera) the line was drawn at the canvas bottom, detached, export_anim.py took it for the feet and the
    # gorilla drew 26 px too high. The other five never got a line. Cropped sprites end at their feet: unchanged.
    low_rows = np.where(solid.any(1))[0]
    y_low = int(low_rows.max()) if len(low_rows) else oh - 1
    feet = [] if os.environ.get("PIXEL_NO_CROP") == "1" else         [x for x in range(ow) if any(solid[y_low - r, x] for r in range(span) if y_low - r >= 0)]
    if feet:
        x0, x1 = min(feet), max(feet) + 4
        for x in range(x0, x1 + 1):
            for y, c in ((y_low + 1, SHADOW[1]), (y_low + 2, SHADOW[0])):
                if img[y, x, 3] == 0:
                    img[y, x, :3] = c; img[y, x, 3] = 255
    res_img = Image.fromarray(img)
    res_img.save(out)
    if nrm is not None:
        nimg = np.zeros_like(img)
        nimg[..., :3] = (128, 128, 255)   # pixels the pixelizer invents (the ground line) face the camera
        nimg[..., 3] = img[..., 3]
        eimg = np.zeros_like(img)
        for y in range(oh):
            for x in range(ow):
                if solid[y, x]:
                    nimg[y, x + 2, :3] = np.round((out_n[y, x] * 0.5 + 0.5) * 255).clip(0, 255)
                    if out_f[y, x] == "teal":
                        eimg[y, x + 2] = img[y, x + 2]
        assert (nimg[..., 3] == img[..., 3]).all()   # the normal map lines up with the sprite, pixel for pixel
        Image.fromarray(nimg).save(out[:-4] + "_n.png")
        Image.fromarray(eimg).save(out[:-4] + "_e.png")
    cols = len(set(map(tuple, img[img[..., 3] > 0][:, :3])))
    print(f"{out}: {res_img.size[0]}x{res_img.size[1]} px, {cols} colours")


# Per-creature palette (creature factory, 2026-10-12): PIXEL_PALETTE=tools/art/palettes/<id>.json replaces the
# gorilla's ramps, colour families and extra shades; the shade balance then comes from the render's own lighting.
import os, json
if os.environ.get("PIXEL_PALETTE"):
    _pal = json.load(open(os.environ["PIXEL_PALETTE"], encoding="utf-8"))["families"]
    RAMPS = {f: [hexc(h) for h in d["ramp"]] for f, d in _pal.items()}
    EXTRA_TOP = {f: [hexc(h) for h in d.get("extra_top", [])] for f, d in _pal.items() if d.get("extra_top")}
    EXTRA_BOTTOM = {f: [hexc(h) for h in d.get("extra_bottom", [])] for f, d in _pal.items() if d.get("extra_bottom")}
    FAMILY_HUES = [(f, d["hue"][0], d["hue"][1], d.get("min_sat", 0.3)) for f, d in _pal.items() if "hue" in d]
    STYLE_REF = ""
    GAMMA_BY_FAMILY = {f: d["gamma"] for f, d in _pal.items() if "gamma" in d}
    EDGE_FLOOR = {f: d["edge_floor"] for f, d in _pal.items() if "edge_floor" in d}
    DESPECKLE = {f for f, d in _pal.items() if d.get("despeckle")}
    DITHER = {f: d["dither"] for f, d in _pal.items() if "dither" in d}
    MATCH_STYLE = {f: d["match_style"] for f, d in _pal.items() if "match_style" in d}
    if "grey" in _pal:   # the ground shadow in the palette's own darkest greys: the fixed shadow colours sat within a
        # few RGB units of every machine's dark greys (near_duplicates.py, after PixelLab's scoring, 2026-10-12)
        _g = _pal["grey"].get("extra_bottom", []) + _pal["grey"]["ramp"]
        SHADOW = [hexc(_g[min(2, len(_g) - 1)]), hexc(_g[min(3, len(_g) - 1)])]   # mid-dark: the darkest read as
        # a near-black edge row under every sprite (factory report v6)
    if json.load(open(os.environ["PIXEL_PALETTE"], encoding="utf-8")).get("shadow"):   # a palette's own ground line (Legacy: violet grey)
        SHADOW = [hexc(h) for h in json.load(open(os.environ["PIXEL_PALETTE"], encoding="utf-8"))["shadow"]]
    if json.load(open(os.environ["PIXEL_PALETTE"], encoding="utf-8")).get("seam_share"):   # plate lines only where a
        # block is mostly seam (2026-10-14: at 0.12 any part boundary through a block marked it; half the wolf was seams)
        SEAM_SHARE_PAL = json.load(open(os.environ["PIXEL_PALETTE"], encoding="utf-8"))["seam_share"]
    TOP_RIM = {f: d["top_rim"] for f, d in _pal.items() if "top_rim" in d}
    UNDER_DROP = {f: d["under_drop"] for f, d in _pal.items() if "under_drop" in d}
    SEAM_SHADE = {f: d["seam_shade"] for f, d in _pal.items() if "seam_shade" in d}   # plate lines a lighter step (Legacy value pass)
    SIDE_DROP = {f: d["side_drop"] for f, d in _pal.items() if "side_drop" in d}

    def family(rgb):
        h, s, v = colorsys.rgb_to_hsv(*(np.array(rgb) / 255.0))
        if "teal" in RAMPS and 0.42 <= h <= 0.53 and s > 0.4 and v > 0.5:
            return "teal"
        for f, h0, h1, ms in FAMILY_HUES:
            inside = h0 <= h <= h1 if h0 <= h1 else (h >= h0 or h <= h1)
            if s >= ms and inside:
                return f
        return "grey"

CDF = style_cdf()
BAYER2 = ((0.125, 0.625), (0.875, 0.375))


def full_len(f):
    return len(RAMPS[f]) + len(EXTRA_TOP.get(f, []))


def shade(f, i):
    """A shade by index: 0..n-1 Preston's ramp, n.. the extra highlights; negative: the darkest base shade, or below
    it the cool extra shadows (-1 = the lightest extra shadow); -3 = the darkest available (an underside edge)."""
    r, top, bot = RAMPS[f], EXTRA_TOP.get(f, []), EXTRA_BOTTOM.get(f, [])
    if i == -3:
        return bot[0] if bot else r[0]
    if i < 0:
        return bot[max(0, len(bot) + i)] if bot else r[0]
    if i >= len(r):
        return top[min(i - len(r), len(top) - 1)] if top else r[-1]
    return r[i]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    arg = sys.argv[3] if len(sys.argv) > 3 else "110"
    # "110" = scale the machine to 110 px tall; "x4.5" = 4.5 render pixels per sprite pixel (same for every view)
    main(sys.argv[1], sys.argv[2], fixed_scale=float(arg[1:])) if arg.startswith("x") else main(sys.argv[1], sys.argv[2], int(arg))
