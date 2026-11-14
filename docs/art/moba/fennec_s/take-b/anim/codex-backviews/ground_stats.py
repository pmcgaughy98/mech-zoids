from finish import *
for name,N in COUNTS.items():
 for v in ['back','ne']:
  print(name,v)
  for i in range(N):
   a=np.array(Image.open(R/name/'frames'/f'{v}_f{i}.png'));m=a[:,:,3]>0;x=np.where(m[160])[0]
   print(i,'bbox',Image.fromarray(a).getbbox(),'holes',int((ndi.binary_fill_holes(m)&~m).sum()),'ground',x.tolist())
