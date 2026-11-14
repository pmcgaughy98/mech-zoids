from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parent
NAMES=['front','side','back']
COUNTS={'dig':6,'pop_out':5,'death':7}
TIMINGS={'dig':[300,120,90,100,100,180],'pop_out':[120,90,130,110,350],'death':[300,100,130,140,160,180,1400]}
HEX='141218 211e27 2e1a6e 3d3a44 6a3cc8 9d9ba2 a46bff b8923a d6d6dc e0c8ff f0d27a 3fe8b0 c8fff0 fff4d6 f6fffb'.split()
PAL=np.array([tuple(bytes.fromhex(h)) for h in HEX],dtype=np.uint8)
REFS={n:Image.open(ROOT/'refs'/f'{n}.png').convert('RGBA') for n in NAMES}
INK=tuple(PAL[0])+(255,)

def approved(n):
 out=Image.new('RGBA',(192,192));out.paste(REFS[n],(16,20));return out

def clean(im,outline=True):
 a=np.array(im);m=a[:,:,3]>127
 lab,k=ndi.label(m,structure=np.ones((3,3)));sz=np.bincount(lab.ravel());m &= sz[lab]>=3
 holes=ndi.binary_fill_holes(m)&~m;m |= holes
 rgb=a[:,:,:3].astype(np.int32);idx=((rgb[:,:,None,:]-PAL.astype(np.int32))**2).sum(3).argmin(2)
 a[:,:,:3]=PAL[idx];a[holes,:3]=PAL[0]
 if outline:a[m&~ndi.binary_erosion(m),:3]=PAL[0]
 a[:,:,3]=m*255;a[~m]=0
 return Image.fromarray(a)

def shifted(im,dx,dy):
 out=Image.new('RGBA',(192,192));out.paste(im,(dx,dy));return out

def clipped(im):
 a=np.array(im);a[161:]=0;return Image.fromarray(a)

def process(name):
 out=ROOT/name;N=COUNTS[name]
 for d in ['frames','slices']:(out/d).mkdir(exist_ok=True)
 raw=Image.open(out/'sheet_raw.png').convert('RGBA');a=np.array(raw);H,W=a.shape[:2];rgb=a[:,:,:3].astype(int)
 m=(a[:,:,3]>160)&~(((rgb[:,:,0]>180)&(rgb[:,:,1]<60)&(rgb[:,:,2]>170))|((rgb[:,:,2]>180)&(rgb[:,:,0]<55)&(rgb[:,:,1]<70))|((rgb[:,:,0]>180)&(rgb[:,:,1]<70)&(rgb[:,:,2]<80)))
 lab,k=ndi.label(m,structure=np.ones((3,3)));sz=np.bincount(lab.ravel());m &= sz[lab]>100
 ys={'dig':[0,289,584,H],'pop_out':[0,316,617,H],'death':[0,269,527,H]}[name]
 nominal=np.rint(np.linspace(0,W,N+1)).astype(int);cells=[];factors={};row_edges={}
 for r,n in enumerate(NAMES):
  xs=nominal.copy()
  for j in range(1,N):
   lo=max(1,int(xs[j]-W/N*.26));hi=min(W-1,int(xs[j]+W/N*.26))
   options=[x for x in range(lo,hi) if not m[ys[r]:ys[r+1],x-1:x+2].any()]
   if options:xs[j]=min(options,key=lambda x:abs(x-nominal[j]))
  row_edges[n]=xs.tolist()
  # Calibrate once per view against the sheet's neutral still. No pose normalization.
  nc=N-1 if name=='pop_out' else 0
  cm=m[ys[r]:ys[r+1],xs[nc]:xs[nc+1]];yy,xx=np.where(cm);rb=REFS[n].getbbox()
  factor=((rb[2]-rb[0])/(xx.max()-xx.min()+1)*(rb[3]-rb[1])/(yy.max()-yy.min()+1))**.5;factors[n]=factor
  for c in range(N):
   box=[int(xs[c]),ys[r],int(xs[c+1]),ys[r+1]];ca=a[box[1]:box[3],box[0]:box[2]].copy();cm=m[box[1]:box[3],box[0]:box[2]];ca[:,:,3]=cm*255;ca[~cm]=0
   # Discard neighboring fragments left by irregular sheet spacing.
   ll,kk=ndi.label(cm,structure=np.ones((3,3)));ss=np.bincount(ll.ravel());ss[0]=0
   cm &= ss[ll]>=max(100,ss.max()*.075);ca[:,:,3]=cm*255;ca[~cm]=0
   cell=Image.fromarray(ca);b=cell.getbbox();sprite=cell.crop(b);sprite.save(out/'slices'/f'{n}_f{c}.png')
   sp=clean(sprite.resize((round(sprite.width*factor),round(sprite.height*factor)),Image.Resampling.NEAREST))
   center=(rb[0]+rb[2]-1)/2+16;x=round(center-(sp.width-1)/2);y=161-sp.height
   if name=='pop_out' and c==2:y-=15
   if name=='dig' and c==3:y+=12
   if name=='dig' and c==4:y+=10
   fr=Image.new('RGBA',(192,192));fr.paste(sp,(x,y));fr=clipped(fr)
   if (name in ['dig','death'] and c==0) or (name=='pop_out' and c==4):fr=approved(n)
   if name=='pop_out' and c==0:
    # Literal native ear tips, translated out of the underground clipping plane.
    tip=REFS[n].copy();ta=np.array(tip);top=rb[1];ta[top+10:]=0;tip=Image.fromarray(ta)
    fr=Image.new('RGBA',(192,192));fr.paste(tip,(16,151-top));fr=clipped(fr)
   if name=='dig' and c==5:
    # Same gold-cream tip, rigid rotation. Everything else is underground.
    tip=REFS['side'].crop((43,130,57,141)).transpose(Image.Transpose.ROTATE_270)
    fr=Image.new('RGBA',(192,192));fr.paste(tip,(91,155));fr=clipped(fr);fr=clean(fr)
   if name=='death' and c==6:
    fa=np.array(fr);g=(fa[:,:,1]>180)&(fa[:,:,0]<210)&(fa[:,:,3]>0);fa[g,:3]=PAL[2];fr=Image.fromarray(fa)
   fr.save(out/'frames'/f'{n}_f{c}.png')
   cells.append(dict(view=n,frame=c,source_box=box,source_opaque_box=list(b),scale=factor,placement=[x,y],duration_ms=TIMINGS[name][c],touches_cut=bool(b[0]==0 or b[1]==0 or b[2]==cell.width or b[3]==cell.height)))
 (out/'grid.json').write_text(json.dumps(dict(raw_size=[W,H],columns=N,rows=NAMES,x_edges=row_edges,y_edges=ys,row_scale=factors,cells=cells,final_canvas=[192,192],approved_offset=[16,20],ground_row=160,durations_ms=TIMINGS[name],loop=False,hold_last_frame=name=='death'),indent=2)+'\n')

