"""Finds thin stray slivers in the fennec's se/ne frames (Claude, animation lane, 2026-11-04).
Preston: "Walks NE is off the top but lots of cutoff etc. Needs touching up", "Sonic boom too and many others do pass".
A sliver is a part of the silhouette an opening with a 3x3 square removes, that is line-like (at most 2 px thick)
and at least MIN_LEN long. The approved stills are scanned the same way; their own slivers (ear tips, tail tip) are
the baseline. Writes slivers.json and slivers-board.png (every flagged frame, flagged pixels in red).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = Path(__file__).parent
TAKE = HERE.parents[1]
MOVES = {"codex-set-c": [("idle", 5), ("walk", 8), ("sand_kick", 6), ("ear_burst", 6), ("sonic_boom", 8)],
         "codex-set-d": [("dig", 6), ("pop_out", 5), ("death", 7)]}
MIN_LEN = 4


def slivers(a):
    m = a[..., 3] > 0
    thin = m & ~ndimage.binary_opening(m, np.ones((3, 3), bool))
    lab, n = ndimage.label(thin, np.ones((3, 3), bool))
    out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        if max(h, w) >= MIN_LEN and min(h, w) <= 2:
            out.append(dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()), n=int(len(ys))))
    return out, lab


def main():
    report, flagged = {}, []
    for v in ("se", "ne"):
        st = np.zeros((192, 192, 4), np.uint8)
        st[20:180, 16:176] = np.asarray(Image.open(TAKE / "views" / f"{v}.png").convert("RGBA"))
        report[f"still_{v}"] = slivers(st)[0]
    for s, moves in MOVES.items():
        for m, n in moves:
            for v in ("se", "ne"):
                for i in range(n):
                    a = np.asarray(Image.open(TAKE / "anim" / s / m / "frames" / f"{v}_f{i}.png").convert("RGBA"))
                    found, _ = slivers(a)
                    if found:
                        report[f"{m}_{v}_f{i}"] = found
                        flagged.append((f"{m} {v} f{i}", a, found))
    (HERE / "slivers.json").write_text(json.dumps(report, indent=1))
    box, z, cols = (40, 60, 152, 164), 3, 6
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    board = Image.new("RGBA", (cols * w, max(1, -(-len(flagged) // cols)) * h), (0x3D, 0x43, 0x50, 255))
    d = ImageDraw.Draw(board)
    for k, (lab, a, found) in enumerate(flagged):
        b = a.copy()
        for f in found:
            sub = b[f["y0"]:f["y1"] + 1, f["x0"]:f["x1"] + 1]
            sub[sub[..., 3] > 0] = (255, 40, 40, 255)
        x, y = (k % cols) * w, (k // cols) * h
        board.alpha_composite(Image.fromarray(b).crop(box).resize((w, h), Image.NEAREST), (x, y))
        d.text((x + 4, y + 4), lab, fill=(255, 230, 150, 255))
    board.save(HERE / "slivers-board.png")
    print("stills:", {k: len(v) for k, v in report.items() if k.startswith("still")})
    print(len(flagged), "frames flagged:", ", ".join(l for l, _, _ in flagged))


if __name__ == "__main__":
    main()
