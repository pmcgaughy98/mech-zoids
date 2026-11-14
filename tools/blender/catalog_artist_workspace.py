"""Build a native editable Blender station with four locked reference boards."""
import bpy
import math
from mathutils import Vector, Quaternion


def make_workspace(root, catalog, entry, meshes):
    scene = bpy.context.scene
    working = bpy.data.collections.new('01 WORKING MODEL - edit this')
    scene.collection.children.link(working)
    for obj in list(scene.objects):
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
        working.objects.link(obj)
    points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    low = Vector(tuple(min(p[a] for p in points) for a in range(3)))
    high = Vector(tuple(max(p[a] for p in points) for a in range(3)))
    scale = 3.2/max(high-low)
    station = bpy.data.objects.new('Working placement (display scale only)', None)
    working.objects.link(station)
    for obj in list(working.objects):
        if obj != station and obj.parent is None:
            obj.parent = station
    station.scale = (scale, scale, scale)
    station.location = (-3.0-(low.x+high.x)*scale/2, -(low.y+high.y)*scale/2, -low.z*scale+0.12)
    refs = bpy.data.collections.new('02 FOUR SOURCE SHEETS - locked reference boards')
    scene.collection.children.link(refs)
    for idx, view in enumerate(('front', 'left', 'back', 'right')):
        path = root / entry['views'][view]['path'].removeprefix('res://')
        image = bpy.data.images.load(str(path), check_existing=True)
        image.pack()
        x = 1.0 + (idx % 2)*2.75
        z = 4.0 - (idx // 2)*2.85
        bpy.ops.mesh.primitive_plane_add(size=2.5, location=(x, 0.8, z), rotation=(math.pi/2, 0, 0))
        plane = bpy.context.object
        plane.name = f'REFERENCE {view.upper()} - exact generation upload'
        for col in list(plane.users_collection):
            col.objects.unlink(plane)
        refs.objects.link(plane)
        mat = bpy.data.materials.new(f'White sheet {view}')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = image
        nodes.active = tex
        emission = nodes.new('ShaderNodeEmission')
        output = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(tex.outputs['Color'], emission.inputs['Color'])
        mat.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
        plane.data.materials.append(mat)
        plane.hide_select = True
        bpy.ops.object.text_add(location=(x-1.25, 0.7, z+1.4), rotation=(math.pi/2, 0, 0))
        label = bpy.context.object
        label.name = f'Label {view}'
        label.data.body = view.upper()
        label.data.size = 0.16
        label.hide_select = True
        for col in list(label.users_collection):
            col.objects.unlink(label)
        refs.objects.link(label)
    stage = bpy.data.collections.new('03 STUDIO - display only')
    scene.collection.children.link(stage)
    bpy.ops.object.camera_add(location=(0, -20, 3.0), rotation=(math.pi/2, 0, 0))
    camera = bpy.context.object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 12
    scene.camera = camera
    for location, power, size in [((-3,-5,8),1300,7),((-6,3,5),900,5),((4,-2,4),400,5)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.data.energy = power
        light.data.shape = 'DISK'
        light.data.size = size
        light.rotation_euler = (Vector((-3,0,1.5))-light.location).to_track_quat('-Z','Y').to_euler()
    for obj in list(scene.objects):
        if obj.type in ('CAMERA','LIGHT'):
            for col in list(obj.users_collection):
                col.objects.unlink(obj)
            stage.objects.link(obj)
            obj.hide_select = True
    if scene.world is None:
        scene.world = bpy.data.worlds.new('Neutral studio world')
    scene.world.color = (0.22,0.22,0.22)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'
    # Start ready to orbit/edit the mesh, with all four sheets beside it.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED' and node.inputs['Base Color'].is_linked:
                        texture = node.inputs['Base Color'].links[0].from_node
                        if texture.type == 'TEX_IMAGE':
                            mat.node_tree.nodes.active = texture
    bpy.context.view_layer.objects.active = meshes[0]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.shading.type = 'SOLID'
                space.shading.color_type = 'TEXTURE'
                space.overlay.show_floor = False
                space.overlay.show_extras = False
                space.overlay.show_axis_x = False
                space.overlay.show_axis_y = False
                space.region_3d.view_perspective = 'ORTHO'
                space.region_3d.view_rotation = Quaternion((1,0,0), math.pi/2)
                space.region_3d.view_location = Vector((0,0,2.7))
                space.region_3d.view_distance = 12
                space.clip_end = 1000
    text = bpy.data.texts.new('START HERE - model and reference provenance.txt')
    text.write(f'''{entry['name']} - artist workspace

Edit the mesh in 01 WORKING MODEL. Tab: mesh edit. Numpad .: frame selection.
The four reference boards in 02 are locked against accidental selection.
Orbit the model freely; boards stay beside it. Each image is packed in this file.
To inspect a sheet alone, use any Image Editor and select front.png / left.png /
back.png / right.png from this file's packed images.

The work is UNREVIEWED. Compare exact limb counts, attachment points, eye socket
shapes and lens placement, left/right consistency, silhouette and back plates.
Do not assume a generated feature is intentional when it conflicts with a sheet.
Record unresolved differences; do not claim a geometry repair from material changes.

Source download is preserved byte-for-byte outside this working file:
{entry['source_model']['path']}
SHA256: {entry['source_model']['sha256']}
References and exact project matches: res://art/model_catalog/catalog.json
The working root changes display placement/scale only, not intended gameplay size.
No rig, animation or geometry correction has been performed by workspace setup.
{entry['status']}
''')
    scene['catalog_id'] = entry['id']
    scene['source_sha256'] = entry['source_model']['sha256']
    scene['review_status'] = 'UNREVIEWED: workspace setup only'
    bpy.ops.file.pack_all()
    folder = catalog/'workspaces'
    folder.mkdir(exist_ok=True)
    (folder/'.gdignore').write_text('# Native artist workspaces, not runtime imports.\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/f'{entry["id"]}.blend'))
    return station
