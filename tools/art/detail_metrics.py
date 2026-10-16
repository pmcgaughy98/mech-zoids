"""How much readable detail a pixel sprite carries (Claude, 2026-10-16; Preston: "better versions and more enhanced and
detailed than zoids sprites"). legacy_gap.py measures tone and fill; this measures detail, so "more detailed than
Legacy" is a number, not a feeling. No reference art is read or stored by the project: run it on reference sprites in
the session scratchpad and keep only the numbers.

    python tools/art/detail_metrics.py <sprite.png> [...]      (or --json for machine-readable rows)

Per sprite (opaque pixels only):
  px       opaque pixels;  h, w  its height and width
  colours  distinct colours
  ramp     mean distinct brightness steps per hue family (hue in 12 bins, greys one family)
  clusters same-colour 4-connected regions per 1000 px (more = more separate shapes drawn)
  csize    mean cluster size in px
  single   share of pixels in 1-px clusters (noise when high; glints when few and bright)
  edges    share of neighbouring pixel pairs inside the body that differ in colour
  lines    share of interior pixels on a dark line: darker by 24+ than both neighbours across it (panel lines, seams)
  glints   bright specks per 1000 px: clusters of 1-4 px at least 30 brighter than everything around them
  c8, s8   clusters per 1000 px and single-pixel share counted 8-connected (diagonal touches join a shape)
  outline  share of silhouette pixels that are near-black (L < 40); low = selective outline (shaded, own colour)
  contrast mean local brightness spread (3x3 standard deviation)
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage


def lum(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def metrics(img):
    a = np.array(img.convert("RGBA")).astype(int)
    m = a[..., 3] > 128
    if m.sum() < 50:
        return None
    ys, xs = np.nonzero(m)
    a, m = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgb = a[..., :3]
    L = lum(rgb.astype(float))
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    key = np.where(m, key, -1)
    n = int(m.sum())
    cols = np.unique(key[m])
    # ramps: brightness steps per hue family
    fam = {}
    for c in cols:
        r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
        mx, mn = max(r, g, b), min(r, g, b)
        if mx - mn < 24:
            h = -1
        else:
            if mx == r:
                hh = ((g - b) / (mx - mn)) % 6
            elif mx == g:
                hh = (b - r) / (mx - mn) + 2
            else:
                hh = (r - g) / (mx - mn) + 4
            h = int(hh * 2) % 12
        fam.setdefault(h, set()).add(int(round((0.299 * r + 0.587 * g + 0.114 * b) / 8)))
    big = [len(v) for v in fam.values() if len(v) >= 2]
    ramp = float(np.mean(big)) if big else 1.0
    # clusters, one label pass per colour; glints: small clusters brighter by 30+ than the brightest pixel touching them
    nclus = 0
    sizes = []
    single = 0
    glints = 0
    cross = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    nclus8 = 0
    single8 = 0
    for c in cols:
        lab, k = ndimage.label(key == c)
        if k == 0:
            continue
        idx = np.arange(1, k + 1)
        s = ndimage.sum(np.ones_like(lab), lab, idx)
        nclus += k
        sizes.extend(s.tolist())
        single += int((s == 1).sum())
        lab8, k8 = ndimage.label(key == c, structure=np.ones((3, 3)))
        s8 = ndimage.sum(np.ones_like(lab8), lab8, range(1, k8 + 1))
        nclus8 += k8
        single8 += int((s8 == 1).sum())
        small = idx[s <= 4]
        if len(small):
            Lc = 0.299 * ((c >> 16) & 255) + 0.587 * ((c >> 8) & 255) + 0.114 * (c & 255)
            # the brightest pixel touching each small cluster from outside it (2026-10-16 fix: the first version
            # masked the cluster's own pixels out of the lookup and so counted every small cluster as a glint)
            other = np.where(m & (key != c), L, -1.0)
            near = ndimage.maximum_filter(other, footprint=cross, mode="constant", cval=-1.0)
            around = np.asarray(ndimage.maximum(near, lab, small))
            glints += int(np.sum((around >= 0) & (Lc - around >= 30)))
    # edges inside the body
    h_pair = m[:, 1:] & m[:, :-1]
    v_pair = m[1:, :] & m[:-1, :]
    diff = (key[:, 1:] != key[:, :-1]) & h_pair
    difv = (key[1:, :] != key[:-1, :]) & v_pair
    edges = (diff.sum() + difv.sum()) / max(1, h_pair.sum() + v_pair.sum())
    # dark lines: darker by 24+ than both neighbours across, horizontally or vertically
    inner = ndimage.binary_erosion(m)
    Lp = np.pad(L, 1, mode="edge")
    c0 = Lp[1:-1, 1:-1]
    across_h = (Lp[1:-1, :-2] - c0 >= 24) & (Lp[1:-1, 2:] - c0 >= 24)
    across_v = (Lp[:-2, 1:-1] - c0 >= 24) & (Lp[2:, 1:-1] - c0 >= 24)
    lines = ((across_h | across_v) & inner).sum() / max(1, inner.sum())
    edge_px = m & ~ndimage.binary_erosion(m)
    outline = (L[edge_px] < 40).mean() if edge_px.any() else 0.0
    w = m.astype(float)
    cnt = ndimage.uniform_filter(w, 3) * 9
    s1 = ndimage.uniform_filter(np.where(m, L, 0.0), 3) * 9
    s2 = ndimage.uniform_filter(np.where(m, L * L, 0.0), 3) * 9
    var = np.maximum(0.0, s2 / np.maximum(cnt, 1) - (s1 / np.maximum(cnt, 1)) ** 2)
    contrast = float(np.sqrt(var)[m].mean())
    return {"px": n, "h": int(m.shape[0]), "w": int(m.shape[1]), "colours": int(len(cols)), "ramp": round(ramp, 2),
            "clusters": round(1000 * nclus / n, 1), "csize": round(float(np.mean(sizes)), 2), "single": round(single / n, 3),
            "c8": round(1000 * nclus8 / n, 1), "s8": round(single8 / n, 3),
            "edges": round(float(edges), 3), "lines": round(float(lines), 3), "glints": round(1000 * glints / n, 2),
            "outline": round(float(outline), 3), "contrast": round(contrast, 1)}


if __name__ == "__main__":
    as_json = "--json" in sys.argv
    rows = []
    for p in [x for x in sys.argv[1:] if not x.startswith("--")]:
        r = metrics(Image.open(p))
        if r is None:
            continue
        r["file"] = p
        rows.append(r)
        if not as_json:
            print("%-50s " % p[-50:] + "  ".join("%s %s" % (k, v) for k, v in r.items() if k != "file"))
    if as_json:
        print(json.dumps(rows))
