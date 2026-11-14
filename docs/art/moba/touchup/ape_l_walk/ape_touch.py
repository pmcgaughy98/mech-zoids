"""Gorilla (ape_l) 35-degree walk touch-up (Preston: "the 2 fold fixed a lot of it just needs touched up").

Input (read only): walk/ape_l/final/frames/<view>_f0-7.png (192x192, raw). Output here: frames/, report.json,
board_game.png (game outline, 2x), board_changes.png (4x, changed pixels marked).

Kept exactly (the walk lane's promises):
- body: every opaque pixel that equals the idle still (placed by the measured offset, 1 px dip on f0 and f4)
- feet: the bottom 8 rows of every frame
- the still's 15 colours, binary alpha, one piece per frame
Changed only in the limbs and the joins the walk lane filled:
1. 1 px specks: a pixel whose four side neighbours are all one other colour takes that colour (glow colours kept)
2. 1 px spurs: an opaque pixel with at most one opaque side neighbour is removed
3. 1 px notches: an empty pixel with three or four opaque side neighbours takes their most common colour
Repeated until nothing changes (max 4 passes).
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(r"D:/dev/new-mech-rpg/docs/art/moba")
SRC = ROOT / "walk/ape_l/final/frames"
STILL = ROOT / "ape_l/take-a/views_cam35_touchup"
HERE = Path(__file__).parent
OUT = HERE / "frames"
VIEWS = ["e", "se", "ne", "s", "n"]
N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
FEET_ROWS = 8
pal = {tuple(int(p["hex"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)): p["role"]
       for p in json.load(open(ROOT / "ape_l/take-a/cam35/palette.json"))}
GLOW = {c for c, r in pal.items() if "glow" in r}
sys.path.insert(0, str(ROOT / "rhino_l/take-a/anim"))
from selout_rhino import selout  # noqa: E402


def place(still, dx, dy, shape):
    out = np.zeros(shape, still.dtype)
    h, w = still.shape[:2]
    out[dy:dy + h, dx:dx + w] = still
    return out


def find_offset(still, frame):
    best = (-1, 0, 0)
    sop = still[..., 3] > 0
    for dy in range(0, 33):
        for dx in range(0, 33):
            p = place(still, dx, dy, frame.shape)
            m = (p[..., 3] > 0) & (frame[..., 3] > 0)
            n = int((np.all(p == frame, -1) & m).sum())
            if n > best[0]:
                best = (n, dx, dy)
    return best[1], best[2], best[0] / sop.sum()


def pieces(m):
    lab = np.zeros(m.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1
        st = [(y, x)]
        lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for dy, dx in N4:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    st.append((ny, nx))
    return n


def touch(a, keep):
    b = a.copy()
    H, W = b.shape[:2]
    log = Counter()
    for _ in range(4):
        ch = 0
        m = b[..., 3] > 0
        for y, x in zip(*np.nonzero(m & ~keep)):
            c = tuple(b[y, x, :3])
            if c in GLOW:
                continue
            nb = [(y + dy, x + dx) for dy, dx in N4 if 0 <= y + dy < H and 0 <= x + dx < W]
            on = [p for p in nb if m[p]]
            if len(on) <= 1:
                b[y, x] = 0
                log["spurs"] += 1
                ch += 1
                continue
            cols = {tuple(b[p][:3]) for p in on}
            if len(on) == 4 and len(cols) == 1 and c not in cols:
                b[y, x, :3] = next(iter(cols))
                log["specks"] += 1
                ch += 1
        m = b[..., 3] > 0
        for y, x in zip(*np.nonzero(~m & ~keep)):
            if y in (0, H - 1) or x in (0, W - 1):
                continue
            on = [(y + dy, x + dx) for dy, dx in N4 if m[y + dy, x + dx]]
            if len(on) >= 3:
                b[y, x, :3] = Counter(tuple(b[p][:3]) for p in on).most_common(1)[0][0]
                b[y, x, 3] = 255
                log["notches"] += 1
                ch += 1
        if not ch:
            break
    # see-through pinholes and slits inside the body (enclosed, 4 px or less) take their neighbours' colour;
    # bigger enclosed gaps (ne f3-f4 beside the far forearm) are real gaps and stay open
    from scipy.ndimage import binary_fill_holes, label
    hl, hn = label(binary_fill_holes(b[..., 3] > 0) & (b[..., 3] == 0))
    for k in range(1, hn + 1):
        pts = list(zip(*np.nonzero(hl == k)))
        if len(pts) > 4:
            continue
        for y, x in pts:
            on = [(y + dy, x + dx) for dy, dx in N4 if b[y + dy, x + dx, 3] > 0]
            b[y, x, :3] = Counter(tuple(b[p][:3]) for p in on).most_common(1)[0][0]
            b[y, x, 3] = 255
            log["pinholes"] += 1
    # slivers that touch the body only at a corner: add the one pixel that joins them side-on
    for _ in range(6):
        lab, n = label(b[..., 3] > 0)
        if n <= 1:
            break
        main_id = int(np.argmax(np.bincount(lab.ravel())[1:])) + 1
        joined = False
        for y, x in zip(*np.nonzero(b[..., 3] == 0)):
            if not (0 < y < H - 1 and 0 < x < W - 1):
                continue
            ids = {int(lab[y + dy, x + dx]) for dy, dx in N4}
            small = [i for i in ids if i and i != main_id]
            if main_id in ids and small:
                p = next((y + dy, x + dx) for dy, dx in N4 if lab[y + dy, x + dx] == small[0])
                b[y, x] = b[p]
                log["joins"] += 1
                joined = True
                break
        if not joined:
            break
    return b, log


def main():
    OUT.mkdir(exist_ok=True)
    report, live, new = {}, {}, {}
    for v in VIEWS:
        still = np.asarray(Image.open(STILL / f"{v}.png").convert("RGBA"))
        fr = [np.asarray(Image.open(SRC / f"{v}_f{i}.png").convert("RGBA")) for i in range(8)]
        dx, dy, share = find_offset(still, fr[1])
        live[v], new[v] = fr, []
        report[v] = {"still_offset": [dx, dy], "f1_body_match": round(share, 3), "frames": {}}
        for i, a in enumerate(fr):
            p = place(still, dx, dy + (1 if i in (0, 4) else 0), a.shape)
            body = (a[..., 3] > 0) & np.all(p == a, -1)
            ys = np.nonzero(a[..., 3] > 0)[0]
            keep = body.copy()
            keep[ys.max() - FEET_ROWS + 1:] = True
            b, log = touch(a, keep)
            m = b[..., 3] > 0
            r = {**log, "changed": int(np.any(a != b, -1).sum()), "pieces": pieces(m),
                 "binary_alpha": set(np.unique(b[..., 3])) <= {0, 255},
                 "off_palette": int(sum(1 for c in b[m][:, :3] if tuple(c) not in pal)),
                 "body_kept": bool(np.array_equal(b[body], a[body])),
                 "feet_rows_kept": bool(np.array_equal(b[ys.max() - FEET_ROWS + 1:], a[ys.max() - FEET_ROWS + 1:]))}
            report[v]["frames"][f"f{i}"] = r
            Image.fromarray(b).save(OUT / f"{v}_f{i}.png")
            new[v].append(b)
        print(v, "offset", (dx, dy), "body match", round(share, 3), "|",
              " ".join(f"f{i}:{r['changed']}" for i, r in enumerate(report[v]["frames"].values())),
              "| all rules", all(r["pieces"] == 1 and r["binary_alpha"] and not r["off_palette"] and r["body_kept"]
                                 and r["feet_rows_kept"] for r in report[v]["frames"].values()))
    (HERE / "report.json").write_text(json.dumps(report, indent=1))
    boards(live, new)


def boards(live, new):
    grey = (0x5A, 0x60, 0x58, 255)
    rows = []
    for v in VIEWS:
        al = np.zeros((192, 192), bool)
        for a in live[v]:
            al |= a[..., 3] > 0
        ys, xs = np.nonzero(al)
        box = (int(xs.min()) - 2, int(ys.min()) - 2, int(xs.max()) + 3, int(ys.max()) + 3)
        for lab, fr, k, mark in ((f"{v} live", live[v], 2, False), (f"{v} new", new[v], 2, False),
                                 (f"{v} changed", new[v], 2, True)):
            cells = []
            for i, a in enumerate(fr):
                img = selout(a)[0] if not mark else a.copy()
                if mark:
                    ch = np.any(live[v][i] != a, -1)
                    g = img.copy()
                    l = (img[..., :3].mean(-1) * 0.45 + 30).astype(np.uint8)
                    g[..., 0] = g[..., 1] = g[..., 2] = l
                    g[ch] = (255, 40, 220, 255)
                    img = g
                c = Image.fromarray(img).crop(box)
                cells.append(c.resize((c.width * k, c.height * k), Image.NEAREST))
            cw, chh = cells[0].size
            R = Image.new("RGBA", (100 + 8 * (cw + 6), chh + 8), (34, 37, 41, 255))
            d = ImageDraw.Draw(R)
            d.text((4, 10), lab, fill=(235, 235, 230, 255))
            for i, c in enumerate(cells):
                x = 100 + i * (cw + 6)
                d.rectangle([x, 4, x + cw, 4 + chh], fill=grey)
                R.alpha_composite(c, (x, 4))
            rows.append(R)
    B = Image.new("RGBA", (max(r.width for r in rows), sum(r.height for r in rows)), (34, 37, 41, 255))
    y = 0
    for r in rows:
        B.alpha_composite(r, (0, y))
        y += r.height
    B.save(HERE / "board_game.png")


if __name__ == "__main__":
    main()
