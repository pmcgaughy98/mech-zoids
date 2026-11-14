"""Closes the one-texel see-through seams left between moved parts (Claude, 2026-11-04).
A seam is a run of 4 or more transparent texels, each with opaque texels on both sides (left and right, or above and
below). Each is filled with the stills' outline colour, so the parts read as separated by ink, not by a gap.
Originals are kept in <animation>/frames_pre_seam/. Rerun is safe: it always starts from those originals."""
import shutil,json
from scipy import ndimage as ndi
log={}
from pathlib import Path
import numpy as np
from PIL import Image

INK = (0x14, 0x1A, 0x16, 255)
HERE = Path(__file__).parent

def runs(mask_1d):
    out, start = [], None
    for i, m in enumerate(list(mask_1d) + [False]):
        if m and start is None:
            start = i
        elif not m and start is not None:
            out.append((start, i))
            start = None
    return out

for anim in ["idle", "walk", "chest_beat", "hex_shield"]:
    src, keep = HERE / anim / "frames", HERE / anim / "frames_pre_seam"
    if not keep.exists():
        shutil.copytree(src, keep)
    for f in sorted(src.glob("*.png")):
        a = np.array(Image.open(f).convert("RGBA"))
        op = a[:, :, 3] > 0
        hv = np.zeros_like(op)
        hv[:, 1:-1] = (~op[:, 1:-1]) & op[:, :-2] & op[:, 2:]   # gap between left and right
        hh = np.zeros_like(op)
        hh[1:-1, :] = (~op[1:-1, :]) & op[:-2, :] & op[2:, :]   # gap between above and below
        fill = np.zeros_like(op)
        for x in range(op.shape[1]):
            for s, e in runs(hv[:, x]):
                if e - s >= 4:
                    fill[s:e, x] = True
        for y in range(op.shape[0]):
            for s, e in runs(hh[y, :]):
                if e - s >= 4:
                    fill[y, s:e] = True
        enclosed=ndi.binary_fill_holes(op)&~op
        _,count=ndi.label(enclosed)
        fill |= enclosed
        # Exact approved endpoints take precedence over seam repair.
        endpoint=f.stem.endswith('_f0') or (anim=='chest_beat' and f.stem.endswith('_f7')) or (anim=='hex_shield' and f.stem.endswith('_f5')) or (anim=='idle' and f.stem.endswith('_f4'))
        if endpoint: fill[:]=False
        log[f'{anim}/{f.stem}']={'enclosed_holes_found':count,'enclosed_hole_pixels_found':int(enclosed.sum()),'hole_pixels_filled':int((fill&enclosed).sum()),'seam_pixels_filled':int((fill&~enclosed).sum())}
        a[fill] = INK
        Image.fromarray(a).save(src / f.name)
        if fill.sum():
            print(anim, f.name, int(fill.sum()))

(HERE/'seam_log.json').write_text(json.dumps(log,indent=2))
