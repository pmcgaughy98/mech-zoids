from pathlib import Path
import json,shutil
from PIL import Image,ImageDraw,ImageFont
BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/hummingbird_s/topology-repair-v2-2026-11-10';OLD=BASE/'docs/art/moba/hummingbird_s/needle-repair-v1-2026-11-10';ROOT=Path(__file__).parent;font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
canvas=Image.new('RGB',(900,1900),'#17202a');draw=ImageDraw.Draw(canvas)
for r in range(4):
 for c,version in enumerate(['before','after']):
  image=Image.open(OUT/f'{version}-patch-{r+1}.png').convert('RGB').resize((450,450));canvas.paste(image,(c*450,r*475+25));draw.text((c*450+10,r*475+2),f'Patch {r+1} / {version.upper()}',font=small,fill='white')
canvas.save(OUT/'repair-closeups.png')
for view in ['front','side','right','back','underside','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');draw=ImageDraw.Draw(canvas)
 for i,(path,label) in enumerate([(OLD/f'intact-{view}.png','INTACT PRE-REMESH'),(OLD/f'before-{view}.png','DOWNLOADED RIGGED REMESH'),(OUT/f'after-{view}.png','NEEDLE + TOPOLOGY v2')]):
  canvas.paste(Image.open(path).convert('RGB'),(i*720,65));draw.text((i*720+15,15),label,font=font,fill='white')
 draw.text((15,790),'HUMMINGBIRD / '+view.upper()+' / original generation sheets remain separate',font=font,fill='white');canvas.save(OUT/f'review-{view}.png')
report=json.loads((OUT/'repair-verification.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text());assert poses['tested_sha256']==report['output_sha256']
catalog=BASE/'art/model_catalog/catalog.json';data=json.loads(catalog.read_text());entry=next(e for e in data['entries'] if e['id']=='hummingbird');prefix='res://docs/art/moba/hummingbird_s/topology-repair-v2-2026-11-10/'
entry['display_model']=prefix+'hummingbird-rigged-needle-topology-v2.glb';entry['status']='Hummingbird v2: straight needle retained; malformed flaps removed and 4 gaps closed. Original 21-bone rig, weights and textures preserved.'
entry['review_models'][2].update(label='NEEDLE + TOPOLOGY v2\nOriginal rig preserved',path=entry['display_model'])
for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]:entry['review_views'][key]['path']=prefix+f'review-{view}.png'
entry['review_provenance'].update(report=prefix+'repair-verification.json',repaired_sha256=report['output_sha256'],scope='Needle correction retained; local topology repair changes indices only. Original rig/weights/textures retained. Broader finish and final proportions remain subject to review.')
catalog.write_text(json.dumps(data,indent=2)+'\n')
for name in ['repair_topology.py','review_topology.py','package_topology.py']:shutil.copy2(ROOT/name,OUT/name)
shutil.copy2('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py',OUT/'diagnose.py')
print('Packaged hummingbird v2 and advanced Workshop comparison.')
