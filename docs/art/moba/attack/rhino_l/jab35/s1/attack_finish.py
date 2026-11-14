"""Finish a draw-only gorilla attack sheet: magenta out, cells by grid, per-row scale from column 1 against the
approved 35 degree still, premultiplied area shrink, map to the still's 15 colours, despeckle, place each frame so its
planted parts (feet and far fist, the bottom band) sit where the still's do, checks and a board.
Usage: python ape_finish.py <run dir> <row views, e.g. se,e> <cols>
Writes <run>/frames/<view>_f<col>.png (160x160, raw, no outline: the packer adds sel-out), checks.txt, board_4x.png."""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as nd

RUN = Path(sys.argv[1]); VIEWS = sys.argv[2].split(','); NC = int(sys.argv[3])
FRAME_SHIFT = {k: (int(x), int(y)) for k, x, y in (t.split(':') for t in sys.argv[5].split(','))} if len(sys.argv) > 5 else {}  # e.g. ne_f1:-1:0, one frame moved so its planted foot meets the still's
ROW_SHIFT = {k: (int(x), int(y)) for k, x, y in (t.split(':') for t in sys.argv[4].split(','))} if len(sys.argv) > 4 else {}  # e.g. e:-6:-2, whole-row move so a planted foot meets the still's
import os
STILLS = Path(os.environ.get('STILLS', 'D:/dev/new-mech-rpg/docs/art/moba/ape_l/take-a/views_cam35_touchup'))
BAND = 14  # bottom band used for placement: rows FEET-BAND+1..FEET

def load_still(v):
    a = np.array(Image.open(STILLS / f'{v}.png').convert('RGBA')); return a
stills = {v: load_still(v) for v in VIEWS}
pal = np.unique(np.concatenate([s[s[:, :, 3] > 0, :3] for s in stills.values()]), axis=0)
INK = pal[np.argmin(pal.astype(float) @ [0.2126, 0.7152, 0.0722])]  # the darkest colour is the seam ink
CANVAS = next(iter(stills.values())).shape[0]
FEET = max(int(np.where(st[:, :, 3].any(1))[0].max()) for st in stills.values())
EYE = np.array([255, 58, 42], np.uint8)

raw = np.array(Image.open(RUN / 'sheet_raw.png').convert('RGBA')).astype(float)
r, g, b = raw[:, :, 0], raw[:, :, 1], raw[:, :, 2]
bg = (r > 170) & (g < 120) & (b > 140) & (np.abs(r - b) < 90)
fg = ~bg
# pink fringe: magenta-tinted edge pixels next to the background become transparent
edge = fg & nd.binary_dilation(bg, iterations=1)
fringe = edge & (r - g > 60) & (b - g > 60)
fg &= ~fringe
fg = nd.binary_opening(fg, iterations=1)
H, W = fg.shape; ch, cw = H / len(VIEWS), W / NC

