"""Independent colour-stamp audit, reusing ape_l/run1/verify.py searches."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import build as m
b=m.b;R=m.R;T=m.T;load=m.load;X,Y=m.X,m.Y
_tree=ast.parse((R.parents[2]/'walk/tools/walk_tools.py').read_text());ns={'np':np}
exec(compile(ast.Module(body=[n for n in _tree.body if isinstance(n,ast.FunctionDef) and n.name=='find_slits'],type_ignores=[]),'walk_tools.py','exec'),ns)
find_slits=ns['find_slits']
def specks(a,details=False):
 out=[]
 for c in set(map(tuple,a[a[:,:,3]>0])):
  mask=np.all(a==c,axis=2)&(Y>=120)&(Y<=164)
  for cc in b.pieces(mask):
   if len(cc)<=2:out.append((bytes(c[:3]).hex(),cc))
 return out if details else len(out)

def audit():
 lines=['hippo-walk35-run1 independent pixel audit.',
 'Reused ape_l/run1 native.py locate(): exhaustive sole colour-stamp translations, no rig/target used in search.',
 'Sole = outer endpoints of bottom TWO painted foot rows; hidden/covered stamps measured on saved leg layer.',
 'Specks = 8-connected single-colour components of 1 or 2 pixels, restricted to rows120-164 inclusive.',
 'Upper canvas is checked above highest moving joint; fixed discs are also checked independently.',
 'GIF cannot encode125ms:120/130 alternating =1000ms total; exact125ms APNG also provided.']
 res={};fails=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
 for v in ['e','se','ne']:
  ref=load(R/f'stills/{v}.png');frames=[load(R/f'walk/frames/{v}_f{f}.png') for f in range(8)];disc=load(R/f'source/{v}_discs.png');body=load(R/f'source/{v}_body.png');allowed=set(map(tuple,ref[ref[:,:,3]>0]));vr={'still_specks':specks(ref),'structure':[],'feet':{}};res[v]=vr
  rig=json.loads((R/'rig.json').read_text())[v]
  seamboard=Image.new('RGB',(9*580,380),(65,73,80));ds=ImageDraw.Draw(seamboard)
  for f,a in enumerate(frames):
   op=a[:,:,3]>0;cc=b.pieces(op);dip=int(f in [0,4]);st=b.shift(ref,0,dip);cut={'e':140,'se':116,'ne':119}[v]+dip;d=np.any(a[:cut]!=st[:cut],axis=2);dm=b.shift(disc,0,dip);dp=dm[:,:,3]>0
   sl=find_slits(a,ref,dip)
   body_slits=[(x,y) for x,y in sl if b.shift(body,0,dip)[y,x,3]>0]
   sr=dict(frame=f,canvas=list(a.shape[:2]),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),off_palette_pixels=sum(tuple(c) not in allowed for c in a[op]),colours=len(set(map(tuple,a[op]))),components=len(cc),stray_pixels=sum(map(len,cc[1:])),holes=int((b.fill_holes(op)&~op).sum()),edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any()),lowest_row=int(np.where(op)[0].max()),upper_canvas_diff_percent=float(100*d.sum()/d.size),upper_canvas_diff_pixels=int(d.sum()),disc_diff_pixels=int(np.any(a[dp]!=dm[dp],axis=1).sum()),specks=specks(a),seams=sl,body_slits=body_slits)
   vr['structure'].append(sr);lines.append('STRUCT '+v+' '+json.dumps(sr))
   for key,ok in [('structure',sr['components']==1 and not sr['holes'] and not sr['edge'] and not sr['off_palette_pixels'] and sr['binary_alpha']),('upper',not sr['upper_canvas_diff_pixels']),('discs',not sr['disc_diff_pixels']),('specks',sr['specks']<=vr['still_specks']+2),('body_slits',not body_slits)]:
    if not ok:fails.append(f'{v} f{f} {key}')
   marked=a.copy()
   for x,y in sl:marked[y,x]=(255,50,50,255)
   tile=Image.fromarray(marked).crop((35,95,151,165)).resize((580,350),Image.Resampling.NEAREST);base=Image.new('RGBA',tile.size,(65,73,80));base.alpha_composite(tile);seamboard.paste(base.convert('RGB'),((f+1)*580,25));ds.text(((f+1)*580+8,3),v+f' f{f}: {len(sl)} flags',font=font,fill='white')
  tile=Image.fromarray(ref).crop((35,95,151,165)).resize((580,350),Image.Resampling.NEAREST);base=Image.new('RGBA',tile.size,(65,73,80));base.alpha_composite(tile);seamboard.paste(base.convert('RGB'),(0,25));ds.text((8,3),v+' still',font=font,fill='white');seamboard.save(R/f'{v}_seams_review.png')
  footpic=Image.new('RGB',(1480,4*270),(58,66,62));dr=ImageDraw.Draw(footpic)
  for j,n in enumerate(['RF','LH','LF','RH']):
   src=load(R/f'source/{v}_{n}_lower.png');sole=b.support(src);tracks=[];pp=[]
   for f,a in enumerate(frames):
    layer=load(R/f'walk/layers/{v}_{n}_f{f}.png');p,score,d,ends=b.locate(a,src);where='composite'
    if score<1 or not ends:p,score,d,ends=b.locate(layer,src);where='leg layer (occluded)'
    rr=next(q for q in rig if q['foot']==n and q['frame']==f);target=np.array(rr['target']);err=np.abs(p-target);lift=rr['lift'];actual_lift=int(np.floor(target[1]+lift+.5))-p[1]
    sy,sx=np.where(src[:,:,3]>0);dx,dy=d;core=sy>=sy.min()+4;match=float(np.all(layer[sy[core]+dy,sx[core]+dx]==src[sy[core],sx[core]],axis=1).mean())
    pad=sy>=sole[1]-7;padmatch=float(np.all(layer[sy[pad]+dy,sx[pad]+dx]==src[sy[pad],sx[pad]],axis=1).mean())
    knee=load(R/f'source/{v}_{n}_knee.png');yy,xx=np.where(knee[:,:,3]>0);kd=rr['knee_delta'];kneematch=float(np.all(layer[yy+kd[1],xx+kd[0]]==knee[yy,xx],axis=1).mean())
    tr=dict(frame=f,sole=p.tolist(),measured_from=where,stamp_match=score,endpoint_visible=ends,delta=d,target=target.tolist(),target_error_xy=err.tolist(),expected_lift=lift,measured_lift=float(actual_lift),native_lower_core_match=match,native_foot_pad_match=padmatch,native_knee_match=kneematch,articulated_length_error=rr['leg_length_error'],upper_link_error=rr['upper_link_error'],lower_link_error=rr['lower_link_error'])
    pp.append(p);tracks.append(tr);lines.append('CONTACT '+v+' '+n+' '+json.dumps(tr))
    if err.max()>1 or actual_lift!=lift or score!=1 or not ends:fails.append(f'{v} {n} f{f} contact')
    if padmatch!=1 or kneematch!=1 or rr['leg_length_error']>1 or rr['upper_link_error'] is None:fails.append(f'{v} {n} f{f} native parts/length')
   start=(T['gait'][n]+3)%8;order=[(start+k)%8 for k in range(5)];step=np.array(T['views'][v]['planted_step_px']);locked=np.array([pp[f]-k*step for k,f in enumerate(order)]);spread=np.ptp(locked,axis=0)
   vr['feet'][n]=dict(planted_order=order,spread_xy=spread.tolist(),max_target_error=float(max(max(t['target_error_xy']) for t in tracks)),frames=tracks)
   if spread.max()>2:fails.append(f'{v} {n} lock')
   oy=j*270;dr.text((10,oy+4),f'{v} {n}: planted {order}; pixel-measured spread {spread[0]:.3f}/{spread[1]:.3f}px',font=font,fill='white');colors=['#ffb575','#75e5cf','#e99fe2','#c9e978','#aab8ff'];orig=locked.mean(0)
   for k,f in enumerate(order):
    dr.text((10,oy+26+k*20),f'f{f} sole {pp[f][0]:.1f},{pp[f][1]:.1f} locked {locked[k][0]:.3f},{locked[k][1]:.3f} {tracks[f]["measured_from"]}',fill=colors[k],font=font)
    dx,dy=tracks[f]['delta'];yy,xx=np.where((src[:,:,3]>0)&(Y>=sole[1]-1))
    for y,x in zip(yy,xx):
     pt=np.array([x+dx,y+dy])-k*step;px,py=np.floor((pt-orig)*7+[1200,oy+65]).astype(int);dr.rectangle((px,py,px+6,py+6),fill=colors[k])
   for f in range(8):
    dr.text((10+f*180,oy+139),f'f{f} '+('layer' if 'layer' in tracks[f]['measured_from'] else 'frame'),font=font,fill='white');cx,cy=sole;box=(int(cx)-17,int(cy)-19,int(cx)+19,int(cy)+9);where=load(R/f'walk/layers/{v}_{n}_f{f}.png') if 'layer' in tracks[f]['measured_from'] else frames[f];tile=Image.new('RGBA',(144,112),(73,79,75));tile.alpha_composite(Image.fromarray(where).crop(box).resize((144,112),Image.Resampling.NEAREST));footpic.paste(tile.convert('RGB'),(10+f*180,oy+158))
  footpic.save(R/f'{v}_footprints.png');lines.append('SUMMARY '+v+' '+json.dumps({n:{k:z for k,z in q.items() if k!='frames'} for n,q in vr['feet'].items()}))
 res['failures']=fails;(R/'verification.json').write_text(json.dumps(res,indent=2));lines.append('FAILURES '+repr(fails));(R/'checks.txt').write_text('\n'.join(lines)+'\n')
 for v in ['e','se','ne']:
  vr=res[v];print(v,'specks',vr['still_specks'],[s['specks'] for s in vr['structure']],'slits',[len(s['seams']) for s in vr['structure']],'body',[len(s['body_slits']) for s in vr['structure']],'discs',[s['disc_diff_pixels'] for s in vr['structure']]);print('feet',{n:(q['spread_xy'],q['max_target_error']) for n,q in vr['feet'].items()})
 print('FAILURES',fails)
 return res
if __name__=='__main__':audit()
