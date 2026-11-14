"""Fix pass on a finished Codex rhino set (Claude, 2026-11-03, eyes reworked 2026-11-04).

1. Eyes: finishing loses most of the red eyes because the shrink blends them away, but they are still in Codex's
   full-size sheet_raw.png. v2 (2026-11-04, after Preston: "some of the frames the red eye dot is not where it
   should be"): each raw eye is mapped through the exact finishing transform, the row's shrink factor plus the
   frame's offset found by matching the shrunk raw silhouette to the frame's alpha, so the approved eye pattern
   (from the cleaned ground-pound frame 0: front = glint + 2 red per eye, side = 5 red + 1 glint) lands with its
   red centre on Codex's red centre. Only an eye Codex did not draw red falls back to a guess: a template match
   of the approved eye's neighbourhood, then following the head from the nearest frame that has the eye. Eye
   pixels only go where all 8 neighbours are opaque. Back views get none; NO_EYES frames keep none.
2. Swaps: SWAP frames are replaced by approved frames (the Codex frame is kept as *_codex.png).
3. Ground: GROUND frames are moved down so the lowest pixel sits on y=160.
Reads from frames_codex/ every time, so rerunning is safe. Writes FIXES.txt and eye-moves.png (old | new) per set.
Usage: python fix_set.py <set dir> <sheet> [<sheet> ...]
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ANIM = Path(__file__).parent
R, G = (0xFF, 0x3A, 0x2A), (0xFF, 0xE6, 0xD8)
GP = ANIM / "codex-ground-pound/clean/frames"
SWAP = {("horn-toss", "front", 4): GP / "front_f1.png", ("horn-toss", "back", 4): GP / "back_f1.png"}
NO_EYES = {("death", "front", 5), ("death", "front", 6), ("death", "side", 5), ("death", "side", 6)}
GROUND = {("stampede", "side", 5)}
# Preston's picks: frames whose eyes are copied as saved (recover_eyes.py), never placed by this script
_OV = ANIM / "eye_overrides.json"
OVERRIDES = json.loads(_OV.read_text()) if _OV.exists() else {}
# row shrink factors (front, side, back) from the Codex reports; sheets not listed use the frame/raw width ratio
FACTORS = {"idle": (0.2768, 0.3589, 0.2623), "walk": (0.3431, 0.4221, 0.3274), "horn-jab": (0.3163, 0.3931, 0.2994),
           "horn-toss": (0.3457, 0.4204, 0.3207), "brace": (0.2976650457, 0.35395189, 0.2770629764),
           "stampede": (0.3481553119, 0.405511811, 0.3273544427), "death": (0.3314461889, 0.3992248062, 0.3164769605)}
N8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
HW, HH = 12, 9


def is_eye(a):
    return (a[..., 3] > 0) & (np.all(a[..., :3] == R, -1) | np.all(a[..., :3] == G, -1))


def bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return xs.min(), ys.min(), xs.max(), ys.max()


def templates(view):
    a = np.asarray(Image.open(GP / f"{view}_f0.png").convert("RGBA"))
    m = is_eye(a)
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        cx, cy = int(round(xs.mean())), int(round(ys.mean()))
        pat = [(x - cx, y - cy, tuple(int(v) for v in a[y, x, :3])) for y, x in zip(ys, xs)]
        reds = [(dx, dy) for dx, dy, col in pat if col == R]
        win = a[cy - HH:cy + HH + 1, cx - HW:cx + HW + 1]
        care = (win[..., 3] > 0) & ~m[cy - HH:cy + HH + 1, cx - HW:cx + HW + 1]
        out.append(dict(c=(cx, cy), pat=pat, red=(np.mean([p[0] for p in reds]), np.mean([p[1] for p in reds])),
                        win=win, care=care))
    return sorted(out, key=lambda t: t["c"][0]), bbox(a)


TPL = {v: templates(v) for v in ("front", "side")}


def exact_eyes(raw, grid, sheet, r, c, n, a):
    """Codex's red eye centres in frame coordinates, through the finishing shrink and the frame's offset."""
    H, W = raw.shape[:2]
    xe = grid.get("x_edges") or [W * i // n for i in range(n + 1)]
    ye = grid.get("y_edges") or [H * i // 3 for i in range(4)]
    if sheet not in FACTORS and isinstance(grid.get("y"), list) and isinstance(grid.get("x"), list):
        # Sets C and D (2026-11-04) record the true cut edges as x (one list per row) and y. Used only for sheets
        # outside FACTORS, so the approved sets A and B keep the eyes Preston signed off.
        xe = grid["x"][r] if isinstance(grid["x"][0], list) else grid["x"]
        ye = grid["y"]
    cell = raw[ye[r]:ye[r + 1], xe[c]:xe[c + 1]].astype(int)
    mag = (cell[..., 0] > 170) & (cell[..., 1] < 110) & (cell[..., 2] > 170)
    lab, k = ndi.label(~mag)
    sizes = ndi.sum(np.ones(lab.shape), lab, range(1, k + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.02 * sizes.max()])
    ys, xs = np.where(keep)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    fb = bbox(a)
    f = FACTORS[sheet][r] if sheet in FACTORS else (fb[2] - fb[0] + 1) / (x1 - x0)
    sw, sh = max(1, round((x1 - x0) * f)), max(1, round((y1 - y0) * f))
    small = np.asarray(Image.fromarray(keep[y0:y1, x0:x1].astype(np.uint8) * 255).resize(
        (sw, sh), Image.Resampling.BOX)) >= 128
    fa = a[..., 3] > 0
    gx, gy = fb[0] + ((fb[2] - fb[0] + 1) - sw) // 2, fb[3] + 1 - sh
    best = (-1, gx, gy)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            X, Y = gx + dx, gy + dy
            if X < 0 or Y < 0 or X + sw > fa.shape[1] or Y + sh > fa.shape[0]:
                continue
            win = fa[Y:Y + sh, X:X + sw]
            best = max(best, ((win & small).sum() / (win | small).sum(), X, Y))
    iou, X, Y = best
    red = (cell[..., 0] > 190) & (cell[..., 1] < 110) & (cell[..., 2] < 110) & ~ndi.binary_dilation(mag, iterations=3)
    lab2, k2 = ndi.label(red)
    pts = []
    for i in range(1, k2 + 1):
        yy, xx = np.where(lab2 == i)
        if len(xx) >= 6:
            pts.append((X + (xx.mean() - x0 + 0.5) * sw / (x1 - x0) - 0.5,
                        Y + (yy.mean() - y0 + 0.5) * sh / (y1 - y0) - 0.5, len(xx)))
    return sorted(pts, key=lambda p: -p[2]), iou


def score(a, t, x, y):
    t_ = a[y - HH:y + HH + 1, x - HW:x + HW + 1]
    if t_.shape != t["win"].shape:
        return -1
    return ((t_[..., 3] > 0) & np.all(t_[..., :3] == t["win"][..., :3], -1) & t["care"]).sum() / t["care"].sum()


def stamp(a, pat, x, y):
    done = 0
    for dx, dy, col in pat:
        px, py = x + dx, y + dy
        if a[py, px, 3] and all(a[py + j, px + i, 3] for i, j in N8):
            a[py, px, :3] = col
            done += 1
    return done


def place_eyes(a, view, pts):
    tpls, gb = TPL[view]
    fb = bbox(a)
    sx, sy = (fb[2] - fb[0]) / (gb[2] - gb[0]), (fb[3] - fb[1]) / (gb[3] - gb[1])
    est = [(fb[0] + (t["c"][0] - gb[0]) * sx, fb[1] + (t["c"][1] - gb[1]) * sy) for t in tpls]
    # give each of Codex's eyes to the nearest approved eye (front: left and right), at most one each
    owner = {}
    for px, py, _ in pts[:len(tpls)]:
        d = sorted((np.hypot(px - ex, py - ey), k) for k, (ex, ey) in enumerate(est) if k not in owner)
        if d and d[0][0] <= 16:
            owner[d[0][1]] = (px, py)
    notes, placed = [], {}
    for k, t in enumerate(tpls):
        if k in owner:
            px, py = owner[k]
            x, y = int(round(px - t["red"][0])), int(round(py - t["red"][1]))
            placed[k] = (x, y)
            notes.append(f"eye {k} at {x},{y} (Codex's eye, {stamp(a, t['pat'], x, y)}/{len(t['pat'])} px)")
            continue
        ex, ey = est[k]
        best = (-9, 0, 0)
        for y in range(int(ey) - 8, int(ey) + 9):
            for x in range(int(ex) - 8, int(ex) + 9):
                if any(abs(x - ux) < 8 and abs(y - uy) < 6 for ux, uy in placed.values()):
                    continue
                best = max(best, (score(a, t, x, y) - 0.004 * np.hypot(x - ex, y - ey), x, y))
        s, x, y = best
        if s < 0.40:
            notes.append(f"eye {k} left for tracking (template best {s:.2f})")
            continue
        placed[k] = (x, y)
        notes.append(f"eye {k} GUESS at {x},{y} (no red in Codex's art; template {s:.2f}, "
                     f"{stamp(a, t['pat'], x, y)}/{len(t['pat'])} px)")
    return "; ".join(notes), placed


def track(a, ref, view, k, rx, ry):
    """Find eye k in frame a by matching the whole head around it in a neighbouring frame that has it."""
    win = ref[ry - 20:ry + 21, rx - 25:rx + 26]
    care = (win[..., 3] > 0) & ~is_eye(win)
    best = (-1, 0, 0)
    for dy in range(-14, 15):
        for dx in range(-14, 15):
            t_ = a[ry + dy - 20:ry + dy + 21, rx + dx - 25:rx + dx + 26]
            if t_.shape != win.shape:
                continue
            s = ((t_[..., 3] > 0) & np.all(t_[..., :3] == win[..., :3], -1) & care).sum() / care.sum()
            best = max(best, (s - 0.003 * np.hypot(dx, dy), dx, dy))
    s, dx, dy = best
    if s < 0.25:
        return f"eye {k} MISSING (no red in Codex's art, head not tracked, best {s:.2f})"
    x, y = rx + dx, ry + dy
    pat = TPL[view][0][k]["pat"]
    return f"eye {k} GUESS tracked to {x},{y} (no red in Codex's art; head match {s:.2f}, {stamp(a, pat, x, y)}/{len(pat)} px)"


def clear_eyes(a):
    m = is_eye(a)
    for y, x in zip(*np.where(m)):
        votes = {}
        for dx, dy in N8:
            p = tuple(int(v) for v in a[y + dy, x + dx, :3])
            if a[y + dy, x + dx, 3] and p not in (R, G):
                votes[p] = votes.get(p, 0) + 1
        if votes:
            a[y, x, :3] = max(votes, key=votes.get)
    return int(m.sum())


def red_centres(a):
    m = (a[..., 3] > 0) & np.all(a[..., :3] == R, -1)
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    return [tuple(np.mean(np.where(lab == i)[::-1], axis=1)) for i in range(1, n + 1)]


def main():
    sdir = Path(sys.argv[1])
    log, moves = [], []
    for sheet in sys.argv[2:]:
        d = sdir / sheet
        frames, backup = d / "frames", d / "frames_codex"
        if not backup.exists():
            shutil.copytree(frames, backup)
        raw = np.asarray(Image.open(d / "sheet_raw.png").convert("RGB"))
        grid = json.loads((d / "grid.json").read_text()) if (d / "grid.json").exists() else {}
        n = len(list(backup.glob("front_f*.png")))
        for r, view in enumerate(("front", "side", "back")):
            arrs, notes, placed, olds = [], [], [], []
            for c in range(n):
                key = (sheet, view, c)
                old_p = frames / f"{view}_f{c}.png"
                olds.append(np.asarray(Image.open(old_p).convert("RGBA")) if old_p.exists() else None)
                a = np.asarray(Image.open(backup / f"{view}_f{c}.png").convert("RGBA")).copy()
                note = f"cleared {clear_eyes(a)}"
                if key in GROUND:
                    drop = 160 - bbox(a)[3]
                    a = np.roll(a, drop, axis=0)
                    note += f"; moved down {drop} px"
                got = {}
                ok = f"{sheet}/{view}/{c}"
                if ok in OVERRIDES:
                    for x, y, hexc in OVERRIDES[ok]:
                        a[y, x, :3] = [int(hexc[i:i + 2], 16) for i in (0, 2, 4)]
                    got = {k: None for k in range(len(TPL[view][0]))}
                    note += f"; eyes as Preston picked ({len(OVERRIDES[ok])} px from eye_overrides.json)"
                elif view != "back" and key not in NO_EYES:
                    pts, iou = exact_eyes(raw, grid, sheet, r, c, n, a)
                    txt, got = place_eyes(a, view, pts)
                    note += f"; raw fit {iou:.2f}; " + txt
                arrs.append(a)
                notes.append(note)
                placed.append(got)
            if view != "back":
                for c in range(n):
                    if (sheet, view, c) in NO_EYES:
                        continue
                    for k in range(len(TPL[view][0])):
                        if k not in placed[c]:
                            donors = sorted((abs(c2 - c), c2) for c2 in range(n) if placed[c2].get(k) is not None)
                            if donors:
                                c2 = donors[0][1]
                                notes[c] += f"; from f{c2}: " + track(arrs[c], arrs[c2], view, k, *placed[c2][k])
            for c in range(n):
                key, a, note = (sheet, view, c), arrs[c], notes[c]
                if key in SWAP:
                    shutil.copyfile(SWAP[key], frames / f"{view}_f{c}.png")
                    Image.fromarray(a).save(frames / f"{view}_f{c}_codex.png")
                    note = f"swapped for ground-pound {SWAP[key].name}"
                else:
                    if view != "back" and olds[c] is not None:
                        old, new = red_centres(olds[c]), red_centres(a)
                        far = max([min([np.hypot(nx - ox, ny - oy) for ox, oy in old] or [99]) for nx, ny in new] or [0])
                        if len(old) != len(new) or far >= 1.5:
                            note += f"; MOVED from last version ({len(old)}->{len(new)} eyes, up to {far:.1f} px)"
                            moves.append((f"{sheet} {view}_f{c}", olds[c], a.copy(), new))
                    Image.fromarray(a).save(frames / f"{view}_f{c}.png")
                log.append(f"{sheet} {view}_f{c}: {note}")
    (sdir / "FIXES.txt").write_text("\n".join(log) + "\n", encoding="utf8")
    print("\n".join(log))

    # what moved: last version | this version, head at 4x, one row per frame
    if moves:
        tile_w, tile_h = 48 * 4, 30 * 4
        board = Image.new("RGBA", (2 * tile_w + 220, len(moves) * (tile_h + 4)), (0x3D, 0x43, 0x50, 255))
        dr = ImageDraw.Draw(board)
        for j, (label, old, new, cen) in enumerate(moves):
            cx, cy = (int(np.mean([p[0] for p in cen])), int(np.mean([p[1] for p in cen]))) if cen else (110, 120)
            for i, im in enumerate((old, new)):
                crop = Image.fromarray(im).crop((cx - 24, cy - 15, cx + 24, cy + 15)).resize((tile_w, tile_h), Image.NEAREST)
                board.alpha_composite(crop, (220 + i * tile_w, j * (tile_h + 4)))
            dr.text((4, j * (tile_h + 4) + 4), label + "\nleft: last version\nright: now", fill=(235, 235, 240, 255))
        board.save(sdir / "eye-moves.png")


if __name__ == "__main__":
    main()
