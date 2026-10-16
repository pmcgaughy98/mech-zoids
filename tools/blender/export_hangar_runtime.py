"""Export approved R1 geometry, code-painted colour and baked room AO to Godot."""
import hashlib
import json
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[2]
ROOM = ROOT / "art/rooms/hangar_bay"
EVIDENCE = ROOM / "evidence"
SIZE = 2048
TILE = 64


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def image(name, pixels, data=False):
    result = bpy.data.images.new(name, pixels.shape[1], pixels.shape[0], is_data=data)
    result.pixels.foreach_set(np.asarray(pixels, dtype=np.float32).ravel())
    result.filepath_raw = str(ROOM / "textures" / (name + ".png"))
    result.file_format = "PNG"
    result.save()
    return result


assert read("milestone-reviews.json")["form"]["status"] == "approved"
assert read("form-approval.json")["approvedBy"] == "Preston"
(ROOM / "textures").mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOM / "source/hangar_bay_form.blend"))
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
rotation = Matrix.Rotation(math.pi, 4, "Z")
parts = []
for ob in scene.objects:
    if ob.type != "MESH" or ob.get("heroAsset") or ob.hide_render:
        continue
    mesh = bpy.data.meshes.new_from_object(ob.evaluated_get(deps), depsgraph=deps)
    mesh.transform(rotation @ ob.matrix_world)
    mesh.update()
    parts.append((ob.name, ob.get("featureId", ""), mesh))
assert parts and any(feature == "floor" for _, feature, _ in parts)
for ob in list(scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

# The tile is two metres wide: a seam, lit lip, shaded edge and sparse corner bolts.
# Calm panels carry the painter's construction without random pixel grain.
materials = {mat for _, _, mesh in parts for mat in mesh.materials if mat}
surface_values = {}
for mat in materials:
    base = np.array(mat.diffuse_color[:3], dtype=np.float32)
    pixels = np.ones((TILE, TILE, 4), dtype=np.float32)
    pixels[:, :, :3] = base
    emissive = mat.name in {"Screen teal", "Work light"}
    if not emissive and mat.name != "Hazard orange":
        pixels[0, :, :3] = base * .55
        pixels[:, 0, :3] = base * .55
        pixels[1, 1:, :3] = np.minimum(1, base * 1.13)
        pixels[1:, 1, :3] = np.minimum(1, base * 1.10)
        pixels[-1, :, :3] = base * .75
        pixels[:, -1, :3] = base * .75
        if mat.name != "Concrete" and not mat.name.startswith("Exterior"):
            for x, y in [(4, 4), (59, 59)]:
                pixels[y:y + 2, x:x + 2, :3] = base * .6
                pixels[y + 1, x, :3] = np.minimum(1, base * 1.3)
    tile = image("paint_" + mat.name.replace(" ", "_").lower(), pixels)
    mat.use_nodes = True
    nt = mat.node_tree
    shader = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = tile
    tex.interpolation = "Closest"
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "paint"
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], shader.inputs["Base Color"])
    if emissive:
        nt.links.new(tex.outputs["Color"], shader.inputs["Emission Color"])
    shader.inputs["Metallic"].default_value = 0 if mat.name == "Concrete" else .2
    shader.inputs["Roughness"].default_value = .88 if mat.name == "Concrete" else .65
    surface_values[mat] = (shader.inputs["Roughness"].default_value,
                           shader.inputs["Metallic"].default_value)

objects = []
for name, feature, mesh in parts:
    for layer in list(mesh.uv_layers):
        mesh.uv_layers.remove(layer)
    uv = mesh.uv_layers.new(name="paint")
    for face in mesh.polygons:
        face.use_smooth = False
        axis = max(range(3), key=lambda k: abs(face.normal[k]))
        u, v = ((1, 2) if axis == 0 else (0, 2) if axis == 1 else (0, 1))
        for loop in face.loop_indices:
            pos = mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv = (pos[u] / 2, pos[v] / 2)
    ob = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(ob)
    if feature in {"floor", "ceiling"}:
        group = ob.vertex_groups.new(name="export_" + feature)
        group.add(list(range(len(mesh.vertices))), 1, "REPLACE")
    ob.select_set(True)
    objects.append(ob)
bpy.context.view_layer.objects.active = objects[0]
bpy.ops.object.join()
body = bpy.context.object
body.name = "hangar_structure"
for i, material in enumerate(body.data.materials):
    if material is None:
        body.data.materials[i] = bpy.data.materials["Frame"]
body.data.uv_layers.new(name="atlas")
body.data.uv_layers.active = body.data.uv_layers["atlas"]
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.003)
bpy.ops.uv.pack_islands(rotate=True, margin=.003)
bpy.ops.object.mode_set(mode="OBJECT")

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.render.bake.use_clear = True
targets = []
for mat in body.data.materials:
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    targets.append(node)


def bake(name, kind, samples, data=False, **kwargs):
    img = bpy.data.images.new(name, SIZE, SIZE, is_data=data)
    for mat, node in zip(body.data.materials, targets):
        node.image = img
        mat.node_tree.nodes.active = node
    scene.cycles.samples = samples
    bpy.ops.object.bake(type=kind, uv_layer="atlas", margin=6, **kwargs)
    pixels = np.empty(SIZE * SIZE * 4, dtype=np.float32)
    img.pixels.foreach_get(pixels)
    return pixels.reshape(SIZE, SIZE, 4)


