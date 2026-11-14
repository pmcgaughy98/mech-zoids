import json,hashlib,shutil,copy
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/cobra_m/rigged-repair-v1-2026-11-10'
catalog=BASE/'art/model_catalog/catalog.json';data=json.loads(catalog.read_text());entry=next(e for e in data['entries'] if e['id']=='cobra');old=copy.deepcopy(entry)
before=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_cobra_remeshed_25k_20261111_character.glb');archived=OUT/'cobra-remeshed-rigged-input.glb'
if not archived.exists():shutil.copy2(before,archived)
assert hashlib.sha256(before.read_bytes()).digest()==hashlib.sha256(archived.read_bytes()).digest()
report=json.loads((OUT/'visual-and-deformation-check.json').read_text());verification=json.loads((OUT/'repair-verification.json').read_text());assert len(report['poses'])==3 and verification['after']['boundary_edges']==0
prefix='res://docs/art/moba/cobra_m/rigged-repair-v1-2026-11-10/'
fit=2.9/3.1133672
entry['display_model']=prefix+'cobra-rigged-local-repair-v1.glb'
entry['status']='Local topology repair v1: cracks/flaps fixed; 21-bone rig preserved. Surface/cap quality still needs restoration.'
entry['review_models']=[{'label':'INTACT BEFORE REMESH\nSingle-tail correction','path':'res://docs/art/moba/cobra_m/tail-correction-2026-11-10/cobra_front - single tail corrected.glb','display_scale':fit*report['intact_display_alignment']['uniform_scale']},{'label':'REMESHED + RIGGED\nDownloaded input','path':prefix+'cobra-remeshed-rigged-input.glb','display_scale':fit},{'label':'LOCAL REPAIR v1\nExisting rig preserved','path':entry['display_model'],'display_scale':fit}]
entry['review_views']={key:{'path':prefix+'review-'+view+'.png','kind':'Rendered comparison, not original generation input','versions':['intact single-tail correction','remeshed rigged download','local repair v1']} for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]}
entry['review_provenance']={'date':'2026-11-10','report':prefix+'repair-verification.json','intact_comparator_sha256':hashlib.sha256((BASE/'docs/art/moba/cobra_m/tail-correction-2026-11-10/cobra_front - single tail corrected.glb').read_bytes()).hexdigest(),'exact_meshy_upload_independently_verified':False,'rigged_input_sha256':verification['source_sha256'],'repaired_sha256':verification['output_sha256'],'scope':'Topology-only repair. No full surface restoration, authored animations or gameplay installation.'}
allowed={'display_model','status','review_models','review_views','review_provenance'}
assert {k:v for k,v in old.items() if k not in allowed}=={k:v for k,v in entry.items() if k not in allowed}
catalog.write_text(json.dumps(data,indent=2)+'\n')
for filename in ['diagnose.py','repair_cobra.py','review_cobra.py','package_review.py','register_review.py']:
 shutil.copy2(ROOT/filename,OUT/filename)
print('Registered cobra only. Original archive and four generation-sheet fields unchanged.')
