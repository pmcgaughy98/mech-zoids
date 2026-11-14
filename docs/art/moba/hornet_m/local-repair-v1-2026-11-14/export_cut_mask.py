from pathlib import Path
import sys
ROOT=Path(__file__).parent
s=Path('D:/dev/_scratch/proportions-2026-11-10/tools/segment.py').read_text();s=s[:s.index("if MODE == 'label':")]
s=s.replace("bpy.ops.import_scene.gltf(filepath=os.path.join(d, 'display_before.glb'))","bpy.ops.import_scene.gltf(filepath='D:/dev/_scratch/hornet-inner-leg-touchup-2026-11-10/hornet/display_before.glb')")
s+='''
import numpy as np
faces=list(bm.faces);coords=np.array([[tuple(mw@v.co) for v in f.verts] for f in faces],dtype=np.float32)
selected=['FL1','FL2','FR1','FR2','L2','L4','R2','R4'];removed=np.array([fc>=0 and comps[fc]['label'] in selected for fc in fcomp]);assert int(removed.sum())==4939,int(removed.sum())
np.savez('D:/dev/_scratch/mech-art-direction/hornet-review-2026-11-14/accepted-cut-mask.npz',triangles=coords,removed=removed)
print('EXPORTED ACCEPTED HORNET CUT MASK',len(faces),int(removed.sum()),flush=True)
'''
sys.argv=['blender','--','D:/dev/_scratch/hornet-inner-leg-touchup-2026-11-10','mask','hornet','.12'];exec(compile(s,'accepted_hornet_segmentation','exec'))
