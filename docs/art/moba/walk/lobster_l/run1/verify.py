import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,ast
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes
import build as m
R=m.R;T=m.T;b=m.b;X=m.X;Y=m.Y;load=m.load
ns={'np':np};tree=ast.parse((R.parents[2]/'walk/tools/walk_tools.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='find_slits'],type_ignores=[]),'walk_tools.py','exec'),ns)
find_slits=ns['find_slits']
def specks(a,details=False):
 out=[]
 for c in set(map(tuple,a[a[:,:,3]>0])):
  lab,num=label(np.all(a==c,axis=2)&(Y>=100)&(Y<=164),np.ones((3,3)));sizes=np.bincount(lab.ravel())
  for j in np.where((sizes>0)&(sizes<=2))[0]:
   if j:out.append((bytes(c[:3]).hex(),list(zip(*np.where(lab==j)))))
 return out if details else len(out)
def locate(a,src):
 yy,xx=np.where(src[:,:,3]>0);cols=src[yy,xx];best=None
 for dy in range(-10,11):
  for dx in range(-10,11):
   score=float(np.all(a[yy+dy,xx+dx]==cols,axis=1).mean());key=(score,-abs(dx)-abs(dy))
   if best is None or key>best[0]:best=(key,dx,dy)
 return [best[1],best[2]],best[0][0]
def audit():
 result={};lines=['lobster-walk35-run1; exhaustive native colour-stamp measurement (no targets/deltas used by search).','Sole centres are measured from the source foot bottom two painted rows; exhaustive pixel stamp independently recovers each displacement.','Whole foot includes all toe and recess pixels in source/*_foot.png; hidden stamps measured on leg layers.','GIF uses120/130ms alternating (GIF10ms limit); APNG has exact125ms.','Specks: 8-connected1/2px single-colour components, rows100-164 inclusive.'];fail=[];rig=json.loads((R/'rig.json').read_text())
 for v in ['e','se','ne']:
  ref=load(R/f'stills/{v}.png');body=load(R/f'source/{v}_body.png');fg=load(R/f'source/{v}_claws.png');allowed=set(map(tuple,ref[ref[:,:,3]>0]));vr={'still_specks':specks(ref),'structure':[],'feet':{},'underside':[]};result[v]=vr
  # Body underside gate on original labelled walking-leg spans, excluding foreground claws.
  for n,foot in T['views'][v]['visible_feet'].items():
   native=load(R/f'source/{v}_{n}_native.png');yy,xx=np.where(native[:,:,3]>0);l,r=int(xx.min()),int(xx.max());rows=[]
   for x in [l-1,r+1]:
    yy=np.where(body[:,x,3]>0)[0];rows.append(int(yy.max()) if len(yy) else None)
   bound=int(np.where(body[:,:,3]>0)[0].max());valid_rows=[y if y is not None else bound for y in rows]
   deviations=[]
   for x in range(l,r+1):
    yy=np.where(body[:,x,3]>0)[0]
    if len(yy):deviations.append(float(yy.max()-np.interp(x,[l-1,r+1],valid_rows)))
   q={'foot':n,'span':[l,r],'outside_rows':rows,'transparent_outside_uses_conservative_body_bound':bound,'max_below_line':max(deviations,default=0),'pass':max(deviations,default=0)<=1};vr['underside'].append(q);lines.append('UNDERSIDE '+v+' '+json.dumps(q))
   if not q['pass']:fail.append(f'{v} {n} underside')
  frames=[load(R/f'walk/frames/{v}_f{f}.png') for f in range(8)]
  for f,a in enumerate(frames):
   op=a[:,:,3]>0;lab,num=label(op,np.ones((3,3)));sizes=np.bincount(lab.ravel())[1:];dip=int(f in [0,4]);st=b.shift(ref,0,dip);cut=min(q['top'] for n,q in m.D[v].items() if n.startswith('R'))+dip
   sl=find_slits(a,ref,dip);pin=b.shift(body,0,dip);inside=[p for p in sl if pin[p[1],p[0],3]]
   row=dict(frame=f,canvas=list(a.shape[:2]),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),off_palette=sum(tuple(c) not in allowed for c in a[op]),colours=len(set(map(tuple,a[op]))),components=int(num),stray_pixels=int(sum(sizes)-max(sizes)),holes=int((binary_fill_holes(op)&~op).sum()),edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any()),lowest_row=int(np.where(op)[0].max()),upper_diff_percent=float(np.any(a[:cut]!=st[:cut],axis=2).mean()*100),specks=specks(a),seams=sl,inside_body_flags=inside)
   vr['structure'].append(row);lines.append('STRUCT '+v+' '+json.dumps(row))
   for k,ok in [('structure',num==1 and not row['holes'] and not row['off_palette'] and not row['edge'] and row['binary_alpha']),('upper',row['upper_diff_percent']==0),('specks',row['specks']<=vr['still_specks']+2),('body slits',not inside)]:
    if not ok:fail.append(f'{v} f{f} {k}')
  footprint=Image.new('RGB',(1600,6*230),(60,70,65));dr=ImageDraw.Draw(footprint);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
  for j,n in enumerate(['R3','R2','R1','L3','L2','L1']):
   src=load(R/f'source/{v}_{n}_foot.png');tracks=[];pp=[]
   rr=next(q for q in rig[v] if q['foot']==n);sole=b.support(src)
   for f,a in enumerate(frames):
    layer=load(R/f'walk/layers/{v}_{n}_f{f}.png');delta,score=locate(a,src);where='frame'
    if score<1:delta,score=locate(layer,src);where='layer: occluded'
    p=sole+delta;pp.append(p);rr=next(q for q in rig[v] if q['foot']==n and q['frame']==f);target=np.array(rr['target']);err=np.abs(p-target)
    sy,sx=np.where(src[:,:,3]>0);footmatch=float(np.all(layer[sy+delta[1],sx+delta[0]]==src[sy,sx],axis=1).mean())
    composite_match=float(np.all(a[sy+delta[1],sx+delta[0]]==src[sy,sx],axis=1).mean())
    # Lift independently measured after rounding the projected ground location.
    lift=int(np.floor(target[1]+rr['lift']+.5))-int(p[1])
    tr=dict(frame=f,sole=p.tolist(),measured_from=where,delta=delta,stamp_match=score,target_error_xy=err.tolist(),expected_lift=rr['lift'],measured_lift=lift,whole_foot_match_layer=footmatch,whole_foot_match_composite=composite_match,projected_length_change=rr['projected_length_change']);tracks.append(tr);lines.append('CONTACT '+v+' '+n+' '+json.dumps(tr))
    if err.max()>1 or score!=1 or footmatch!=1 or lift!=rr['lift']:fail.append(f'{v} {n} f{f} foot')
    oy=j*230;dr.text((f*195+5,oy+32),f'f{f} {where} {footmatch:.0%}',font=font,fill='white');cx,cy=sole;box=(int(cx)-18,int(cy)-23,int(cx)+21,int(cy)+10);im=Image.fromarray(a if where=='frame' else layer).crop(box).resize((156,132),Image.Resampling.NEAREST);base=Image.new('RGBA',im.size,(70,77,73));base.alpha_composite(im);footprint.paste(base.convert('RGB'),(f*195+5,oy+56))
   start=0 if n in ['L1','R2','L3'] else 4;order=[(start+k)%8 for k in range(4)];step=np.array(T['views'][v]['planted_step_px']);locked=np.array([pp[f]-k*step for k,f in enumerate(order)]);spread=np.ptp(locked,axis=0);maxerr=max(max(t['target_error_xy']) for t in tracks)
   vr['feet'][n]=dict(planted_order=order,spread_xy=spread.tolist(),max_target_error=maxerr,frames=tracks)
   if spread.max()>2:fail.append(f'{v} {n} footlock')
   dr.text((5,j*230+4),f'{v} {n} planted {order}; pixel-stamp lock spread x/y {spread[0]:.3f}/{spread[1]:.3f}px; error <= {maxerr:.3f}px',font=font,fill='white')
   for k,f in enumerate(order):dr.text((5+k*390,j*230+196),f'f{f} sole {pp[f]} ; lock {np.round(locked[k],3)}',font=font,fill=['#ffb575','#75e5cf','#e99fe2','#c9e978'][k])
  footprint.save(R/f'{v}_footprints.png')
 result['failures']=fail;(R/'verification.json').write_text(json.dumps(result,indent=2));lines.append('FAILURES '+repr(fail));(R/'checks.txt').write_text('\n'.join(lines)+'\n')
 for v in ['e','se','ne']:
  q=result[v];print(v,'specks',q['still_specks'],[s['specks'] for s in q['structure']],'components',[s['components'] for s in q['structure']],'holes',[s['holes'] for s in q['structure']],'bodyflags',[len(s['inside_body_flags']) for s in q['structure']]);print('underside',q['underside']);print('feet',{n:(z['spread_xy'],z['max_target_error'],[t['whole_foot_match_layer'] for t in z['frames']]) for n,z in q['feet'].items()})
 print('FAILURES',fail)
if __name__=='__main__':audit()
