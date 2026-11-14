p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();pos=s.index('def sources(v):')
s=s[:pos]+'''BALL={
'e':{'R3':[(75,133),(81,131),(85,134),(86,138),(84,141),(76,141),(73,138)],'R2':[(96,135),(101,134),(104,136),(105,141),(102,143),(95,142),(93,139)],'R1':[(114,135),(120,133),(123,136),(124,140),(121,142),(114,142),(111,139)]},
'se':{'R3':[(61,98),(65,97),(67,100),(66,104),(64,106),(59,104),(59,101)],'R2':[(67,113),(72,112),(75,115),(75,119),(73,123),(68,122),(64,119),(64,116)],'R1':[(81,124),(86,123),(90,126),(91,131),(87,134),(81,133),(77,130),(78,126)]},
'ne':{'R3':[(110,117),(115,116),(118,119),(119,123),(116,126),(110,126),(107,123),(107,120)],'R2':[(126,109),(131,108),(134,110),(135,114),(132,117),(126,116),(123,114),(123,111)],'R1':[(136,100),(140,99),(143,101),(143,104),(141,107),(136,106),(134,103)]}}
''' +s[pos:]
s=s.replace("cm=b.mask(CLAW[v])&(ref[:,:,3]>0)","cm=b.mask(CLAW[v])&(ref[:,:,3]>0)\n bm=np.logical_or.reduce([b.mask(p) for p in BALL[v].values()])\n grey=np.logical_or.reduce([np.all(ref==P[h],axis=2) for h in ['34343e','555562','7e7e8e','9a9aa6','b8b8c2','eeeef2']]);bm &= grey")
s=s.replace("m=(m&(Y<q['ft']))|fm", "m=((m&(Y<q['ft']))|fm)&~bm")
s=s.replace("body=b.piece(ref,~used&~cm)","body=b.piece(ref,~used&~cm&~bm)")
s=s.replace("save(body,f'source/{v}_body.png');save(fg", "sockets=b.piece(ref,bm);save(sockets,f'source/{v}_sockets.png')\n save(body,f'source/{v}_body.png');save(fg")
s=s.replace("return ref,parts,body,fg", "return ref,parts,body,fg,sockets")
s=s.replace("ref,parts,body,fg=sources(v)","ref,parts,body,fg,sockets=sources(v)")
s=s.replace("front=b.shift(fg,0,dip);b.comp(a,pin)","front=b.shift(fg,0,dip);b.comp(a,pin);b.comp(a,b.shift(sockets,0,dip))")
s=s.replace("save(pin,f'walk/layers/{v}_body_f{f}.png')", "save(pin,f'walk/layers/{v}_body_f{f}.png');save(b.shift(sockets,0,dip),f'walk/layers/{v}_sockets_f{f}.png')")
# Tighten only the traced back belly corner by one pixel; avoid blanket line cuts.
s=s.replace("save(body,f'source/{v}_body.png')", "\n if v=='e':body[146,73:79]=0\n save(body,f'source/{v}_body.png')")
open(p,'w').write(s)
