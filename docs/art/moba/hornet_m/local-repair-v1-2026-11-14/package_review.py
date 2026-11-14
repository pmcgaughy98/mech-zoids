import json,sys,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/hornet_m/local-repair-v1-2026-11-14';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text());assert a['passed'] and a['tested_sha256']==r['output_sha256']==poses['tested_sha256'] and len(poses['poses'])==24
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
archives=[]
for src,sha in [(Path(r['source']),r['source_sha256']),(Path(r['accepted_touchup']),r['accepted_touchup_sha256'])]:
 assert hashlib.sha256(src.read_bytes()).hexdigest()==sha;dest=BASE/'art/model_catalog/sources'/src.name
 if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==sha
 else:shutil.copy2(src,dest)
 archives.append(dest)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));e=next(e for e in cat['entries'] if e['id']=='hornet');review={};versions=[('archive','INTACT SOURCE / EXTRA LIMBS UNAPPROVED','#c5d8ed'),('intact','APPROVED SIX-LEG CUT / CRACKED SURFACE','#e3d5a0'),('before','DOWNLOADED RIG / DAMAGED SURFACE','#f4c48b'),('after','RESTORED SURFACE / SAME 51-JOINT RIG','#97e8b8')]
for key in ['front','left','back','right']:
 im=Image.new('RGB',(2880,865),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Hornet / '+key.upper()+' / source, approved cuts, rig and restoration',font=font(28),fill='white')
 for i,(v,label,color) in enumerate(versions):d.text((i*720+15,58),label,font=font(22),fill=color);im.paste(Image.open(OUT/f'{v}-{key}.png').convert('RGB'),(i*720,100))
 d.text((18,830),'Original sources and generation sheets preserved. Approved six-leg cuts reapplied to the intact source; transferred skin on original skeleton.',font=font(22),fill='#c5d8ed');dest=OUT/f'review-{key}.png';im.save(dest);review[key]={'path':res(dest),'kind':'Intact generated archive (extra anatomy unapproved) / approved six-leg pre-rig touch-up (cracked) / damaged rig / restored surface; matched framing'}
im=Image.new('RGB',(1440,1570),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Hornet / intact surface restored, approved six-leg layout',font=font(29),fill='white')
for row,suffix in enumerate(['head','wings']):
 for col,(v,label) in enumerate([('before','BEFORE / DAMAGED RIG'),('after','AFTER / RESTORED SURFACE')]):
  y=60+row*755;d.text((col*720+18,y),label,font=font(25),fill='#f4c48b' if col==0 else '#97e8b8');im.paste(Image.open(OUT/f'{v}-{suffix}.png').convert('RGB'),(col*720,y+35))
im.save(OUT/'before-after.png')
im=Image.new('RGB',(1440,810),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Hornet / underside / six legs and approved closures',font=font(29),fill='white')
for col,v in enumerate(['before','after']):d.text((col*720+18,58),v.upper(),font=font(25),fill='white');im.paste(Image.open(OUT/f'{v}-underside-detail.png').convert('RGB'),(col*720,90))
im.save(OUT/'underside-proof.png')
im=Image.new('RGB',(1040,1778),'#14212c');d=ImageDraw.Draw(im);d.text((12,10),'Hornet / 24 native-joint diagnostics',font=font(24),fill='white')
for i,p in enumerate(poses['poses']):
 x=i%4*260;y=50+i//4*288;im.paste(Image.open(OUT/f'pose-{p["label"]}.png').convert('RGB').resize((260,260)),(x,y));d.text((x+7,y+263),p['label'],font=font(15),fill='white')
im.save(OUT/'pose-proof.png')
cfg=json.loads((ROOT/'input-audit.json').read_text());fit=min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7);metas={v:json.loads((OUT/f'{v}-render-metadata.json').read_text()) for v in ['archive','intact']}
e['display_model']=res(Path(r['output']));e['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));e['status']='Approved six-leg layout restored from intact source. Original 51-joint skeleton retained; skin transferred and tested. High-detail review (445k triangles); optimisation and authored movement pending.';e['review_models']=[{'label':'INTACT SOURCE ARCHIVE\nExtra limbs unapproved','path':e['source_model']['path'],'display_scale':fit*metas['archive']['height_scale']},{'label':'APPROVED SIX-LEG CUT\nPre-rig / cracked surface','path':res(archives[1]),'display_scale':fit*metas['intact']['height_scale']},{'label':'DOWNLOADED RIG\nDamaged surface','path':res(archives[0]),'display_scale':fit},{'label':'RESTORED SURFACE\nSix legs / original 51-joint rig','path':res(Path(r['output'])),'display_scale':fit}];e['review_views']=review;e['review_provenance']={'date':'2026-11-14','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':51,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_available':True,'accepted_pre_rig_touchup':res(archives[1]),'accepted_pre_rig_touchup_sha256':r['accepted_touchup_sha256'],'source_archive_scope':'Original generated archive plus the documented approved six-leg pre-rig touch-up. Exact historical Meshy upload not independently verified. Both damaged inputs remain visible.','scope':r['scope']};(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
for f in ['diagnose_model.py','render_model.py','weld_audit.py','baseline_geometry.py','baseline-geometry-audit.json','precision-and-baseline-audit.json','export_cut_mask.py','restore_surface.py','bind_restored.py','audit_export.py','detail_pose_review.py','package_review.py','input-audit.json','joint-bind-map.json']:shutil.copy2(ROOT/f,OUT/f)
shutil.copy2(ROOT/'accepted-cut-mask.npz',OUT/'accepted-cut-mask.npz');shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:
 latest=json.loads(catpath.read_text(encoding='utf-8'));other=[x for x in latest['entries'] if x['id']!='hornet'];latest['entries']=[e if x['id']=='hornet' else x for x in latest['entries']];assert [x for x in latest['entries'] if x['id']!='hornet']==other;catpath.write_text(json.dumps(latest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Hornet restoration published; other entries preserved.')
print('Final SHA256',r['output_sha256'])
