import json,sys,shutil,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/dragonfly_m/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());audit=json.loads((OUT/'independent-export-audit.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text());assert audit['passed'] and audit['tested_sha256']==r['output_sha256']==poses['tested_sha256'] and len(poses['poses'])==17
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
src=Path(r['source']);archive=BASE/'art/model_catalog/sources'/src.name;assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
if archive.exists():assert hashlib.sha256(archive.read_bytes()).hexdigest()==r['source_sha256']
else:shutil.copy2(src,archive)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));e=next(e for e in cat['entries'] if e['id']=='dragonfly');review={}
for key in ['front','left','back','right']:
 im=Image.new('RGB',(2160,880),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Dragonfly / '+key.upper()+' / approved pair 2 removal',font=font(28),fill='white')
 for i,(version,label,color) in enumerate([('intact','QUALITY ARCHIVE\nOriginal generated anatomy','#c8d9ee'),('before','DOWNLOADED RIG\nFour leg pairs','#f2c18a'),('after','PAIR 2 REMOVED\nSix legs / same 46-joint skeleton','#97eab9')]):
  d.multiline_text((720*i+18,52),label,font=font(23),fill=color);im.paste(Image.open(OUT/f'{version}-{key}.png').convert('RGB'),(720*i,110))
 d.text((18,838),'Archive is a surface-quality reference; its anatomy is not approved. Original GLB and reference PNGs preserved.',font=font(22),fill='#c8d9ee');dest=OUT/f'review-{key}.png';im.save(dest);review[key]={'path':res(dest),'kind':'Original quality archive / downloaded four-pair rig / six-leg repair; archive anatomy not approved'}
im=Image.new('RGB',(1440,850),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Dragonfly / outer-front pair 2 removed',font=font(30),fill='white')
for i,(version,label) in enumerate([('before','BEFORE / FOUR LEG PAIRS'),('after','AFTER / THREE LEG PAIRS')]):
 d.text((720*i+18,55),label,font=font(24),fill='#f2c18a' if i==0 else '#97eab9');im.paste(Image.open(OUT/f'{version}-three-quarter.png').convert('RGB'),(720*i,95))
d.text((18,818),'Four wings, antennae, tail and original 46-joint skeleton retained.',font=font(23),fill='#c8d9ee');im.save(OUT/'before-after.png')
files=[OUT/f'pose-{p["label"]}.png' for p in poses['poses']];cell=260;cols=4;im=Image.new('RGB',(cols*cell,math.ceil(len(files)/cols)*(cell+28)+50),'#14212c');d=ImageDraw.Draw(im);d.text((12,10),'Dragonfly / 17 native-joint diagnostic poses',font=font(24),fill='white')
for i,p in enumerate(files):
 x=i%cols*cell;y=50+i//cols*(cell+28);im.paste(Image.open(p).convert('RGB').resize((cell,cell)),(x,y));d.text((x+7,y+cell+3),p.stem,font=font(15),fill='white')
im.save(OUT/'pose-proof.png')
oldmeta=json.loads((OUT/'intact-render-metadata.json').read_text());cfg=json.loads((ROOT/'input-audit.json').read_text());fit=min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7)
e['display_model']=res(Path(r['output']));e['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));e['status']='Pair 2 removed: six legs and four wings. Local flaps/sockets repaired; original 46-joint skeleton retained.';e['review_models']=[{'label':'QUALITY ARCHIVE\nAnatomy not approved','path':e['source_model']['path'],'display_scale':fit*oldmeta['height_scale']},{'label':'DOWNLOADED RIG\nFour leg pairs','path':res(archive),'display_scale':fit},{'label':'SIX-LEG REPAIR\nSame 46-joint skeleton','path':res(Path(r['output'])),'display_scale':fit}];e['review_views']=review;e['review_provenance']={'date':'2026-11-13','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':46,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'selected_removed_pair':2,'remaining_pairs':[1,3,4],'intact_pre_remesh_available':True,'source_archive_scope':'Original generated quality archive; exact historical remesh upload not verified. Original archive anatomy is not approved.','scope':r['scope']+' Original nodes/rest/binds and source texture/UV/position rows retained. Local removed-chain skin reassigned to existing body parent; small new socket finish. No gameplay replacement.'};(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
for f in ['diagnose_model.py','render_model.py','repair_topology.py','check_cut.py','remove_pair2.py','audit_export.py','pose_review.py','package_review.py','input-audit.json','face-components.json','cut-fields.npz']:shutil.copy2(ROOT/f,OUT/f)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Dragonfly six-leg repair published in Workshop.')
print('Final SHA256',r['output_sha256'])
