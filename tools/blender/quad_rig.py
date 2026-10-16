# Shared quadruped rig for the creature factory (Claude, 2026-10-12). Lifted from build_pangolin_m.py v18, where it
# was proven: planted feet within 1.5 cm through the walk, 8-10 cm steps. A machine build supplies a config dict and
# calls rig_and_clips() after kit.join_into_one(). Bone names match the gorilla's (body, head, upper_arm / forearm /
# hand, thigh / shin / foot, .L / .R) plus tail.N, so the kit's clip() and tools/blender/render_sprite_views.py work
# unchanged.
#
# Part naming the tagger understands (s = 1 is .L, -1 is .R, as in the gorilla):
#   front_upper_s, front_scale_s            -> upper_arm      hind_upper_s, hind_scale_s          -> thigh
#   front_lower_s, front_shin_s, front_elbow_s -> forearm     hind_lower_s, hind_shin_s, hind_knee_s -> shin
#   front_foot_s, front_claw_s_k            -> hand           hind_foot_s, hind_claw_s_k          -> foot
#   anything starting with a cfg["head"] prefix -> head; cfg["tail_bone"](name) -> tail index or None; the rest -> body
# Joints: cfg["joints"] holds sh / el / wr / fingers and hp / kn / an / toe, each ".L" and ".R", as Vectors.
import bpy, importlib.util, math, os, re
from mathutils import Vector

_aspec = importlib.util.spec_from_file_location("attacks", os.path.join(os.path.dirname(os.path.abspath(__file__)), "attacks.py"))
attacks = importlib.util.module_from_spec(_aspec)
_aspec.loader.exec_module(attacks)

PART_BONE = (("front_upper", "upper_arm"), ("front_scale", "upper_arm"), ("front_lower", "forearm"),
             ("front_shin", "forearm"), ("front_elbow", "forearm"), ("front_foot", "hand"), ("front_claw", "hand"),
             ("hind_upper", "thigh"), ("hind_scale", "thigh"), ("hind_lower", "shin"), ("hind_shin", "shin"),
             ("hind_knee", "shin"), ("hind_foot", "foot"), ("hind_claw", "foot"))

# Lateral-sequence walk, the slow gait of most quadrupeds: left hind, left fore, right hind, right fore, a quarter
# cycle apart, each foot down 70% of the cycle.
CONTACT = {"thigh.L": 0.0, "upper_arm.L": 0.25, "thigh.R": 0.5, "upper_arm.R": 0.75}
DUTY = 0.7
WALK_FRAMES = 36


def bone_for(name, cfg):
    if name.startswith(cfg["head"]):
        return "head"
    k = cfg["tail_bone"](name) if cfg.get("tail_bone") else None
    if k is not None:
        return "tail.%d" % k
    for prefix, bone in PART_BONE:
        if name.startswith(prefix):
            side = re.search(r"_(-1|1)(?:_[A-Za-z0-9]+)*$", name)   # 2026-10-13: also "_1_cap", "_-1_hub" (those rode the .R bone on both sides)
            return "%s.%s" % (bone, "L" if side and side.group(1) == "1" else "R")
    return "body"


def tag_parts(cfg):
    """Before the join: one vertex group per part, named for the bone it rides (machines are rigid, weight 1)."""
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            vg = o.vertex_groups.new(name=bone_for(o.name, cfg))
            vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    if os.environ.get("BIND_NAMES"):   # tools/blender/bind_audit.py: which part rides which bone, before the join
        import json
        rows = []
        for o in bpy.context.scene.objects:
            if o.type == "MESH" and o.vertex_groups:
                c = sum((o.matrix_world @ v.co for v in o.data.vertices), __import__("mathutils").Vector()) / max(1, len(o.data.vertices))
                rows.append({"name": o.name, "bone": o.vertex_groups[0].name, "verts": len(o.data.vertices), "center": [round(x, 3) for x in c]})
        with open(os.environ["BIND_NAMES"], "w") as fh:
            json.dump(rows, fh, indent=0)


