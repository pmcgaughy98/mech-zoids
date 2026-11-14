"""Adapted from set A details.py and set B final_pass.py: straight native tails and seated bases."""
from finish import *
LOG=[]
for name,N in COUNTS.items():
 if name=='idle':continue
 for n in NAMES:
  ref=np.array(approved(n))
  for c in range(N):
   if name!='walk' and c in [0,N-1]:continue
   p=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(p).convert('RGBA');a=np.array(fr)
   if name=='ear_burst':
    # Fixed native haunches, feet and grounded tail, as in set A.
    a[140:]=ref[140:];fr=Image.fromarray(a)
   else:
    # Tail rigidly translated as one native segmented piece; never bent or resized.
    box=(48,125,77,139) if n=='se' else (51,128,81,141)
    lift=-6 if name=='walk' else 0
    edge=93 if n=='se' else 97
    a[(np.indices(a.shape[:2])[1]<(85 if n=='se' else 88))&(np.indices(a.shape[:2])[0]>=145+lift)]=0
    fr=Image.fromarray(a);fr.alpha_composite(REFS[n].crop(box),(box[0]+16,box[1]+20+lift))
    # Native root/coupling joins the tail to the hip with the same segment geometry.
    root=(74,124,79,137) if n=='se' else (76,125,87,136)
    # Preserve the generated hip/coupling; overlay only the isolated native tail.
   clean(fr).save(p);LOG.append(f'{name}/{n}_f{c}: native straight tail'+('; fixed seated lower body' if name=='ear_burst' else ''))
(ROOT/'final_pass_log.txt').write_text('\n'.join(LOG)+'\n')
