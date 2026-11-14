"""Native grey discs, copied from B polish.py's component matching pass."""
from finish import *
LOG=[]
def discs(name):
 for n in NAMES:
  boxes=[(83,113,92,121),(76,125,84,133)] if n=='se' else [(94,108,101,117),(91,122,98,130)]
  templates=[]
  for box in boxes:
   patch=REFS[n].crop(box);pa=np.array(patch);keep=np.zeros(pa.shape[:2],bool)
   for j in [3,5,8]:keep |= np.all(pa[:,:,:3]==PAL[j],2)&(pa[:,:,3]>0)
   g=np.all(pa[:,:,:3]==PAL[5],2)&keep;y,x=np.where(g)
   if len(x):
    pa[~keep]=0;templates.append((Image.fromarray(pa),x.mean(),y.mean(),len(x)))
  for c in range(COUNTS[name]):
   if c==0 or (name=='dig' and c>=3) or (name=='pop_out' and c==4):continue
   p=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(p).convert('RGBA');a=np.array(fr);m=a[:,:,3]>0
   grey=np.all(a[:,:,:3]==PAL[5],2)&m;grey[154:]=False;l,k=ndi.label(grey)
   for j in range(1,k+1):
    y,x=np.where(l==j)
    if len(x)<6 or len(x)>45 or y.min()<125 or y.max()-y.min()>9:continue
    patch,cx,cy,size=min(templates,key=lambda t:abs(t[3]-len(x)));dx,dy=round(x.mean()-cx),round(y.mean()-cy)
    fr.alpha_composite(patch,(dx,dy));a=np.array(fr);a[~m]=0;fr=Image.fromarray(a);LOG.append(f'{name}/{n}_f{c}: native grey disc {dx},{dy}')
   clean(fr).save(p)
if __name__=='__main__':
 import sys
 for name in sys.argv[1:] or COUNTS:discs(name)
 (ROOT/'detail_finish_log.txt').write_text('\n'.join(LOG)+'\n');print('Native disc placements',len(LOG))
