import json,sys,shutil,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text());assert a['passed'] and a['tested_sha256']==r['output_sha256']==poses['tested_sha256'] and len(poses['poses'])==18
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
src=Path(r['source']);archive=BASE/'art/model_catalog/sources'/src.name;assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
if archive.exists():assert hashlib.sha256(archive.read_bytes()).hexdigest()==r['source_sha256']
else:shutil.copy2(src,archive)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));e=next(e for e in cat['entries'] if e['id']=='electric_eel');review={};versions=[('intact','INTACT QUALITY / EXTRA PRONG UNAPPROVED','#c5d8ed'),('before','DOWNLOADED RIG / THREE PRONGS','#f4c48b'),('after','LOCAL REPAIR / TWO PRONGS, SAME RIG','#97e8b8')]
for key in ['front','left','back','right']:
 if key in ['left','right']:
  im=Image.new('RGB',(720,760),'#14212c');d=ImageDraw.Draw(im);d.text((15,12),'Electric Eel / '+key.upper()+' / matched profile',font=font(25),fill='white')
  for i,(v,label,color) in enumerate(versions):
   y=55+i*220;d.text((15,y),label,font=font(22),fill=color);im.paste(Image.open(OUT/f'{v}-{key}.png').convert('RGB').crop((0,270,720,450)),(0,y+32))
  d.text((15,724),'Original source GLBs and reference PNGs preserved.',font=font(21),fill='#c5d8ed')
 else:
  im=Image.new('RGB',(2160,865),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Electric Eel / '+key.upper()+' / quality and repair',font=font(28),fill='white')
  for i,(v,label,color) in enumerate(versions):d.text((i*720+15,58),label,font=font(22),fill=color);im.paste(Image.open(OUT/f'{v}-{key}.png').convert('RGB'),(i*720,100))
  d.text((18,830),'Original sources and references preserved. Upper prong removed; local closure and weight cleanup.',font=font(22),fill='#c5d8ed')
 dest=OUT/f'review-{key}.png';im.save(dest);review[key]={'path':res(dest),'kind':'Intact generated quality archive / downloaded rig / local repair; matched view and scale'}
im=Image.new('RGB',(720,520),'#14212c');d=ImageDraw.Draw(im);d.text((15,12),'Electric Eel / two-prong tail and surface repair',font=font(28),fill='white')
for i,(v,label) in enumerate([('before','BEFORE / DOWNLOADED RIG'),('after','AFTER / TWO PRONGS, SIX GAPS CLOSED')]):
 y=56+i*220;d.text((15,y),label,font=font(23),fill='#f4c48b' if i==0 else '#97e8b8');im.paste(Image.open(OUT/f'{v}-left.png').convert('RGB').crop((0,270,720,450)),(0,y+32))
im.save(OUT/'before-after.png')
im=Image.new('RGB',(1440,810),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Electric Eel / selected upper prong 1 removed',font=font(30),fill='white')
for col,(v,label) in enumerate([('before','BEFORE / THREE PRONGS'),('after','AFTER / TWO LOWER PRONGS')]):
 d.text((col*720+18,58),label,font=font(26),fill='#f4c48b' if col==0 else '#97e8b8');im.paste(Image.open(OUT/f'{v}-fork.png').convert('RGB'),(col*720,90))
im.save(OUT/'tail-before-after.png')
for group,indices in [('A',[1,2,3]),('B',[4,5,6])]:
 im=Image.new('RGB',(720,1250),'#14212c');d=ImageDraw.Draw(im);d.text((12,10),'Electric Eel / matched patch closeups '+group,font=font(25),fill='white')
 for row,idx in enumerate(indices):
  for col,v in enumerate(['before','after']):
   x=360*col;y=50+row*395;im.paste(Image.open(OUT/f'{v}-patch-{idx}.png').convert('RGB').resize((360,360)),(x,y));d.text((x+8,y+363),f'{v} / patch {idx}',font=font(19),fill='white')
 im.save(OUT/f'local-proof-{group}.png')
files=[OUT/f'pose-{p["label"]}.png' for p in poses['poses']];cell=260;cols=4;im=Image.new('RGB',(1040,1490),'#14212c');d=ImageDraw.Draw(im);d.text((12,10),'Electric Eel / 18 native-joint diagnostics',font=font(24),fill='white')
for i,p in enumerate(files):
 x=i%4*260;y=50+i//4*288;im.paste(Image.open(p).convert('RGB').resize((260,260)),(x,y));d.text((x+7,y+263),p.stem,font=font(15),fill='white')
im.save(OUT/'pose-proof.png')
cfg=json.loads((ROOT/'input-audit.json').read_text());meta=json.loads((OUT/'intact-render-metadata.json').read_text());fit=min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7)
e['display_model']=res(Path(r['output']));e['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));e['status']='Upper tail prong 1 removed; two lower prongs retained. Six gaps and malformed strips repaired. Original 56-joint rig and textures preserved, deleted-chain weights cleaned locally.';e['review_models']=[{'label':'INTACT QUALITY ARCHIVE\nExtra upper prong unapproved','path':e['source_model']['path'],'display_scale':fit*meta['height_scale']},{'label':'DOWNLOADED RIG\nUnrepaired / three prongs','path':res(archive),'display_scale':fit},{'label':'LOCAL REPAIR\nTwo prongs / original 56-joint rig','path':res(Path(r['output'])),'display_scale':fit}];e['review_views']=review;e['review_provenance']={'date':'2026-11-13','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':56,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_available':True,'source_archive_scope':'Intact generated quality archive; exact historical Meshy upload not independently verified.','scope':r['scope']+' One original balanced four-face contact between closed assembly surfaces is protected; no new contact edges. No gameplay replacement.'};(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
for f in ['setup.py','diagnose_model.py','render_model.py','repair_model.py','audit_export.py','detail_pose_review.py','package_review.py','remove_upper.py','check_tail_cut.py','input-audit.json','face-components.json']:shutil.copy2(ROOT/f,OUT/f)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:
 latest=json.loads(catpath.read_text(encoding='utf-8'));other_before=[x for x in latest['entries'] if x['id']!='electric_eel'];latest['entries']=[e if x['id']=='electric_eel' else x for x in latest['entries']];assert [x for x in latest['entries'] if x['id']!='electric_eel']==other_before;catpath.write_text(json.dumps(latest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Electric Eel repair published in Workshop; other entries preserved.')
print('Final SHA256',r['output_sha256'])
