from repair import *
exec((OUT/'apply_repairs.py').read_text().split('# Idle')[0].split('from repair import *')[1])
oldlog=json.loads((OUT/'edits.json').read_text());LOG=[]
for m,v,inds,dy in [('walk','back',range(8),0),('ear_burst','back',[2],-1)]:
 for i in inds:
  p,a=load(m,v,i)
  left=[89,88,88,87,87,86,86,85,84,84]
  right=[103,104,104,105,105,106,106,107,108,108]
  for j,(l,r) in enumerate(zip(left,right)):
   y=125+j+dy
   # Hand-drawn paired shoulder silhouettes; keep the central plate pixels.
   a[y,80:l]=0;a[y,r+1:114]=0
   a[y,l]=COL[0];a[y,r]=COL[0]
   for x in range(l+1,91):
    if a[y,x,3]==0 or tuple(a[y,x])==COL[0]:a[y,x]=COL[4 if x<l+3 else 6]
   for x in range(103,r):
    if a[y,x,3]==0 or tuple(a[y,x])==COL[0]:a[y,x]=COL[4]
  save(p,a,'redrew stepped shoulder outline as an unbroken taper')
p,a=load('dig','side',2)
a[145,81]=COL[0];a[146,81]=COL[0];a[148,83:85]=COL[4]
save(p,a,'blended final grey tail-remnant texels into the haunch edge')
(OUT/'edits.json').write_text(json.dumps(oldlog+LOG,indent=2))
boards()
