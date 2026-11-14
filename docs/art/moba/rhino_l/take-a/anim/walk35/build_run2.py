from pathlib import Path
import ast,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent; B=R.parents[1]; T=json.loads((R/'targets.json').read_text())
Y,X=np.indices((192,192))
P=[tuple(bytes.fromhex(c))+(255,) for c in '141218 211e27 3d3a44 58555e 7a4a06 9d9ba2 d18a0a d6d6dc ff3a2a ffcf1f fff4a8'.split()]
F=R/'walk/frames'; L=R/'run2/layers'; L.mkdir(parents=True,exist_ok=True)
# Save the previous top-level report/checks before replacing the delivery summaries.
for name in ['REPORT.txt','checks.txt','board.png']:
 p=R/name; dst=R/'run2'/('before_'+name)
 if p.exists() and not dst.exists():dst.write_bytes(p.read_bytes())
manifest=R/'run2/protected_hashes.json'
if not manifest.exists():
 paths=list(F.glob('*.png'))+list((B/'views_cam35').glob('*.png'))+[R/'targets.json']
 manifest.write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if not p.name.startswith(('s_f','n_f'))},indent=2))
def shift(a,dy):
 b=np.zeros_like(a)
 if dy>=0:b[dy:]=a[:192-dy]
 else:b[:192+dy]=a[-dy:]
 return b

def comp(a,b):
 m=b[:,:,3]>0;a[m]=b[m]

def traces(view):
 # Native per-row borders follow the round knee, cuff and inner cheek contour.
 if view=='s':
  lo=[66,65,65,65,65,65,66,66,65,65,65,64,63,63,63,63,63]+[63]*7
  hi=[77,78,79,79,79,79,79,80,81,82,83,84,85,86,87,87,88]+[91]*7
  left=np.zeros((192,192),bool)
  for j,y in enumerate(range(137,161)):left[y,lo[j]:hi[j]+1]=True
  # The opposing disc is asymmetric in the still; use its own native border.
  right=np.zeros_like(left)
  bounds=[(115,125),(114,126),(113,126),(112,127),(112,127),(112,127),(112,126),(111,126),(110,127),(109,127),(108,128),(107,129),(106,130),(105,130),(104,130),(103,130),(102,131)]+[(100,132)]*7
  for y,(a,b) in zip(range(137,161),bounds):right[y,a:b+1]=True
  return {'RF':left,'LF':right}
 left=(Y>=134)&(Y<=160)&(X>=61)&(X<=88)
 right=(Y>=134)&(Y<=160)&(X>=103)&(X<=132)
 return {'LH':left,'RH':right}

def socket(src,dx,dy,dip,view,name):
 # Native rows are extended into the joint recess when the rigid leg travels down.
 # No scaling: original bands, knee disc, cuff and sole are unchanged translations.
 moved=shift(src,dy)
 if dx:
  m=np.zeros_like(moved)
  if dx>0:m[:,dx:]=moved[:,:192-dx]
  else:m[:,:192+dx]=moved[:,-dx:]
  moved=m
 a=np.zeros_like(src)
 start=137 if view=='s' else 134
 top=start+dy; anchor=start+dip
 if top>anchor:
  # Dark recessed bearing with a bevel, under the fixed shoulder/body paint.
  cx={'RF':71,'LF':120,'LH':75,'RH':117}[name]+dx
  for y in range(anchor,top+2):
   a[y,cx-4:cx+5]=P[0]
   a[y,cx-3:cx+4]=P[1]
   a[y,cx-3:cx-1]=P[2]
 comp(a,moved)
 return a

