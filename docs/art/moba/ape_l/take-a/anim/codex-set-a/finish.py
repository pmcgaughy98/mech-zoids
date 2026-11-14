from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parent
NAMES=['front','side','back']
COUNTS={'idle':5,'walk':8,'chest_beat':8,'hex_shield':6}
REFS={n:Image.open(ROOT/'refs'/f'{n}.png').convert('RGBA') for n in NAMES}
PAL=np.unique(np.concatenate([np.array(im)[np.array(im)[:,:,3]>0,:3] for im in REFS.values()]),axis=0)

def approved(n):
 out=Image.new('RGBA',(192,192));out.paste(REFS[n],(16,30));return out

def process(name):
 out=ROOT/name; (out/'frames').mkdir(exist_ok=True);(out/'slices').mkdir(exist_ok=True)
 raw=Image.open(out/'sheet_raw.png').convert('RGBA');a=np.array(raw);W,H=raw.size;N=COUNTS[name]
 rgb0=a[:,:,:3].astype(int)
 m=(a[:,:,3]>127)&~((rgb0.min(2)>195)&(np.ptp(rgb0,axis=2)<24))
 # Real alpha first; fallback only for opaque generated backgrounds.
 if m.mean()>.9:
  rgb=a[:,:,:3].astype(int);m &= ~((rgb[:,:,0]-rgb[:,:,1]>45)&(rgb[:,:,2]-rgb[:,:,1]>45))
 lab,_=ndi.label(m);sz=np.bincount(lab.ravel());m &= sz[lab]>max(16,m.sum()*.0001)
 bands=[s[0] for s in ndi.find_objects(ndi.label(m.any(1))[0]) if s[0].stop-s[0].start>H*.1]
 if len(bands)!=3: raise ValueError(f'{name}: row bands {bands}')
 ys=[0]+[(bands[i].stop+bands[i+1].start)//2 for i in range(2)]+[H]
 xs=np.rint(np.linspace(0,W,N+1)).astype(int)
 for i in range(1,N):
  candidates=[x for x in range(max(2,xs[i]-W//(N*5)),min(W-2,xs[i]+W//(N*5))) if not m[:,x-1:x+2].any()]
  if candidates: xs[i]=min(candidates,key=lambda x:abs(x-xs[i]))
 cells=[]; factors={}
 for r,n in enumerate(NAMES):
  local=m[ys[r]:ys[r+1],xs[0]:xs[1]]; yy,xx=np.where(local);rb=REFS[n].getbbox()
  # Fixed factor per row based on reference neutral size, never normalize each pose.
  factor=((rb[2]-rb[0])/(xx.max()-xx.min()+1)*(rb[3]-rb[1])/(yy.max()-yy.min()+1))**.5
  factors[n]=factor
  for c in range(N):
   box=[int(xs[c]),ys[r],int(xs[c+1]),ys[r+1]];cell=raw.crop(box);cm=m[box[1]:box[3],box[0]:box[2]]
   ca=np.array(cell);ca[:,:,3]=cm*255;ca[~cm]=0;cell=Image.fromarray(ca);b=cell.getbbox();sprite=cell.crop(b)
   sprite.save(out/'slices'/f'{n}_f{c}.png')
   scaled=sprite.resize((round(sprite.width*factor),round(sprite.height*factor)),Image.Resampling.NEAREST)
   sa=np.array(scaled);sm=sa[:,:,3]>127
   # Restore pure native palette and a one-texel dark silhouette.
   rgb=sa[:,:,:3].astype(np.int32);idx=((rgb[:,:,None,:]-PAL.astype(np.int32)[None,None,:,:])**2).sum(3).argmin(2)
   sa[:,:,:3]=PAL[idx];sa[:,:,3]=sm*255
   labels,_=ndi.label(sm);sizes=np.bincount(labels.ravel());sm &= sizes[labels]>2
   rim=sm&~ndi.binary_erosion(sm);sa[rim,:3]=PAL[0];sa[:,:,3]=sm*255;sa[~sm]=0
   fin=Image.fromarray(sa);fr=Image.new('RGBA',(192,192))
   # Native reference center anchor; all ground contacts at 160.
   center=(rb[0]+rb[2]-1)/2+16;x=round(center-(fin.width-1)/2);y=161-fin.height
   fr.paste(fin,(x,y));fr.save(out/'frames'/f'{n}_f{c}.png')
   cells.append(dict(view=n,frame=c,source_box=box,source_opaque_box=list(b),scale=factor,placement=[x,y],touches_cut=bool(b[0]==0 or b[1]==0 or b[2]==cell.width or b[3]==cell.height)))
 (out/'grid.json').write_text(json.dumps(dict(raw_size=[W,H],columns=N,rows=NAMES,x_edges=xs.tolist(),y_edges=ys,row_scale=factors,cells=cells),indent=2))

def board(name):
 out=ROOT/name;N=COUNTS[name];checks=[];rows=[]
 review=Image.new('RGB',(100+N*384,90+3*420),(53,57,62));d=ImageDraw.Draw(review);d.text((10,12),f'APE L / {name} / native frames at 2x; cyan = ground y160',fill='white')
 for r,n in enumerate(NAMES):
  row=[];ref=np.array(approved(n));rm=ref[:,:,3]>0
  d.text((8,90+r*420+180),n,fill='white')
  for c in range(N):
   fr=Image.open(out/'frames'/f'{n}_f{c}.png').convert('RGBA');a=np.array(fr);m=a[:,:,3]>0;yy,xx=np.where(m);colors=np.unique(a[m,:3],axis=0);union=m|rm
   iou=float((m&rm).sum()/union.sum());exact=float((np.all(a==ref,2)&union).sum()/union.sum())
   labels,k=ndi.label(m,structure=np.ones((3,3)));sizes=np.bincount(labels.ravel())[1:]
   checks.append(dict(frame=f'{n}_f{c}',bottom_row=int(yy.max()),colour_count=len(colors),pixels_below_160=int(m[161:].sum()),frame0_IoU=iou if c==0 else None,frame0_exact_colour_IoU=exact if c==0 else None,palette_ok=all(any(np.array_equal(v,p) for p in PAL) for v in colors),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),canvas_edge=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any()),stray_components=int((sizes<3).sum())))
   bg=Image.new('RGB',(192,192),(101,106,112));bg.paste(fr,mask=fr.getchannel('A'));z=bg.resize((384,384),Image.Resampling.NEAREST);review.paste(z,(100+c*384,90+r*420));d.line((100+c*384,90+r*420+322,100+(c+1)*384-1,90+r*420+322),fill=(83,180,183));d.text((110+c*384,70+r*420),f'F{c}',fill='white');row.append(bg.resize((576,576),Image.Resampling.NEAREST))
  durations={'idle':[220]*N,'walk':[110]*N,'chest_beat':[350,130,100,100,100,150,140,350],'hex_shield':[350,130,170,100,170,350]}[name]
  row[0].save(out/f'preview_{n}.gif',save_all=True,append_images=row[1:],duration=durations,loop=0,disposal=2,optimize=False)
 review.save(out/'review.png');review.resize((min(review.width,1800),round(review.height*min(review.width,1800)/review.width)),Image.Resampling.NEAREST).save(out/'review_small.png')
 (out/'checks.txt').write_text('Native palette: 15 opaque colours. IoU uses approved still at (+16,+30).\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 return checks

if __name__=='__main__':
 import sys
 for name in sys.argv[1:] or COUNTS:
  process(name)
  for n in NAMES:
   approved(n).save(ROOT/name/'frames'/f'{n}_f0.png')
   if name in ['chest_beat','hex_shield']:approved(n).save(ROOT/name/'frames'/f'{n}_f{COUNTS[name]-1}.png')
  board(name)
  print(name,'finished')
