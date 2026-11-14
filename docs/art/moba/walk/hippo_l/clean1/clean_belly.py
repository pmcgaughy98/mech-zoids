"""Hippo run 1 se/ne cleanup (walk lane, 2026-11-05, free script, no redraw).
Run 1's body layer (run1/source/<v>_body.png) was filled where a leg stood in the still, including below the belly, so
dark body colour hung below the belly where a leg moved away, and in ne it covered the far hind foot (a dark split line).
Fix, per frame: inside each leg's column span (from run 1's own leg pieces, widened 3 px), a pixel that still shows the
dipped body layer, lies more than 1 px below the belly line, and is not covered by a near leg becomes the far leg's pixel
if a far leg layer has one there, else transparent. Belly line: the still's lowest body row in the columns just outside
each span, joined by a straight line (the same rule run 2's belly gate uses). Nothing else changes.
Writes clean1/frames/<v>_f<i>.png for se and ne (e copied unchanged) and report.txt."""
import numpy as np
from pathlib import Path
from PIL import Image
R = Path(__file__).parent.parent / 'run1'; OUT = Path(__file__).parent / 'frames'
ld = lambda p: np.array(Image.open(p).convert('RGBA'))
FAR = {'se': ['LH', 'LF'], 'ne': ['LF', 'LH']}
# Spans whose outside column is the head or jaw, not the trunk, would cut the head: skipped (only near legs live there).
SKIP = {'se': ['LF'], 'ne': ['RF']}
rep = []
for v in ['se', 'ne']:
    ref = ld(R / f'stills/{v}.png'); body = ld(R / f'source/{v}_body.png'); W = ref.shape[1]
    legcols = np.zeros(W, bool); spans = []
    for n in ['RF', 'RH', 'LF', 'LH']:
        m = np.zeros(ref.shape[:2], bool)
        for part in ['lower', 'knee']:
            p = R / f'source/{v}_{n}_{part}.png'
            if p.exists(): m |= ld(p)[:, :, 3] > 0
        xs = np.where(m.any(0))[0]
        if len(xs) and n not in SKIP[v]: spans.append((n, max(xs.min() - 3, 0), min(xs.max() + 3, W - 1)))
    for _, a, b in spans: legcols[a:b + 1] = True
    low = np.full(W, -1)
    for x in range(W):
        ys = np.where(ref[:, x, 3] > 0)[0]
        if len(ys): low[x] = ys.max()
    belly = np.full(W, 999.0)
    for n, a, b in spans:
        l = a - 1
        while l >= 0 and legcols[l] and low[l] >= 0: l -= 1
        r = b + 1
        while r < W and legcols[r] and low[r] >= 0: r += 1
        yl = low[l] if l >= 0 and low[l] >= 0 else None; yr = low[r] if r < W and low[r] >= 0 else None
        if yl is None and yr is None: continue
        if yl is None: yl = yr
        if yr is None: yr = yl
        for x in range(a, b + 1): belly[x] = min(belly[x], yl + (yr - yl) * (x - l) / max(r - l, 1))
        rep.append(f'{v} {n} span x {a}-{b}, belly row {yl} (x {l}) to {yr} (x {r})')
    for f in range(8):
        a = ld(R / f'walk/frames/{v}_f{f}.png'); dip = int(f in (0, 4))
        bd = np.zeros_like(body); bd[dip:] = body[:body.shape[0] - dip]
        far = [ld(R / f'walk/layers/{v}_{n}_f{f}.png') for n in FAR[v]]
        Y, X = np.mgrid[0:a.shape[0], 0:W]
        hang = (a[:, :, 3] > 0) & (bd[:, :, 3] > 0) & np.all(a == bd, axis=2) & (Y > belly[None, :] + dip + 1) & legcols[None, :]
        out = a.copy(); out[hang] = 0
        shown = 0
        for lay in far:
            put = hang & (lay[:, :, 3] > 0); out[put] = lay[put]; shown += int(put.sum())
        Image.fromarray(out).save(OUT / f'{v}_f{f}.png')
        per = {n: int(hang[:, a:b + 1].sum()) for n, a, b in spans}
        rep.append(f'{v} f{f}: {per} by span; {int(hang.sum())} hanging body px removed, {shown} of them now show a far leg')
for f in range(8):
    Image.open(R / f'walk/frames/e_f{f}.png').save(OUT / f'e_f{f}.png')
(Path(__file__).parent / 'report.txt').write_text('\n'.join(rep) + '\n'); print('\n'.join(rep))
