"""Approved take finishing adapted for fixed ramps and kangaroo camera anchor; no drawing."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parent
im=Image.open(ROOT/'sheet_raw.png').convert('RGBA'); a=np.array(im)
r,g,b=a[...,:3].astype(int).transpose(2,0,1)
bg=(r>190)&(g<85)&(b>185)
a[bg]=0
# Remove blended magenta/plum before palette mapping, preserving the silhouette.
solid=a[...,3]>127
bad=solid&(r-g>25)&(b-g>25)&(r>b*.85) # magenta hue, not legitimate violet armour
good=solid&~bad
idx=ndimage.distance_transform_edt(~good,return_distances=False,return_indices=True)
a[bad,:3]=a[idx[0][bad],idx[1][bad],:3]
# Light raw-resolution median smoothing, before the one nearest sheet shrink.
smooth=ndimage.median_filter(a[...,:3],size=(3,3,1),mode='nearest')
interior=ndimage.binary_erosion(solid,iterations=2)
raw_eye=solid&(g-r>25)&(b-r>20)&(g>90)
raw_eye |= solid&ndimage.binary_dilation(raw_eye,iterations=3)&(g-r>35)&(b-r>25)&(g>130)
raw_eye |= solid&ndimage.binary_dilation(raw_eye,iterations=5)&(r>170)&(g-r>4)&(b-r>3)
seam=((np.dot(a[...,:3],[.2126,.7152,.0722])<55)|raw_eye)&solid
interior &= ~seam
a[interior,:3]=smooth[interior]
# One shared nearest shrink, anchored by mean south/north/east width ratios.
CELLS={'s':(2,1),'n':(0,1),'e':(1,0)}
ANCHOR={'s':55,'n':49,'e':69}
def widths(mask):
 h,w=mask.shape; result={}
 # Components allow a sprite to extend a pixel into the empty middle cell,
 # matching slice_grid's subject extent instead of clipping at a cell divider.
 labels,n=ndimage.label(mask)
 objects=ndimage.find_objects(labels)
 for d,(row,col) in CELLS.items():
  found=[]
  for i,box in enumerate(objects,1):
   if box is None: continue
   sy,sx=box; cy=(sy.start+sy.stop-1)/2; cx=(sx.start+sx.stop-1)/2
   if int(cy*3/h)==row and int(cx*3/w)==col:
    found.append((int((labels[box]==i).sum()),sx.stop-sx.start))
  result[d]=max(found)[1]
 return result

raw_widths=widths(solid); raw_width=raw_widths['e']
scale=1/np.mean([raw_widths[d]/ANCHOR[d] for d in CELLS])
w0=round(im.width*scale); candidates=[]
for w in range(w0-20,w0+21):
 h=round(im.height*w/im.width)
 sampled=np.array(Image.fromarray((solid*255).astype('uint8')).resize((w,h),Image.Resampling.NEAREST))>0
 ws=widths(sampled); ratios={d:ws[d]/ANCHOR[d] for d in CELLS}
 candidates.append((abs(np.mean(list(ratios.values()))-1),abs(w-w0),w,h,ws,ratios))
err,_,w,h,anchor_widths,anchor_ratios=min(candidates)
small=Image.fromarray(a).resize((w,h),Image.Resampling.NEAREST)
src=np.array(small); vis=src[...,3]>127; rgb=src[...,:3].astype(float)
palette=json.loads((ROOT/'palette.json').read_text())
triples=np.array([list(bytes.fromhex(c['hex'])) for c in palette],np.uint8)
r,g,b=rgb.transpose(2,0,1); lum=rgb@[.2126,.7152,.0722]
# Classify material before shade mapping: each material keeps its own ramp.
glow=vis&(np.array(Image.fromarray((raw_eye*255).astype('uint8')).resize((w,h),Image.Resampling.NEAREST))>0)
orange=vis&~glow&(r-g>18)&(r-b>35)
neutral_dist=np.stack([((rgb-np.array(list(bytes.fromhex(c))))**2).sum(2) for c in ['47444e','26232b','d6d6dc','9d9ba2','58555e','38353e']],axis=2)
charcoal=vis&~glow&~orange&(neutral_dist.argmin(2)<2)
role=np.full(vis.shape,1); role[orange]=0; role[charcoal]=2; role[glow]=3
# Internal opposed bright neighbours distinguish thin seams from broad shadows.
inside=ndimage.binary_erosion(vis)
thin=np.zeros(vis.shape,bool)
for dy,dx in [(0,1),(1,0),(1,1),(1,-1)]:
 for dist in [1,2]:
  plus=ndimage.shift(lum,(dy*dist,dx*dist),order=0,mode='constant',cval=0)
  minus=ndimage.shift(lum,(-dy*dist,-dx*dist),order=0,mode='constant',cval=0)
  thin|=(plus>lum+18)&(minus>lum+18)
ink=vis&inside&~glow&(lum<90)&thin
# Retain the darkest eligible thin seams to the approved accent share per view.
# This changes colour roles only, with the same fixed palette throughout.
target={(2,1):.078,(2,0):.077,(1,0):.075,(0,0):.060,(0,1):.058,(0,2):.060,(1,2):.075,(2,2):.077}
keep=np.zeros(vis.shape,bool)
for (row,col),share in target.items():
 y0,y1=row*h//3,(row+1)*h//3; x0,x1=col*w//3,(col+1)*w//3
 local=ink[y0:y1,x0:x1]; yy,xx=np.where(local)
 count=min(len(yy),round(vis[y0:y1,x0:x1].sum()*share))
 order=np.argsort(lum[y0+yy,x0+xx],kind='stable')[:count]
 keep[y0+yy[order],x0+xx[order]]=True
role[keep]=4
source_lab=np.array(small.convert('RGB').convert('LAB')).astype(float)
choices_lab=np.array(Image.fromarray(triples[None]).convert('LAB')).astype(float)[0]
source_lab[...,1:]=(source_lab[...,1:]+128)%256-128
choices_lab[...,1:]=(choices_lab[...,1:]+128)%256-128
cost=((source_lab[:,:,None]-choices_lab[None,None])**2*[1,3,3]).sum(3)
for k,c in enumerate(palette):
 ri=['orange-red','steel','charcoal frame','eye','dark accent'].index(c['role'])
 cost[...,k]=np.where(role==ri,cost[...,k],1e12)
nearest=cost.argmin(2)

out=np.zeros_like(src); out[...,:3]=triples[nearest]; out[...,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
meta={'raw_size':im.size,'anchor_widths':anchor_widths,'anchor_ratios':anchor_ratios,'anchor_mean':float(np.mean(list(anchor_ratios.values()))),'raw_east_width':raw_width,'target_east_width':69,'shared_scale':w/im.width,'finished_sheet_size':[w,h],'raw_plum_repainted':int(bad.sum()),'smooth':'3x3 median at raw resolution, interior only','raw_sha256':hashlib.sha256((ROOT/'sheet_raw.png').read_bytes()).hexdigest()}
(ROOT/'preparation.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta))
