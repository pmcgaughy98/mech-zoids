"""EX audit adapted to this run; read only approved stills, write only beside this script."""
from pathlib import Path
import json,importlib.util,sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from finish import P,TAKE,NAMES,CROSS,specks,note

def arr(path):return np.array(Image.open(path).convert('RGBA'))
def iou(a,b):return float((a&b).sum()/(a|b).sum())
def haus(a,b):return float(max(nd.distance_transform_edt(~a)[b].max(),nd.distance_transform_edt(~b)[a].max()))
def rowstr(rows,fmt):return '; '.join(v+' '+','.join(fmt(x) for x in rows[v]) for v in NAMES)
def fmt(x):return f'{x:.2f}'

def main():
 meta=json.loads((P/'preparation.json').read_text()); place=json.loads((P/'placement.json').read_text()); targets=json.loads((P/'targets.json').read_text()); sm=json.loads((P/'still_metrics.json').read_text()); pal={tuple(bytes.fromhex(c['hex'])) for c in json.loads((TAKE/'palette.json').read_text())}
 frames={v:[arr(P/'frames'/f'{v}_f{i}.png') for i in range(6)] for v in NAMES}; still={v:arr(TAKE/'views_cam35_touchup'/f'{v}.png') for v in NAMES}
 data={};invalid=set(); allbinary=True; allborder=True
 for v in NAMES:
  data[v]=[]; st=still[v]; sh=nd.binary_fill_holes(st[:,:,3]>0)&~(st[:,:,3]>0)
  for i,a in enumerate(frames[v]):
   m=a[:,:,3]>0; pixels=a[m,:3]; yy,xx=np.where(m); lab,n=nd.label(m,CROSS); hole=nd.binary_fill_holes(m)&~m
   p=place['frames'][f'{v}_f{i}']; ht=np.array([[s['x'],s['y']] for s in targets['views'][v]['soles'] if s['leg']=='hind']); drift=np.linalg.norm(np.array(p['hind'])-ht,axis=1)
   fr=np.array([s for s in targets['views'][v]['soles'] if s['leg'].startswith('front')]); base=np.array([[s['x'],s['y']] for s in fr]); shift=targets['views'][v]['frames'][i]['front_feet_shift_px']; expect=base+shift
   if i==5:expect[0,1]-=2
   actual=np.array(p['front']); err=np.linalg.norm(actual-expect,axis=1)
   invalid.update(tuple(c) for c in pixels if tuple(c) not in pal); binary=bool(set(np.unique(a[:,:,3])).issubset({0,255}));border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any());allbinary &= binary;allborder &= not border
   ink=float(np.all(pixels==[20,18,24],axis=1).sum()/len(pixels));eye=int(np.all(pixels==[255,58,42],axis=1).sum())
   data[v].append({'hind_drift':drift.tolist(),'front_measured':actual.tolist(),'front_target':expect.tolist(),'front_error':err.tolist(),'near_front_lift':float(base[0,1]-actual[0,1]),'lowest':int(yy.max()),'pieces':n,'specks':specks(a),'ink':ink,'eye':eye,'slits':int((hole&~sh).sum()),'holes':int(hole.sum()),'border':border,'binary_alpha':binary})
 lines=[]
 def check(ok,name,detail):lines.append(('PASS' if ok else 'MISS')+' '+name+': '+detail)
 diff={v:int(np.any(frames[v][0]!=still[v],axis=2).sum()) for v in NAMES};check(all(x==0 for x in diff.values()),'f0',str(diff)+' pixels differ')
 hr={v:[max(z['hind_drift']) for z in data[v]] for v in NAMES};check(all(x<=1 for z in hr.values() for x in z),'hind soles',rowstr(hr,fmt)+' px; 1 px limit; steel-pad/dark-sole boxes in placement.json')
 front={v:[data[v][i]['front_error'] for i in [2,3,4]] for v in NAMES}; check(all(max(data[v][i]['front_error'])<=tol for v in NAMES for i,tol in [(2,2),(3,2),(4,1)]),'front F2/F3/F4', '; '.join(v+' '+ '/'.join(','.join(fmt(z) for z in es) for es in front[v]) for v in NAMES)+' px error per visible foot; traced steel pads, outermost dark sole midpoint; SE far pad overlaps jaw, uncertain')
 lifts={v:data[v][5]['near_front_lift'] for v in NAMES};check(all(1<=x<=4 for x in lifts.values()),'front F5',str(lifts)+' px up, 1-4 required; same pad labels')
 lows={v:[z['lowest'] for z in data[v]] for v in NAMES};check(all(160<=x<=163 for z in lows.values() for x in z),'lowest row',rowstr(lows,str)+'; 160-163 allowed only camera-facing toes')
 movement={};
 for name,ia,ib,limit in [('F4-F5',4,5,3),('F5-still',5,0,4)]:
  vals={v:haus(frames[v][ia][:,:,3]>0,frames[v][ib][:,:,3]>0) for v in NAMES};feet={v:float(max(np.linalg.norm(np.array(place['frames'][f'{v}_f{ia}'][part])-np.array(place['frames'][f'{v}_f{ib}'][part]),axis=1).max() for part in ['hind','front'])) for v in NAMES};lower={v:max(vals[v],feet[v]) for v in NAMES};movement[name]={'silhouette_hausdorff':vals,'foot_landmark_max':feet,'motion_lower_bound':lower};check(all(x<=limit for x in lower.values()),name,'largest part move >= '+', '.join(v+' '+fmt(lower[v]) for v in NAMES)+f' px; limit {limit}; max(symmetric silhouette Hausdorff, foot landmarks), lower bounds, no claim of full part correspondence')
 f1={v:{'alpha_iou':iou(frames[v][1][:,:,3]>0,still[v][:,:,3]>0),'same_colour_union':float((np.all(frames[v][1]==still[v],axis=2)&(still[v][:,:,3]>0)).sum()/((frames[v][1][:,:,3]>0)|(still[v][:,:,3]>0)).sum())} for v in NAMES};check(True,'F1-still', '; '.join(v+' IoU '+fmt(z['alpha_iou'])+' same-colour/opaque-union '+fmt(z['same_colour_union']) for v,z in f1.items())+'; measured, no threshold supplied')
 f3={v:iou(frames[v][3][:,:,3]>0,still[v][:,:,3]>0) for v in NAMES};check(all(x<=.85 for x in f3.values()),'F3 rear IoU',', '.join(v+' '+fmt(x) for v,x in f3.items())+' <=0.85')
 eyes={v:[z['eye'] for z in data[v]] for v in NAMES};check(all(x>=4 for v in ['e','se'] for x in eyes[v]) and all(x==0 for x in eyes['ne']),'eye pixels',rowstr(eyes,str)+'; E/SE dark generated sockets, >=4; NE 0')
 inks={v:[z['ink']*100 for z in data[v]] for v in NAMES};check(all(abs(z['ink']/sm[v]['ink_share']-1)<=.15 for v in NAMES for z in data[v]),'ink %',rowstr(inks,fmt)+' vs E 8.14 SE 7.79 NE 8.25, +/-15%')
 check(not invalid and allbinary and allborder,'palette/alpha/border',f'extra colours {[bytes(c).hex() for c in invalid]}; binary alpha {allbinary}; border contacts {sum(z["border"] for v in NAMES for z in data[v])}')
 pieces={v:[z['pieces'] for z in data[v]] for v in NAMES}; sp={v:[z['specks'] for z in data[v]] for v in NAMES};check(all(z['pieces']==1 and z['specks']<=1.2*sm[v]['specks_1_2px'] for v in NAMES for z in data[v]),'pieces/specks','pieces '+rowstr(pieces,str)+'; specks '+rowstr(sp,str)+'; limits E386.4 SE496.8 NE415.2; no despeckle threshold exceeded')
 check(all(abs(meta['rows'][v][key]/meta['rows'][v]['still_wh'][j]-1)<=.04 for v in NAMES for j,key in enumerate(['width','height'])),'column1 bbox', '; '.join(v+' '+str(meta['rows'][v]['width'])+'x'+str(meta['rows'][v]['height'])+' vs '+str(meta['rows'][v]['still_wh'][0])+'x'+str(meta['rows'][v]['still_wh'][1]) for v in NAMES)+'; +/-4%')
 he={v:meta['rows'][v]['head_error']*100 for v in NAMES};check(all(abs(x)<=3 for x in he.values()),'head size',', '.join(v+' '+fmt(x)+'%' for v,x in he.items())+' vs still, +/-3%; manual horn-to-eye E/SE, horn-to-back-head NE; landmarks in preparation.json')
 slits={v:[z['slits'] for z in data[v]] for v in NAMES};check(all(x==0 for z in slits.values() for x in z),'seam slits',rowstr(slits,str)+' enclosed transparent pixels absent from still hole mask at same canvas coordinates')
 # Final fringe audit, read only; approved still f0 is never cleaned or remapped.
 from defringe import clean
 fringe={v:[list(clean(a)[1:]) for a in frames[v]] for v in NAMES};check(all(z[0]==0 and z[1]==0 for v in NAMES for z in fringe[v]),'fringe','plum/pale-rim '+str({v:[z[:2] for z in fringe[v]] for v in NAMES}))
 (P/'checks.txt').write_text('\n'.join(lines)+'\n'); (P/'audit_metrics.json').write_text(json.dumps({'frames':data,'f1':f1,'f3_iou':f3,'movement':movement,'fringe':fringe},indent=2));note('Step 4 complete: checks.txt and audit_metrics.json written; pose/scale misses retained.');print('\n'.join(lines))
 # Exact import without executing source main or touching its directory.
 spec=importlib.util.spec_from_file_location('rhino_selout',TAKE/'anim/selout_rhino.py'); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 assert module.OUTLINE.tolist()==[20,18,24]
 sd=P/'frames_selout';sd.mkdir(exist_ok=True);sel={};stsel={}
 for v in NAMES:
  sel[v]=[]; stsel[v]=Image.fromarray(module.selout(still[v])[0])
  for i,a in enumerate(frames[v]):
   z=Image.fromarray(module.selout(a)[0]);z.save(sd/f'{v}_f{i}.png');sel[v].append(z)
 def board(scale,path):
  cw=192*scale;ch=192*scale+20;b=Image.new('RGB',(7*cw,3*ch),(128,128,128));d=ImageDraw.Draw(b)
  for r,v in enumerate(NAMES):
   for c,z in enumerate([stsel[v]]+sel[v]):
    z=z.resize((cw,cw),Image.Resampling.NEAREST);b.paste(z,(c*cw,r*ch+20),z);d.text((c*cw+4,r*ch+4),v+' '+('still' if c==0 else 'f'+str(c-1)),fill='white')
  b.save(P/path)
 board(4,'review.png');board(1,'strip_1x.png')
 b=Image.new('RGB',(3*550,3*420),(128,128,128));d=ImageDraw.Draw(b)
 for r,v in enumerate(NAMES):
  for c,i in enumerate([2,3,4]):
   z=sel[v][i].crop((40,85,150,165)).resize((550,400),Image.Resampling.NEAREST);b.paste(z,(c*550,r*420+20),z);d.text((c*550+5,r*420+4),v+' f'+str(i)+' hips and legs 5x',fill='white')
 b.save(P/'joints_5x.png')
 for v in NAMES:
  gifs=[]
  for z in sel[v]:
   bg=Image.new('RGB',(768,768),(128,128,128));z=z.resize((768,768),Image.Resampling.NEAREST);bg.paste(z,(0,0),z);gifs.append(bg)
  gifs[0].save(P/f'preview_{v}.gif',save_all=True,append_images=gifs[1:],duration=[100,100,100,200,300,300],loop=0,disposal=2,optimize=False)
 note('Step 5 complete: sel-out copies, labelled review 4x / strip 1x / joints 5x and three timed GIFs saved.');print('review assets complete')
if __name__=='__main__':main()
