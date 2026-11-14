"""Approved take finishing adapted for fixed ramps and east width 79; no drawing."""
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
bad=solid&(r-g>25)&(b-g>25)&(b>r*.65)
good=solid&~bad
idx=ndimage.distance_transform_edt(~good,return_distances=False,return_indices=True)
a[bad,:3]=a[idx[0][bad],idx[1][bad],:3]
# Light raw-resolution median smoothing, before the one nearest sheet shrink.
smooth=ndimage.median_filter(a[...,:3],size=(3,3,1),mode='nearest')
interior=ndimage.binary_erosion(solid,iterations=2)
seam=(np.dot(a[...,:3],[.2126,.7152,.0722])<40)&solid
interior &= ~seam
a[interior,:3]=smooth[interior]
east=solid[im.height//3:2*im.height//3,:im.width//3]
y,x=np.where(east); raw_width=int(np.ptp(x)+1); scale=79/raw_width
# Predict nearest sample locations, choosing a whole-sheet size with exact east width.
w0=round(im.width*scale); candidates=[]
for w in range(w0-8,w0+9):
 h=round(im.height*w/im.width)
 ys=np.minimum(((np.arange(h)+.5)*im.height/h).astype(int),im.height-1)
 xs=np.minimum(((np.arange(w)+.5)*im.width/w).astype(int),im.width-1)
 m=solid[np.ix_(ys,xs)][h//3:2*h//3,:w//3]
 yy,xx=np.where(m)
 if len(xx) and np.ptp(xx)+1==79: candidates.append((abs(w-w0),w,h))
if not candidates: raise RuntimeError('No single nearest shrink size yields east width 79')
_,w,h=min(candidates)
small=Image.fromarray(a).resize((w,h),Image.Resampling.NEAREST)
src=np.array(small); vis=src[...,3]>127; rgb=src[...,:3].astype(float)
palette=json.loads((ROOT/'palette.json').read_text())
triples=np.array([list(bytes.fromhex(c['hex'])) for c in palette],np.uint8)
r,g,b=rgb.transpose(2,0,1); lum=rgb@[.2126,.7152,.0722]
# Classify material before shade mapping: each material keeps its own ramp.
glow=vis&(g>70)&(g-r>35)&(g>r*1.2)&(b>r*1.12)&(g>b*1.12)
glow|=vis&ndimage.binary_dilation(glow,iterations=2)&(r>150)&(g>180)&(b>150)&(g>r*1.04)&(g>b*1.02)
orange=vis&(r>g*1.16)&(g>b*1.15)
green=vis&~glow&~orange&(g>r*1.08)&(g>b*1.12)
role=np.full(vis.shape,2); role[green]=0; role[orange]=1; role[glow]=3
# Preserve near-black ink and thin dark seams between lighter surfaces.
# Opposed neighbours identify 1-2px seams; broad deep shadows stay on material ramps.
bright=ndimage.maximum_filter(lum,size=3)>75
thin=np.zeros(vis.shape,bool)
for dy,dx in [(0,1),(1,0),(1,1),(1,-1)]:
 for dist in [1,2]:
  plus=ndimage.shift(lum,(dy*dist,dx*dist),order=0,mode='constant',cval=0)
  minus=ndimage.shift(lum,(-dy*dist,-dx*dist),order=0,mode='constant',cval=0)
  thin|=(plus>lum+22)&(minus>lum+22)
ink=vis&((lum<30)|((lum<57)&thin&bright))
role[ink]=4
source_lab=np.array(small.convert('RGB').convert('LAB')).astype(float)
choices_lab=np.array(Image.fromarray(triples[None]).convert('LAB')).astype(float)[0]
source_lab[...,1:]=(source_lab[...,1:]+128)%256-128
choices_lab[...,1:]=(choices_lab[...,1:]+128)%256-128
cost=((source_lab[:,:,None]-choices_lab[None,None])**2*[1,3,3]).sum(3)
for k,c in enumerate(palette):
 ri=['armour green','orange','steel','shield and visor glow','dark accent'].index(c['role'])
 cost[...,k]=np.where(role==ri,cost[...,k],1e12)
nearest=cost.argmin(2)

out=np.zeros_like(src); out[...,:3]=triples[nearest]; out[...,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
meta={'raw_size':im.size,'raw_east_width':raw_width,'target_east_width':79,'shared_scale':w/im.width,'finished_sheet_size':[w,h],'raw_plum_repainted':int(bad.sum()),'smooth':'3x3 median at raw resolution, interior only','raw_sha256':hashlib.sha256((ROOT/'sheet_raw.png').read_bytes()).hexdigest()}
(ROOT/'preparation.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta))
