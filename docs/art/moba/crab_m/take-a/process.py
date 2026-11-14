from pathlib import Path
import subprocess,sys,os,json
P=Path(__file__).resolve().parent
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def run(args,name):
 r=subprocess.run([sys.executable,'-B']+args,capture_output=True,text=True)
 (P/name).write_text(r.stdout+r.stderr)
 print(name+': '+r.stdout.strip())
 if r.returncode: raise RuntimeError(r.stderr)
run([str(P/'finish.py')],'finish.txt')
run([str(P/'defringe.py')],'defringe.txt')
def slicecheck(suffix):
 run(['tools/art/slice_grid.py',str(P/'sheet_finished.png'),str(P/'views'),'--canvas','192','--feet','160'],'slice'+suffix+'.txt')
 run(['tools/art/view_check.py',str(P/'views')],'view_check'+suffix+'.txt')
def lone():
 sys.path.insert(0,'tools/art')
 import sprite_director as sd
 return max(sd.lone_share(sd.load(P/'views'/f'{d}.png')) for d in sd.FACINGS)
slicecheck('-before')
before=lone()
if before>0.11:
 run([str(P/'despeckle.py')],'despeckle.txt')
 run([str(P/'defringe.py')],'defringe-after.txt')
slicecheck('')
after=lone()
(P/'lone.json').write_text(json.dumps({'before':before,'after':after,'passes':int(before>0.11)},indent=2))
run(['tools/art/sheet_judge.py',str(P/'views')],'sheet_judge.txt')
run([str(P/'audit.py')],'audit.txt')
print('LONE',before,after)
