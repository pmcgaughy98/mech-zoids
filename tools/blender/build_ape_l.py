# Builds the Gorilla type (ape_l) as a hard-surface 3D mech in Blender, exports a GLB for Godot, saves the .blend,
# and renders eight turnaround views (Claude, 2026-10-11; Preston: "build the green gorilla 3d model").
# Design: docs/design/starters-2026-10-11.md and machines-2026-10-11.md. Nothing copied from any Zoid; built from
# how a real gorilla stands: knuckle-walking on long arms, shoulders above the hips, a low head with a brow ridge.
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_ape_l.py
# Model space: metres, Z up, the machine faces -Y (toward Blender's front view). About 2.1 m tall at the crest.
import bpy, math, os
from mathutils import Vector, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_GLB = os.path.join(ROOT, "art", "machines", "ape_l", "ape_l.glb")
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "ape_l.blend")
OUT_VIEWS = os.path.join(ROOT, "docs", "art", "3d", "ape_l_views")

# Palette from machines.gd (sRGB hex); the faction shows in the teal eyes and running lights.
HEX = {"main": "4a7a3c", "trim": "2c4a2a", "accent": "a8763e", "frame": "4a4f57", "frame_dark": "2b2e33", "light": "5fe1d0"}


def srgb(h):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), 1.0)


def make_materials():
    mats = {}
    for key, h in HEX.items():
        m = bpy.data.materials.new("ape_" + key)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = srgb(h)
        b.inputs["Roughness"].default_value = {"accent": 0.38, "frame": 0.45, "frame_dark": 0.5}.get(key, 0.6)
        b.inputs["Metallic"].default_value = {"accent": 0.75, "frame": 0.55, "frame_dark": 0.5}.get(key, 0.1)
        if key == "light":
            b.inputs["Emission Color"].default_value = srgb(h)
            b.inputs["Emission Strength"].default_value = 4.0
        tex = os.path.join(ROOT, "art", "machines", "ape_l", "textures", key + ".png")
        if os.path.exists(tex):   # painted panels and machinery (tools/blender/make_mech_textures.py)
            node = m.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = bpy.data.images.load(tex)
            node.interpolation = "Closest"
            m.node_tree.links.new(node.outputs["Color"], b.inputs["Base Color"])
        mats[key] = m
    return mats


def uv_box(ob, size=0.9):
    """Box-project UVs so one texture tile covers about `size` metres on every part."""
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=size, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


def bevel(ob, width, segments=1):   # one segment = a hard chamfer, the hard-surface look (2+ reads soft)
    mod = ob.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.harden_normals = True
    return ob


def box(name, mat, center, size, rot=(0, 0, 0), bev=0.04, taper=1.0):
    """A box; taper < 1 narrows its bottom face (a waist, a wedge)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center, rotation=[math.radians(a) for a in rot])
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # size only; position and tilt stay on the object
    if taper != 1.0:
        for v in ob.data.vertices:
            if v.co.z < 0:
                v.co.x *= taper
                v.co.y *= 0.5 + 0.5 * taper
    ob.data.materials.append(MATS[mat])
    if bev > 0:
        bevel(ob, bev)
    return ob


def cyl(name, mat, a, b, radius, verts=12):
    """A cylinder from point a to point b (pistons, joints, rods)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=d.length, location=(a + b) / 2)
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    ob.data.materials.append(MATS[mat])
    return ob


