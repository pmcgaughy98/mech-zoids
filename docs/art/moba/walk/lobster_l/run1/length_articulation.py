p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();key=" # A fixed ball covers the uppermost join. Knee band and lit edge remain native."
new=''' # Place the knee on the native two-link reach, choosing the closest integer
 # articulation that preserves the leg's projected length. The socket is fixed.
 root0=np.array(q['root'],float);k0=np.array([q['sole'][0],(ba+bb)/2]);ank0=np.array([q['sole'][0],ft]);root=root0+[0,dip];ank=ank0+[dx,dy]
 u0=np.linalg.norm(k0-root0);l0=np.linalg.norm(ank0-k0);best=None
 for ox in range(-8,9):
  for oy in range(-5,6):
   # Keep the band beneath the socket cap; overlapping shin rows are hidden
   # by the whole foot and the band, as a hinged short leg folds.
   if ba+oy<top+dip-2:continue
   kn=k0+[ox,oy];u=np.linalg.norm(kn-root);lo=np.linalg.norm(ank-kn);err=abs(u+lo-u0-l0)
   motion=(ox-kdx)**2+(oy-kdy)**2
   key=(max(0,err-.95)*1000+max(0,abs(u-u0)-1)*2+max(0,abs(lo-l0)-1)*2+motion*.15,err)
   if best is None or key<best[0]:best=(key,ox,oy)
 kdx,kdy=best[1:]
'''
s=s.replace(key,new+key);open(p,'w').write(s)
