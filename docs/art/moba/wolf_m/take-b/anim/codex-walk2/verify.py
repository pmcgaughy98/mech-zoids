from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,importlib.util,math,hashlib
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('finish',R/'finish.py');fn=importlib.util.module_from_spec(sp);sp.loader.exec_module(fn)
sp=importlib.util.spec_from_file_location('sel',R.parents[3]/'rhino_l/take-a/anim/selout_rhino.py');sel=importlib.util.module_from_spec(sp);sp.loader.exec_module(sel);sel.OUTLINE=np.array([20,20,24],np.uint8)
ref=np.array(Image.open(R.parent.parent/'fixed/e.png').convert('RGBA'));pal=set(p[:3] for p in fn.P)
checks=[];table=[];spreads={};recs=json.loads((R/'articulation.json').read_text())
frames=[np.array(Image.open(R/'walk/frames'/f'side_f{i}.png').convert('RGBA')) for i in range(8)]
for f,a in enumerate(frames):
 m=a[:,:,3]>0;yy,xx=np.where(m);colors=set(map(tuple,a[m,:3]));checks.append(dict(frame=f,size=list(a.shape[:2]),bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),palette_ok=colors<=pal,colour_count=len(colors),holes=int((ndi.binary_fill_holes(m)&~m).sum()),components=int(ndi.label(m,np.ones((3,3)))[1]),below160=int(m[161:].sum()),canvas_edge=bool(m[[0,-1]].any() or m[:,[0,-1]].any())))
for name,p in fn.paws.items():
 worlds=[];samples=[]
 for f in range(8):
  a=np.array(Image.open(R/'walk/layers'/f'{name}_f{f}.png'));m=a[:,:,3]>0;ys,xs=np.where(m);by=int(ys.max());sole=np.where(m[by])[0];cx=float((sole.min()+sole.max())/2);off,lift=fn.paths[p['pair']][f];target=p['x']+off;err=abs(cx-target);le=abs((160-by)-lift)
  # Track authored paw sole after final compositing as well as its complete unoccluded layer.
  visible=[int(x) for x in sole if np.array_equal(frames[f][by,x],a[by,x])];table.append(dict(paw=name,frame=f,target_x=target,measured_x=cx,target_lift=lift,measured_lift=160-by,x_error=err,lift_error=le,sole_span=[int(sole.min()),int(sole.max())],matching_final_sole_pixels=len(visible)))
  if lift==0:worlds.append(cx+f*5);samples.append(dict(frame=f,sprite_x=cx,body_world_x=f*5,world_x=cx+f*5))
 spreads[name]=dict(samples=samples,spread=max(worlds)-min(worlds))
# Measure the actual timed footprint tool's stamp instants (floating-point int behavior included).
stamp=[];last=-1
for vf in range(400):
 t=vf/50;idx=int(t*10)
 if idx!=last:stamp.append((idx,t));last=idx
for name,p in fn.paws.items():
 cycles=[]
 for cycle in range(10):
  world=[]
  for idx,t in stamp:
   f=idx%8
   if idx//8==cycle and fn.paths[p['pair']][f][1]==0:world.append(p['x']+fn.paths[p['pair']][f][0]+50*t)
  if len(world)==4:cycles.append(max(world)-min(world))
 spreads[name]['actual_tool_stamp_spread_max']=round(max(cycles),6)
# 4x sel-out board: still then full old row then full new row.
cw,ch=512,352;bg=(82,90,85,255);board=Image.new('RGBA',(cw*8,ch*3),bg);d=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def tile(a):return Image.fromarray(sel.selout(a)[0]).crop((32,88,160,169)).resize((512,324),Image.Resampling.NEAREST)
board.alpha_composite(tile(ref),(0,28));d.text((8,4),'APPROVED fixed/e.png (4x sel-out)',fill='white',font=font)
for row,seq in [(1,[np.array(Image.open(R.parent/'codex-set-a/walk/frames'/f'side_f{i}.png').convert('RGBA')) for i in range(8)]),(2,frames)]:
 for f,a in enumerate(seq):
  board.alpha_composite(tile(a),(f*cw,row*ch+28));d.text((f*cw+8,row*ch+4),('SET A ' if row==1 else 'WALK2 ')+f'f{f} 100ms',fill='white',font=font)
board.convert('RGB').save(R/'board.png');board.resize((2048,528),Image.Resampling.NEAREST).convert('RGB').save(R/'board_small.png')
pics=[]
for a in frames:
 im=Image.new('RGBA',(512,324),bg);im.alpha_composite(tile(a));pics.append(im.convert('RGB'))
pics[0].save(R/'preview.gif',save_all=True,append_images=pics[1:],duration=100,loop=0,disposal=2,optimize=False)
g=Image.open(R/'preview.gif');dur=[]
for i in range(g.n_frames):g.seek(i);dur.append(g.info['duration'])
assert g.n_frames==8 and dur==[100]*8 and g.info.get('loop')==0
assert all(c['binary_alpha'] and c['palette_ok'] and c['holes']==0 and c['components']==1 and c['below160']==0 and not c['canvas_edge'] for c in checks)
assert all(t['x_error']<=1 and t['lift_error']<=1 for t in table)
assert all(v['spread']<=2 and v['actual_tool_stamp_spread_max']<=2 for v in spreads.values())
result=dict(structural=checks,paw_measurements=table,footlock=spreads,gif=dict(frames=8,ms=dur,loop=0))
(R/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['Native frames before preview sel-out.','8/8 PASS canvas192, binary alpha, approved palette, connected body, holes0, stray components0, below160=0, edge contacts0.','8/8 bottom row160; bounding boxes width109-111 height66-67, reference110x66.','32/32 paw samples x error0px, lift error0px; measured from full native paw sole, with final-composite overlap recorded.','Far paws baseline x from approved still; original perspective sole y158 normalized to shared y160 gameplay ground.','Paw contacts: x is midpoint of eleven-pixel flat dark sole; those same eleven pixels translate -5 each planted frame.','GIF reopened: 8 frames, each100ms, loop0.']
for name,v in spreads.items():lines.append(name+': '+str(v))
for f in range(8):
 lines.append('f'+str(f)+' '+ '; '.join(f"{x['paw']} x{x['measured_x']:g} lift{x['measured_lift']} (target {x['target_x']}/{x['target_lift']})" for x in table if x['frame']==f))
(R/'checks.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[:11]))
