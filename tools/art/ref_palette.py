"""A machine's colour ramps measured from a reference image (Claude, 2026-10-15).

    python tools/art/ref_palette.py <machine_id> <reference.png> <out_palette.json> [base_palette.json]

Preston's pixel-art "Mechabeast V2" references (2026-10-15) differ from our sprites mostly in colour, and Codex can only
finish with a machine's existing colours, so the palette has to be right first. Every opaque reference pixel is sorted
into the base palette's colour families with the pixelizer's own rules (hue ranges, minimum saturation, the teal eye),
near-black outline pixels (brightness under MIN_L, 34) are left out, and each family's ramp is rebuilt with the same number
of shades: the pixels sorted by brightness, cut into equal-count bins, the median colour of each bin. A family's extra
top shade, if it had one, becomes the brightest 1% of its pixels. Everything else in the base palette (gamma, edge
settings, notes) is kept. Without a base palette (the gorilla, whose pixelizer uses built-in ramps) a base equivalent
to those built-in families is used.
"""
import colorsys, json, sys
import numpy as np
from PIL import Image

MIN_L = 34   # the references outline in near-black at brightness 20 to 33; those pixels are outline, not material
GORILLA_BASE = {"note": "Gorilla families as tools/art/pixelize_render.py's built-in family() sorts them.", "families": {
    "teal": {"ramp": ["1f6e66", "5fe1d0", "bff7ef"]},
    "orange": {"hue": [0.02, 0.15], "min_sat": 0.22, "ramp": ["4a2f17", "704c2b", "8c5626", "aa692c", "d4853b", "eba655"],
               "extra_top": ["f6c27c"], "match_style": False},
    "green": {"hue": [0.15, 0.45], "min_sat": 0.22, "ramp": ["1f2a1b", "303e29", "3b5a31", "4c713c", "598644", "6c9b4a", "79ac54", "8eb960"],
              "extra_top": ["9fc96f", "b3d686"], "match_style": False},
    "grey": {"ramp": ["181f1c", "2a2c31", "3f3e43", "4c4b52", "5a585f", "69686f", "828188", "9a9aa2", "b4b5bb"],
             "extra_top": ["c9cbd2"], "match_style": False}}}


def family_of(fams, rgb):
    h, s, v = colorsys.rgb_to_hsv(*(np.array(rgb) / 255.0))
    if "teal" in fams and 0.42 <= h <= 0.56 and s > 0.4 and v > 0.4:
        return "teal"
    for f, d in fams.items():
        if "hue" in d:
            h0, h1 = d["hue"]
            inside = h0 <= h <= h1 if h0 <= h1 else (h >= h0 or h <= h1)
            if s >= d.get("min_sat", 0.3) and inside:
                return f
    return "grey"


def main(mid, ref, out, base=None):
    pal = json.load(open(base, encoding="utf-8")) if base else json.loads(json.dumps(GORILLA_BASE))
    fams = pal["families"]
    a = np.array(Image.open(ref).convert("RGBA"))
    px = a[a[..., 3] > 200][:, :3].astype(float)
    lum = 0.299 * px[:, 0] + 0.587 * px[:, 1] + 0.114 * px[:, 2]
    px, lum = px[lum >= MIN_L], lum[lum >= MIN_L]
    who = np.array([family_of(fams, p) for p in px])
    report = {}
    for f, d in fams.items():
        sel = who == f
        if f == "teal" or sel.sum() < 50:
            report[f] = int(sel.sum())
            continue
        fp, fl = px[sel], lum[sel]
        order = np.argsort(fl)
        fp = fp[order]
        n = len(d["ramp"])
        bins = np.array_split(np.arange(len(fp)), n)
        d["ramp"] = ["%02x%02x%02x" % tuple(int(round(c)) for c in np.median(fp[b], axis=0)) for b in bins]
        if d.get("extra_top"):
            top = fp[int(len(fp) * 0.99):]
            d["extra_top"] = ["%02x%02x%02x" % tuple(int(round(c)) for c in np.median(top, axis=0))]
        report[f] = int(sel.sum())
    pal["note"] = (pal.get("note", "").rstrip() + " Ramps measured from %s by tools/art/ref_palette.py (2026-10-15)." % ref.replace("\\", "/")).strip()
    json.dump(pal, open(out, "w", encoding="utf-8"), indent=2)
    print(mid, "pixels per family:", report, "->", out)


if __name__ == "__main__":
    main(*sys.argv[1:5])
