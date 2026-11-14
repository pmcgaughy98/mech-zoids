"""Sheet judge: pass or fail a creature's eight views and name the views to redo (Claude, 2026-10-28).

Preston, 2026-10-28: make the eight-angle views consistent, with code doing the corrections and Codex's image
generation doing the drawing. The GitHub pipelines that hold eight views together (PerfectPixel Studio, Sprite8,
PixelArt 8-Dir Studio; read for structure only, nothing copied) share one idea this project lacked: an automatic
judge that names the views that drifted, so only those are generated again. This is that judge, built on
measure_views.py. The skill that drives it is .codex/skills/hollowtide-sprites/SKILL.md.

Checks, per view against the set (thresholds in LIMITS):
  files     all eight views, one canvas size
  alpha     no partial alpha (the game's sprites are 0 or 255)
  ground    every view stands on the same foot row
  centre    each view sits on the canvas's middle column
  height    no view much taller or shorter than the others
  palette   the view's colours come from the main view's colours (drift)
  specks    few lone pixels
  mirror    e/w, ne/nw, se/sw are flips of each other (skipped with --asymmetric)
  face      the north view is not the south view again. Whether a back diagonal (ne, nw) shows the face is checked
            by eye: a colour test (face colours = the south view's head minus the north view) was tried on 2026-10-28
            and failed both ways, missing the agile line's Stage III (its eye colours are on its back too) and calling
            Tallowroot's good back views 11 times the face. A wrong check is worse than none.
  turned    the north view is about as even left to right as the south view, and is not a diagonal

The verdict splits in two. FIX: faults code corrects without drawing (alpha, ground, centre, and mirror pairs on a
creature that is the same on both sides). REDO: views only a new generation mends (height, palette, specks, face,
turned, and mirror pairs on a one-sided creature, --asymmetric).

  python tools/art/sheet_judge.py <folder> [--main s] [--asymmetric] [--json out.json]
  python tools/art/sheet_judge.py <folder> --fix <out_dir> [--mirror-from east|west]
  python tools/art/sheet_judge.py --all [--set dungeon]        one line per creature in assets/sprites/arena

--fix never repaints (Preston, 2026-10-13: the raw Nano Banana output beat our finishing). It sets alpha to 0 or
255, moves each view so it stands on the shared foot row and the middle column, and with --mirror-from replaces the
other side's three views with flips of this side's. Exit code 0 when every check passes, 1 otherwise.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from measure_views import DIRS, MIRROR, box, iou  # noqa: E402

ART = Path("assets/sprites/arena")
LIMITS = {
    "partial_alpha": 0.01,   # share of visible pixels with alpha between 0 and 255
    "ground_px": 1,          # foot row spread allowed
    "centre_frac": 0.05,     # of the canvas width
    "height_frac": 0.10,     # of the median height (at least height_min_px)
    "height_min_px": 2,
    "palette_share": 0.85,   # share of a view's pixels near a main-view colour
    "palette_dist": 40.0,    # RGB distance that counts as near
    "specks": 6,             # lone pixels allowed
    "mirror_iou": 0.85,
    "n_same": 0.60,          # share of pixels the north view shares, colour for colour, with the south view
    "north_even": 0.80,      # north's left-right evenness as a share of south's
    "north_diag_iou": 0.93,  # north against a back diagonal, silhouettes aligned
}


def load_views(folder):
    views = {}
    for d in DIRS:
        p = Path(folder) / (d + ".png")
        if p.exists():
            views[d] = np.asarray(Image.open(p).convert("RGBA")).copy()
    return views


def feet_row(mask, need=3):
    """The lowest row with at least `need` pixels, so a stray pixel or a tail tip doesn't set the ground."""
    counts = mask.sum(1)
    rows = np.where(counts >= need)[0]
    return int(rows.max()) if len(rows) else -1


def shift(a, dy, dx):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    src_y, dst_y = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    src_x, dst_x = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[dst_y, dst_x] = a[src_y, src_x]
    return out


def placement(views):
    """The shared foot row (the median) and each view's move onto it and onto the middle column."""
    feet = {d: feet_row(im[:, :, 3] > 127) for d, im in views.items()}
    target = int(np.median(list(feet.values())))
    moves = {}
    for d, im in views.items():
        b = box(im[:, :, 3] > 127)
        cx = (b[0] + b[2]) / 2.0
        moves[d] = (target - feet[d], int(round(im.shape[1] / 2.0 - cx)))
    return feet, target, moves


def colours(im):
    vis = im[:, :, 3] > 127
    cols, counts = np.unique(im[vis][:, :3], axis=0, return_counts=True)
    return cols.astype(float), counts


