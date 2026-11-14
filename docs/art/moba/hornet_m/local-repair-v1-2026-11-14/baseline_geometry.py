import sys,json,hashlib,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;source=Path('D:/user/Downloads/hornet_front - 6 legs touchup.glb');d,b=read_glb(source);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);m,e,g,deg=topology(p,t);print('BASELINE',len(p),len(t),'BOUNDARY',sum(len(v)==1 for v in e.values()),'OVER',sum(len(v)>2 for v in e.values()),'GROUPS',len(g),'DEG',len(deg),flush=True);print('NODES',d['nodes'],flush=True)
cfg=json.loads((ROOT/'input-audit.json').read_text());rd,rb=read_glb(cfg['source']);print('RIG_MESH_NODES',[n for n in rd['nodes'] if 'mesh' in n],flush=True);lo=p.min(0);hi=p.max(0);scale=1.7/(hi[1]-lo[1]);shift=np.array([-(lo[0]+hi[0])/2*scale,-lo[1]*scale,-(lo[2]+hi[2])/2*scale]);aligned=p*scale+shift;rp=accessor(rd,rb,rd['meshes'][0]['primitives'][0]['attributes']['POSITION']);dist=cKDTree(rp).query(aligned)[0];print('ALIGN',scale,shift,'DIST',np.percentile(dist,[50,90,99,100]).tolist(),flush=True)
adj=[set() for _ in t]
for fs in e.values():
 if len(fs)==2:a,c=fs;adj[a].add(c);adj[c].add(a)
seen=set();comps=[]
for start in range(len(t)):
 if start in seen:continue
 stack=[start];part=set()
 while stack:
  f=stack.pop()
  if f in part:continue
  part.add(f);stack.extend(adj[f]-part)
 seen.update(part);ids=np.array(sorted(part));pts=p[t[ids]];ee={edge:fs for edge,fs in e.items() if any(f in part for f in fs)};comps.append({'faces':ids.tolist(),'count':len(ids),'boundary_edges':sum(len(fs)==1 for fs in ee.values()),'over_shared_contacts':sum(len(fs)>2 for fs in ee.values()),'bounds':[pts.reshape(-1,3).min(0).tolist(),pts.reshape(-1,3).max(0).tolist()],'signed_volume':float(np.einsum('ij,ij->i',pts[:,0],np.cross(pts[:,1],pts[:,2])).sum()/6)})
print('COMPONENTS',collections.Counter((c['count'],c['boundary_edges'],c['over_shared_contacts']) for c in comps),flush=True);print('HOLES',[(x['edge_count'],x['min'],x['max']) for x in g if x['edge_count']>2][:15],flush=True)
(ROOT/'baseline-components.json').write_text(json.dumps(comps,indent=2));(ROOT/'baseline-geometry-audit.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'triangles':len(t),'boundary_edges':sum(len(v)==1 for v in e.values()),'over_shared_edges':sum(len(v)>2 for v in e.values()),'groups':g,'alignment_scale':float(scale),'alignment_shift':shift.tolist(),'nearest_rig_vertex_distance_percentiles':np.percentile(dist,[50,90,99,100]).tolist()},indent=2))
