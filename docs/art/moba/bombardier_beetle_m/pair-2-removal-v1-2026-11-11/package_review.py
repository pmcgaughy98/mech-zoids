from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/bombardier_beetle_m/pair-2-removal-v1-2026-11-11'
v=json.loads((OUT/'repair-verification.json').read_text());check=json.loads((OUT/'visual-deformation-check.json').read_text());audit=json.loads((OUT/'export-topology-audit.json').read_text())
assert check['tested_sha256']==v['output_sha256']==audit['sha256']==hashlib.sha256((OUT/'bombardier-beetle-six-legs-rigged-v1.glb').read_bytes()).hexdigest()
assert len(check['poses'])==10 and check['joint_count']==64
assert max(p['uv_split_seam_gap_m'] for p in check['poses'])<1e-5
assert all(p['max_displacement_m']<1e-6 for p in check['poses'] if p['label'].startswith('removed-'))
assert audit['boundary_edges']==audit['over_shared_edges']==audit['collapsed']==0
archive=OUT/'beetle-unrepaired-rigged-input.glb'
if not archive.exists():shutil.copy2(v['source_rig'],archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==v['source_rig_sha256']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for view in ['front','side','right','back','underside','top','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');dr=ImageDraw.Draw(canvas)
 for i,(version,label) in enumerate([('intact','INTACT QUALITY / extra-pair archive'),('before','DOWNLOADED RIG / eight walking legs'),('after','REPAIRED / PAIR 2 REMOVED')]):
  canvas.paste(Image.open(OUT/f'{version}-{view}.png').convert('RGB'),(i*720,65));dr.text((i*720+14,15),label,font=font,fill='white')
 dr.text((15,790),'BOMBARDIER BEETLE / '+view.upper()+' / archive quality reference does not approve extra legs',font=font,fill='white');canvas.save(OUT/f'review-{view}.png')
canvas=Image.new('RGB',(1440,790),'#17202a');dr=ImageDraw.Draw(canvas)
for i,(version,label) in enumerate([('before','BEFORE / extra walking pair'),('after','AFTER / six walking legs, same skeleton')]):
 canvas.paste(Image.open(OUT/f'{version}-three-quarter.png').convert('RGB'),(i*720,55));dr.text((i*720+14,15),label,font=font,fill='white')
canvas.save(OUT/'beetle-before-after.png')
canvas=Image.new('RGB',(2160,1440),'#17202a');dr=ImageDraw.Draw(canvas)
for i,p in enumerate(check['poses'][:6]):
 im=Image.open(OUT/('pose-'+p['label']+'.png')).convert('RGB').resize((720,680));x=i%3*720;y=i//3*720;canvas.paste(im,(x,y+40));dr.text((x+12,y+8),p['label']+' / '+p['bone'],font=font,fill='white')
canvas.save(OUT/'six-leg-pose-proof.png')
canvas=Image.new('RGB',(1440,790),'#17202a');dr=ImageDraw.Draw(canvas)
for i,view in enumerate(['underside','side']):
 canvas.paste(Image.open(OUT/f'after-{view}.png').convert('RGB'),(i*720,55));dr.text((i*720+14,15),'SIX LEGS / '+view.upper()+' / pair 2 removed',font=font,fill='white')
canvas.save(OUT/'six-leg-anatomy-proof.png')
catalog=BASE/'art/model_catalog/catalog.json';data=json.loads(catalog.read_text());entry=next(e for e in data['entries'] if e['id']=='bombardier_beetle');prefix='res://docs/art/moba/bombardier_beetle_m/pair-2-removal-v1-2026-11-11/';fit=2.9/2.68278265
entry['display_model']=prefix+'bombardier-beetle-six-legs-rigged-v1.glb'
entry['status']='Walking pair 2 removed as selected: six walking legs. Four small folds repaired. Original 64-joint skeleton retained; socket weights adjusted locally.'
entry['review_models']=[{'label':'INTACT QUALITY ARCHIVE\nExtra pair is not approved','path':entry['source_model']['path'],'display_scale':fit*check['intact_alignment']['uniform_scale'],'display_basis':check['intact_alignment']['rotation_basis_godot']},{'label':'DOWNLOADED RIG\nEight walking legs','path':prefix+archive.name,'display_scale':fit},{'label':'REPAIRED / SIX LEGS\nOriginal 64-joint skeleton','path':entry['display_model'],'display_scale':fit}]
entry['review_views']={key:{'path':prefix+f'review-{view}.png','kind':'Rendered version comparison; original generation sheets preserved separately'} for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]}
entry['review_provenance']={'date':'2026-11-11','report':prefix+'repair-verification.json','joint_count':64,'rigged_input_sha256':v['source_rig_sha256'],'repaired_sha256':v['output_sha256'],'scope':'Local walking-pair-2 cut and socket finish plus four folded-triangle removals. Original skeleton/rest/binds and original surface attributes retained; residual removed-chain weights reassigned to existing body parent. No remesh or gameplay installation.'}
catalog.write_text(json.dumps(data,indent=2)+'\n')
for name in ['remove_pair_2.py','review_repair.py','package_review.py','audit_export.py','repair_folds.py']:shutil.copy2(ROOT/name,OUT/name)
for name in ['input-audit.json','joint-influence-regions.json']:shutil.copy2(ROOT/name,OUT/name)
shutil.copy2('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py',OUT/'diagnose.py')
shutil.copy2(BASE/'docs/art/moba/bombardier_beetle_m/input-review-2026-11-11/walking-pair-choice.png',OUT/'walking-pair-choice-BEFORE.png')
print('Beetle six-leg repair packaged; Workshop entry and version comparisons updated.')
