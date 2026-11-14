"""Capped detail ink trials (sprite factory lane, Claude, 2026-11-04). Preston: "Build all five".

Same rule as hippo_l/take-b/remaster-pilot/capped_ink.py, which Preston kept for the hippo:
  - gate: only views under 0.75 x target (target = the lower of se and e);
  - candidates: the interior pixels the rhino walk's contour rule (rhino_l/take-a/anim/detail_ink.py) would ink;
  - order: strongest contrast first, +0.5 for touching existing ink;
  - stop: when the view reaches the target. Ink colour: the machine's own darkest.
Read-only on the approved stills (fixed/ if present, else views/). For each machine it writes
<machine>/<take>/remaster-pilot/{views_capped_trial, views_capped_trial_selout, board.png, metrics.json, RUN.md}
and refuses to run if that remaster-pilot folder already exists. Then one overview of every gated view:
CAPPED_INK_BOARD_2026-11-04.png in this folder.
Run: python capped_ink_trial.py wolf_m:take-b fennec_s:take-b ...
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "rhino_l" / "take-a" / "anim"))
from detail_ink import darkest, ink, interior_ink  # noqa: E402
from selout_rhino import selout  # noqa: E402

VIEWS = ["s", "se", "e", "ne", "n"]
W_LUMA = np.array([0.299, 0.587, 0.114]) / 255
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
K, BG, PAGE = 4, (0x5A, 0x60, 0x58), (34, 37, 41, 255)
TXT, DIM = (235, 235, 230), (165, 170, 165)
FB = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 20)
F = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 16)
FS = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 14)


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


def magenta(o_sel, c_sel):
    diff = np.any(o_sel != c_sel, -1)
    g = c_sel.copy()
    lum = (g[..., :3].astype(int) @ [77, 150, 29] >> 8).astype(np.uint8)
    g[..., :3] = (lum[..., None] * 0.45 + 60).astype(np.uint8)
    g[diff, :3] = (255, 40, 220)
    g[diff, 3] = 255
    return g, int(diff.sum())


def put(board, im, x, y, cw, ch, k=K):
    im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    board.alpha_composite(im, (x + (cw - 8 - im.width) // 2, y + (ch - im.height) // 2))


def machine_board(tr, path):
    res, mv, boxes, target = tr["res"], tr["metrics"]["views"], tr["box"], tr["metrics"]["target"]
    cws = {v: (boxes[v][2] - boxes[v][0]) * K + 16 for v in VIEWS}
    ch = max(b[3] - b[1] for b in boxes.values()) * K + 16
    lbl = 230
    rows = ["His original (approved)", "In game today\n(original + sel-out)", "Capped trial\n(+ sel-out)",
            "Full rule, for comparison\n(+ sel-out; the look\nturned down on the gorilla)",
            "Capped: changed pixels\n(magenta)", "Game size, about 2x\nleft today, right capped"]
    W, H = lbl + sum(cws.values()) + 10, 70 + len(rows) * (ch + 8) + 34
    board = Image.new("RGBA", (W, H), PAGE)
    dr = ImageDraw.Draw(board)
    dr.text((12, 12), f"{tr['name']}: capped detail ink, only up to the side views' level ({target * 100:.1f}%).",
            font=FB, fill=TXT)
    dr.text((12, 40), f"Read from {tr['src']}/. Ink in its own darkest colour. 4x on the map grey. Only the views with a "
            "share under the row-3 label change.", font=F, fill=DIM)
    for r, lab in enumerate(rows):
        y = 70 + r * (ch + 8)
        dr.text((12, y + 8), lab, font=F, fill=TXT)
        x = lbl
        for v in VIEWS:
            cw, bx, m = cws[v], boxes[v], mv[v]
            o_raw, o_sel, c_sel, f_sel = res[v]
            dr.rectangle([x, y, x + cw - 8, y + ch], fill=BG)
            if r < 4:
                put(board, Image.fromarray([o_raw, o_sel, c_sel, f_sel][r]).crop(bx), x, y, cw, ch)
                if r == 0:
                    dr.text((x + 6, y + 4), f"{v}  {m['share_before'] * 100:.1f}%", font=FB, fill=TXT)
                if r == 2 and m["gated"]:
                    dr.text((x + 6, y + ch - 22), f"{m['share_before'] * 100:.1f} -> {m['share_capped'] * 100:.1f}%, "
                            f"+{m['added']} px", font=FS, fill=TXT)
                if r == 3 and m["gated"]:
                    dr.text((x + 6, y + ch - 22), f"-> {m['share_full_rule'] * 100:.1f}%, +{m['full_rule_px']} px",
                            font=FS, fill=TXT)
            elif r == 4:
                g, n = magenta(o_sel, c_sel)
                put(board, Image.fromarray(g).crop(bx), x, y, cw, ch)
                dr.text((x + 6, y + ch - 22), f"{n} px", font=FS, fill=TXT)
            else:
                for k, src in enumerate((o_sel, c_sel)):
                    im = Image.fromarray(src).crop(bx)
                    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
                    board.alpha_composite(im, (x + 4 + k * ((cw - 8) // 2), y + (ch - im.height) // 2))
            x += cw
    dr.text((12, H - 28), f"Approved {tr['src']}/ untouched. Trial stills: remaster-pilot/views_capped_trial/.",
            font=F, fill=DIM)
    board.convert("RGB").save(path)


def trial(c, t):
    take = ROOT / c / t
    src = "fixed" if (take / "fixed").is_dir() else "views"
    out = take / "remaster-pilot"
    if out.exists():
        raise SystemExit(f"{out} already exists; not overwriting it")
    orig = {v: np.asarray(Image.open(take / src / f"{v}.png").convert("RGBA")) for v in VIEWS}
    share = {v: interior_ink(orig[v]) for v in VIEWS}
    target = min(share["se"], share["e"])
    metrics = {"src": src, "target": round(target, 4), "views": {}}
    res, box = {}, {}
    for d in ("views_capped_trial", "views_capped_trial_selout"):
        (out / d).mkdir(parents=True)
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
        Image.fromarray(cap).save(out / "views_capped_trial" / f"{v}.png")
        cap_sel = selout(cap)[0]
        Image.fromarray(cap_sel).save(out / "views_capped_trial_selout" / f"{v}.png")
        o_sel = selout(a)[0]
        res[v] = (a, o_sel, cap_sel, selout(full)[0])
        ys, xs = np.nonzero(o_sel[..., 3] > 0)
        box[v] = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
        metrics["views"][v] = m
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    tr = {"c": c, "t": t, "name": c.rsplit("_", 1)[0].capitalize(), "src": src, "metrics": metrics, "res": res,
          "box": box}
    machine_board(tr, out / "board.png")
    rows = []
    for v in VIEWS:
        m = metrics["views"][v]
        if m["gated"]:
            rows.append(f"| {v} | {m['share_before'] * 100:.1f}% | {m['share_capped'] * 100:.1f}% | {m['added']} of "
                        f"{m['candidates']} candidates | {m['share_full_rule'] * 100:.1f}%, +{m['full_rule_px']} px |")
        else:
            rows.append(f"| {v} | {m['share_before'] * 100:.1f}% | not gated | 0 | not gated |")
    lone = sum(metrics["views"][v].get("lone", 0) for v in VIEWS)
    (out / "RUN.md").write_text(f"""# {tr['name']} capped-ink trial (sprite factory lane, 2026-11-04)

