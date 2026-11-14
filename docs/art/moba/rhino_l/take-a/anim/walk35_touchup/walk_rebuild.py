"""Rhino cam35 walk touch-up: legs rebuilt from the still's own whole parts (sprite touch-up lane, Claude, 2026-11-04).

Preston: "Touch up rhino walk, lots of missing art because of movement and cutoffs."

Read only:  ../views_cam35/<v>.png (approved stills), walk35/walk/frames/<v>_f*.png (run 1, cleaned),
            walk35/rig.json (foot targets per leg per frame), walk35/walk/layers/<v>_pinned_mask.png
Write:      walk35_touchup/frames/<v>_f*.png, board.png, metrics.json

Why the run 1 frames break: the thigh plates belong to the pinned body while the knee, cuff and foot move, and the
composite cut each plate where the moved parts overlapped it (socket bars, half discs, torn plate bottoms, shards).
The rebuild, per frame:
  1. body = the still's pinned pixels (Codex's own mask), dipped 1 px on the frames run 1 dipped. Drawn LAST, on
     top, so no leg can ever cut a plate.
  2. each visible leg = the still's own leg pixels (still minus pinned mask), in three parts found by rows:
     disc (top, mostly steel), cuff (yellow), foot (sole block). The foot goes exactly on run 1's foot target
     (rig.json), so the foot lock and gait are unchanged. The disc moves half as far (the hip pivot). The cuff
     leans between them one row at a time (rows shifted whole, never rotated or resampled).
  3. hidden far legs = the paired near leg's parts at the far foot's target, drawn first (behind everything).
  4. sockets: a transparent pixel the moving disc left behind, closed in by opaque pixels left, right and above
     within 3 px, becomes charcoal shadow (the hollow behind the joint), so no notch or hole is left in a plate.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

T = Path(r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a")
W35 = T / "anim" / "walk35"
OUT = T / "anim" / "walk35_touchup"
sys.path.insert(0, str(T / "anim"))
from selout_rhino import selout  # noqa: E402

VIEWS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["e", "se", "ne"]
YR = {(0xff, 0xf4, 0xa8), (0xff, 0xcf, 0x1f), (0xd1, 0x8a, 0x0a), (0x7a, 0x4a, 0x06)}
STEEL = {(0xd6, 0xd6, 0xdc), (0x9d, 0x9b, 0xa2), (0x58, 0x55, 0x5e)}
SOCKET = (0x21, 0x1e, 0x27)
PAIR = {"LF": "RF", "LH": "RH"}
# the game's idle is now the touched-up still (the walk frames in walk35/walk/frames were recoloured to it on
# 2026-11-04 22:18), so the walk is built from it too, or idle to walk would pop. Same alpha as views_cam35.
STILL_DIR = "views_cam35_touchup"


# Hand-drawn legs (Preston: "Hand-draw it, free", 2026-11-05). In se the near front leg is hidden by the jaw except
# its foot and a dark ankle stem at the jaw's left, so the still-parts method cannot rebuild it. Pixel decisions:
#   foot = the still's own sole block (rows 148-157, x 104-141), including 4 toe pixels the pinned mask gave the jaw;
#   stem = the still's dark ankle (rows 145-147, x 108-115), extended up to row 134 as one 3d3a44 column on the lit
#          left and 141218 behind it, so the leg always reaches the body when the foot moves; the jaw covers it;
#   both move to the rig's foot target; the 1-3 px gap that opens under the jaw is 211e27 shadow.
HAND = {"se": {"leg": "RF", "foot_rows": (148, 157), "foot_x": (104, 141), "stem_rows": (145, 147),
               "stem_x": (108, 115), "ext_top": 134}}
DARKSET = {(0x14, 0x12, 0x18), (0x21, 0x1e, 0x27), (0x3d, 0x3a, 0x44)}


def hand_draw(img, still, hd, o_f, src):
    H, W = src.shape
    dx, dy = int(o_f[0]), int(o_f[1])
    x0, x1 = hd["stem_x"]
    for r in range(hd["ext_top"], hd["stem_rows"][0]):
        for x in range(x0, x1 + 1):
            ny, nx = r + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W:
                img[ny, nx, :3] = (0x3d, 0x3a, 0x44) if x == x0 else (0x14, 0x12, 0x18)
                img[ny, nx, 3] = 255
                src[ny, nx] = 5
    for m in (hd["stem"], hd["foot"]):
        for y, x in zip(*np.nonzero(m)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W:
                img[ny, nx] = still[y, x]
                src[ny, nx] = 5


def gap_fill(img, src, maxgap=3):
    H, W = src.shape
    n = 0
    for x in range(W):
        ys = np.nonzero(src[:, x] == 5)[0]
        if not len(ys):
            continue
        top = int(ys.min())
        for k in range(1, maxgap + 2):
            y = top - k
            if y < 0:
                break
            if img[y, x, 3] > 0:
                for yy in range(y + 1, top):
                    img[yy, x, :3] = SOCKET
                    img[yy, x, 3] = 255
                    src[yy, x] = 4
                    n += 1
                break
    return n


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def comps(mask):
    lab = np.zeros(mask.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        n += 1
        st = [(y, x)]
        lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        st.append((ny, nx))
    return lab, n


def cls(px):
    t = tuple(int(v) for v in px[:3])
    return "y" if t in YR else "s" if t in STEEL else "d"


def split_rows(still, region):
    """disc rows end where steel stops dominating; foot rows start below the last mostly-yellow row."""
    ys = np.nonzero(region.any(1))[0]
    y_t, y_b = int(ys.min()), int(ys.max())
    frac = {}
    for r in range(y_t, y_b + 1):
        xs = np.nonzero(region[r])[0]
        c = [cls(still[r, x]) for x in xs]
        frac[r] = (c.count("y") / max(1, len(c)), c.count("s") / max(1, len(c)))
    y_c = next((r for r in range(y_t + 3, y_b + 1) if frac[r][1] < 0.20 and frac[r][0] >= 0.30), y_t + 6)
    y_f = next((r + 1 for r in range(y_b, y_c, -1) if frac[r][0] > 0.30), y_b - 7)
    return y_t, y_c, y_f, y_b


def place(canvas, still, region, rows, o_d, o_f, src=None, tag=0):
    """Draw one leg: cuff (leaning), then foot, then disc on top."""
    y_t, y_c, y_f, y_b = rows
    H, W = region.shape

    def put(src_r, dst_r, dx):
        if not (0 <= dst_r < H):
            return
        for x in np.nonzero(region[src_r])[0]:
            nx = x + dx
            if 0 <= nx < W:
                canvas[dst_r, nx] = still[src_r, x]
                if src is not None:
                    src[dst_r, nx] = tag
    d0, d1 = y_c + o_d[1], y_f - 1 + o_f[1]
    if d1 >= d0 and y_f - 1 >= y_c:
        for d in range(d0, d1 + 1):
            u = 0.0 if d1 == d0 else (d - d0) / (d1 - d0)
            s = int(round(y_c + u * (y_f - 1 - y_c)))
            put(s, d, int(round(o_d[0] + u * (o_f[0] - o_d[0]))))
    for r in range(y_f, y_b + 1):
        put(r, r + o_f[1], o_f[0])
    for r in range(y_t, y_c):
        put(r, r + o_d[1], o_d[0])


DARKER = {"fff4a8": "ffcf1f", "ffcf1f": "d18a0a", "d18a0a": "7a4a06", "7a4a06": "7a4a06",
          "d6d6dc": "9d9ba2", "9d9ba2": "58555e", "58555e": "3d3a44", "3d3a44": "211e27", "211e27": "211e27"}


def shade_far(img, src):
    """Far legs sit behind the body: one step darker on their own ramp (the classic back-limb read)."""
    for y, x in zip(*np.nonzero(src == 3)):
        h = "%02x%02x%02x" % tuple(int(c) for c in img[y, x, :3])
        if h in DARKER:
            img[y, x, :3] = [int(DARKER[h][i:i + 2], 16) for i in (0, 2, 4)]


def erode(m, r):
    H, W = m.shape
    p = np.pad(m, r, constant_values=False)
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out &= p[r + dy:r + dy + H, r + dx:r + dx + W]
    return out


def dilate(m, r):
    H, W = m.shape
    p = np.pad(m, r, constant_values=False)
    out = np.zeros_like(m)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= p[r + dy:r + dy + H, r + dx:r + dx + W]
    return out


def opening(m, r):
    """Keep only pixels covered by a (2r+1) square that fits inside the mask: drops parts thinner than 2r+1."""
    return dilate(erode(m, r), r) & m


def drop_far_slivers(img, src):
    """A far-leg piece that is only a strip or a sliver reads as a fleck or tab, not a leg. Keep a far piece only if
    a 5x5 block of it shows, and trim its 1-2 px thin bits."""
    far = src == 3
    keep = opening(far, 1)
    solid = erode(far, 2)
    lab, n = comps(keep)
    for i in range(1, n + 1):
        m = lab == i
        if not (m & solid).any():
            keep[m] = False
    drop = far & ~keep
    img[drop] = 0
    src[drop] = 0
    return int(drop.sum())


def sockets(img, src):
    """Close pinholes (2 px wide or less) left right under the body's bottom edge with charcoal shadow."""
    op = img[..., 3] > 0
    H, W = op.shape
    n = 0
    for y, x in zip(*np.nonzero(~op)):
        if y == 0 or src[y - 1, x] != 1:
            continue
        left = any(op[y, x - k] for k in range(1, 3) if x - k >= 0)
        right = any(op[y, x + k] for k in range(1, 3) if x + k < W)
        if left and right:
            img[y, x, :3] = SOCKET
            img[y, x, 3] = 255
            n += 1
    return n


