"""Re-finish Codex's ground pound sheet (Claude, 2026-11-03, Preston's ask: "do the cleanup").

Same keying and smoothing as ../finish.py, with three changes:
- one shrink factor per row, so each row's frame 1 matches its approved sprite (Codex used the side factor for all rows,
  which left the front and back rows 15 to 20% too big);
- the two eye colours are left out of the palette, so magenta-blended rim pixels can no longer turn red;
- each frame is moved up or down by at most 2 px so its lowest pixel sits on the ground line y=160.
The red eyes are put back by hand afterwards (Aseprite).
"""
from pathlib import Path
import json, hashlib
from PIL import ImageDraw
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC = Path(__file__).resolve().parent
OUT = SRC / "walk"
(OUT / "frames").mkdir(exist_ok=True)
NAMES = ["front", "side", "back"]
TARGET = {"front": (72, 70), "side": (103, 67), "back": (66, 77)}
refs = [Image.open(SRC / "refs" / f"{n}.png").convert("RGBA") for n in NAMES]
allpal = np.unique(np.concatenate([np.array(im)[np.array(im)[:, :, 3] > 0, :3] for im in refs]), axis=0)
EYE = {(0xFF, 0x3A, 0x2A), (0xFF, 0xE6, 0xD8)}
pal = allpal
non_eye = np.array([c for c in allpal if tuple(int(v) for v in c) not in EYE])
palette = pal.astype(np.int32)

raw = Image.open(OUT / "sheet_raw.png").convert("RGBA")
a = np.array(raw); rgb = a[:, :, :3].astype(float)
pink = (rgb[:, :, 0] - rgb[:, :, 1] > 28) & (rgb[:, :, 2] - rgb[:, :, 1] > 24) & (rgb[:, :, 2] > rgb[:, :, 0] * .64)
mask = (a[:, :, 3] > 127) & ~pink
labels, _ = ndi.label(mask)
sizes = np.bincount(labels.ravel()); keep = np.flatnonzero(sizes > max(20, mask.sum() * .0003)); keep = keep[keep != 0]
mask = np.isin(labels, keep)
W, H = raw.size; xs = np.rint(np.linspace(0, W, 8)).astype(int)
# Use actual common empty gutters near the nominal equal-cell divisions.
# The first side horn extends one pixel beyond the nominal boundary.
for c in range(1,7):
    candidates=[x for x in range(max(2,xs[c]-20),min(W-2,xs[c]+21)) if not mask[:,x-2:x+3].any()]
    if candidates: xs[c]=min(candidates,key=lambda x:abs(x-xs[c]))
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
    interior = ndi.binary_erosion(alpha, structure=np.ones((3, 3), bool))
    eyehit = np.isin(quant.view('u1').reshape(nh,nw,3)[:,:,0], [255]) & np.any(np.all(quant[:,:,None,:] == np.array(list(EYE))[None,None,:,:], axis=3), axis=2)
    bad = eyehit & ~interior
    v = small[bad].astype(np.int32)
    quant[bad] = non_eye[((v[:,None,:]-non_eye.astype(np.int32)[None,:,:])**2).sum(2).argmin(1)]
    fin = np.dstack([quant, alpha.astype("uint8") * 255]); fin[~alpha] = 0
    return Image.fromarray(fin.astype("uint8"), "RGBA")

meta = {'walk': {'size': list(raw.size), 'sha256': hashlib.sha256((OUT/'sheet_raw.png').read_bytes()).hexdigest()}}
(SRC/'generation.json').write_text(json.dumps(meta, indent=2)+'\n')
cells=[]
for r,n in enumerate(NAMES):
    for c in range(7):
        m=mask[ys[r]:ys[r+1],xs[c]:xs[c+1]]
        b=cellbox(r,c)
        lab,_=ndi.label(m); counts=np.bincount(lab.ravel())[1:]
        major=int((counts>max(30,m.sum()*.025)).sum())
        clean=min(b[0],b[1],m.shape[1]-b[2],m.shape[0]-b[3])>=2 and major==1
        cells.append(dict(row=n,column=c+1,box=[int(v) for v in b],major_components=major,clean=bool(clean)))
