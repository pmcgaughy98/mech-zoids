"""Remaster pilot on the gorilla's five approved stills (sprite factory lane, Claude, 2026-11-04).

Preston: "Start the gorilla test". Still-only pass, the approved views in ../views are never written.
  1. Detail ink: the rhino walk's `contour` rule (rhino_l/take-a/anim/detail_ink.py, imported, not copied), gated the
     same way: only views whose interior ink share is under the lower of se and e get it.
  2. Palette lock: every pixel snapped to the approved palette (the 15 colours of the five views) plus the roster
     outline #141218.
  3. Sel-out (rhino_l/take-a/anim/selout_rhino.py) only for review: views_ink_trial/ holds the trial stills (the packer
     adds sel-out), views_ink_trial_selout/ shows them as the game would.
Writes views_ink_trial/, views_ink_trial_selout/, board.png and metrics.json here, never ../views.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
TAKE = HERE.parent
sys.path.insert(0, str(TAKE.parents[1] / "rhino_l" / "take-a" / "anim"))
from detail_ink import OUTLINE, ink  # noqa: E402
from detail_ink import interior_ink as interior_ink_rhino  # noqa: E402
from selout_rhino import selout  # noqa: E402

VIEWS = ["s", "se", "e", "ne", "n"]
orig = {v: np.asarray(Image.open(TAKE / "views" / f"{v}.png").convert("RGBA")) for v in VIEWS}
PAL = np.array(sorted({tuple(p) for v in VIEWS for p in orig[v][orig[v][..., 3] > 0][:, :3]} | {tuple(OUTLINE)}), int)


def lock(a):
    out = a.copy()
    op = out[..., 3] > 0
    rgb = out[op][:, :3].astype(int)
    d = ((rgb[:, None, :] - PAL[None]) ** 2).sum(-1)
    px = out[op]
    px[:, :3] = PAL[d.argmin(1)].astype(np.uint8)
    out[op] = px
    return out, int((d.min(1) > 0).sum())


_own = PAL[~np.all(PAL == OUTLINE, 1)]
DARK = _own[np.argmin(_own @ np.array([299, 587, 114]))].astype(np.uint8)  # the gorilla's own darkest colour


def ink_share(a):
    """detail_ink.interior_ink counts only #141218, the rhino's darkest; the gorilla's ink colour is its own darkest."""
    b = a.copy()
    b[np.all(a[..., :3] == DARK, -1), :3] = OUTLINE
    return interior_ink_rhino(b)


def ink_own(a):
    out, _ = ink(a)
    hit = np.all(out[..., :3] == OUTLINE, -1) & ~np.all(a[..., :3] == OUTLINE, -1)
    out[hit, :3] = DARK
    return out, int((hit & ~np.all(a[..., :3] == DARK, -1)).sum())


interior_ink = ink_share
share = {v: interior_ink(orig[v]) for v in VIEWS}
target = min(share["se"], share["e"])
print("palette:", [("#%02x%02x%02x" % tuple(p)) for p in PAL], "ink colour", "#%02x%02x%02x" % tuple(DARK))
res, metrics = {}, {"palette": len(PAL), "target_share": round(target, 4), "views": {}}
for d in ("views_ink_trial", "views_ink_trial_selout"):
    (HERE / d).mkdir(exist_ok=True)
for v in VIEWS:
    a = orig[v]
    inked = 0
    if v not in ("se", "e") and share[v] < target:
        a, inked = ink_own(a)
    a, snapped = lock(a)
    b, added, darkened = selout(a)
    b, snapped2 = lock(b)
    o, _, _ = selout(orig[v])
    o, _ = lock(o)
    Image.fromarray(a).save(HERE / "views_ink_trial" / f"{v}.png")
    Image.fromarray(b).save(HERE / "views_ink_trial_selout" / f"{v}.png")
    res[v] = (orig[v], o, b)
    metrics["views"][v] = {"ink_share_before": round(share[v], 4), "ink_share_after": round(interior_ink(a), 4),
                           "ink_px": inked, "snapped_px": snapped + snapped2, "selout_px": added,
                           "dark_edge_px": darkened, "foot_row_selout": int(np.nonzero(b[..., 3] > 0)[0].max())}
(HERE / "metrics.json").write_text(json.dumps(metrics, indent=1))

# board: his original | in game today (original + sel-out) | in game after (remaster + sel-out) | changed | 2x
K, BG = 4, (0x5A, 0x60, 0x58)
boxes = {}
for v in VIEWS:
    ys, xs = np.nonzero(res[v][2][..., 3] > 0)
    boxes[v] = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
cw = max((b[2] - b[0]) for b in boxes.values()) * K + 16
ch = max((b[3] - b[1]) for b in boxes.values()) * K + 16
LBL = 210
rows = ["His original (approved)", "In game today\n(original + sel-out)", "In game after\n(remaster + sel-out)",
        "Changed pixels\n(magenta)", "Game size, about 2x\nleft today, right after"]
W, H = LBL + 5 * cw + 10, 64 + len(rows) * (ch + 8) + 30
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 12), "Gorilla remaster pilot: detail ink on the flat views, palette locked, sel-out as the game adds it",
        font=fb, fill=(235, 235, 230))
dr.text((12, 38), "Same pixels, same palette (15 colours + outline #141218). Shown at 4x on the map grey.", font=f,
        fill=(165, 170, 165))
for r, lab in enumerate(rows):
    y = 64 + r * (ch + 8)
    dr.text((12, y + 8), lab, font=f, fill=(235, 235, 230))
    for c, v in enumerate(VIEWS):
        x = LBL + c * cw
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        if r == 0:
            dr.text((x + 6, y + 4), v, font=fb, fill=(235, 235, 230))
        bx = boxes[v]
        o_raw, o_sel, b_sel = res[v]
        if r < 3:
            im = Image.fromarray([o_raw, o_sel, b_sel][r]).crop(bx)
            im = im.resize((im.width * K, im.height * K), Image.NEAREST)
            board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + (ch - im.height) // 2))
        elif r == 3:
            diff = np.any(o_sel != b_sel, -1)
            g = b_sel.copy()
            lum = (g[..., :3].astype(int) @ [77, 150, 29] >> 8).astype(np.uint8)
            g[..., :3] = (lum[..., None] * 0.45 + 60).astype(np.uint8)
            g[diff, :3] = (255, 40, 220)
            g[diff, 3] = 255
            im = Image.fromarray(g).crop(bx)
            im = im.resize((im.width * K, im.height * K), Image.NEAREST)
            board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + (ch - im.height) // 2))
            dr.text((x + 6, y + ch - 22), f"{int(diff.sum())} px", font=f, fill=(235, 235, 230))
        else:
            for k, src in enumerate((o_sel, b_sel)):
                im = Image.fromarray(src).crop(bx)
                im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
                board.alpha_composite(im, (x + 10 + k * ((cw - 8) // 2), y + (ch - im.height) // 2))
dr.text((12, H - 26), "Approved ../views untouched. Ink trial: views_ink_trial/ (ne, n inked), with sel-out: views_ink_trial_selout/.",
        font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "board.png")
print(json.dumps(metrics, indent=1))
print("board", board.size)
