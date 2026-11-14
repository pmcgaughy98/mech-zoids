import json,sys,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/fennec_s/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text());assert a['passed'] and a['tested_sha256']==r['output_sha256']==poses['tested_sha256'] and len(poses['poses'])==19
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
src=Path(r['source']);archive=BASE/'art/model_catalog/sources'/src.name;assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
if archive.exists():assert hashlib.sha256(archive.read_bytes()).hexdigest()==r['source_sha256']
else:shutil.copy2(src,archive)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));e=next(e for e in cat['entries'] if e['id']=='fennec');review={};versions=[('intact','INTACT GENERATED QUALITY ARCHIVE','#c5d8ed'),('before','DOWNLOADED RIG / BEFORE REPAIR','#f4c48b'),('after','LOCAL REPAIR / SAME RIG AND WEIGHTS','#97e8b8')]
for key in ['front','left','back','right']:
 im=Image.new('RGB',(2160,865),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Fennec / '+key.upper()+' / quality and local repair',font=font(28),fill='white')
 for i,(v,label,color) in enumerate(versions):d.text((i*720+15,58),label,font=font(22),fill=color);im.paste(Image.open(OUT/f'{v}-{key}.png').convert('RGB'),(i*720,100))
 d.text((18,830),'Original sources/references preserved. Local triangle repair; original positions, skin, skeleton and textures.',font=font(22),fill='#c5d8ed');dest=OUT/f'review-{key}.png';im.save(dest);review[key]={'path':res(dest),'kind':'Intact generated quality archive / downloaded rig / local repair; matched view and scale'}
im=Image.new('RGB',(1440,1570),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Fennec / both local openings repaired',font=font(30),fill='white')
for row,idx in enumerate([1,2]):
 for col,(v,label) in enumerate([('before','BEFORE / OPEN FOLD'),('after','AFTER / CLOSED SURFACE')]):
  y=60+row*755;d.text((col*720+18,y),f'{label} / PATCH {idx}',font=font(25),fill='#f4c48b' if col==0 else '#97e8b8');im.paste(Image.open(OUT/f'{v}-patch-{idx}.png').convert('RGB'),(col*720,y+35))
im.save(OUT/'before-after.png')
im=Image.new('RGB',(1040,1490),'#14212c');d=ImageDraw.Draw(im);d.text((12,10),'Fennec / 19 native-joint diagnostics',font=font(24),fill='white')
for i,p in enumerate(poses['poses']):
 x=i%4*260;y=50+i//4*288;im.paste(Image.open(OUT/f'pose-{p["label"]}.png').convert('RGB').resize((260,260)),(x,y));d.text((x+7,y+263),'pose-'+p['label'],font=font(15),fill='white')
im.save(OUT/'pose-proof.png')
cfg=json.loads((ROOT/'input-audit.json').read_text());meta=json.loads((OUT/'intact-render-metadata.json').read_text());fit=min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7)
e['display_model']=res(Path(r['output']));e['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));e['status']='Two small gaps and 52 malformed triangles repaired. Four legs, two ears and one tail retained. Original 44-joint rig, all skin weights and textures unchanged.';e['review_models']=[{'label':'INTACT QUALITY ARCHIVE\nOriginal generated geometry','path':e['source_model']['path'],'display_scale':fit*meta['height_scale']},{'label':'DOWNLOADED RIG\nLocal gaps and folds','path':res(archive),'display_scale':fit},{'label':'LOCAL REPAIR\nSame 44-joint rig and skin','path':res(Path(r['output'])),'display_scale':fit}];e['review_views']=review;e['review_provenance']={'date':'2026-11-13','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':44,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_available':True,'source_archive_scope':'Intact generated quality archive; exact historical Meshy upload not independently verified.','scope':r['scope']+' All 23,720 healthy main-body source faces retained. No gameplay replacement.'};(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
for f in ['diagnose_model.py','render_model.py','repair_model.py','audit_export.py','detail_pose_review.py','package_review.py','input-audit.json','face-components.json']:shutil.copy2(ROOT/f,OUT/f)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:
 latest=json.loads(catpath.read_text(encoding='utf-8'));other=[x for x in latest['entries'] if x['id']!='fennec'];latest['entries']=[e if x['id']=='fennec' else x for x in latest['entries']];assert [x for x in latest['entries'] if x['id']!='fennec']==other;catpath.write_text(json.dumps(latest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Fennec repair published; other entries preserved.')
print('Final SHA256',r['output_sha256'])
