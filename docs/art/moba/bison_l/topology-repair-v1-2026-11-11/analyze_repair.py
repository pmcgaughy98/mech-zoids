import sys,json,collections
from pathlib import Path
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent
d,b=read_glb('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bison_remeshed_25k_20261108_character.glb');pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);mp,edges,groups,deg=topology(p,t)
print('BOUNDARY SIGNATURES',dict(collections.Counter((len(g['vertices']),g['edge_count']) for g in groups)))
for g in groups:
 if not (len(g['vertices'])==3 and g['edge_count']==2):print('NON-FIN',json.dumps(g))
j=accessor(d,b,pr['attributes']['JOINTS_0']);w=accessor(d,b,pr['attributes']['WEIGHTS_0']);rows=[]
for bi,ni in enumerate(d['skins'][0]['joints']):
 bw=(w*(j==bi)).sum(1);sel=bw>.3
 if sel.any():rows.append({'bone':d['nodes'][ni]['name'],'influenced_vertices':int(sel.sum()),'center_gltf':p[sel].mean(0).tolist(),'range':[p[sel].min(0).tolist(),p[sel].max(0).tolist()]})
(ROOT/'joint-influence-regions.json').write_text(json.dumps(rows,indent=2))
print('JOINT CENTERS',json.dumps([{'bone':v['bone'],'n':v['influenced_vertices'],'center':v['center_gltf']} for v in rows]))
