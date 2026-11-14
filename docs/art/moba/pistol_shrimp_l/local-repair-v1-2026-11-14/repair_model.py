import copy, hashlib, itertools, json, struct, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb, accessor, topology
ROOT=Path(__file__).parent
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/pistol_shrimp_l/local-repair-v1-2026-11-14')
cfg=json.loads((ROOT/'input-audit.json').read_text())
d,b=read_glb(cfg['source']);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0]
p=accessor(d,b,pr['attributes']['POSITION']);n=accessor(d,b,pr['attributes']['NORMAL']);uv=accessor(d,b,pr['attributes']['TEXCOORD_0']);t=accessor(d,b,pr['indices']).reshape(-1,3)
components=json.loads((ROOT/'face-components.json').read_text())
removed=sorted(f for c in components if c['count']==1 and c['boundary_edges']==2 and c['over_shared_contacts']==1 for f in c['faces']);assert len(removed)==10
new=np.delete(t,removed,axis=0);mp,edges,groups,deg=topology(p,new);assert len(groups)==1 and len(groups[0]['vertices'])==3 and groups[0]['edge_count']==2
g=groups[0];ids=set(g['vertices']);edge,fs=next((edge,fs) for edge,fs in edges.items() if len(fs)==1 and set(edge)<=ids);ft=new[fs[0]]
a,c=next((int(a),int(c)) for a,c in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[a]),int(mp[c]))))==edge)
order=[int(mp[c]),int(mp[a]),next(iter(ids-{int(mp[a]),int(mp[c])}))];choices=[]
for raw in itertools.product(*(np.where(mp==vi)[0].tolist() for vi in order)):
    pts=p[list(raw)];normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);normal/=max(np.linalg.norm(normal),1e-12);alignment=float(normal@n[list(raw)].mean(0))
    if alignment>.25:
        perimeter=sum(float(np.linalg.norm(uv[raw[i]]-uv[raw[(i+1)%3]])) for i in range(3));choices.append((perimeter,list(raw),normal.tolist(),alignment))
assert choices
perimeter,raw,normal,alignment=min(choices)
new=np.concatenate([new,np.array([raw])]);mapping,final_edges,gg,dd=topology(p,new);assert not gg and not dd
contacts=[]
for edge,fs in final_edges.items():
    if len(fs)==2:continue
    assert len(fs)==4
    directions=[int(a<c) for fi in fs for a,c in zip(mapping[new[fi]],np.roll(mapping[new[fi]],-1)) if tuple(sorted((int(a),int(c))))==edge]
    assert sum(directions)==2
    contacts.append({'edge':list(edge),'incident_faces':len(fs),'balanced_orientation':True})
assert len(contacts)==2
out=b+b'\0'*(-len(b)%4);offset=len(out);assert new.max()<65536
array=new.astype('<u2').reshape(-1,1);data=array.tobytes();out+=data;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':34963});ai=len(d['accessors']);d['accessors'].append({'bufferView':vi,'componentType':5123,'count':len(array),'type':'SCALAR'});pr['indices']=ai;d['buffers'][0]['byteLength']=len(out)
js=json.dumps(d,separators=(',',':')).encode();js+=b' '*(-len(js)%4);out+=b'\0'*(-len(out)%4)
dest=OUT/'pistol-shrimp-rigged-local-repair-v1.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(out))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(out),0x004e4942)+out)
for key in ['nodes','skins','materials','images','textures','samplers','scene','scenes','animations']:assert d.get(key)==original.get(key),key
report={'source':cfg['source'],'source_sha256':cfg['sha256'],'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'before_triangles':len(t),'final_triangles':len(new),'joint_count':53,'removed_malformed_triangles':len(removed),'removed_face_ids':removed,'holes_closed':[{'triangle':raw,'bounds':[g['min'],g['max']],'normal':normal,'normal_alignment':alignment,'uv_perimeter':perimeter}],'boundary_edges':0,'over_shared_edges':len(contacts),'protected_closed_contact_edges':contacts,'collapsed_triangles':0,'healthy_source_faces_retained':len(t)-len(removed),'all_original_vertex_attribute_rows_weights_materials_skeleton_rest_binds_preserved':True,'new_geometric_vertices':0,'scope':'Remove ten verified single-triangle flaps and close one tiny large-claw opening using original vertex corners. Retain snapping claw, smaller claw, eight walking legs, two antennae, two dorsal vessels and tail fan. Preserve original vertex/skin rows, 53-joint hierarchy/rest/binds and materials/textures. No remesh or rerig.','limitations':'Two balanced original closed-surface assembly contacts remain on the large claw. Existing baked surface roughness and grouped rig controls remain. No authored clips or gameplay replacement.'}
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