tree=ast.parse((R.parent/'selout_rhino.py').read_text());env={'np':np,'OUTLINE':np.array(P[0][:3],np.uint8)}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selout'],type_ignores=[]),'selout','exec'),env);selout=env['selout']
frames={}; rig={}; bg=(86,126,107,255); font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for view in ['s','n']:
 ref=np.array(Image.open(B/'views_cam35'/f'{view}.png').convert('RGBA'));masks=traces(view);body=ref.copy();sources={}
 for name,m in masks.items():
  src=ref.copy();src[~m]=0;sources[name]=src;body[m]=0
  Image.fromarray(src).save(L/f'{view}_{name}_source.png')
 Image.fromarray(body).save(L/f'{view}_body.png')
 # Far soles are 16 body-axis projected pixels behind the near pair in the side reference.
 # Their entire swept bounds remain inside the pinned body: do not invent exposed feet.
 seq=[];rig[view]=[]
 for f in range(8):
  dip=int(f in (0,4));a=np.zeros_like(ref)
  for name,src in sources.items():
   target=T['views'][view]['visible_feet'][name]['frames'][f];lift=target['lift'];ground=int(np.floor(target['sole_centre'][1]+lift+.5));dy=ground-lift-160
   sole_x=np.where(src[160,:,3]>0)[0];oldcx=(sole_x.min()+sole_x.max())/2;dx=int(round(target['sole_centre'][0]-oldcx))
   leg=socket(src,dx,dy,dip,view,name)
   comp(a,leg);Image.fromarray(leg).save(L/f'{view}_{name}_f{f}.png')
   rig[view].append({'name':name,'frame':f,'translation_x':dx,'translation_y':dy,'ground_row':ground,'lift':lift,'target':target['sole_centre'],'rigid_length_delta':0})
  comp(a,shift(body,dip))
  # Explicit native joint recesses; close only enclosed pixels below the shoulder cut.
  holes=ndi.binary_fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)
  a[holes]=P[0]
  seq.append(a);Image.fromarray(a).save(F/f'{view}_f{f}.png')
 frames[view]=seq
(R/'run2/rig.json').write_text(json.dumps(rig,indent=2))
# Complete 192px canvases, all nine tiles at exact nearest-neighbour 4x.
board=Image.new('RGBA',(9*768,2*800),bg);d=ImageDraw.Draw(board)
for vi,view in enumerate(frames):
 ref=np.array(Image.open(B/'views_cam35'/f'{view}.png').convert('RGBA'))
 for j,a in enumerate([ref]+frames[view]):
  tile=Image.fromarray(selout(a)[0]).resize((768,768),Image.Resampling.NEAREST)
  board.alpha_composite(tile,(j*768,vi*800+30));d.text((j*768+12,vi*800+5),view+' '+('APPROVED STILL' if j==0 else f'f{j-1}'),font=font,fill='white')
 board.crop((0,vi*800,9*768,(vi+1)*800)).convert('RGB').save(R/f'{view}_board.png')
 pics=[]
 for a in frames[view]:
  tile=Image.fromarray(selout(a)[0]).resize((768,768),Image.Resampling.NEAREST);pic=Image.new('RGBA',tile.size,bg);pic.alpha_composite(tile);pics.append(pic.convert('RGB'))
 pics[0].save(R/f'{view}_preview.gif',save_all=True,append_images=pics[1:],duration=[120,130]*4,loop=0,disposal=2,optimize=False)
 raw=[Image.fromarray(a) for a in frames[view]];raw[0].save(R/f'{view}_preview.apng',save_all=True,append_images=raw[1:],duration=125,loop=0,disposal=0,blend=0)
board.convert('RGB').save(R/'board.png')
# Compact leg board preserves exact 4x for pixel inspection.
crop=(56,126,137,166);w,h=324,160
b=Image.new('RGBA',(w*9,2*(h+26)),bg);d=ImageDraw.Draw(b)
for vi,view in enumerate(frames):
 ref=np.array(Image.open(B/'views_cam35'/f'{view}.png').convert('RGBA'))
 for j,a in enumerate([ref]+frames[view]):
  b.alpha_composite(Image.fromarray(selout(a)[0]).crop(crop).resize((w,h),Image.Resampling.NEAREST),(j*w,vi*(h+26)+26));d.text((j*w+5,vi*(h+26)+2),view+' '+('STILL' if j==0 else f'f{j-1}'),font=font,fill='white')
b.convert('RGB').save(R/'run2/legs4x.png')
print('Built s/n native frames, unchanged source knee/cuff/foot translations; boards and previews.')
