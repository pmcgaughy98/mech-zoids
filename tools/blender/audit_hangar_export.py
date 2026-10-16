"""Audit the actual exported room against the current machine and game camera."""
import hashlib
import json
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
ROOM = ROOT / "art/rooms/hangar_bay"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOM / "hangar_bay.glb"))
room_meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
before = set(bpy.context.scene.objects)
hero_path = ROOT / "art/machines/ape_l/ape_l.glb"
bpy.ops.import_scene.gltf(filepath=str(hero_path))
imported = set(bpy.context.scene.objects) - before
rig = next(o for o in imported if o.type == "ARMATURE")
rig.data.pose_position = "REST"
hero_meshes = [o for o in rig.children_recursive if o.type == "MESH"]
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()


def geometry(objects):
    vertices, faces = [], []
    for ob in objects:
        evaluated = ob.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        offset = len(vertices)
        vertices.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        faces.extend([offset + i for i in face.vertices] for face in mesh.polygons)
        evaluated.to_mesh_clear()
    return vertices, faces


rv, rf = geometry(room_meshes)
hv, hf = geometry(hero_meshes)
room_tree = BVHTree.FromPolygons(rv, rf)
hero_tree = BVHTree.FromPolygons(hv, hf)
config = json.loads((ROOM / "hangar_bay.runtime.json").read_text())
camera = config["camera"]


def blender_position(pos):
    return Vector((pos[0], -pos[2], pos[1]))


position = blender_position(camera["position"])
visible = occluded = 0
occlusions = []
for vertex in hv[::max(1, len(hv) // 2000)]:
    ray = vertex - position
    first = hero_tree.ray_cast(position, ray.normalized(), ray.length + .01)
    if first[0] is None or first[3] < ray.length - .035:
        continue
    visible += 1
    hit = room_tree.ray_cast(position, ray.normalized(), ray.length - .04)
    if hit[0] is not None:
        occluded += 1
        occlusions.append({"heroPoint": list(vertex), "roomPoint": list(hit[0])})
scene = bpy.context.scene
data = bpy.data.cameras.new("Runtime audit camera")
cam = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(cam)
cam.location = position
cam.rotation_euler = (blender_position(camera["target"]) - position).to_track_quat("-Z", "Y").to_euler()
data.sensor_fit = "VERTICAL"
data.sensor_height = 24
import math
data.lens = 24 / (2 * math.tan(math.radians(camera["verticalFovDegrees"]) / 2))
scene.render.resolution_x, scene.render.resolution_y = 320, 180
bpy.context.view_layer.update()
projected = [world_to_camera_view(scene, cam, vertex) for vertex in hv]
framing = {"left": min(p.x for p in projected), "right": max(p.x for p in projected),
           "bottom": min(p.y for p in projected), "top": max(p.y for p in projected)}
floor = next(o for o in room_meshes if o.name.startswith("floor"))
fv, _ = geometry([floor])
floor_top = max(p.z for p in fv)
hero_floor = min(p.z for p in hv)
door_rays = []
for x in [-2.4, 0, 2.4]:
    for z in [.75, 2.5, 4.25]:
        # Export rotates the scheduled door to Blender -Y / Godot +Z.
        door_rays.append(room_tree.ray_cast(Vector((x, -7.7, z)), Vector((0, -1, 0)), 1)[0] is None)
triangles = sum(len(face) - 2 for face in rf)
result = {"passed": visible > 0 and occluded == 0 and all(door_rays)
          and abs(floor_top) < .005 and abs(hero_floor) < .005
          and all(0 <= value <= 1 for value in framing.values()),
          "roomTriangles": triangles, "heroRestPoseOnly": True,
          "heroFloorGapMeters": round(hero_floor - floor_top, 6),
          "visibleHeroSamples": visible, "occludedHeroSamples": occluded,
          "occlusions": occlusions,
          "heroFrame": {key: round(value, 6) for key, value in framing.items()},
          "doorFacesGodotPositiveZ": all(door_rays), "clearDoorRays": sum(door_rays),
          "roomSha256": hashlib.sha256((ROOM / "hangar_bay.glb").read_bytes()).hexdigest(),
          "machineSha256": hashlib.sha256(hero_path.read_bytes()).hexdigest()}
(ROOM / "evidence/runtime/geometry-check.json").write_text(json.dumps(result, indent=2) + "\n")
print("EXPORTED_ROOM_AUDIT " + json.dumps(result))
assert result["passed"]
