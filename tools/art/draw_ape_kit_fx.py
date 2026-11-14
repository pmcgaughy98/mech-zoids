"""Effect art for the gorilla's kit in the 3D slice (Claude, 2026-11-04, game feel lane).
- silverback_ring_f0.png: the passive's aura ring, a dashed hex-green ring with an ink edge, drawn as the ground ellipse the
  30-degree chase camera sees (2:1), at 50 texels a metre for a 2.5 m radius (a placeholder size). Fx3D.spawn_flat
  lays it flat and stretches it back to a circle. Chest beat reuses it as a quick pulse.
- taunt_mark.png: the mark over a taunted machine's head, a "!" in the same green with the #141218 sel-out.
Colours are the hex tile's own (art/fx/moba3d/hex_tile.png): bright (63, 224, 127), deep (27, 154, 82).
"""
import math
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parents[2] / "art" / "fx" / "moba3d"
BRIGHT, DEEP, INK = (63, 224, 127), (27, 154, 82), (20, 18, 24)

# Aura ring: radius 2.5 m = 125 texels across the ground, squashed 2:1 for the camera.
R = 125
W, H = 2 * R + 2, R + 2
ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
px = ring.load()
cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
steps = 2400
for i in range(steps):
    a = math.tau * i / steps
    seg = int((a / math.tau) * 72) % 2  # 72 segments, every other one drawn: a dashed, panel-like ring
    if seg:
        continue
    x, y = round(cx + R * math.cos(a)), round(cy + R * 0.5 * math.sin(a))
    px[x, y] = BRIGHT + (230,)
    for yi in (y - 1, y + 1):  # a one-texel ink edge on both sides, so the ring reads on grass (the sel-out colour)
        if 0 <= yi < H and px[x, yi][3] == 0:
            px[x, yi] = INK + (150,)
ring.save(OUT / "silverback_ring_f0.png")

# Taunt mark: a 5x9 "!" with a one-texel ink outline (7x11).
glyph = ["XXX", "XXX", "XXX", "XXX", "XXX", ".X.", "...", "XXX", "XXX"]
mark = Image.new("RGBA", (7, 11), (0, 0, 0, 0))
m = mark.load()
cells = {(x + 2, y + 1) for y, row in enumerate(glyph) for x, ch in enumerate(row) if ch == "X"}
for (x, y) in cells:
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (x + dx, y + dy) not in cells and 0 <= x + dx < 7 and 0 <= y + dy < 11:
                m[x + dx, y + dy] = INK + (255,)
for (x, y) in cells:
    m[x, y] = BRIGHT + (255,) if x != 4 else DEEP + (255,)  # a darker centre column gives it a little form
mark.save(OUT / "taunt_mark.png")
print("wrote", OUT / "silverback_ring_f0.png", ring.size, "and", OUT / "taunt_mark.png", mark.size)
