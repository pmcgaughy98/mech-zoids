from pathlib import Path
import ast,json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
R=Path(__file__).parent
# Read constants and trace functions without rebuilding.
tree=ast.parse((R/'build.py').read_text());env={}
keep=[]
for n in tree.body:
 if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)):keep.append(n)
 elif isinstance(n,ast.Assign) and not any(isinstance(z,ast.Call) and isinstance(z.func,ast.Attribute) and z.func.attr in ['write_text','mkdir','save'] for z in ast.walk(n)):
  if n.lineno<80:keep.append(n)
# Simpler explicit load of just the pre-build module text.
s=(R/'build.py').read_text().split("(R/'walk/frames').mkdir")[0];env={'__file__':str(R/'build.py')};exec(s,env)
D=env['D'];trace=env['trace'];rig=json.loads((R/'rig.json').read_text())
def widths(a,start,end):
 m=np.array(a)[:,:,3]>0;s=np.array(start,float);v=np.array(end,float)-s;u=v/np.linalg.norm(v);n=np.array([-u[1],u[0]]);ds=np.arange(-20,20.001,.02);out=[]
 for frac in [.25,.5,.75]:
  p=np.floor(s+v*frac+ds[:,None]*n+.5).astype(int);on=m[p[:,1],p[:,0]];lab,k=ndi.label(on);out.append(round(max([(lab==j).sum()*.02 for j in range(1,k+1)],default=0)))
 return out
for view,legs in D.items():
 ref=np.array(Image.open(R.parents[1]/'fixed'/f'{view}.png').convert('RGBA'))
 for name,q in legs.items():
  for tag,aa,bb,ix in [('upper',0,1,4),('shank',1,2,5)]:
   rw=widths(trace(ref,q[ix]),q[aa],q[bb]);ws=[]
   for rec in [r for r in rig[view] if r['name']==name]:
    a=Image.open(R/'walk/layers'/f"{view}_{name}_{tag}_f{rec['frame']}.png");w=widths(a,rec['root' if aa==0 else 'joint'],rec['joint' if bb==1 else 'ankle']);ws.append(w)
   delta=np.max(np.abs(np.array(ws)-rw));print(view,name,tag,rw,np.min(ws,axis=0),np.max(ws,axis=0),'delta',delta)