def slot_fill(img, src, maxrun=3):
    """A 1-3 px slot that opens between a moved leg and the body (a hip or knee pulling away from the plate edge)
    is the shadowed hollow behind the joint: 211e27, so the frame stays one piece."""
    H, W = src.shape
    op = img[..., 3] > 0
    n = 0
    for y in range(H):
        x = 0
        while x < W:
            if op[y, x]:
                x += 1
                continue
            x2 = x
            while x2 < W and not op[y, x2]:
                x2 += 1
            if 0 < x and x2 < W and x2 - x <= maxrun:
                a, b = src[y, x - 1], src[y, x2]
                if (a == 1) != (b == 1) and {a, b} <= {1, 2, 3, 5}:
                    img[y, x:x2, :3] = SOCKET
                    img[y, x:x2, 3] = 255
                    src[y, x:x2] = 4
                    n += x2 - x
            x = x2
    return n


def holes(img):
    """Fill fully enclosed transparent pixels (not reachable from the canvas edge) with charcoal shadow."""
    tr = img[..., 3] == 0
    H, W = tr.shape
    seen = np.zeros_like(tr)
    st = [(y, x) for y in range(H) for x in (0, W - 1) if tr[y, x]] + [(y, x) for x in range(W) for y in (0, H - 1)
                                                                         if tr[y, x]]
    for y, x in st:
        seen[y, x] = True
    while st:
        y, x = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and tr[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                st.append((ny, nx))
    hole = tr & ~seen
    img[hole, :3] = SOCKET
    img[hole, 3] = 255
    return int(hole.sum())


def build(v):
    still = load(T / STILL_DIR / f"{v}.png")
    pm = load(W35 / "walk" / "layers" / f"{v}_pinned_mask.png")
    pinned = (pm[..., :3].max(-1) > 127) & (pm[..., 3] > 0) & (still[..., 3] > 0)
    legpx = (still[..., 3] > 0) & ~pinned
    rig = json.load(open(W35 / "rig.json"))[v]
    legs = sorted(set(e["name"] for e in rig))
    visible = [g for g in legs if not next(e for e in rig if e["name"] == g)["hidden_in_still"]]
    sole = {g: np.array(next(e for e in rig if e["name"] == g)["sole_source"]) for g in legs}
    # assign leg pixels to the nearest visible leg's sole (by component)
    lab, n = comps(legpx)
    region = {g: np.zeros(legpx.shape, bool) for g in visible}
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        low = np.array([xs[ys.argmax()], ys.max()])
        g = min(visible, key=lambda k: np.hypot(*(sole[k] - low)))
        region[g] |= lab == i
    # rows from the rig's own joints at the still pose: disc to knee+4, cuff to ankle+3, foot below
    pose = {g: min((e for e in rig if e["name"] == g),
                   key=lambda e: np.hypot(*(np.array(e["target"]) - np.array(e["sole_source"])))) for g in legs}
    rows = {}
    for g in visible:
        ys = np.nonzero(region[g].any(1))[0]
        y_t, y_b = int(ys.min()), int(ys.max())
        y_c = int(min(max(round(pose[g]["knee"][1]) + 4, y_t), y_b + 1))
        y_f = int(min(max(round(pose[g]["ankle"][1]) + 3, y_c), y_b + 1))
        rows[g] = (y_t, y_c, y_f, y_b)
    # hip pendulum: the knee moves (knee - hip) / (sole - hip) of the foot's move
    frac = {g: (pose[g]["knee"][1] - pose[g]["root"][1]) / max(1.0, pose[g]["sole_source"][1] - pose[g]["root"][1])
            for g in legs}
    # the pinned mask kept some of each disc's steel rim with the body; those flecks float beside the moved disc.
    # Give pinned steel pixels touching a disc (its rows, up to 4 above) back to that leg.
    stl = np.array([[tuple(int(c) for c in still[y, x, :3]) in STEEL for x in range(still.shape[1])]
                    for y in range(still.shape[0])])
    # Also: pinned pixels in pieces 1-2 px thin (gone after a 3x3 opening) at leg height are leg parts the mask kept
    # (the dark shank side, rim slivers); they spike or float once the leg moves, so they go back to the leg too.
    thin = pinned & ~opening(pinned, 1)
    thin[:max(0, min(r[0] for r in rows.values()) - 4)] = False
    grabbed_total = 0
    for g in visible:
        y_t, y_c, y_f, y_b = rows[g]
        band = np.zeros_like(pinned)
        band[max(0, y_t - 4):y_c] = True
        cand = (pinned & stl & band) | thin
        seed = region[g]
        grab = np.zeros_like(pinned)
        st = list(zip(*np.nonzero(seed)))
        while st:
            y, x = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < cand.shape[0] and 0 <= nx < cand.shape[1] and cand[ny, nx] and not grab[ny, nx]:
                        grab[ny, nx] = True
                        st.append((ny, nx))
        if grab.any():
            region[g] |= grab
            pinned &= ~grab
            legpx |= grab
            grabbed_total += int(grab.sum())
            rows[g] = (min(y_t, int(np.nonzero(grab.any(1))[0].min())), y_c, y_f, y_b)
    # dip per frame from run 1: does the pinned body sit 0 or 1 px lower?
    hd = HAND.get(v)
    if hd:
        yy, xx = np.mgrid[0:still.shape[0], 0:still.shape[1]]
        op = still[..., 3] > 0
        dark = np.array([[tuple(int(c) for c in still[y, x, :3]) in DARKSET for x in range(still.shape[1])]
                         for y in range(still.shape[0])])
        win = lambda r, c: (yy >= r[0]) & (yy <= r[1]) & (xx >= c[0]) & (xx <= c[1])
        hd = dict(hd, foot=op & win(hd["foot_rows"], hd["foot_x"]),
                  stem=op & dark & win(hd["stem_rows"], hd["stem_x"]))
        part = hd["foot"] | hd["stem"]
        for k in region:
            region[k] &= ~part
        region[hd["leg"]] = part
        pinned &= ~part
        legpx |= part
    out, info = [], {"rows": {g: list(map(int, rows[g])) for g in visible}, "grabbed_steel_px": grabbed_total, "still": STILL_DIR,
                     "frames": []}
    srcs = []
    for f in range(8):
        run1 = load(W35 / "walk" / "frames" / f"{v}_f{f}.png")
        score = {}
        for dip in (0, 1):
            sh = np.roll(still, dip, 0)
            pm2 = np.roll(pinned, dip, 0)
            score[dip] = float(np.all(run1[pm2] == sh[pm2], -1).mean())
        dip = max(score, key=score.get)
        img = np.zeros_like(still)
        src = np.zeros(still.shape[:2], int)
        ent = {e["name"]: e for e in rig if e["frame"] == f}
        order = sorted(legs, key=lambda g: (not ent[g]["hidden_in_still"], ent[g]["target"][1]))
        for g in order:
            e = ent[g]
            if e["hidden_in_still"]:
                near = PAIR.get(g)
                if near not in visible or (hd and near == hd["leg"]):
                    continue
                lane = np.array(e["sole_source"]) - sole[near]
                rel = np.array(e["target"]) - np.array(e["sole_source"])
                o_f = np.rint(lane + rel).astype(int)
                o_d = np.rint(lane + rel * frac[near]).astype(int)
                place(img, still, region[near], rows[near], o_d, o_f, src, 3)
            elif hd and g == hd["leg"]:
                hand_draw(img, still, hd, np.rint(np.array(e["target"]) - sole[g]).astype(int), src)
            else:
                rel = np.array(e["target"]) - sole[g]
                o_f = np.rint(rel).astype(int)
                o_d = np.rint(rel * frac[g]).astype(int)
                place(img, still, region[g], rows[g], o_d, o_f, src, 2)
        body = np.roll(still, dip, 0)
        bm = np.roll(pinned, dip, 0)
        img[bm] = body[bm]
        src[bm] = 1
        n_gap = gap_fill(img, src) if hd else 0
        shade_far(img, src)
        n_sliver = drop_far_slivers(img, src)
        before = img[..., 3] > 0
        n_slot = slot_fill(img, src)
        n_sock = sockets(img, src)
        n_hole = holes(img)
        src[(img[..., 3] > 0) & ~before] = 4
        out.append(img)
        srcs.append(src)
        diff_run1 = int(np.any(img != run1, -1).sum())
        info["frames"].append({"f": f, "dip": dip, "dip_match": round(score[dip], 3), "socket_px": n_sock,
                               "far_sliver_px_dropped": n_sliver, "jaw_gap_px": n_gap, "slot_px": n_slot,
                               "hole_px": n_hole, "px_vs_run1": diff_run1,
                               "lowest_row": int(np.nonzero(img[..., 3] > 0)[0].max())})
    info["_srcs"] = srcs
    return still, out, info


def main():
    (OUT / "frames").mkdir(parents=True, exist_ok=True)
    allinfo = {}
    for v in VIEWS:
        still, frames, info = build(v)
        for f, img in enumerate(frames):
            Image.fromarray(img).save(OUT / "frames" / f"{v}_f{f}.png")
        np.save(Path(__file__).parent / f"src_{v}.npy", np.stack(info.pop("_srcs")))
        allinfo[v] = info
        print(v, "rows", info["rows"])
        print("  ", [(d["f"], d["dip"], d["socket_px"], d["hole_px"], d["px_vs_run1"], d["lowest_row"])
                     for d in info["frames"]])
    (OUT / "metrics.json").write_text(json.dumps(allinfo, indent=1))


if __name__ == "__main__":
    main()
