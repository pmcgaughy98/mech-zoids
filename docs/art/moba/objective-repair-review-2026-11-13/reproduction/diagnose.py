import json,struct,collections
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).parent
SOURCE=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_cobra_remeshed_25k_20261111_character.glb')
def read_glb(p):
 with Path(p).open('rb') as f:
  f.read(12);n,t=struct.unpack('<II',f.read(8));doc=json.loads(f.read(n));n,t=struct.unpack('<II',f.read(8));blob=f.read(n)
 return doc,blob
def accessor(doc,blob,idx):
 a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']];dt={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];dtype=np.dtype(dt)
 return np.ndarray((a['count'],c),dtype=dtype,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',c*dtype.itemsize),dtype.itemsize)).copy()
def topology(pos,tri):
 parent=np.arange(len(pos))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a,b in cKDTree(pos).query_pairs(1e-6):
  a=find(a);b=find(b);parent[b]=a
 mapping=np.array([find(i) for i in range(len(pos))]);wt=mapping[tri]
 edge=collections.defaultdict(list)
 deg=[]
 for f,t in enumerate(wt):
  if len(set(t))<3:deg.append(f)
  for a,b in zip(t,np.roll(t,-1)):edge[tuple(sorted((int(a),int(b))))].append(f)
 boundary=[e for e,v in edge.items() if len(v)==1];adj=collections.defaultdict(set)
 for a,b in boundary:adj[a].add(b);adj[b].add(a)
 seen=set();groups=[]
 for a in adj:
  if a in seen:continue
  stack=[a];verts=set()
  while stack:
   b=stack.pop()
   if b in verts:continue
   verts.add(b);stack.extend(adj[b]-verts)
  seen.update(verts);pts=pos[list(verts)];groups.append({'vertices':sorted(verts),'edge_count':sum(len(adj[v]) for v in verts)//2,'degrees':dict(collections.Counter(len(adj[v]) for v in verts)),'min':pts.min(0).tolist(),'max':pts.max(0).tolist(),'center':pts.mean(0).tolist()})
 return mapping,edge,groups,deg
if __name__=='__main__':
 d,b=read_glb(SOURCE);p=d['meshes'][0]['primitives'][0];pos=accessor(d,b,p['attributes']['POSITION']);tri=accessor(d,b,p['indices']).reshape(-1,3);mapping,edge,groups,deg=topology(pos,tri)
 report={'coordinate_system':'glTF Y up','boundary_components':groups,'boundary_edges':sum(len(v)==1 for v in edge.values()),'edges_over_two_faces':sum(len(v)>2 for v in edge.values()),'collapsed_triangles':deg,'same_vertex_triangle_duplicates':len(tri)-len(set(tuple(sorted(t)) for t in mapping[tri]))}
 (ROOT/'cobra-topology-diagnosis.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
