"""Measure a creature's eight views for consistency (Claude, 2026-10-12, the sprites-in-3D workshop).

The question the workshop asks is whether a 3D model rendered to pixels gives more consistent eight directions
than the Retro Diffusion rotations we have. So first the baseline: for one set of views, per facing, the
sprite's height and width in pixels, where its feet sit, how many colours it uses, and how well the east and
west (and ne/nw, se/sw) pairs mirror each other (intersection over union of the silhouettes after a flip).
Prints a table and writes a JSON beside the views.

    python tools/art/measure_views.py assets/sprites/arena/kithflare            (the 128 px set, files e.png ...)
    python tools/art/measure_views.py assets/sprites/arena/kithflare/dungeon    (the dungeon set)
    python tools/art/measure_views.py <folder> --out docs/design/sprite3d-workshop-2026-10-12/measure_rd.json
"""
import json, os, sys
import numpy as np
from PIL import Image

DIRS = ["e", "ne", "n", "nw", "w", "sw", "s", "se"]
MIRROR = {"e": "w", "ne": "nw", "se": "sw"}


def load(folder, d):
    p = os.path.join(folder, d + ".png")
    if not os.path.exists(p):
        return None
    return np.asarray(Image.open(p).convert("RGBA"))


def box(mask):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def iou(a, b):
    return float((a & b).sum()) / max(1, float((a | b).sum()))


def measure(folder):
    out = {"folder": folder, "views": {}}
    masks = {}
    for d in DIRS:
        im = load(folder, d)
        if im is None:
            continue
        mask = im[:, :, 3] > 64
        masks[d] = mask
        b = box(mask)
        colours = len({tuple(c) for c in im[mask][:, :3].tolist()})
        feet = int(np.where(mask.any(1))[0].max()) + 1
        ground = mask[feet - 1]
        foot_x = int(np.where(ground)[0].mean()) if ground.any() else -1
        out["views"][d] = {"h": int(b[3] - b[1]), "w": int(b[2] - b[0]), "feet_row": feet, "foot_x": foot_x,
                           "area": int(mask.sum()), "colours": colours, "canvas": [int(im.shape[1]), int(im.shape[0])]}
    hs = [v["h"] for v in out["views"].values()]
    out["height_spread"] = int(max(hs) - min(hs)) if hs else 0
    out["mirror_iou"] = {}
    for a, b in MIRROR.items():
        if a in masks and b in masks:
            out["mirror_iou"]["%s/%s" % (a, b)] = round(iou(masks[a], np.fliplr(masks[b])), 3)
    return out


def main():
    folder = sys.argv[1]
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    m = measure(folder)
    print("views in %s" % folder)
    print("  dir   h    w   feet  foot_x  area  colours")
    for d in DIRS:
        v = m["views"].get(d)
        if v:
            print("  %-3s %4d %4d  %4d  %5d  %5d  %5d" % (d, v["h"], v["w"], v["feet_row"], v["foot_x"], v["area"], v["colours"]))
    print("  height spread across views: %d px" % m["height_spread"])
    for k, v in m["mirror_iou"].items():
        print("  mirror IoU %s: %.3f" % (k, v))
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(m, f, indent=1)
        print("  wrote %s" % out_path)


if __name__ == "__main__":
    main()
