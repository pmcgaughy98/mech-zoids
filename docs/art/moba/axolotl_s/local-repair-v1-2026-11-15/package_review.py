import json,sys,shutil,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');c=json.loads((ROOT/'batch-config.json').read_text());OUT=BASE/f"docs/art/moba/{c['folder']}/local-repair-v1-2026-11-15";e=json.loads((ROOT/'model-entry.json').read_text());r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'];assert len(p['poses'])+len(p['no_surface_motion'])==c['joints'] and len(p['rendered_poses'])==len(c['poses'])
res=lambda p:'res://'+p.relative_to(BASE).as_posix();font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n);review={}
for v in ['front','left','back','right']:
 im=Image.new('RGB',(1440,865),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),e['name']+' / '+v.upper()+' / local repair',font=font(28),fill='white')
 for col,(stage,label,color) in enumerate([('before','DOWNLOADED RIG / BEFORE REPAIR','#f4c48b'),('after',f"LOCAL REPAIR / SAME {c['joints']}-JOINT RIG",'#97e8b8')]):
  d.text((col*720+15,58),label,font=font(23),fill=color);im.paste(Image.open(OUT/f'{stage}-{v}.png').convert('RGB'),(col*720,100))
 d.text((18,830),f"{c['remove']} malformed triangles removed; {c['caps']} small gaps closed. Intact pre-remesh unavailable; raw rig archived.",font=font(20),fill='#c5d8ed');dest=OUT/f'review-{v}.png';im.save(dest);review[v]={'path':res(dest),'kind':'Exact downloaded remeshed rig / local repair; matched view and scale; intact pre-remesh GLB not located'}
if c['caps']:
 im=Image.new('RGB',(1440,795),'#14212c');d=ImageDraw.Draw(im)
 for col,(stage,label,color) in enumerate([('before','BEFORE / LOCAL GAP','#f4c48b'),('after','AFTER / LOCAL CLOSURE','#97e8b8')]):
  d.text((col*720+18,18),label,font=font(28),fill=color);im.paste(Image.open(OUT/f'{stage}-patch-1.png').convert('RGB'),(col*720,65))
 im.save(OUT/'before-after.png')
im=Image.new('RGB',(1200,55+math.ceil(len(p['rendered_poses'])/4)*320),'#14212c');d=ImageDraw.Draw(im);d.text((14,10),e['name']+' / native joint diagnostics',font=font(29),fill='white')
for i,label in enumerate(p['rendered_poses']):
 x=i%4*300;y=55+i//4*320;im.paste(Image.open(OUT/f'pose-{label}.png').convert('RGB').resize((300,290)),(x,y));d.text((x+7,y+292),label,font=font(19),fill='white')
im.save(OUT/'pose-proof.png')
cfg=json.loads((ROOT/'input-audit.json').read_text());fit=min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7);e['display_model']=res(Path(r['output']));e['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));e['status']=c['ui_status']
e['review_models']=[{'label':'DOWNLOADED RIG\nBefore local repair','path':e['source_model']['path'],'display_scale':fit},{'label':'LOCAL REPAIR\n'+f"Same {c['joints']}-joint rig and skin",'path':e['display_model'],'display_scale':fit}];e['review_views']=review;e['review_provenance']={'date':'2026-11-15','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':c['joints'],'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_available':False,'source_archive_scope':'Exact downloaded rig archived; intact pre-remesh GLB not located. Original generation PNGs are separate.','scope':r['scope']}
(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
for name in ['diagnose_model.py','render_model.py','repair_model.py','fix_patch_uv.py','audit_export.py','detail_pose_review.py','package_review.py','finalize_review.py','input-audit.json','face-components.json','model-entry.json','batch-config.json']:
 if (ROOT/name).exists():shutil.copy2(ROOT/name,OUT/name)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:
 catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));others=[x for x in cat['entries'] if x['id']!=c['id']];snapshot=ROOT/'catalog-before-model.json'
 if not snapshot.exists():snapshot.write_text(json.dumps(cat,indent=2)+'\n')
 if any(x['id']==c['id'] for x in cat['entries']):cat['entries']=[e if x['id']==c['id'] else x for x in cat['entries']]
 else:cat['entries'].append(e)
 assert [x for x in cat['entries'] if x['id']!=c['id']]==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(e['name'],'package ready',r['output_sha256'])
