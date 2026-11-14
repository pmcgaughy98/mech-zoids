"""Walk audit: one line per creature for the walk problems Preston named (Claude, 2026-10-28).

Preston: "tallow root paddles forward like its using them to walk ... some creatures unnecessarily move limbs or the
waterbug skimmer thing still has water around its leg. Sparkwick and some other creatures point northeast when going
north or vice versa. some look like they are floating and shadow isnt correct".

Measured on each creature's dungeon set, from the Retro Diffusion frames (the walk_lock backup when there is one):
  boil     share of the body's pixels that change colour from one frame to the next (the shimmer)
  limbs    share of the upper body (above the leg band) that moves after the bob is taken out; arms and paddles
  stray    share of walk pixels whose colour is far from every colour of the still (water, sparks, smears)
  facing   facings whose walk fits another facing's still better than its own, and a north view that is turned
           (much less even left to right than the south view, or nearly the same as a diagonal)
  shadow   how far the feet's middle sits from the sprite's middle, where the shadow is drawn (px)
  ground   how far the walk's planted row sits from the still's foot row (px; the creature drops or rises
           when it starts walking)

  python tools/art/walk_audit.py [name ...] [--md=docs/creatures/walk-lock-2026-10-28/AUDIT.md]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ART = Path("assets/sprites/arena")
BEFORE = Path("docs/creatures/walk-lock-2026-10-28/before")
FACINGS = ["s", "se", "e", "ne", "n", "nw", "w", "sw"]


def load(p):
    return np.array(Image.open(p).convert("RGBA"))


def walk(name, fc):
    k = BEFORE / name / "dungeon"
    base = k if (k / f"walk_{fc}_f0.png").exists() else ART / name / "dungeon"
    return [load(base / f"walk_{fc}_f{i}.png") for i in range(8)]


def foot_row(a, need=4):
    """The game's foot row (dungeon.gd _count_foot_row): the lowest row with four or more solid pixels."""
    for y in range(a.shape[0] - 1, -1, -1):
        if (a[y, :, 3] > 0).sum() >= need:
            return y
    return a.shape[0] - 1


def planted(frames):
    rows = sorted(foot_row(f) for f in frames)
    med = rows[len(rows) // 2]
    return max(r for r in rows if r <= med + 4)


def feet_mid(a):
    y = foot_row(a)
    xs = np.where(a[max(0, y - 1): y + 1, :, 3].any(0))[0]
    return (xs.min() + xs.max()) / 2 if len(xs) else a.shape[1] / 2


def anchored(m, a):
    """Alpha moved so the feet's middle and foot row sit at a fixed point (for comparing shapes)."""
    h, w = m.shape
    out = np.zeros((h * 2, w * 2), bool)
    dy, dx = h - foot_row(a), int(round(w - feet_mid(a)))
    ys, xs = np.nonzero(m)
    out[np.clip(ys + dy, 0, 2 * h - 1), np.clip(xs + dx, 0, 2 * w - 1)] = True
    return out


def iou(p, q):
    return (p & q).sum() / max(1, (p | q).sum())


def boil(frames):
    r = []
    for i, a in enumerate(frames):
        b = frames[(i + 1) % 8]
        both = (a[..., 3] > 0) & (b[..., 3] > 0)
        r.append(((np.abs(a[..., :3].astype(int) - b[..., :3]).sum(-1) > 30) & both).sum() / max(1, both.sum()))
    return float(np.mean(r))


def audit(name):
    stills = {fc: load(ART / name / "dungeon" / f"{fc}.png") for fc in FACINGS}
    walks = {fc: walk(name, fc) for fc in FACINGS}
    row = {"boil": np.mean([boil(walks[fc]) for fc in FACINGS])}
    limbs, stray, shadow, ground, turned = [], [], [], [], []
    for fc in FACINGS:
        st, fr = stills[fc], walks[fc]
        sa = st[..., 3] > 0
        rows = np.where(sa.any(1))[0]
        hip = rows.max() - int(round(0.3 * (rows.max() - rows.min() + 1)))
        up = sa.copy()
        up[hip:] = False
        moved = []
        for f in fr:
            fa = f[..., 3] > 0
            best = min(((up ^ np.roll(np.roll(fa, -dy, 0), -dx, 1)) & up).sum() for dy in range(-2, 3) for dx in range(-2, 3))
            moved.append(best / max(1, up.sum()))
        limbs.append(np.mean(moved))
        pal = np.unique(st[sa][:, :3].astype(int), axis=0)
        far = []
        for f in fr:
            px = f[f[..., 3] > 0][:, :3].astype(int)
            d = np.sqrt(((px[:, None] - pal[None]) ** 2).sum(-1)).min(1)
            far.append((d > 60).mean())
        stray.append(np.mean(far))
        shadow.append(abs(feet_mid(st) - st.shape[1] / 2))
        ground.append(planted(fr) - foot_row(st))
        own = iou(anchored(fr[0][..., 3] > 0, fr[0]), anchored(sa, st))
        for other in FACINGS:
            if other == fc:
                continue
            o = stills[other]
            if iou(anchored(fr[0][..., 3] > 0, fr[0]), anchored(o[..., 3] > 0, o)) > own + 0.05:
                turned.append(f"{fc} walk looks {other}")
                break

    def even(a):
        m = anchored(a[..., 3] > 0, a)
        return iou(m, m[:, ::-1])

    n, s = stills["n"], stills["s"]
    if even(n) < even(s) - 0.12:
        turned.append(f"n still turned (even {even(n):.2f} vs s {even(s):.2f})")
    for d in ("ne", "nw"):
        if iou(anchored(n[..., 3] > 0, n), anchored(stills[d][..., 3] > 0, stills[d])) > 0.85:
            turned.append(f"n still close to {d}")
    row.update(limbs=max(limbs), stray=max(stray), shadow=max(shadow), ground=max(ground, key=abs), facing=turned,
               size=stills["s"].shape[0])
    return row


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(
        p.name for p in ART.iterdir() if (p / "dungeon" / "walk_s_f0.png").exists())
    md = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--md=")), None)
    lines = ["| creature | px | boil | limbs | stray | shadow off | ground | facing |", "|---|---|---|---|---|---|---|---|"]
    for name in names:
        r = audit(name)
        lines.append(f"| {name} | {r['size']} | {r['boil']:.2f} | {r['limbs']:.2f} | {r['stray']:.3f} | {r['shadow']:.1f} | "
                     f"{r['ground']:+d} | {'; '.join(r['facing']) or 'ok'} |")
        print(lines[-1], flush=True)
    if md:
        Path(md).parent.mkdir(parents=True, exist_ok=True)
        Path(md).write_text("# Walk audit, 2026-10-28\n\nMade by tools/art/walk_audit.py; definitions in its docstring.\n\n"
                            + "\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
