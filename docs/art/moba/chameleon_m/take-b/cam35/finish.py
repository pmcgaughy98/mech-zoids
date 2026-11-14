"""Adapted take-B finish: one shared nearest shrink; fixed material ramps and contextual lenses."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
P=Path(__file__).resolve().parent
im=Image.open(P/'sheet_raw.png').convert('RGBA'); a=np.array(im)
bg=(a[:,:,0]>190)&(a[:,:,1]<85)&(a[:,:,2]>185); a[bg]=0
h,w=a.shape[:2]
slots={'ne':(0,0),'n':(0,1),'nw':(0,2),'e':(1,0),'w':(1,2),'se':(2,0),'s':(2,1),'sw':(2,2)}
def widths(b):
 H,W=b.shape[:2]; result={}
 for d,(r,c) in slots.items():
  y,x=np.where(b[r*H//3:(r+1)*H//3,c*W//3:(c+1)*W//3,3]>0)
  result[d]=int(x.max()-x.min()+1)
 return result
raw=widths(a); base=1/np.mean([raw['s']/49,raw['n']/47,raw['e']/84])
# Search only integer whole-sheet dimensions to reduce rounding error in the specified average.
candidates=[]
for size in range(round(w*base)-5,round(w*base)+6):
 b=np.array(Image.fromarray(a).resize((size,round(h*size/w)),Image.Resampling.NEAREST)); ws=widths(b)
 error=abs(np.mean([ws['s']/49,ws['n']/47,ws['e']/84])-1)
 candidates.append((error,abs(size/w-base),size,b,ws))
_,_,size,b,ws=min(candidates,key=lambda z:z[:2]); vis=b[:,:,3]>0
# A light median on colours only; preserve alpha and silhouettes.
rgb=b[:,:,:3].copy(); smooth=ndi.median_filter(rgb,size=(3,3,1),mode='nearest')
interior=ndi.binary_erosion(vis); rgb[interior]=smooth[interior]
# Lens regions on this generated sheet: amber-ringed circles on steel turrets.
# Gold jaw, throat and belly are outside these regions and remain on the gold ramp.
r,g,bl=rgb.astype(float).transpose(2,0,1)
yy,xx=np.indices(vis.shape); u=xx/b.shape[1]*1254; v=yy/b.shape[0]*1254
zone=np.zeros(vis.shape,bool)
for x0,y0,x1,y1 in [(319,577,354,614),(900,577,935,614),(240,1034,278,1074),(978,1034,1016,1074),(551,1021,585,1061),(668,1021,701,1061)]:
 zone|=(u>=x0)&(u<=x1)&(v>=y0)&(v<=y1)
lens=zone&vis&(r>155)&(g>75)&((bl<160)|((r>220)&(g>210)))
labs,num=ndi.label(lens,np.ones((3,3)))
for k in range(1,num+1):
 if (labs==k).sum()==1:
  lens[labs==k]=False
lens_regions=[]
colours=json.loads((P/'palette.json').read_text()); triples=np.array([list(bytes.fromhex(x['hex'])) for x in colours],dtype=np.uint8)
source_lab=np.array(Image.fromarray(rgb).convert('LAB')).astype(float)
choices_lab=np.array(Image.fromarray(triples[None]).convert('LAB')).astype(float)[0]
source_lab[...,1:]=(source_lab[...,1:]+128)%256-128; choices_lab[...,1:]=(choices_lab[...,1:]+128)%256-128
cost=(((source_lab[:,:,None]-choices_lab[None,None])**2)*[1,3,3]).sum(3)
cost[:,:,12:15]=np.where(lens[:,:,None],cost[:,:,12:15],1e12)
for k in list(range(12))+[15]: cost[:,:,k]=np.where(lens,1e12,cost[:,:,k])
nearest=cost.argmin(2)
# Keep narrow dark seams as accent; leave broad deep shadow on its own material ramp.
lum=rgb@[.2126,.7152,.0722]; dark=vis&(lum<57)&~lens
narrow=dark&~ndi.binary_opening(dark,structure=np.ones((3,3)))
near_light=ndi.maximum_filter(lum,size=5)-lum>48
seam=narrow&near_light&ndi.binary_erosion(vis)
nearest[seam]=15
out=np.zeros_like(b); out[:,:,:3]=triples[nearest]; out[:,:,3]=vis*255; out[~vis]=0
# Restore only existing narrow dark seam pixels, ranked by contrast, up to the
# approved accent share. Broad ramp shadows and the silhouette remain untouched.
accent_restored={}
L=out[:,:,:3]@[.2126,.7152,.0722]
dark=vis&(L<75)
narrow=dark&~ndi.binary_opening(dark,structure=np.ones((3,3)))
contrast=ndi.maximum_filter(L,size=5)-L
candidate=narrow&(contrast>48)&ndi.binary_erosion(vis)&~lens
for d,(rr,cc) in slots.items():
 y0,y1=rr*out.shape[0]//3,(rr+1)*out.shape[0]//3; x0,x1=cc*out.shape[1]//3,(cc+1)*out.shape[1]//3
 m=vis[y0:y1,x0:x1]; part=out[y0:y1,x0:x1]
 ink=np.all(part[:,:,:3]==(20,18,24),axis=2)&m
 target={'s':.073,'se':.060,'sw':.060,'e':.082,'w':.082,'ne':.060,'nw':.060,'n':.071}[d]
 need=max(0,round(m.sum()*target)-int(ink.sum()))
 cy,cx=np.where(candidate[y0:y1,x0:x1]&~ink)
 order=np.argsort(-contrast[y0+cy,x0+cx],kind='stable')[:need]
 out[y0+cy[order],x0+cx[order],:3]=(20,18,24)
 accent_restored[d]=int(len(order))
Image.fromarray(out).save(P/'sheet_finished.png')
result={'raw_widths':raw,'raw_e_s_ratio':raw['e']/raw['s'],'scale':size/w,'sheet_size':list(out.shape[:2][::-1]),'shrunk_widths':ws,'anchor_ratios':{d:ws[d]/v for d,v in [('s',49),('n',47),('e',84)]},'anchor_average':float(np.mean([ws['s']/49,ws['n']/47,ws['e']/84])),'lens_regions':lens_regions,'seam_pixels':int(seam.sum()),'accent_restored':accent_restored}
(P/'preparation.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
