"""Replace one battle clip in a machine's live animation, keeping every other clip's hand finish (Claude, 2026-10-15).

    python tools/art/replace_clip.py <machine_id> <clip> <frames_dir> <plan.json>

export_anim.py rewrites the whole live anim folder, which would throw away Codex's finish on the clips that did not
change. This writes only <clip>: frames_dir holds the clip's new renders, pixelized uncropped
(<frames_dir>/<clip>/<k>/e_px.png), plus idle/0/e_px.png rendered with the same camera, which locates the live canvas
inside the new frames (its silhouette must match the live idle/0.png exactly; a wider SPRITE_ORTHO whose extra margin
is a whole number of sprite pixels per side keeps the pixel grid). If the clip reaches past the live canvas, the canvas
grows right, up or down, every other clip's live frames are padded with transparent pixels (no pixel changes), and
anim.json's size and feet_y follow. Growing left is refused: battle.gd places the player's machine by its left edge,
so it would shift the body. The clip's ms/loop/strike come from plan.json. live_guard backs the live folder up first
and the install record is updated for the replaced clip only, so the other clips' finish still reads as hand edits.
"""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_guard


def alpha(p):
    return np.array(Image.open(p).convert("RGBA"))[..., 3] > 0


def main(mid, clip, frames_dir, plan_path):
    out = os.path.join("art", "machines", mid, "anim")
    meta = json.load(open(os.path.join(out, "anim.json")))
    plan = json.load(open(plan_path))[clip]
    w, h = meta["size"]
    live_idle, wide_idle = alpha(os.path.join(out, "idle", "0.png")), alpha(os.path.join(frames_dir, "idle", "0", "e_px.png"))
    H, W = wide_idle.shape
    hits = [(ox, oy) for oy in range(H - h + 1) for ox in range(W - w + 1) if (wide_idle[oy:oy + h, ox:ox + w] == live_idle).all()
            and wide_idle.sum() == live_idle.sum()]
    if len(hits) != 1:
        raise SystemExit("STOP: the new idle/0 does not line up with the live idle/0 exactly once (%d matches): the model or "
                         "camera changed, or the margin is not a whole number of sprite pixels." % len(hits))
    ox, oy = hits[0]
    frames = [Image.open(os.path.join(frames_dir, clip, str(k), "e_px.png")).convert("RGBA") for k in range(len(plan["frames"]))]
    u = np.zeros((H, W), bool)
    for im in frames:
        u |= np.array(im)[..., 3] > 0
    ys, xs = u.nonzero()
    # the same margin export_anim.py leaves around the union (2 before, 3 after)
    x0, y0 = min(ox, max(0, xs.min() - 2)), min(oy, max(0, ys.min() - 2))
    x1, y1 = max(ox + w, min(W, xs.max() + 3)), max(oy + h, min(H, ys.max() + 3))
    if x0 < ox:
        raise SystemExit("STOP: %s reaches %d px left of the live canvas; growing left would shift the player's machine." % (clip, ox - x0))
    if xs.min() == 0 or ys.min() == 0 or xs.max() == W - 1 or ys.max() == H - 1:
        raise SystemExit("STOP: %s touches the edge of the new renders; widen SPRITE_ORTHO." % clip)
    nw, nh, px, py = x1 - x0, y1 - y0, ox - x0, oy - y0
    live_guard.guard(out, mid, "anim")
    rec_path = os.path.join(out, live_guard.RECORD)
    rec = json.load(open(rec_path)) if os.path.exists(rec_path) else {}
    if (nw, nh) != (w, h):
        for c, d in meta["clips"].items():
            if c == clip:
                continue
            for fn in d["frames"]:
                p = os.path.join(out, fn)
                big = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
                big.paste(Image.open(p).convert("RGBA"), (px, py))
                big.save(p)
    for fn in meta["clips"][clip]["frames"]:
        os.remove(os.path.join(out, fn))
        rec.pop(fn, None)
    files = []
    for k, im in enumerate(frames):
        fn = "%s/%d.png" % (clip, k)
        im.crop((x0, y0, x1, y1)).save(os.path.join(out, fn))
        files.append(fn)
        rec[fn] = live_guard._sha(os.path.join(out, fn))
    meta["size"], meta["feet_y"] = [int(nw), int(nh)], int(meta["feet_y"] + py)
    meta["clips"][clip] = {"frames": files, "ms": plan["ms"], "loop": plan.get("loop", "once"), "strike": plan.get("strike", -1)}
    json.dump(meta, open(os.path.join(out, "anim.json"), "w"), indent=1)
    json.dump(rec, open(rec_path, "w"), indent=1)
    print("%s %s: %d frames; canvas %dx%d -> %dx%d (others padded %d left, %d top), feet row %d" % (
        mid, clip, len(files), w, h, nw, nh, px, py, meta["feet_y"]))


if __name__ == "__main__":
    main(*sys.argv[1:5])
