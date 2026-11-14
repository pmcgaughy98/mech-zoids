p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();start=s.index('  for l,r in spans:');end=s.index(" save(sockets",start)
block=s[start:end];s=s[:start]+"  for pass_no in range(4):\n"+'\n'.join(' '+line for line in block.splitlines())+'\n'+s[end:]
open(p,'w').write(s)
