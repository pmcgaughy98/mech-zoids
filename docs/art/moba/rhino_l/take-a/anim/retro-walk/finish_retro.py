"""Finish the Retro Diffusion walk frames into the rhino's format (Claude, 2026-11-04).

Retro kept the design but nudged most colours by one step (FECF1F for FFCF1F and so on), added black and white,
and painted over the red eyes. Per frame:
  1. snap every colour to the nearest rhino colour (eye red and glint excluded, so they only appear as eyes);
  2. put the eyes back: the input frame's eye pixels are carried to where the head is in this frame, found by
     matching a patch around each eye (eye pixels left out of the match) within 6 px;
  2b. ground each frame: its lowest pixel goes back on the input's ground row;
  3. re-run the sel-out pass from selout_rhino.py so any edge Retro left bare gets its outline;
  4. move the frame back into the game's 192 canvas (the same offset the input was cut with), feet near y=160.
Writes frames/{view}_f0..f7.png (192) and frames128/ (Retro size) beside this script.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
ANIM = HERE.parent
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402

GP = ANIM / "codex-ground-pound/clean/frames_selout"
R, G = (0xFF, 0x3A, 0x2A), (0xFF, 0xE6, 0xD8)
PAL = [0x141218, 0x211E27, 0x3D3A44, 0x7A4A06, 0x58555E, 0xD18A0A, 0x9D9BA2, 0xFFCF1F, 0xD6D6DC, 0xFFF4A8]
PAL = np.array([[c >> 16, c >> 8 & 255, c & 255] for c in PAL], np.int32)


def snap(a):
    out = a.copy()
    op = a[..., 3] > 0
    px = a[op][:, :3].astype(np.int32)
    d = ((px[:, None, :] - PAL[None]) ** 2).sum(-1)
    out[op, :3] = PAL[d.argmin(1)]
    out[..., 3] = np.where(op, 255, 0)
    return out


def eye_groups(inp):
    m = np.all(inp[..., :3] == R, -1) | np.all(inp[..., :3] == G, -1)
    ys, xs = np.where(m & (inp[..., 3] > 0))
    groups = []
    for x, y in zip(xs, ys):
        for g in groups:
            if any(abs(x - gx) <= 3 and abs(y - gy) <= 3 for gx, gy, _ in g):
                g.append((x, y, tuple(inp[y, x, :3])))
                break
        else:
            groups.append([(x, y, tuple(inp[y, x, :3]))])
    return groups


def place_eyes(f, inp_snapped, groups):
    moves = []
    for g in groups:
        cx = int(np.mean([p[0] for p in g]))
        cy = int(np.mean([p[1] for p in g]))
        y0, y1, x0, x1 = cy - 8, cy + 8, cx - 12, cx + 12
        tmpl = inp_snapped[y0:y1, x0:x1]
        skip = np.zeros(tmpl.shape[:2], bool)
        for x, y, _ in g:
            skip[y - y0, x - x0] = True
        best = (-1, 0, 0)
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                win = f[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
                if win.shape != tmpl.shape:
                    continue
                same = np.all(win == tmpl, -1) & (tmpl[..., 3] > 0) & ~skip
                score = same.sum() / max(1, ((tmpl[..., 3] > 0) & ~skip).sum())
                if score > best[0]:
                    best = (score, dx, dy)
        score, dx, dy = best
        for x, y, c in g:
            if f[y + dy, x + dx, 3]:
                f[y + dy, x + dx, :3] = c
        moves.append((dx, dy, round(float(score), 2)))
    return moves


def main():
    (HERE / "frames").mkdir(exist_ok=True)
    (HERE / "frames128").mkdir(exist_ok=True)
    for v in ("front", "side", "back", "se", "ne"):
        sheet = HERE / f"{v}_sheet.png"
        if not sheet.exists():
            print(v, "no sheet")
            continue
        a = np.asarray(Image.open(sheet).convert("RGBA"))
        frs = [a[r * 128:(r + 1) * 128, c * 128:(c + 1) * 128] for r in range(a.shape[0] // 128)
               for c in range(a.shape[1] // 128)]
        inp = np.asarray(Image.open(HERE / "input" / f"{v}_128.png").convert("RGBA"))
        inp_s = snap(inp)
        groups = eye_groups(inp)
        if (GP / f"{v}_f0.png").exists():
            gp = np.asarray(Image.open(GP / f"{v}_f0.png").convert("RGBA"))
        else:  # diagonals: the approved still view, outlined, is where the input was cut from
            gp = selout(np.asarray(Image.open(ANIM.parent / "views" / f"{v}.png").convert("RGBA")))[0]
        gy, gx = [w.min() for w in np.where(gp[..., 3] > 0)]
        iy, ix = [w.min() for w in np.where(inp[..., 3] > 0)]
        dx, dy = gx - ix, gy - iy
        def body_floor(a):  # lowest row with at least 4 opaque pixels, so one stray pixel cannot move the frame
            return np.where((a[..., 3] > 0).sum(1) >= 4)[0].max()

        floor = body_floor(inp)
        for i, f in enumerate(frs):
            f = snap(f)
            # ground: the lowest foot pixel goes back on the input's foot row, outline below it
            # (Retro's front and back walks drift up to 3 px)
            shift = floor - body_floor(f)
            f = np.roll(f, shift, axis=0)
            moves = place_eyes(f, inp_s, groups) if groups else []
            f, added, _ = selout(f)
            Image.fromarray(f).save(HERE / "frames128" / f"{v}_f{i}.png")
            big = np.zeros((192, 192, 4), np.uint8)
            ys, xs = np.where(f[..., 3] > 0)
            big[ys + dy, xs + dx] = f[ys, xs]
            Image.fromarray(big).save(HERE / "frames" / f"{v}_f{i}.png")
            print(f"{v}_f{i}: grounded {shift:+d}, eyes moved {moves}, outline px added {added}, bottom {ys.max() + dy}")


if __name__ == "__main__":
    main()
