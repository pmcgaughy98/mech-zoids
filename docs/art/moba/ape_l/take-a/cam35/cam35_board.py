"""Board and checks: the approved gorilla views against the 35 degree redraw (cam35).

Fleet redraw lane, Claude, 2026-11-04. Adapted from rhino_l/take-a/cam35/cam35_board.py.
Reads ../views and ../views_cam35 (s, se, e, ne, n), writes board_cam35.png and verify.txt here.
Sel-out is added for review only (the rhino's selout with this gorilla's darkest colour); the packer adds it in game.
Nothing in either views folder is written.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
TAKE = HERE.parent
MOBA = TAKE.parent.parent
sys.path.insert(0, str(MOBA / "rhino_l" / "take-a" / "anim"))
import selout_rhino  # noqa: E402

selout_rhino.OUTLINE = np.array([0x14, 0x1A, 0x16], np.uint8)
VIEWS = ["s", "se", "e", "ne", "n"]
HULL_H = {"s": 83, "se": 89, "e": 89, "ne": 90, "n": 85}  # guide_sizes.txt, the shape guide at 35 degrees
APP_ACC = {"s": 10.2, "se": 8.5, "e": 8.9, "ne": 7.6, "n": 8.4}
GLOW = {(0x1B, 0x9A, 0x52), (0x3F, 0xE0, 0x7F), (0xD6, 0xFF, 0xE6)}
ACC = (0x14, 0x1A, 0x16)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def size(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


palset = {rgb(p["hex"]) for p in json.loads((HERE / "palette.json").read_text())}
sets = {"Approved\n(low camera)": {v: load(TAKE / "views" / f"{v}.png") for v in VIEWS},
        "cam35\n(this run)": {v: load(TAKE / "views_cam35" / f"{v}.png") for v in VIEWS}}
app, new = sets.values()

# ---- checks, written to verify.txt ----
out = []
for v in VIEWS:
    a = new[v]
    op = a[..., 3] > 0
    alpha = sorted(set(np.unique(a[..., 3]).tolist()))
    left = {tuple(c) for c in a[op][:, :3]} - palset
    ys, xs = np.nonzero(op)
    border = ys.min() == 0 or xs.min() == 0 or ys.max() == a.shape[0] - 1 or xs.max() == a.shape[1] - 1
    acc = np.all(a[..., :3] == ACC, axis=2)[op].mean() * 100
    g = np.zeros(op.shape, bool)
    for c in GLOW:
        g |= np.all(a[..., :3] == c, axis=2)
    g &= op
    lab, n = ndimage.label(g, structure=np.ones((3, 3)))
    comps = sorted((((lab[sl] == i).sum()), sl[0].start, sl[0].stop, sl[1].start, sl[1].stop)
                   for i, sl in enumerate(ndimage.find_objects(lab), 1))[::-1]
    w, h = size(a)
    wa, ha = size(app[v])
    out.append(f"{v:>2}: {w}x{h} (approved {wa}x{ha}), H/approved {h / ha:.2f}, H/shape guide {h / HULL_H[v]:.2f}; "
               f"lowest row {ys.max()}; border {'TOUCH' if border else 'clear'}; alpha {alpha}; "
               f"off-palette {len(left)}; accent {acc:.1f}% (approved {APP_ACC[v]}%)")
    out.append("     glow groups (px, y0, y1, x0, x1): " + ", ".join(str(tuple(int(x) for x in c)) for c in comps[:6]))
spread = [size(new[v])[1] / size(app[v])[1] for v in VIEWS]
out.append(f"H/approved spread {max(spread) - min(spread):.2f}")
meas = subprocess.run([sys.executable, str(MOBA / "cam35_fleet" / "hull_guide.py"), "measure", str(TAKE / "views"),
                       str(TAKE / "views"), str(TAKE / "views_cam35")], capture_output=True, text=True)
out.append("shape-aware angle measure (pitch at which the solid cut from the approved outlines best matches each view):")
out.append(meas.stdout.strip() or meas.stderr.strip())
(HERE / "verify.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))

# ---- board ----
union = np.zeros(app["s"].shape[:2], bool)
for d in sets.values():
    for v in VIEWS:
        union |= d[v][..., 3] > 0
ys, xs = np.nonzero(union)
box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
K, BG = 4, (0x5A, 0x60, 0x58)
GS = 1.55  # game size: 1.55 screen px per texel at 1280 x 720 (rhino 3d_test screen_sizes; same texel size)
cw, ch = (box[2] - box[0]) * K + 12, (box[3] - box[1]) * K + 30
gcw, gh = round((box[2] - box[0]) * GS) + 8, round((box[3] - box[1]) * GS) + 16
LBL = 150
W = max(LBL + 5 * cw + 10, LBL + 10 * gcw + 60)
H = 70 + 2 * (ch + 8) + 10 + gh + 40
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 10), "Gorilla (ape_l take A): approved (drawn low) vs the 35 degree redraw (cam35), fleet pilot",
        font=fb, fill=(235, 235, 230))
dr.text((12, 38), "4x with sel-out (review only) on the map grey. Same 160 canvas, lowest foot on row 130, the 15 colours. "
        "Numbers: W x H, and H over the approved H.", font=f, fill=(165, 170, 165))


def cell(arr, k):
    im = Image.fromarray(selout_rhino.selout(arr)[0]).crop(box)
    return im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)


for r, (lab, d) in enumerate(sets.items()):
    y = 70 + r * (ch + 8)
    dr.text((12, y + 8), lab, font=fb, fill=(235, 235, 230))
    for i, v in enumerate(VIEWS):
        x = LBL + i * cw
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        im = cell(d[v], K)
        board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + 6))
        w, h = size(d[v])
        dr.text((x + 6, y + 4), v, font=fb, fill=(235, 235, 230))
        dr.text((x + 6, y + ch - 22), f"{w}x{h}  H/approved {h / size(app[v])[1]:.2f}", font=f, fill=(235, 235, 230))
y = 70 + 2 * (ch + 8) + 10
dr.text((12, y + 4), "Game size,\n1.55 px per\ntexel", font=f, fill=(235, 235, 230))
dr.rectangle([LBL, y, W - 10, y + gh], fill=BG)
x = LBL + 8
for d in sets.values():
    for v in VIEWS:
        im = cell(d[v], GS)
        board.alpha_composite(im, (x, y + 8))
        x += gcw
    x += 24
dr.text((12, H - 28), "Game size row: approved five, then cam35 five. Files: views_cam35/. views/ unchanged.",
        font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "board_cam35.png")
print("board", board.size)
