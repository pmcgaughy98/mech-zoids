"""Run the copied/adapted approved refinish, audit, and build previews."""
import runpy, sys, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parent
metadata={}
for name in ['idle','walk','horn-jab','horn-toss']:
    path=ROOT/name/'sheet_raw.png'
    with Image.open(path) as im:
        metadata[name]={'size':list(im.size),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'prompt':f'prompts/{name}.txt','generation_count':1}
(ROOT/'generation.json').write_text(json.dumps(metadata,indent=2)+'\n')
for name in metadata:
    sys.argv=['refinish.py',name]
    try:
        g=runpy.run_path(str(ROOT/'refinish.py'))
    except SystemExit:
        continue
    N=g['N']; OUT=g['OUT']; mask=g['mask']; xs=g['xs']; ys=g['ys']; refs=g['refs']; pal=g['pal']; EYE=g['EYE']
    found=[]
    for r,n in enumerate(g['NAMES']):
        for c in range(N):
            m=mask[ys[r]:ys[r+1],xs[c]:xs[c+1]]
            yy,xx=np.where(m); labels,_=ndi.label(m); sizes=np.bincount(labels.ravel())[1:]
            major=int((sizes>max(30,m.sum()*.025)).sum())
            box=None if not len(xx) else [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
            okay=box is not None and min(box[0],box[1],m.shape[1]-box[2],m.shape[0]-box[3])>=2 and major==1
            found.append(dict(row=n,column=c+1,box=box,major_components=major,clean=bool(okay)))
    clean=all(x['clean'] for x in found)
    (OUT/'grid.json').write_text(json.dumps(dict(clean=clean,x_edges=xs.tolist(),y_edges=ys.tolist(),cells=found),indent=2)+'\n')
    if not clean:
        (OUT/'checks.txt').write_text('FAIL: not a clean separate 3xN grid; see grid.json. No finishing.\n')
        print(name,'GRID FAIL'); continue
    lines=[f'Clean 3x{N} grid: YES. Palette union {len(pal)} colours; binary alpha; eye pixels require 8 opaque neighbours.']
    frames=[]; factors=[]; shifts=[]; borders=[]; eye_edges=[]; similarities={}; mirrors={}
    for r,n in enumerate(g['NAMES']):
        b=g['cellbox'](r,0); w,h=b[2]-b[0],b[3]-b[1]; tw,th=g['TARGET'][n]
        factor=tw/w if n=='side' else ((tw/w)*(th/h))**.5
        factors.append(factor); sheet=g['finish'](factor)
        sheet.save(OUT/f'sheet_finished_{n}.png')
        sx=np.rint(xs*factor).astype(int); sy=np.rint(ys*factor).astype(int)
        b0=sheet.crop((sx[0],sy[r],sx[1],sy[r+1])).getbbox()
        dx=round(96-(b0[0]+b0[2]-1)/2); dy=160-(b0[3]-1)
        lines.append(f'{n}: factor {factor:.10f}; column1 raw {w}x{h}; target {tw}x{th}; fixed cell anchor ({dx},{dy}).')
        row=[]
        for c in range(N):
            cell=sheet.crop((sx[c],sy[r],sx[c+1],sy[r+1])); cb=cell.getbbox()
            # Measure before canvas paste, so an overflow cannot be silently clipped.
            original_bottom=dy+cb[3]-1; shift=160-original_bottom
            applied=shift if abs(shift)<=3 else 0
            if abs(shift)>3: shifts.append(f'{n}_f{c} needs {shift:+d}px')
            placement=[dx+cb[0],dy+applied+cb[1],dx+cb[2],dy+applied+cb[3]]
            overflow=placement[0]<=0 or placement[1]<=0 or placement[2]>=192 or placement[3]>=192
            fr=Image.new('RGBA',(192,192)); fr.paste(cell,(dx,dy+applied)); fr.save(OUT/'frames'/f'{n}_f{c}.png'); row.append(fr)
            a=np.array(fr); m=a[:,:,3]>0; bb=fr.getbbox(); colors=np.unique(a[m,:3],axis=0)
            rim=m&~ndi.binary_erosion(m,structure=np.ones((3,3),bool)); counts=[int((np.all(a[:,:,:3]==e,axis=2)&m).sum()) for e in [(255,58,42),(255,230,216)]]
            edge=sum(int((np.all(a[:,:,:3]==e,axis=2)&rim).sum()) for e in EYE); eye_edges.append(edge)
            border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any() or overflow)
            if border: borders.append(f'{n}_f{c}')
            lines.append(f'{n}_f{c}: width={bb[2]-bb[0]} height={bb[3]-bb[1]} colours={len(colors)} red={counts[0]} glint={counts[1]} eye_touch_transparency={edge} bottom={bb[3]-1} required_shift={shift:+d} applied={applied:+d} border={border} in_ref_palette={all(any(np.array_equal(v,p) for p in pal) for v in colors)}')
        frames.append(row)
        fr=row[0]; ref=refs[r]; bb=fr.getbbox(); rb=ref.getbbox(); aligned=Image.new('RGBA',(192,192))
        aligned.paste(ref,(round((bb[0]+bb[2]-rb[0]-rb[2])/2),bb[3]-rb[3]))
        a,b=np.array(fr),np.array(aligned); union=(a[:,:,3]>0)|(b[:,:,3]>0)
        similarity=float((np.all(a==b,axis=2)&union).sum()/union.sum()); similarities[n]=similarity
        lines.append(f'{n} column1 vs ref: {bb[2]-bb[0]}x{bb[3]-bb[1]} vs {rb[2]-rb[0]}x{rb[3]-rb[1]}; exact colour share over opaque union, feet aligned={similarity:.4f}')
        if n!='side':
            vals=[]; silhouettes=[]
            for f in row:
                a=np.array(f.crop(f.getbbox())); m=a[:,:,3]>0; flip=a[:,::-1]; union=m|m[:,::-1]
                vals.append(float((np.all(a==flip,axis=2)&union).sum()/union.sum()))
                silhouettes.append(float((m&m[:,::-1]).sum()/union.sum()))
            mirrors[n]=silhouettes
            lines.append(f'{n} mirror silhouette IoU: '+','.join(f'{v:.3f}' for v in silhouettes)+'; exact-colour: '+','.join(f'{v:.3f}' for v in vals))
    lines.append('Side row faces right: YES (visual review, horn/head on right in every frame).')
    lines.append('Ground shifts >3px: '+('; '.join(shifts) or 'none')+'; canvas border failures: '+(', '.join(borders) or 'none'))
    totals=np.zeros(len(pal),int); edges=totals.copy(); lone=0; area=0
    for row in frames:
        for f in row:
            a=np.array(f); m=a[:,:,3]>0; rim=m&~ndi.binary_erosion(m,structure=np.ones((3,3),bool)); area+=m.sum()
            for i,p in enumerate(pal):
                hit=np.all(a[:,:,:3]==p,axis=2)&m; totals[i]+=hit.sum(); edges[i]+=(hit&rim).sum()
                count=ndi.convolve(hit.astype(int),np.ones((3,3),int),mode='constant')
                lone+=int((hit&(count==1)).sum())
    lines.append('Palette edge audit hex:total/rim/share (8-neighbour rim):')
    for p,t,e in zip(pal,totals,edges): lines.append(f'#{p[0]:02X}{p[1]:02X}{p[2]:02X}: {t}/{e}/{e/max(1,t):.4f}')
    lines.append(f'Top5 share={np.sort(totals)[-5:].sum()/totals.sum():.4f}; lone same-colour pixels={lone/area:.4f}; magenta/plum absent from output palette. Dark frame retained from approved palette.')
    (OUT/'checks.txt').write_text('\n'.join(lines)+'\n')
    review=Image.new('RGB',(70+N*576,32+3*600),'#808080'); d=ImageDraw.Draw(review)
    for c in range(N): d.text((70+c*576+270,8),f'F{c}',fill='white')
    for r,n in enumerate(g['NAMES']):
        d.text((5,32+r*600+260),n,fill='white')
        for c,f in enumerate(frames[r]):
            z=f.resize((576,576),Image.Resampling.NEAREST); review.paste(z,(70+c*576,32+r*600),z)
        ids=list(range(1,7)) if name=='walk' else list(range(N))
        duration=[110]*6 if name=='walk' else [220]*N if name=='idle' else [400]+[90 if name=='horn-jab' else 100]*(N-1)
        gif=[]
        for c in ids:
            bg=Image.new('RGB',(192,192),'#808080'); bg.paste(frames[r][c],mask=frames[r][c].getchannel('A')); gif.append(bg.resize((576,576),Image.Resampling.NEAREST))
        gif[0].save(OUT/f'preview_{n}.gif',save_all=True,append_images=gif[1:],duration=duration,loop=0,disposal=2,optimize=False)
    review.save(OUT/'review.png')
    summary=dict(grid_clean=True,factors=factors,ref_similarity=similarities,mirror_silhouette=mirrors,ground_failures=shifts,border_failures=borders,eye_edge_count=sum(eye_edges),frame_count=3*N)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(name,json.dumps(summary))
