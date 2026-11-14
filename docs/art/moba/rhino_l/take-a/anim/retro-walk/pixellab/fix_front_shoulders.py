"""Separate the front walk's shoulders from its legs again (Claude, 2026-11-04).

Preston on the posed front walk: "the shoulder and the big bulky body look fused as part of the leg just fyi
compared to the others." PixelLab drew each shoulder plate down onto the knee disc, losing the dark underside band
the approved still (ground-pound front f0) has between them.

Per frame, per front-leg column band (outer columns, outside the head and horn band):
  - from the knee disc's top row down (first row with 3 or more light-grey disc pixels), keep PixelLab's leg, so
    the posed step Preston liked is untouched;
  - above it, use the approved still's pixels (shoulder plate, dark underside), moved by the frame's sideways
    body offset (best match of the upper body, within 2 px).
The middle band (head, horn, chest) also comes from the still with the same offset. Then the sel-out pass again.
Writes pixellab/frames/front_f*.png (the fused originals go to pixellab/frames/fused/) and front-shoulder-fix.png.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
ANIM = HERE.parent.parent
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402

DISC = np.array([0x9D, 0x9B, 0xA2])
STILL = ANIM / "codex-ground-pound/clean/frames_selout/front_f0.png"


def disc_top(a, x0, x1, y0=118):
    band = a[:, x0:x1]
    hits = (np.all(band[..., :3] == DISC, -1) & (band[..., 3] > 0)).sum(1)
    rows = [y for y in range(y0, 162) if hits[y] >= 3]
    return rows[0] if rows else None


def shift_x(a, dx):
    out = np.zeros_like(a)
    if dx >= 0:
        out[:, dx:] = a[:, :a.shape[1] - dx]
    else:
        out[:, :dx] = a[:, -dx:]
    return out


def main():
    still = np.asarray(Image.open(STILL).convert("RGBA"))
    ys, xs = np.where(still[..., 3] > 0)
    cx = (xs.min() + xs.max()) // 2
    bands = [(xs.min() - 3, cx - 14), (cx + 15, xs.max() + 4)]
    st_tops = [disc_top(still, *b) for b in bands]
    src = HERE / "frames"
    keep = src / "fused"
    keep.mkdir(exist_ok=True)
    before, after = [], []
    for i in range(8):
        p = src / f"front_f{i}.png"
        if not (keep / p.name).exists():
            shutil.copy(p, keep / p.name)
        f = np.asarray(Image.open(keep / p.name).convert("RGBA"))
        # sideways body offset: best match of the upper body (rows above the shoulders' bottom)
        best = max(range(-2, 3), key=lambda d: (np.all(shift_x(still, d)[95:130] == f[95:130], -1)
                                               & (f[95:130, :, 3] > 0)).sum())
        s = shift_x(still, best)
        out = s.copy()
        tops = []
        for (x0, x1), st in zip(bands, st_tops):
            t = disc_top(f, x0, x1) or st
            tops.append(t)
            cut = min(t, st)  # a lowered leg must not leave the still's own knee showing above it
            out[cut:, x0:x1] = f[cut:, x0:x1]
        # middle band below the knees: the frame's own (belly shadow and hind feet, if any)
        out[150:, bands[0][1]:bands[1][0]] = f[150:, bands[0][1]:bands[1][0]]
        out, _, _ = selout(out)
        Image.fromarray(out).save(p)
        before.append(f)
        after.append(out)
        print(f"front_f{i}: body offset {best:+d}, disc tops {tops} (still {st_tops}), "
              f"bottom {np.where(out[..., 3] > 0)[0].max()}")
    crop, k = (xs.min() - 3, ys.min() - 3, xs.max() + 4, ys.max() + 6), 4
    w, h = (crop[2] - crop[0]) * k, (crop[3] - crop[1]) * k
    im = Image.new("RGBA", (w * 9, h * 2 + 28), (0x3D, 0x43, 0x50, 255))
    d = ImageDraw.Draw(im)
    for j, row in enumerate(([still] + before, [still] + after)):
        for i, a in enumerate(row):
            im.alpha_composite(Image.fromarray(a).crop(crop).resize((w, h), Image.NEAREST), (i * w, 14 + j * (h + 14)))
            d.text((i * w + 4, j * (h + 14)), "still" if i == 0 else f"{'fused' if j == 0 else 'fixed'} f{i - 1}",
                   fill=(255, 230, 150, 255))
    im.save(HERE / "front-shoulder-fix.png")
    print("saved front-shoulder-fix.png")


if __name__ == "__main__":
    main()
