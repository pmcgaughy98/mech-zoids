"""Rebuild back frames 1-3 so the rhino rears on its hind legs, as in the front and side rows.

Codex's back row lifted the whole body on longer legs with all four feet planted. Here each frame starts
from back_f0: the outer (hind) legs stay exactly as drawn; the dark inner (front) legs are moved up by L
and slide behind the belly, leaving daylight under them; the whole upper body (shoulder pads, top plate, horn) lifts off the hips
by adding plain side rows at row 119, and the top plate grows a little as it tips toward the camera (his notes, 2026-11-03).
The Codex versions are kept in frames_back_codex/.
"""
from pathlib import Path
import numpy as np
from PIL import Image

D = Path(__file__).parent
DARK = {(0x14, 0x12, 0x18), (0x21, 0x1E, 0x27), (0x3D, 0x3A, 0x44)}
f0 = np.asarray(Image.open(D / "frames/back_f0.png").convert("RGBA")).copy()
TOP = int(np.where(f0[..., 3] > 0)[0].min())
HIP, LEG0 = 131, 144          # body rows end at HIP; front legs show below LEG0
# frame: (T top-plate rows added, S rows added at the straight body sides (row 119) so shoulders and top rise
# together off the hips, L front-leg lift, C hind-leg crouch rows)
PLAN = {1: (1, 2, 4, 0), 2: (3, 6, 12, 1), 3: (5, 9, 15, 2)}
TOPBAND, SIDEROW, LEGBAND = (94, 106), 119, (147, 151)
assert (f0[119] == f0[120]).all(), 'row 119 is not a plain side row'

def is_dark(p):
    return p[3] > 0 and tuple(int(v) for v in p[:3]) in DARK

inner = np.zeros(f0.shape[:2], bool)
for y in range(LEG0, 161):
    for x in range(83, 111):
        inner[y, x] = is_dark(f0[y, x])
def resample(rows, n):
    return [rows[min(len(rows) - 1, int(i * len(rows) / n))] for i in range(n)]

for c, (T, S, L, C) in PLAN.items():
    a = f0.copy()
    a[inner] = 0
    for y, x in zip(*np.where(inner)):
        ny = y - L
        if ny >= LEG0 and (a[ny, x, 3] == 0):
            a[ny, x] = f0[y, x]
    # whole upper body (shoulder pads, top plate, horn) lifts off the hips; the top plate also grows a little as it tips
    rows = []
    y = TOP
    while y <= HIP:
        if y == TOPBAND[0]:
            band = [a[k] for k in range(TOPBAND[0], TOPBAND[1] + 1)]; rows += resample(band, len(band) + T); y = TOPBAND[1] + 1
        elif y == SIDEROW:
            rows += [a[y]] * (1 + S); y += 1
        else:
            rows.append(a[y]); y += 1
    body = np.stack(rows)
    out = a.copy()
    out[:HIP + 1] = 0
    out[HIP + 1 - len(body):HIP + 1] = body
    # hind legs bend a little at the top of the rear: drop C rows from the foot band, everything above moves down
    if C:
        drop = set(np.round(np.linspace(LEGBAND[0] + 1, LEGBAND[1] - 1, C)).astype(int).tolist())
        keep = [k for k in range(0, 161) if k not in drop]
        top = np.zeros((161, 192, 4), np.uint8); top[161 - len(keep):] = out[keep]
        out[:161] = top
    Image.fromarray(out).save(D / f"frames/back_f{c}.png")
    ys, xs = np.where(out[..., 3] > 0)
    print(f"back_f{c}: top +{T}, shoulders up +{S}, front legs up {L}, crouch {C}; size {xs.max()-xs.min()+1}x{ys.max()-ys.min()+1}, bottom {ys.max()}")

# board: Codex back row / rebuilt back row / side row for the motion, 4x on the stage colour
S, BG = 4, (0x3D, 0x43, 0x50, 255)
sets = [[Image.open(D / ("frames_back_codex" if c in PLAN else "frames") / f"back_f{c}.png") for c in range(6)],
        [Image.open(D / "frames" / f"back_f{c}.png") for c in range(6)],
        [Image.open(D / "frames" / f"side_f{c}.png") for c in range(6)]]
box = (40, 70, 152, 164)
cw, ch = (box[2] - box[0]) * S // 2, (box[3] - box[1]) * S // 2
board = Image.new("RGBA", (6 * cw, 3 * ch), BG)
for r, row in enumerate(sets):
    for c, im in enumerate(row):
        board.alpha_composite(im.convert("RGBA").crop(box).resize((cw, ch), Image.NEAREST), (c * cw, r * ch))
board.save(D / "review-back-rear.png")