def make_rig(ob, cfg):
    arm = bpy.data.armatures.new(cfg["name"] + "_rig")
    rig = bpy.data.objects.new(cfg["name"] + "_rig", arm)
    bpy.context.scene.collection.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones

    def bone(name, head, tail, parent=None):
        b = eb.new(name)
        b.head, b.tail = Vector(head), Vector(tail)
        b.align_roll(Vector((1, 0, 0)).cross((b.tail - b.head).normalized()))   # local X = world X: pitch is swing
        if parent:
            b.parent = eb[parent]
    bone("body", *cfg["body_bone"])
    bone("head", *cfg["head_bone"], "body")
    pts = cfg.get("tail_points", [])
    for i in range(len(pts) - 1):
        bone("tail.%d" % i, pts[i], pts[i + 1], "body" if i == 0 else "tail.%d" % (i - 1))
    J = cfg["joints"]
    for side in ("L", "R"):
        bone("upper_arm." + side, J["sh." + side], J["el." + side], "body")
        bone("forearm." + side, J["el." + side], J["wr." + side], "upper_arm." + side)
        bone("hand." + side, J["wr." + side], J["fingers." + side], "forearm." + side)
        bone("thigh." + side, J["hp." + side], J["kn." + side], "body")
        bone("shin." + side, J["kn." + side], J["an." + side], "thigh." + side)
        bone("foot." + side, J["an." + side], J["toe." + side], "shin." + side)
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.parent = rig
    ob.modifiers.new("rig", "ARMATURE").object = rig
    return rig


def _phase(t, c):
    u = (t - c) % 1.0
    if u < DUTY:
        return -1.0 + 2.0 * u / DUTY, 0.0
    v = (u - DUTY) / (1.0 - DUTY)
    return 1.0 - 2.0 * (0.5 - 0.5 * math.cos(math.pi * v)), math.sin(math.pi * v)


def ik2(a, b, target):
    """Two-bone IK in the leg's side plane (y, z). a, b: the upper and lower bone vectors at rest; target: where the
    lower bone's end should be, relative to the upper bone's root. Returns the world swing of each bone in degrees
    (positive swings toward +y, the back, as the rig's X rotations do), bending the joint the way it bends at rest."""
    l1, l2 = math.hypot(*a), math.hypot(*b)
    d = max(abs(l1 - l2) + 1e-4, min(l1 + l2 - 1e-4, math.hypot(*target)))
    pa, pb, pt = math.atan2(a[1], a[0]), math.atan2(b[1], b[0]), math.atan2(target[1], target[0])
    al = math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    rest = (a[0] + b[0], a[1] + b[1])   # pick the elbow / knee side that matches the rest pose
    sgn = 1 if (a[0] * rest[1] - a[1] * rest[0]) < 0 else -1
    p1 = pt + sgn * al
    e = (l1 * math.cos(p1), l1 * math.sin(p1))
    p2 = math.atan2(target[1] - e[1], target[0] - e[0])
    return math.degrees(p1 - pa), math.degrees(p2 - pb)


def walk_pose_for(cfg):
    """Each wrist / ankle follows a path: flat along the floor while planted (all four at one height, the body
    cfg["crouch"] lower so no leg runs out of reach), an arc while stepping. IK finds the angles; hands and feet stay
    level while planted and curl by cfg's curl while stepping. Fixed leg angles could not keep four feet on one
    floor: the pangolin's planted feet were 14.9 cm apart that way."""
    J, stride, crouch = cfg["joints"], cfg.get("stride", 0.24), cfg.get("crouch", 0.04)
    legs = {"upper_arm": ("sh", "el", "wr", "forearm", "hand") + tuple(cfg["front_path"]),   # back, down, lift, curl
            "thigh": ("hp", "kn", "an", "shin", "foot") + tuple(cfg["hind_path"])}
    n_tail = max(0, len(cfg.get("tail_points", [])) - 1)

    def pose(t):
        p = {}
        for side in ("L", "R"):
            for upper, (j0, j1, j2, lower, end, back, down, lift_h, curl) in legs.items():
                r, m, e = J["%s.%s" % (j0, side)], J["%s.%s" % (j1, side)], J["%s.%s" % (j2, side)]
                a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
                sw, lift = _phase(t, CONTACT[upper + "." + side])
                w1, w2 = ik2(a, b, (a[0] + b[0] + back + sw * stride / 2, a[1] + b[1] + crouch + down + lift_h * lift))
                p[upper + "." + side] = (w1, 0, 0)
                p[lower + "." + side] = (w2 - w1, 0, 0)
                p[end + "." + side] = (-w2 + curl * lift, 0, 0)
        w = 2 * math.pi * t
        p["head"] = (2 * math.cos(2 * w), 0, 4 * math.sin(w + 0.5))
        for i in range(n_tail):
            p["tail.%d" % i] = (0, 0, (5 + 3 * i) * cfg.get("tail_sway", 1.0) * math.sin(w - 0.6 * (i + 1)))
        return p
    return pose


