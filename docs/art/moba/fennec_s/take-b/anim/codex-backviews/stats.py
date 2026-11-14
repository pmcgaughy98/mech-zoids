from finish import *
for name,N in COUNTS.items():
 print(name)
 for v in ['back','ne']:
  for i in range(N):
   a=np.array(Image.open(R/name/'frames'/f'{v}_f{i}.png'));m=a[:,:,3]>0;box=Image.fromarray(a).getbbox();y0=box[1]
   # widths per row from top down for identifying neck minimum
   widths=[]
   for y in range(y0+25,min(y0+54,161)):
    x=np.where(m[y])[0];widths.append((y,int(x[-1]-x[0]+1) if len(x) else 0))
   print(v,i,box,'widths',widths)
