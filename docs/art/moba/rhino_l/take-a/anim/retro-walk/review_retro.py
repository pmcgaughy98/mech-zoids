"""Review of the Retro Diffusion walks (rd_advanced_animation__walking, 128x128, 8 frames) against the rhino's
current walk (Claude, 2026-11-04). Preston: "now try walking animations in retro".

Checks per frame: lowest pixel (feet grounded on one line?), silhouette height and width against the input
frame (legs keep length, body keeps size), colours outside the rhino palette plus outline, and how much of the
input silhouette survives (alpha IoU). Writes review-retro.png (input, 8 Retro frames, current walk per view)
and compare-retro.gif (top row Retro, bottom row current walk).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
ANIM = HERE.parent
WALK = ANIM / "codex-set-a/walk/frames_selout"
GP = ANIM / "codex-ground-pound/clean/frames_selout"
VIEWS = ("front", "side", "back", "se", "ne")
PAL = {0x141218, 0x211E27, 0x3D3A44, 0x7A4A06, 0x58555E, 0xFF3A2A, 0xD18A0A, 0x9D9BA2, 0xFFCF1F, 0xD6D6DC,
       0xFFE6D8, 0xFFF4A8}
BG = (0x3D, 0x43, 0x50, 255)
K = 3


def frames_of(sheet):
    a = np.asarray(Image.open(sheet).convert("RGBA"))
    h, w = a.shape[:2]
    n = 128
    return [a[r * n:(r + 1) * n, c * n:(c + 1) * n] for r in range(h // n) for c in range(w // n)]


def bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return xs.min(), ys.min(), xs.max(), ys.max()


def current_walk(view, inp):
    """The current walk frames moved into the same 128 canvas as the Retro input."""
    gp = np.asarray(Image.open(GP / f"{view}_f0.png").convert("RGBA"))
    gx0, gy0, _, _ = bbox(gp)
    ix0, iy0, _, _ = bbox(inp)
    dx, dy = ix0 - gx0, iy0 - gy0
    out = []
    for i in range(1, 7):
        a = np.asarray(Image.open(WALK / f"{view}_f{i}.png").convert("RGBA"))
        c = np.zeros((128, 128, 4), np.uint8)
        c[...] = 0
        ys, xs = np.where(a[..., 3] > 0)
        ok = (ys + dy >= 0) & (ys + dy < 128) & (xs + dx >= 0) & (xs + dx < 128)
        c[ys[ok] + dy, xs[ok] + dx] = a[ys[ok], xs[ok]]
        out.append(c)
    return out


def tile(a, label=""):
    im = Image.new("RGBA", (128, 128), BG)
    im.alpha_composite(Image.fromarray(a))
    im = im.resize((128 * K, 128 * K), Image.NEAREST)
    if label:
        ImageDraw.Draw(im).text((4, 4), label, fill=(235, 235, 240, 255))
    return im


def main():
    report, rows, gif_rows = [], [], {}
    for v in VIEWS:
        sheet = HERE / f"{v}_sheet.png"
        if not sheet.exists():
            report.append(f"{v}: no sheet yet")
            continue
        inp = np.asarray(Image.open(HERE / "input" / f"{v}_128.png").convert("RGBA"))
        ix0, iy0, ix1, iy1 = bbox(inp)
        frs = frames_of(sheet)
        cols = np.concatenate([f[f[..., 3] > 0][:, :3] for f in frs])
        cols = {int(r) << 16 | int(g) << 8 | int(b) for r, g, b in cols}
        report.append(f"{v}: {len(frs)} frames, {len(cols)} colours, {len(cols - PAL)} outside the rhino palette; "
                      f"input bottom {iy1}, height {iy1 - iy0 + 1}, width {ix1 - ix0 + 1}")
        m_in = inp[..., 3] > 0
        for i, f in enumerate(frs):
            x0, y0, x1, y1 = bbox(f)
            m = f[..., 3] > 0
            iou = (m & m_in).sum() / (m | m_in).sum()
            report.append(f"  f{i}: bottom {y1} ({y1 - iy1:+d}), height {y1 - y0 + 1} ({(y1 - y0) - (iy1 - iy0):+d}), "
                          f"width {x1 - x0 + 1}, IoU with input {iou:.2f}")
        cur = current_walk(v, inp) if (GP / f"{v}_f0.png").exists() else []
        done = sorted((HERE / "frames128").glob(f"{v}_f*.png"))
        if done:  # show the finished frames (finish_retro.py) instead of the raw sheet
            frs = [np.asarray(Image.open(p).convert("RGBA")) for p in done]
        rows.append((v, inp, frs, cur))
        gif_rows[v] = (frs, cur)
    (HERE / "REVIEW.txt").write_text("\n".join(report) + "\n", encoding="utf8")
    print("\n".join(report))
    if not rows:
        return
    W = 128 * K
    board = Image.new("RGBA", (9 * W, len(rows) * 2 * W), (0x2A, 0x2E, 0x38, 255))
    for j, (v, inp, frs, cur) in enumerate(rows):
        y = j * 2 * W
        board.alpha_composite(tile(inp, f"{v} input"), (0, y))
        for i, f in enumerate(frs[:8]):
            board.alpha_composite(tile(f, f"retro f{i}"), ((i + 1) * W, y))
        for i, f in enumerate(cur):
            board.alpha_composite(tile(f, f"current f{i + 1}"), ((i + 1) * W, y + W))
    board.save(HERE / "review-retro.png")
    gifs = []
    for t in range(24):
        g = Image.new("RGBA", (len(gif_rows) * W, 2 * W), BG)
        for j, (v, (frs, cur)) in enumerate(gif_rows.items()):
            g.alpha_composite(tile(frs[t % len(frs)], f"retro {v}"), (j * W, 0))
            if cur:
                g.alpha_composite(tile(cur[t % len(cur)], f"current {v}"), (j * W, W))
        gifs.append(g.convert("RGB"))
    gifs[0].save(HERE / "compare-retro.gif", save_all=True, append_images=gifs[1:], duration=120, loop=0)
    print("saved review-retro.png, compare-retro.gif, REVIEW.txt")


if __name__ == "__main__":
    main()