def battle_pose_for(cfg):
    """The battle stance as explicit foot positions (2026-10-13, wolf pass 3: the reference's feet sit where no walk
    frame puts them). cfg["battle_feet"] = {"R_arm": (dy, dz), ...}: each wrist / ankle moved from its planted
    walk target by dy (negative is forward) and dz; two-bone IK finds the leg. Hands and feet stay level."""
    J, crouch, feet = cfg["joints"], cfg.get("crouch", 0.04), cfg["battle_feet"]
    legs = {"arm": ("upper_arm", "sh", "el", "wr", "forearm", "hand") + tuple(cfg["front_path"]),
            "leg": ("thigh", "hp", "kn", "an", "shin", "foot") + tuple(cfg["hind_path"])}

    def pose(t):
        p = {}
        for side in ("L", "R"):
            for kind, (upper, j0, j1, j2, lower, end, back, down, lift_h, curl) in legs.items():
                r, m, e = J["%s.%s" % (j0, side)], J["%s.%s" % (j1, side)], J["%s.%s" % (j2, side)]
                a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
                dy, dz = feet.get("%s_%s" % (side, kind), (0.0, 0.0))
                w1, w2 = ik2(a, b, (a[0] + b[0] + back + dy, a[1] + b[1] + crouch + down + dz))
                p[upper + "." + side] = (w1, 0, 0)
                p[lower + "." + side] = (w2 - w1, 0, 0)
                p[end + "." + side] = (-w2, 0, 0)
        return p
    return pose


def idle_pose_for(cfg):
    n_tail = max(0, len(cfg.get("tail_points", [])) - 1)

    def pose(t):
        br = math.sin(2 * math.pi * t)
        p = {"body": (1.0 * br, 0, 0), "head": (-1.5 * br, 0, 10 * math.sin(2 * math.pi * t + 0.6)),
             "body_move": (0, 0, 0.012 * br)}
        for i in range(n_tail):
            p["tail.%d" % i] = (0, 0, (4 + 3 * i) * cfg.get("tail_sway", 1.0) * math.sin(2 * math.pi * t - 0.8 * (i + 1)))
        return p
    return pose


def _ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _front(cfg):
    """+1 if the machine faces +y, -1 if it faces -y. Bones turn about world X (make_rig), so a positive X turn lifts
    whatever lies toward +y: multiplying by this makes "nose up" and "leg forward" the same sign on every machine."""
    hb, bb = cfg["head_bone"], cfg["body_bone"]
    mid = (bb[0][1] + bb[1][1]) / 2
    return 1.0 if hb[1][1] > mid else -1.0


def attack_pose_for(cfg):
    """Lunge (combat set, 2026-10-12, after the gorilla's punch): rock back onto the hind legs with the head up
    (0 to 0.35), drive forward with the head down and the front legs reaching (0.35 to 0.55), then settle back."""
    F = _front(cfg)

    def pose(t):
        wind = _ease(t / 0.35) * (1 - _ease((t - 0.35) / 0.12))
        hit = _ease((t - 0.35) / 0.2) * (1 - _ease((t - 0.6) / 0.4))
        return {"body": (F * (7 * wind - 9 * hit), 0, 0), "head": (F * (14 * wind - 22 * hit), 0, 0),
                "upper_arm.L": (F * 22 * hit, 0, 0), "upper_arm.R": (F * 26 * hit, 0, 0),
                "forearm.L": (-F * 10 * hit, 0, 0), "forearm.R": (-F * 12 * hit, 0, 0),
                "thigh.L": (-F * 12 * hit, 0, 0), "thigh.R": (-F * 14 * hit, 0, 0),
                "body_move": (0, F * (0.4 * hit - 0.14 * wind), 0)}
    return pose


