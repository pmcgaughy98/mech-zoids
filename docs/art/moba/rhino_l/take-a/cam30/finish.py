"""Approved take finishing adapted for fixed ramps and east width 103; no drawing."""
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
a[interior,:3]=smooth[interior]
east=solid[im.height//3:2*im.height//3,:im.width//3]
y,x=np.where(east); raw_width=int(np.ptp(x)+1); scale=103/raw_width
# Predict nearest sample locations, choosing a whole-sheet size with exact east width.
w0=round(im.width*scale); candidates=[]
for w in range(w0-8,w0+9):
 h=round(im.height*w/im.width)
 ys=np.minimum(((np.arange(h)+.5)*im.height/h).astype(int),im.height-1)
 xs=np.minimum(((np.arange(w)+.5)*im.width/w).astype(int),im.width-1)
 m=solid[np.ix_(ys,xs)][h//3:2*h//3,:w//3]
 yy,xx=np.where(m)
 if len(xx) and np.ptp(xx)+1==103: candidates.append((abs(w-w0),w,h))
if not candidates: raise RuntimeError('No single nearest shrink size yields east width 103')
_,w,h=min(candidates)
small=Image.fromarray(a).resize((w,h),Image.Resampling.NEAREST)
src=np.array(small); vis=src[...,3]>127; rgb=src[...,:3].astype(float)
palette=json.loads((ROOT.parent/'palette.json').read_text())
triples=np.array([list(bytes.fromhex(c['hex'])) for c in palette],np.uint8)
r,g,b=rgb.transpose(2,0,1); lum=rgb@[.2126,.7152,.0722]
# Lens material must be inside the body; warm magenta/yellow blends on the rim are fringe.
lens_zone=np.indices(vis.shape)[0]>=h//3  # As in approved finish: eyes only in front/profile cells.
red=lens_zone&ndimage.binary_erosion(vis,iterations=2)&(r>180)&(g<110)&(b<135)&(r>g*2)
glint=vis&ndimage.binary_dilation(red,iterations=2)&(r>220)&(g>170)&(b>150)
lens=red|glint
yellow=vis&~lens&(r>g*1.02)&(g>b*1.6)&(g>35)
# Material labels constrain smoothing and mapping; charcoal stays on its own ramp.
role=np.full(vis.shape,2); role[yellow]=0; role[lens]=3
role[vis&~yellow&~lens&(lum>=68)]=1
role[vis&~yellow&~lens&(lum<25)]=4
source_lab=np.array(small.convert('RGB').convert('LAB')).astype(float)
choices_lab=np.array(Image.fromarray(triples[None]).convert('LAB')).astype(float)[0]
source_lab[...,1:]=(source_lab[...,1:]+128)%256-128
choices_lab[...,1:]=(choices_lab[...,1:]+128)%256-128
cost=((source_lab[:,:,None]-choices_lab[None,None])**2*[1,3,3]).sum(3)
for k,c in enumerate(palette):
 ri=['yellow','steel','charcoal','eye','accent'].index(c['role'])
 cost[...,k]=np.where(role==ri,cost[...,k],1e12)
nearest=cost.argmin(2)
nearest[yellow]=np.select([lum[yellow]>215,lum[yellow]>163,lum[yellow]>105],[0,1,2],default=3)
out=np.zeros_like(src); out[...,:3]=triples[nearest]; out[...,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
meta={'raw_size':im.size,'raw_east_width':raw_width,'target_east_width':103,'shared_scale':w/im.width,'finished_sheet_size':[w,h],'raw_plum_repainted':int(bad.sum()),'smooth':'3x3 median at raw resolution, interior only','raw_sha256':hashlib.sha256((ROOT/'sheet_raw.png').read_bytes()).hexdigest()}
(ROOT/'preparation.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta))
