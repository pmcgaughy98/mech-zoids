from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parent
NAMES=['se','ne']
COUNTS={'idle':5,'walk':8,'sand_kick':6,'ear_burst':6,'sonic_boom':8}
TIMINGS={'idle':[220]*5,'walk':[100]*8,'sand_kick':[260,130,130,90,160,280],'ear_burst':[260,130,100,100,160,280],'sonic_boom':[300,150,230,260,100,140,180,350]}
HEX='141218 211e27 2e1a6e 3d3a44 6a3cc8 9d9ba2 a46bff b8923a d6d6dc e0c8ff f0d27a 3fe8b0 c8fff0 fff4d6 f6fffb'.split()
PAL=np.array([tuple(bytes.fromhex(s)) for s in HEX],dtype=np.uint8)
REFS={n:Image.open(ROOT/'refs'/f'{n}.png').convert('RGBA') for n in NAMES}
def approved(n):
 out=Image.new('RGBA',(192,192));out.paste(REFS[n],(16,20));return out

def clean(im):
 a=np.array(im);m=a[:,:,3]>127
 lab,k=ndi.label(m,structure=np.ones((3,3)));size=np.bincount(lab.ravel());m &= size[lab]>=3
 holes=ndi.binary_fill_holes(m)&~m
 rgb=a[:,:,:3].astype(np.int32);idx=((rgb[:,:,None,:]-PAL.astype(np.int32)[None,None,:,:])**2).sum(3).argmin(2)
 a[:,:,:3]=PAL[idx];a[holes]=[20,18,24,255];m|=holes
 a[:,:,3]=m*255;a[~m]=0
 rim=m&~ndi.binary_erosion(m);a[rim,:3]=PAL[0]
 a[161:]=0
 return Image.fromarray(a)

def build_idle():
 out=ROOT/'idle';(out/'frames').mkdir(parents=True,exist_ok=True)
 cells=[]
 for n in NAMES:
  a=np.array(approved(n));y,x=np.indices((192,192));sx=x-16;sy=y-20
  # Only head, neck and chest above haunches breathe. Front legs, haunches and grounded tail remain exact.
  upper=sy<118
  if n=='se':upper &= ~((sx<80)&(sy>=113))
  if n=='ne':upper &= ~((sx<88)&(sy>=113))
  if n=='front':upper &= ~(((sx<74)|(sx>86))&(sy>=115))
  if n=='side':upper &= ~((sx<96)&(sy>=113));upper &= ~((sx>=102)&(sy>=119))
  if n=='back':upper &= ~(((sx<71)|(sx>89))&(sy>=116))
  for c,lift in enumerate([0,1,1,1,0]):
   b=a.copy()
   if lift:
    moving=a.copy();moving[~upper]=0;b[upper]=0
    patch=Image.fromarray(moving);im=Image.fromarray(b);im.alpha_composite(patch,(0,-lift));b=np.array(im)
    # Native overlaps bridge the breathing seam without altering fixed lower parts.
    holes=ndi.binary_fill_holes(b[:,:,3]>0)&(b[:,:,3]==0);b[holes]=[20,18,24,255]
    # Close a vertical boundary using the approved texel directly under it.
    for yy in range(132,140):
     gap=(b[yy,:,3]==0)&(b[yy-1,:,3]>0)&(b[yy+1,:,3]>0)&(a[yy,:,3]>0)
     b[yy,gap]=a[yy,gap]
   Image.fromarray(b).save(out/'frames'/f'{n}_f{c}.png')
   cells.append(dict(view=n,frame=c,upper_lift=lift,scale=1,placement=[16,20],duration_ms=220))
 (out/'grid.json').write_text(json.dumps(dict(source='approved still parts only; no generated sheet',columns=5,rows=NAMES,cells=cells,final_canvas=[192,192],approved_offset=[16,20]),indent=2))

