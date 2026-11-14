from pathlib import Path
import ast,json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
C=Path(__file__).resolve().parent;R=C.parent
ns={'__file__':str(C/'cleanup.py')};exec(compile((C/'cleanup.py').read_text().split('for view,legs in D.items():')[0],'setup','exec'),ns)
D,P,lmask,shift,fp,T,B=[ns[k] for k in ['D','P','lmask','shift','fp','T','B']]
vt=ast.parse((R/'verify.py').read_text());b=type('B',(),{'fp':staticmethod(fp)})();env={'np':np,'b':b}
exec(compile(ast.Module(body=[n for n in vt.body if isinstance(n,ast.FunctionDef) and n.name=='measure'],type_ignores=[]),'measure','exec'),env);measure=env['measure']
lines=['CLEAN WALK35: native saved-pixel audit','Dark = #141218/#211e27/#3d3a44; 4 neighbours must all be source gold/grey (opaque, neither dark nor red).','Contacts: exhaustive original foot lower-row pixel match in composite, independent of targets.','Fully occluded feet: saved limb pixels only; cannot measure an invisible contact in a composite.'];fails=[];result={}
def noise(a,region):
 dark=np.isin(a[:,:,:3].astype('uint32')@np.array([65536,256,1]),[0x141218,0x211e27,0x3d3a44])&(a[:,:,3]>0)
 material=(a[:,:,3]>0)&~dark&~np.all(a[:,:,:3]==[255,58,42],axis=2)
 p=np.pad(material,1);inside=p[:-2,1:-1]&p[2:,1:-1]&p[1:-1,:-2]&p[1:-1,2:]
 return int((dark&inside&region).sum())
for v,legs in D.items():
 ref=np.array(Image.open(B/'views_cam35'/f'{v}.png'));body=np.array(Image.open(R/'walk/layers'/f'{v}_body.png'))
 olds=[np.array(Image.open(R/'walk/frames'/f'{v}_f{f}.png')) for f in range(8)];news=[np.array(Image.open(C/'walk/frames'/f'{v}_f{f}.png')) for f in range(8)]
 rr={'noise':[],'structure':[],'feet':{}};result[v]=rr
 for f,(old,a) in enumerate(zip(olds,news)):
  pin=shift(body,0,int(f in (0,4)))[:,:,3]>0

  diff=int(np.any(a!=old,axis=2)[pin].sum());n0=noise(old,~pin);n1=noise(a,~pin);rr['noise'].append([n0,n1])
  op=a[:,:,3]>0;_,components=ndi.label(op,np.ones((3,3)));holes=int((ndi.binary_fill_holes(op)&~op).sum());palette=set(map(tuple,a[op]))<=set(P);edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any());binary=bool(np.isin(a[:,:,3],[0,255]).all());lowest=int(np.where(op)[0].max());same_low=lowest==int(np.where(old[:,:,3]>0)[0].max())
  st={'frame':f,'upper_changed_pixels':diff,'upper_changed_pct':100*diff/int(pin.sum()),'noise_run1_clean':[n0,n1],'components':components,'hole_pixels':holes,'palette':palette,'binary_alpha':binary,'edge':edge,'lowest':lowest,'lowest_same':same_low,'size':list(a.shape[:2])};rr['structure'].append(st);lines.append(f'FRAME {v} '+json.dumps(st))
  if diff or n1 or components!=1 or holes or not palette or not binary or edge or not same_low:fails.append(f'{v} f{f} structure/noise/body')
 hidden={'LH':('RH',(0,-16)),'LF':('RF',(0,-16))} if v=='e' else {'LF':('RF',(-24,-17 if v=='se' else -10))}
 for name in ['LH','RH','LF','RF']:
  hiddenfoot=name not in legs;donor,delta=hidden[name] if hiddenfoot else (name,(0,0));q=legs[donor];foot=ref.copy();foot[~lmask(v,donor,q)]=0;foot[ns['Y']<q[4]]=0;foot=shift(foot,*delta)
  pp=[];oldpp=[];scores=[]
  for f in range(8):
   if hiddenfoot:
    oa=np.array(Image.open(R/'walk/layers'/f'{v}_{name}_f{f}.png'));aa=np.array(Image.open(C/'walk/layers'/f'{v}_{name}_f{f}.png'));p,_=fp(aa);p0,_=fp(oa);score=1.
   else:
    p,score,dxy,vis=measure(news[f],foot);p0,_,_,_=measure(olds[f],foot)
   pp.append(p);oldpp.append(p0);scores.append(score)
  err=np.abs(np.array(pp)-oldpp);land=(T['gait'][name]+3)%8;order=[(land+k)%8 for k in range(5)];step=np.array(T['views'][v]['planted_step_px']);spread=np.ptp([pp[f]-k*step for k,f in enumerate(order)],axis=0)
  out={'evidence':'isolated limb PNG (occluded)' if hiddenfoot else 'complete frame pixels','max_difference_xy':err.max(axis=0).tolist(),'lock_spread_xy':spread.tolist(),'contacts':np.array(pp).tolist(),'run1_contacts':np.array(oldpp).tolist(),'min_match':min(scores),'lowest_rows_equal':bool((err[:,1]==0).all())};rr['feet'][name]=out;lines.append(f'FOOT {v} {name} '+json.dumps(out))
  if err.max()>.5 or spread.max()>2 or not out['lowest_rows_equal'] or min(scores)<.8:fails.append(f'{v} {name} contacts')
 for suffix in ['gif','apng']:
  im=Image.open(C/f'{v}_preview.{suffix}');dur=[]
  for f in range(im.n_frames):im.seek(f);dur.append(im.info['duration'])
  lines.append(f'TIMING {v} {suffix}: {dur}')
lines.append('FAILURES '+repr(fails));(C/'checks.txt').write_text('\n'.join(lines)+'\n');(C/'verification.json').write_text(json.dumps(result,indent=2));print('\n'.join([l for l in lines if l.startswith(('FOOT','FAILURES'))]));print('NOISE',{v:r['noise'] for v,r in result.items()})
