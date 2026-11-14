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
NAMES=['se','ne']
TARGET={'se':(89,70),'ne':(77,74)}
EYE={(255,58,42),(255,230,216)}
refs=[Image.open(OUT/'refs'/f'{n}.png').convert('RGBA') for n in NAMES]
allpal=np.unique(np.concatenate([np.array(im)[np.array(im)[:,:,3]>0,:3] for im in refs]),axis=0)

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


# Set C: preserve set B's finishing functions; adapt layout, anchors and audits.
SHEETS=[('stampede',7,[80]*6),('horn-toss',7,[200,100,100,100,200,100,100]),('ground-pound',6,[100,200,100,300,300,300]),('horn-jab',6,[200,200,100,200,100,100])]
def similarity(f, ref):
    a,b=np.array(f),np.array(ref); union=(a[:,:,3]>0)|(b[:,:,3]>0)
    return float((np.all(a==b,2)&union).sum()/max(1,union.sum()))
def reference_canvas(ref, mirror=False):
    cut=ref.crop(ref.getbbox())
    if mirror: cut=cut.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    dst=Image.new('RGBA',(192,192)); rb=ref.getbbox()
    dst.paste(cut,(rb[0],161-cut.height)); return dst
metadata={}; summary={}
for name,N,timing in SHEETS:
    path=OUT/name; raw=Image.open(path/'sheet_raw.png').convert('RGBA'); W,H=raw.size
    metadata[name]=dict(size=[W,H],sha256=hashlib.sha256((path/'sheet_raw.png').read_bytes()).hexdigest(),prompt=f'prompts/{name}.txt',prompt_sha256=hashlib.sha256((OUT/'prompts'/f'{name}.txt').read_bytes()).hexdigest(),references=['refs/se_6x.png','refs/ne_6x.png'],generations=1)
    (OUT/'generation.json').write_text(json.dumps(metadata,indent=2)+'\n')
    a,mask=keyed(raw); R=2
    ys=boundaries(mask,R,1); xrows=[boundaries(mask[ys[r]:ys[r+1]],N,0) for r in range(R)]
    found=[]; clean=True
    for r in range(R):
        xs=xrows[r]
        for c in range(N):
            m=mask[ys[r]:ys[r+1],xs[c]:xs[c+1]]; b=box(m)
            labels,_=ndi.label(m); sizes=np.bincount(labels.ravel())[1:]
            major=int((sizes>max(30,m.sum()*.025)).sum())
            ok=b is not None and min(b[0],b[1],m.shape[1]-b[2],m.shape[0]-b[3])>=1 and major==1
            found.append(dict(row=NAMES[r],column=c,cell_box_raw=[int(xs[c]),int(ys[r]),int(xs[c+1]),int(ys[r+1])],foreground_box_in_cell=b,major=major,clean=bool(ok)))
            clean &= ok
    grid=dict(clean=bool(clean),raw_size=[W,H],x=[v.tolist() for v in xrows],y=ys.tolist(),cells=found,rows={},coordinate_note='Boxes are half-open. Whole raw sheet resized once per row; rounded scaled cell boxes are then pasted at fixed_cell_offset + ground_adjustment. Effective x/y scale uses resized dimensions/raw dimensions; filtered colours use the set B pipeline.')
    (path/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
    indices=ndi.distance_transform_edt(~mask,return_distances=False,return_indices=True)
    filled=Image.fromarray(a[:,:,:3][tuple(indices)]).filter(ImageFilter.MedianFilter(3))
    lines=[f'Clean 2x{N} grid: {clean}; binary alpha; transparent RGB zero.','Front/back symmetry and side facing-right checks: N/A (se/ne only).']
    pal=allpal; palette=pal.astype(np.int32); (path/'frames').mkdir(exist_ok=True)
    factors=[]; frames=[]; rowstats=[]; comparisons=[]
    for r,n in enumerate(NAMES):
        xs=xrows[r]; b=found[r*N]['foreground_box_in_cell']; w,h=b[2]-b[0],b[3]-b[1]; tw,th=TARGET[n]
        factor=((tw/w)*(th/h))**.5; factors.append(factor)
        sheet=finish(factor); sheet.save(path/f'row_{n}_finished.png')
        sx=np.rint(xs*factor).astype(int); sy=np.rint(ys*factor).astype(int)
        cells=[sheet.crop((sx[c],sy[r],sx[c+1],sy[r+1])) for c in range(N)]
        b0=cells[0].getbbox(); dy=160-(b0[3]-1)
        target=reference_canvas(refs[r]); mirrored=reference_canvas(refs[r],True)
        # Best exact-colour overlap with the actual approved ref, feet aligned.
        centre=round((refs[r].getbbox()[0]+refs[r].getbbox()[2]-b0[0]-b0[2])/2)
        candidates=[]
        for x in range(centre-16,centre+17):
            f=Image.new('RGBA',(192,192)); f.paste(cells[0],(x,dy))
            candidates.append((similarity(f,target),-abs(x-centre),x))
        dx=max(candidates)[2]
        grid['rows'][n]=dict(factor=factor,raw_column1_size=[w,h],target_size=[tw,th],resized_sheet_size=list(sheet.size),effective_scale=[sheet.width/W,sheet.height/H],fixed_cell_offset=[dx,dy],frames=[])
        lines.append(f'{n}: factor={factor:.10f}; fixed cell offset=({dx},{dy}); f0 best exact-colour overlap search +/-16px from ref centre.')
        row=[]; st=[]
        for c,cell in enumerate(cells):
            cb=cell.getbbox(); requested=160-(cb[3]-1+dy); shift=requested if abs(requested)<=3 else 0
            f=Image.new('RGBA',(192,192)); f.paste(cell,(dx,dy+shift)); f.save(path/'frames'/f'{n}_f{c}.png')
            row.append(f); d=stats(f); d['requested_shift']=requested; d['applied_shift']=shift; st.append(d)
            # Every frame records the full source-to-canvas transform.
            grid['rows'][n]['frames'].append(dict(frame=c,raw_cell_box=found[r*N+c]['cell_box_raw'],scaled_cell_box=[int(sx[c]),int(sy[r]),int(sx[c+1]),int(sy[r+1])],fixed_cell_offset=[dx,dy],ground_adjustment=shift,requested_ground_adjustment=requested,final_cell_offset=[dx,dy+shift],foreground_box=list(f.getbbox())))
            lines.append(f'{n}_f{c}: '+', '.join(f'{k}={v}' for k,v in d.items())+(' GROUND_FAIL_OVER_3PX' if abs(requested)>3 else ''))
        f=row[0]; b=f.getbbox(); sim=similarity(f,target)
        # Mirrored reference gets its own best horizontal alignment, feet aligned.
        ms=[]
        for x in range(-16,17):
            q=Image.new('RGBA',(192,192)); q.paste(mirrored,(x,0)); ms.append(similarity(f,q))
        mir=max(ms); facing=sim>mir
        check=f'{n} column1 vs ref: {b[2]-b[0]}x{b[3]-b[1]} vs {tw}x{th}; exact-colour share over opaque union feet aligned={sim:.4f}; mirrored-ref best share={mir:.4f}; direction={"PASS" if facing else "FAIL"}'
        comparisons.append(dict(row=n,frame_size=[b[2]-b[0],b[3]-b[1]],reference_share=sim,mirrored_share=mir,direction_pass=facing)); lines.append(check)
        frames.append(row); rowstats.append(st)
        seq=row[1:] if name=='stampede' else row
        gifsave(seq,path/f'preview_{n}.gif',timing,3,(128,128,128),name=='stampede')
    grid['rows']=grid['rows']; (path/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
    review=Image.new('RGB',(60+(N+1)*576,32+R*576),(128,128,128)); draw=ImageDraw.Draw(review)
    draw.text((60,8),'game-size reference (3x)',fill='white')
    for r,n in enumerate(NAMES):
        draw.text((4,32+r*576+260),n,fill='white')
        z=refs[r].resize((576,576),Image.Resampling.NEAREST); review.paste(z,(60,32+r*576),z)
        for c,f in enumerate(frames[r]):
            z=f.resize((576,576),Image.Resampling.NEAREST); review.paste(z,(60+(c+1)*576,32+r*576),z); draw.text((60+(c+1)*576,8),f'f{c}',fill='white')
    review.save(path/'review.png'); lines+=audit([f for row in frames for f in row],pal)
    # Same-colour singleton ratio using all eight neighbours.
    for r,n in enumerate(NAMES):
        ratios=[]
        for f in frames[r]:
            ar=np.array(f); m=ar[:,:,3]>0; same=np.zeros(m.shape,bool)
            for oy in (-1,0,1):
                for ox in (-1,0,1):
                    if ox or oy: same |= np.all(ar==np.roll(ar,(oy,ox),(0,1)),2)&np.roll(m,(oy,ox),(0,1))
            ratios.append(float((m&~same).sum()/max(1,m.sum())))
        lines.append(n+' lone same-colour pixel shares: '+', '.join(f'{v:.4f}' for v in ratios))
    (path/'checks.txt').write_text('\n'.join(lines)+'\n')
    summary[name]=dict(clean=bool(clean),factors=factors,stats=rowstats,comparisons=comparisons,refchecks=[s for s in lines if 'column1 vs' in s],ground_failures=[f'{n}_f{c}: requested {d["requested_shift"]:+d}px, bottom={d["bottom"]}' for n,row in zip(NAMES,rowstats) for c,d in enumerate(row) if abs(d['requested_shift'])>3])
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(name,'grid',clean,'factors',factors,flush=True)
