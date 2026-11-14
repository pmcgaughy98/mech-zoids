"""Fennec cam35 eye fix (fleet redraw lane, Claude, 2026-11-04, on Preston's "Yes, fix the eyes").

Codex drew the eyes at about the right size, but the palette mapping turned some pale glow pixels into steel
(d6d6dc, 9d9ba2) or violet highlight (e0c8ff). This script puts those pixels back on the eye ramp, along the dark
socket Codex drew, the gorilla lane's method. It also makes the two front eyes mirror images.
Reads cam35/<view>_codex_original.png, which is saved on the first run, and writes views_cam35/<view>.png.
Every pixel it changes is checked against its expected old colour first.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

TAKE = Path(sys.argv[1])
C = {"g": "3fe8b0", "b": "c8fff0", "w": "f6fffb", "#": "141218", "8": "d6d6dc", "9": "9d9ba2", "1": "e0c8ff"}
rgb = lambda k: [int(C[k][i:i + 2], 16) for i in (0, 2, 4)]

# (x, y, old, new). s: the left eye; the right eye is its mirror at x' = 158 - x.
S_LEFT = [
    (71, 106, "8", "b"),
    (72, 107, "8", "w"),
    (70, 108, "9", "#"),
]
# The right eye after the fix, as the mirror of the left (x, y, new), with old colours to check.
S_RIGHT = [
    (89, 105, "#", "g"),
    (87, 106, "g", "b"),
    (86, 107, "8", "w"), (85, 107, "w", "w"), (84, 107, "g", "g"),
    (88, 108, "1", "#"), (87, 108, "g", "b"), (86, 108, "w", "w"), (85, 108, "8", "w"), (84, 108, "8", "g"),
]
SE = [
    (94, 107, "8", "b"), (96, 107, "8", "w"), (97, 107, "8", "w"), (99, 107, "9", "g"),
    (94, 109, "9", "g"), (95, 109, "8", "g"), (96, 109, "8", "g"), (97, 109, "8", "g"),
]
EYES = [np.array(rgb(k)) for k in "gbw"]


def eye_px(a):
    m = np.zeros(a.shape[:2], bool)
    for e in EYES:
        m |= np.all(a[..., :3] == e, axis=2)
    return int((m & (a[..., 3] > 0)).sum())


for view, edits in (("s", S_LEFT + S_RIGHT), ("se", SE)):
    orig = TAKE / "cam35" / f"{view}_codex_original.png"
    if not orig.exists():
        shutil.copy2(TAKE / "views_cam35" / f"{view}.png", orig)
    a = np.asarray(Image.open(orig).convert("RGBA")).copy()
    before = eye_px(a)
    for x, y, old, new in edits:
        assert list(a[y, x, :3]) == rgb(old) and a[y, x, 3] > 0, (view, x, y, old, a[y, x])
        a[y, x, :3] = rgb(new)
    Image.fromarray(a).save(TAKE / "views_cam35" / f"{view}.png")
    print(f"{view}: {len(edits)} px changed, eye px {before} -> {eye_px(a)}")
