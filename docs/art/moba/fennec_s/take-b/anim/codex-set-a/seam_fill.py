from finish import *
# Native collar/chest at the same translation as the approved head joins it to the generated torso.
for name in ['walk','sand_kick']:
 for n in NAMES:
  ref=np.array(approved(n))
  for c in range(COUNTS[name]):
   if name=='sand_kick' and c in [0,5]:continue
   p=ROOT/name/'frames'/f'{n}_f{c}.png';im=Image.open(p).convert('RGBA');a=np.array(im)
   # Native eye location gives exact head translation after polish.
   def eyes(arr):
    g=(arr[:,:,1]>180)&(arr[:,:,0]<100)&(arr[:,:,3]>0); yy,xx=np.where(g);return np.array([xx.mean(),yy.mean()])
   if n!='back':
    if not ((a[:,:,1]>180)&(a[:,:,0]<100)&(a[:,:,3]>0)).any():continue
    dx,dy=np.rint(eyes(a)-eyes(ref)).astype(int)
   else:dx,dy=0,(0 if name=='walk' else [0,4,8,0,5,0][c])
   box={'front':(76,107,85,120),'side':(96,105,105,120),'back':(73,105,87,120)}[n]
   native=REFS[n].crop(box);im.alpha_composite(native,(box[0]+16+int(dx),box[1]+20+int(dy)))
   clean(im).save(p)


