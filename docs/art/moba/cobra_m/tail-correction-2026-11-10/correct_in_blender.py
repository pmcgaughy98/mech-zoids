import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from array import array
base=Path('D:/dev/new-mech-rpg')
src=Path('D:/dev/_scratch/mech-art-direction/cobra-tail-2026-11-10/cobra-source.glb')
out=base/'docs/art/moba/cobra_m/tail-correction-2026-11-10'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');ob.name='Cobra_single_rear_tail'
bpy.context.view_layer.objects.active=ob;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
original_positions=[v.co.copy() for v in ob.data.vertices]
me=ob.data
saved=me.attributes.new('_corner_normal','FLOAT_VECTOR','CORNER')
values=array('f',[0.0])*(len(me.loops)*3);me.corner_normals.foreach_get('vector',values);saved.data.foreach_set('vector',values)
bm=bmesh.new();bm.from_mesh(me)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
before={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges)}
# Tail duplicate extends +X at floor height. The intended rear tail is +Y.
# Use a limited low-volume cut, preserving the full flared hood above it.
bm.to_mesh(me);bm.free();me.update()
me.normals_split_custom_set([tuple(v.vector) for v in me.attributes['_corner_normal'].data]);me.attributes.remove(me.attributes['_corner_normal'])
cap=bpy.data.materials.new('Cut_cap_dark_steel');cap.use_nodes=True
bs=cap.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(0.025,0.13,0.055,1);bs.inputs['Metallic'].default_value=0.25;bs.inputs['Roughness'].default_value=0.55
ob.data.materials.append(cap)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0.57,0,-0.125))
cutter=bpy.context.object;cutter.name='extra_tail_removal_volume';cutter.dimensions=(1.2,2.0,0.5)
for mat in ob.data.materials:cutter.data.materials.append(mat)
for f in cutter.data.polygons:f.material_index=1
bpy.context.view_layer.update()
bpy.context.view_layer.objects.active=ob
mod=ob.modifiers.new('remove_generated_side_tail','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)
# Finish the large side closure as a small recessed armor panel, rather than
# leaving a featureless sawn-off branch face. Existing exterior stays fixed.
rim=bpy.data.materials.new('Local_cap_recess_rim');rim.use_nodes=True
rbs=rim.node_tree.nodes.get('Principled BSDF');rbs.inputs['Base Color'].default_value=(0.025,0.04,0.03,1);rbs.inputs['Metallic'].default_value=0.55;rbs.inputs['Roughness'].default_value=0.52
ob.data.materials.append(rim)
me=ob.data
saved=me.attributes.new('_cap_finish_normals','FLOAT_VECTOR','CORNER')
values=array('f',[0.0])*(len(me.loops)*3);me.corner_normals.foreach_get('vector',values);saved.data.foreach_set('vector',values)
bm=bmesh.new();bm.from_mesh(me)
cap_edges=[e for e in bm.edges if any(f.material_index==1 for f in e.link_faces) and any(f.material_index==0 for f in e.link_faces)]
finish=bmesh.ops.bevel(bm,geom=cap_edges,offset=0.0015,segments=2,affect='EDGES',clamp_overlap=True,material=2) if cap_edges else {'faces':[]}
for f in finish['faces']:f.material_index=2;f.smooth=False
local_edges=[e for e in bm.edges if any(f.material_index>0 for f in e.link_faces)]
bmesh.ops.dissolve_degenerate(bm,dist=1e-5,edges=local_edges)
bm.to_mesh(me);bm.free();me.update()
restored=[]
for f in me.polygons:
 for i in f.loop_indices:
  restored.append((0,0,0) if f.material_index else tuple(me.attributes['_cap_finish_normals'].data[i].vector))
me.normals_split_custom_set(restored);me.attributes.remove(me.attributes['_cap_finish_normals'])
ob.data.calc_loop_triangles()
bm=bmesh.new();bm.from_mesh(ob.data)
after={'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':len(ob.data.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'cap_faces':sum(f.material_index==1 for f in bm.faces)}
bm.free()
tree=KDTree(len(ob.data.vertices))
for i,v in enumerate(ob.data.vertices):tree.insert(v.co,i)
tree.balance()
protected=[p for p in original_positions if p.z>0.13 or p.x< -0.04]
errors=[tree.find(p)[2] for p in protected]
report={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'rig_present':False,'intended_tail':'Continuous rearward +Y branch from neck; paired side profiles support one rear-trailing body. Lateral +X branch is the generated duplicate.','cut_volume_blender_z_up':{'x_min':-0.03,'z_max':0.125,'y_range':[-1,1]},'before_position_welded':before,'after':after,'protected_geometry':{'regions':'all geometry above z=.13, or x<-.04 (head/hood/neck and rear tail)','source_samples':len(protected),'maximum_position_error':max(errors),'samples_over_1e-5':sum(e>1e-5 for e in errors)},'cap_note':'Local green painted-metal cap with a small 1.5mm clamped bevel at its outer boundary; source texture images retained unchanged. No generated or repainted atlas.'}
ob['correction']='Generated lateral duplicate tail removed. Single continuous rear tail retained.'
ob['source_sha256']=report['source_sha256']
ob['rig_status']='Source unrigged; no rig generated or replaced.'
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'cobra-single-tail-corrected.blend'))
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(out/'cobra_front - single tail corrected.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=False)
(out/'correction-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