def process(name):
 out=ROOT/name;(out/'frames').mkdir(exist_ok=True);(out/'slices').mkdir(exist_ok=True)
 raw=Image.open(out/'sheet_raw.png').convert('RGBA');a=np.array(raw);W,H=raw.size;N=COUNTS[name]
 rgb=a[:,:,:3].astype(int);m=a[:,:,3]>127
 if m.mean()>.85:
  m &= ~((rgb.min(2)>220)&(np.ptp(rgb,axis=2)<25))
  m &= ~((rgb[:,:,0]>180)&(rgb[:,:,2]>180)&(rgb[:,:,1]<100))
 lab,k=ndi.label(m);sz=np.bincount(lab.ravel());m &= sz[lab]>12
 bands=[s[0] for s in ndi.find_objects(ndi.label(m.any(1))[0]) if s[0].stop-s[0].start>H*.10]
 if len(bands)!=2:raise ValueError((name,bands))
 ys=[0]+[(bands[i].stop+bands[i+1].start)//2 for i in range(1)]+[H]
 xs=np.rint(np.linspace(0,W,N+1)).astype(int)
 for i in range(1,N):
  cand=[x for x in range(max(2,xs[i]-W//(N*4)),min(W-2,xs[i]+W//(N*4))) if not m[:,x-1:x+2].any()]
  if cand:xs[i]=min(cand,key=lambda x:abs(x-xs[i]))
 cells=[];factors={}
 # Set B's neighbor-fragment exclusion, extended for overlapping bounding boxes:
 # sonic f4's mouth extends across the nominal f4/f5 vertical cut, but bodies do not touch.
 cl,ck=ndi.label(m);sizes=np.bincount(cl.ravel());objects=ndi.find_objects(cl)
 parts={}
 if name=='sonic_boom':
  for rr,nn in enumerate(NAMES):
   candidates=[(j,b) for j,b in enumerate(objects,1) if b is not None and sizes[j]>500 and ys[rr]<=((b[0].start+b[0].stop)/2)<ys[rr+1]]
   candidates.sort(key=lambda jb:jb[1][1].start)
   assert len(candidates)==N,(name,nn,len(candidates))
   parts[nn]=candidates

 for r,n in enumerate(NAMES):
  yy,xx=np.where(m[ys[r]:ys[r+1],xs[0]:xs[1]]);rb=REFS[n].getbbox()
  factor=((rb[2]-rb[0])/(xx.max()-xx.min()+1)*(rb[3]-rb[1])/(yy.max()-yy.min()+1))**.5
  factors[n]=factor
  for c in range(N):
   nominal_box=[int(xs[c]),ys[r],int(xs[c+1]),ys[r+1]];box=nominal_box.copy();raw_overlap=False
   if name=='sonic_boom':
    j,bb=parts[n][c];raw_overlap=bb[1].start<nominal_box[0] or bb[1].stop>nominal_box[2]
    box=[max(0,bb[1].start-2),max(0,bb[0].start-2),min(W,bb[1].stop+2),min(H,bb[0].stop+2)]
    cm=cl[box[1]:box[3],box[0]:box[2]]==j
   else:cm=m[box[1]:box[3],box[0]:box[2]]
   ca=np.array(raw.crop(box));ca[:,:,3]=cm*255;ca[~cm]=0
   cell=Image.fromarray(ca);b=cell.getbbox();sprite=cell.crop(b);sprite.save(out/'slices'/f'{n}_f{c}.png')
   scaled=sprite.resize((round(sprite.width*factor),round(sprite.height*factor)),Image.Resampling.NEAREST)
   fr=Image.new('RGBA',(192,192));x=round((rb[0]+rb[2]-1)/2+16-(scaled.width-1)/2);y=161-scaled.height;fr.paste(scaled,(x,y));clean(fr).save(out/'frames'/f'{n}_f{c}.png')
   cells.append(dict(view=n,frame=c,source_box=box,nominal_cell_box=nominal_box,raw_nominal_overlap=raw_overlap,component_isolated=name=='sonic_boom',source_opaque_box=list(b),scale=factor,placement=[x,y],touches_cut=bool(b[0]==0 or b[1]==0 or b[2]==cell.width or b[3]==cell.height),duration_ms=TIMINGS[name][c]))
 (out/'grid.json').write_text(json.dumps(dict(raw_size=[W,H],columns=N,rows=NAMES,x_edges=xs.tolist(),y_edges=ys,row_scale=factors,cells=cells,final_canvas=[192,192],approved_offset=[16,20],ground_row=160),indent=2))
 if name!='walk':
  for n in NAMES:
   approved(n).save(out/'frames'/f'{n}_f0.png');approved(n).save(out/'frames'/f'{n}_f{N-1}.png')

if __name__=='__main__':
 import sys
 for name in sys.argv[1:] or COUNTS:
  if name=='idle':build_idle()
  else:process(name)
  print(name,'processed')
