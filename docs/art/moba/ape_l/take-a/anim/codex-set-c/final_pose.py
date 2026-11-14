"""Final native endpoints and chest recovery, adapted from set A gems.py."""
from finish import *
for name,N in COUNTS.items():
 for n in NAMES:
  approved(n).save(ROOT/name/'frames'/f'{n}_f0.png')
  if name in ['chest_beat','hex_shield']:approved(n).save(ROOT/name/'frames'/f'{n}_f{N-1}.png')
  if name=='chest_beat':Image.open(ROOT/'idle'/'frames'/f'{n}_f1.png').save(ROOT/name/'frames'/f'{n}_f6.png')
print('Exact endpoints and recovery restored')
