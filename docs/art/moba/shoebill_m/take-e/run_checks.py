from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
import json, subprocess, sys
P=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/take-e')
def run(tool,args,name):
 r=subprocess.run([sys.executable,'-B',tool,*args],capture_output=True,text=True)
 (P/name).write_text(r.stdout+r.stderr)
 print(r.stdout+r.stderr)
 if r.returncode: raise RuntimeError(r.returncode)
run('tools/art/view_check.py',[str(P/'views')],'view_check-before.txt')
sys.path.insert(0,'tools/art')
import sprite_director as sd
before=max(sd.lone_share(sd.load(P/'views'/f'{d}.png')) for d in sd.FACINGS)
if before>0.11:
 a=np.array(Image.open(P/'sheet_finished.png').convert('RGBA')); out=a.copy(); count=0
 lens={(255,225,74),(255,251,208)}
 h,w=a.shape[:2]
 for y in range(h):
  for x in range(w):
   if a[y,x,3]==0 or tuple(a[y,x,:3]) in lens: continue
   ns=[tuple(a[yy,xx]) for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if 0<=yy<h and 0<=xx<w and a[yy,xx,3]>0]
   if not ns or any(np.abs(a[y,x,:3].astype(int)-np.array(n[:3],int)).sum()<30 for n in ns): continue
   out[y,x]=Counter(ns).most_common(1)[0][0];count+=1
 Image.fromarray(out).save(P/'sheet_finished.png')
 # Recheck the rim after the single despeckle pass without a second despeckle.
 import importlib.util
 spec=importlib.util.spec_from_file_location('defringe',P/'defringe.py'); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 out,bad,pale,ink=mod.clean(out);Image.fromarray(out).save(P/'sheet_finished.png')
 run('tools/art/slice_grid.py',[str(P/'sheet_finished.png'),str(P/'views'),'--canvas','160','--feet','140'],'slice_grid.txt')
 after=max(sd.lone_share(sd.load(P/'views'/f'{d}.png')) for d in sd.FACINGS)
 (P/'despeckle.json').write_text(json.dumps({'passes':1,'before':before,'after':after,'repainted':count,'lens_colours_preserved':True,'post_pass_rim_cleanup':{'plum':bad,'pale':pale,'ink':ink}},indent=2))
 print('lone before',before,'after',after,'changed',count)
run('tools/art/view_check.py',[str(P/'views')],'view_check.txt')
run('tools/art/sheet_judge.py',[str(P/'views')],'sheet_judge.txt')
run(str(P/'audit.py'),[],'audit.txt')
