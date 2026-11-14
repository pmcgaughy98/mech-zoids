import json,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/cobra_m/base-reshape-v2-2026-11-10';OLD=BASE/'docs/art/moba/cobra_m/rigged-repair-v1-2026-11-10';ROOT=Path(__file__).parent
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
canvas=Image.new('RGB',(2160,810),'#17202a');draw=ImageDraw.Draw(canvas)
for i,(name,label,mirror) in enumerate([('before-left','LEFT BASE / BEFORE',False),('after-left','LEFT BASE / REPAIRED v2',False),('before-right','HEALTHY RIGHT / mirrored for comparison',True)]):
 image=Image.open(OUT/(name+'.png')).convert('RGB')
 if mirror:image=ImageOps.mirror(image)
 canvas.paste(image,(i*720,60));draw.text((i*720+18,16),label,font=font,fill='white')
draw.text((18,784),'Local geometry + UV restoration from the existing opposite side; same 21-bone skeleton.',font=font,fill='white');canvas.save(OUT/'left-base-before-after.png')
for view in ['front','side','right','back','underside','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');draw=ImageDraw.Draw(canvas)
 for i,(path,label) in enumerate([(OLD/f'intact-{view}.png','INTACT PRE-REMESH | earlier tail cut'),(OLD/f'remeshed-{view}.png','REMESHED + RIGGED | downloaded input'),(OUT/f'repaired-{view}.png','BASE REPAIR v2 | existing skeleton')]):
  canvas.paste(Image.open(path).convert('RGB'),(720*i,65));draw.text((720*i+15,15),label,font=font,fill='white')
 draw.text((15,790),'COBRA / '+view.upper()+' / original generation sheets remain separate',font=font,fill='white');canvas.save(OUT/f'review-{view}.png')
canvas=Image.new('RGB',(1440,1540),'#17202a');draw=ImageDraw.Draw(canvas)
for i,(name,label) in enumerate([('pose-Bone_001-8','Base joint +8 degrees'),('pose-Bone_001--8','Base joint -8 degrees'),('pose-Bone_014-10','Tail root +10 degrees'),('pose-Bone_014--10','Tail root -10 degrees')]):
 canvas.paste(Image.open(OUT/(name+'.png')).convert('RGB'),((i%2)*720,(i//2)*770+40));draw.text(((i%2)*720+15,(i//2)*770+8),label,font=font,fill='white')
canvas.save(OUT/'base-rig-proof.png')
check=json.loads((OUT/'deformation-check.json').read_text());verification=json.loads((OUT/'verification.json').read_text());assert check['tested_glb_sha256']==verification['output_sha256'];assert all(p['maximum_uv_split_position_gap_m']<1e-5 for p in check['poses'])
catalog=BASE/'art/model_catalog/catalog.json';data=json.loads(catalog.read_text());entry=next(e for e in data['entries'] if e['id']=='cobra');prefix='res://docs/art/moba/cobra_m/base-reshape-v2-2026-11-10/'
entry['display_model']=prefix+'cobra-rigged-base-reshape-v2.glb';entry['status']='Base repair v2: left junction rebuilt from healthy right side. Existing 21-bone skeleton retained; local weights transferred and bend-tested.'
entry['review_models'][2].update(label='BASE REPAIR v2\nExisting 21-bone skeleton',path=entry['display_model'])
for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]:entry['review_views'][key].update(path=prefix+f'review-{view}.png',versions=['intact before remesh, earlier tail cut','remeshed rigged input','left-base repair v2'])
entry['review_provenance'].update(report=prefix+'verification.json',repaired_sha256=verification['output_sha256'],scope='Local left-base geometry and UV restoration using mirrored right patch. Existing skeleton/binds/materials/textures retained; local weights transferred with seam fade. No gameplay installation.')
catalog.write_text(json.dumps(data,indent=2)+'\n')
for name in ['diagnose.py','mirror_patch.py','review_base_v2.py','package_base_v2.py']:shutil.copy2(ROOT/name,OUT/name)
print('Packaged comparison sheets, base/rig proof, and updated Cobra review to v2.')