clean=all(v['clean'] for v in cells)
(OUT/'grid.json').write_text(json.dumps(dict(clean=clean,xs=xs.tolist(),ys=ys.tolist(),cells=cells),indent=2)+'\n')
lines=[f'Clean 3x7 grid: {clean}; union palette: {len(pal)} colours. Alpha binary.']
frames=[]; factors={}; issues=[]
for r,n in enumerate(NAMES):
    b=cellbox(r,0); w,h=b[2]-b[0],b[3]-b[1]; tw,th=TARGET[n]
    f=tw/w if n=='side' else ((tw/w)*(th/h))**.5
    factors[n]=float(f); sheet=finish(f)
    sx=np.rint(xs*f).astype(int); sy=np.rint(ys*f).astype(int)
    b0=sheet.crop((sx[0],sy[r],sx[1],sy[r+1])).getbbox()
    dx=round(96-(b0[0]+b0[2]-1)/2); dy=160-(b0[3]-1)
    row=[]
    lines.append(f'{n}: factor={f:.10f}; raw column1={w}x{h}; target={tw}x{th}; anchor=({dx},{dy})')
    for c in range(7):
        cell=sheet.crop((sx[c],sy[r],sx[c+1],sy[r+1]))
        cb=cell.getbbox(); desired=(cb[0]+dx,cb[1]+dy,cb[2]+dx,cb[3]+dy)
        if min(desired[:2])<0 or max(desired[2:])>192: issues.append(f'{n}_f{c}: pre-placement clipping')
        fr=Image.new('RGBA',(192,192)); fr.paste(cell,(dx,dy))
        bb=fr.getbbox(); shift=160-(bb[3]-1)
        if abs(shift)<=3:
            moved=Image.new('RGBA',(192,192)); moved.paste(fr,(0,shift)); fr=moved
        else: issues.append(f'{n}_f{c}: ground offset {shift:+d} exceeds 3 px; left at y={bb[3]-1}')
        fr.save(OUT/'frames'/f'{n}_f{c}.png'); row.append(fr)
        ar=np.array(fr); m=ar[:,:,3]>0; interior=ndi.binary_erosion(m,structure=np.ones((3,3),bool))
        red=np.all(ar[:,:,:3]==[255,58,42],axis=2)&m
        glint=np.all(ar[:,:,:3]==[255,230,216],axis=2)&m
        border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
        bb=fr.getbbox()
        lines.append(f'{n}_f{c}: {bb[2]-bb[0]}x{bb[3]-bb[1]}, colours={len(np.unique(ar[m,:3],axis=0))}, red={red.sum()}, glint={glint.sum()}, eye_touch_transparency={((red|glint)&~interior).sum()}, bottom={bb[3]-1}, ground_correction={shift:+d}, border={border}')
    frames.append(row)
    fr=row[0]; bb=fr.getbbox(); ref=refs[r]; rb=ref.getbbox()
    aligned=Image.new('RGBA',(192,192)); aligned.paste(ref,(round((bb[0]+bb[2]-rb[0]-rb[2])/2),bb[3]-rb[3]))
    aa,ra=np.array(fr),np.array(aligned); union=(aa[:,:,3]>0)|(ra[:,:,3]>0)
    same=(np.all(aa==ra,axis=2)&union).sum()/union.sum()
    lines.append(f'{n} column1 vs ref: {bb[2]-bb[0]}x{bb[3]-bb[1]} vs {rb[2]-rb[0]}x{rb[3]-rb[1]}; same-colour share over opaque union, feet aligned={same:.4f}')
    if n!='side':
        vals=[]; silhouettes=[]
        for fr in row:
            ar=np.array(fr.crop(fr.getbbox())); m=ar[:,:,3]>0; flip=ar[:,::-1]; u=m|(flip[:,:,3]>0)
            vals.append((np.all(ar==flip,axis=2)&u).sum()/u.sum())
            silhouettes.append((m&(flip[:,:,3]>0)).sum()/u.sum())
        lines.append(f'{n} mirror colour F0-F6: '+', '.join(f'{v:.3f}' for v in vals))
        lines.append(f'{n} mirror silhouette IoU F0-F6: '+', '.join(f'{v:.3f}' for v in silhouettes))
lines.append('Side faces right: YES (visual: horns and muzzle on right, tail on left, every frame).')
review=Image.new('RGB',(70+7*576,32+3*600),'#808080'); d=ImageDraw.Draw(review)
for c in range(7): d.text((70+c*576+270,8),f'f{c}',fill='white')
for r,n in enumerate(NAMES):
    d.text((5,32+r*600+260),n,fill='white')
    for c,fr in enumerate(frames[r]):
        z=fr.resize((576,576),Image.Resampling.NEAREST); review.paste(z,(70+c*576,32+r*600),z)
    gif=[]
    for fr in frames[r][1:]:
        bg=Image.new('RGB',(192,192),'#808080'); bg.paste(fr,mask=fr.getchannel('A')); gif.append(bg.resize((576,576),Image.Resampling.NEAREST))
    gif[0].save(OUT/f'preview_{n}.gif',save_all=True,append_images=gif[1:],duration=130,loop=0,disposal=2)
review.save(OUT/'review.png')
totals=np.zeros(len(pal),int); edges=totals.copy(); lone=0; pixels=0
for row in frames:
    for fr in row:
        ar=np.array(fr); m=ar[:,:,3]>0; rim=m&~ndi.binary_erosion(m,structure=np.ones((3,3),bool))
        for i,p in enumerate(pal):
            hit=np.all(ar[:,:,:3]==p,axis=2)&m; totals[i]+=hit.sum(); edges[i]+=(hit&rim).sum()
            neighbours=ndi.convolve(hit.astype(int),np.ones((3,3),int),mode='constant')-hit
            lone+=(hit&(neighbours==0)).sum()
        pixels+=m.sum()
lines.append('Palette audit (hex total rim rim_share):')
for p,t,e in zip(pal,totals,edges): lines.append(f'#{p[0]:02X}{p[1]:02X}{p[2]:02X} {t} {e} {e/max(1,t):.4f}')
lines.append(f'Top5 share={np.sort(totals)[-5:].sum()/totals.sum():.4f}; lone same-colour pixels={lone/pixels:.4f}; exact union palette prevents magenta/plum fringe.')
lines+=issues
(OUT/'checks.txt').write_text('\n'.join(lines)+'\n')
meta['walk'].update(grid_clean=clean,row_factors=factors,issues=issues)
(SRC/'generation.json').write_text(json.dumps(meta,indent=2)+'\n')
print('\n'.join(lines[:36])); print('ISSUES',issues)

