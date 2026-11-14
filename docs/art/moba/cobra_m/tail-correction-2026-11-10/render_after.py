import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
out=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/tail-correction-2026-11-10')
bpy.ops.wm.open_mainfile(filepath='D:/dev/_scratch/mech-art-direction/cobra-tail-2026-11-10/before-scene.blend')
for ob in list(bpy.data.objects):
 if ob.type=='MESH':bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'cobra_front - single tail corrected.glb'))
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bm=bmesh.new();bm.from_mesh(ob.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
areas=[f.calc_area() for f in bm.faces]
audit={'boundary_edges_after_seam_weld':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges_after_seam_weld':sum(not e.is_manifold for e in bm.edges),'strict_zero_area_faces':sum(a==0 for a in areas),'positive_area_faces_under_1e_12':sum(0<a<1e-12 for a in areas),'minimum_positive_face_area':min(a for a in areas if a>0),'vertices_after_seam_weld':len(bm.verts),'faces':len(bm.faces)}
bm.free()
(out/'export-reimport-audit.json').write_text(json.dumps(audit,indent=2))
if '--audit-only' in sys.argv:
 print(json.dumps(audit),flush=True)
 raise SystemExit
settings=json.loads((out/'render-settings.json').read_text())
center=Vector(settings['center']);cam=bpy.context.scene.camera
for name,offset in settings['views']:
 cam.location=center+Vector(offset)
 cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.scene.render.filepath=str(out/f'after-{name}.png')
 bpy.ops.render.render(write_still=True)
print('CORRECTED COBRA RENDER COMPLETE',json.dumps(audit),flush=True)
