"""Adapted set B native grey joint restoration, excluding neighboring chest colours."""
from finish import *
LOG=[]
BOXES={'se':[(84,112,92,120),(77,125,84,132)],'ne':[(96,111,101,118),(92,123,99,131)]}
for name,N in COUNTS.items():
 if name=='idle' or not (ROOT/name/'sheet_raw.png').exists():continue
 for n in NAMES:
  templates=[]
  for box in BOXES[n]:
   a=np.array(REFS[n].crop(box));g=np.all(a[:,:,:3]==PAL[5],2)&(a[:,:,3]>0);y,x=np.where(g)
   keep=np.isin(a[:,:,0],[61,157,214])&(a[:,:,3]>0);a[~keep]=0
   if len(x):templates.append((Image.fromarray(a),x.mean(),y.mean(),len(x)))
  for c in range(N):
   if name!='walk' and c in [0,N-1]:continue
   p=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(p).convert('RGBA');a=np.array(fr);m=a[:,:,3]>0
   g=np.all(a[:,:,:3]==PAL[5],2)&m;g[:130]=False;g[153:]=False;lab,k=ndi.label(g)
   for j in range(1,k+1):
    y,x=np.where(lab==j)
    if len(x)<5 or len(x)>40 or y.max()-y.min()>9:continue
    patch,cx,cy,sz=min(templates,key=lambda t:abs(t[3]-len(x)));dx,dy=round(x.mean()-cx),round(y.mean()-cy);fr.alpha_composite(patch,(dx,dy));a=np.array(fr);a[~m]=0;fr=Image.fromarray(a);LOG.append(f'{name}/{n}_f{c}: native disc at {dx},{dy}')
   clean(fr).save(p)
(ROOT/'detail_finish_log.txt').write_text('\n'.join(LOG)+'\n')
