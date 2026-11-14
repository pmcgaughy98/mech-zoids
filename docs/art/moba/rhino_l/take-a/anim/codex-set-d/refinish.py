"""Adapted from the approved gp/clean/refinish.py, preserving its keying,
nearest-foreground fill, median smoothing, reduction, and palette pipeline.
Only this job's refs and generated images are opened. All writes stay here.
"""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi
OUT=Path(__file__).resolve().parent
EYE={(255,58,42),(255,230,216)}
refnames=['se','ne','brace_front','brace_side','brace_back']
refmap={n:Image.open(OUT/'refs'/f'{n}.png').convert('RGBA') for n in refnames}
allpal=np.unique(np.concatenate([np.array(im)[np.array(im)[:,:,3]>0,:3] for im in refmap.values()]),axis=0)

def keyed(raw, effects=False):
    a=np.array(raw); rgb=a[:,:,:3].astype(float)
    pink=(rgb[:,:,0]-rgb[:,:,1]>28)&(rgb[:,:,2]-rgb[:,:,1]>24)&(rgb[:,:,2]>rgb[:,:,0]*.64)
    mask=(a[:,:,3]>127)&~pink
    labels,_=ndi.label(mask); sizes=np.bincount(labels.ravel())
    threshold=2 if effects else max(20,mask.sum()*.0003)
    keep=np.flatnonzero(sizes>threshold); keep=keep[keep!=0]
    mask=np.isin(labels,keep)
    return a,mask

def boundaries(mask, count, axis):
    occ=mask.any(axis=axis); L=len(occ)
    # Choose empty gutters nearest the ideal equal-cell boundary.
    edges=[0]
    for i in range(1,count):
        lo=int((i-.22)*L/count); hi=int((i+.22)*L/count)
        runs=ndi.find_objects(ndi.label(~occ)[0]); candidates=[(v[0].start+v[0].stop)//2 for v in runs if v[0].stop-v[0].start>=3 and lo<=(v[0].start+v[0].stop)//2<hi]
        edges.append(min(candidates,key=lambda v:abs(v-i*L/count)) if candidates else round(i*L/count))
    return np.array(edges+[L])

def box(m):
    yy,xx=np.where(m)
    return None if not len(xx) else [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]

def stats(im):
    ar=np.array(im); m=ar[:,:,3]>0; b=im.getbbox()
    rim=m&~ndi.binary_erosion(m,structure=np.ones((3,3)))
    red=np.all(ar[:,:,:3]==[255,58,42],2)&m; glint=np.all(ar[:,:,:3]==[255,230,216],2)&m
    return dict(width=b[2]-b[0],height=b[3]-b[1],colours=len(np.unique(ar[m,:3],axis=0)),red=int(red.sum()),glint=int(glint.sum()),eye_rim=int(((red|glint)&rim).sum()),bottom=b[3]-1,border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any()))

def gifsave(frames,path,durations,scale,bg,loop):
    ims=[]
    for f in frames:
        b=Image.new('RGB',f.size,bg); b.paste(f,mask=f.getchannel('A')); ims.append(b.resize((b.width*scale,b.height*scale),Image.Resampling.NEAREST))
    kw={'loop':0} if loop else {}
    ims[0].save(path,save_all=True,append_images=ims[1:],duration=durations,disposal=2,optimize=False,**kw)

def audit(frames,pal):
    counts=np.zeros(len(pal),int); edges=counts.copy()
    for f in frames:
        ar=np.array(f); m=ar[:,:,3]>0; rim=m&~ndi.binary_erosion(m,structure=np.ones((3,3)))
        for i,p in enumerate(pal):
            hit=np.all(ar[:,:,:3]==p,2)&m; counts[i]+=hit.sum(); edges[i]+=(hit&rim).sum()
    return ['Palette audit hex total rim rim_share:']+[f'#{p[0]:02X}{p[1]:02X}{p[2]:02X} {t} {e} {e/max(1,t):.4f}' for p,t,e in zip(pal,counts,edges)]+[f'Top5 share={np.sort(counts)[-5:].sum()/max(1,counts.sum()):.4f}; near-black (<48 each) share={sum(t for p,t in zip(pal,counts) if max(p)<48)/max(1,counts.sum()):.4f}']

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
    # Eye colours only inside a full opaque 3x3 neighbourhood.
    interior = ndi.binary_erosion(alpha, structure=np.ones((3,3)))
    nonpal = np.array([c for c in pal if tuple(map(int,c)) not in EYE])
    bad = ~interior & np.isin(quant[:,:,0].astype(int)*65536+quant[:,:,1].astype(int)*256+quant[:,:,2], [0xFF3A2A,0xFFE6D8])
    vals=small[bad].astype(np.int32)
    if len(vals): quant[bad]=nonpal[((vals[:,None,:]-nonpal.astype(np.int32)[None])**2).sum(2).argmin(1)]
    fin = np.dstack([quant, alpha.astype("uint8") * 255]); fin[~alpha] = 0
    return Image.fromarray(fin.astype("uint8"), "RGBA")

