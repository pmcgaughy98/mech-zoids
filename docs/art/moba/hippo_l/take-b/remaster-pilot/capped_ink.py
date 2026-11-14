"""Capped detail ink trial on the hippo's approved stills (sprite factory lane, Claude, 2026-11-04).

Preston: "Try the hippo". Read-only on ../views. The rhino walk's contour rule overshoots: wherever it fires, a view
lands at 1.5 to 2.8 times its target (STILLS_STOCKTAKE_2026-11-04.md, "Ink measure"). This trial caps it:
  - gate: a view is inked only when its interior ink share is under 0.75 x target (target = the lower of se and e);
  - candidates: the interior pixels the contour rule would ink;
  - order: strongest contrast first, with a bonus for touching existing ink, so new ink extends lines instead of
    adding dots;
  - stop: as soon as the view's share reaches the target.
Ink colour is the hippo's own darkest (detail_ink.darkest). Sel-out is added for review only; the packer adds it in game.
Writes views_capped_trial/, views_capped_trial_selout/, board.png and metrics.json here, never ../views.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
TAKE = HERE.parent
sys.path.insert(0, str(TAKE.parents[1] / "rhino_l" / "take-a" / "anim"))
from detail_ink import darkest, ink, interior_ink  # noqa: E402
from selout_rhino import selout  # noqa: E402

VIEWS = ["s", "se", "e", "ne", "n"]
W_LUMA = np.array([0.299, 0.587, 0.114]) / 255
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def shift(m, dy, dx):
    """out[y, x] = m[y + dy, x + dx], zero outside the canvas."""
    p = np.pad(m, ((1, 1), (1, 1)) + ((0, 0),) * (m.ndim - 2))
    return p[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]]


def interior(a):
    op = a[..., 3] > 0
    inner = op.copy()
    for dy, dx in N4:
        inner &= shift(op, dy, dx)
    return inner


def touches(is_ink, y, x):
    h, w = is_ink.shape
    return any(0 <= y + dy < h and 0 <= x + dx < w and is_ink[y + dy, x + dx] for dy, dx in N8)


def capped(a, target):
    dark = darkest(a)
    full = ink(a)[0]
    inner = interior(a)
    cand = np.any(full != a, -1) & inner
    lum = a[..., :3].astype(float) @ W_LUMA
    contrast = np.max([shift(lum, dy, dx) for dy, dx in N4], 0) - lum
    is_ink = np.all(a[..., :3] == dark, -1) & (a[..., 3] > 0)
    need = int(np.ceil(target * inner.sum() - (is_ink & inner).sum()))
    out = a.copy()
    left = sorted(zip(*map(lambda z: z.tolist(), np.nonzero(cand))))
    n_cand = len(left)
    added = []
    while len(added) < need and left:
        best = max(left, key=lambda p: contrast[p] + (0.5 if touches(is_ink, *p) else 0.0))
        left.remove(best)
        out[best[0], best[1], :3] = dark
        is_ink[best] = True
        added.append(best)
    lone = sum(1 for p in added if not touches(is_ink, *p))
    return out, full, {"need": need, "added": len(added), "candidates": n_cand, "lone": lone}


orig = {v: np.asarray(Image.open(TAKE / "views" / f"{v}.png").convert("RGBA")) for v in VIEWS}
share = {v: interior_ink(orig[v]) for v in VIEWS}
target = min(share["se"], share["e"])
metrics = {"target": round(target, 4), "views": {}}
res = {}
for d in ("views_capped_trial", "views_capped_trial_selout"):
    (HERE / d).mkdir(exist_ok=True)
for v in VIEWS:
    a = orig[v]
    m = {"share_before": round(share[v], 4), "gated": v not in ("se", "e") and share[v] < 0.75 * target}
    cap, full = a, a
    if m["gated"]:
        cap, full, info = capped(a, target)
        m.update(info)
        m["share_capped"] = round(interior_ink(cap), 4)
        m["share_full_rule"] = round(interior_ink(full), 4)
        m["full_rule_px"] = int(np.any(full != a, -1).sum())
    Image.fromarray(cap).save(HERE / "views_capped_trial" / f"{v}.png")
    cap_sel = selout(cap)[0]
    Image.fromarray(cap_sel).save(HERE / "views_capped_trial_selout" / f"{v}.png")
    res[v] = (a, selout(a)[0], cap_sel, selout(full)[0])
    metrics["views"][v] = m
(HERE / "metrics.json").write_text(json.dumps(metrics, indent=1))

# Board: his original | in game today | capped trial | full rule | changed pixels | game size
K, BG = 4, (0x5A, 0x60, 0x58)
boxes = {}
for v in VIEWS:
    ys, xs = np.nonzero(res[v][1][..., 3] > 0)
    boxes[v] = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
cws = {v: (boxes[v][2] - boxes[v][0]) * K + 16 for v in VIEWS}
ch = max((b[3] - b[1]) for b in boxes.values()) * K + 16
LBL = 230
rows = ["His original (approved)", "In game today\n(original + sel-out)", "Capped trial\n(+ sel-out)",
        "Full rule, for comparison\n(+ sel-out; the look\nturned down on the gorilla)", "Capped: changed pixels\n(magenta)",
        "Game size, about 2x\nleft today, right capped"]
W, H = LBL + sum(cws.values()) + 10, 70 + len(rows) * (ch + 8) + 34
board = Image.new("RGBA", (W, H), (34, 37, 41, 255))
dr = ImageDraw.Draw(board)
fb = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
f = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
dr.text((12, 12), f"Hippo: capped detail ink. Back views get ink only up to the side views' level ({target * 100:.1f}%).",
        font=fb, fill=(235, 235, 230))
dr.text((12, 40), "Same palette, ink in the hippo's own darkest colour. Shown at 4x on the map grey. s, se and e are not "
        "changed.", font=f, fill=(165, 170, 165))


def put(im, x, y, cw, k=K):
    im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + (ch - im.height) // 2))


for r, lab in enumerate(rows):
    y = 70 + r * (ch + 8)
    dr.text((12, y + 8), lab, font=f, fill=(235, 235, 230))
    x = LBL
    for v in VIEWS:
        cw, bx, m = cws[v], boxes[v], metrics["views"][v]
        o_raw, o_sel, c_sel, f_sel = res[v]
        dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
        if r < 4:
            put(Image.fromarray([o_raw, o_sel, c_sel, f_sel][r]).crop(bx), x, y, cw)
            if r == 0:
                dr.text((x + 6, y + 4), f"{v}  {m['share_before'] * 100:.1f}%", font=fb, fill=(235, 235, 230))
            if r == 2 and m["gated"]:
                dr.text((x + 6, y + ch - 24), f"{m['share_before'] * 100:.1f} -> {m['share_capped'] * 100:.1f}%, "
                        f"+{m['added']} px", font=f, fill=(235, 235, 230))
            if r == 3 and m["gated"]:
                dr.text((x + 6, y + ch - 24), f"{m['share_before'] * 100:.1f} -> {m['share_full_rule'] * 100:.1f}%, "
                        f"+{m['full_rule_px']} px", font=f, fill=(235, 235, 230))
        elif r == 4:
            diff = np.any(o_sel != c_sel, -1)
            g = c_sel.copy()
            lum = (g[..., :3].astype(int) @ [77, 150, 29] >> 8).astype(np.uint8)
            g[..., :3] = (lum[..., None] * 0.45 + 60).astype(np.uint8)
            g[diff, :3] = (255, 40, 220)
            g[diff, 3] = 255
            put(Image.fromarray(g).crop(bx), x, y, cw)
            dr.text((x + 6, y + ch - 24), f"{int(diff.sum())} px", font=f, fill=(235, 235, 230))
        else:
            for k, src in enumerate((o_sel, c_sel)):
                im = Image.fromarray(src).crop(bx)
                im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
                board.alpha_composite(im, (x + 4 + k * ((cw - 8) // 2), y + (ch - im.height) // 2))
        x += cw
dr.text((12, H - 28), "Approved ../views untouched. Trial stills: views_capped_trial/ (with sel-out: "
        "views_capped_trial_selout/).", font=f, fill=(165, 170, 165))
board.convert("RGB").save(HERE / "board.png")
print(json.dumps(metrics, indent=1))
print("board", board.size)
