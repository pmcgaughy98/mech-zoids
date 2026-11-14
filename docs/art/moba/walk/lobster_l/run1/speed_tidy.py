p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();s=s.replace("edits=[]\n for _ in range(100):", """def count_colour(c):
  labs,num=label(np.all(a[100:165]==c,axis=2),np.ones((3,3)));sz=np.bincount(labs.ravel())[1:]
  return int(((sz>0)&(sz<=2)).sum())
 edits=[]
 for _ in range(100):""")
s=s.replace("for nc in options:\n    for y,x in pts:a[y,x]=nc\n    gain=len(old)-len(pieces(a))", "for nc in options:\n    before=count_colour(c)+count_colour(nc)\n    for y,x in pts:a[y,x]=nc\n    gain=before-count_colour(c)-count_colour(nc)")
open(p,'w').write(s)