def share(f,ref):
    fa,ra=np.array(f),np.array(ref); union=(fa[:,:,3]>0)|(ra[:,:,3]>0)
    return float((np.all(fa==ra,2)&union).sum()/max(1,union.sum()))

def bestalign(cell,ref):
    # Fixed reference canvas, normalized to the required foot line.
    rb=ref.getbbox(); target=Image.new('RGBA',(192,192)); target.paste(ref,(0,161-rb[3]))
    b=cell.getbbox(); dy=161-b[3]
    centre=round((rb[0]+rb[2]-b[0]-b[2])/2)
    options=[]
    for dx in range(centre-24,centre+25):
        f=Image.new('RGBA',(192,192)); f.paste(cell,(dx,dy)); options.append((share(f,target),dx))
    _,dx=max(options,key=lambda x:(x[0],-abs(x[1]-centre)))
    return dx,dy,target

import sys
metadata=json.loads((OUT/'generation.json').read_text()) if (OUT/'generation.json').exists() else {}
summary=json.loads((OUT/'summary.json').read_text()) if (OUT/'summary.json').exists() else {}
for name,N in [('brace',5),('death',7),('idle',5),('brace-shuffle',6)]:
    if len(sys.argv)>1 and name not in sys.argv[1:]: continue
    path=OUT/name
    if not (path/'sheet_raw.png').exists():
        summary[name]={'failed':'No raw output; generation failed'}; continue
    names=['front','side','back'] if name=='brace-shuffle' else ['se','ne']
    keys=['brace_'+n for n in names] if name=='brace-shuffle' else names
    refs=[refmap[k] for k in keys]; R=len(names)
    raw=Image.open(path/'sheet_raw.png').convert('RGBA'); W,H=raw.size
    metadata[name]=dict(size=[W,H],sha256=hashlib.sha256((path/'sheet_raw.png').read_bytes()).hexdigest(),prompt=f'prompts/{name}.txt',generations=1)
    a,mask=keyed(raw); ys=boundaries(mask,R,1)
    xrows=[boundaries(mask[ys[r]:ys[r+1]],N,0) for r in range(R)]
    found=[]; clean=True
    for r in range(R):
        xs=xrows[r]
        for c in range(N):
            m=mask[ys[r]:ys[r+1],xs[c]:xs[c+1]]; b=box(m)
            labels,_=ndi.label(m); sizes=np.bincount(labels.ravel())[1:]
            major=int((sizes>max(30,m.sum()*.025)).sum())
            ok=b is not None and min(b[0],b[1],m.shape[1]-b[2],m.shape[0]-b[3])>=1 and major==1
            found.append(dict(row=r,column=c,box=b,raw_cell=[int(xs[c]),int(ys[r]),int(xs[c+1]),int(ys[r+1])],major=major,clean=bool(ok))); clean &= ok
    grid=dict(clean=bool(clean),x=[v.tolist() for v in xrows],y=ys.tolist(),cells=found,rows=[],placements=[],mapping='raw coordinates * effective_scale_xy, rounded cell origin subtracted, then placement_offset added; colour finishing uses nearest fill, median, Lanczos and palette mapping')
    (path/'grid.json').write_text(json.dumps(grid,indent=2))
    if any(f['box'] is None for f in found):
        (path/'checks.txt').write_text('FAIL: empty cells; see grid.json. No substitute images or redraw.\n'); summary[name]={'clean':False,'failed':'empty cells'}; continue
    indices=ndi.distance_transform_edt(~mask,return_distances=False,return_indices=True)
    filled=Image.fromarray(a[:,:,:3][tuple(indices)]).filter(ImageFilter.MedianFilter(3))
    pal=allpal; palette=pal.astype(np.int32); (path/'frames').mkdir(exist_ok=True)
    lines=[f'Clean {R}x{N} grid: {clean}; binary alpha; transparent RGB zero.']
    factors=[]; frames=[]; rowstats=[]; refchecks=[]
    for r,n in enumerate(names):
        xs=xrows[r]; b=found[r*N]['box']; w,h=b[2]-b[0],b[3]-b[1]
        ref=refs[r]; rb=ref.getbbox(); tw,th=rb[2]-rb[0],rb[3]-rb[1]
        factor=tw/w if n=='side' else ((tw/w)*(th/h))**.5; factors.append(factor)
        sheet=finish(factor); sheet.save(path/f'row_{n}_finished.png')
        sx=np.rint(xs*factor).astype(int); sy=np.rint(ys*factor).astype(int)
        first=sheet.crop((sx[0],sy[r],sx[1],sy[r+1])); dx,dy,target=bestalign(first,ref)
        grid['rows'].append(dict(name=n,factor=factor,effective_scale_xy=[sheet.width/W,sheet.height/H],fixed_cell_offset=[dx,dy],target=[tw,th]))
        row=[]; st=[]; lines.append(f'{n}: factor={factor:.10f}; fixed cell anchor offset=({dx},{dy})')
        for c in range(N):
            cell=sheet.crop((sx[c],sy[r],sx[c+1],sy[r+1])); b=cell.getbbox()
            requested=160-(b[3]-1+dy); shift=requested if abs(requested)<=3 else 0
            f=Image.new('RGBA',(192,192)); f.paste(cell,(dx,dy+shift))
            f.save(path/'frames'/f'{n}_f{c}.png'); row.append(f); d=stats(f); d['requested_shift']=requested; st.append(d)
            clipped=b[0]+dx<0 or b[2]+dx>192 or b[1]+dy+shift<0 or b[3]+dy+shift>192
            grid['placements'].append(dict(row=n,column=c,scaled_cell=[int(sx[c]),int(sy[r]),int(sx[c+1]),int(sy[r+1])],placement_offset=[dx,dy+shift],ground_requested=requested,ground_applied=shift,clipped=clipped))
            lines.append(f'{n}_f{c}: '+', '.join(f'{k}={v}' for k,v in d.items())+(' GROUND_FAIL_OVER_3PX' if abs(requested)>3 else '')+(' CLIPPED' if clipped else ''))
        frames.append(row); rowstats.append(st)
        # Compare both references after independently aligning feet and best horizontal overlap.
        f=row[0]; crop=f.crop(f.getbbox()); _,_,t=bestalign(crop,ref)
        _,_,mt=bestalign(crop,ref.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
        def bestshare(target):
            dx2,dy2,target2=bestalign(crop,target); temp=Image.new('RGBA',(192,192)); temp.paste(crop,(dx2,dy2)); return share(temp,target2)
        sim=bestshare(ref); msim=bestshare(ref.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
        d=st[0]; line=f'{n} column1 vs ref: {d["width"]}x{d["height"]} vs {tw}x{th}; exact-colour share={sim:.4f}; mirrored ref={msim:.4f}; orientation={"PASS" if msim<sim else "FAIL"} (opaque union; feet aligned; best x overlap each)'
        lines.append(line); refchecks.append(line)
        if n in ('front','back'):
            vals=[]
            for f in row:
                ar=np.array(f.crop(f.getbbox())); flip=ar[:,::-1]; union=(ar[:,:,3]>0)|(flip[:,:,3]>0)
                vals.append(float((np.all(ar==flip,2)&union).sum()/union.sum()))
            lines.append(f'{n} mirror colour similarities: '+', '.join(f'{v:.3f}' for v in vals))
    if 'side' in names: lines.append('Side faces right: pending visual audit in REPORT.txt (not inferred from numbers).')
    review=Image.new('RGB',((N+1)*576,32+R*576),(128,128,128)); draw=ImageDraw.Draw(review)
    for r,n in enumerate(names):
        ref=refs[r]; refcanvas=Image.new('RGBA',(192,192)); refcanvas.paste(ref,(0,161-ref.getbbox()[3])); z=refcanvas.resize((576,576),Image.Resampling.NEAREST)
        review.paste(z,(0,32+r*576),z); draw.text((8,40+r*576),n+' REF',fill='white')
        for c,f in enumerate(frames[r]):
            z=f.resize((576,576),Image.Resampling.NEAREST); review.paste(z,((c+1)*576,32+r*576),z); draw.text(((c+1)*576+8,8),f'f{c}',fill='white')
        dur={'brace':[120,120,120,600,120],'death':[120]*6+[1000],'idle':[200]*5,'brace-shuffle':[150]*6}[name]
        gifsave(frames[r],path/f'preview_{n}.gif',dur,3,(128,128,128),name in ('idle','brace-shuffle'))
    review.save(path/'review.png'); lines+=audit([f for row in frames for f in row],pal)
    for r,n in enumerate(names):
        lone=[]
        for f in frames[r]:
            ar=np.array(f); m=ar[:,:,3]>0; same=np.zeros(m.shape,int)
            for yy,xx in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                shifted=np.roll(ar,(yy,xx),(0,1)); same+=np.all(ar==shifted,2)&m
            lone.append(float(((same==0)&m).sum()/max(1,m.sum())))
        lines.append(f'{n} lone-colour-pixel shares: '+', '.join(f'{v:.4f}' for v in lone))
    (path/'checks.txt').write_text('\n'.join(lines)+'\n')
    (path/'grid.json').write_text(json.dumps(grid,indent=2))
    summary[name]=dict(clean=bool(clean),factors=factors,stats=rowstats,refchecks=refchecks,mirror=[s for s in lines if 'mirror colour' in s])
    print(name,'grid',clean,'factors',factors)
(OUT/'generation.json').write_text(json.dumps(metadata,indent=2)+'\n')
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
