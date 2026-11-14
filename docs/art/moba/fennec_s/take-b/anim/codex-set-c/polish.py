"""Adapted from set A polish.py and set B polish.py: native identity restoration."""
from finish import *
LOG=[]
HEAD_BOTTOM={'se':109,'ne':107}
COLLAR={'se':(85,106,95,119),'ne':(84,104,97,115)}
def eyes(a):
 g=(a[:,:,1]>180)&(a[:,:,0]<100)&(a[:,:,3]>0);y,x=np.where(g)
 return np.array([x.mean(),y.mean()]) if len(x) else None

def head_delta(name,n,c,a):
 if name=='walk':return (0,0)
 if n=='se':
  p=eyes(a);q=eyes(np.array(approved(n)))
  if p is not None:return tuple(np.clip(np.rint(p-q),[-8,-8],[8,12]).astype(int))
 if n=='ne':return (0,int(np.clip(Image.fromarray(a).getbbox()[1]-approved(n).getbbox()[1],-8,16)))
 return (0,{'sand_kick':[0,3,8,-2,4,0],'ear_burst':[0,3,-1,-2,2,0],'sonic_boom':[0,0,10,10,-2,3,2,0]}[name][c])

def native_head(fr,n,dx,dy):
 a=np.array(fr);end=HEAD_BOTTOM[n]+20;yy,xx=np.indices(a.shape[:2]);a[(yy<end+dy)&((yy<122+dy)|(xx>=100+dx))]=0
 p=np.array(approved(n));p[end:]=0;fr=Image.fromarray(a);fr.alpha_composite(Image.fromarray(p),(int(dx),int(dy)))
 box=COLLAR[n];fr.alpha_composite(REFS[n].crop(box),(box[0]+16+int(dx),box[1]+20+int(dy)))
 return clean(fr)

for name,N in COUNTS.items():
 if name=='idle' or not (ROOT/name/'sheet_raw.png').exists():continue
 for n in NAMES:
  for c in range(N):
   if name!='walk' and c in [0,N-1]:continue
   path=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr)
   full=name in ['walk','sand_kick'] or (name=='ear_burst' and c==2) or (name=='sonic_boom' and c in [1,6])
   dx,dy=head_delta(name,n,c,a)
   if full:
    fr=native_head(fr,n,dx,dy);LOG.append(f'{name}/{n}_f{c}: native complete head, ears, face and collar translated {dx},{dy}')
   elif n=='se' and not ((name=='ear_burst' and c==3) or (name=='sonic_boom' and c==4)):
    # Half-closed native eye/muzzle plate, clipped to the generated posed head.
    box=(85,96,112,110);patch=REFS[n].crop(box);g=eyes(a);q=eyes(np.array(patch))
    if g is not None and q is not None:
     x,y=np.rint(g-q).astype(int);mask=a[:,:,3]>0;fr.alpha_composite(patch,(int(x),int(y)));b=np.array(fr);b[~mask]=0;fr=clean(Image.fromarray(b));LOG.append(f'{name}/{n}_f{c}: native sleepy face at {x},{y}')
   if n=='ne' and ((name=='ear_burst' and c==3) or (name=='sonic_boom' and c==4)):
    # Rear release: retain full native ear/head dimensions, pitched forward as one rigid plate.
    b=np.array(fr);yy,xx=np.indices(b.shape[:2]);b[(yy<134)&((yy<123)|(xx>=102))]=0;fr=Image.fromarray(b)
    patch=REFS[n].crop((68,66,110,108));rot=patch.rotate(-10,resample=Image.Resampling.NEAREST,expand=True)
    x=round(88-(rot.width-patch.width)/2);y=round(84-(rot.height-patch.height)/2)
    fr.alpha_composite(rot,(x,y));box=(75,105,103,127);fr.alpha_composite(REFS[n].crop(box),(box[0]+20,box[1]+18));fr=clean(fr)
    LOG.append(f'{name}/{n}_f{c}: native full-size rear head/ears rigid -10deg; forward thrust')
   fr.save(path)
(ROOT/'native_finish_log.txt').write_text('\n'.join(LOG)+'\n')
