"""Install only the battle frames a rebuild actually changed, keeping every other live frame (Claude, 2026-10-16).

    python tools/art/patch_frames.py <machine_id> <old_frames_dir> <new_frames_dir> [--write]

After Codex has hand-finished a machine's battle frames, a rebuild that fixes something small (a part bound to the
wrong bone: tools/blender/bind_audit.py) would replace all of them with raw renders through export_anim.py. Instead:
both folders hold the raw pixelized renders (<clip>/<k>/e_px.png on the full render canvas, as tools/art/anim_round.sh
leaves them in docs/art/2d/<id>/anim_frames): the old ones the live frames were exported from, the new ones from the
rebuild. Frames whose raw render is pixel-identical keep their live (finished) file. Changed frames are cropped with
the same box export_anim.py used for the old set (the union of the old frames plus its margin), so they land on the
live canvas exactly where the old ones did. Prints each changed frame with its count of changed pixels; with --write,
backs up the live folder (tools/art/live_guard.py) and writes the changed frames. Exits 2 without writing if a new
frame reaches outside the old box (the canvas would have to grow: use export_anim.py and a full finish instead).
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_guard   # noqa: E402


def load(d, clip, k):
    p = os.path.join(d, clip, str(k), "e_px.png")
    return np.array(Image.open(p).convert("RGBA")) if os.path.exists(p) else None


def main(mid, old_dir, new_dir, write):
    live = os.path.join("art", "machines", mid, "anim")
    meta = json.load(open(os.path.join(live, "anim.json")))
    olds, news = {}, {}
    for clip, c in meta["clips"].items():
        for k in range(len(c["frames"])):
            olds[(clip, k)] = load(old_dir, clip, k)
            news[(clip, k)] = load(new_dir, clip, k)
    missing = [key for key, im in list(olds.items()) + list(news.items()) if im is None]
    if missing:
        print("PATCH_FRAMES missing raw frames:", sorted(set(missing))[:8])
        return 1
    first = next(iter(olds.values()))
    union = np.zeros(first.shape[:2], bool)
    for im in olds.values():
        union |= im[..., 3] > 0
    ys, xs = union.nonzero()   # the same box export_anim.py cut the old set with
    x0, y0 = max(0, xs.min() - 2), max(0, ys.min() - 2)
    x1, y1 = min(first.shape[1], xs.max() + 3), min(first.shape[0], ys.max() + 3)
    if [int(x1 - x0), int(y1 - y0)] != list(meta["size"]):
        print("PATCH_FRAMES the old frames do not rebuild the live canvas (%s against %s): wrong old folder?" % ([int(x1 - x0), int(y1 - y0)], meta["size"]))
        return 1
    changed, outside = [], []
    for key, new in news.items():
        old = olds[key]
        diff = np.any(new != old, axis=2)
        if not diff.any():
            continue
        n = int(diff.sum())
        alpha = new[..., 3] > 0
        if alpha[:y0].any() or alpha[y1:].any() or alpha[:, :x0].any() or alpha[:, x1:].any():
            outside.append(key)
        changed.append((key, n))
    for (clip, k), n in sorted(changed):
        print("PATCH_FRAMES changed %s/%d: %d pixels%s" % (clip, k, n, "  (OUTSIDE the canvas)" if (clip, k) in outside else ""))
    print("PATCH_FRAMES %d of %d frames changed" % (len(changed), len(news)))
    if outside:
        print("PATCH_FRAMES stop: %d frames reach outside the live canvas; nothing written" % len(outside))
        return 2
    if write and changed:
        live_guard.guard(live, mid, "anim")
        for (clip, k), _n in changed:
            frame = news[(clip, k)][y0:y1, x0:x1]
            name = meta["clips"][clip]["frames"][k]
            Image.fromarray(frame, "RGBA").save(os.path.join(live, name))
        # the install record learns the new raw frames only: the finished frames keep their old raw hashes, so their
        # deliberate mismatch still tells live_guard they hold hand edits
        rec_path = os.path.join(live, live_guard.RECORD)
        rec = json.load(open(rec_path)) if os.path.exists(rec_path) else {}
        for (clip, k), _n in changed:
            name = meta["clips"][clip]["frames"][k]
            rec[name] = live_guard._sha(os.path.join(live, name))
        json.dump(rec, open(rec_path, "w"), indent=1)
        print("PATCH_FRAMES wrote %d frames into %s" % (len(changed), live))
    return 0


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    sys.exit(main(a[0], a[1], a[2], "--write" in sys.argv))
