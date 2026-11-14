"""Take B finishing orchestration. Writes only beside this script."""
from pathlib import Path
import os, sys, subprocess, json, hashlib
P = Path(__file__).resolve().parent
REPO = Path('C:/Users/pmcga/dev/hollowtide')
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
def run(*args):
    result = subprocess.run([sys.executable, *map(str,args)], cwd=REPO, env=os.environ, capture_output=True, text=True)
    print(result.stdout + result.stderr)
    if result.returncode: raise RuntimeError(args)
def slice_sheet(label):
    result = subprocess.run([sys.executable, str(REPO/'tools/art/slice_grid.py'), str(P/'sheet_finished.png'), str(P/'views'), '--canvas','160','--feet','140'], cwd=REPO, env=os.environ, capture_output=True,text=True)
    (P/('slice'+label+'.txt')).write_text(result.stdout+result.stderr)
    print(result.stdout+result.stderr)
    if result.returncode: raise RuntimeError('slice')
run(P/'finish.py')
run(P/'defringe.py')
slice_sheet('-before')
run(P/'run_checks.py','-before')
before=json.loads((P/'lone-before.json').read_text())
if max(before.values()) > .11:
    run(P/'despeckle.py')
    run(P/'defringe.py')
    slice_sheet('')
run(P/'run_checks.py')
run(P/'audit.py')
(P/'generation.json').write_text(json.dumps({'images_generated':1,'tool':'built-in image_gen','prompt':'prompt-sheet.txt verbatim','reference':'refs/craft_drembit.png only','raw_sha256':hashlib.sha256((P/'sheet_raw.png').read_bytes()).hexdigest(),'tokens_used':None,'lone_before':max(before.values()),'lone_after':max(json.loads((P/'lone.json').read_text()).values())},indent=2))
