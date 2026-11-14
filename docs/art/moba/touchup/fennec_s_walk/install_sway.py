"""Fennec trot sway: finish and install (Preston: "Keep, do all views").

1. Pinholes: the lean can seal a 1 px slit at a leg seam for one frame. Enclosed holes of 8 px or less are filled
   with their most common dark neighbour (ink 141218, charcoal 211e27 or 3d3a44), else their most common neighbour.
   Bigger enclosed gaps (se f2, 17 px) stay see-through: they read as the ground between the legs, as in the frames
   either side.
2. Checks every frame against the installed touch-up: one piece, binary alpha, only its colours, the bottom 8 rows
   equal, eye pixel counts equal.
3. Install: the current touchup/fennec_s_walk frames, GIFs, board and .aseprite go to pre_sway/ first; then the new
   frames, per-view GIFs (3x, game sel-out, 100 ms), board_sway_all.png, sway.py, this script and sway_report.json.
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, label

HERE = Path(__file__).parent
DST = Path(r"D:/dev/new-mech-rpg/docs/art/moba/touchup/fennec_s_walk")
sys.path.insert(0, r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim")
from selout_rhino import selout  # noqa: E402

VIEWS = ["s", "se", "e", "ne", "n"]
DARK = ["141218", "211e27", "3d3a44"]
EYES = [(0x3F, 0xE8, 0xB0), (0xC8, 0xFF, 0xF0), (0xF6, 0xFF, 0xFB)]
LOCK = 8


def hexc(p):
    return "%02x%02x%02x" % tuple(int(v) for v in p[:3])


def fill_pinholes(a):
    a = a.copy()
    m = a[..., 3] > 0
    lab, n = label(binary_fill_holes(m) & ~m)
    filled = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) > 8:
            continue
        nb = Counter()
        for y, x in zip(ys, xs):
            for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                if m[y + dy, x + dx]:
                    nb[hexc(a[y + dy, x + dx])] += 1
        dark = [c for c in nb if c in DARK]
        c = max(dark, key=nb.get) if dark else nb.most_common(1)[0][0]
        rgb = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
        for y, x in zip(ys, xs):
            a[y, x, :3], a[y, x, 3] = rgb, 255
        filled.append({"px": int(len(ys)), "at": [int(xs.min()), int(ys.min())], "colour": c})
    return a, filled


def check(a, src):
    m, m0 = a[..., 3] > 0, src[..., 3] > 0
    _, n = label(m, np.ones((3, 3), int))
    b = int(np.nonzero(m.any(1))[0].max())
    b0 = int(np.nonzero(m0.any(1))[0].max())
    eye = [int(((a[..., :3] == c).all(-1) & m).sum()) for c in EYES]
    eye0 = [int(((src[..., :3] == c).all(-1) & m0).sum()) for c in EYES]
    r = {"pieces": int(n), "alpha_binary": bool(set(np.unique(a[..., 3])) <= {0, 255}),
         "colours_ok": {hexc(p) for p in a[m]} <= {hexc(p) for p in src[m0]},
         "foot_rows_same": bool(b == b0 and np.array_equal(a[b - LOCK + 1:b + 1], src[b0 - LOCK + 1:b0 + 1])),
         "eyes_same": eye == eye0, "hole_px": int((binary_fill_holes(m) & ~m).sum())}
    r["pass"] = r["pieces"] == 1 and r["alpha_binary"] and r["colours_ok"] and r["foot_rows_same"] and r["eyes_same"]
    return r


def main():
    old = {v: [np.asarray(Image.open(DST / f"frames/{v}_f{i}.png").convert("RGBA")) for i in range(8)] for v in VIEWS}
    new, rep = {}, {"method": "sway.py (per-row warp, feet locked) + pinhole fill", "views": {}}
    for v in VIEWS:
        cfg = json.loads((HERE / f"report_{v}.json").read_text())
        fr, rows = [], []
        for i in range(8):
            a = np.asarray(Image.open(HERE / f"frames/{v}_f{i}.png").convert("RGBA"))
            a, filled = fill_pinholes(a)
            r = check(a, old[v][i])
            r["filled"] = filled
            rows.append(r)
            fr.append(a)
        new[v] = fr
        rep["views"][v] = {"dx": cfg["dx"], "dy": cfg["dy"], "hip": cfg["hip"], "ear_base": cfg["ear_base"],
                           "frames": rows}
        print(v, "pass", all(r["pass"] for r in rows), "holes", [r["hole_px"] for r in rows],
              "filled", [sum(f["px"] for f in r["filled"]) for r in rows])
    ok = all(r["pass"] for v in VIEWS for r in rep["views"][v]["frames"])
    rep["all_pass"] = ok
    print("ALL PASS", ok)
    if not ok:
        return
    bak = DST / "pre_sway"
    if bak.exists():
        raise SystemExit("pre_sway/ already exists; not overwriting the backup")
    (bak / "frames").mkdir(parents=True)
    for p in (DST / "frames").glob("*.png"):
        shutil.copy2(p, bak / "frames" / p.name)
    for p in list(DST.glob("*.gif")) + list(DST.glob("*.aseprite")) + [DST / "board_game.png"]:
        if p.exists():
            shutil.copy2(p, bak / p.name)
    for v in VIEWS:
        for i, a in enumerate(new[v]):
            Image.fromarray(a).save(DST / f"frames/{v}_f{i}.png")
    for p in (HERE / "sway.py", Path(__file__)):
        shutil.copy2(p, DST / p.name)
    (DST / "sway_report.json").write_text(json.dumps(rep, indent=1))
    gifs_and_board(new, old)
    print("installed", sum(len(f) for f in new.values()), "frames; backup in", bak)


def gifs_and_board(new, old):
    grey = (0x5A, 0x60, 0x58, 255)
    k = 3
    rows = []
    for v in VIEWS:
        al = np.zeros((192, 192), bool)
        for a in new[v] + old[v]:
            al |= a[..., 3] > 0
        ys, xs = np.nonzero(al)
        box = (int(xs.min()) - 3, int(ys.min()) - 3, int(xs.max()) + 4, int(ys.max()) + 4)
        bw, bh = (box[2] - box[0]) * k, (box[3] - box[1]) * k
        gif = []
        for a in new[v]:
            G = Image.new("RGBA", (bw + 10, bh + 10), grey)
            G.alpha_composite(Image.fromarray(selout(a)[0]).crop(box).resize((bw, bh), Image.NEAREST), (5, 5))
            gif.append(G.convert("RGB"))
        gif[0].save(DST / f"fennec_trot_{v}.gif", save_all=True, append_images=gif[1:], duration=100, loop=0)
        rows.append((v, box))
    W = max(b[2] - b[0] for _, b in rows) * k
    H = max(b[3] - b[1] for _, b in rows) * k
    B = Image.new("RGBA", (60 + 8 * (W + 6), len(rows) * (H + 10) + 10), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 8
    for v, box in rows:
        d.text((8, y + 6), v, fill=(235, 235, 230, 255))
        for i, a in enumerate(new[v]):
            x = 60 + i * (W + 6)
            d.rectangle([x, y, x + W, y + H], fill=grey)
            img = Image.fromarray(selout(a)[0]).crop(box)
            B.alpha_composite(img.resize((img.width * k, img.height * k), Image.NEAREST), (x, y))
        y += H + 10
    B.save(DST / "board_sway_all.png")


if __name__ == "__main__":
    main()
