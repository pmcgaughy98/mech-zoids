import bpy,bmesh,json
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
from array import array
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/mantis_m/surface-restoration-v1-2026-11-10');OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath='D:/dev/new-mech-rpg/art/model_catalog/sources/mantis_front - Hunyuan 3D v3.1 Pro.glb');ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.context.view_layer.objects.active=ob
mask=np.load(ROOT/'accepted-cut-mask.npz');proxy=mask['triangles'];labels=mask['removed'];lo=proxy.reshape(-1,3).min(0);hi=proxy.reshape(-1,3).max(0);pts=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices]);slo=pts.min(0);shi=pts.max(0);scale=float(max(hi-lo)/max(shi-slo));offset=(lo+hi)/2-(slo+shi)/2*scale
from mathutils import Matrix
ob.matrix_world=Matrix.Translation(Vector(offset))@Matrix.Diagonal((scale,scale,scale,1))@ob.matrix_world;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
me=ob.data;attr=me.attributes.new('_source_norm','FLOAT_VECTOR','CORNER');values=array('f',[0])*(len(me.loops)*3);me.corner_normals.foreach_get('vector',values);attr.data.foreach_set('vector',values)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.faces.ensure_lookup_table();before={'faces':len(bm.faces),'vertices':len(bm.verts),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)}
bm.verts.ensure_lookup_table();bm.verts.index_update();flat=proxy.reshape(-1,3);tree=BVHTree.FromPolygons([Vector(p) for p in flat],[(i*3,i*3+1,i*3+2) for i in range(len(proxy))],all_triangles=True);field=np.zeros(len(bm.verts));errors=[]
for v in bm.verts:
 co,normal,i,dist=tree.find_nearest(v.co);field[v.index]=float(labels[i]);errors.append(dist)
# Smooth classification only, not the source geometry. A continuous level set
# gives closed cut contours instead of jagged face-selection pinholes.
adj=np.array([(e.verts[0].index,e.verts[1].index) for e in bm.edges]);degree=np.bincount(adj.ravel(),minlength=len(field))
for _ in range(8):
 sums=np.zeros(len(field));np.add.at(sums,adj[:,0],field[adj[:,1]]);np.add.at(sums,adj[:,1],field[adj[:,0]]);field=.5*field+.5*sums/np.maximum(degree,1)
layer=bm.verts.layers.float.new('accepted_cut_field')
for v in bm.verts:v[layer]=float(field[v.index])
level=.500001
crossing=[e for e in bm.edges if (e.verts[0][layer]>level)!=(e.verts[1][layer]>level)]
for e in crossing:
 a,b=e.verts;fraction=(level-a[layer])/(b[layer]-a[layer]);ne,nv=bmesh.utils.edge_split(e,a,fraction);nv[layer]=level
for f in list(bm.faces):
 cuts=[v for v in f.verts if abs(v[layer]-level)<1e-7]
 if len(cuts)==2 and len(f.verts)>3:bmesh.utils.face_split(f,cuts[0],cuts[1])
remove=[f for f in bm.faces if sum(v[layer] for v in f.verts)/len(f.verts)>level+1e-7]
dset=set(remove);border=set(e for f in remove for e in f.edges if any(n not in dset for n in e.link_faces));bmesh.ops.delete(bm,geom=remove,context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');border=[e for e in border if e.is_valid and e.is_boundary]
cap=bpy.data.materials.new('Local_removed_leg_root_finish');cap.use_nodes=True;bs=cap.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.05,.11,.035,1);bs.inputs['Roughness'].default_value=.55;bs.inputs['Metallic'].default_value=.3;me.materials.append(cap)
filled=bmesh.ops.holes_fill(bm,edges=border,sides=0)['faces']
for f in filled:f.material_index=len(me.materials)-1;f.smooth=False
bmesh.ops.triangulate(bm,faces=filled)
seen=set();components=[]
for seed in bm.verts:
 if seed in seen:continue
 pending=[seed];part=set()
 while pending:
  v=pending.pop()
  if v in part:continue
  part.add(v);pending.extend(e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in part)
 seen.update(part);components.append(part)
largest=max(components,key=len);scraps=[v for part in components if part is not largest for v in part]
# The source after detached-piece removal is one connected body. These smaller
# islands were introduced by the approved middle-pair cut, not separate armor.
print('CUT SCRAPS',len(components)-1,len(scraps),flush=True)
if scraps:bmesh.ops.delete(bm,geom=scraps,context='VERTS')
after={'faces':len(bm.faces),'vertices':len(bm.verts),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.to_mesh(me);bm.free();me.update();vals=[]
for f in me.polygons:
 for li in f.loop_indices:vals.append((0,0,0) if f.material_index==len(me.materials)-1 else tuple(me.attributes['_source_norm'].data[li].vector))
me.normals_split_custom_set(vals);me.attributes.remove(me.attributes['_source_norm'])
# Same six-limb layout, now align the complete restored surface to Meshy's rig.
riglo=np.array([-1.0495472,0.,-1.1398897]);righi=np.array([1.0495472,1.7000002,1.1398897]);targetspan=Vector((righi[0]-riglo[0],righi[2]-riglo[2],righi[1]-riglo[1]));pts=np.array([tuple(v.co) for v in me.vertices]);clo=pts.min(0);chi=pts.max(0);fit=float(max(targetspan)/max(chi-clo));targetcenter=Vector((0,0,.85));shift=targetcenter-Vector((clo+chi)/2)*fit;ob.matrix_world=Matrix.Translation(shift)@Matrix.Diagonal((fit,fit,fit,1));bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for image in bpy.data.images:
 if image.has_data and image.source=='FILE':image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'restored-six-limb-surface.blend'));bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.ops.export_scene.gltf(filepath=str(OUT/'restored-six-limb-surface-STATIC-STAGING.glb'),export_format='GLB',use_selection=True,export_animations=False)
report={'method':'Restore intact high-detail original; transfer approved floating-piece and middle walking-pair cuts via nearest proxy surface and smoothed classification. Close new cut roots and discard only detached remnants created by this cut. No remeshing or broad hole fill.','before':before,'after':after,'removed_source_faces':len(remove),'cut_boundary_edges':len(border),'cut_caps':len(filled),'cut_scrap_components_removed':len(components)-1,'cut_scrap_vertices_removed':len(scraps),'proxy_alignment_scale':scale,'rig_alignment_scale':fit,'source_to_proxy_centroid_distance_99pct':float(np.percentile(errors,99)),'rig_status':'Surface staging only; actual 44-joint rig retained in following weight transfer.'};(OUT/'surface-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
