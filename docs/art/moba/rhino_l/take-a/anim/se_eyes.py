"""Red eye for se frames that lost it (Claude, animation lane, 2026-11-04).

Codex's se rows (sets C and D) keep the red eye in most frames but drop it in some. For each se frame with no eye red,
the nearest frame in the same row that has one is the donor: a patch of the donor's head around its eye (eye pixels
masked out) is matched against the target within SEARCH px, and the donor's eye pixels are stamped where it fits, on
interior pixels only (all 8 neighbours opaque, the canon's no-red-on-the-rim rule). Frames listed in NO_EYES are
meant to be dark (death after the light goes out).

    python se_eyes.py            # all sets C and D se rows; writes se-eye-board.png
Originals: <sheet>/frames_pre_eyes/.
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ANIM = Path(__file__).parent
SHEETS = ["codex-set-c/stampede", "codex-set-c/horn-toss", "codex-set-c/ground-pound", "codex-set-c/horn-jab",
          "codex-set-d/brace", "codex-set-d/death"]
NO_EYES = {("death", 4), ("death", 5), ("death", 6)}
RED, GLINT = np.array([0xFF, 0x3A, 0x2A]), np.array([0xFF, 0xE6, 0xD8])
HW, HH, SEARCH, MIN_SCORE = 10, 8, 14, 0.55


def eye_mask(a):
    return (a[..., :3] == RED).all(axis=2) | (a[..., :3] == GLINT).all(axis=2)


def interior(a):
    op = a[..., 3] > 0
    p = np.pad(op, 1)
    return np.logical_and.reduce([p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx]
                                  for dy in (-1, 0, 1) for dx in (-1, 0, 1)])


def fix_row(d, n):
    frames, keep = d / "frames", d / "frames_pre_eyes"
    if not keep.exists():
        shutil.copytree(frames, keep)
    arr = [np.asarray(Image.open(keep / f"se_f{i}.png").convert("RGBA")).copy() for i in range(n)]
    has = [eye_mask(a).any() for a in arr]
    notes, changed = [], []
    for i in range(n):
        if has[i] or (d.name, i) in NO_EYES:
            continue
        donors = sorted((abs(j - i), j) for j in range(n) if has[j])
        if not donors:
            notes.append(f"{d.name} se_f{i}: no donor")
            continue
        j = donors[0][1]
        src = arr[j]
        ys, xs = np.nonzero(eye_mask(src))
        cy, cx = int(round(ys.mean())), int(round(xs.mean()))
        patch = src[cy - HH:cy + HH + 1, cx - HW:cx + HW + 1].astype(int)
        pm = eye_mask(src)[cy - HH:cy + HH + 1, cx - HW:cx + HW + 1]
        tgt = arr[i].astype(int)
        best = (-1.0, 0, 0)
        for dy in range(-SEARCH, SEARCH + 1):
            for dx in range(-SEARCH, SEARCH + 1):
                y0, x0 = cy - HH + dy, cx - HW + dx
                win = tgt[y0:y0 + patch.shape[0], x0:x0 + patch.shape[1]]
                if win.shape != patch.shape:
                    continue
                both = ((patch[..., 3] > 0) | (win[..., 3] > 0)) & ~pm
                score = ((patch == win).all(axis=2) & both).sum() / max(1, both.sum())
                best = max(best, (score, dx, dy))
        score, dx, dy = best
        if score < MIN_SCORE:
            notes.append(f"{d.name} se_f{i}: skipped, best fit {score:.2f} from f{j}")
            continue
        inner = interior(arr[i])
        n_px = 0
        for y, x in zip(ys, xs):
            Y, X = y + dy, x + dx
            if inner[Y, X]:
                arr[i][Y, X, :3] = src[y, x, :3]
                n_px += 1
        Image.fromarray(arr[i]).save(frames / f"se_f{i}.png")
        changed.append((f"{d.name} se_f{i}", np.asarray(Image.open(keep / f"se_f{i}.png").convert("RGBA")), arr[i],
                        (cy + dy, cx + dx)))
        notes.append(f"{d.name} se_f{i}: {n_px} eye px from f{j} at {dx:+d},{dy:+d} (fit {score:.2f})")
    return notes, changed


def main():
    notes, changed = [], []
    for s in SHEETS:
        d = ANIM / s
        n = len(list((d / "frames").glob("se_f*.png")))
        a, b = fix_row(d, n)
        notes += a
        changed += b
    print("\n".join(notes))
    if changed:
        k, tw, th = 5, 40, 26
        board = Image.new("RGBA", (2 * tw * k + 170, len(changed) * (th * k + 4)), (0x80, 0x80, 0x80, 255))
        dr = ImageDraw.Draw(board)
        for r, (lab, old, new, (cy, cx)) in enumerate(changed):
            for c, im in enumerate((old, new)):
                crop = Image.fromarray(im).crop((cx - tw // 2, cy - th // 2, cx + tw // 2, cy + th // 2))
                board.alpha_composite(crop.resize((tw * k, th * k), Image.NEAREST), (170 + c * tw * k, r * (th * k + 4)))
            dr.text((4, r * (th * k + 4) + 4), lab + "\nleft: Codex\nright: eye tracked", fill=(255, 255, 255, 255))
        board.save(ANIM / "se-eye-board.png")
        print("board se-eye-board.png", board.size)


if __name__ == "__main__":
    main()
