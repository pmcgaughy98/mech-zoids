"""Remove the one stray eye-glow pixel on the wolf's ne ear tip (fleet redraw lane, 2026-11-04).

Preston: "Turn test, then fix". The game feel turn test passed (no pop), so the fix applies.
Keeps Codex's original as cam35/ne_codex_original.png. Sets (119, 71) from eye glow 6ff0dc to gunmetal base 6e6e7e,
the colour of the ear tip above and beside it. The outline and every height stay the same.
"""
import shutil
from pathlib import Path

from PIL import Image

TAKE = Path(__file__).resolve().parent.parent
NE = TAKE / "views_cam35" / "ne.png"
ORIG = TAKE / "cam35" / "ne_codex_original.png"
if not ORIG.exists():
    shutil.copy2(NE, ORIG)
im = Image.open(ORIG).convert("RGBA")
assert im.getpixel((119, 71)) == (0x6F, 0xF0, 0xDC, 255), im.getpixel((119, 71))
im.putpixel((119, 71), (0x6E, 0x6E, 0x7E, 255))
eye = sum(1 for p in im.getdata() if p[3] and p[:3] == (0x6F, 0xF0, 0xDC))
assert eye == 0, eye
im.save(NE)
print("ne fixed: 1 pixel, eye glow left in ne:", eye, "bbox", im.getbbox())
