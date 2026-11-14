from pathlib import Path
import json,struct,hashlib
from PIL import Image,ImageFont,ImageDraw
out=Path('D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/rhino-generated')
src=Path('D:/dev/_scratch/mech-art-direction/rhino-generated/source.glb')
original=Path('D:/user/Downloads/rhino_s - Hunyuan 3D v3.1 Pro.glb')
with src.open('rb') as f:
 f.read(12); n,t=struct.unpack('<II',f.read(8)); d=json.loads(f.read(n))
inv={'supplied_file':str(original),'isolated_copy':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_unchanged':hashlib.sha256(original.read_bytes()).hexdigest()==hashlib.sha256(src.read_bytes()).hexdigest(),'triangles':sum(d['accessors'][s['indices']]['count']//3 for m in d['meshes'] for s in m['primitives']),'vertices':306875,'materials':len(d.get('materials',[])),'skins':len(d.get('skins',[])),'animations':len(d.get('animations',[])),'texture_dimensions':[4096,4096],'texture_count':3,'source_height_m':0.719021976,'test_height_m':2.0,'identity_note':'Preston confirmed this is the current gorilla despite the rhino_s filename.'}
inv['matches_current_attachment_path']=inv.pop('original_unchanged')
inv['attachment_note']='The attachment path changed size and hash during this review. Captures use the preserved initial 50,001,268-byte copy, SHA256 5c223ba84c7cde87be15d75b9414b13630c6e75760c019eb9bedc2828ff6d915. This lane did not write to the attachment.'
(out/'inventory.json').write_text(json.dumps(inv,indent=2))
board=Image.new('RGB',(1536,790),'#171c22'); dr=ImageDraw.Draw(board)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
dr.text((16,10),'SUPPLIED MESHFORGE MODEL | same geometry, pose, camera and foundry lighting',font=font,fill='white')
for i,(v,title) in enumerate([('A-original','A | Original export'),('B-satin','B | Satin armor'),('C-graphic','C | Graphic lighting response')]):
 x=i*512
 dr.text((x+16,48),title,font=font,fill='white')
 im=Image.open(out/f'{v}-1280x720-y45-d0.png')
 board.paste(im.crop((384,200,896,560)),(x,80))
 far=Image.open(out/f'{v}-1280x720-y135-d8.png')
 board.paste(far.resize((512,288),Image.Resampling.LANCZOS),(x,476))
dr.text((16,447),'Above: identical native-resolution crops. Below: 8 metres farther, whole frames reduced equally.',font=small,fill='#d4dce4')
dr.text((16,768),'Test scale: 2 m tall, provisional. Static material test only; no rig, animation, geometry edits or game installation.',font=small,fill='#d4dce4')
board.save(out/'material-comparison.png')
print('Current attachment matches captured copy:',inv['matches_current_attachment_path'])
print('Captures:',len(json.loads((out/'capture-manifest.json').read_text())['captures']))
