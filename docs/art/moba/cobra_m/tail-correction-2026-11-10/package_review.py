from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,struct,hashlib,io
p=Path(__file__).parent
src=Path('D:/user/Downloads/Mecha Beast GLB/cobra_front - Hunyuan 3D v3.1 Pro.glb')
fixed=p/'cobra_front - single tail corrected.glb'
def read(path):
 with path.open('rb') as f:
  f.read(12);n,t=struct.unpack('<II',f.read(8));d=json.loads(f.read(n));n,t=struct.unpack('<II',f.read(8));b=f.read(n)
 return d,b
def textures(path):
 d,b=read(path);rows={}
 for im in d.get('images',[]):
  v=d['bufferViews'][im['bufferView']];start=v.get('byteOffset',0);png=b[start:start+v['byteLength']]
  image=Image.open(io.BytesIO(png)).convert('RGBA')
  rows[im['name']]={'png_sha256':hashlib.sha256(png).hexdigest(),'rgba_sha256':hashlib.sha256(image.tobytes()).hexdigest(),'size':list(image.size)}
 return rows
d,b=read(fixed);a=textures(src);z=textures(fixed)
report={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()=='af7353fcb7967f579bd715e64df339f52e6488958990dde25d652b47078bcfa3','output':str(fixed),'output_sha256':hashlib.sha256(fixed.read_bytes()).hexdigest(),'bytes':fixed.stat().st_size,'triangles':sum(d['accessors'][s['indices']]['count']//3 for m in d['meshes'] for s in m['primitives']),'skin_count':len(d.get('skins',[])),'animations':[a.get('name') for a in d.get('animations',[])],'embedded_textures':z,'source_texture_pixels_identical':all(name in z and val['rgba_sha256']==z[name]['rgba_sha256'] for name,val in a.items()),'source_png_bytes_identical':all(name in z and val['png_sha256']==z[name]['png_sha256'] for name,val in a.items()),'material_count':len(d.get('materials',[])),'render_size_checks':all(Image.open(p/f'{kind}-{view}.png').size==(640,640) for kind in ['before','after'] for view in ['front','side','back','underside','top','three-quarter']),'reimport':json.loads((p/'export-reimport-audit.json').read_text())}
(p/'verification.json').write_text(json.dumps(report,indent=2))
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
overview=Image.new('RGB',(1040,552),'#171c22');dr=ImageDraw.Draw(overview)
dr.text((16,8),'COBRA TAIL CORRECTION | preserved source versus single-tail repair',font=f,fill='white')
for i,(kind,label) in enumerate([('before','Before: two full tail branches'),('after','After: one continuous rear tail')]):
 x=i*520;dr.text((x+12,38),label,font=sm,fill='white')
 overview.paste(Image.open(p/f'{kind}-top.png').crop((60,80,580,565)),(x,62))
overview.save(p/'cobra-tail-before-after.png')
proof=Image.new('RGB',(1040,1524),'#171c22');dr=ImageDraw.Draw(proof)
dr.text((16,8),'FRONT / SIDE / BACK / UNDERSIDE | matched camera, scale and lighting',font=f,fill='white')
y=42
for view in ['front','side','back','underside']:
 box=(60,80,580,565) if view=='underside' else (60,180,580,465)
 h=box[3]-box[1]
 for i,kind in enumerate(['before','after']):
  dr.text((i*520+12,y),kind.upper()+' | '+view,font=sm,fill='white')
  proof.paste(Image.open(p/f'{kind}-{view}.png').crop(box),(i*520,y+24))
 y+=h+30
proof.crop((0,0,1040,y)).save(p/'four-view-proof.png')
print(json.dumps({k:v for k,v in report.items() if k!='embedded_textures'},indent=2))
