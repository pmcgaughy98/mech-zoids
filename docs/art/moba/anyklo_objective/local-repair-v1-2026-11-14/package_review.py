import json,hashlib,shutil,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'];assert p['joint_count']==37 and p['original_controls_tested']==37 and len(p['poses'])+len(p['no_surface_motion'])==41 and len(p['rendered_poses'])==19
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n);res=lambda p:'res://'+p.relative_to(BASE).as_posix();entry=json.loads((ROOT/'model-entry.json').read_text());review={}
for v in ['front','left','back','right']:
 im=Image.new('RGB',(1440,865),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'anyklo / '+v.upper()+' / tail mallet correction',font=font(28),fill='white')
 for col,(stage,label,color) in enumerate([('before','DOWNLOADED RIG / cyber tortoise','#f4c48b'),('after','anyklo / ALIGNED TAIL MALLET','#97e8b8')]):
  d.text((col*720+15,58),label,font=font(24),fill=color);im.paste(Image.open(OUT/f'{stage}-{v}.png').convert('RGB'),(col*720,100))
 d.text((18,830),'Same 37-joint rig and weights. Intact pre-remesh model unavailable; downloaded rig archived.',font=font(21),fill='#c5d8ed');dest=OUT/f'review-{v}.png';im.save(dest);review[v]={'path':res(dest),'kind':'Downloaded remeshed rig / locally aligned mallet; matched view and scale; no intact pre-remesh source located'}
im=Image.new('RGB',(1440,2330),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'anyklo / tail hammer before and after',font=font(30),fill='white')
for row,view in enumerate(['tail-back','tail-top','tail-three-quarter']):
 for col,(stage,label,color) in enumerate([('before','BEFORE','#f4c48b'),('after','AFTER','#97e8b8')]):
  y=60+row*755;d.text((col*720+18,y),label+' / '+view.upper(),font=font(24),fill=color);im.paste(Image.open(OUT/f'{stage}-{view}.png').convert('RGB'),(col*720,y+35))
im.save(OUT/'tail-before-after.png')
im=Image.new('RGB',(1200,1660),'#14212c');d=ImageDraw.Draw(im);d.text((14,10),'anyklo / 19 native joint poses',font=font(29),fill='white')
for i,label in enumerate(p['rendered_poses']):
 x=i%4*300;y=55+i//4*320;im.paste(Image.open(OUT/f'pose-{label}.png').convert('RGB').resize((300,290)),(x,y));d.text((x+7,y+292),label,font=font(18),fill='white')
im.save(OUT/'pose-proof.png')
entry['display_model']=res(Path(r['output']));entry['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));entry['status']='Renamed from cyber tortoise. Tail hammer lobes aligned into a crosswise mallet; 15 stray triangles removed. Four legs, head and capacitor armor retained. Original 37-joint rig, all skin weights and textures preserved.'
cfg=json.loads((ROOT/'input-audit.json').read_text());fit=min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7)
entry['review_models']=[{'label':'DOWNLOADED RIG\ncyber tortoise / before repair','path':entry['source_model']['path'],'display_scale':fit},{'label':'anyklo\nAligned mallet / same 37-joint rig','path':entry['display_model'],'display_scale':fit}];entry['review_views']=review
entry['review_provenance']={'date':'2026-11-14','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':37,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_available':False,'source_archive_scope':'Exact cyber tortoise rigged download, renamed in Workshop to anyklo. Intact pre-remesh GLB not located; no static proxy mislabeled as an original. Original generation PNGs preserved.','scope':r['scope']}
(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n')
for name in ['diagnose_model.py','render_model.py','render_tail.py','repair_model.py','audit_export.py','detail_pose_review.py','package_review.py','input-audit.json','face-components.json','model-entry.json','measure_panels.py','panel-measurements.json']:shutil.copy2(ROOT/name,OUT/name)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:
 catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));others=[x for x in cat['entries'] if x['id']!='anyklo'];assert len(others)==29
 if not (ROOT/'catalog-before-anyklo.json').exists():(ROOT/'catalog-before-anyklo.json').write_text(json.dumps(cat,indent=2)+'\n')
 if any(x['id']=='anyklo' for x in cat['entries']):cat['entries']=[entry if x['id']=='anyklo' else x for x in cat['entries']]
 else:cat['entries'].append(entry)
 assert len(cat['entries'])==30 and [x for x in cat['entries'] if x['id']!='anyklo']==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('anyklo package ready:',r['output_sha256'])
