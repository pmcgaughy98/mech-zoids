"""Approved take finishing adapted for fixed ramps and east width 75; no drawing."""
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
# Violet armour is intentional; detect only saturated magenta spill, not violet.
bad=solid&(r>g*1.5)&(b>g*1.5)&(r>b*.78)&((r-g)>30)
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
y,x=np.where(east); raw_width=int(np.ptp(x)+1); scale=75/raw_width
# Predict nearest sample locations, choosing a whole-sheet size with exact east width.
w0=round(im.width*scale); candidates=[]
for w in range(w0-8,w0+9):
 h=round(im.height*w/im.width)
 ys=np.minimum(((np.arange(h)+.5)*im.height/h).astype(int),im.height-1)
 xs=np.minimum(((np.arange(w)+.5)*im.width/w).astype(int),im.width-1)
 m=solid[np.ix_(ys,xs)][h//3:2*h//3,:w//3]
 yy,xx=np.where(m)
 if len(xx) and np.ptp(xx)+1==75: candidates.append((abs(w-w0),w,h))
if not candidates: raise RuntimeError('No single nearest shrink size yields east width 75')
_,w,h=min(candidates)
small=Image.fromarray(a).resize((w,h),Image.Resampling.NEAREST)
src=np.array(small); vis=src[...,3]>127; rgb=src[...,:3].astype(float)
palette=json.loads((ROOT/'palette.json').read_text())
triples=np.array([list(bytes.fromhex(c['hex'])) for c in palette],np.uint8)
r,g,b=rgb.transpose(2,0,1); lum=rgb@[.2126,.7152,.0722]
# Material masks, using the approved fennec's own ramps.
lens_zone=np.indices(vis.shape)[0]>=h//3
mint=vis&lens_zone&(g>r+25)&(g>b+5)
lens=mint|(vis&lens_zone&ndimage.binary_dilation(mint,iterations=1)&(rgb.min(2)>180)&(g>=r))
yellow=vis&~lens&(r>g*1.02)&(g>b*1.18)&(g>35)
violet=vis&~lens&~yellow&(b>r*1.18)&(b>g*1.25)
role=np.full(vis.shape,3); role[violet]=0; role[yellow]=1; role[lens]=4
steel=vis&~violet&~yellow&~lens&(lum>=85)
role[steel]=2
# Thin dark overlap lines receive accent; broad dark fields stay on material ramps.
dark=vis&~lens&(lum<48)
radius=ndimage.distance_transform_edt(dark)
light=vis&(lum>65)
light_count=ndimage.convolve(light.astype(int),np.ones((5,5),int),mode='constant')
seams=dark&(radius<=1.5)&(light_count>=5)&ndimage.binary_erosion(vis)
# Preserve only the strongest thin seams up to each approved accent share.
# Unselected dark regions retain violet deep or charcoal shadow, never new ink.
seam_selected=np.zeros(vis.shape,bool)
targets={(2,1):.050,(2,0):.061,(1,0):.058,(0,0):.062,(0,1):.062,(2,2):.061,(1,2):.058,(0,2):.062}
for (row,col),target in targets.items():
 y0,y1=row*h//3,(row+1)*h//3; x0,x1=col*w//3,(col+1)*w//3
 local=seams[y0:y1,x0:x1]; yy,xx=np.where(local)
 wanted=round(vis[y0:y1,x0:x1].sum()*target)
 # Near-black source colour and narrowness distinguish seams from deep material.
 score=lum[y0:y1,x0:x1][local]+8*radius[y0:y1,x0:x1][local]-.15*light_count[y0:y1,x0:x1][local]
 keep=np.argsort(score,kind='stable')[:wanted]
 seam_selected[y0+yy[keep],x0+xx[keep]]=True
role[seam_selected]=5
source_lab=np.array(small.convert('RGB').convert('LAB')).astype(float)
choices_lab=np.array(Image.fromarray(triples[None]).convert('LAB')).astype(float)[0]
source_lab[...,1:]=(source_lab[...,1:]+128)%256-128
choices_lab[...,1:]=(choices_lab[...,1:]+128)%256-128
cost=((source_lab[:,:,None]-choices_lab[None,None])**2*[1,3,3]).sum(3)
for k,c in enumerate(palette):
 ri=['violet','cream-gold','steel','charcoal frame','eye','dark accent'].index(c['role'])
 cost[...,k]=np.where(role==ri,cost[...,k],1e12)
nearest=cost.argmin(2)
out=np.zeros_like(src); out[...,:3]=triples[nearest]; out[...,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
meta={'raw_size':im.size,'raw_east_width':raw_width,'target_east_width':75,'shared_scale':w/im.width,'finished_sheet_size':[w,h],'raw_plum_repainted':int(bad.sum()),'smooth':'3x3 median at raw resolution, interior only','raw_sha256':hashlib.sha256((ROOT/'sheet_raw.png').read_bytes()).hexdigest()}
(ROOT/'preparation.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta))
