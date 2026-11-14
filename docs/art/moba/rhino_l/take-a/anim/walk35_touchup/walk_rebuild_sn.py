"""Rhino cam35 walk, front (s) and back (n): legs rebuilt from the still's own whole parts (touch-up lane, 2026-11-05).

Preston, via the Rhino session: asked "Have the touch-up lane rebuild the s and n legs?", he answered "Yes, rebuild them".
Defect: the s/n legs (walk35/build_run2.py) move as rigid blocks under a body drawn on top, so whenever a foot rises the
round grey knee disc slides under the body and is cut to a flat bar or vanishes (s f0 f1 f2 f4 f5 f6, n f0 f3 f4 f5 f6).

Same method as walk_rebuild.py (se/e/ne), adapted to the two views that have no rig.json joints:
  - leg masks = run 2's own hand-traced leg borders (build_run2.traces); body = the still minus them
  - each leg splits by rows into disc (steel ball), cuff (yellow), foot (sole block):
      s: disc 137-145, cuff 146-152, foot 153-160;  n: disc 134-144, cuff 145-153, foot 154-160
  - the foot goes exactly where the live frame (walk35/walk/frames) has it, measured per frame, so the foot path and
    footlock against walk35/targets.json are unchanged; the body dip (0 or 1 px) is measured the same way
  - the disc moves half the foot's move (the hip pivot, truncated toward zero); the cuff leans between disc and foot one
    whole row at a time (rows dropped or repeated, never resampled)
  - draw order: cuffs and feet, then the body, then the discs, so a disc is never cut; a rising knee sits in front of
    the body's lower edge (the knee comes toward the viewer when the foot lifts)
  - a disc that moved down leaves a 1-2 px slot under the body: 211e27 shadow (the joint hollow), as on se/e/ne
Reads views_cam35_touchup/<s|n>.png and walk35/walk/frames/<s|n>_f*.png. Writes walk35_touchup/frames/<s|n>_f0-7.png
and walk35_touchup/metrics_sn.json. Never touches se/e/ne or art/machines.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
T = HERE.parents[1]
W35 = T / "anim" / "walk35"
sys.path.insert(0, str(HERE))
from walk_rebuild import holes, place, slot_fill, sockets, SOCKET  # noqa: E402

Y, X = np.indices((192, 192))
ROWS = {"s": (137, 146, 153, 160), "n": (134, 145, 154, 160)}   # disc top, cuff top, foot top, sole row


def traces(view):
    """build_run2.py's own leg borders, copied so this script never runs that one (it rewrites the live frames)."""
    if view == "s":
        lo = [66, 65, 65, 65, 65, 65, 66, 66, 65, 65, 65, 64, 63, 63, 63, 63, 63] + [63] * 7
        hi = [77, 78, 79, 79, 79, 79, 79, 80, 81, 82, 83, 84, 85, 86, 87, 87, 88] + [91] * 7
        left = np.zeros((192, 192), bool)
        for j, y in enumerate(range(137, 161)):
            left[y, lo[j]:hi[j] + 1] = True
        right = np.zeros_like(left)
        bounds = [(115, 125), (114, 126), (113, 126), (112, 127), (112, 127), (112, 127), (112, 126), (111, 126),
                  (110, 127), (109, 127), (108, 128), (107, 129), (106, 130), (105, 130), (104, 130), (103, 130),
                  (102, 131)] + [(100, 132)] * 7
        for y, (a, b) in zip(range(137, 161), bounds):
            right[y, a:b + 1] = True
        return {"RF": left, "LF": right}
    left = (Y >= 134) & (Y <= 160) & (X >= 61) & (X <= 88)
    right = (Y >= 134) & (Y <= 160) & (X >= 103) & (X <= 132)
    return {"LH": left, "RH": right}


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def shift_mask(m, dx, dy):
    out = np.zeros_like(m)
    ys, xs = np.nonzero(m)
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < 192) & (nx >= 0) & (nx < 192)
    out[ny[ok], nx[ok]] = True
    return out


def shift_img(a, m, dx, dy):
    """The still's pixels under mask m, moved by (dx, dy), on an empty canvas."""
    out = np.zeros_like(a)
    ys, xs = np.nonzero(m)
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < 192) & (nx >= 0) & (nx < 192)
    out[ny[ok], nx[ok]] = a[ys[ok], xs[ok]]
    return out


def match(live, still, mask, dx, dy):
    ys, xs = np.nonzero(mask)
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < 192) & (nx >= 0) & (nx < 192)
    return float(np.all(live[ny[ok], nx[ok]] == still[ys[ok], xs[ok]], -1).mean())


