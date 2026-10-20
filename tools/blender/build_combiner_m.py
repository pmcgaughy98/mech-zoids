# The combination machine, v1: a new machine from the creature factory (Claude, 2026-10-19). Preston: "create a whole
# new model using mass manufacturing, the zoids will kind of get dragged towards the center and the circle of light
# ... then out comes a whole new creature with a different color etc. but you can tell it has aspects of all creatures
# or is a combination of them exampled by legacy and fuzors".
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_combiner_m.py
# Structure from Zoids Legacy's battle combinations (ZoidsLegacyDecomp src/battle/combinations: a recipe of up to six
# component models swaps the owner's battle model for a new combined one) and Zoids Fuzors (one beast carrying another's
# wings, armour and weapons); the part mapping after chimera lore (the Nue: monkey face, tanuki body, tiger limbs, snake
# tail; the Greek chimera: a second head rising from the back). docs/reference/combiner-v2-2026-10-19.md.
# A proposal: the look, colours and name are Preston's. Each starter shows in one trait:
#   gorilla   the high shoulder hump, the huge forearms and knuckle fists (forelegs)
#   wolf      the wedge head, fangs, tall ears
#   kangaroo  the big digitigrade hind legs, the thick tail root, the Pouch Cannon port in the chest
#   shoebill  the gold bill crest over the snout, folded feather wings, the dorsal head-gun
#   hippo     the barrel body, tusks at the jaw corners
#   pangolin  overlapping scale rows over the back and down the tail, the crimson tail cone
# Colours: new, its own (pearl armour, gold trim, gunmetal frame), with the six starters' colours as six core gems.
import bpy, importlib.util, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.environ["MECH_KIT_IMPORT"] = "1"


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kit = _load("mech_kit", "build_ape_l_v2.py")
quad = _load("quad_rig", "quad_rig.py")
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "combiner_m.blend")

PAL = {
    "main": "e4e0d6",        # pearl armour
    "trim": "b02028",        # crimson: tail cone, seams of the gold, inner ears
    "accent": "d9b56a",      # gold: the bill crest, knuckles, plate rims, feather edges
    "frame": "4a4e58",       # gunmetal limbs and joints
    "frame_dark": "24262e",  # the body under the plates
    "face": "e4e0d6",
    "tusk": "f2ecdc",        # fangs and tusks
    "light": "8a8d92",
    "eye_src": "5fe1d0",     # teal eyes (player faction)
    "gem_green": "3f9a3a",   # the six starters: gorilla
    "gem_red": "d81c1c",     # wolf
    "gem_orange": "e0602c",  # kangaroo
    "gem_blue": "3c6ec8",    # shoebill
    "gem_purple": "8c4aa0",  # hippo
    "gem_gold": "e8b830",    # pangolin
}


def make_materials():
    for key, h in PAL.items():
        m = bpy.data.materials.new("mech_" + key if key != "eye_src" else "eye_src")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = kit.srgb(h)
        b.inputs["Roughness"].default_value = 0.5
        m.diffuse_color = kit.srgb(h)
        kit.MATS[key] = m


# ---- the body: a gorilla's shoulder hump running back into a hippo's barrel, pangolin scale rows over it --------
TOP = [(-1.55, 2.05), (-1.1, 2.38), (-0.5, 2.28), (0.2, 2.02), (0.9, 1.96), (1.4, 1.8)]   # (y, top height)
HALF_W = 0.86


