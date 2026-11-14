from finish import *
for v,centres in [('back',[83,107]),('ne',[111,100])]:
 print(v)
 for i in range(8):
  a=np.array(Image.open(R/'walk/frames'/f'{v}_f{i}.png'));m=a[:,:,3]>0
  print(i,[160-int(np.where(m[:,x])[0].max()) for x in centres])
