from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/chameleon_m/local-repair-v1-2026-11-11'
v=json.loads((OUT/'repair-verification.json').read_text());check=json.loads((OUT/'visual-deformation-check.json').read_text());audit=json.loads((OUT/'export-topology-audit.json').read_text());assert audit['sha256']==v['output_sha256']
assert check['tested_sha256']==v['output_sha256']==hashlib.sha256((OUT/'chameleon-rigged-local-repair-v1.glb').read_bytes()).hexdigest()
assert len(check['poses'])==10 and check['joint_count']==51
assert max(p['uv_split_seam_gap_m'] for p in check['poses'])<1e-5
assert v['after']['boundary_edges']==v['after']['edges_over_two_faces']==0
archive=OUT/'chameleon-unrepaired-rigged-input.glb'
if not archive.exists():shutil.copy2(v['source'],archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==v['source_sha256']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for view in ['front','side','right','back','underside','top','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');dr=ImageDraw.Draw(canvas)
 for i,(version,label) in enumerate([('intact','INTACT ORIGINAL / before remesh'),('before','DOWNLOADED RIG / local defects'),('after','REPAIRED / original rig and weights')]):
  canvas.paste(Image.open(OUT/f'{version}-{view}.png').convert('RGB'),(i*720,65));dr.text((i*720+14,15),label,font=font,fill='white')
 dr.text((15,790),'CHAMELEON / '+view.upper()+' / matched framing; original generation sheets kept separately',font=font,fill='white');canvas.save(OUT/f'review-{view}.png')
canvas=Image.new('RGB',(1440,790),'#17202a');dr=ImageDraw.Draw(canvas)
for i,(version,label) in enumerate([('before','BEFORE / malformed folds and small gaps'),('after','AFTER / local closure; rig unchanged')]):
 canvas.paste(Image.open(OUT/f'{version}-patch-1.png').convert('RGB').crop((180,180,540,540)).resize((720,720)),(i*720,55));dr.text((i*720+14,15),label,font=font,fill='white')
canvas.save(OUT/'local-patch-before-after.png')
canvas=Image.new('RGB',(2160,1440),'#17202a');dr=ImageDraw.Draw(canvas)
for i,p in enumerate(check['poses'][:6]):
 im=Image.open(OUT/('pose-'+p['label']+'.png')).convert('RGB').resize((720,680));x=i%3*720;y=i//3*720;canvas.paste(im,(x,y+40));dr.text((x+12,y+8),p['label']+' / '+p['bone'],font=font,fill='white')
canvas.save(OUT/'rig-pose-proof.png')
catalog=BASE/'art/model_catalog/catalog.json';data=json.loads(catalog.read_text());entry=next(e for e in data['entries'] if e['id']=='chameleon');prefix='res://docs/art/moba/chameleon_m/local-repair-v1-2026-11-11/';fit=2.9/5.24628258
entry['display_model']=prefix+'chameleon-rigged-local-repair-v1.glb'
entry['status']='Four small gaps and malformed folds repaired. Four legs, two eyes, one segmented tail; original 51-joint rig and skin weights retained.'
entry['review_models']=[{'label':'INTACT ORIGINAL\nBefore remeshing','path':entry['source_model']['path'],'display_scale':fit*check['intact_alignment']['uniform_scale'],'display_basis':check['intact_alignment']['rotation_basis_godot']},{'label':'DOWNLOADED RIG\nLocal folds and gaps','path':prefix+archive.name,'display_scale':fit},{'label':'LOCAL REPAIR\nSame 51-joint rig and weights','path':entry['display_model'],'display_scale':fit}]
entry['review_views']={key:{'path':prefix+f'review-{view}.png','kind':'Rendered version comparison; original generation sheets preserved separately'} for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]}
entry['review_provenance']={'date':'2026-11-11','report':prefix+'repair-verification.json','joint_count':51,'rigged_input_sha256':v['source_sha256'],'repaired_sha256':v['output_sha256'],'scope':'Local triangle-index repair only. Original skeleton, weights, positions, normals, UVs and material/texture data retained byte-for-byte. No new vertices, materials, full-detail reconstruction or gameplay installation.'}
catalog.write_text(json.dumps(data,indent=2)+'\n')
for name in ['repair_topology.py','review_repair.py','review_eyes.py','package_review.py','analyze_repair.py','audit_export.py']:shutil.copy2(ROOT/name,OUT/name)
for name in ['input-audit.json','joint-influence-regions.json']:shutil.copy2(ROOT/name,OUT/name)
shutil.copy2('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py',OUT/'diagnose.py')
print('Chameleon local repair packaged; Workshop entry and comparisons updated.')
