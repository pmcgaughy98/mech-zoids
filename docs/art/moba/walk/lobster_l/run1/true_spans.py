p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read().replace("tail=b.piece(body,tailmask)","if v=='e':tailmask &= X<71\n if v=='ne':tailmask &= ~((X>=103)&(Y>=135))\n tail=b.piece(body,tailmask)")
s=s.replace("spans={'e':[(73,84)],'se':[(58,71),(76,86)],'ne':[(108,122),(124,137)]}[v]", "spans=[tuple(D[v][n]['span']) for n in ['R3','R2','R1']]")
open(p,'w').write(s)
p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/verify.py';s=open(p).read();s=s.replace("l,r,sy=foot['still_sole'];rows=[]", "native=load(R/f'source/{v}_{n}_native.png');yy,xx=np.where(native[:,:,3]>0);l,r=int(xx.min()),int(xx.max());rows=[]")
s=s.replace("deviations=[]\n   for x", "bound=int(np.where(body[:,:,3]>0)[0].max());valid_rows=[y if y is not None else bound for y in rows]\n   deviations=[]\n   for x")
s=s.replace("if len(yy) and all(y is not None for y in rows):deviations.append(float(yy.max()-np.interp(x,[l-1,r+1],rows)))", "if len(yy):deviations.append(float(yy.max()-np.interp(x,[l-1,r+1],valid_rows)))")
s=s.replace("'outside_rows':rows,'max_below_line'", "'outside_rows':rows,'transparent_outside_uses_conservative_body_bound':bound,'max_below_line'")
open(p,'w').write(s)