def board(name):
 out=ROOT/name;N=COUNTS[name];checks=[]
 review=Image.new('RGB',((N+1)*384,3*420+42),(62,66,72));d=ImageDraw.Draw(review)
 d.text((10,10),f'FENNEC S TAKE B / {name} / native pixels at 2x / cyan ground y160',fill='white')
 for r,n in enumerate(NAMES):
  ref=np.array(approved(n));rm=ref[:,:,3]>0;gif=[]
  for c in range(-1,N):
   fr=approved(n) if c==-1 else Image.open(out/'frames'/f'{n}_f{c}.png').convert('RGBA');a=np.array(fr);m=a[:,:,3]>0
   if c>=0:
    yy,xx=np.where(m);union=m|rm;colors=np.unique(a[m,:3],axis=0);iou=float((m&rm).sum()/union.sum());ciou=float((np.all(a==ref,2)&union).sum()/union.sum())
    labs,k=ndi.label(m,structure=np.ones((3,3)));sz=np.bincount(labs.ravel())[1:]
    required=(name in ['dig','death'] and c==0) or (name=='pop_out' and c==4)
    checks.append(dict(frame=f'{n}_f{c}',duration_ms=TIMINGS[name][c],bottom_row=int(yy.max()),colour_count=len(colors),pixels_below_160=int(m[161:].sum()),silhouette_IoU_vs_still=iou,colour_IoU_vs_still=ciou,exact_still_required=required,binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),palette_ok=all(any(np.array_equal(v,p) for p in PAL) for v in colors),canvas_edge=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any()),stray_components=int((sz<3).sum()),enclosed_hole_pixels=int((ndi.binary_fill_holes(m)&~m).sum())))
   bg=Image.new('RGB',(192,192),(96,102,110));bg.paste(fr,mask=fr.getchannel('A'));z=bg.resize((384,384),Image.Resampling.NEAREST);px=(c+1)*384;py=74+r*420;review.paste(z,(px,py));d.line((px,py+322,px+383,py+322),fill=(68,187,187));d.text((px+8,py-18),f'{n}: APPROVED' if c==-1 else f'{n} F{c} / {TIMINGS[name][c]} ms',fill='white')
   if c>=0:gif.append(bg.resize((576,576),Image.Resampling.NEAREST))
  gif[0].save(out/f'preview_{n}.gif',save_all=True,append_images=gif[1:],duration=TIMINGS[name],disposal=2,optimize=False)
 review.save(out/'review.png');review.resize((min(1800,review.width),round(review.height*min(1800,review.width)/review.width)),Image.Resampling.NEAREST).save(out/'review_small.png')
 (out/'checks.txt').write_text('Approved offset (+16,+20); palette 15; all IoUs measured on opaque union. pop_out f0 ear-tips instruction overrides generic still-f0 rule.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 return checks

if __name__=='__main__':
 for name in COUNTS:process(name);board(name);print(name,'finished')
