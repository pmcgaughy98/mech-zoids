from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,struct,hashlib,io
out=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-transfer-2026-11-10')
paths={
 'marked_backplate_donor':Path('D:/user/Downloads/shoebill_front - Hunyuan 3D v3.1 Pro (1)(correct moon plate on back only use for that other model is best).glb'),
 'designated_recipient':Path('D:/user/Downloads/shoebill_front - Hunyuan 3D v3.1 Pro.glb')
}
rows=[]
for role,path in paths.items():
 data=path.read_bytes()
 n,t=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+n])
 offset=20+n;n,t=struct.unpack_from('<II',data,offset);binary=data[offset+8:offset+8+n]
 images=[]
 for image in d.get('images',[]):
  v=d['bufferViews'][image['bufferView']];i=v.get('byteOffset',0)
  im=Image.open(io.BytesIO(binary[i:i+v['byteLength']]))
  images.append({'name':image.get('name'),'dimensions':list(im.size)})
 rows.append({'role':role,'path':str(path),'bytes':len(data),'mtime_utc':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'triangles':sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives']),
 'node_count':len(d.get('nodes',[])),'node_names':[node.get('name') for node in d.get('nodes',[])],
 'skin_count':len(d.get('skins',[])),'joint_count':sum(len(s.get('joints',[])) for s in d.get('skins',[])),
 'nodes_referencing_a_skin':sum('skin' in node for node in d.get('nodes',[])),
 'primitive_attributes':[list(p.get('attributes',{})) for m in d['meshes'] for p in m['primitives']],
 'animation_names':[a.get('name') for a in d.get('animations',[])],'images':images})
report={'status':'Missing verified rigged recipient. No transfer performed. Both source files read-only.','sources':rows,'source_search':'D:/user/Downloads and C:/Users/pmcga/Downloads including nested files; shoebill-named scratch paths. No newer shoebill model or designated rigged variant found.','reference_review':['docs/art/moba/shoebill_m/take-i-sidefix-original/white_views/review.png','docs/art/moba/shoebill_m/take-g-power/white_views/review.png'],'missing_requirement':'Current shoebill export with actual skeleton/skin weights. Designated November 10 file is one static mesh node with no skin or joint attributes.'}
(out/'source-inspection.json').write_text(json.dumps(report,indent=2))
print(json.dumps(rows,indent=2))