def top_at(y):
    for (y0, z0), (y1, z1) in zip(TOP, TOP[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return TOP[0][1] if y < TOP[0][0] else TOP[-1][1]


def bottom_at(y):
    return 1.12 if y < -0.9 else (0.98 if y < 0.9 else 1.08)


def body():
    side = [(-1.66, 1.5)] + TOP + [(1.62, 1.45), (1.5, 1.1), (0.9, 0.97), (0.0, 0.95), (-0.9, 1.0), (-1.5, 1.15)]
    front = kit.mirror_x([(0.3, 2.38), (0.7, 2.22), (0.88, 1.8), (0.86, 1.4), (0.7, 1.1), (0.35, 0.95)])
    core = kit.profile_solid("torso_core", "frame", (0, 0, 0), side, front, chamfer=0.03)   # v1b: gunmetal (the near-black core showed between the scales and the body read dark)
    # pangolin scale rows: each row a ring of plates tipped back so its lower edge overlaps the row behind
    for row, y in enumerate([-1.3 + 0.3 * k for k in range(10)]):
        t, b = top_at(y), bottom_at(y)
        zc, rz = (t + b) / 2, (t - b) / 2
        pitch = math.degrees(math.atan2(-(top_at(y + 0.05) - top_at(y - 0.05)), 0.1))
        for j, th in enumerate((0, -34, 34, -68, 68)):   # v1b: no lower row (it hung below the flank like a row of teeth)
            rt = math.radians(th)
            aim = Vector((HALF_W * math.sin(rt), y, zc + rz * math.cos(rt)))
            normal = (math.sin(rt) / HALF_W, 0, math.cos(rt) / rz)
            c = kit.on_surface(core, aim, normal, 0.05)
            tilt = math.degrees(math.atan2(math.sin(rt) / HALF_W, math.cos(rt) / rz))
            mat = "accent" if (th == 0 and row % 3 == 1) else "main"   # a gold spine scale every third row
            kit.plate("armor_%d_%d" % (row, j), mat, c, 0.56 - 0.03 * abs(j // 2), 0.42, 0.05,   # v1b: bigger, overlapping
                      (-90 - pitch - 14, tilt, 0), bend=0.45, bevel=0.012, taper=0.8)
    # the chest: the Pouch Cannon port, and the six core gems round it, one per starter
    c = kit.on_surface(core, Vector((0, -1.6, 1.62)), (0, -1, 0.1), 0.02)
    kit.plate("chest_plate", "main", c, 0.9, 0.7, 0.06, (10, 0, 0), bend=0.4, bevel=0.012, recess=0.02, rim=0.05)
    kit.cyl("chest_port_rim", "accent", c + Vector((0, -0.02, -0.04)), c + Vector((0, -0.1, -0.05)), 0.17, 16)
    kit.cyl("chest_port", "frame_dark", c + Vector((0, -0.05, -0.04)), c + Vector((0, -0.12, -0.05)), 0.11, 16)
    kit.cyl("chest_cannon", "frame", c + Vector((0, 0.0, -0.04)), c + Vector((0, -0.3, -0.07)), 0.07, 12)
    for k, g in enumerate(("gem_green", "gem_red", "gem_orange", "gem_blue", "gem_purple", "gem_gold")):
        a = math.radians(90 + 60 * k)
        p = c + Vector((0.3 * math.cos(a), -0.06, -0.04 + 0.24 * math.sin(a)))
        kit.shell("chest_gem_%d" % k, g, p, (0.15, 0.07, 0.15), (0, 0, 45), 0.4, levels=1)   # v1b: bigger, to read from the front
    # belly plates
    for k, y in enumerate((-0.7, 0.0, 0.7)):
        c = kit.on_surface(core, (0, y, 0.95), (0, 0, -1), 0.02)
        kit.plate("belly_%d" % k, "frame", c, 0.8, 0.5, 0.05, (90, 0, 0), bend=0.2, bevel=0.01)
    # shoebill: folded feather wings on the shoulders, pearl blades with gold leading edges, sweeping back and up
    for s in (-1, 1):
        root = Vector((s * 0.72, -0.95, 2.28))
        for k, (back, up, ln) in enumerate(((0.9, 0.16, 1.9), (0.92, 0.26, 1.7), (0.94, 0.36, 1.45), (0.95, 0.46, 1.2))):
            d = Vector((s * 0.18, back, up)).normalized()
            mid = root + Vector((s * 0.05 * k, 0.12 * k, -0.08 * k)) + d * ln / 2
            yaw, pitch = math.degrees(math.atan2(d.x, d.y)), math.degrees(math.asin(d.z))
            kit.plate("wing_%d_%d" % (s, k), "main", mid, 0.22, ln, 0.05, (90 + pitch, 0, -yaw), bend=0.25, bevel=0.01, taper=0.45)
            kit.segment("wing_%d_%d_edge" % (s, k), "accent", root + Vector((s * 0.05 * k, 0.12 * k, -0.08 * k + 0.1)),
                        root + Vector((s * 0.05 * k, 0.12 * k, -0.08 * k + 0.1)) + d * ln * 0.85, 0.05, 0.05, 0.5)
        kit.disc("wing_root_%d" % s, root + Vector((s * 0.08, 0, 0)), 0.18, axis=(s, 0, 0), depth=0.12)
    # the shoebill's head-gun as a dorsal cannon between the wings, over the head
    base = Vector((0, -1.0, 2.42))
    kit.shell("dorsal_gun_mount", "frame", base, (0.36, 0.5, 0.22), (0, 0, 0), 0.5, levels=1)
    kit.cyl("dorsal_gun", "frame_dark", base + Vector((0, -0.1, 0.08)), base + Vector((0, -1.05, 0.2)), 0.07, 12)
    kit.cyl("dorsal_gun_tip", "accent", base + Vector((0, -1.0, 0.19)), base + Vector((0, -1.12, 0.21)), 0.09, 12)


# ---- the tail: a kangaroo's thick root, pangolin scales down it, the crimson cone tip -------------------------
TAIL = [Vector((0, 1.5, 1.72)), Vector((0, 2.15, 1.42)), Vector((0, 2.75, 1.05)), Vector((0, 3.25, 0.72)), Vector((0, 3.65, 0.5))]


def tail():
    r = (0.36, 0.3, 0.23, 0.16)
    for k in range(4):
        a, b = TAIL[k], TAIL[k + 1]
        kit.segment("tail_core_%d" % k, "frame", a, b, r[k] * 2, r[k] * 1.9, 0.5)
        d = (b - a).normalized()
        for j in range(3):   # scales on top and both sides, each a shingle tipped back
            p = a.lerp(b, (j + 0.5) / 3)
            pitch = math.degrees(math.atan2(-d.z, d.y))
            kit.plate("tail_scale_%d_%d" % (k, j), "main", p + Vector((0, 0, r[k] * 0.9)), r[k] * 1.7, r[k] * 1.3, 0.04,
                      (-90 + pitch - 14, 0, 0), bend=0.5, bevel=0.01, taper=0.8)
    a, b = TAIL[-1], TAIL[-1] + (TAIL[-1] - TAIL[-2]).normalized() * 0.5
    kit.segment("tail_core_3_cone", "trim", a, b, 0.24, 0.22, 0.95)


def tail_bone(name):
    if name.startswith(("tail_core_", "tail_scale_")):
        return int(name.split("_")[2])
    return None


# ---- the head: a wolf's wedge with fangs and tall ears, the shoebill's gold bill crest, the hippo's tusks -------
HC = Vector((0, -2.25, 2.25))


def head():
    hc = HC
    kit.segment("neck_core", "frame", Vector((0, -1.35, 2.05)), hc + Vector((0, 0.25, -0.05)), 0.62, 0.6, 0.5)
    for k in range(2):
        kit.plate("neckplate_%d" % k, "main", Vector((0, -1.55 - 0.22 * k, 2.36 - 0.04 * k)), 0.5, 0.2, 0.05, (-80, 0, 0),
                  bend=0.45, bevel=0.01)
    side = [(0.32, 0.0), (0.28, 0.3), (0.0, 0.38), (-0.4, 0.3), (-0.8, 0.16), (-0.96, 0.02), (-0.86, -0.12), (-0.3, -0.18), (0.26, -0.15)]
    front = kit.mirror_x([(0.15, 0.38), (0.3, 0.28), (0.34, 0.05), (0.3, -0.15)])
    core = kit.profile_solid("head_core", "main", hc, side, front, chamfer=0.015)
    jaw_side = [(0.1, -0.14), (-0.3, -0.18), (-0.82, -0.14), (-0.86, -0.26), (-0.6, -0.36), (0.05, -0.3)]
    jaw_front = kit.mirror_x([(0.28, -0.14), (0.3, -0.26), (0.2, -0.36)])
    kit.profile_solid("head_jaw", "frame", hc, jaw_side, jaw_front, chamfer=0.012)
    # the shoebill's bill: a gold crest over the snout, hooked down at the tip
    kit.plate("head_bill", "accent", hc + Vector((0, -0.5, 0.36)), 0.4, 0.8, 0.07, (-82, 0, 0), bend=0.55, bevel=0.012, taper=0.7)
    kit.segment("head_bill_hook", "accent", hc + Vector((0, -0.92, 0.3)), hc + Vector((0, -1.04, 0.12)), 0.12, 0.1, 0.5)
    kit.segment("head_bill_seam", "trim", hc + Vector((0, -0.12, 0.42)), hc + Vector((0, -0.86, 0.36)), 0.03, 0.03, 0.4)
    for s in (-1, 1):
        for k, y in enumerate((-0.42, -0.62, -0.8)):   # the wolf's fangs, upper row
            kit.segment("head_fang_%d_%d" % (s, k), "tusk", hc + Vector((s * 0.2, y, -0.14)), hc + Vector((s * 0.2, y - 0.02, -0.3)),
                        0.06, 0.05, 0.6)
        kit.segment("head_tusk_%d" % s, "tusk", hc + Vector((s * 0.3, -0.3, -0.3)), hc + Vector((s * 0.4, -0.46, -0.04)),
                    0.12, 0.1, 0.5)   # the hippo's tusks at the jaw corners
        kit.shell("eye_%d_socket" % s, "frame_dark", hc + Vector((s * 0.27, -0.3, 0.18)), (0.1, 0.24, 0.1), (0, 0, 0), 0.5, levels=1)
        kit.shell("eye_%d" % s, "eye_src", hc + Vector((s * 0.32, -0.3, 0.18)), (0.05, 0.18, 0.06), (0, 0, 0), 0.0, levels=0)
        # tall pointed ears (wolf and kangaroo), crimson inside
        kit.plate("ear_%d" % s, "main", hc + Vector((s * 0.2, 0.1, 0.62)), 0.24, 0.55, 0.05, (-12, 0, s * 30), bend=0.5, taper=0.2, bevel=0.008)
        kit.plate("ear_%d_inner" % s, "trim", hc + Vector((s * 0.19, 0.07, 0.6)), 0.12, 0.4, 0.03, (-12, 0, s * 30), bend=0.5, taper=0.2, bevel=0.005)
        kit.disc("head_hinge_%d" % s, hc + Vector((s * 0.33, -0.02, -0.1)), 0.1, depth=0.1)


# ---- legs: gorilla forelegs (huge forearms, knuckle fists), kangaroo hind legs (digitigrade, long feet) --------
JOINTS = {}


def legs():
    for s in (-1, 1):
        side = "L" if s == 1 else "R"
        sh, el, wr = Vector((s * 0.95, -1.15, 1.95)), Vector((s * 1.05, -0.95, 1.12)), Vector((s * 1.0, -1.25, 0.42))
        hp, kn = Vector((s * 0.74, 1.05, 1.55)), Vector((s * 0.82, 0.5, 0.98))
        an, toe = Vector((s * 0.76, 1.35, 0.26)), Vector((s * 0.76, 0.45, 0.06))
        JOINTS.update({"sh." + side: sh, "el." + side: el, "wr." + side: wr, "fingers." + side: wr + Vector((0, -0.25, -0.3)),
                       "hp." + side: hp, "kn." + side: kn, "an." + side: an, "toe." + side: toe})
        # gorilla forelegs
        kit.limb_solid("front_upper_%d" % s, "frame", sh, el, (s, 0, 0), [(0, 0.34, 0.32), (1, 0.28, 0.26)], [(0, 0.34), (1, 0.28)], chamfer=0.05)
        kit.limb_solid("front_lower_%d" % s, "frame", el, wr, (s, 0, 0), [(0, 0.3, 0.28), (0.6, 0.4, 0.36), (1, 0.34, 0.32)],
                       [(0, 0.3), (0.6, 0.4), (1, 0.34)], chamfer=0.08)
        lo = bpy.data.objects["front_lower_%d" % s]   # v1b: the big forearm gunmetal with a curved pearl guard on its outer face (a pearl box read crude)
        kit.plate("front_lower_%d_guard" % s, "main", kit.on_surface(lo, el.lerp(wr, 0.55), (s, -0.4, 0), 0.03), 0.42, 0.62, 0.05,
                  (0, 0, s * 70), bend=0.6, bevel=0.012, rim=0.04)
        kit.plate("front_scale_%d" % s, "main", sh + Vector((s * 0.26, 0.0, 0.2)), 0.64, 0.58, 0.07, (-10, 0, s * 80), bend=0.75, bevel=0.012, rim=0.05)   # v1b: smaller, rounder
        kit.disc("front_elbow_%d" % s, el + Vector((s * 0.36, 0, 0)), 0.17, depth=0.1)
        kit.shell("front_foot_%d" % s, "frame", wr + Vector((0, -0.08, -0.18)), (0.5, 0.56, 0.42), (0, 0, 0), 0.5, levels=1)
        for k in range(4):   # gold knuckles
            kit.segment("front_claw_%d_%d" % (s, k), "accent", wr + Vector((s * (-0.16 + 0.11 * k), -0.36, -0.22)),
                        wr + Vector((s * (-0.16 + 0.11 * k), -0.38, -0.36)), 0.1, 0.12, 0.5)
        # kangaroo hind legs
        kit.limb_solid("hind_upper_%d" % s, "main", hp, kn, (s, 0, 0), [(0, 0.5, 0.46), (1, 0.32, 0.3)], [(0, 0.5), (1, 0.32)], chamfer=0.05)
        kit.limb_solid("hind_lower_%d" % s, "frame", kn, an, (s, 0, 0), [(0, 0.24, 0.22), (1, 0.18, 0.16)], [(0, 0.24), (1, 0.18)], chamfer=0.04)
        kit.plate("hind_scale_%d" % s, "main", kn.lerp(hp, 0.5) + Vector((s * 0.27, 0, 0.02)), 0.5, 0.52, 0.06, (0, 0, s * 84), bend=0.65, bevel=0.012, rim=0.05)   # v1b: smaller, rounder
        kit.disc("hind_knee_%d" % s, kn + Vector((s * 0.22, 0, 0)), 0.15, depth=0.1)
        kit.shell("hind_foot_%d" % s, "frame", an.lerp(toe, 0.5) + Vector((0, 0, 0.02)), (0.24, 1.0, 0.14), (0, 0, 0), 0.5, levels=1)
        kit.shell("hind_foot_%d_cap" % s, "main", an.lerp(toe, 0.62) + Vector((0, 0, 0.1)), (0.22, 0.6, 0.1), (0, 0, 0), 0.5, levels=1)
        for k in range(2):
            kit.segment("hind_claw_%d_%d" % (s, k), "accent", toe + Vector((s * (-0.05 + 0.1 * k), 0.06, 0.03)),
                        toe + Vector((s * (-0.05 + 0.1 * k), -0.16, 0.0)), 0.07, 0.06, 0.5)


CFG = {
    "name": "combiner_m",
    "head": ("head_", "neck", "eye_", "ear_"),
    "tail_bone": tail_bone,
    "tail_points": TAIL,
    "tail_sway": 1.2,
    "body_bone": ((0, 1.0, 1.7), (0, -1.0, 1.8)),
    "head_bone": ((0, -1.4, 2.1), (0, -3.2, 2.2)),
    "joints": JOINTS,
    "stride": 0.3,
    "battle_feet": {"R_arm": (0.0, 0.0), "L_arm": (-0.3, 0.0), "R_leg": (0.0, 0.0), "L_leg": (0.0, 0.0)},
    "stance": "clip=battle;frame=1",
    "crouch": 0.04,
    "front_path": (0.04, 0.0, 0.09, -15),
    "hind_path": (-0.04, 0.0, 0.1, 0),
}


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    body()
    tail()
    head()
    legs()
    quad.tag_parts(CFG)
    ob = kit.join_into_one()
    ob.name = "combiner_m"
    quad.rig_and_clips(ob, CFG, kit, OUT_BLEND)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("COMBINER_M_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
