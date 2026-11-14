p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();s=s.replace("'9a9aa6','b8b8c2','eeeef2']]);bm &= grey", "'9a9aa6','b8b8c2','eeeef2','26262e','141218']]);bm &= grey")
# Recolor only new connector fragments, same-ramp neighbour shade; feet/fixed parts locked.
pos=s.index('def boards(v,ref,frames):')
s=s[:pos]+'''def tidy_connectors(a,ll,parts,rig,pinned,cut,limit):
 from scipy.ndimage import label
 def pieces(im):
  out=[]
  for c in set(map(tuple,im[im[:,:,3]>0])):
   labs,num=label(np.all(im==c,axis=2)&(Y>=100)&(Y<=164),np.ones((3,3)));sizes=np.bincount(labs.ravel())
   for i in np.where((sizes>0)&(sizes<=2))[0]:
    if i:out.append((c,list(zip(*np.where(labs==i)))))
  return out
 immutable=(pinned[:,:,3]>0)&np.all(a==pinned,axis=2);immutable[:cut]=True
 for rr in rig:
  raw=b.shift(parts[rr['foot']]['foot'],*rr['delta']);immutable|=raw[:,:,3]>0
 mutable=(a[:,:,3]>0)&~immutable
 owner=np.full((192,192),'',dtype='<U2')
 for n in ['L3','L2','L1','R3','R2','R1']:owner[(ll[n][:,:,3]>0)&np.all(a==ll[n],axis=2)]=n
 mutable&=owner!=''
 ramps=[set(P[h] for h in ['141218','26262e','34343e','555562','7e7e8e','9a9aa6','b8b8c2','eeeef2']),set(P[h] for h in ['6a0a10','c41216','ee2c26','f85a4a'])]
 edits=[]
 for _ in range(100):
  old=pieces(a)
  if len(old)<=limit:break
  best=None
  for c,pts in old:
   if not all(mutable[y,x] for y,x in pts):continue
   ramp=next((r for r in ramps if c in r),{c});options=set()
   for y,x in pts:
    for yy in range(max(0,y-1),min(192,y+2)):
     for xx in range(max(0,x-1),min(192,x+2)):
      nc=tuple(a[yy,xx])
      if nc in ramp and nc!=c:options.add(nc)
   for nc in options:
    for y,x in pts:a[y,x]=nc
    gain=len(old)-len(pieces(a))
    for y,x in pts:a[y,x]=c
    if gain>0:
     key=(gain,-sum(abs(int(c[k])-int(nc[k])) for k in range(3)))
     if best is None or key>best[0]:best=(key,c,pts,nc)
  if best is None:break
  _,c,pts,nc=best
  for y,x in pts:a[y,x]=nc;ll[owner[y,x]][y,x]=nc
  edits.append(dict(pixels=[[int(x),int(y)] for y,x in pts],old=bytes(c[:3]).hex(),new=bytes(nc[:3]).hex()))
 return edits

''' +s[pos:]
s=s.replace("save(a,f'walk/frames/{v}_f{f}.png');save(pin", "protected=pin.copy();b.comp(protected,b.shift(sockets,0,dip));b.comp(protected,front)\n  from verify import specks\n  edits=tidy_connectors(a,ll,parts,[rr for rr in rig if rr['frame']==f],protected,cut,specks(ref)+2)\n  for n,layer in ll.items():save(layer,f'walk/layers/{v}_{n}_f{f}.png')\n  (R/f'walk/layers/{v}_join_edits_f{f}.json').write_text(json.dumps(edits))\n  save(a,f'walk/frames/{v}_f{f}.png');save(pin")
open(p,'w').write(s)
