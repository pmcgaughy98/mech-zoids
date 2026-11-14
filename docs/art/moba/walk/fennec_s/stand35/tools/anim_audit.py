"""Animation audit: every frame of every creature, not only the walks (Claude, 2026-10-31; Preston: "fix all
animations, poses, etc."). walk_audit.py reads walks only, and its facing flags trip on lopsided creatures, so this
one scores a frame against all eight stills with a margin and reads attack, hurt and sleep as well.

For one set (dungeon by default), per creature, per action, per facing:
  facing   the still this action's frames fit best, when that is not its own still and the lead is over MARGIN.
           Only the body above the leg band is scored, so a stride does not read as a turn.
  flip     how the same action on the mirror facing scores on this still after a flip: a flagged facing with a
           good mirror partner can be repaired for free by flipping the partner.
  clip     frames with solid pixels on the canvas edge (the art is cut off)
  empty    frames with next to nothing drawn
  frozen   an action whose frames are all the same picture
  pop      the biggest jump in solid-pixel count between neighbouring frames, as a share of the still; a frame that
           swells or shrinks reads as a flash
  soft     frames with partial alpha (the game's sprites are 0 or 255)

  python tools/art/anim_audit.py [name ...] [--set=dungeon] [--json=out.json]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ART = Path("assets/sprites/arena")
FACINGS = ["s", "se", "e", "ne", "n", "nw", "w", "sw"]
MIRROR = {"s": "s", "n": "n", "e": "w", "w": "e", "se": "sw", "sw": "se", "ne": "nw", "nw": "ne"}
ACTIONS = {"walk": 8, "attack": 6, "hurt": 6, "sleep": 4}
MARGIN = 0.07     # a lead smaller than this is two views that look alike, not a wrong facing
BODY_SHARE = 0.68  # the top share of the sprite that counts as body


def load(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(np.int16)
    return a


def box(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def body(a):
    """The upper body, centred on its own middle column, on a fixed square of cells."""
    b = box(a)
    if b is None:
        return None
    x0, y0, x1, y1 = b
    cut = y0 + max(2, int((y1 - y0 + 1) * BODY_SHARE))
    part = a[y0:cut, x0:x1 + 1]
    return part


def fit(a, b):
    """How well two body cuts overlap: matching colour on shared cells over the union, tried at small offsets."""
    best = 0.0
    ha, wa = a.shape[:2]
    hb, wb = b.shape[:2]
    h, w = max(ha, hb) + 8, max(wa, wb) + 8
    pa = np.zeros((h, w, 4), np.int16)
    oy, ox = 4 + (h - 8 - ha) // 2, 4 + (w - 8 - wa) // 2
    pa[oy:oy + ha, ox:ox + wa] = a
    sa = pa[..., 3] > 0
    for dy in range(-2, 3):
        for dx in range(-4, 5):
            pb = np.zeros((h, w, 4), np.int16)
            y = 4 + (h - 8 - hb) // 2 + dy
            x = 4 + (w - 8 - wb) // 2 + dx
            if y < 0 or x < 0 or y + hb > h or x + wb > w:
                continue
            pb[y:y + hb, x:x + wb] = b
            sb = pb[..., 3] > 0
            both = sa & sb
            union = (sa | sb).sum()
            if union == 0:
                continue
            near = (np.abs(pa[..., :3] - pb[..., :3]).sum(2) < 90) & both
            best = max(best, near.sum() / union)
    return best


def stills(name, set_):
    out = {}
    for f in FACINGS:
        p = ART / name / set_ / (f + ".png")
        if p.exists():
            out[f] = load(p)
    return out


def frames(name, set_, action, facing):
    out = []
    for i in range(ACTIONS[action]):
        p = ART / name / set_ / f"{action}_{facing}_f{i}.png"
        if p.exists():
            out.append(load(p))
    return out


def score(seq, still_bodies, take=4):
    """Mean fit of a sample of the frames against every still's body."""
    picks = seq[:: max(1, len(seq) // take)][:take]
    cuts = [body(a) for a in picks]
    cuts = [c for c in cuts if c is not None]
    if not cuts:
        return {}
    return {f: float(np.mean([fit(c, b) for c in cuts])) for f, b in still_bodies.items()}


def audit(name, set_):
    still = stills(name, set_)
    if len(still) < 8:
        return None
    bodies = {f: body(a) for f, a in still.items()}
    report = {"name": name, "faults": []}
    for action in ACTIONS:
        seqs = {f: frames(name, set_, action, f) for f in FACINGS}
        for f, seq in seqs.items():
            if not seq:
                continue
            h, w = seq[0].shape[:2]
            area = float((still[f][..., 3] > 0).sum()) or 1.0
            areas = [float((a[..., 3] > 0).sum()) for a in seq]
            clip = sum(1 for a in seq if (a[0, :, 3] > 0).any() or (a[-1, :, 3] > 0).any() or (a[:, 0, 3] > 0).any() or (a[:, -1, 3] > 0).any())
            empty = sum(1 for x in areas if x < area * 0.25)
            soft = sum(1 for a in seq if ((a[..., 3] > 0) & (a[..., 3] < 255)).any())
            frozen = len(seq) > 1 and all(np.array_equal(seq[0], a) for a in seq[1:])
            pop = max((abs(areas[i] - areas[i - 1]) / area for i in range(1, len(areas))), default=0.0)
            row = {"action": action, "facing": f, "frames": len(seq), "clip": clip, "empty": empty, "soft": soft,
                   "frozen": bool(frozen), "pop": round(pop, 2)}
            if action in ("walk", "attack"):
                got = score(seq, bodies)
                if got:
                    own = got[f]
                    top = max(got, key=got.get)
                    row["own"] = round(own, 3)
                    if top != f and got[top] - own > MARGIN:
                        row["looks"] = top
                        row["lead"] = round(got[top] - own, 3)
                        partner = seqs.get(MIRROR[f]) or []
                        if partner and MIRROR[f] != f:
                            flipped = [a[:, ::-1] for a in partner]
                            back = score(flipped, {f: bodies[f]})
                            row["flip_fit"] = round(back.get(f, 0.0), 3)
            if clip or empty or soft or frozen or pop > 0.45 or "looks" in row:
                report["faults"].append(row)
    return report


def main():
    set_ = "dungeon"
    out = None
    names = []
    for a in sys.argv[1:]:
        if a.startswith("--set="):
            set_ = a[6:]
        elif a.startswith("--json="):
            out = a[7:]
        else:
            names.append(a)
    if not names:
        names = sorted(p.name for p in ART.iterdir() if (p / set_).is_dir())
    all_reports = []
    totals = {}
    for n in names:
        r = audit(n, set_)
        if r is None:
            print(n, "no full set")
            continue
        all_reports.append(r)
        bits = {}
        for row in r["faults"]:
            key = row["action"]
            d = bits.setdefault(key, {"clip": 0, "empty": 0, "soft": 0, "frozen": 0, "pop": 0, "facing": []})
            d["clip"] += row["clip"]
            d["empty"] += row["empty"]
            d["soft"] += row["soft"]
            d["frozen"] += int(row["frozen"])
            d["pop"] += int(row["pop"] > 0.45)
            if "looks" in row:
                d["facing"].append(f"{row['facing']}>{row['looks']}")
        line = []
        for k, d in bits.items():
            text = [f"{m} {d[m]}" for m in ("clip", "empty", "soft", "frozen", "pop") if d[m]]
            if d["facing"]:
                text.append("facing " + " ".join(d["facing"]))
            line.append(f"{k}: " + ", ".join(text))
            for m in ("clip", "empty", "soft", "frozen", "pop"):
                totals[(k, m)] = totals.get((k, m), 0) + d[m]
            totals[(k, "facing")] = totals.get((k, "facing"), 0) + len(d["facing"])
        print(f"{n:12s} " + ("; ".join(line) if line else "ok"))
    print("\ntotals:")
    for k in ACTIONS:
        print(" ", k, {m: totals.get((k, m), 0) for m in ("clip", "empty", "soft", "frozen", "pop", "facing")})
    if out:
        Path(out).write_text(json.dumps(all_reports, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
