"""Front shoulder line for poses front_shoulder_ink.py cannot fit (Claude, animation lane, 2026-11-04).

The braced shuffle's front row starts from the approved brace front_f3, which already carries the shoulder line. The
line is the difference between brace front_f3 and its pre_shoulder copy. For each target frame and each shoulder, the
offset (within +-4 px) where the pre-ink shoulder area matches the frame best is found, and the line is stamped there
onto opaque pixels. A side whose best match is under MIN_MATCH is skipped and reported.

    python shoulder_transfer.py <frames dir> [...]
Originals are kept in <frames dir>/pre_shoulder/.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
POST = HERE / "codex-set-b/brace/frames/front_f3.png"
PRE = HERE / "codex-set-b/brace/frames/pre_shoulder/front_f3.png"
MIN_MATCH = 0.6


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(int)


def main():
    post, pre = load(POST), load(PRE)
    delta = (post != pre).any(axis=2)
    for d in map(Path, sys.argv[1:]):
        keep = d / "pre_shoulder"
        keep.mkdir(exist_ok=True)
        for p in sorted(d.glob("front_f*.png")):
            if not (keep / p.name).exists():
                shutil.copyfile(p, keep / p.name)
            a = load(keep / p.name)
            out = a.copy()
            notes = []
            for name, half in (("left", slice(0, 96)), ("right", slice(96, 192))):
                m = np.zeros_like(delta)
                m[:, half] = delta[:, half]
                ys, xs = np.nonzero(m)
                y0, y1, x0, x1 = ys.min() - 3, ys.max() + 4, xs.min() - 3, xs.max() + 4
                best = (-1.0, 0, 0)
                for dy in range(-4, 5):
                    for dx in range(-4, 5):
                        ref = pre[y0:y1, x0:x1]
                        win = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
                        both = (ref[..., 3] > 0) | (win[..., 3] > 0)
                        same = ((ref == win).all(axis=2) & both).sum() / max(1, both.sum())
                        best = max(best, (same, dx, dy))
                score, dx, dy = best
                if score < MIN_MATCH:
                    notes.append(f"{name} skipped ({score:.2f})")
                    continue
                n = 0
                for y, x in zip(ys, xs):
                    if a[y + dy, x + dx, 3] > 0:
                        out[y + dy, x + dx] = post[y, x]
                        n += 1
                notes.append(f"{name} {n} px at {dx:+d},{dy:+d} ({score:.2f})")
            Image.fromarray(out.astype(np.uint8)).save(p)
            print(f"{d.parent.name} {p.name}: " + "; ".join(notes))


if __name__ == "__main__":
    main()
