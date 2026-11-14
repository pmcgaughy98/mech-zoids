p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read().replace("if v=='se':bm[122,67]=False;bm[123,68]=False", "if v=='se':bm &= ~rect(63,120,68,123)")
open(p,'w').write(s)
