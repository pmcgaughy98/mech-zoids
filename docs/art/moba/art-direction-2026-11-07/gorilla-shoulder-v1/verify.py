import json,struct,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
p=Path(__file__).parent
frames=Path('D:/dev/_scratch/mech-art-direction/gorilla-shoulder/motion')
def read(path):
 with path.open('rb') as f:
  f.read(12);n,t=struct.unpack('<II',f.read(8));d=json.loads(f.read(n));n,t=struct.unpack('<II',f.read(8));b=f.read(n)
 return d,b
def geometry(path):
 d,b=read(path);out={}
 for mesh in d['meshes']:
  hs=[]
  for pr in mesh['primitives']:
   for a in list(pr['attributes'].values())+[pr['indices']]:
    v=d['bufferViews'][d['accessors'][a]['bufferView']];o=v.get('byteOffset',0)
    hs.append(hashlib.sha256(b[o:o+v['byteLength']]).hexdigest())
  out[mesh['name']]=hs
 return out
manifest=json.loads((p/'capture-manifest.json').read_text())
audit=json.loads((p/'exported-parts-audit.json').read_text())
source=Path('D:/user/Downloads/Gorilla_s - Hunyuan 3D v3.1 Pro.glb')
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'original_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()=='5c223ba84c7cde87be15d75b9414b13630c6e75760c019eb9bedc2828ff6d915','rest_and_reach_mesh_buffers_identical':geometry(p/'shoulder-rest-2k.glb')==geometry(p/'shoulder-reach-2k.glb'),'all_exported_parts_closed_after_accounting_for_uv_splits':all(o['boundary_edges_after_weld']==0 and o['nonmanifold_edges_after_weld']==0 for o in audit),'components_per_part_after_uv_weld':{o['object']:o['connected_components_after_position_weld'] for o in audit},'static_capture_pairs':len(manifest['captures']),'motion_frames':len(list(frames.glob('frame*.png'))),'rest_min_silhouette_iou':min(r['rest_silhouette_iou'] for r in json.loads((p/'rest-comparison-report.json').read_text()))}
for frame,name in [(0,'rest'),(36,'reach'),(72,'rest')]:
 motion=np.asarray(Image.open(frames/f'frame{frame:03d}.png').convert('RGB'),dtype=np.float32)
 static=np.asarray(Image.open(p/f'{name}-y-45-d0.png').convert('RGB'),dtype=np.float32)
 report[f'motion_frame_{frame}_mean_abs_difference_in_body_crop']=float(np.abs(motion[200:560,384:896]-static[200:560,384:896]).mean())
(p/'verification.json').write_text(json.dumps(report,indent=2))
# Review samples of the actual moving model, not interpolated stills.
board=Image.new('RGB',(1536,1164),'#171c22');dr=ImageDraw.Draw(board)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
angles=json.loads((p/'motion-manifest.json').read_text())['angle_degrees']
for index,n in enumerate(range(0,73,9)):
 x=(index%3)*512;y=(index//3)*388
 dr.text((x+12,y+6),f'Frame {n:02d} | {abs(angles[n]):.2f} degrees',font=font,fill='white')
 board.paste(Image.open(frames/f'frame{n:03d}.png').crop((384,200,896,560)),(x,y+28))
board.save(p/'motion-contact-sheet.png')
print(json.dumps(report,indent=2))
