"""Carries the n and ne stills' new detail ink onto the fennec's n and ne frames (Claude, animation lane, 2026-11-04).

The sprite factory installed capped detail ink on the approved n (+49 px) and ne (+50 px) stills after Preston's "Keep
all five" (remaster-pilot/RUN.md; his originals in views_pre_ink/). Frames built on the old stills now miss it, so the
pack check fails and idle/walk would pop. Per frame:
  - a frame that equals the old still exactly (f0 and the end frames) becomes the new still exactly;
  - otherwise each cluster of ink pixels is carried with its part: the old still's pixels around the cluster (the ink
    pixels left out) are matched in the frame within 6 px; when 85% or more of them match, the ink goes on at that
    shift, only on opaque texels. Parts the frame redrew do not match and get no ink (counted in the log).
Originals are kept once in <move>/frames_pre_ink/. Usage: python carry_ink.py [--apply]
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
ANIM = HERE.parent
TAKE = ANIM.parent
JOBS = {"n": [("codex-set-a", m) for m in ("idle", "walk", "sand_kick", "ear_burst", "sonic_boom")]
             + [("codex-set-b", m) for m in ("dig", "pop_out", "death")],
        "ne": [("codex-set-c", m) for m in ("idle", "walk", "sand_kick", "ear_burst", "sonic_boom")]
              + [("codex-set-d", m) for m in ("dig", "pop_out", "death")]}
FILE = {"n": "back", "ne": "ne"}
PAD, SEARCH, MIN_SCORE = 4, 6, 0.85
sys.path.insert(0, str(TAKE.parents[1] / "rhino_l/take-a/anim"))


def placed(path):
    c = np.zeros((192, 192, 4), np.uint8)
    c[20:180, 16:176] = np.asarray(Image.open(path).convert("RGBA"))
    return c


def clusters(mask):
    pts = list(zip(*np.nonzero(mask)))
    groups = []
    for p in pts:
        hit = [g for g in groups if any(abs(p[0] - q[0]) <= 2 and abs(p[1] - q[1]) <= 2 for q in g)]
        merged = [p] + [q for g in hit for q in g]
        groups = [g for g in groups if g not in hit] + [merged]
    return groups


def carry(f, old, new, groups, ink):
    out = f.copy()
    placed_n, missed = 0, 0
    for g in groups:
        ys, xs = [q[0] for q in g], [q[1] for q in g]
        y0, y1, x0, x1 = min(ys) - PAD, max(ys) + PAD + 1, min(xs) - PAD, max(xs) + PAD + 1
        tmpl = old[y0:y1, x0:x1]
        use = (tmpl[..., 3] > 0) & ~ink[y0:y1, x0:x1]
        best = (-1.0, 0, 0)
        for dy in range(-SEARCH, SEARCH + 1):
            for dx in range(-SEARCH, SEARCH + 1):
                if y0 + dy < 0 or x0 + dx < 0 or y1 + dy > 192 or x1 + dx > 192:
                    continue
                win = f[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
                score = (np.all(win == tmpl, -1) & use).sum() / max(1, use.sum())
                if score > best[0] or (score == best[0] and abs(dx) + abs(dy) < abs(best[1]) + abs(best[2])):
                    best = (score, dx, dy)
        score, dx, dy = best
        if score < MIN_SCORE:
            missed += len(g)
            continue
        for y, x in g:
            if out[y + dy, x + dx, 3] > 0:
                out[y + dy, x + dx] = new[y, x]
                placed_n += 1
    return out, placed_n, missed


def main():
    apply = "--apply" in sys.argv
    import selout_rhino
    selout_rhino.OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
    log, board_rows = {}, []
    for v, jobs in JOBS.items():
        old, new = placed(TAKE / "views_pre_ink" / f"{v}.png"), placed(TAKE / "views" / f"{v}.png")
        ink = np.any(old != new, -1)
        cols = {"#" + bytes(c).hex() for c in new[ink][:, :3]}
        groups = clusters(ink)
        print(f"{v}: {int(ink.sum())} ink px in {len(groups)} clusters, colours {sorted(cols)}")
        for set_name, move in jobs:
            d = ANIM / set_name / move / "frames"
            keep = ANIM / set_name / move / "frames_pre_ink"
            files = sorted(d.glob(f"{FILE[v]}_f*.png"), key=lambda p: int(p.stem.split("_f")[1]))
            before, after, rec = [], [], []
            for p in files:
                src = keep / p.name if (keep / p.name).exists() else p
                f = np.asarray(Image.open(src).convert("RGBA"))
                if np.array_equal(f, old):
                    out, how = new.copy(), "still"
                else:
                    out, n_in, n_miss = carry(f, old, new, groups, ink)
                    how = f"+{n_in} miss {n_miss}"
                before.append(f)
                after.append(out)
                rec.append(how)
                if apply:
                    keep.mkdir(exist_ok=True)
                    if not (keep / p.name).exists():
                        shutil.copy(p, keep / p.name)
                    Image.fromarray(out).save(p)
            log[f"{move}_{v}"] = rec
            print(f"  {move} {v}: {rec}")
            board_rows += [before, after]
    (HERE / "carry-log.json").write_text(json.dumps(log, indent=1))
    box, z = (40, 60, 152, 164), 3
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    cols = max(len(r) for r in board_rows)
    board = Image.new("RGBA", (cols * w, len(board_rows) * h), (0x3D, 0x43, 0x50, 255))
    for r, row in enumerate(board_rows):
        for c, a in enumerate(row):
            t = Image.fromarray(selout_rhino.selout(a)[0]).crop(box).resize((w, h), Image.NEAREST)
            board.alpha_composite(t, (c * w, r * h))
    board.save(HERE / "carry-board.png")
    print("board carry-board.png (before/after row pairs, n moves then ne moves);", "applied" if apply else "dry run")


if __name__ == "__main__":
    main()
