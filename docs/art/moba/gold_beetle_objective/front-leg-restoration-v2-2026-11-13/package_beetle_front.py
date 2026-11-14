import json,sys,shutil,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent
OUT=BASE/'docs/art/moba/gold_beetle_objective/front-leg-restoration-v2-2026-11-13'
OLD=BASE/'docs/art/moba/gold_beetle_objective/repair-v1-2026-11-11'
report=json.loads((OUT/'repair-verification.json').read_text());audit=json.loads((OUT/'independent-export-audit.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text())
assert audit['passed'] and audit['tested_sha256']==report['output_sha256']==poses['tested_sha256']
assert len(poses['poses'])==11 and max(p['coincident_surface_gap_m'] for p in poses['poses'])<1e-6
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def compare(before,after,dest,title,close=False):
 im=Image.new('RGB',(1440,865),'#14212c');draw=ImageDraw.Draw(im)
 draw.text((18,12),title,font=font(28),fill='white')
 draw.text((18,53),'BEFORE / FUSED FRONT LEGS',font=font(24),fill='#f5c383')
 draw.text((738,53),'AFTER / ONE SHIN AND FOOT PER LEG',font=font(24),fill='#95eaba')
 for i,p in enumerate([before,after]):im.paste(Image.open(p).convert('RGB').resize((720,720)),(i*720,90))
 draw.text((18,823),'Same 23-joint skeleton. Source references unchanged. True pre-remesh GLB unavailable.',font=font(23),fill='#c6d9e8')
 im.save(dest)
review={}
for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]:
 dest=OUT/f'review-{view}.png';compare(OLD/f'after-{view}.png',OUT/f'after-{view}.png',dest,'Golden Beetle / '+key.upper())
 review[key]={'path':res(dest),'kind':'Prior fused rig / reconstructed six-leg review; true pre-remesh source unavailable'}
compare(OUT/'before-front-leg-outside.png',OUT/'after-front-leg-outside.png',OUT/'front-leg-before-after.png','Golden Beetle / front-leg correction')
compare(OLD/'after-three-quarter.png',OUT/'after-three-quarter.png',OUT/'review-three-quarter.png','Golden Beetle / repaired front-leg proportions')
files=[OUT/f'pose-{p["label"]}.png' for p in poses['poses']];cell=340;cols=3
im=Image.new('RGB',(cols*cell,math.ceil(len(files)/cols)*(cell+30)+50),'#14212c');draw=ImageDraw.Draw(im);draw.text((12,12),'Golden Beetle v2 / native-joint tests',font=font(24),fill='white')
for i,p in enumerate(files):
 x=i%cols*cell;y=50+i//cols*(cell+30);pic=Image.open(p).convert('RGB').resize((cell,cell));im.paste(pic,(x,y));draw.text((x+8,y+cell+3),p.stem,font=font(18),fill='white')
im.save(OUT/'pose-proof.png')
for f in ['rebuild_beetle_front.py','review_beetle_front.py','audit_beetle_front.py','package_beetle_front.py']:shutil.copy2(ROOT/f,OUT/f)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));entry=next(e for e in cat['entries'] if e['id']=='gold_beetle')
entry['display_model']=res(Path(report['output']));entry['artist_workspace']=res(Path(report['output']).with_suffix('.blend'))
entry['status']='Fused front legs rebuilt from the healthy legs: six single shins/feet. Original 23-joint skeleton; local skin transfer.'
entry['review_models'][1]['path']=res(Path(report['output']));entry['review_models'][1]['label']='FRONT LEGS FIXED\nSame 23-joint skeleton'
entry['review_views']=review;entry['review_provenance'].update({'date':'2026-11-13','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'repaired_sha256':report['output_sha256'],'scope':'Both front legs reconstructed from the healthy middle legs, aligned to existing front chains; source joint connections protected and locally bridged. Six feet independently verified, eleven native joint poses checked. Original hierarchy/rest/binds/materials/textures retained; local donor weights and one gray collar material added. True pre-remesh unavailable; no gameplay/map replacement.','previous_repair':res(Path(report['source']))})
(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n')
if '--publish' in sys.argv:
 catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Golden Beetle v2 Workshop entry published')
print('Sheets packaged; final SHA256',report['output_sha256'])
