from repair import *
for m,d in MOVES.items():
 for v in VIEWS:
  for p in files(m,v):
   i=int(p.stem.split('_f')[1]);n=len(files(m,v));locked=(i==0 and m not in ['walk','pop_out']) or (i==n-1 and m in ['idle','sand_kick','ear_burst','sonic_boom','pop_out'])
   if locked:continue
   a=np.array(Image.open(p));mask=a[:,:,3]>0;above=np.roll(mask,1,axis=0);edge=mask&~above
   runs=[]
   for y in range(122,155):
    lab,k=ndi.label(edge[y]);
    for j in range(1,k+1):
     x=np.where(lab==j)[0]
     if len(x)>=5:runs.append((y,int(x[0]),int(x[-1])))
   if runs:print(m,v,i,runs)