def near_share(im, palette):
    cols, counts = colours(im)
    if len(cols) == 0:
        return 0.0
    dist = np.sqrt(((cols[:, None, :] - palette[None, :, :]) ** 2).sum(2)).min(1)
    return float(counts[dist <= LIMITS["palette_dist"]].sum()) / float(counts.sum())


def specks(mask):
    p = np.pad(mask, 1)
    nb = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    return int((mask & (nb == 0)).sum())


def evenness(mask):
    b = box(mask)
    if b is None:
        return 0.0
    m = mask[b[1]:b[3], b[0]:b[2]]
    return iou(m, np.fliplr(m))


def same_share(a, b):
    """Share of the pixels visible in either view that are the same colour at the same place."""
    va, vb = a[:, :, 3] > 127, b[:, :, 3] > 127
    both = va & vb
    same = both & np.all(a[:, :, :3] == b[:, :, :3], axis=2)
    return float(same.sum()) / max(1.0, float((va | vb).sum()))


def judge(folder, main="s", asymmetric=False):
    views = load_views(folder)
    fails = {d: [] for d in DIRS}
    notes = {}
    missing = [d for d in DIRS if d not in views]
    for d in missing:
        fails[d].append("files: missing")
    sizes = {im.shape[:2] for im in views.values()}
    if len(sizes) > 1:
        for d in views:
            fails[d].append("files: canvases differ %s" % sorted(sizes))
    if len(views) < 2 or len(sizes) > 1:
        return {"folder": str(folder), "fails": fails, "notes": notes, "fix": [], "mirror_from": None,
                "redo": [d for d in DIRS if fails[d]]}
    feet, target, moves = placement(views)
    al = {d: shift(im, *moves[d]) for d, im in views.items()}
    masks = {d: im[:, :, 3] > 127 for d, im in al.items()}
    heights = {d: int(box(m)[3] - box(m)[1]) for d, m in masks.items()}
    med_h = float(np.median(list(heights.values())))
    h_tol = max(LIMITS["height_min_px"], LIMITS["height_frac"] * med_h)
    palette = colours(views[main])[0] if main in views else colours(next(iter(views.values())))[0]
    for d, im in views.items():
        a = im[:, :, 3]
        vis = a > 0
        partial = float(((a > 0) & (a < 255)).sum()) / max(1.0, float(vis.sum()))
        if partial > LIMITS["partial_alpha"]:
            fails[d].append("alpha: %.0f%% partial" % (partial * 100))
        if abs(feet[d] - target) > LIMITS["ground_px"]:
            fails[d].append("ground: feet on row %d, the set on %d" % (feet[d], target))
        if abs(moves[d][1]) > LIMITS["centre_frac"] * im.shape[1]:
            fails[d].append("centre: %+d px off the middle" % -moves[d][1])
        if abs(heights[d] - med_h) > h_tol:
            fails[d].append("height: %d px, the set's median %d" % (heights[d], med_h))
        share = near_share(im, palette)
        if d != main and share < LIMITS["palette_share"]:
            fails[d].append("palette: %.0f%% near the %s view's colours" % (share * 100, main))
        sp = specks(masks[d])
        if sp > LIMITS["specks"]:
            fails[d].append("specks: %d lone pixels" % sp)
        notes[d] = {"h": heights[d], "feet": feet[d], "palette": round(share, 3), "colours": int(len(colours(im)[0]))}
    if not asymmetric:
        for a, b in MIRROR.items():
            if a in masks and b in masks:
                m = iou(masks[a], np.fliplr(masks[b]))
                notes["mirror %s/%s" % (a, b)] = round(m, 3)
                if m < LIMITS["mirror_iou"]:
                    # redo the side that is further from the set (more other faults, then height further off)
                    worse = sorted([a, b], key=lambda v: (-len(fails[v]), -abs(heights[v] - med_h)))[0]
                    fails[worse].append("mirror: %.2f against %s flipped" % (m, b if worse == a else a))
    if "n" in al and "s" in al:
        s = same_share(al["n"], al["s"])
        notes["same n/s"] = round(s, 3)
        if s > LIMITS["n_same"]:
            fails["n"].append("face: %.0f%% the same as the south view" % (s * 100))
    if "n" in masks and "s" in masks:
        ev_n, ev_s = evenness(masks["n"]), evenness(masks["s"])
        notes["even n/s"] = [round(ev_n, 3), round(ev_s, 3)]
        if ev_s > 0 and ev_n / ev_s < LIMITS["north_even"]:
            fails["n"].append("turned: %.2f as even as the south view" % (ev_n / ev_s))
        for diag in ["ne", "nw"]:
            if diag in masks:
                m = iou(masks["n"], masks[diag])
                if m > LIMITS["north_diag_iou"]:
                    fails["n"].append("turned: %.2f the same shape as %s" % (m, diag))
    return verdict(folder, fails, notes, heights, med_h, asymmetric)


