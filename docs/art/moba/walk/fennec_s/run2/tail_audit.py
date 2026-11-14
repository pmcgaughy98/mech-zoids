import sys
sys.dont_write_bytecode=True
import frontback as m
import repair
for f in range(8):
 a=m.load(m.R/f'walk/frames/ne_f{f}.png');tail=m.load(m.R/'source/ne_tail.png');tail=m.b.shift(tail,0,int(f in [1,5]));bright=m.np.logical_or.reduce([m.np.all(tail[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['e0c8ff','a46bff','fff4d6','f0d27a','b8923a']]);bad=bright&m.np.any(a!=tail,axis=2);print(f,'covered tail light/gold',m.np.argwhere(bad).tolist())
