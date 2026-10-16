import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[2]/'art/rooms/hangar_bay/source/hangar_bay_form.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
d=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
    if not o.get('heroAsset'):continue
    if o.type=='ARMATURE':
        print('ARMATURE',o.name,o.location[:],o.data.pose_position)
    if o.type!='MESH':continue
    ev=o.evaluated_get(d);m=ev.to_mesh()
    used={i for f in m.polygons for i in f.vertices}
    def bounds(ids):
        pts=[ev.matrix_world@m.vertices[i].co for i in ids]
        return [[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]]
    print('HERO_MESH',o.name,'hiddenRender',o.hide_render,'hiddenViewport',o.hide_viewport,'parent',o.parent.name if o.parent else None,'verts',len(m.vertices),'used',len(used),'allbounds',bounds(range(len(m.vertices))),'visiblebounds',bounds(used))
    ev.to_mesh_clear()
