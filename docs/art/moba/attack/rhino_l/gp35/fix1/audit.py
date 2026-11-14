"""Run1 audit adapted for fix1, preserving failed anatomy and poses."""
import json,importlib.util,sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from finish import P,TAKE,NAMES,CROSS,specks,note
R=P.parent/'run1'
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def iou(a,b):return float((a&b).sum()/(a|b).sum())
def main():
 meta=json.loads((P/'preparation.json').read_text());pl=json.loads((P/'placement.json').read_text());targets=json.loads((P/'targets.json').read_text());pal={tuple(bytes.fromhex(z['hex'])) for z in json.loads((TAKE/'palette.json').read_text())}
 still={v:arr(TAKE/'views_cam35_touchup'/f'{v}.png') for v in NAMES};frames={v:[arr((P if i in [2,3] else R)/'frames'/f'{v}_f{i}.png') for i in range(6)] for v in NAMES}
 data={};lines=[]
 def check(ok,name,detail):lines.append(('PASS' if ok else 'MISS')+' '+name+': '+detail)
 for v in NAMES:
  for i in [2,3]:
   a=frames[v][i];m=a[:,:,3]>0;px=a[m,:3];p=pl['frames'][f'{v}_f{i}'];soles=targets['views'][v]['soles'];hind=next(s for s in soles if s['leg']=='hind');base=np.array([[s['x'],s['y']] for s in soles if s['leg'].startswith('front')]);expect=base+targets['views'][v]['frames'][i]['front_feet_shift_px'];holes=nd.binary_fill_holes(m)&~m;sh=nd.binary_fill_holes(still[v][:,:,3]>0)&~(still[v][:,:,3]>0)
   data[f'{v}{i}']={'drift':float(np.linalg.norm(np.array(p['hind'])-[hind['x'],hind['y']])),'front_error':np.linalg.norm(np.array(p['front'])-expect,axis=1).tolist(),'eyes':int(np.all(px==[255,58,42],axis=1).sum()),'ink':float(np.all(px==[20,18,24],axis=1).mean()*100),'pieces':int(nd.label(m,CROSS)[1]),'specks':specks(a),'slits':int((holes&~sh).sum()),'palette_extra':len(set(map(tuple,px))-pal),'binary':bool(set(np.unique(a[:,:,3]))<={0,255}),'border':bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())}
 def values(k):return '; '.join(n+' '+str(z[k]) for n,z in data.items())
 check(all(z['drift']<=1 for z in data.values()),'hind soles',values('drift')+' px <=1')
 # Main round steel face traced visually, excluding bracket steel above/behind it.
 discs={'e':{'still':[137,145],2:[139,147],3:[139,147]},'se':{'still':[119,128],2:[122,130],3:[122,130]}}
 hips={};legs={};gaps={};oldhip={}
 def hip(a,v,top):
  rgb=a[:,:,:3].astype(int);y=(rgb[:,:,0]>rgb[:,:,1])&(rgb[:,:,1]>rgb[:,:,2]*1.18)&(a[:,:,3]>0);yy,xx=np.where(y[:top,62:67]);return int(yy.max())
 for v in NAMES:
  hips[v]={'still':hip(still[v],v,discs[v]['still'][0])};legs[v]={};gaps[v]={}
  sole=next(s['y'] for s in targets['views'][v]['soles'] if s['leg']=='hind')
  for tag,a in [('still',still[v]),(2,frames[v][2]),(3,frames[v][3])]:
   top,bottom=discs[v][tag];h=hip(a,v,top);hips[v][tag]=h;legs[v][tag]=sole-(top+bottom)/2;gaps[v][tag]=max(0,top-h-1)
  oldhip[v]={i:hip(frames[v][i],v,137 if v=='e' else 118) for i in [1,4]}
 check(all(abs(z[i]-z['still'])<=2 for z in legs.values() for i in [2,3]),'HIND LEG LENGTH',str(legs)+' px sole-to-disc-centre; <=2 delta; round steel face top/bottom '+str(discs)+' traced excluding bracket')
 check(all(abs(z[i]-z['still'])<=2 for z in gaps.values() for i in [2,3]),'above-disc run',str(gaps)+' rows between disc top and plate, <=2 delta')
 check(all(abs(z[i]-z['still'])<=3 for z in hips.values() for i in [2,3]),'HIP HEIGHT',str(hips)+' lowest yellow row in x62:66 immediately above disc; <=3 delta')
 check(all(max(z['front_error'])<=3 for z in data.values()),'front feet',values('front_error')+' px <=3; manually traced steel pads/dark sole row midpoint; boxes in placement.json')
 io={v:iou(frames[v][3][:,:,3]>0,still[v][:,:,3]>0) for v in NAMES};check(all(z<=.85 for z in io.values()),'F3 alpha IoU',str(io)+' <=0.85')
 check(all(z['eyes']>=4 for z in data.values()),'eye pixels',values('eyes')+' >=4, red lenses in dark sockets')
 check(all(abs(z['ink']/({'e':8.1,'s':7.8}[n[0]])-1)<=.15 for n,z in data.items()),'ink %',values('ink')+' vs e8.1/se7.8 +/-15%')
 check(all(z['palette_extra']==0 and z['binary'] and not z['border'] for z in data.values()),'palette/alpha/border','extra colours '+values('palette_extra')+'; binary all '+str(all(z['binary'] for z in data.values()))+'; border contacts '+str(sum(z['border'] for z in data.values())))
 check(all(z['pieces']==1 and z['specks']<=({'e':386.4,'s':496.8}[n[0]]) for n,z in data.items()),'pieces/specks',values('pieces')+' pieces; specks '+values('specks')+' <=e386.4/se496.8; 0 despeckle passes')
 check(all(abs(z[k]/z['still_wh'][j]-1)<=.04 for z in meta['rows'].values() for j,k in enumerate(['width','height'])),'column1 size','; '.join(v+' '+str(z['width'])+'x'+str(z['height'])+' vs '+str(z['still_wh']) for v,z in meta['rows'].items())+' +/-4%')
 # Raw horn tip to eye centre, fixed scale in every cell.
 rawheads={'e2':[[894,123],[889,224]],'e3':[[1397,55],[1392,161]],'se2':[[872,632],[851,733]],'se3':[[1372,564],[1353,666]]};he={n:100*(np.linalg.norm(np.subtract(*pts))*meta['median_factor']/meta['heads']['se' if n.startswith('se') else 'e']['still_length']-1) for n,pts in rawheads.items()};he.update({v+'col1':z['head_error']*100 for v,z in meta['rows'].items()})
 check(all(abs(z)<=3 for z in he.values()),'head size',str({k:round(v,2) for k,v in he.items()})+' % error <=3; manual raw horn-tip/eye-centre')
 check(all(z['slits']==0 for z in data.values()),'seam slits',values('slits')+' enclosed transparent pixels absent from still mask')
 from defringe import clean
 fringe={n:list(clean(frames['se' if n.startswith('se') else 'e'][int(n[-1])])[1:]) for n in data};check(all(z[0]==0 and z[1]==0 for z in fringe.values()),'fringe',str(fringe)+' plum/pale/ink-rim')
 # Lens centroid gives repeatable head height; old front soles measured with run1 boxes/placement.
 oldpl=json.loads((R/'placement.json').read_text())
 cont={};ok=True
 for v in NAMES:
  def eye_y(a): yy,xx=np.where(np.all(a[:,:,:3]==[255,58,42],axis=2)&(a[:,:,3]>0));return float(yy.mean())
  heads=[eye_y(frames[v][i]) for i in [1,2,3]];feet=[oldpl['frames'][f'{v}_f1']['front'][0][1]]+[pl['frames'][f'{v}_f{i}']['front'][0][1] for i in [2,3]];hd=max(abs(hips[v][i]-oldhip[v][j]) for i in [2,3] for j in [1,4]);ok &= heads[0]>=heads[1]>=heads[2] and feet[0]>=feet[1]>=feet[2] and hd<=2;cont[v]={'head_y':heads,'front_sole_y':feet,'hip_max_delta':hd,'run1_hip_rows':oldhip[v]}
 check(ok,'continuity',str(cont)+'; F1>=F2>=F3 rows, hips <=2 px from run1 F1/F4')
 (P/'checks.txt').write_text('\n'.join(lines)+'\n');(P/'audit_metrics.json').write_text(json.dumps({'frames':data,'discs':discs,'hips':hips,'legs':legs,'gaps':gaps,'continuity':cont,'raw_head_landmarks':rawheads},indent=2));note('Step 4 complete: checks.txt records all PASS/MISS; no anatomy patched.');print('\n'.join(lines))
 # Selout function only; never execute source main.
 spec=importlib.util.spec_from_file_location('rhino_selout',TAKE/'anim/selout_rhino.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);(P/'frames_selout').mkdir(exist_ok=True)
 for v in NAMES:
  for i in [2,3]:Image.fromarray(mod.selout(frames[v][i])[0]).save(P/'frames_selout'/f'{v}_f{i}.png')
 def board(path,scale,items):
  cw=192*scale;ch=cw+20;b=Image.new('RGB',(len(items)*cw,2*ch),(128,128,128));d=ImageDraw.Draw(b)
  for r,v in enumerate(NAMES):
   for c,(label,key) in enumerate(items):
    a=still[v] if key=='still' else arr(R/'frames'/f'{v}_f3.png') if key=='old' else frames[v][key];im=Image.fromarray(a).resize((cw,cw),Image.Resampling.NEAREST);b.paste(im,(c*cw,r*ch+20),im);d.text((c*cw+4,r*ch+3),v+' '+label,fill='white')
  b.save(P/path)
 board('review.png',4,[('still','still'),('run 1 f1',1),('fix1 f2',2),('fix1 f3',3),('run 1 f4',4),('run 1 f3 (old)','old')]);board('strip_1x.png',1,[(f'f{i}',i) for i in range(6)])
 b=Image.new('RGB',(750,740),(128,128,128));d=ImageDraw.Draw(b)
 for r,v in enumerate(NAMES):
  for c,(lab,a) in enumerate([('still',still[v]),('fix1 f3',frames[v][3]),('run 1 f3 (old)',arr(R/'frames'/f'{v}_f3.png'))]):
   im=Image.fromarray(a).crop((45,95,95,165)).resize((250,350),Image.Resampling.NEAREST);b.paste(im,(c*250,r*370+20),im);d.text((c*250+4,r*370+3),v+' '+lab,fill='white')
 b.save(P/'legs_5x.png')
 for v in NAMES:
  ims=[]
  for a in frames[v]:
   im=Image.fromarray(a).resize((768,768),Image.Resampling.NEAREST);bg=Image.new('RGB',(768,768),(128,128,128));bg.paste(im,(0,0),im);ims.append(bg)
  ims[0].save(P/f'preview_{v}.gif',save_all=True,append_images=ims[1:],duration=[100,100,100,200,300,300],loop=0,disposal=2,optimize=False)
 note('Step 5 complete: four selout copies, review.png, strip_1x.png, legs_5x.png, two timed GIFs; all source frames unaltered.')
if __name__=='__main__':main()
