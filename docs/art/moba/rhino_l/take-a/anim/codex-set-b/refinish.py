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
NAMES=['front','side','back']
TARGET={'front':(72,70),'side':(103,67),'back':(66,77)}
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

metadata={}; summary={}
for name,N in [('brace',5),('stampede',7),('death',7),('effects',6)]:
    path=OUT/name; raw=Image.open(path/'sheet_raw.png').convert('RGBA'); W,H=raw.size
    metadata[name]=dict(size=[W,H],sha256=hashlib.sha256((path/'sheet_raw.png').read_bytes()).hexdigest(),prompt=f'prompts/{name}.txt',generations=1)
    a,mask=keyed(raw,name=='effects'); R=6 if name=='effects' else 3
    ys=boundaries(mask,R,1); xs=boundaries(mask,N,0)
    xrows=[boundaries(mask[ys[r]:ys[r+1]],N,0) for r in range(R)]
    found=[]; clean=True
    for r in range(R):
        xs=xrows[r]
        for c in range(N):
            m=mask[ys[r]:ys[r+1],xs[c]:xs[c+1]]; b=box(m)
            labels,_=ndi.label(m); sizes=np.bincount(labels.ravel())[1:]
            major=int((sizes>max(30,m.sum()*.025)).sum())
            ok=b is not None and min(b[0],b[1],m.shape[1]-b[2],m.shape[0]-b[3])>=1 and (name=='effects' or major==1)
            found.append(dict(row=r,column=c,box=b,major=major,clean=bool(ok))); clean &= ok
    (path/'grid.json').write_text(json.dumps(dict(clean=bool(clean),x=[v.tolist() for v in xrows],y=ys.tolist(),cells=found),indent=2))
    indices=ndi.distance_transform_edt(~mask,return_distances=False,return_indices=True)
    filled=Image.fromarray(a[:,:,:3][tuple(indices)]).filter(ImageFilter.MedianFilter(3))
    lines=[f'Clean {R}x{N} grid: {clean}; binary alpha; transparent RGB zero.']
    factors=[]; frames=[]; rowstats=[]
    if name!='effects':
        pal=allpal; palette=pal.astype(np.int32); (path/'frames').mkdir(exist_ok=True)
        for r,n in enumerate(NAMES):
            xs=xrows[r]
            b=found[r*N]['box']; w,h=b[2]-b[0],b[3]-b[1]; tw,th=TARGET[n]
            factor=tw/w if n=='side' else ((tw/w)*(th/h))**.5; factors.append(factor)
            sheet=finish(factor); sheet.save(path/f'row_{n}_finished.png')
            sx=np.rint(xs*factor).astype(int); sy=np.rint(ys*factor).astype(int)
            b0=sheet.crop((sx[0],sy[r],sx[1],sy[r+1])).getbbox()
            dx=round(96-(b0[0]+b0[2]-1)/2); dy=160-(b0[3]-1)
            row=[]; st=[]
            lines.append(f'{n}: factor={factor:.10f}; fixed cell anchor offset=({dx},{dy})')
            for c in range(N):
                cell=sheet.crop((sx[c],sy[r],sx[c+1],sy[r+1])); f=Image.new('RGBA',(192,192)); f.paste(cell,(dx,dy))
                shift=160-(f.getbbox()[3]-1)
                if abs(shift)<=3:
                    moved=Image.new('RGBA',f.size); moved.paste(f,(0,shift)); f=moved
                f.save(path/'frames'/f'{n}_f{c}.png'); row.append(f); d=stats(f); d['requested_shift']=shift; st.append(d)
                lines.append(f'{n}_f{c}: '+', '.join(f'{k}={v}' for k,v in d.items())+(' GROUND_FAIL_OVER_3PX' if abs(shift)>3 else ''))
            frames.append(row); rowstats.append(st)
            f=row[0]; ref=refs[r]; b=f.getbbox(); rb=ref.getbbox(); aligned=Image.new('RGBA',(192,192))
            aligned.paste(ref,(round((b[0]+b[2]-rb[0]-rb[2])/2),b[3]-rb[3]))
            fa,ra=np.array(f),np.array(aligned); union=(fa[:,:,3]>0)|(ra[:,:,3]>0)
            sim=float((np.all(fa==ra,2)&union).sum()/union.sum())
            lines.append(f'{n} column1 vs ref: {b[2]-b[0]}x{b[3]-b[1]} vs {tw}x{th}; exact colour share over opaque union, feet aligned={sim:.4f}')
            if n!='side':
                vals=[]
                for f in row:
                    ar=np.array(f.crop(f.getbbox())); flip=ar[:,::-1]; union=(ar[:,:,3]>0)|(flip[:,:,3]>0)
                    vals.append(float((np.all(ar==flip,2)&union).sum()/union.sum()))
                lines.append(f'{n} mirror colour similarities: '+', '.join(f'{v:.3f}' for v in vals))
        lines.append('Side faces right: YES (visual audit; horn and head at right).')
        review=Image.new('RGB',(60+N*576,32+3*576),(128,128,128)); draw=ImageDraw.Draw(review)
        for r,n in enumerate(NAMES):
            draw.text((4,32+r*576+260),n,fill='white')
            for c,f in enumerate(frames[r]):
                z=f.resize((576,576),Image.Resampling.NEAREST); review.paste(z,(60+c*576,32+r*576),z); draw.text((60+c*576,8),f'f{c}',fill='white')
            seq=frames[r][1:] if name=='stampede' else frames[r]
            dur=[80]*6 if name=='stampede' else ([120,120,120,600,120] if name=='brace' else [120]*6+[1000])
            gifsave(seq,path/f'preview_{n}.gif',dur,3,(128,128,128),name=='stampede')
        review.save(path/'review.png')
        lines+=audit([f for row in frames for f in row],pal)
        summary[name]=dict(clean=bool(clean),factors=factors,stats=rowstats,refchecks=[s for s in lines if 'column1 vs' in s],mirror=[s for s in lines if 'mirror colour' in s])
    else:
        pal=np.unique(np.array([c.tolist() for c in allpal if tuple(map(int,c)) not in EYE]+[[117,84,58],[141,113,87],[234,190,83]],dtype=np.uint8),axis=0); palette=pal.astype(np.int32)
        names=['impact-puff','hit-spark','stun-loop','dust-trail','brace-ring','deflect-spark']; targets=[40,28,26,16,110,28]; anchors={}
        for r,(n,tw) in enumerate(zip(names,targets)):
            xs=xrows[r]
            widest=max(found[r*N+c]['box'][2]-found[r*N+c]['box'][0] for c in range(N)); factor=tw/widest; factors.append(factor)
            # Effects keep their deliberate spark fragments; reduce directly after nearest-foreground fill.
            for attempt in range(30):
                dims=(round(W*factor),round(H*factor))
                test=np.array(Image.fromarray(mask.astype('uint8')*255).resize(dims,Image.Resampling.BOX))>=128
                tx=np.rint(xs*factor).astype(int); ty=np.rint(ys*factor).astype(int)
                widths=[]
                for c in range(N):
                    b=box(test[ty[r]:ty[r+1],tx[c]:tx[c+1]])
                    widths.append(b[2]-b[0] if b else 0)
                actual=max(widths)
                if actual==tw: break
                factor *= (tw+.25)/(actual+.25)
            factors[-1]=factor
            scaled=filled.resize((round(W*factor),round(H*factor)),Image.Resampling.LANCZOS)
            rgb=np.array(scaled); alpha=np.array(Image.fromarray(mask.astype('uint8')*255).resize(scaled.size,Image.Resampling.BOX))>=128
            if r not in (1,5):
                lab,_=ndi.label(alpha,structure=np.ones((3,3))); sz=np.bincount(lab.ravel()); alpha &= sz[lab]>1
            vals=rgb.reshape(-1,3).astype(np.int32); q=pal[((vals[:,None,:]-palette[None])**2).sum(2).argmin(1)].reshape(rgb.shape)
            ar=np.dstack([q,alpha.astype('uint8')*255]); ar[~alpha]=0; sheet=Image.fromarray(ar)
            sx=np.rint(xs*factor).astype(int); sy=np.rint(ys*factor).astype(int)
            cells=[sheet.crop((sx[c],sy[r],sx[c+1],sy[r+1])) for c in range(N)]
            boxes=[f.getbbox() for f in cells]
            # One stable cell-coordinate anchor, estimated across the complete row.
            ax=round(np.median([(b[0]+b[2]-1)/2 for b in boxes])); ground=r in (0,3,4)
            ay=max(b[3]-1 for b in boxes) if ground else round(np.median([(b[1]+b[3]-1)/2 for b in boxes]))
            left=max(ax-b[0] for b in boxes); right=max(b[2]-1-ax for b in boxes); top=max(ay-b[1] for b in boxes); bottom=max(b[3]-1-ay for b in boxes)
            cw,ch=left+right+1+8,top+bottom+1+8; dest=(left+4,top+4); row=[]; (path/n).mkdir(exist_ok=True)
            anchors[n]=dict(canvas=[cw,ch],anchor=list(dest),source_cell_anchor=[ax,ay],type='ground-centre' if ground else 'burst-centre',margin=4,factor=factor)
            for c,cell in enumerate(cells):
                f=Image.new('RGBA',(cw,ch)); f.paste(cell,(dest[0]-ax,dest[1]-ay)); f.save(path/n/f'f{c}.png'); row.append(f); d=stats(f)
                lines.append(f'{n}/f{c}: '+', '.join(f'{k}={v}' for k,v in d.items()))
            frames.append(row); gifsave(row,path/f'preview_{n}.gif',[90]*6,4,(61,67,80),n=='stun-loop')
            lines.append(f'{n}: factor={factor:.10f}; widest target={tw}; actual widest={max(stats(f)["width"] for f in row)}; anchor={dest}; canvas={cw}x{ch}')
        (path/'anchor.json').write_text(json.dumps(anchors,indent=2))
        cellw=max(f.width for row in frames for f in row)*4+20; cellh=max(f.height for row in frames for f in row)*4+20
        review=Image.new('RGB',(110+6*cellw,30+6*cellh),(61,67,80)); draw=ImageDraw.Draw(review)
        for r,n in enumerate(names):
            draw.text((4,30+r*cellh+8),n,fill='white')
            for c,f in enumerate(frames[r]):
                z=f.resize((f.width*4,f.height*4),Image.Resampling.NEAREST); review.paste(z,(110+c*cellw+(cellw-z.width)//2,30+r*cellh+(cellh-z.height)//2),z)
        review.save(path/'review.png'); lines+=audit([f for row in frames for f in row],pal)
        summary[name]=dict(clean=bool(clean),factors=factors,anchors=anchors)
    (path/'checks.txt').write_text('\n'.join(lines)+'\n')
    print(name, 'grid',clean,'factors',factors)
(OUT/'generation.json').write_text(json.dumps(metadata,indent=2)+'\n')
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
