from pathlib import Path
import sys
root=Path(__file__).parent
s=Path('D:/dev/_scratch/proportions-2026-11-10/tools/segment.py').read_text();s=s[:s.index("if MODE == 'label':")]
s=s.replace("bpy.ops.import_scene.gltf(filepath=os.path.join(d, 'display_before.glb'))","bpy.ops.import_scene.gltf(filepath='D:/dev/_scratch/proportions-2026-11-10/mantis/display_before.glb')")
s+='''
import numpy as np
faces=list(bm.faces)
coords=np.array([[tuple(mw@v.co) for v in f.verts] for f in faces],dtype=np.float32)
assert coords.shape[1:]==(3,3)
removed=np.array([fc>=0 and comps[fc]['label'] in ['FL1','FR1','L3','R3'] for fc in fcomp])
np.savez('D:/dev/_scratch/mech-art-direction/mantis-review-2026-11-10/accepted-cut-mask.npz',triangles=coords,removed=removed)
print('EXPORTED CUT MASK',len(faces),int(removed.sum()),flush=True)
'''
sys.argv=['blender','--','D:/dev/_scratch/proportions-2026-11-10','mask','mantis','.12'];exec(compile(s,'accepted_segment_method','exec'))
