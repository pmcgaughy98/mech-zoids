"""Wolf take B: bring the back views down to the front views' heights (Claude, 2026-11-03).

Preston: "do the back view fix". Codex's back camera sat too high, so n, ne and nw stand 80 to 84 px against the
front's 70 to 72. Each back view is squashed vertically with nearest-neighbour (no new colours) to its front partner's
height, keeping its width, feet row and centre. Everything else is copied unchanged into fixed/.

    python fix_backs.py        (from this folder)
"""
import os
import shutil

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "views"), os.path.join(HERE, "fixed")
PAIRS = {"n": "s", "ne": "se", "nw": "sw"}

os.makedirs(OUT, exist_ok=True)
for name in ("n", "ne", "nw", "e", "w", "s", "se", "sw"):
    src = os.path.join(SRC, name + ".png")
    if name not in PAIRS:
        shutil.copy(src, os.path.join(OUT, name + ".png"))
        continue
    im = Image.open(src).convert("RGBA")
    x0, y0, x1, y1 = im.getbbox()
    target = Image.open(os.path.join(SRC, PAIRS[name] + ".png")).getbbox()
    h = target[3] - target[1]
    part = im.crop((x0, y0, x1, y1)).resize((x1 - x0, h), Image.NEAREST)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(part, (x0, y1 - h))
    out.save(os.path.join(OUT, name + ".png"))
    print("%s: %d -> %d px tall (matches %s)" % (name, y1 - y0, h, PAIRS[name]))
