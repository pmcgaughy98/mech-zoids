from repair import *
exec(open(str(OUT/'dump.py')).read().split('for args in')[0])
for i in [0,2,5,6]:dump('walk','side',i,(85,149,104,161))
for m,v,i in [('sand_kick','side',3),('dig','front',2),('dig','side',2),('dig','back',2)]:
 a=np.array(Image.open(files(m,v)[i]));op=a[:,:,3]>0;h=ndi.binary_fill_holes(op)&~op;print(m,v,i,'holes',[(int(x),int(y)) for y,x in zip(*np.where(h))])
