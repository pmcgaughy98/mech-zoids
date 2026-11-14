"""Black line between the front view's shoulder plates and the hump (Claude, 2026-11-04).

Preston: "also put a black outline around top of shoulders so you can tell they are seperate on front view".
The shoulder is the plate over each front knee disc (se and side views show it as a dome with a black line over its
top). In the front view it is the block over each knee disc: cols 61-76 and 118-133, rows 121-135 of the Codex walk
frame 0. It already has a dark channel on its inner side and an outline under it, but no top edge, so it runs up
into the pale flank. This draws a domed one-texel #141218 top line from the outer outline to the inner channel on
each side, mirrored, and lights the texel under it one step (orange to yellow) like the dome rim in se. The line is placed on the Codex walk frame 0 (codex-consistency/frames/front_f0.png) and moved to
each target frame by matching the upper body, so it follows the bob. Frames whose upper body does not match within
6% are skipped and listed. Originals are kept in <dir>/pre_shoulder/.
Usage: python front_shoulder_ink.py <frames dir> [<frames dir> ...]
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
INK = (0x14, 0x12, 0x18)
TEMPLATE = HERE / "codex-consistency/frames/front_f0.png"
LEFT = [(61, 124), (62, 123), (63, 122), (64, 121), (65, 121), (66, 120), (67, 120), (68, 120), (69, 120), (70, 120),
        (71, 121), (72, 121), (73, 121), (74, 122), (75, 122), (76, 122)]
SIDES = [((58, 112, 80, 131), LEFT), ((114, 112, 136, 131), [(194 - x, y) for x, y in LEFT])]  # region, arc
ORANGE, YELLOW, BROWN = (0xD1, 0x8A, 0x0A), (0xFF, 0xCF, 0x1F), (0x7A, 0x4A, 0x06)


def match(a, t, region):
    x0, y0, x1, y1 = region
    tw = t[y0:y1, x0:x1]
    best = (1.0, 0, 0)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            w = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
            op = (tw[..., 3] > 0) | (w[..., 3] > 0)
            bad = np.any(tw[..., :4] != w[..., :4], axis=-1) & op
            best = min(best, (bad.sum() / max(op.sum(), 1), dx, dy))
    return best


def ink_file(p, t, keep):
    a = np.asarray(Image.open(p).convert("RGBA")).copy()
    notes = []
    for side, (region, arc) in zip(("left", "right"), SIDES):
        miss, dx, dy = match(a, t, region)
        if miss > 0.06:
            notes.append(f"{side} skipped ({miss:.0%} differs)")
            continue
        n = 0
        for x, y in arc:
            x, y = x + dx, y + dy
            if a[y, x, 3] and tuple(a[y, x, :3]) != INK:
                a[y, x, :3] = INK
                n += 1
            if a[y + 1, x, 3] and tuple(a[y + 1, x, :3]) in (ORANGE, BROWN):
                a[y + 1, x, :3] = YELLOW
        notes.append(f"{side} offset ({dx},{dy}) {miss:.1%}, {n} px")
    keep.mkdir(exist_ok=True)
    if not (keep / p.name).exists():
        shutil.copy2(p, keep / p.name)
    Image.fromarray(a).save(p)
    return f"{p.name}: " + "; ".join(notes)


def main():
    t = np.asarray(Image.open(TEMPLATE).convert("RGBA"))
    for d in map(Path, sys.argv[1:]):
        for p in sorted(d.glob("front_f*.png")):
            src = d / "pre_shoulder" / p.name  # rerun from the kept original so the line is never doubled
            if src.exists():
                shutil.copy2(src, p)
            print(ink_file(p, t, d / "pre_shoulder"))


if __name__ == "__main__":
    main()
