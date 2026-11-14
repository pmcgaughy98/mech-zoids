"""Fennec (fennec_s) 35-degree trot touch-up, same method as the gorilla walk (ape_touch.py).

Input (read only): walk/fennec_s/final/frames/<view>_f0-7.png (192x192, raw, s view widened per Preston).
Still: walk/fennec_s/final/stills/<view>.png (the 192-canvas standing stills these frames match).
Output here: frames/, report.json, board_game.png (2x, game outline), board_fills.png (6x crops of every pinhole fill).

Kept exactly: every opaque pixel equal to the standing still (1 px dip on f0 and f4), the bottom 8 rows (foot lock),
the still's 15 colours, binary alpha, one piece per frame. Eye colours never change.
Cleanup only on what is left: 1 px specks, spurs, notches; enclosed see-through pinholes of 4 px or less;
corner-only slivers joined side-on. Bigger gaps (between legs, tail and leg) stay open, as the walk lane asked.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, label

ROOT = Path(r"D:/dev/new-mech-rpg/docs/art/moba")
SRC = ROOT / "walk/fennec_s/final/frames"
STILL = ROOT / "walk/fennec_s/final/stills"
HERE = Path(__file__).parent
OUT = HERE / "frames"
VIEWS = ["e", "se", "ne", "s", "n"]
N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
FEET_ROWS = 8
pal = {tuple(int(p["hex"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)): p["role"]
       for p in json.load(open(ROOT / "fennec_s/take-b/cam35/palette.json"))}
GLOW = {c for c, r in pal.items() if r == "eye"}
sys.path.insert(0, str(ROOT / "rhino_l/take-a/anim"))
from selout_rhino import selout  # noqa: E402


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = a[max(-dy, 0):H - max(dy, 0), max(-dx, 0):W - max(dx, 0)]
    return out


def find_offset(still, frame):
    best = (-1, 0, 0)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            p = shift(still, dx, dy)
            m = (p[..., 3] > 0) & (frame[..., 3] > 0)
            n = int((np.all(p == frame, -1) & m).sum())
            if n > best[0]:
                best = (n, dx, dy)
    return best[1], best[2], best[0] / (still[..., 3] > 0).sum()


def touch(a, keep, fills):
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
            lr, ud = m[y, x - 1] and m[y, x + 1], m[y - 1, x] and m[y + 1, x]
            slit = (lr and ((not m[y + 1, x] and m[y + 1, x - 1] and m[y + 1, x + 1]) or
                            (not m[y - 1, x] and m[y - 1, x - 1] and m[y - 1, x + 1]))) or \
                   (ud and ((not m[y, x + 1] and m[y - 1, x + 1] and m[y + 1, x + 1]) or
                            (not m[y, x - 1] and m[y - 1, x - 1] and m[y + 1, x - 1])))
            if len(on) >= 3 and not slit:   # a 1 px dent is filled; a 1 px slit between legs stays open
                b[y, x, :3] = Counter(tuple(b[p][:3]) for p in on).most_common(1)[0][0]
                b[y, x, 3] = 255
                log["notches"] += 1
                ch += 1
        if not ch:
            break
    hl, hn = label(binary_fill_holes(b[..., 3] > 0) & (b[..., 3] == 0))
    big = []
    for k in range(1, hn + 1):
        pts = list(zip(*np.nonzero(hl == k)))
        if len(pts) > 4:
            ys, xs = zip(*pts)
            big.append([len(pts), int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))])
            continue
        for y, x in pts:
            on = [(y + dy, x + dx) for dy, dx in N4 if b[y + dy, x + dx, 3] > 0]
            b[y, x, :3] = Counter(tuple(b[p][:3]) for p in on).most_common(1)[0][0]
            b[y, x, 3] = 255
            log["pinholes"] += 1
        fills.append(pts[0])
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
    return b, log, big


def main():
    OUT.mkdir(exist_ok=True)
    report, live, new, allfills = {}, {}, {}, []
    for v in VIEWS:
        still = np.asarray(Image.open(STILL / f"{v}.png").convert("RGBA"))
        fr = [np.asarray(Image.open(SRC / f"{v}_f{i}.png").convert("RGBA")) for i in range(8)]
        dx, dy, share = find_offset(still, fr[1])
        live[v], new[v] = fr, []
        report[v] = {"still_offset": [dx, dy], "f1_body_match": round(float(share), 3), "frames": {}}
        for i, a in enumerate(fr):
            p = shift(still, dx, dy + (1 if i in (0, 4) else 0))
            body = (a[..., 3] > 0) & np.all(p == a, -1)
            ys = np.nonzero(a[..., 3] > 0)[0]
            keep = body.copy()
            keep[ys.max() - FEET_ROWS + 1:] = True
            fills = []
            b, log, big = touch(a, keep, fills)
            allfills += [(v, i, f) for f in fills]
            m = b[..., 3] > 0
            r = {**log, "changed": int(np.any(a != b, -1).sum()), "pieces": int(label(m)[1]),
                 "binary_alpha": set(np.unique(b[..., 3]).tolist()) <= {0, 255},
                 "off_palette": int(sum(1 for c in b[m][:, :3] if tuple(c) not in pal)),
                 "body_kept": bool(np.array_equal(b[body], a[body])),
                 "feet_rows_kept": bool(np.array_equal(b[ys.max() - FEET_ROWS + 1:], a[ys.max() - FEET_ROWS + 1:])),
                 "eyes_kept": all(tuple(b[y, x, :3]) == tuple(a[y, x, :3]) for y, x in zip(*np.nonzero(a[..., 3] > 0))
                                  if tuple(a[y, x, :3]) in GLOW),
                 "gaps_left_open": big}
            report[v]["frames"][f"f{i}"] = r
            Image.fromarray(b).save(OUT / f"{v}_f{i}.png")
            new[v].append(b)
        fs = report[v]["frames"].values()
        print(v, "offset", (dx, dy), "body match", round(float(share), 3), "|",
              " ".join(f"f{i}:{r['changed']}" for i, r in enumerate(fs)), "| pinholes",
              sum(r.get("pinholes", 0) for r in fs), "| all rules",
              all(r["pieces"] == 1 and r["binary_alpha"] and not r["off_palette"] and r["body_kept"]
                  and r["feet_rows_kept"] for r in fs),
              "| open gaps", [(k, len(r["gaps_left_open"])) for k, r in report[v]["frames"].items() if r["gaps_left_open"]])
    (HERE / "report.json").write_text(json.dumps(report, indent=1))
    boards(live, new, allfills)


def boards(live, new, allfills):
    grey = (0x5A, 0x60, 0x58, 255)
    rows = []
    for v in VIEWS:
        al = np.zeros((192, 192), bool)
        for a in live[v]:
            al |= a[..., 3] > 0
        ys, xs = np.nonzero(al)
        box = (int(xs.min()) - 2, int(ys.min()) - 2, int(xs.max()) + 3, int(ys.max()) + 3)
        for lab, fr, mark in ((f"{v} live", live[v], False), (f"{v} new", new[v], False), (f"{v} changed", new[v], True)):
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
                cells.append(c.resize((c.width * 2, c.height * 2), Image.NEAREST))
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
    # every pinhole fill: before | after at 6x, 20 px around it
    k, s = 6, 10
    cells = []
    for v, i, (py, px) in allfills[:40]:
        pair = []
        for a in (live[v][i], new[v][i]):
            c = Image.fromarray(a).crop((px - s, py - s, px + s, py + s)).resize((2 * s * k, 2 * s * k), Image.NEAREST)
            bg = Image.new("RGBA", c.size, grey)
            bg.alpha_composite(c)
            pair.append(bg)
        cells.append((f"{v} f{i} ({px},{py})", pair))
    if cells:
        cw = 2 * s * k
        F = Image.new("RGBA", (4 * (2 * cw + 30), ((len(cells) + 3) // 4) * (cw + 24)), (34, 37, 41, 255))
        d = ImageDraw.Draw(F)
        for n, (lab, (b0, b1)) in enumerate(cells):
            x, y = (n % 4) * (2 * cw + 30), (n // 4) * (cw + 24)
            d.text((x + 4, y + 4), lab + "  before | after", fill=(235, 235, 230, 255))
            F.alpha_composite(b0, (x, y + 20))
            F.alpha_composite(b1, (x + cw + 6, y + 20))
        F.save(HERE / "board_fills.png")


if __name__ == "__main__":
    main()
