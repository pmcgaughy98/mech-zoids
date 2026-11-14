from pathlib import Path
ROOT=Path(__file__).parent
s=(ROOT/'review_repair.py').read_text()
start=s.index(" for name,offset in [('front'");end=s.index(" if version=='after':",start)
s=s[:start]+" for side,label in [(-1,'left'),(1,'right')]:shot(version+'-eye-'+label,(side*.60,-1.95,1.23),(side*6,-3,1),1.15)\n"+s[end:]
start=s.index(" if version=='after':");s=s[:start]+"\nprint('Both eye close-ups rendered for all three versions.',flush=True)\n"
exec(compile(s,'chameleon_eye_closeups','exec'))
