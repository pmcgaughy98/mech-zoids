from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from scipy import ndimage
P=Path(__file__).resolve().parent
sys.path.insert(0,'tools/art')
import sprite_director as sd
A={d:np.array(Image.open(P/'views'/f'{d}.png').convert('RGBA')) for d in sd.FACINGS}
C={d:a[Image.open(P/'views'/f'{d}.png').getbbox()[1]:Image.open(P/'views'/f'{d}.png').getbbox()[3],Image.open(P/'views'/f'{d}.png').getbbox()[0]:Image.open(P/'views'/f'{d}.png').getbbox()[2]] for d,a in A.items()}
def material(a,cs):
 return (a[...,3]>0)&np.any(np.all(a[...,:3,None]==np.array([tuple(bytes.fromhex(c)) for c in cs]).T,axis=2),axis=2)
def span(m):
 y,x=np.where(m); return int(x.max()-x.min()+1),[int(x.min()),int(x.max()),int(y.min()),int(y.max())]
e=C['e']; south=C['s']
red=material(e,['ff6a72','e01e3c','9c0f26','520716']); red[63:]=False; red[:,56:]=False
wl,wb=span(red)
# Anatomical ROIs in bbox-local pixels, chosen by eye on take-B review.png.
body=(e[...,3]>0); body[:18]=False;body[54:]=False;body[:,:36]=False;body[:,64:]=False
bl,bb=span(body)
head=material(e,['ffffff','ece6d6','b8ae98']);head[16:]=False
hl,hb=span(head)
beak=material(e,['ffe680','ffc21a','c4820a']);beak[24:]=False
kl,kb=span(beak)
trunk=material(south,['ffffff','ece6d6','b8ae98']);trunk[:26]=False;trunk[49:]=False
bw,bb2=span(trunk)
sp=span(south[...,3]>0)[0]
green={d:int(np.sum((A[d][...,3]>0)&np.all(A[d][...,:3]==(106,255,106),axis=2))) for d in ['ne','nw']}
r={'measurement':'horizontal projected lengths, inclusive pixels; manually selected anatomical regions, uncertainty about 2px','east_wing':{'length':wl,'bbox':wb},'east_body':{'length':bl,'bbox':bb},'east_wing_body_ratio':wl/bl,'east_head':{'length':hl,'bbox':hb},'east_beak':{'length':kl,'bbox':kb},'east_beak_head_ratio':kl/hl,'east_south_height_ratio':len(e)/len(south),'south_wingspan':sp,'south_body_width':bw,'south_body_bbox':bb2,'south_wingspan_body_ratio':sp/bw,'green_eye_pixels':green}
(P/'shape.json').write_text(json.dumps(r,indent=2))
(P/'shape.txt').write_text(f'East wing {wl}px / body {bl}px = {wl/bl:.3f}; beak {kl}px / head {hl}px = {kl/hl:.3f}.\nEast height {len(e)}px / south {len(south)}px = {len(e)/len(south):.3f}.\nSouth wing span {sp}px / body width {bw}px = {sp/bw:.3f}.\nGreen eye pixels ne {green["ne"]}; nw {green["nw"]}.\nHorizontal projected spans; anatomical ROIs and bounding boxes in shape.json; manual boundary uncertainty +/-2px.\n')
lone={d:sd.lone_share(A[d]) for d in sd.FACINGS};(P/'lone-after.json').write_text(json.dumps(lone,indent=2))
print((P/'shape.txt').read_text());print('max lone',max(lone.values()))
# Final independent edge invariants, no mutation.
edge_counts={'plum_magenta':0,'lone_pale':0,'ink':0}
for d,a in A.items():
 m=a[...,3]>0;edge=m&~ndimage.binary_erosion(m);rgb=a[...,:3].astype(float); rr,gg,bb=rgb.transpose(2,0,1)
 edge_counts['plum_magenta']+=int((edge&(rr-gg>25)&(bb-gg>25)&(bb>rr*.65)&~np.all(rgb==(20,18,24),axis=2)).sum())
 edge_counts['ink']+=int((edge&np.all(rgb==(20,18,24),axis=2)).sum())
 for c in np.unique(a[edge,:3],axis=0):
  if c@[.2126,.7152,.0722]<145:continue
  same=m&np.all(rgb==c,axis=2); neighbours=ndimage.convolve(same.astype(int),np.ones((3,3),int),mode='constant')-same
  edge_counts['lone_pale']+=int((same&edge&(neighbours==0)).sum())
(P/'edge-invariants.json').write_text(json.dumps(edge_counts,indent=2));print(edge_counts)