colour = bake("colour_bake", "DIFFUSE", 1, pass_filter={"COLOR"})
emission = bake("emission_bake", "EMIT", 1)
ao = bake("ao_bake", "AO", 32, True)[:, :, :1]
for axis in [0, 1]:
    ao = sum(np.roll(ao, shift, axis=axis) for shift in [-1, 0, 1]) / 3
colour[:, :, :3] *= .65 + .35 * np.clip(ao, 0, 1)
colour[:, :, 3] = 1
for mat in body.data.materials:
    nt = mat.node_tree
    emit = nt.nodes.new("ShaderNodeEmission")
    roughness, metallic = surface_values[mat]
    emit.inputs["Color"].default_value = (roughness, metallic, 0, 1)
    nt.links.new(emit.outputs["Emission"], nt.nodes.get("Material Output").inputs["Surface"])
surface = bake("surface_bake", "EMIT", 1, True)
orm = np.ones_like(colour)
orm[:, :, 0] = np.clip(ao[:, :, 0], 0, 1)
orm[:, :, 1] = surface[:, :, 0]
orm[:, :, 2] = surface[:, :, 1]
col_img = image("hangar_colour", colour)
orm_img = image("hangar_orm", orm, True)
emission[:, :, 3] = 1
emit_img = image("hangar_emission", np.clip(emission, 0, 1))

mat = bpy.data.materials.new("hangar_atlas")
mat.use_nodes = True
nt = mat.node_tree
shader = nt.nodes.get("Principled BSDF")


def texture(img):
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = img
    node.interpolation = "Closest"
    return node


nt.links.new(texture(col_img).outputs["Color"], shader.inputs["Base Color"])
nt.links.new(texture(emit_img).outputs["Color"], shader.inputs["Emission Color"])
shader.inputs["Emission Strength"].default_value = 1
split = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(texture(orm_img).outputs["Color"], split.inputs["Color"])
nt.links.new(split.outputs["Green"], shader.inputs["Roughness"])
nt.links.new(split.outputs["Blue"], shader.inputs["Metallic"])
# The exporter recognises this node group as glTF's occlusion channel.
group = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
group.interface.new_socket(name="Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
occlusion = nt.nodes.new("ShaderNodeGroup")
occlusion.node_tree = group
nt.links.new(split.outputs["Red"], occlusion.inputs["Occlusion"])
body.data.materials.clear()
body.data.materials.append(mat)
for face in body.data.polygons:
    face.material_index = 0
body.data.uv_layers.remove(body.data.uv_layers["paint"])
body.data.uv_layers.active = body.data.uv_layers["atlas"]
body.data.uv_layers["atlas"].active_render = True

# Keep separately named floor/ceiling meshes for the stage's contact and shadow rules.
for feature in ["floor", "ceiling"]:
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    body.vertex_groups.active_index = body.vertex_groups["export_" + feature].index
    before = set(scene.objects)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.separate(type="SELECTED")
    bpy.ops.object.mode_set(mode="OBJECT")
    separated = list(set(scene.objects) - before)
    assert len(separated) == 1
    separated[0].name = feature
for ob in scene.objects:
    if ob.type == "MESH":
        for face in ob.data.polygons:
            face.use_smooth = False
        ob.select_set(True)
triangles = sum(len(face.vertices) - 2 for ob in scene.objects if ob.type == "MESH"
                for face in ob.data.polygons)
assert triangles < 40000
output = ROOM / "hangar_bay.glb"
bpy.ops.export_scene.gltf(filepath=str(output), use_selection=True, export_format="GLB",
                          export_apply=True, export_animations=False, export_cameras=False,
                          export_lights=False)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOM / "source/hangar_bay_runtime.blend"))
fixtures = read("lighting-fixtures.json")
runtime = {"roomId": "hangar_bay", "viewport": [320, 180], "camera": {"position": [3.8, 7.3, 6.6],
           "target": [0, 1.35, 0], "verticalFovDegrees": 50}, "fixtures": []}
for fixture in fixtures["fixtures"]:
    x, y, z = fixture["location"]
    runtime["fixtures"].append({"id": fixture["id"], "position": [-x, z, y],
                                "color": fixture["color"], "energy": 1.5, "range": 12})
write(ROOM / "hangar_bay.runtime.json", runtime)
evidence = {"roomId": "hangar-bay", "triangles": triangles,
            "bytes": output.stat().st_size, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "sourceSha256": hashlib.sha256((ROOM / "source/hangar_bay_form.blend").read_bytes()).hexdigest(),
            "coordinateTransform": "Rotate room 180 degrees in Blender Z, then glTF Y-up; door faces Godot +Z. Machine is loaded independently.",
            "heroIncluded": False, "lightsIncluded": False, "camerasIncluded": False,
            "texturePainting": "Deterministic 64px panels per 2m; lit lip, dark seam and sparse bolts; no noise or generated images",
            "atlasSize": SIZE, "aoSamples": 32, "aoIncludesMachine": False,
            "fixtureManifestSha256": hashlib.sha256((EVIDENCE / "lighting-fixtures.json").read_bytes()).hexdigest(),
            "textures": {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in (ROOM / "textures").glob("hangar_*.png")}}
assert evidence["bytes"] < read("room-brief.json")["performanceBudget"]["maxVLowBytes"]
assert sum(t["bytes"] for t in evidence["textures"].values()) <= read("room-brief.json")["performanceBudget"]["maxHighTextureBytes"]
write(EVIDENCE / "runtime/export-audit.json", evidence)
print("HANGAR_EXPORT_DONE " + json.dumps(evidence))
