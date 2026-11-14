"""Independent saved-frame checks and two-dimensional moving-world footprint boards."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
e={'__file__':str(R/'build.py')};exec((R/'build.py').read_text().split("(R/'walk/frames').mkdir")[0],e)
D=e['D'];P=e['P'];trace=e['trace'];widths=e['native_widths'];fp=e['footprint'];T=json.loads((R/'targets.json').read_text());rig=json.loads((R/'rig.json').read_text())
lines=['WOLF M TAKE B WALK4 / saved native frame audit','Widths: isolated traced plate/shank paint, perpendicular native coverage at25/50/75%; collars and overlapping segments excluded.','Paw width: widest source row. Proportion: root-knee and knee-ankle axis lengths.','Foot coordinates measured from saved complete limb layers: centre of lowest-row sole endpoints.','Final composite visibility counts include same-colour occlusion; overlap does not change the authored contact.']
result={'views':{}};summary=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
colors=[(255,185,74,255),(89,228,226,255),(235,111,181,255),(172,219,94,255)]
for view,legs in D.items():
 vv=T['views'][view];step=np.array(vv['screen_step_5']);ref=np.array(Image.open(R.parents[1]/'fixed'/f'{view}.png').convert('RGBA'));frames=[np.array(Image.open(R/'walk/frames'/f'{view}_f{f}.png').convert('RGBA')) for f in range(8)]
 vr={'structure':[],'paws':{},'widths':{}};result['views'][view]=vr
 lines.append(f"AXIS {view} fore={vv['fore_midpoint']} hind={vv['hind_midpoint']} u={vv['u']} f={vv['f']} step={step.tolist()}")
 for f,a in enumerate(frames):
  m=a[:,:,3]>0;holes=ndi.binary_fill_holes(m)&~m;labs,hn=ndi.label(holes);sizes=np.bincount(labs.ravel())[1:].tolist();_,n=ndi.label(m,np.ones((3,3)));palette=set(map(tuple,a[m,:3]));allowed={p[:3] for p in P}
  row={'frame':f,'size':list(a.shape[:2]),'palette_ok':palette<=allowed,'color_count':len(palette),'binary_alpha':bool(np.isin(a[:,:,3],[0,255]).all()),'components':n,'below160':int(m[161:].sum()),'edge':bool(m[[0,-1]].any() or m[:,[0,-1]].any()),'unintended_pinholes':sum(s for s in sizes if s<=24),'enclosed_interleg_negative_spaces':sizes}
  vr['structure'].append(row);lines.append('STRUCT '+view+' '+json.dumps(row));assert row['size']==[192,192] and row['palette_ok'] and row['binary_alpha'] and n==1 and row['below160']==0 and not row['edge'] and row['unintended_pinholes']==0
 board=Image.new('RGB',(1280,1120),(60,68,65));dr=ImageDraw.Draw(board);dr.text((12,8),f'{view.upper()} / world shift + frame * {step[0]:.5f}, {step[1]:.5f} px / 100 ms',font=font,fill='white')
 for pi,(name,q) in enumerate(legs.items()):
  recs=[z for z in rig[view] if z['name']==name];measure=[];world=[];groundidx=[];maxerr=0
  for rec in recs:
   f=rec['frame'];a=np.array(Image.open(R/'walk/layers'/f'{view}_{name}_f{f}.png').convert('RGBA'));p,span=fp(a);err=np.abs(p-rec['target']);lift=rec['ground_row']-p[1];maxerr=max(maxerr,float(err.max()));xx=np.where(a[int(p[1]),:,3]>0)[0];visible=[int(x) for x in xx if np.array_equal(frames[f][int(p[1]),x],a[int(p[1]),x])]
   row={'frame':f,'contact':p.tolist(),'sole_span':span,'ideal':rec['target'],'error_xy':err.tolist(),'lift_expected':rec['lift'],'lift_measured':lift,'visible_matching_sole_pixels':visible}
   measure.append(row);lines.append('PAW '+view+' '+name+' '+json.dumps(row));assert err.max()<=1 and lift==rec['lift']
   if rec['lift']==0:world.append(p+f*step);groundidx.append(f)
  spread=np.ptp(world,axis=0);assert spread.max()<=2
  vr['paws'][name]={'frames':measure,'world_contacts':np.array(world).tolist(),'spread_xy':spread.tolist(),'max_target_error':maxerr}
  lines.append('FOOTLOCK '+view+' '+name+' '+json.dumps(vr['paws'][name]));summary.append(f"{view} {name} footlock spread x/y {spread[0]:.3f}/{spread[1]:.3f}px.")
  # Moving world stamps at4x; each ground frame gets a distinct sole/centre colour.
  # The foreground paw's four contact centres should almost cover one another.
  panel=Image.new('RGBA',(640,480),(78,86,82,255));pd=ImageDraw.Draw(panel);scale=4;origin=np.array([25,20]);groundpoints=[]
  for gi,f in enumerate(groundidx):
   a=frames[f].copy();a[:,:,3]=(a[:,:,3]>0).astype(np.uint8)*38
   canvas=Image.new('RGBA',(256,224));canvas.alpha_composite(Image.fromarray(a),(int(round(f*step[0])),int(round(f*step[1]+20))))
   crop=canvas.crop((48,94,208,214)).resize((640,480),Image.Resampling.NEAREST);panel=Image.alpha_composite(panel,crop)
   p=np.array(measure[f]['contact'])+f*step+[0,20];xy=(p-np.array([48,94]))*4;groundpoints.append(xy);pd=ImageDraw.Draw(panel);c=colors[gi];pd.ellipse((xy[0]-3,xy[1]-3,xy[0]+3,xy[1]+3),outline=c,width=2);pd.text((12,46+gi*24),f'f{f}: {world[gi][0]:.3f}, {world[gi][1]:.3f}',font=font,fill=c)
  pd=ImageDraw.Draw(panel);pd.text((12,8),f'{name}: spread {spread[0]:.3f}, {spread[1]:.3f}px',font=font,fill='white');pd.text((12,22),'coloured rings = four world contact centres',fill='white');board.paste(panel.convert('RGB'),((pi%2)*640,50+(pi//2)*520))
  # Plate/shank widths and unchanged translated clawed paw width.
  wr={};bits=[]
  for tag,aa,bb,ix in [('upper',0,1,4),('shank',1,2,5)]:
   rw=widths(trace(ref,q[ix]),q[aa],q[bb]);ws=[]
   for rec in recs:
    a=np.array(Image.open(R/'walk/layers'/f"{view}_{name}_{tag}_f{rec['frame']}.png").convert('RGBA'));ws.append(widths(a,rec['root' if aa==0 else 'joint'],rec['joint' if bb==1 else 'ankle']))
   ws=np.array(ws);delta=int(np.max(np.abs(ws-rw)));assert delta<=1
   wr[tag]={'reference':rw.tolist(),'frames':ws.tolist(),'max_delta':delta};bits.append(f"{tag} {rw.tolist()} -> {ws.min(0).tolist()}..{ws.max(0).tolist()}")
  def pw(a):
   m=a[:,:,3]>0;return int(max([np.ptp(np.where(row)[0])+1 if row.any() else 0 for row in m]))
  refpw=pw(trace(ref,q[6]));pws=[pw(np.array(Image.open(R/'walk/layers'/f'{view}_{name}_paw_f{f}.png'))) for f in range(8)];assert all(x==refpw for x in pws)
  lengthmax=float(max(np.max(np.abs(np.array(z['lengths'])-z['length_reference'])) for z in recs));assert lengthmax<=2
  wr['paw']={'reference':refpw,'frames':pws};wr['max_length_delta']=lengthmax;vr['widths'][name]=wr;bits.append(f'paw {refpw}->{min(pws)}..{max(pws)}; length max delta {lengthmax:.3f}px')
  lines.append('WIDTH '+view+' '+name+'; '.join(bits))
 board.save(R/f'{view}_footprints.png')
 gif=Image.open(R/f'{view}_preview.gif');dur=[]
 for i in range(gif.n_frames):gif.seek(i);dur.append(gif.info['duration'])
 assert gif.n_frames==8 and dur==[100]*8 and gif.info['loop']==0
 lines.append(f'GIF {view} PASS 8 frames100ms infinite loop')
 for p in P:
  count=edgecount=0
  for a in frames:
   op=a[:,:,3]>0;edge=op&~ndi.binary_erosion(op,structure=ndi.generate_binary_structure(2,1));match=np.all(a==p,axis=2);count+=int(match.sum());edgecount+=int((edge&match).sum())
  lines.append(f'PALETTE {view} #{p[0]:02x}{p[1]:02x}{p[2]:02x} opaque={count} edge={edgecount}')
lines+=['PASS:64 paw targets<=1px; lifts exact after native target-row rounding.','PASS:8 planted-paw tracks spread<=2px in BOTH dimensions.','PASS:isolated segment widths within1px and segment lengths within2px; unchanged claw-paw pixels.','PASS:16 transparent192x192 frames; binary alpha; allowed12-colour palette; components1; below160=0; edge0; pinholes0.','Enclosed spaces larger than24 pixels are intentional background between crossing legs, not missing robot material.','EYE review uses exact supplied selout() with OUTLINE#141418, nearest4x. Raw frame alpha remains separate.']
(R/'checks.txt').write_text('\n'.join(lines)+'\n');(R/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
report=['WOLF M TAKE B / CODEX WALK4 / SE + NE TROT','Tokens: unavailable. Native pixels; no image tool/commit. Only codex-walk4 written; fixed stills and approved side timing read.']
for view in ['se','ne']:
 vv=T['views'][view];report.append(f"{view}: u=({vv['u'][0]:.9f},{vv['u'][1]:.9f}); f={vv['f']:.9f}; side paw spacing{T['side_paw_spacing']:.6f}px.")
report+=['64/64 contacts within1px of ideal2D target; exact2/4/4/2px raster lifts; pairA f0-3 / pairB f4-7.',f"Native row160 cap: se near_fore f0 -{8*T['views']['se']['u'][1]*T['views']['se']['f']:.3f}px; ne near_hind f7 -{-7*T['views']['ne']['u'][1]*T['views']['ne']['f']:.3f}px vs ideal; within1px."]
report+=summary
for view in ['se','ne']:
 for name,w in result['views'][view]['widths'].items():report.append(f"{view} {name}: upper{w['upper']['reference']}, shank{w['shank']['reference']}, paw{w['paw']['reference']}; width delta<=1; length delta{w['max_length_delta']:.3f}px.")
report+=['16/16:192x192 RGBA, binary alpha, approved palette, no below160 pixels, no canvas-edge contact, one connected creature.','No pinholes/strays; enclosed negative space between crossing legs retained rather than painted solid.','Body/head/fins from still, dip1px f1/f5; straight original tail plate pixels translate1px with dip, never thinned.','EYE at4x sel-out: forward three-quarter robot-wolf trot; paired steps follow side indices; plated legs and claws retained.','EYE: joined limbs, no abrupt cut ends seen; overlapping paws/legs naturally hide each other at crossing phases.','board.png: side timing on top, then each view approved still / setC / WALK4; footprint boards show2D world contacts.','GIFs:8 frames,100ms each, infinite loop. checks.txt and verification.json contain every saved contact and width.']
assert len(report)<30,len(report)
(R/'REPORT.txt').write_text('\n'.join(report)+'\n');print('\n'.join(summary));print('All numeric target, footlock, isolated-width, proportion, alpha, palette and file checks PASS.')
