p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();s=s.replace("bm &= grey", "bm &= grey\n if v=='se':bm[122,67]=False;bm[123,68]=False")
s=s.replace("if v in ['se','ne']:\n  spans={'se':[(76,86)],'ne':[(108,122),(124,137)]}[v]", "if v in ['e','se','ne']:\n  spans={'e':[(73,84)],'se':[(58,71),(76,86)],'ne':[(108,122),(124,137)]}[v]")
open(p,'w').write(s)
