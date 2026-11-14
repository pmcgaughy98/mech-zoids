"""Measure interior ink on every roster machine's approved stills. Read-only: no still is written.

Sprite factory lane, 2026-11-04 (Preston: "Measure them"). Uses the rhino walk's rule from
rhino_l/take-a/anim/detail_ink.py, which counts each view's own darkest colour as ink.
  share   = interior ink share of the view as drawn
  target  = the lower of se and e (the gate the pilot used)
  strict  = share under target (the pilot's gate; on the gorilla it fired on noise)
  tol     = share under 0.75 x target (the tolerance gate RUN.md suggests)
  +px     = ink pixels the contour rule would add to the view, counted in memory only
Run: python measure_ink.py [out.json]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "rhino_l" / "take-a" / "anim"))
from detail_ink import darkest, ink, interior_ink  # noqa: E402

ORDER = [("rhino_l", "take-a"), ("ape_l", "take-a"), ("hippo_l", "take-b"), ("lobster_l", "take-g"),
         ("kangaroo_m", "take-a"), ("pangolin_m", "take-a"), ("wolf_m", "take-b"), ("shoebill_m", "take-e"),
         ("fennec_s", "take-b"), ("falcon_m", "take-b"), ("squirrel_s", "take-b"), ("chameleon_m", "take-b"),
         ("hummingbird_s", "take-a")]
VIEWS = ["s", "se", "e", "ne", "n"]


def load(c, t, v):
    p = ROOT / c / t / "fixed" / f"{v}.png"
    src = "fixed" if p.exists() else "views"
    return np.asarray(Image.open(ROOT / c / t / src / f"{v}.png").convert("RGBA")), src


rows = []
for c, t in ORDER:
    imgs = {v: load(c, t, v) for v in VIEWS}
    share = {v: interior_ink(imgs[v][0]) for v in VIEWS}
    dark = {v: "#%02x%02x%02x" % tuple(darkest(imgs[v][0])) for v in VIEWS}
    target = min(share["se"], share["e"])
    rec = {"machine": c, "take": t, "src": imgs["s"][1], "target": round(target, 4),
           "spread": round(max(share.values()) / max(1e-9, min(share.values())), 2),
           "darkest_differs": len(set(dark.values())) > 1, "views": {}}
    for v in VIEWS:
        a = imgs[v][0]
        r = {"share": round(share[v], 4), "darkest": dark[v],
             "strict": v not in ("se", "e") and share[v] < target,
             "tol": v not in ("se", "e") and share[v] < 0.75 * target}
        if r["strict"]:
            out = ink(a)[0]
            r["px"] = int(np.any(out != a, -1).sum())
            r["share_after"] = round(interior_ink(out), 4)
        rec["views"][v] = r
    rows.append(rec)

if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(json.dumps(rows, indent=1))
print(f"{'machine':15}{'src':7}" + "".join(f"{v:>8}" for v in VIEWS) + f"{'target':>8}{'spread':>8}  flags")
for r in rows:
    V = r["views"]
    cells = "".join(f"{V[v]['share'] * 100:7.1f}{'*' if V[v]['tol'] else ('+' if V[v]['strict'] else ' ')}"
                    for v in VIEWS)
    flags = "; ".join(f"{v} {V[v]['share'] * 100:.1f}->{V[v]['share_after'] * 100:.1f}% (+{V[v]['px']} px)"
                      for v in VIEWS if V[v]["strict"])
    if r["darkest_differs"]:
        flags += " | darkest differs by view: " + ",".join(V[v]["darkest"] for v in VIEWS)
    print(f"{r['machine']:15}{r['src']:7}{cells}{r['target'] * 100:8.1f}{r['spread']:8.2f}  {flags}")
print("* under 0.75 x target (tolerance gate)   + under target only (strict gate)")
