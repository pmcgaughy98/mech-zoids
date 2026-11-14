"""Set A's long one-texel seam check and set B's enclosed-hole fill."""
from finish import *
LOG=[]
def repair(name):
 for n in NAMES:
  for c in range(COUNTS[name]):
   if (name in ['dig','death'] and c==0) or (name=='pop_out' and c in [0,4]):continue
   p=ROOT/name/'frames'/f'{n}_f{c}.png';a=np.array(Image.open(p));m=a[:,:,3]>0
   gap=np.zeros_like(m);gap[:,1:-1]=~m[:,1:-1]&m[:,:-2]&m[:,2:]
   count=0
   for x in range(192):
    lab,k=ndi.label(gap[:,x])
    for j in range(1,k+1):
     yy=np.where(lab==j)[0]
     if len(yy)>=4:a[yy,x]=[*PAL[0],255];count+=len(yy)
   holes=int((ndi.binary_fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)).sum())
   fr=clean(Image.fromarray(a));a=np.array(fr);m=a[:,:,3]>0;lab,k=ndi.label(m,structure=np.ones((3,3)))
   if k>1 and not(name=='pop_out' and c==0):
    sz=np.bincount(lab.ravel());sz[0]=0;a[m&(lab!=sz.argmax())]=0
   Image.fromarray(a).save(p);LOG.append(f'{name}/{n}_f{c}: long seam fill {count}; enclosed fill {holes}')
if __name__=='__main__':
 import sys
 for name in sys.argv[1:] or COUNTS:repair(name);board(name)
 (ROOT/'seam_fill_log.txt').write_text('\n'.join(LOG)+'\n')
