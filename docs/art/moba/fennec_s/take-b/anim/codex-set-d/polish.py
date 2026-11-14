"""Native-piece finishing adapted from set B polish.py; no part resizing."""
from finish import *
LOG=[]
def eye(a):
 g=np.all(a[:,:,:3]==PAL[11],2)&(a[:,:,3]>0);y,x=np.where(g)
 return np.array([x.mean(),y.mean()]) if len(x) else None

def restore(name,n,c):
 path=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr);ra=np.array(approved(n));ge=eye(a);re=eye(ra)
 # Whole upright head can retain every native identity texel.
 full=(name=='dig' and c in [1,2]) or (name=='pop_out' and c in [1,2,3]) or (name=='death' and c==1)
 if full:
  if n=='se' and ge is not None:dx,dy=np.rint(ge-re).astype(int)
  else:dx,dy=0,fr.getbbox()[1]-approved(n).getbbox()[1]
  dx=int(np.clip(dx,-12,12));dy=int(np.clip(dy,-20,24))
  cut=110 if n=='se' else 107
  # Remove old complete head, restore native head plus neck connector.
  a[:cut+20+dy]=0;fr=Image.fromarray(a)
  patch=ra.copy();patch[cut+20:]=0;fr.alpha_composite(shifted(Image.fromarray(patch),dx,dy))
  box=(89,108,99,122) if n=='se' else (83,104,97,116)
  fr.alpha_composite(REFS[n].crop(box),(box[0]+16+dx,box[1]+20+dy))
  LOG.append(f'{name}/{n}_f{c}: full native head/ears/neck at {dx},{dy}, unscaled')
 elif n=='se' and ge is not None:
  box=(91,98,111,109);patch=REFS[n].crop(box);pe=eye(np.array(patch))
  if pe is not None:
   dx,dy=np.rint(ge-pe).astype(int);mask=a[:,:,3]>0
   fr.alpha_composite(patch,(int(dx),int(dy)));a=np.array(fr);a[~mask]=0;fr=Image.fromarray(a)
   LOG.append(f'{name}/{n}_f{c}: native sleepy eye/muzzle plate')
 fr=clean(clipped(fr));fr.save(path)

if __name__=='__main__':
 import sys
 for name in sys.argv[1:] or COUNTS:
  for n in NAMES:
   for c in range(COUNTS[name]):
    if c==0 or (name=='pop_out' and c==4) or (name=='dig' and c>=3):continue
    restore(name,n,c)
  board(name)
 (ROOT/'native_finish_log.txt').write_text('\n'.join(LOG)+'\n')
 print('Native head and face restoration',len(LOG))
