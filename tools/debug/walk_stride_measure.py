"""How fast does a walk carry its machine? (Claude, 2026-11-04, game feel lane.)

A foot that is planted keeps its shape from one frame to the next and slides backward in sprite space. For each
foot blob on the ground line, this finds the x shift into the next frame that overlaps it best. Shifts with a good
overlap (IoU >= 0.7) and pointing backward are planted feet; their median, times the fps and the metres per pixel,
is the speed at which the feet stay put. Use the side view: it is the only one where the step runs across the screen.

    python tools/debug/walk_stride_measure.py <frames dir> [view ...] [--fps 8] [--m-per-px 0.02]

Rerun it after any change to the walk frames (the Codex remaster pass, a new walk) and update stride_speed in
scripts/moba3d/machine_test_player.gd.
"""
import statistics
import sys
from pathlib import Path

from PIL import Image

args = sys.argv[1:]
fps, m_per_px = 8.0, 0.02
if "--fps" in args:
    i = args.index("--fps"); fps = float(args[i + 1]); del args[i:i + 2]
if "--m-per-px" in args:
    i = args.index("--m-per-px"); m_per_px = float(args[i + 1]); del args[i:i + 2]
root = Path(args[0])
views = args[1:] or ["side"]


def foot_band(path):
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A").load()
    w, h = im.size
    low = max(y for y in range(h) for x in range(w) if a[x, y] > 0)
    return low, {(x, y) for y in range(low - 8, low + 3) for x in range(w) if 0 <= y < h and a[x, y] > 0}


def blobs(mask, low):
    xs = sorted({x for x, y in mask if y >= low - 2})
    out, run = [], []
    for x in xs:
        if run and x != run[-1] + 1:
            out.append(run)
            run = []
        run.append(x)
    if run:
        out.append(run)
    return out


for view in views:
    frames = sorted(root.glob(f"{view}_f*.png"), key=lambda p: int(p.stem.split("_f")[1]))
    if not frames:
        print(f"{view}: no frames in {root}")
        continue
    bands = [foot_band(p) for p in frames]
    planted, swing = [], []
    for i, (low, m0) in enumerate(bands):
        m1 = bands[(i + 1) % len(bands)][1]
        for b in blobs(m0, low):
            part = {(x, y) for x, y in m0 if b[0] - 1 <= x <= b[-1] + 1}
            dx = max(range(-12, 13), key=lambda d: len({(x + d, y) for x, y in part} & m1))
            iou = len({(x + dx, y) for x, y in part} & m1) / len(part)
            if iou >= 0.7 and abs(dx) < 12:  # a best match at the search edge is a wrong match
                (planted if dx < 0 else swing).append(dx)
    if not planted:
        print(f"{view}: no planted feet found")
        continue
    med = -statistics.median(planted)
    q = statistics.quantiles([-d for d in planted], n=4) if len(planted) >= 4 else [med, med, med]
    spd = lambda px: px * fps * m_per_px
    print(f"{view}: {len(frames)} frames, {len(planted)} planted-foot shifts {sorted(planted)}")
    print(f"  planted foot slides {med:.1f} px/frame (middle half {q[0]:.1f} to {q[2]:.1f})")
    print(f"  => feet stay put at {spd(med):.2f} m/s (middle half {spd(q[0]):.2f} to {spd(q[2]):.2f}) "
          f"at {fps:g} fps and {m_per_px:g} m/px")
