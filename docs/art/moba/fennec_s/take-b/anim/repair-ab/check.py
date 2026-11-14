from repair import *
R=[]
for m,d in MOVES.items():
 for v in VIEWS:
  for p in files(m,v):
   a=np.array(Image.open(p).convert('RGBA'));op=a[:,:,3]>0;y,x=np.where(op);lab,k=ndi.label(op,np.ones((3,3)));sz=np.bincount(lab.ravel())[1:];holes=ndi.binary_fill_holes(op)&~op
   r=dict(move=m,frame=p.stem,bottom=int(max(y)),palette=all(tuple(c) in COL for c in a[op]),alpha=set(np.unique(a[:,:,3]).tolist())<={0,255},holes=int(holes.sum()),components=k,strays=int(sum(s for s in sz if s<=3)),edge=bool(op[0].any() or op[-1].any() or op[:,0].any() or op[:,-1].any()))
   R.append(r)
   if r['holes'] or r['strays'] or k>1:print(r)
(OUT/'checks.json').write_text(json.dumps(R,indent=2))
print('Total',len(R))
