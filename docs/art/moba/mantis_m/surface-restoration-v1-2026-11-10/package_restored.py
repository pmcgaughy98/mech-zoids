from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/mantis_m/surface-restoration-v1-2026-11-10';ROOT=Path(__file__).parent;font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
v=json.loads((OUT/'rig-transfer-verification.json').read_text());check=json.loads((OUT/'visual-rig-check.json').read_text());audit=json.loads((OUT/'export-topology-audit.json').read_text());assert check['sha256']==v['output_sha256'];assert audit['boundary_edges']==0 and audit['over_shared_edges']==0;assert len(check['poses'])==8 and max(p['uv_split_seam_gap_m'] for p in check['poses'])<1e-5
assert hashlib.sha256((OUT/'mantis-restored-six-limbs-rigged-v1.glb').read_bytes()).hexdigest()==check['sha256']
surface=json.loads((OUT/'surface-report.json').read_text())
if 'source_to_proxy_centroid_distance_99pct' in surface:surface['source_to_proxy_surface_distance_99pct']=surface.pop('source_to_proxy_centroid_distance_99pct')
(OUT/'surface-report.json').write_text(json.dumps(surface,indent=2))
archive=OUT/'mantis-damaged-rigged-input.glb'
if not archive.exists():shutil.copy2(v['source_rig'],archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==v['source_rig_sha256']
canvas=Image.new('RGB',(1440,790),'#17202a');dr=ImageDraw.Draw(canvas)
for i,(version,label) in enumerate([('before','DOWNLOADED RIG / damaged surface'),('after','RESTORED SURFACE / same 44-joint rig')]):canvas.paste(Image.open(OUT/f'{version}-three-quarter.png').convert('RGB'),(i*720,55));dr.text((i*720+15,15),label,font=font,fill='white')
canvas.save(OUT/'mantis-before-after.png')
for view in ['front','side','right','back','underside','top','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');dr=ImageDraw.Draw(canvas)
 for i,(version,label) in enumerate([('intact','ORIGINAL QUALITY / extra-limb archive'),('before','DOWNLOADED RIG / extra walking pair'),('after','RESTORED / WALKING PAIR 2 REMOVED')]):canvas.paste(Image.open(OUT/f'{version}-{view}.png').convert('RGB'),(720*i,65));dr.text((720*i+14,15),label,font=font,fill='white')
 dr.text((15,790),'MANTIS / '+view.upper()+' / archive quality reference does not approve extra limbs',font=font,fill='white');canvas.save(OUT/f'review-{view}.png')
canvas=Image.new('RGB',(1440,1440),'#17202a');dr=ImageDraw.Draw(canvas)
for i,bone in enumerate(['Bone_026','Bone_031','Bone_035','Bone_037']):
 image=Image.open(OUT/f'pose-{bone}.png').convert('RGB').resize((720,680));canvas.paste(image,((i%2)*720,(i//2)*720+40));dr.text(((i%2)*720+15,(i//2)*720+10),bone+' / native joint test',font=font,fill='white')
canvas.save(OUT/'leg-pose-proof.png')
catalog=BASE/'art/model_catalog/catalog.json';data=json.loads(catalog.read_text());entry=next(e for e in data['entries'] if e['id']=='mantis');prefix='res://docs/art/moba/mantis_m/surface-restoration-v1-2026-11-10/';fit=2.9/2.2797794
entry['display_model']=prefix+'mantis-restored-six-limbs-rigged-v1.glb';entry['status']='Surface restored; walking pair 2 removed as selected. Four walking legs + two scythes; original 44-joint skeleton retained, weights transferred. High-detail review; optimisation pending.'
entry['review_models']=[{'label':'INTACT QUALITY ARCHIVE\nExtra limbs are not approved','path':entry['source_model']['path'],'display_scale':fit*check['intact_display_scale']},{'label':'DOWNLOADED RIG\nExtra walking pair / damage','path':prefix+'mantis-damaged-rigged-input.glb','display_scale':fit},{'label':'RESTORED / PAIR 2 REMOVED\nOriginal 44-joint skeleton','path':entry['display_model'],'display_scale':fit}]
entry['review_views']={key:{'path':prefix+f'review-{view}.png','kind':'Rendered version comparison; original generation sheets preserved separately'} for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]}
entry['review_provenance']={'date':'2026-11-10','report':prefix+'rig-transfer-verification.json','joint_count':44,'rigged_input_sha256':v['source_rig_sha256'],'repaired_sha256':v['output_sha256'],'scope':'High-detail original surface restored with accepted six-limb cuts. Original Meshy skeleton/binds retained, weights transferred; not an optimised gameplay replacement.'}
catalog.write_text(json.dumps(data,indent=2)+'\n')
for name in ['export_cut_mask.py','restore_surface.py','bind_restored.py','review_restored.py','package_restored.py','extra_leg_tests.py','audit_export.py']:shutil.copy2(ROOT/name,OUT/name)
shutil.copy2(ROOT/'accepted-cut-mask.npz',OUT/'accepted-cut-mask.npz');shutil.copy2('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py',OUT/'diagnose.py')
print('Mantis restoration packaged and Workshop review registered.')
