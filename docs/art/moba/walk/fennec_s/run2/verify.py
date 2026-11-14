import sys
sys.dont_write_bytecode=True
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R.parent/'run1/verify.py').read_text()
s=s.replace('import build as m','import frontback as m').replace("['e','se','ne']","['ne','e','s','n']").replace("{'e':131,'se':127,'ne':124}","{'e':131,'ne':124,'s':130,'n':122}").replace('fennec-trot35-run1','fennec-trot35-run2')
s=s.replace("ky,kx=np.where(knee[:,:,3]>0)","km=knee[:,:,3]>0; contamination=np.logical_or.reduce([np.all(knee[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['fff4d6','f0d27a','b8923a']]) if v=='e' else np.zeros_like(km); ky,kx=np.where(km&~contamination)")
s=s.replace("lines=['fennec-trot35-run2: native pixel audit.'", "lines=['fennec-trot35-run2: native pixel audit.','e RF/LF knee comparison excludes five native chest-shadow pixels accidentally extracted into each run1 knee; these are replaced by deepest violet, leaving the steel disc unchanged.'")
exec(compile(s,str(R/'verify_reused.py'),'exec'))
