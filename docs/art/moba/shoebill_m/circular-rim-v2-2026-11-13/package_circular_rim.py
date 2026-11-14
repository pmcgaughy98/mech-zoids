import json,sys,shutil,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/shoebill_m/circular-rim-v2-2026-11-13';OLD=BASE/'docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());assert a['passed'] and a['tested_sha256']==r['output_sha256']
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));entry=next(e for e in cat['entries'] if e['id']=='shoebill')
review={}
for key in ['front','left','back','right']:
 im=Image.new('RGB',(2100,865),'#14212c');d=ImageDraw.Draw(im);d.text((20,12),'Shoebill / '+key.upper()+' / circular moon rim',font=font(28),fill='white')
 for i,(path,label,color) in enumerate([(OLD/f'intact-{key}.png','INTACT BODY ARCHIVE\nOriginal backplate','#c6d9ee'),(OLD/f'before-{key}.png','RIGGED DOWNLOAD\nFitted plate / donor overlap','#f4c286'),(OUT/f'after-{key}.png','CIRCULAR RIM V2\nSame 38-joint skeleton','#96e9b7')]):
  d.multiline_text((700*i+18,52),label,font=font(24),fill=color);im.paste(Image.open(path).convert('RGB').resize((700,700)),(700*i,115))
 d.text((20,827),'Original body archive has the earlier backplate. Current moon design retained; original GLBs and source PNGs preserved.',font=font(22),fill='#c6d9ee');dest=OUT/f'review-{key}.png';im.save(dest);review[key]={'path':res(dest),'kind':'Body archive / downloaded composite / circular rim v2; prior backplate labeled'}
for view in ['plate-back','plate-three-quarter']:
 im=Image.new('RGB',(1600,940),'#14212c');d=ImageDraw.Draw(im);d.text((18,12),'Shoebill / circular rim and fitted casing',font=font(30),fill='white')
 for i,(path,label) in enumerate([(OLD/f'after-{view}.png','BEFORE / EXPOSED GREY BACKING'),(OUT/f'after-{view}.png','AFTER / CIRCULAR RIM; MOON VISIBLE')]):
  d.text((800*i+18,55),label,font=font(24),fill='#f4c286' if i==0 else '#96e9b7');im.paste(Image.open(path).convert('RGB'),(800*i,95))
 d.text((18,905),'Original moon face, brass mounts, body and source rig weights preserved.',font=font(24),fill='#c6d9ee');im.save(OUT/('before-after-'+view+'.png'))
posefile=OUT/'visual-deformation-check.json'
if posefile.exists():
 poses=json.loads(posefile.read_text());assert poses['tested_sha256']==r['output_sha256'] and len(poses['poses'])==14
 files=[OUT/f'pose-{p["label"]}.png' for p in poses['poses']];cell=280;cols=4;im=Image.new('RGB',(cols*cell,math.ceil(len(files)/cols)*(cell+30)+50),'#14212c');d=ImageDraw.Draw(im);d.text((12,10),'Circular moon rim v2 / native-joint checks',font=font(24),fill='white')
 for i,p in enumerate(files):
  x=i%cols*cell;y=50+i//cols*(cell+30);im.paste(Image.open(p).convert('RGB').resize((cell,cell)),(x,y));d.text((x+7,y+cell+3),p.stem,font=font(16),fill='white')
 im.save(OUT/'pose-proof.png')
entry['display_model']=res(Path(r['output']));entry['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));entry['status']='Circular silver rim and blue casing cover grey backing. Moon face, brass mounts and original 38-joint rig retained.';entry['review_models'][-1]['path']=res(Path(r['output']));entry['review_models'][-1]['label']='CIRCULAR MOON RIM\nSame 38-joint skeleton';entry['review_views']=review;entry['review_provenance'].update({'report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'repaired_sha256':r['output_sha256'],'previous_repair':res(Path(r['source'])),'scope':r['scope']+' New frame is rigidly attached to existing Bone_003; no original skin rows changed. No gameplay replacement.'});(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n')
for file in ['build_circular_rim.py','render_circular_rim.py','audit_circular_rim.py','pose_circular_rim.py','package_circular_rim.py']:shutil.copy2(ROOT/file,OUT/file)
if '--publish' in sys.argv:
 assert posefile.exists() and (OUT/'pose-proof.png').exists();catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Circular rim v2 published in Workshop.')
print('Packaged',r['output_sha256'])
