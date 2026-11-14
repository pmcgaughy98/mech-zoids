"""Claude's review board: the still then each new frame, sel-out on, 4x, tight crop. python zoom_rows.py walk|sand_kick"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim")
import selout_rhino
selout_rhino.OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
HERE = Path(__file__).parent
move = sys.argv[1]
n = 8 if move == "walk" else 6
rows = []
for fv, v in (("back", "n"), ("ne", "ne")):
    st = np.zeros((192, 192, 4), np.uint8)
    st[20:180, 16:176] = np.asarray(Image.open(HERE.parent.parent / "views" / f"{v}.png").convert("RGBA"))
    rows.append([st] + [np.asarray(Image.open(HERE / move / "frames" / f"{fv}_f{i}.png").convert("RGBA")) for i in range(n)])
z = 4
out = []
for row in rows:
    al = np.any([f[..., 3] > 0 for f in row], 0)
    ys, xs = np.nonzero(al)
    box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    b = Image.new("RGBA", (len(row) * w, h), (0x3D, 0x43, 0x50, 255))
    for c, a in enumerate(row):
        b.alpha_composite(Image.fromarray(selout_rhino.selout(a)[0]).crop(box).resize((w, h), Image.NEAREST), (c * w, 0))
    out.append(b)
W = max(b.width for b in out)
final = Image.new("RGBA", (W, sum(b.height for b in out)), (0x3D, 0x43, 0x50, 255))
y = 0
for b in out:
    final.alpha_composite(b, (0, y)); y += b.height
final.save(HERE / f"zoom-{move}.png")
print(final.size)
