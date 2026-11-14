from pathlib import Path
import sys,subprocess,json
P=Path(__file__).resolve().parent
sys.path.insert(0,str(Path.cwd()/'tools/art'))
import sprite_director as sd
before=max(sd.lone_share(sd.load(P/'views'/f'{d}.png')) for d in sd.FACINGS)
r=subprocess.run([sys.executable,'tools/art/view_check.py',str(P/'views')],text=True,capture_output=True)
(P/'view-check-before.txt').write_text(r.stdout+r.stderr)
if before>.11:
 subprocess.run([sys.executable,str(P/'despeckle.py')],check=True)
 subprocess.run([sys.executable,str(P/'defringe.py')],check=True)
 subprocess.run([sys.executable,'tools/art/slice_grid.py',str(P/'sheet_finished.png'),str(P/'views'),'--canvas','192','--feet','160'],check=True)
after=max(sd.lone_share(sd.load(P/'views'/f'{d}.png')) for d in sd.FACINGS)
(P/'lone.json').write_text(json.dumps({'before':before,'after':after,'despeckle_passes':int(before>.11),'source_median_filter':9},indent=2))
for tool,name in [('view_check.py','view-check.txt'),('sheet_judge.py','sheet-judge.txt')]:
 r=subprocess.run([sys.executable,'tools/art/'+tool,str(P/'views')],text=True,capture_output=True)
 (P/name).write_text(r.stdout+r.stderr)
 print(r.stdout)
subprocess.run([sys.executable,str(P/'audit.py')],check=True)
