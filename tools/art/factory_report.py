# Factory report (Claude, 2026-10-12): every installed view of every machine measured against the Legacy bands
# (docs/reference/sprite-rules-legacy-2026-10-12.md), one table, out-of-band values starred.
#   python tools/art/factory_report.py [machine_id ...]   (default: every art/machines/*/views)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite_quality import measure

BANDS = {"colours": (27, 54), "cluster": (3.3, 4.5), "stray": (0.11, 0.16), "light": (49, 107),
         "highlight": (0.03, 0.24), "outline": (0.09, 0.23)}
VIEWS = ("e", "se", "s", "sw", "w", "nw", "n", "ne")
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art", "machines")
ids = sys.argv[1:] or sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d, "views")))
print("| machine | view | colours | cluster | stray | light | highlight | near-black |")
print("|---|---|---|---|---|---|---|---|")
summary = {}
for m in ids:
    out = 0
    for v in VIEWS:
        p = os.path.join(root, m, "views", v + ".png")
        if not os.path.exists(p):
            continue
        r = measure(p)
        cells = []
        for k in ("colours", "cluster", "stray", "light", "highlight", "outline"):
            lo, hi = BANDS[k]
            ok = lo <= r[k] <= hi
            out += not ok
            txt = ("%d" % r[k]) if k == "colours" else ("%.1f" % r[k]) if k == "cluster" else ("%+.0f" % r[k]) if k == "light" else ("%.0f%%" % (100 * r[k]))
            cells.append(txt if ok else "**%s**" % txt)
        print("| %s | %s | %s |" % (m, v, " | ".join(cells)))
    summary[m] = out
print()
print("Out-of-band values per machine (of 48): " + ", ".join("%s %d" % kv for kv in summary.items()))
