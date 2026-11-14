p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();s=s.replace("sockets=b.piece(ref,bm);save(sockets,f'source/{v}_sockets.png')", """sockets=b.piece(ref,bm)
 # Native fixed socket backs, including the original dark rim above each
 # moving band, belong to the joint, not to the trunk underside.
 jointbacks={'e':[(73,131,86,137),(93,133,106,139),(111,132,124,138)],'se':[(57,96,68,102),(63,112,77,118),(77,122,91,129)],'ne':[(106,115,120,122),(122,107,135,112),(133,98,144,103)]}
 for box in jointbacks[v]:
  mm=rect(*box)&(ref[:,:,3]>0)&~cm
  b.comp(sockets,b.piece(ref,mm));body[mm]=0
 # The complete segmented tail is a separate pinned source; its shape is not
 # part of the body's belly-line test. It follows the same dip, never a lag.
 tailmask={'e':b.mask([(32,128),(46,120),(60,119),(66,113),(73,113),(73,132),(71,140),(75,146),(70,149),(38,149),(31,141)]),
 'se':b.mask([(46,69),(58,65),(67,68),(72,74),(80,79),(85,88),(80,96),(72,99),(64,95),(60,87),(54,84),(49,78)]),
 'ne':b.mask([(42,141),(54,132),(64,128),(74,124),(79,116),(88,112),(96,116),(103,127),(105,140),(103,151),(95,160),(59,162),(43,156)])}[v]
 tail=b.piece(body,tailmask);body[tailmask]=0;save(tail,f'source/{v}_tail.png')
 # Remove only reconstruction below the two specifically reviewed belly
 # corners (not native plate paint). Preserve the native join foreground.
 if v in ['se','ne']:
  spans={'se':[(76,86)],'ne':[(108,122),(124,137)]}[v]
  for l,r in spans:
   ly=np.where(body[:,l-1,3]>0)[0];ry=np.where(body[:,r+1,3]>0)[0]
   if len(ly) and len(ry):
    for xx in range(l,r+1):
     limit=np.interp(xx,[l-1,r+1],[ly.max(),ry.max()])+1
     body[(Y[:,xx]>limit)&fill[:,xx],xx]=0
 save(sockets,f'source/{v}_sockets.png')""")
s=s.replace("return ref,parts,body,fg,sockets", "return ref,parts,body,fg,sockets,tail")
s=s.replace("ref,parts,body,fg,sockets=sources(v)","ref,parts,body,fg,sockets,tail=sources(v)")
s=s.replace("b.comp(a,pin);b.comp(a,b.shift(sockets,0,dip))", "b.comp(a,b.shift(tail,0,dip));b.comp(a,pin);b.comp(a,b.shift(sockets,0,dip))")
s=s.replace("protected=pin.copy();b.comp(protected", "protected=pin.copy();b.comp(protected,b.shift(tail,0,dip));b.comp(protected")
s=s.replace("save(pin,f'walk/layers/{v}_body_f{f}.png');", "save(pin,f'walk/layers/{v}_body_f{f}.png');save(b.shift(tail,0,dip),f'walk/layers/{v}_tail_f{f}.png');")
open(p,'w').write(s)