lab, n = nd.label(nd.binary_dilation(fg, iterations=4))
sizes = nd.sum(fg, lab, range(1, n + 1))
cells = {}
for i, sz in enumerate(sizes, 1):
    if sz < 0.02 * sizes.max(): continue
    yy, xx = np.where((lab == i) & fg)
    rr = min(int(yy.mean() // ch), len(VIEWS) - 1); cc = min(int(xx.mean() // cw), NC - 1)
    cells.setdefault((rr, cc), np.zeros_like(fg))
    cells[(rr, cc)] |= (lab == i) & fg

def bbox(m):
    yy, xx = np.where(m); return xx.min(), yy.min(), xx.max() + 1, yy.max() + 1

def shrink(mask, f, ink_goal=None):
    """Map the raw cell to the palette at full size, then each output pixel takes the most common palette colour of its
    source block (clean clusters, no blended shades). Thin dark seams: pixels whose block holds enough ink are inked,
    darkest first, until the frame reaches the still's ink share."""
    x0, y0, x1, y1 = bbox(mask)
    rgb = raw[y0:y1, x0:x1, :3]; m = mask[y0:y1, x0:x1]
    d = ((rgb[:, :, None, :] - pal[None, None].astype(float)) ** 2 * [0.3, 0.59, 0.11]).sum(3); idx = d.argmin(2)
    w = max(1, round((x1 - x0) * f)); h = max(1, round((y1 - y0) * f))
    def frac(b):
        return np.array(Image.fromarray(np.uint8(b * 255)).resize((w, h), Image.Resampling.BOX)).astype(float) / 255
    alpha = frac(m.astype(float)); keep = alpha >= 0.5
    votes = np.stack([frac((m & (idx == k)).astype(float)) for k in range(len(pal))], 2)
    ink_k = int(np.where(np.all(pal == INK, axis=1))[0][0])
    inkf = votes[:, :, ink_k] / np.maximum(alpha, 1e-6)
    v2 = votes.copy(); v2[:, :, ink_k] = 0; choice = v2.argmax(2)
    choice[(votes.argmax(2) == ink_k)] = ink_k
    if ink_goal is not None:
        goal = round(ink_goal * keep.sum()); cur = int(((choice == ink_k) & keep).sum())
        cand = keep & (choice != ink_k) & (inkf >= 0.12)
        yy, xx = np.where(cand); order = np.argsort(-inkf[yy, xx]); take = order[:max(0, goal - cur)]
        choice[yy[take], xx[take]] = ink_k
    out = np.zeros((h, w, 4), np.uint8); out[:, :, :3] = pal[choice]; out[:, :, 3] = np.where(keep, 255, 0)
    return out, (x0, y0)

def despeckle(a):
    m = a[:, :, 3] > 0; fixed = 0
    for c in np.unique(a[m, :3], axis=0):
        same = m & np.all(a[:, :, :3] == c, axis=2)
        lab, n = nd.label(same)
        if not n: continue
        sz = np.bincount(lab.ravel()); small = np.isin(lab, np.where(sz <= 1)[0]) & (lab > 0)
        for y, x in zip(*np.where(small)):
            nb = a[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4); nb = nb[(nb[:, 3] > 0) & ~np.all(nb[:, :3] == c, axis=1)]
            if len(nb):
                v, k = np.unique(nb[:, :3], axis=0, return_counts=True); a[y, x, :3] = v[k.argmax()]; fixed += 1
    # lone opaque pixels with no opaque 4-neighbour go
    m = a[:, :, 3] > 0; lone = m & (nd.convolve(m.astype(int), [[0, 1, 0], [1, 0, 1], [0, 1, 0]], mode='constant') == 0)
    a[lone] = 0
    return a, fixed

def paste(cell, dx, dy):
    h, w = cell.shape[:2]; out = np.zeros((CANVAS, CANVAS, 4), np.uint8)
    ys0, xs0 = max(0, dy), max(0, dx); ys1, xs1 = min(CANVAS, dy + h), min(CANVAS, dx + w)
    if ys1 > ys0 and xs1 > xs0: out[ys0:ys1, xs0:xs1] = cell[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    clipped = dy < 0 or dx < 0 or dy + h > CANVAS or dx + w > CANVAS
    return out, clipped

def iou(a, b): return (a & b).sum() / max((a | b).sum(), 1)

def fit_still(cell, sm):
    h, w = cell.shape[:2]; best = None
    for dy in range(FEET + 1 - h - 3, FEET + 1 - h + 4):
        for dx in range(-10, CANVAS + 10 - w):
            o, _ = paste(cell, dx, dy); sc = iou(o[:, :, 3] > 0, sm)
            if best is None or sc > best[0]: best = (sc, dx, dy)
    return best

def fine_tune(cell, dx0, dy0, target_band):
    best = None
    dy = FEET + 1 - cell.shape[0]  # the lowest sole always on the feet row
    for dy in [dy]:
        for dx in range(dx0 - 8, dx0 + 9):
            o, _ = paste(cell, dx, dy); m = o[:, :, 3] > 0
            sc = iou(m[FEET - BAND + 1:FEET + 1], target_band) - 0.01 * abs(dx - dx0)
            if best is None or sc > best[0]: best = (sc, dx, dy)
    return best

(RUN / 'frames').mkdir(exist_ok=True)
lines = []; meta = {}
for ri, v in enumerate(VIEWS):
    st = stills[v]; sm = st[:, :, 3] > 0; sx0, sy0, sx1, sy1 = bbox(sm)
    c1 = cells.get((ri, 0))
    if c1 is None: lines.append(f'{v}: no column 1 found'); continue
    x0, y0, x1, y1 = bbox(c1)
    f = float(np.sqrt(((sy1 - sy0) / (y1 - y0)) * ((sx1 - sx0) / (x1 - x0))))
    still_ink = (np.all(st[:, :, :3] == INK, axis=2) & sm).sum() / sm.sum()
    target = sm[FEET - BAND + 1:FEET + 1]
    lines.append(f'{v}: scale {f:.4f} (col 1 {x1-x0}x{y1-y0} raw -> still {sx1-sx0}x{sy1-sy0}); still ink {still_ink:.3f}')
    small1, org1 = shrink(c1, f, still_ink); small1, _ = despeckle(small1)
    sc, bdx, bdy = fit_still(small1, sm)
    sh = ROW_SHIFT.get(v, (0, 0)); bdx += sh[0]; bdy += sh[1]
    lines.append(f'  column 1 fit to the still: IoU {sc:.3f}, row moved {sh} to ({bdx},{bdy})')
    for c in range(NC):
        m = cells.get((ri, c))
        if m is None: lines.append(f'  f{c}: MISSING'); continue
        small, org = shrink(m, f, still_ink); small, fixed = despeckle(small)
        # same place in its cell as column 1 in its cell
        ddx = (org[0] - c * cw) - (org1[0] - 0 * cw); ddy = org[1] - org1[1]
        dx0 = int(round(bdx + ddx * f)); dy0 = int(round(bdy + ddy * f))
        fs = FRAME_SHIFT.get(f'{v}_f{c}', (0, 0)); dx0 += fs[0]; dy0 += fs[1]
        dx, dy = dx0, dy0  # keep Codex's own placement in the row: its ground line held; a fist out toward the camera sits below row 130
        out, clipped = paste(small, dx, dy)
        se_ = np.all(st[:, :, :3] == EYE, axis=2) & sm
        if se_.any():
            x0r, y0r, x1r, y1r = bbox(m); rr, gg, bb = raw[y0r:y1r, x0r:x1r, 0], raw[y0r:y1r, x0r:x1r, 1], raw[y0r:y1r, x0r:x1r, 2]
            red = m[y0r:y1r, x0r:x1r] & (rr > 170) & (gg < 120) & (bb < 110) & (rr > 2 * gg)
            lab_, n_ = nd.label(red)
            if n_:
                k = np.bincount(lab_.ravel())[1:].argmax() + 1; ry, rx = np.where(lab_ == k)
                cy = int(round(ry.mean() * f)) + dy; cx = int(round(rx.mean() * f)) + dx
                ey, ex = np.where(se_); oy, ox = ey - int(round(ey.mean())), ex - int(round(ex.mean()))
                for yy_, xx_ in zip(cy + oy, cx + ox):
                    if 0 <= yy_ < CANVAS and 0 <= xx_ < CANVAS and out[yy_, xx_, 3]: out[yy_, xx_, :3] = EYE
        om = out[:, :, 3] > 0; fx0, fy0, fx1, fy1 = bbox(om)
        ink = (np.all(out[:, :, :3] == INK, axis=2) & om).sum() / om.sum()
        ncol = len(np.unique(out[om, :3], axis=0)); low = fy1 - 1
        bi = iou(om[FEET - BAND + 1:FEET + 1], target)
        Image.fromarray(out).save(RUN / 'frames' / f'{v}_f{c}.png')
        meta[f'{v}_f{c}'] = dict(bbox=[int(fx0), int(fy0), int(fx1), int(fy1)], ink=round(float(ink), 3), colours=ncol,
                                 from_cell=[dx0, dy0], placed=[dx, dy], band_iou=round(float(bi), 3), clipped=bool(clipped))
        lines.append(f'  f{c}: bbox x {fx0}-{fx1-1} y {fy0}-{fy1-1} (still x {sx0}-{sx1-1} y {sy0}-{sy1-1}) lowest {low} '
                     f'band IoU {bi:.3f} ink {ink:.3f} colours {ncol} despeckled {fixed} moved {dx-dx0:+d},{dy-dy0:+d} clipped {clipped}')
(RUN / 'checks.txt').write_text('\n'.join(lines) + '\n'); (RUN / 'finish.json').write_text(json.dumps(meta, indent=1))
print('\n'.join(lines))
# board: still then frames, 4x, on grey, one row per view
S = 4; board = Image.new('RGBA', (CANVAS * (NC + 1) * S, CANVAS * len(VIEWS) * S), (58, 60, 70, 255))
for ri, v in enumerate(VIEWS):
    row = [Image.fromarray(stills[v])] + [Image.open(RUN / 'frames' / f'{v}_f{c}.png') if (RUN / 'frames' / f'{v}_f{c}.png').exists()
                                          else Image.new('RGBA', (CANVAS, CANVAS)) for c in range(NC)]
    for ci, im in enumerate(row):
        board.alpha_composite(im.resize((CANVAS * S, CANVAS * S), Image.Resampling.NEAREST), (ci * CANVAS * S, ri * CANVAS * S))
board.save(RUN / 'board_4x.png'); print('board', board.size)
