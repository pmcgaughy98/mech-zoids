"""Board and checks for one machine's cam35 views (fleet redraw lane, Claude, 2026-11-04).

Usage: python fleet_board.py TAKE_DIR APPROVED_SUBDIR "Title" EYE_HEXES ACCENT_HEX OUTLINE_HEX
Reads TAKE_DIR/APPROVED_SUBDIR and TAKE_DIR/views_cam35 (s, se, e, ne, n) and TAKE_DIR/cam35/palette.json.
Writes TAKE_DIR/cam35/board_cam35.png and verify.txt. Sel-out (the rhino's rule, this machine's darkest colour as the
outline) is added for review only. Approved views are never written.
Checks: size, H over approved H, lowest row, border contact, alpha, off-palette colours, accent share against approved,
eye pixels and groups, and the shape-aware angle by outline and by height over width (hull_guide.py).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rhino_l" / "take-a" / "anim"))
import hull_guide as hg  # noqa: E402
import selout_rhino  # noqa: E402

TAKE, SUB, TITLE, EYES, ACC, OUTL = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
rgb = lambda h: tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
selout_rhino.OUTLINE = np.array(rgb(OUTL), np.uint8)
VIEWS = ["s", "se", "e", "ne", "n"]
OUT = TAKE / "cam35"
palset = {rgb(p["hex"]) for p in json.loads((OUT / "palette.json").read_text())}
eyes = [rgb(h) for h in EYES.split(",")]
load = lambda p: np.asarray(Image.open(p).convert("RGBA")).copy()
app = {v: load(TAKE / SUB / f"{v}.png") for v in VIEWS}
new = {v: load(TAKE / "views_cam35" / f"{v}.png") for v in VIEWS}


def size(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


def stats(a):
    op = a[..., 3] > 0
    acc = np.all(a[..., :3] == rgb(ACC), axis=2)[op].mean() * 100
    g = np.zeros(op.shape, bool)
    for e in eyes:
        g |= np.all(a[..., :3] == e, axis=2)
    g &= op
    lab, n = ndimage.label(g, structure=np.ones((3, 3)))
    comps = sorted((int((lab[sl] == i).sum()), sl[0].start, sl[0].stop - 1, sl[1].start, sl[1].stop - 1)
                   for i, sl in enumerate(ndimage.find_objects(lab), 1))[::-1]
    return acc, int(g.sum()), comps


hull = hg.build_hull(TAKE / SUB)
asp = {v: [] for v in VIEWS}
for p in range(0, 71):
    for v in VIEWS:
        w, h = hg.size(hg.raster(hull, v, p)[0])
        asp[v].append(h / w)
out = []
for v in VIEWS:
    a = new[v]
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    border = ys.min() == 0 or xs.min() == 0 or ys.max() == a.shape[0] - 1 or xs.max() == a.shape[1] - 1
    left = {tuple(c) for c in a[op][:, :3]} - palset
    (w, h), (wa, ha) = size(a), size(app[v])
    acc, eye, comps = stats(a)
    acca, eyea, _ = stats(app[v])
    pitch = int(np.argmin([abs(x - h / w) for x in asp[v]]))
    out.append(f"{v:>2}: {w}x{h} (approved {wa}x{ha}), H/approved {h / ha:.2f}, angle by H/W {pitch} deg; lowest row "
               f"{ys.max()}; border {'TOUCH' if border else 'clear'}; alpha {sorted(set(np.unique(a[..., 3]).tolist()))}; "
               f"off-palette {len(left)}; accent {acc:.1f}% (approved {acca:.1f}%); eye px {eye} (approved {eyea})")
    out.append(f"     eye groups (px, y0, y1, x0, x1): {comps[:5]}")
gain = [size(new[v])[1] / size(app[v])[1] for v in VIEWS]
out.append(f"H/approved spread {max(gain) - min(gain):.2f}")
(OUT / "verify.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))

union = np.zeros(app["s"].shape[:2], bool)
for d in (app, new):
    for v in VIEWS:
        union |= d[v][..., 3] > 0
ys, xs = np.nonzero(union)
box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
K = 4 if app["s"].shape[0] <= 160 else 3
BG, GS = (0x5A, 0x60, 0x58), 1.55
cw, ch = (box[2] - box[0]) * K + 12, (box[3] - box[1]) * K + 30
gcw, gh = round((box[2] - box[0]) * GS) + 8, round((box[3] - box[1]) * GS) + 16
LBL = 150
W = max(LBL + 5 * cw + 10, LBL + 10 * gcw + 60)
H = 70 + 2 * (ch + 8) + 10 + gh + 40
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 10), f"{TITLE}: approved (drawn low) vs the 35 degree redraw (cam35)", font=fb, fill=(235, 235, 230))
dr.text((12, 38), f"{K}x with sel-out (review only) on the map grey. Same canvas and feet row. Numbers: W x H, and H over "
        "the approved H.", font=f, fill=(165, 170, 165))


def cell(arr, k):
    im = Image.fromarray(selout_rhino.selout(arr)[0]).crop(box)
    return im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)


for r, (lab, d) in enumerate((("Approved\n(low camera)", app), ("cam35\n(this run)", new))):
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
for d in (app, new):
    for v in VIEWS:
        im = cell(d[v], GS)
        board.alpha_composite(im, (x, y + 8))
        x += gcw
    x += 24
dr.text((12, H - 28), f"Game size row: approved five, then cam35 five. Files: views_cam35/. {SUB}/ unchanged.",
        font=f, fill=(165, 170, 165))
board.convert("RGB").save(OUT / "board_cam35.png")
print("board", board.size)
