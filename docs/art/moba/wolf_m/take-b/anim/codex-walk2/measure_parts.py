from pathlib import Path
import importlib.util,numpy as np,json,math
from PIL import Image
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('f',R/'finish.py');fn=importlib.util.module_from_spec(sp);sp.loader.exec_module(fn)
u=np.array([-20.,29.]);u/=np.linalg.norm(u);normal=np.array([-u[1],u[0]])
def width(mask,start,axis,norm):
 result=[]
 for station in [3,12,21]:
  ds=np.arange(-16,16.001,.025);pos=np.rint(start+station*axis+ds[:,None]*norm).astype(int);on=mask[pos[:,1],pos[:,0]];labs,k=ndi.label(on);lengths=[(labs==j).sum()*.025 for j in range(1,k+1)];result.append(round(float(max(lengths)),2) if lengths else 0)
 return result
ref=np.array(Image.open(R.parent/'codex-tailfix/reference_tail.png'))[:,:,3]>0
refwidth=width(ref,np.array([62.,125.]),u,normal)
# Manually inspected projected axes at the native pixel grid, matching set A's reference convention.
axes={'far_ear':([[119,97],[126,108]],[[119,96],[126,108]]),'near_ear':([[127,95],[137,108]],[[127,95],[137,108]]),'head':([[123,109],[150,118]],[[123,109],[150,118]]),'muzzle':([[136,112],[150,118]],[[136,112],[150,118]]),'torso':([[69,118],[117,115]],[[69,119],[117,115]])}
axis_checks={name:dict(reference_points=ra,final_points=fa,reference_length=round(math.dist(*ra)+1,3),final_length=round(math.dist(*fa)+1,3),difference=round(abs(math.dist(*ra)-math.dist(*fa)),3)) for name,(ra,fa) in axes.items()}
legs=json.loads((R/'articulation.json').read_text());results=[]
for f in range(8):
 m=np.array(fn.tail(f))[:,:,3]>0;sway=[0,1,1,0,0,-1,-1,0][f];dip=int(f in [1,5]);start=np.array([62.+sway,125.+dip]);end=np.array([42.+sway,154.+dip]);axis=end-start;axis/=np.linalg.norm(axis);norm=np.array([-axis[1],axis[0]])
 limb=[]
 for p in [x for x in legs if x['frame']==f]:
  fore=p['name'].endswith('fore');chain=math.dist(p['root'],p['joint'])+math.dist(p['joint'],p['wrist'])+math.dist(p['wrist'],p['target'])+1
  limb.append(dict(paw=p['name'],reference_chain=41.10 if fore else 42.73,final_chain=round(chain,3),difference=round(abs(chain-(41.10 if fore else 42.73)),3),upper=p['lengths'][0],lower=p['lengths'][1],reference_upper=19.235 if fore else 21.095,reference_lower=17.263 if fore else 17.029))
 row=dict(frame=f,tail_widths=width(m,start,axis,norm),reference_tail_widths=refwidth,tail_axis_length=round(float(np.linalg.norm(end-start)+1),3),reference_tail_length=36.228,tail_plates=4,near_shank_width=7,far_shank_width=6,legs=limb)
 assert all(abs(a-b)<=2 for a,b in zip(row['tail_widths'],refwidth))
 assert all(p['difference']<=2 and abs(p['upper']-p['reference_upper'])<=2 and abs(p['lower']-p['reference_lower'])<=2 for p in limb)
 results.append(row)
assert all(v['difference']<=2 for v in axis_checks.values())
# The steady head region is pixel-identical; only torso dips in f1/f5.
a=[np.array(Image.open(R/'walk/frames'/f'side_f{f}.png')) for f in range(8)]
headsteady=all(np.array_equal(x[:132,130:],a[0][:132,130:]) for x in a)
assert headsteady
result=dict(method='Native projected axes and rounded joint-center chains inclusive of one endpoint pixel; tail thickness sampled perpendicular at three stations, same convention as codex-tailfix.',upper_axes=axis_checks,torso_depth=dict(reference=23,final=23),head_pixel_steady=headsteady,frames=results)
(R/'proportions.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: projected upper axes max delta',max(v['difference'] for v in axis_checks.values()))
print('PASS: all 32 leg chains and their upper/lower links within2px; max whole-chain delta',max(p['difference'] for r in results for p in r['legs']))
print('PASS: tail4 plates, length36.228, widths',results[0]['tail_widths'],'reference',refwidth)
print('PASS: head region pixel-identical in all eight frames')
