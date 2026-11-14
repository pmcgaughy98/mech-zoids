"""Re-finish Codex's ground pound sheet (Claude, 2026-11-03, Preston's ask: "do the cleanup").

Same keying and smoothing as ../finish.py, with three changes:
- one shrink factor per row, so each row's frame 1 matches its approved sprite (Codex used the side factor for all rows,
  which left the front and back rows 15 to 20% too big);
- the two eye colours are left out of the palette, so magenta-blended rim pixels can no longer turn red;
- each frame is moved up or down by at most 2 px so its lowest pixel sits on the ground line y=160.
The red eyes are put back by hand afterwards (Aseprite).
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
(OUT / "frames").mkdir(exist_ok=True)
NAMES = ["front", "side", "back"]
TARGET = {"front": (72, 70), "side": (103, 67), "back": (66, 77)}
refs = [Image.open(SRC / "refs" / f"{n}.png").convert("RGBA") for n in NAMES]
allpal = np.unique(np.concatenate([np.array(im)[np.array(im)[:, :, 3] > 0, :3] for im in refs]), axis=0)
EYE = {(0xFF, 0x3A, 0x2A), (0xFF, 0xE6, 0xD8)}
pal = np.array([c for c in allpal if tuple(int(v) for v in c) not in EYE])
palette = pal.astype(np.int32)

raw = Image.open(SRC / "sheet_raw.png").convert("RGBA")
a = np.array(raw); rgb = a[:, :, :3].astype(float)
pink = (rgb[:, :, 0] - rgb[:, :, 1] > 28) & (rgb[:, :, 2] - rgb[:, :, 1] > 24) & (rgb[:, :, 2] > rgb[:, :, 0] * .64)
mask = (a[:, :, 3] > 127) & ~pink
labels, _ = ndi.label(mask)
sizes = np.bincount(labels.ravel()); keep = np.flatnonzero(sizes > max(20, mask.sum() * .0003)); keep = keep[keep != 0]
mask = np.isin(labels, keep)
W, H = raw.size; xs = np.rint(np.linspace(0, W, 7)).astype(int)
bands = ndi.find_objects(ndi.label(mask.any(axis=1))[0]); bands = [b[0] for b in bands if b[0].stop - b[0].start > H * .12]
assert len(bands) == 3, "row gutters not found"
ys = np.array([0] + [(bands[i].stop + bands[i + 1].start) // 2 for i in range(2)] + [H])
indices = ndi.distance_transform_edt(~mask, return_distances=False, return_indices=True)
filled = Image.fromarray(a[:, :, :3][tuple(indices)]).filter(ImageFilter.MedianFilter(3))


def cellbox(r, c):
    m = mask[ys[r]:ys[r + 1], xs[c]:xs[c + 1]]; yy, xx = np.where(m)
    return xx.min(), yy.min(), xx.max() + 1, yy.max() + 1


def finish(factor):
    nw, nh = round(W * factor), round(H * factor)
    small = np.array(filled.resize((nw, nh), Image.Resampling.LANCZOS))
    alpha = np.array(Image.fromarray(mask.astype("uint8") * 255).resize((nw, nh), Image.Resampling.BOX)) >= 128
    small = np.array(Image.fromarray(small).filter(ImageFilter.MedianFilter(3)))
    rim = alpha & ~ndi.binary_erosion(alpha)
    for _ in range(4):
        prev = small.copy()
        for y, x in zip(*np.where(rim & (small.mean(2) > 170))):
            y0, y1, x0, x1 = max(0, y - 1), min(nh, y + 2), max(0, x - 1), min(nw, x + 2)
            near = prev[y0:y1, x0:x1][alpha[y0:y1, x0:x1]].astype(float)
            if len(near) > 1 and (np.linalg.norm(near - prev[y, x], axis=1) < 70).sum() < 3:
                small[y, x] = np.median(near, axis=0).astype("uint8")
    for _ in range(12):
        trial = ((small[:, :, None, :].astype(np.int32) - palette[None, None]) ** 2).sum(3).argmin(2)
        changes = []
        for y, x in zip(*np.where(rim & (pal[trial].mean(2) > 180))):
            y0, y1, x0, x1 = max(0, y - 1), min(nh, y + 2), max(0, x - 1), min(nw, x + 2)
            lm = alpha[y0:y1, x0:x1].copy(); lm[y - y0, x - x0] = False
            nearby = trial[y0:y1, x0:x1][lm]
            if len(nearby) and not (nearby == trial[y, x]).any():
                changes.append((y, x, np.median(small[y0:y1, x0:x1][lm], axis=0).astype("uint8")))
        if not changes:
            break
        for y, x, v in changes:
            small[y, x] = v
    flat = small.reshape(-1, 3).astype(np.int32)
    quant = pal[((flat[:, None, :] - palette[None]) ** 2).sum(2).argmin(1)].reshape(nh, nw, 3)
    fin = np.dstack([quant, alpha.astype("uint8") * 255]); fin[~alpha] = 0
    return Image.fromarray(fin.astype("uint8"), "RGBA")


lines = []
for r, n in enumerate(NAMES):
    b = cellbox(r, 0); w, h = b[2] - b[0], b[3] - b[1]
    tw, th = TARGET[n]
    f = tw / w if n == "side" else ((tw / w) * (th / h)) ** .5
    sheet = finish(f)
    sx = np.rint(xs * f).astype(int); sy = np.rint(ys * f).astype(int)
    b0 = sheet.crop((sx[0], sy[r], sx[1], sy[r + 1])).getbbox()
    dx = round(96 - (b0[0] + b0[2] - 1) / 2); dy = 160 - (b0[3] - 1)
    for c in range(6):
        fr = Image.new("RGBA", (192, 192)); fr.paste(sheet.crop((sx[c], sy[r], sx[c + 1], sy[r + 1])), (dx, dy))
        bb = fr.getbbox(); shift = 160 - (bb[3] - 1)
        if shift and abs(shift) <= 2:
            moved = Image.new("RGBA", (192, 192)); moved.paste(fr, (0, shift)); fr = moved
        fr.save(OUT / "frames" / f"{n}_f{c}.png")
        bb = fr.getbbox(); ar = np.array(fr); m = ar[:, :, 3] > 0
        border = bool(m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any())
        lines.append(f"{n}_f{c}: {bb[2]-bb[0]}x{bb[3]-bb[1]} bottom {bb[3]-1} moved {shift:+d} colours {len(np.unique(ar[m, :3], axis=0))} border {border}")
    lines.insert(len(lines) - 6, f"{n}: factor {f:.4f}; frame 1 {w}x{h} raw -> target {tw}x{th}")
(OUT / "refinish-checks.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
