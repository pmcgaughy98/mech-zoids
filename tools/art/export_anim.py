"""Pack rendered, pixelized clip frames into the game's animation folder (Claude, 2026-10-12, animation pass 3).

    python tools/art/export_anim.py <machine_id> <frames_dir> <plan.json>

frames_dir holds <clip>/<k>/e_px.png, one pixelized side-view frame per entry of plan.json (the frame picks and
Godot durations from reports/Gorilla mech animation foundation.md). Every frame comes from the same fixed camera,
so one crop box (the union of all frames plus a margin) keeps the ground line and the body in place across clips.
Writes art/machines/<id>/anim/<clip>/<k>.png and anim.json: canvas size, the feet row (ground line) inside the
canvas, and per clip its frames, durations in ms, loop mode and strike frame index.
"""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_guard   # backs up hand-finished live frames before they are replaced (2026-10-15)


def main(mid, frames_dir, plan_path):
    plan = json.load(open(plan_path))
    imgs = {}
    for clip, d in plan.items():
        for k in range(len(d["frames"])):
            p = os.path.join(frames_dir, clip, str(k), "e_px.png")
            imgs[(clip, k)] = Image.open(p).convert("RGBA")
    first = next(iter(imgs.values()))
    assert all(im.size == first.size for im in imgs.values()), "frames must share one canvas"
    union = np.zeros((first.height, first.width), bool)
    for im in imgs.values():
        union |= np.array(im)[..., 3] > 0
    ys, xs = union.nonzero()
    x0, y0, x1, y1 = max(0, xs.min() - 2), max(0, ys.min() - 2), min(first.width, xs.max() + 3), min(first.height, ys.max() + 3)
    # the ground line: the lowest opaque row of the idle's first frame (the grounded clip puts the feet on the floor)
    idle = np.array(imgs[("idle", 0)])[..., 3] > 0
    feet_y = int(int(idle.nonzero()[0].max()) - int(y0))
    out = os.path.join("art", "machines", mid, "anim")
    live_guard.guard(out, mid, "anim")
    written = []
    meta = {"size": [int(x1) - int(x0), int(y1) - int(y0)], "feet_y": feet_y, "clips": {}}
    for clip, d in plan.items():
        os.makedirs(os.path.join(out, clip), exist_ok=True)
        files = []
        for k in range(len(d["frames"])):
            fn = "%s/%d.png" % (clip, k)
            imgs[(clip, k)].crop((x0, y0, x1, y1)).save(os.path.join(out, fn))
            files.append(fn)
            written.append(fn)
        meta["clips"][clip] = {"frames": files, "ms": d["ms"], "loop": d.get("loop", "once"), "strike": d.get("strike", -1)}
    json.dump(meta, open(os.path.join(out, "anim.json"), "w"), indent=1)
    live_guard.record(out, written)
    print("%s: %d clips, %d frames, canvas %dx%d, feet row %d -> %s" % (
        mid, len(plan), len(imgs), meta["size"][0], meta["size"][1], feet_y, out))


if __name__ == "__main__":
    main(*sys.argv[1:4])
