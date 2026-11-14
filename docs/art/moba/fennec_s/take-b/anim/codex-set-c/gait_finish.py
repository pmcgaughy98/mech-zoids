"""Adapted from set A gait_finish.py: short native leg patches and fixed support coordinates."""
from finish import *
LOG=[]
# (native box, base vertical shift to put its pad at ground, diagonal pair)
LEGS={'se':[((100,120,110,139),2,1),((73,122,89,139),2,1),((89,119,100,141),0,0)],
      'ne':[((98,116,107,137),4,1),((86,122,99,138),3,0)]}
for n in NAMES:
 for c in range(8):
  p=ROOT/'walk'/'frames'/f'{n}_f{c}.png';fr=Image.open(p).convert('RGBA');a=np.array(fr)
  # Retain generated standing torso. Replace only lower leg silhouettes.
  a[151:]=0;fr=Image.fromarray(a)
  planted=[]
  for box,base,pair in LEGS[n]:
   phase=c if pair==0 else (c+4)%8
   # Fixed planted x/y; the swing uses a short rigid translation, never stretched limbs.
   dx=[0,0,0,0,0,1,2,1][phase];lift=[0,0,0,0,0,-2,-3,-1][phase]
   patch=REFS[n].crop(box);fr.alpha_composite(patch,(box[0]+16+dx,box[1]+20+base+lift))
   if phase<=3:planted.append([box[0]+16,160])
  clean(fr).save(p);LOG.append(dict(view=n,frame=c,native_leg_scale=1,planted_contacts=planted))
(ROOT/'gait_contacts.json').write_text(json.dumps(LOG,indent=2)+'\n')
