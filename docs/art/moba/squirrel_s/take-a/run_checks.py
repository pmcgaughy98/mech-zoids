from pathlib import Path
import subprocess,sys,os,json
P=Path(__file__).resolve().parent
label=sys.argv[1] if len(sys.argv)>1 else ''
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for name in ['view_check','sheet_judge']:
 r=subprocess.run([sys.executable,'tools/art/'+name+'.py',str(P/'views')],text=True,capture_output=True,env=env)
 (P/(name+label+'.txt')).write_text(r.stdout+r.stderr)
 print(r.stdout+r.stderr)
sys.path.insert(0,'tools/art')
import sprite_director as sd
v=[sd.load(P/'views'/f'{d}.png') for d in sd.FACINGS]
(P/('lone'+label+'.json')).write_text(json.dumps({d:sd.lone_share(a) for d,a in zip(sd.FACINGS,v)},indent=2))