def beam(name, mat, a, b, width, depth, bev=0.04, taper=1.0):
    """A squared limb segment from joint a to joint b; taper scales the b end (above 1 = thicker at b)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (width, depth, d.length)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # size only; position and tilt stay on the object
    if taper != 1.0:
        for v in ob.data.vertices:
            if v.co.z > 0:
                v.co.x *= taper
                v.co.y *= taper
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    ob.data.materials.append(MATS[mat])
    if bev > 0:
        bevel(ob, bev)
    return ob


def joint(name, center, radius, axis="X", length=0.0):
    c = Vector(center)
    off = Vector((length / 2, 0, 0)) if axis == "X" else Vector((0, length / 2, 0))
    return cyl(name, "frame_dark", c - off, c + off, radius, verts=16)


def build():
    lean = -12  # the torso tips forward: shoulders higher and further forward than the hips
    # Core: hips, the barrel chest, the bulwark plate, armour panels on the flanks.
    box("hips", "frame", (0, 0.55, 0.98), (0.82, 0.55, 0.42), (lean, 0, 0), 0.05)
    box("torso", "main", (0, 0.0, 1.42), (1.16, 1.0, 0.92), (lean, 0, 0), 0.07, taper=0.78)
    box("torso_seam", "frame_dark", (0, 0.0, 1.5), (1.18, 1.02, 0.025), (lean, 0, 0), 0.0)   # a panel seam around the chest
    box("chest_plate_mark", "trim", (0.24, -0.63, 1.5), (0.16, 0.03, 0.22), (lean - 4, 0, 0), 0.01)  # a small unit plate on the bulwark
    box("torso_spine", "trim", (0, 0.18, 1.86), (0.5, 0.95, 0.12), (lean, 0, 0), 0.03)
    box("bulwark_plate", "accent", (0, -0.55, 1.4), (0.95, 0.13, 0.72), (lean - 4, 0, 0), 0.05)
    for s in (-1, 1):
        box("bulwark_bolt_%d" % s, "frame_dark", (s * 0.34, -0.63, 1.62), (0.09, 0.05, 0.09), (lean, 0, 0), 0.015)
        box("bulwark_bolt_low_%d" % s, "frame_dark", (s * 0.34, -0.6, 1.15), (0.09, 0.05, 0.09), (lean, 0, 0), 0.015)
        box("flank_panel_%d" % s, "trim", (s * 0.575, 0.0, 1.38), (0.04, 0.72, 0.5), (lean, 0, 0), 0.015)
        # Shoulders: big rounded pauldrons with a pine edge.
        box("pauldron_%d" % s, "main", (s * 0.76, -0.22, 1.78), (0.56, 0.66, 0.44), (lean, 0, s * 8), 0.1)
        box("pauldron_edge_%d" % s, "trim", (s * 0.98, -0.22, 1.66), (0.1, 0.62, 0.2), (lean, 0, s * 8), 0.03)
        box("pauldron_seam_%d" % s, "frame_dark", (s * 0.76, -0.22, 1.86), (0.57, 0.67, 0.02), (lean, 0, s * 8), 0.0)
        box("faction_stripe_%d" % s, "light", (s * 1.0, -0.42, 1.8), (0.03, 0.2, 0.05), (lean, 0, s * 8), 0.0)
        box("shoulder_vent_%d" % s, "frame_dark", (s * 0.62, 0.12, 1.93), (0.22, 0.14, 0.08), (lean, 0, 0), 0.02)
        # Arms: long, down and forward to the knuckles; the elbow cylinder reads as a hard joint.
        sh, el, wr = (s * 0.88, -0.3, 1.62), (s * 0.98, -0.5, 0.98), (s * 0.98, -0.72, 0.34)
        joint("shoulder_joint_%d" % s, sh, 0.2, "X", 0.34)
        beam("upper_arm_%d" % s, "main", sh, el, 0.38, 0.4, 0.05, taper=0.8)
        joint("elbow_%d" % s, el, 0.16, "X", 0.44)
        beam("forearm_%d" % s, "main", el, wr, 0.4, 0.38, 0.06, taper=1.3)
        beam("forearm_seam_%d" % s, "frame_dark", (s * 0.98, -0.55, 0.84), (s * 0.98, -0.58, 0.76), 0.47, 0.44, 0.0, taper=1.06)
        beam("forearm_plate_%d" % s, "trim", (s * 1.2, -0.52, 0.92), (s * 1.2, -0.7, 0.42), 0.04, 0.3, 0.015)
        # Piston Knuckles: a hydraulic ram on the outside of each forearm, bronze rod in a gunmetal sleeve.
        cyl("piston_sleeve_%d" % s, "frame", (s * 1.25, -0.48, 0.86), (s * 1.25, -0.62, 0.55), 0.07)
        cyl("piston_rod_%d" % s, "accent", (s * 1.25, -0.62, 0.55), (s * 1.25, -0.72, 0.3), 0.04)
        # The fist it walks on: a heavy bronze block with four knuckle studs on the ground.
        box("fist_%d" % s, "accent", (s * 0.98, -0.82, 0.17), (0.5, 0.5, 0.34), (0, 0, 0), 0.07)
        for k in range(4):
            box("knuckle_%d_%d" % (s, k), "frame_dark", (s * 0.98 + (k - 1.5) * 0.115, -1.08, 0.09), (0.09, 0.07, 0.15), (0, 0, 0), 0.02)
        # Legs: short and bowed, a frame shin, a broad foot.
        hp, kn, an = (s * 0.36, 0.62, 0.92), (s * 0.48, 0.8, 0.54), (s * 0.42, 0.68, 0.14)
        beam("thigh_%d" % s, "trim", hp, kn, 0.3, 0.34, 0.05)
        joint("knee_%d" % s, kn, 0.13, "X", 0.34)
        beam("shin_%d" % s, "frame", kn, an, 0.24, 0.26, 0.04)
        box("foot_%d" % s, "frame_dark", (s * 0.42, 0.58, 0.07), (0.34, 0.52, 0.14), (0, 0, 0), 0.03)
    # Inner frame: the working machinery between the armour, so it reads as a machine, not a stack of boxes.
    box("waist_frame", "frame", (0, 0.32, 1.08), (0.62, 0.42, 0.34), (lean, 0, 0), 0.02)
    for s in (-1, 1):
        cyl("waist_piston_%d" % s, "frame_dark", (s * 0.22, 0.12, 1.02), (s * 0.24, 0.42, 1.3), 0.05)
        cyl("shoulder_actuator_%d" % s, "frame", (s * 0.5, -0.05, 1.42), (s * 0.82, -0.36, 1.32), 0.06)
        cyl("hip_actuator_%d" % s, "frame_dark", (s * 0.28, 0.48, 1.02), (s * 0.44, 0.72, 0.66), 0.05)
        for k in range(3):   # neck cable bundle from the chest up into the head
            cyl("neck_cable_%d_%d" % (s, k), "frame_dark", (s * (0.06 + k * 0.05), -0.42, 1.68), (s * (0.05 + k * 0.04), -0.55, 1.62), 0.025, 8)
    # Head: low between the shoulders, a brow ridge, a crest, the teal eyes, a gunmetal jaw.
    box("head", "trim", (0, -0.6, 1.74), (0.44, 0.46, 0.38), (lean, 0, 0), 0.06)
    box("brow", "trim", (0, -0.83, 1.86), (0.5, 0.14, 0.1), (lean, 0, 0), 0.03)
    box("crest", "main", (0, -0.52, 1.97), (0.1, 0.38, 0.14), (lean, 0, 0), 0.03)
    box("jaw", "frame", (0, -0.78, 1.6), (0.36, 0.26, 0.14), (lean, 0, 0), 0.03)
    for s in (-1, 1):
        box("eye_%d" % s, "light", (s * 0.11, -0.88, 1.77), (0.11, 0.03, 0.05), (lean, 0, 0), 0.0)
    # Ballast Throw: the rack on its back holds the blocks it tears off and throws.
    box("rack_base", "frame", (0, 0.32, 1.95), (0.86, 0.7, 0.07), (lean, 0, 0), 0.02)
    for s in (-1, 1):
        box("rack_rail_%d" % s, "frame_dark", (s * 0.4, 0.32, 2.03), (0.05, 0.7, 0.14), (lean, 0, 0), 0.01)
    for i, (x, y, z) in enumerate([(-0.19, 0.16, 2.12), (0.19, 0.16, 2.12), (-0.19, 0.5, 2.06), (0.19, 0.5, 2.06), (0.0, 0.33, 2.38)]):
        box("ballast_block_%d" % i, "trim", (x, y, z), (0.32, 0.3, 0.3), (lean, 0, 0), 0.03)
    box("rack_strap", "accent", (0, 0.33, 2.24), (0.86, 0.06, 0.04), (lean, 0, 0), 0.01)
    # Running lights: two teal points on the back of the hips.
    for s in (-1, 1):
        box("running_light_%d" % s, "light", (s * 0.28, 0.84, 1.06), (0.08, 0.02, 0.05), (lean, 0, 0), 0.0)


def join_into_one():
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in obs:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        if o.rotation_mode == "QUATERNION":
            pass
    bpy.context.view_layer.objects.active = obs[0]
    for o in obs:
        bpy.context.view_layer.objects.active = o
        for m in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
    for o in obs:
        uv_box(o)
    # Bake every part's position and tilt into its mesh, so the joined model sits at the origin with no rotation.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    ob = bpy.context.active_object
    ob.name = "ape_l"
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    return ob


def render_views(ob):
    os.makedirs(OUT_VIEWS, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 480
    scene.render.resolution_y = 360
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("world")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.055, 0.065, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    sun.data.energy = 3.2
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
    rim = bpy.context.active_object
    rim.rotation_euler = (math.radians(120), 0, math.radians(150))
    rim.data.energy = 1.5
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.3
    scene.camera = cam
    target = Vector((0, 0, 1.15))
    # Slot order used by the game: e ne n nw w sw s se (facing relative to the camera; s = toward the camera).
    names = ["e", "ne", "n", "nw", "w", "sw", "s", "se"]
    elev = math.radians(30)
    for k, name in enumerate(names):
        facing = math.radians(k * 45)
        # The machine faces -Y in model space; turn it so it faces `facing` (0 = screen right) for a camera at -Y.
        ob.rotation_euler = (0, 0, facing + math.radians(90))
        d = 8.0
        cam.location = target + Vector((0, -d * math.cos(elev), d * math.sin(elev)))
        cam.rotation_euler = (math.radians(90) - elev, 0, 0)
        scene.render.filepath = os.path.join(OUT_VIEWS, "%s.png" % name)
        bpy.ops.render.render(write_still=True)
    ob.rotation_euler = (0, 0, 0)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global MATS
    MATS = make_materials()
    build()
    ob = join_into_one()
    dims = tuple(round(v, 3) for v in ob.dimensions)
    os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=OUT_GLB, use_selection=True, export_format="GLB", export_apply=True)
    render_views(ob)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("APE_L_DONE dims=%s triangles=%d glb=%s" % (dims, tris, OUT_GLB))


MATS = {}
main()
