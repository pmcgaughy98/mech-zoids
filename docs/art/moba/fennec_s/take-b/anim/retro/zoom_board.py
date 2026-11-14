"""Zoomed review board: input (or still) then the Retro frames, sel-out on, 4x, 5 per row. python zoom_board.py walk_n"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[3] / "rhino_l/take-a/anim"))
import selout_rhino  # noqa: E402
selout_rhino.OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
name = sys.argv[1]
off = json.loads((HERE / "offsets.json").read_text())[name]
inp = np.asarray(Image.open(HERE / "input" / f"{name}_128.png").convert("RGBA"))
ref = np.zeros((192, 192, 4), np.uint8)
ys, xs = np.nonzero(inp[..., 3] > 0)
ref[ys - off["dy"], xs - off["dx"]] = inp[ys, xs]
fr = [ref] + [np.asarray(Image.open(p).convert("RGBA")) for p in
              sorted(HERE.glob(f"frames/{name}_f*.png"), key=lambda p: int(p.stem.split("_f")[1]))]
al = np.any([f[..., 3] > 0 for f in fr], 0)
ys, xs = np.nonzero(al)
box = (xs.min() - 3, ys.min() - 3, xs.max() + 4, ys.max() + 4)
z, per = 4, 5
w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
rows = (len(fr) + per - 1) // per
b = Image.new("RGBA", (per * w, rows * h), (0x3D, 0x43, 0x50, 255))
for i, f in enumerate(fr):
    t = Image.fromarray(selout_rhino.selout(f)[0]).crop(box).resize((w, h), Image.NEAREST)
    b.alpha_composite(t, ((i % per) * w, (i // per) * h))
b.save(HERE / f"zoom-{name}.png")
print(b.size)
