"""Set A long one-texel join check, followed by set B enclosed-hole and debris cleanup."""
from finish import *
LOG=[]
for name,N in COUNTS.items():
 if name=='idle' or not (ROOT/name/'sheet_raw.png').exists():continue
 for n in NAMES:
  for c in range(N):
   if name!='walk' and c in [0,N-1]:continue
   p=ROOT/name/'frames'/f'{n}_f{c}.png';a=np.array(Image.open(p));m=a[:,:,3]>0
   gap=np.zeros_like(m);gap[:,1:-1]=~m[:,1:-1]&m[:,:-2]&m[:,2:]
   count=0
   for x in range(192):
    lab,k=ndi.label(gap[:,x])
    for j in range(1,k+1):
     yy=np.where(lab==j)[0]
     if len(yy)>=4:a[yy,x]=[20,18,24,255];count+=len(yy)
   holes=int((ndi.binary_fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)).sum())
   fr=clean(Image.fromarray(a));a=np.array(fr);m=a[:,:,3]>0;lab,k=ndi.label(m,structure=np.ones((3,3)))
   dropped=0
   if k>1:
    size=np.bincount(lab.ravel());size[0]=0;drop=m&(lab!=size.argmax());dropped=int(drop.sum());a[drop]=0
   Image.fromarray(a).save(p);LOG.append(f'{name}/{n}_f{c}: long_join_pixels={count}, enclosed_fill_pixels={holes}, detached_remnant_pixels={dropped}')
(ROOT/'seam_log.txt').write_text('\n'.join(LOG)+'\n')
