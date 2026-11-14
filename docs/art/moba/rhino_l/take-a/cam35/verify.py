"""Independent re-measure of the cam35 views (rhino camera-angle lane, Claude, 2026-11-04).

Recomputes from the PNGs, not from Codex's reports: size, height over the 35 degree guide, width over the guide,
role shares (accent = the seam colour), eye pixels, palette, border contact and the lowest row. Writes verify.txt.
Usage: python verify.py [views_dir]   (default ../views_cam35; also prints ../views and ../views_cam30 for reference)
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TAKE = HERE.parent
VIEWS = ["s", "se", "e", "ne", "n"]
GUIDE = {"s": (72, 108), "se": (89, 100), "e": (103, 90), "ne": (89, 100), "n": (72, 108)}
pal = json.loads((TAKE / "palette.json").read_text())
role = {tuple(int(p["hex"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)): p["role"] for p in pal}
ROLES = ["yellow", "steel", "charcoal", "eye", "accent"]


def measure(d):
    out = {}
    for v in VIEWS:
        a = np.asarray(Image.open(d / f"{v}.png").convert("RGBA"))
        op = a[..., 3] > 0
        ys, xs = np.nonzero(op)
        w, h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        cols = [tuple(c) for c in a[op][:, :3]]
        bad = sorted({c for c in cols if c not in role})
        n = len(cols)
        share = {r: sum(1 for c in cols if role.get(c) == r) / n for r in ROLES}
        border = bool(op[0].any() or op[-1].any() or op[:, 0].any() or op[:, -1].any())
        alpha = sorted(set(np.unique(a[..., 3]).tolist()))
        out[v] = dict(w=int(w), h=int(h), hr=h / GUIDE[v][1], wr=w / GUIDE[v][0], share=share,
                      eye=sum(1 for c in cols if role.get(c) == "eye"), bad=bad, border=border,
                      low=int(ys.max()), alpha=alpha, canvas=a.shape[:2])
    return out


lines = []
for tag, d in (("approved", TAKE / "views"), ("cam30", TAKE / "views_cam30"),
               ("cam35", Path(sys.argv[1]) if len(sys.argv) > 1 else TAKE / "views_cam35")):
    m = measure(d)
    lines.append(f"== {tag} ({d})")
    for v in VIEWS:
        r = m[v]
        ok = "PASS" if 0.85 <= r["hr"] <= 1.08 else "MISS"
        lines.append(f"{v}: {r['w']}x{r['h']}  H/guide {r['hr']:.3f} {ok}  W/guide {r['wr']:.3f}  "
                     + " ".join(f"{k} {100 * r['share'][k]:.1f}%" for k in ROLES)
                     + f"  eye px {r['eye']}  lowest row {r['low']}  border {r['border']}  canvas {r['canvas']}"
                     + f"  alpha {r['alpha']}" + (f"  OFF-PALETTE {r['bad']}" if r["bad"] else ""))
    hr = [m[v]["hr"] for v in VIEWS]
    sp = max(hr) - min(hr)
    lines.append(f"height-ratio spread {sp:.3f} {'PASS' if sp <= 0.08 else 'MISS'}; se width {m['se']['w']} "
                 f"{'PASS' if m['se']['w'] >= 84 else 'MISS'} (target 89)")
txt = "\n".join(lines)
print(txt)
(HERE / "verify.txt").write_text(txt + "\n")