def disc_gap(img, src, disc_top, maxgap=3):
    """Transparent pixels between anything opaque above and a lowered disc's top: the joint hollow, 211e27."""
    n = 0
    for y, x in zip(*np.nonzero(disc_top)):
        for k in range(1, maxgap + 2):
            yy = y - k
            if yy < 0:
                break
            if img[yy, x, 3] > 0:
                for z in range(yy + 1, y):
                    img[z, x, :3] = SOCKET
                    img[z, x, 3] = 255
                    src[z, x] = 4
                    n += 1
                break
    return n


def build(v):
    still = load(T / "views_cam35_touchup" / f"{v}.png")
    legs = traces(v)
    y_t, y_c, y_f, y_b = ROWS[v]
    op = still[..., 3] > 0
    region = {g: m & op for g, m in legs.items()}
    body = op & ~np.logical_or.reduce(list(region.values()))
    disc_m = {g: region[g] & (Y < y_c) for g in region}
    foot_m = {g: region[g] & (Y >= y_f) for g in region}
    out, info = [], {"rows": {"disc": [y_t, y_c - 1], "cuff": [y_c, y_f - 1], "foot": [y_f, y_b]}, "frames": []}
    for f in range(8):
        live = load(W35 / "walk" / "frames" / f"{v}_f{f}.png")
        dips = {d: match(live, still, body & (Y < y_t - 2), 0, d) for d in (0, 1)}
        dip = max(dips, key=dips.get)
        img = np.zeros_like(still)
        src = np.zeros((192, 192), int)
        fi = {"f": f, "dip": dip, "dip_match": round(dips[dip], 3), "legs": {}}
        offs = {}
        for g in region:
            best = max(((dx, dy) for dx in range(-3, 4) for dy in range(-7, 8)),
                       key=lambda o: match(live, still, foot_m[g], *o))
            o_f = np.array(best)
            # x: run 2 set each leg 1 px outward in every frame (a fixed lane, not a step), so the disc keeps it too
            o_d = np.array([int(o_f[0]), int(o_f[1] / 2)])
            offs[g] = (o_d, o_f)
            fi["legs"][g] = {"foot": [int(o_f[0]), int(o_f[1])],
                             "foot_match": round(match(live, still, foot_m[g], *best), 3),
                             "disc": [int(o_d[0]), int(o_d[1])]}
            place(img, still, region[g] & (Y >= y_c), (y_c, y_c, y_f, y_b), o_d, o_f, src, 2)
        bm = shift_mask(body, 0, dip)
        img[bm] = np.roll(still, dip, 0)[bm]
        src[bm] = 1
        n_gap = 0
        whole = {}
        for g, (o_d, o_f) in offs.items():
            dx, dy = int(o_d[0]), int(o_d[1])
            dm = shift_mask(disc_m[g], dx, dy)
            di = shift_img(still, disc_m[g], dx, dy)
            img[dm] = di[dm]
            src[dm] = 2
            if dy > dip:
                n_gap += disc_gap(img, src, dm & ~np.roll(dm, 1, 0))
            whole[g] = (dm, di)
        before = img[..., 3] > 0
        fi["joint_gap_px"] = n_gap
        fi["slot_px"] = slot_fill(img, src)
        fi["socket_px"] = sockets(img, src)
        fi["hole_px"] = holes(img)
        src[(img[..., 3] > 0) & ~before] = 4
        fi["disc_whole"] = {g: bool(np.array_equal(img[dm], di[dm])) for g, (dm, di) in whole.items()}
        fi["px_vs_live"] = int(np.any(img != live, -1).sum())
        fi["lowest_row"] = int(np.nonzero(img[..., 3] > 0)[0].max())
        info["frames"].append(fi)
        out.append(img)
    return out, info


def main():
    (HERE / "frames").mkdir(exist_ok=True)
    allinfo = {}
    for v in ("s", "n"):
        frames, info = build(v)
        for f, img in enumerate(frames):
            Image.fromarray(img).save(HERE / "frames" / f"{v}_f{f}.png")
        allinfo[v] = info
        for d in info["frames"]:
            print(v, d["f"], "dip", d["dip"], d["dip_match"],
                  {g: (lg["foot"], lg["foot_match"], lg["disc"]) for g, lg in d["legs"].items()},
                  "gap", d["joint_gap_px"], "slot", d["slot_px"], "sock", d["socket_px"], "hole", d["hole_px"],
                  "discs whole", all(d["disc_whole"].values()), "px vs live", d["px_vs_live"], "low", d["lowest_row"])
    (HERE / "metrics_sn.json").write_text(json.dumps(allinfo, indent=1))


if __name__ == "__main__":
    main()
