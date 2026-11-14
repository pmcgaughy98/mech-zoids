from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R=Path(r'D:\dev\new-mech-rpg\docs\art\moba\wolf_m\take-b\anim\codex-tailfix')
rec=json.loads((R/'measurements.json').read_text())
u=np.array([-20.,29.]);u/=np.linalg.norm(u);normal=np.array([-u[1],u[0]])
def width(mask,start,axis,norm):
 result=[]
 for station in [3,12,21]:
  ds=np.arange(-16,16.001,.025);pos=np.rint(start+station*axis+ds[:,None]*norm).astype(int);on=mask[pos[:,1],pos[:,0]];labs,k=ndi.label(on)
  # The run through the plate center; masks contain only the tail.
  lengths=[(labs==j).sum()*.025 for j in range(1,k+1)]
  result.append(round(max(lengths),2) if lengths else 0)
 return result
refmask=np.array(Image.open(R/'reference_tail.png'))[:,:,3]>0
refwidth=width(refmask,np.array([62.,125.]),u,normal)
checks=[]
for r in rec:
 m,i=r['move'],r['frame'];p=R/m/'frames'/f'side_f{i}.png';a=np.array(Image.open(p).convert('RGBA'));old=np.array(Image.open(R.parent/'codex-set-a'/m/'frames'/p.name).convert('RGBA'))
 theta=math.radians(r['rotation_deg']);rot=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
 root=np.array(r['root']);start=root+rot@(np.array([62,125])-np.array([68,122]));end=root+rot@(np.array([42,154])-np.array([68,122]));startpix=np.rint(start).astype(int);endpix=np.rint(end).astype(int)
 tm=np.array(Image.open(R/m/f'new_tail_mask_f{i}.png'))>0;om=np.array(Image.open(R/m/f'old_tail_mask_f{i}.png'))>0;diff=np.any(a!=old,2);op=a[:,:,3]>0
 r.update(thickness_cross_sections=width(tm,start,rot@u,rot@normal),tail_axis_start=startpix.tolist(),tail_axis_end=endpix.tolist(),length_axis_inclusive=round(float(np.linalg.norm(endpix-startpix)+1),2),reference_thickness=refwidth,plates=4)
 palette=set(tuple(bytes.fromhex(c)) for c in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split())
 c=dict(move=m,frame=i,canvas=a.shape== (192,192,4),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),palette=all(tuple(rgb) in palette for rgb in a[op,:3]),bottom=int(np.where(op)[0].max()),edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any()),components=ndi.label(op,np.ones((3,3)))[1],holes=int((ndi.binary_fill_holes(op)&~op).sum()),old_tail_remaining_outside_new=int((om&~tm&op&~(np.array(Image.open(R/m/f'join_mask_f{i}.png'))>0)).sum()),outside_tail_pixels=int((diff&~(om|tm)).sum()),bounds=Image.open(p).getbbox(),source_unchanged=hashlib.sha256((R.parent/'codex-set-a'/m/'frames'/p.name).read_bytes()).hexdigest()==r['source_sha256'])
 checks.append(c)
for m,n,ms in [('walk',8,100),('sprint',6,70)]:
 g=Image.open(R/m/'preview.gif');ds=[]
 for i in range(g.n_frames):g.seek(i);ds.append(g.info['duration'])
 assert g.n_frames==n and ds==[ms]*n and g.info['loop']==0
for c in checks:
 assert c['canvas'] and c['binary_alpha'] and c['palette'] and c['bottom']<=160 and not c['edge'] and c['components']==1 and c['old_tail_remaining_outside_new']==0 and c['source_unchanged'],c
(R/'measurements.json').write_text(json.dumps(rec,indent=2)+'\n');(R/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print('reference widths',refwidth)
for r,c in zip(rec,checks):print(r['move'],r['frame'],r['thickness_cross_sections'],r['length_axis_inclusive'],'outside',c['outside_tail_pixels'],'holes',c['holes'],'bounds',c['bounds'])