def hit_pose_for(cfg):
    """Struck from the front, as the gorilla's hit: a sharp jolt back by frame 3, nose snapped up, heavy recovery."""
    F = _front(cfg)
    n_tail = max(0, len(cfg.get("tail_points", [])) - 1)

    def pose(t):
        k = _ease(t / 0.15) * (1 - _ease((t - 0.25) / 0.75))
        p = {"body": (F * 6 * k, 0, 0), "head": (F * 18 * k, 0, 6 * k),
             "upper_arm.L": (-F * 10 * k, 0, 0), "upper_arm.R": (-F * 10 * k, 0, 0),
             "body_move": (0, -F * 0.2 * k, 0)}
        for i in range(n_tail):
            p["tail.%d" % i] = (0, 0, -(6 + 4 * i) * k)
        return p
    return pose


def death_pose_for(cfg):
    """Shut-down collapse: the front legs fold, then the hind legs, the body rolls onto its side and the head and
    tail drop; holds at the end. clip() keeps the lowest point on the floor throughout."""
    F = _front(cfg)
    n_tail = max(0, len(cfg.get("tail_points", [])) - 1)

    def pose(t):
        front = _ease(t / 0.35)
        hind = _ease((t - 0.2) / 0.35)
        roll = _ease((t - 0.35) / 0.45)
        p = {"upper_arm.L": (-F * 30 * front, 0, 0), "upper_arm.R": (-F * 30 * front, 0, 0),
             "forearm.L": (F * 70 * front, 0, 0), "forearm.R": (F * 70 * front, 0, 0),
             "thigh.L": (F * 25 * hind, 0, 0), "thigh.R": (F * 25 * hind, 0, 0),
             "shin.L": (-F * 50 * hind, 0, 0), "shin.R": (-F * 50 * hind, 0, 0),
             "body": (-F * 6 * front, 38 * roll, 0), "head": (-F * 20 * roll, 0, 12 * roll)}
        for i in range(n_tail):
            p["tail.%d" % i] = (-F * 4 * roll, 0, 0)
        return p
    return pose


def stance_spec():
    """SPRITE_STANCE for the renderer: each leg held from the walk at its own point of the stroke, near (.R) fore leg
    forward and near hind leg back, the far pair the other way, so the side view shows four staggered contacts."""
    sweep = {"R_arm": ("upper_arm.R", -0.5), "L_arm": ("upper_arm.L", 0.5),
             "R_leg": ("thigh.R", 0.4), "L_leg": ("thigh.L", -0.4)}
    out = ["base=1"]
    for limb, (b, sw) in sweep.items():
        u = DUTY * (sw + 1) / 2
        out.append("%s=%d" % (limb, round(((u + CONTACT[b]) % 1.0) * WALK_FRAMES) + 1))
    return ";".join(out)


def rig_and_clips(ob, cfg, kit, out_blend):
    """After the join: rig, walk, idle, attack, hit and death clips, and the stance file next to the .blend (read by the sprite round)."""
    rig = make_rig(ob, cfg)
    kit.knuckle_walk(rig)   # 24 fps, Euler rotations
    kit.clip(rig, "walk", WALK_FRAMES, walk_pose_for(cfg))
    kit.clip(rig, "idle", 48, idle_pose_for(cfg))
    kit.clip(rig, "attack", 30, attack_pose_for(cfg))
    kit.clip(rig, "hit", 20, hit_pose_for(cfg))
    kit.clip(rig, "death", 48, death_pose_for(cfg))
    if cfg.get("battle_feet"):   # a machine may pose its battle stance by foot positions; its stance is then "clip=battle"
        kit.clip(rig, "battle", 2, battle_pose_for(cfg))
    if cfg.get("battle_set"):   # battle clips (tools/blender/attacks.py, 2026-10-13): b_idle, three attacks, b_hit, b_death
        attacks.bake(kit, rig, cfg["battle_set"], attacks.quad_stance(ik2, cfg))
    for b in rig.pose.bones:   # back to rest, as the gorilla's animation_set, so stills and the saved file show it
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    bpy.context.view_layer.update()
    with open(out_blend.replace(".blend", ".stance"), "w") as f:
        f.write(cfg.get("stance") or stance_spec())   # a machine's CFG may set its own stance (part pass, 2026-10-13)
    return rig