FIXABLE = {"alpha", "ground", "centre"}
EAST, WEST = ["e", "ne", "se"], ["w", "nw", "sw"]


def verdict(folder, fails, notes, heights, med_h, asymmetric):
    """Split the faults: FIX (code corrects them) and REDO (a new generation). A symmetric creature's mirror
    fault is fixed by flipping its better side; that side has fewer faults that need drawing, then heights nearer
    the set's median."""
    fixable = FIXABLE | (set() if asymmetric else {"mirror"})
    kind = lambda f: f.split(":")[0]  # noqa: E731
    redo = [d for d in DIRS if any(kind(f) not in fixable for f in fails[d])]
    fix_views = [d for d in DIRS if any(kind(f) in fixable for f in fails[d])]
    mirror_from = None
    if not asymmetric and any(kind(f) == "mirror" for d in DIRS for f in fails[d]):
        cost = lambda side: (sum(1 for d in side for f in fails[d] if kind(f) not in fixable),  # noqa: E731
                             sum(abs(heights.get(d, med_h) - med_h) for d in side))
        mirror_from = "east" if cost(EAST) <= cost(WEST) else "west"
        # the flipped side is replaced, so its own drawing faults go with it
        gone = WEST if mirror_from == "east" else EAST
        redo = [d for d in redo if d not in gone]
    return {"folder": str(folder), "fails": fails, "notes": notes, "fix": fix_views, "mirror_from": mirror_from,
            "redo": redo}


def fix(folder, out, mirror_from=None):
    views = load_views(folder)
    feet, target, moves = placement(views)
    fixed = {}
    for d, im in views.items():
        im = im.copy()
        im[:, :, 3] = np.where(im[:, :, 3] > 127, 255, 0)
        im[im[:, :, 3] == 0] = 0
        fixed[d] = shift(im, *moves[d])
    if mirror_from:
        pairs = MIRROR.items() if mirror_from == "east" else [(b, a) for a, b in MIRROR.items()]
        for keep, flip in pairs:
            if keep in fixed:
                fixed[flip] = np.ascontiguousarray(np.fliplr(fixed[keep]))
    Path(out).mkdir(parents=True, exist_ok=True)
    for d, im in fixed.items():
        Image.fromarray(im, "RGBA").save(Path(out) / (d + ".png"))
    print("fixed %d views into %s (alpha 0/255, feet on row %d, centred%s)" % (len(fixed), out, target,
          ", %s side mirrored" % mirror_from if mirror_from else ""))


def report(r):
    print("sheet judge: %s" % r["folder"])
    for d in DIRS:
        n = r["notes"].get(d, {})
        line = "  %-3s h %3s feet %3s palette %5s colours %3s  " % (d, n.get("h", "-"), n.get("feet", "-"),
                                                                    n.get("palette", "-"), n.get("colours", "-"))
        print(line + ("ok" if not r["fails"][d] else "; ".join(r["fails"][d])))
    pairs = {k: v for k, v in r["notes"].items() if k not in DIRS}
    if pairs:
        print("  " + "  ".join("%s %s" % (k, v) for k, v in pairs.items()))
    print("  FIX (code, --fix): %s%s" % (", ".join(r["fix"]) or "nothing",
          "; --mirror-from %s if the creature is the same on both sides" % r["mirror_from"] if r["mirror_from"] else ""))
    print("  REDO (generate again): %s" % (", ".join(r["redo"]) or "nothing"))


def main():
    args = sys.argv[1:]
    opt = lambda k, default=None: args[args.index(k) + 1] if k in args else default  # noqa: E731
    if "--all" in args:
        sub = opt("--set", "")
        bad = 0
        for c in sorted(p for p in ART.iterdir() if p.is_dir() and (p / sub / "s.png").exists()):
            r = judge(c / sub, asymmetric="--asymmetric" in args)
            bad += bool(r["redo"])
            kinds = sorted({f.split(":")[0] for d in r["redo"] for f in r["fails"][d]})
            print("%-12s redo %-20s %-24s fix %s%s" % (c.name, ",".join(r["redo"]) or "-", " ".join(kinds),
                  ",".join(r["fix"]) or "-", " (mirror %s)" % r["mirror_from"] if r["mirror_from"] else ""))
        print("%d sets need views generated again" % bad)
        return 0
    folder = args[0]
    if "--fix" in args:
        fix(folder, opt("--fix"), opt("--mirror-from"))
        folder = opt("--fix")
    r = judge(folder, opt("--main", "s"), "--asymmetric" in args)
    report(r)
    if "--json" in args:
        Path(opt("--json")).write_text(json.dumps(r, indent=1))
    return 1 if r["redo"] else 0


if __name__ == "__main__":
    sys.exit(main())
