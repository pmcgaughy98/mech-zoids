import json,sys,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/falcon_m/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text());assert a['passed'] and a['tested_sha256']==r['output_sha256']==poses['tested_sha256'] and len(poses['poses'])==24
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
src=Path(r['source']);archive=BASE/'art/model_catalog/sources'/src.name;assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
if archive.exists():assert hashlib.sha256(archive.read_bytes()).hexdigest()==r['source_sha256']
else:shutil.copy2(src,archive)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));e=next(e for e in cat['entries'] if e['id']=='falcon');review={};versions=[('intact','INTACT QUALITY / EXTRA TOES UNAPPROVED','#c5d8ed'),('before','DOWNLOADED RIG / FIVE TOES PER FOOT','#f4c48b'),('after','LOCAL REPAIR / FOUR TOES PER FOOT','#97e8b8')]
for key in ['front','left','back','right']:
 im=Image.new('RGB',(2160,865),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Falcon / '+key.upper()+' / quality and local repair',font=font(28),fill='white')
 for i,(v,label,color) in enumerate(versions):d.text((i*720+15,58),label,font=font(22),fill=color);im.paste(Image.open(OUT/f'{v}-{key}.png').convert('RGB'),(i*720,100))
 d.text((18,830),'Original sources/references preserved. Extra outer rear toes removed; original rig, local weight cleanup.',font=font(22),fill='#c5d8ed');dest=OUT/f'review-{key}.png';im.save(dest);review[key]={'path':res(dest),'kind':'Intact generated quality archive / downloaded rig / local repair; matched view and scale'}
im=Image.new('RGB',(1440,810),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Falcon / chest opening repaired',font=font(30),fill='white')
for col,(v,label) in enumerate([('before','BEFORE / OPEN FOLD'),('after','AFTER / CLOSED SURFACE')]):d.text((col*720+18,58),label,font=font(26),fill='#f4c48b' if col==0 else '#97e8b8');im.paste(Image.open(OUT/f'{v}-patch-1.png').convert('RGB'),(col*720,90))
im.save(OUT/'before-after.png')
im=Image.new('RGB',(1440,1570),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Falcon / outer rear toe 1 removed on both feet',font=font(30),fill='white')
for row,suffix in enumerate(['feet','feet-left']):
 for col,(v,label) in enumerate([('before','BEFORE / FIVE TOES'),('after','AFTER / THREE FRONT + ONE REAR')]):
  y=60+row*755;d.text((col*720+18,y),label,font=font(25),fill='#f4c48b' if col==0 else '#97e8b8');im.paste(Image.open(OUT/f'{v}-{suffix}.png').convert('RGB'),(col*720,y+35))
im.save(OUT/'feet-before-after.png')
im=Image.new('RGB',(1440,1570),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Falcon / both retained foot pads and closed toe mounts',font=font(30),fill='white')
for row,idx in enumerate([1,2]):
 for col,v in enumerate(['before','after']):
  y=60+row*755;d.text((col*720+18,y),f'{v.upper()} / MOUNT {idx}',font=font(25),fill='#f4c48b' if col==0 else '#97e8b8');im.paste(Image.open(OUT/f'{v}-toe-socket-{idx}.png').convert('RGB'),(col*720,y+35))
im.save(OUT/'socket-before-after.png')
files=[OUT/f'pose-{p["label"]}.png' for p in poses['poses']];im=Image.new('RGB',(1040,1778),'#14212c');d=ImageDraw.Draw(im);d.text((12,10),'Falcon / 24 native-joint diagnostics',font=font(24),fill='white')
for i,p in enumerate(files):
 x=i%4*260;y=50+i//4*288;im.paste(Image.open(p).convert('RGB').resize((260,260)),(x,y));d.text((x+7,y+263),p.stem,font=font(15),fill='white')
im.save(OUT/'pose-proof.png')
cfg=json.loads((ROOT/'input-audit.json').read_text());meta=json.loads((OUT/'intact-render-metadata.json').read_text());fit=min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7)
e['display_model']=res(Path(r['output']));e['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));e['status']='Four toes per foot: three forward and one rear. Extra outer rear toes removed, chest gap and malformed triangles repaired. Original 45-joint rig retained; deleted-chain skin cleaned locally.';e['review_models']=[{'label':'INTACT QUALITY ARCHIVE\nExtra rear toes unapproved','path':e['source_model']['path'],'display_scale':fit*meta['height_scale']},{'label':'DOWNLOADED RIG\nUnrepaired / five toes per foot','path':res(archive),'display_scale':fit},{'label':'LOCAL REPAIR\nFour toes / original 45-joint rig','path':res(Path(r['output'])),'display_scale':fit}];e['review_views']=review;e['review_provenance']={'date':'2026-11-13','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':45,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_available':True,'source_archive_scope':'Intact generated quality archive; exact historical Meshy upload not independently verified.','scope':r['scope']+' Protected one original balanced four-face contact between closed assembly surfaces. No gameplay replacement.'};(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
for f in ['diagnose_model.py','render_model.py','repair_model.py','audit_export.py','detail_pose_review.py','package_review.py','input-audit.json','face-components.json','foot_labels.py','label_foot.py','remove_toes.py','inspect_toe.py']:shutil.copy2(ROOT/f,OUT/f)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:
 assert r.get('anatomy_review_resolved'), 'Resolve toe selection before promotion.'
 latest=json.loads(catpath.read_text(encoding='utf-8'));other=[x for x in latest['entries'] if x['id']!='falcon'];latest['entries']=[e if x['id']=='falcon' else x for x in latest['entries']];assert [x for x in latest['entries'] if x['id']!='falcon']==other;catpath.write_text(json.dumps(latest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Falcon repair published; other entries preserved.')
print('Final SHA256',r['output_sha256'])