Preston: "Build all five". Still-only trial: the approved `../{src}` were never written.
- Rule: the one Preston kept for the hippo (`hippo_l/take-b/remaster-pilot/RUN.md`).
- Script: `docs/art/moba/capped_ink_trial.py`. Board: `board.png`. Numbers: `metrics.json`.
- Overview of all five: `docs/art/moba/CAPPED_INK_BOARD_2026-11-04.png`.

| View | Before | Capped | Pixels added | Full rule, for comparison |
|---|---|---|---|---|
""" + "\n".join(rows) + f"""

- Target (the lower of se and e): {target * 100:.1f}%.
- Added pixels with no inked neighbour: {lone}.
- `views_capped_trial/` holds the trial stills; `views_capped_trial_selout/` shows them as the game would.
- Neither folder is packer-ready. `../{src}` stays as drawn until Preston rules.
- The by-eye review is in `docs/art/moba/STILLS_STOCKTAKE_2026-11-04.md`, "Capped ink, five more".
""", encoding="utf-8")
    return tr


def overview(trials, path):
    rows = []
    for tr in trials:
        mv, res, box = tr["metrics"]["views"], tr["res"], tr["box"]
        cells = [("e (side) today", res["e"][1], box["e"])]
        for v in VIEWS:
            m = mv[v]
            if m["gated"]:
                o_sel, c_sel = res[v][1], res[v][2]
                g, _ = magenta(o_sel, c_sel)
                cells += [(f"{v} today {m['share_before'] * 100:.1f}%", o_sel, box[v]),
                          (f"{v} capped {m['share_capped'] * 100:.1f}%  +{m['added']}", c_sel, box[v]),
                          (f"{v} changed", g, box[v])]
        rows.append((tr, cells))
    lbl = 190
    cw = lambda b: (b[2] - b[0]) * K + 16
    rh = [max(b[3] - b[1] for _, _, b in cells) * K + 44 for _, cells in rows]
    W = lbl + max(sum(cw(b) for _, _, b in cells) for _, cells in rows) + 10
    H = 76 + sum(h + 10 for h in rh) + 30
    board = Image.new("RGBA", (W, H), PAGE)
    dr = ImageDraw.Draw(board)
    dr.text((12, 12), "Capped detail ink, five more machines: only the views that change, next to the side view.",
            font=FB, fill=TXT)
    dr.text((12, 42), "All with sel-out, as the game adds it. 4x on the map grey. Magenta = changed pixels. "
            "Approved stills untouched.", font=F, fill=DIM)
    y = 76
    for (tr, cells), h in zip(rows, rh):
        dr.text((12, y + 8), tr["name"], font=FB, fill=TXT)
        dr.text((12, y + 34), f"target {tr['metrics']['target'] * 100:.1f}%\nfrom {tr['src']}/", font=F, fill=DIM)
        x = lbl
        for lab, im, b in cells:
            w = cw(b)
            dr.rectangle([x, y, x + w - 8, y + h], fill=BG)
            crop = Image.fromarray(im).crop(b)
            crop = crop.resize((crop.width * K, crop.height * K), Image.NEAREST)
            board.alpha_composite(crop, (x + (w - 8 - crop.width) // 2, y + 30 + (h - 30 - crop.height) // 2))
            dr.text((x + 6, y + 6), lab, font=FS, fill=TXT)
            x += w
        y += h + 10
    board.convert("RGB").save(path)


if __name__ == "__main__":
    trials = [trial(*arg.split(":")) for arg in sys.argv[1:]]
    for tr in trials:
        mv = tr["metrics"]["views"]
        print(tr["name"], tr["src"], "target", tr["metrics"]["target"],
              {v: (mv[v]["share_before"], mv[v].get("share_capped"), mv[v].get("added"), mv[v].get("lone"),
                   mv[v].get("full_rule_px")) for v in VIEWS if mv[v]["gated"]})
    overview(trials, ROOT / "CAPPED_INK_BOARD_2026-11-04.png")
    print("overview written")
