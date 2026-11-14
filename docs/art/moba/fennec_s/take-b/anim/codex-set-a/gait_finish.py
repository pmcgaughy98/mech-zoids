from finish import *
# Rear projection: retain native short leg length and rigid native tail, but lift the tail clear of the ground.
# Feet have fixed planted coordinates. Opposite visible legs swing in alternating diagonal phases.
for c in range(8):
 p=ROOT/'walk/frames'/f'back_f{c}.png';im=Image.open(p).convert('RGBA');a=np.array(im);a[143:]=0;im=Image.fromarray(a)
 phases=([0,0,0,0,0,-2,-3,-1][c],[0,-2,-3,-1,0,0,0,0][c])
 for box,lift in zip([(62,110,77,135),(84,110,98,135)],phases):
  patch=REFS['back'].crop(box);im.alpha_composite(patch,(box[0]+16,box[1]+26+lift))
 tail=REFS['back'].crop((74,122,87,141));im.alpha_composite(tail,(90+[-1,0,1,0,-1,0,1,0][c],136))
 clean(im).save(p)

# Clean final seams and enclosed holes without changing exact still endpoints or the fixed native idle lower body.
for name,N in COUNTS.items():
 if name=='idle':continue
 for n in NAMES:
  for c in range(N):
   if name!='walk' and c in [0,N-1]:continue
   p=ROOT/name/'frames'/f'{n}_f{c}.png';im=Image.open(p).convert('RGBA');a=np.array(im);m=a[:,:,3]>0
   gap=np.zeros_like(m);gap[:,1:-1]=~m[:,1:-1]&m[:,:-2]&m[:,2:]
   # Only close long one-texel joins. Natural gaps between the legs remain open.
   for x in range(192):
    lab,k=ndi.label(gap[:,x])
    for j in range(1,k+1):
     yy=np.where(lab==j)[0]
     if len(yy)>=4:a[yy,x]=[20,18,24,255]
   clean(Image.fromarray(a)).save(p)

