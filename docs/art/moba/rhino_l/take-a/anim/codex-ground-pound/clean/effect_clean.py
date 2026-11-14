"""Clean the Effect-forge ground pound sheet (forge/ground-pound-forge-v1.jpg) into 8 game frames.

Panels are found as the non-magenta regions, the dark brown panel colour is keyed out, the sheet is
shrunk so the widest ring (cell 5) is about 110 px, and every pixel snaps to the rhino palette (no eye red)
plus up to 3 extra colours for dust and rock. All frames share one anchor: the ring centre.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ANIM = Path("D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim")
SRC = ANIM / "forge/ground-pound-forge-v1.jpg"
REFS = ANIM / "codex-ground-pound/refs"
OUT = ANIM / "codex-ground-pound/clean/effect"
OUT.mkdir(exist_ok=True)
EYE = {(0xFF, 0x3A, 0x2A), (0xFF, 0xE6, 0xD8)}
T, ERODE, RING_W = 32, 8, 110

A = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
mag = (A[..., 0] > 140) & (A[..., 1] < 110) & (A[..., 2] > 90) & (A[..., 0] - A[..., 1] > 90) & (A[..., 2] - A[..., 1] > 40)
lab, n = ndi.label(~mag)
cand = []
for i, sl in enumerate(ndi.find_objects(lab)):
    area = int((lab[sl] == i + 1).sum())
    if area > 20000:
        cand.append((sl, i + 1))
cand.sort(key=lambda t: t[0][0].start)
panels = [p for k in range(0, len(cand), 2) for p in sorted(cand[k:k + 2], key=lambda t: t[0][1].start)]
print("panels", len(panels), [(s[1].start, s[0].start, s[1].stop - s[1].start, s[0].stop - s[0].start) for s, _ in panels])
assert len(panels) == 8

def warm(c):
    return (c[..., 0] > 170) & (c[..., 1] > 90) & (c[..., 2] < 120) & (c[..., 0] - c[..., 2] > 90)

masks, crops = [], []
for k, (sl, lid) in enumerate(panels):
    inside = ndi.binary_erosion(lab[sl] == lid, iterations=ERODE)
    crop = A[sl]
    q = (crop[inside] // 12).astype(int)
    keys = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
    vals, cnt = np.unique(keys, return_counts=True)
    bg = crop[inside][keys == vals[cnt.argmax()]].mean(0)
    d = np.sqrt(((crop - bg) ** 2).sum(-1))
    al = (d > T) & inside
    al = ndi.binary_opening(al, structure=np.ones((2, 2)))
    l2, n2 = ndi.label(al)
    if n2:
        s2 = ndi.sum(al, l2, range(1, n2 + 1))
        al &= np.isin(l2, 1 + np.where(s2 >= 10)[0])
    masks.append(al); crops.append(crop)
    print(f"cell {k+1}: panel bg #{int(bg[0]):02X}{int(bg[1]):02X}{int(bg[2]):02X}, kept {al.sum()/inside.sum():.1%} of panel")

ys, xs = np.where(warm(crops[4]) & masks[4])
w5 = np.percentile(xs, 99) - np.percentile(xs, 1)
f = RING_W / w5
print(f"cell 5 ring width {w5:.0f} px -> factor {f:.4f}")

small = []
for al, crop in zip(masks, crops):
    h, w = al.shape
    tw, th = round(w * f), round(h * f)
    rs = lambda a: np.asarray(Image.fromarray(a.astype(np.float32), mode="F").resize((tw, th), Image.BOX))
    a_s = rs(al)
    col = np.stack([rs(crop[..., c] * al) for c in range(3)], -1) / np.maximum(a_s[..., None], 1e-6)
    small.append((col, a_s > 0.5))

ref = np.concatenate([np.asarray(Image.open(REFS / f"{v}.png").convert("RGBA")).reshape(-1, 4) for v in ("front", "side", "back")])
pal = [tuple(int(v) for v in c) for c in np.unique(ref[ref[:, 3] > 0, :3], axis=0) if tuple(int(v) for v in c) not in EYE]
P = np.array(pal, np.float32)
X = np.concatenate([c[m] for c, m in small])
far = np.sqrt(((X[:, None] - P[None]) ** 2).sum(-1)).min(1) > 40
blue = X[:, 2] > X[:, 0] + 15
Y = X[far & ~blue]
extra = []
if len(Y) > 30:
    C = Y[np.argsort(Y.sum(1))][np.linspace(0, len(Y) - 1, 3).astype(int)]
    for _ in range(25):
        lb = ((Y[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        C = np.array([Y[lb == j].mean(0) if (lb == j).any() else C[j] for j in range(3)])
    extra = [tuple(int(round(v)) for v in c) for c in C]
print("extra colours", ["#%02X%02X%02X" % c for c in extra], "from", len(Y), "far pixels")
P = np.array(pal + extra, np.float32)

frames, centres = [], []
for col, m in small:
    idx = ((col[..., None, :] - P[None, None]) ** 2).sum(-1).argmin(-1)
    rgb = P[idx].astype(np.uint8)
    l3, n3 = ndi.label(m, structure=np.ones((3, 3)))
    if n3:
        s3 = ndi.sum(m, l3, range(1, n3 + 1))
        m = m & np.isin(l3, 1 + np.where(s3 >= 2)[0])
    rgba = np.dstack([rgb, (m * 255).astype(np.uint8)])
    frames.append(rgba)
    wy, wx = np.where(warm(col.astype(np.float32)) & m)
    centres.append(((np.percentile(wx, 2) + np.percentile(wx, 98)) / 2, (np.percentile(wy, 2) + np.percentile(wy, 98)) / 2) if len(wx) > 8 else None)
print("ring centres", [None if c is None else (round(c[0], 1), round(c[1], 1)) for c in centres])
good = [c for c in centres[1:5] if c]
ax, ay = round(float(np.median([c[0] for c in good]))), round(float(np.median([c[1] for c in good])))
meta = {"source": str(SRC), "factor": f, "anchor": [ax, ay], "palette_extra": ["#%02X%02X%02X" % c for c in extra], "frames": []}
for k, fr in enumerate(frames):
    Image.fromarray(fr).save(OUT / f"e{k+1}.png")
    bb = Image.fromarray(fr).getbbox()
    meta["frames"].append({"file": f"e{k+1}.png", "size": [fr.shape[1], fr.shape[0]], "bbox": bb, "pixels": int((fr[..., 3] > 0).sum())})
    print(f"e{k+1}: size {fr.shape[1]}x{fr.shape[0]}, bbox {bb}, {int((fr[..., 3] > 0).sum())} px")
(OUT / "anchor.json").write_text(json.dumps(meta, indent=1))
print("anchor", ax, ay)

S, pad = 3, 12
cw = max(fr.shape[1] for fr in frames) * S; ch = max(fr.shape[0] for fr in frames) * S
board = Image.new("RGBA", (pad + 4 * (cw + pad), pad + 2 * (ch + pad)), (0x3D, 0x43, 0x50, 255))
dr = ImageDraw.Draw(board)
for k, fr in enumerate(frames):
    im = Image.fromarray(fr).resize((fr.shape[1] * S, fr.shape[0] * S), Image.NEAREST)
    x, y = pad + (k % 4) * (cw + pad), pad + (k // 4) * (ch + pad)
    board.alpha_composite(im, (x, y))
    cx, cy = x + ax * S + 1, y + ay * S + 1
    dr.line([(cx - 6, cy), (cx + 6, cy)], fill=(0, 255, 255, 255)); dr.line([(cx, cy - 6), (cx, cy + 6)], fill=(0, 255, 255, 255))
    dr.text((x + 3, y + 3), f"e{k+1}", fill=(255, 255, 255, 255))
board.save(OUT / "effect-board.png")
