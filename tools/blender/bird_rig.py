# Shared bird rig for the creature factory (Claude, 2026-10-12): two legs and two folded wings. Built on quad_rig.py
# (same bone names, so the kit's clip() and the sprite renderer work unchanged: the wings ride upper_arm / forearm /
# hand, a bird's wing being its arm; the legs ride thigh / shin / foot, where the shin ends at the ankle, the joint that
# looks like a backward knee, and the foot is the long bare tarsus with the toes on it).
#
# Part naming the tagger understands (s = 1 is .L, -1 is .R):
#   wing_upper_s*            -> upper_arm      leg_thigh_s*           -> thigh
#   wing_fore_s*, wing_lead_s* -> forearm      leg_shin_s*, leg_ankle_s* -> shin
#   wing_hand_s*             -> hand           leg_foot_s*, toe_s_k   -> foot
#   anything starting with a cfg["head"] prefix -> head; the rest -> body
# Joints: cfg["joints"] holds sh / el / wr / fingers (the folded wing) and hp / kn / an / toe, each ".L" and ".R".
import importlib.util, math, os, re
import bpy

_spec = importlib.util.spec_from_file_location("quad_rig", os.path.join(os.path.dirname(os.path.abspath(__file__)), "quad_rig.py"))
quad = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(quad)
_aspec = importlib.util.spec_from_file_location("attacks", os.path.join(os.path.dirname(os.path.abspath(__file__)), "attacks.py"))
attacks = importlib.util.module_from_spec(_aspec)
_aspec.loader.exec_module(attacks)

PART_BONE = (("wing_upper", "upper_arm"), ("wing_fore", "forearm"), ("wing_lead", "forearm"), ("wing_hand", "hand"),
             ("leg_thigh", "thigh"), ("leg_shin", "shin"), ("leg_ankle", "shin"), ("leg_foot", "foot"), ("toe", "foot"))
CONTACT = {"thigh.L": 0.0, "thigh.R": 0.5}   # a walk: the feet alternate
DUTY = 0.62
WALK_FRAMES = 40   # slow: the shoebill "strides very slowly"


def bone_for(name, cfg):
    for prefix, bone in cfg.get("part_bones", ()):   # extra bones (2026-10-19): a jaw, a hatch, a flip-out gun
        if name.startswith(prefix):
            return bone
    if name.startswith(cfg["head"]):
        return "head"
    for prefix, bone in PART_BONE:
        if name.startswith(prefix):
            # the side is the last 1 or -1 token; words after it ("_1_bolt", "_1_edge", "_1_fan2", "_1_2hl") are allowed.
            # 2026-10-16 (creature factory pass, tools/blender/bind_audit.py): digits only here put 33 far-wing pieces on
            # the near wing's bones; quad_rig had the same fix on 2026-10-13.
            side = re.search(r"_(-1|1)(?:_[A-Za-z0-9]+)*$", name)
            return "%s.%s" % (bone, "L" if side and side.group(1) == "1" else "R")
    return "body"


def tag_parts(cfg):
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


def _phase(t, c):
    u = (t - c) % 1.0
    if u < DUTY:
        return -1.0 + 2.0 * u / DUTY, 0.0
    v = (u - DUTY) / (1.0 - DUTY)
    return 1.0 - 2.0 * (0.5 - 0.5 * math.cos(math.pi * v)), math.sin(math.pi * v)


def walk_pose_for(cfg):
    """The ankle follows a path, flat along the floor while the foot is planted and an arc while it steps; IK on thigh
    and shin finds the angles; the tarsus keeps its rest angle while planted, so the long toes stay flat, and tucks
    back in swing. The head pumps a little at each step, the wings stay folded."""
    J, stride, crouch = cfg["joints"], cfg.get("stride", 0.36), cfg.get("crouch", 0.04)
    back, lift_h, curl = cfg.get("leg_path", (0.0, 0.12, 25))

    def pose(t):
        p = {}
        for side in ("L", "R"):
            r, m, e = J["hp." + side], J["kn." + side], J["an." + side]
            a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
            sw, lift = _phase(t, CONTACT["thigh." + side])
            w1, w2 = quad.ik2(a, b, (a[0] + b[0] + back + sw * stride / 2, a[1] + b[1] + crouch + lift_h * lift))
            p["thigh." + side] = (w1, 0, 0)
            p["shin." + side] = (w2 - w1, 0, 0)
            p["foot." + side] = (-w2 + curl * lift, 0, 0)
        w = 2 * math.pi * t
        p["body"] = (0, 2.0 * math.sin(w), 0)          # weight rolls over the planted foot
        p["head"] = (-3 * math.cos(2 * w), 0, 0)       # a small pump at each step
        return p
    return pose


def battle_pose_for(cfg):
    """The battle stance by leg (2026-10-13, shoebill: his two legs stand apart in the three-quarter view and no walk
    frame separates ours). cfg["battle_legs"] = {"R": (dy, dz, splay), "L": ...}: the ankle moved from its planted
    target by dy (negative is forward) and dz, IK on thigh and shin, then the whole leg swung out sideways by splay
    degrees (about the thigh's own Z); the tarsus turns back by the same so the long toes stay flat."""
    J, crouch = cfg["joints"], cfg.get("crouch", 0.04)
    back = cfg.get("leg_path", (0.0, 0.12, 25))[0]
    legs = cfg["battle_legs"]

    def pose(t):
        p = {}
        for side in ("L", "R"):
            dy, dz, splay = legs.get(side, (0.0, 0.0, 0.0))
            r, m, e = J["hp." + side], J["kn." + side], J["an." + side]
            a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
            w1, w2 = quad.ik2(a, b, (a[0] + b[0] + back + dy, a[1] + b[1] + crouch + dz))
            sgn = 1 if side == "L" else -1
            p["thigh." + side] = (w1, 0, sgn * splay)
            p["shin." + side] = (w2 - w1, 0, 0)
            p["foot." + side] = (-w2, 0, -sgn * splay)
        p["head"] = tuple(cfg.get("battle_head", (-3, 0, 0)))   # the walk's first frame tilts the head 3 degrees; the stance kept it
        return p
    return pose


def idle_pose_for(cfg):
    """Statue-like: barely a breath, the head turning slowly to scan."""
    def pose(t):
        br = math.sin(2 * math.pi * t)
        return {"body": (0.8 * br, 0, 0), "head": (-1.0 * br, 0, 8 * math.sin(2 * math.pi * t + 0.6)),
                "upper_arm.L": (0, 0, 0.6 * br), "upper_arm.R": (0, 0, -0.6 * br), "body_move": (0, 0, 0.008 * br)}
    return pose


def stance_spec_default():
    """Near (.R) foot forward, far foot back, wings at rest, so the side view shows the stride."""
    out = ["base=1"]
    for limb, b, sw in (("R_leg", "thigh.R", -0.5), ("L_leg", "thigh.L", 0.5)):
        u = DUTY * (sw + 1) / 2
        out.append("%s=%d" % (limb, round(((u + CONTACT[b]) % 1.0) * WALK_FRAMES) + 1))
    return ";".join(out)


def rig_and_clips(ob, cfg, kit, out_blend):
    rig = quad.make_rig(ob, cfg)
    kit.knuckle_walk(rig)   # 24 fps, Euler rotations
    kit.clip(rig, "walk", WALK_FRAMES, walk_pose_for(cfg))
    kit.clip(rig, "idle", 48, idle_pose_for(cfg))
    if cfg.get("battle_legs"):   # a bird may pose its battle stance by leg; its stance is then "clip=battle"
        kit.clip(rig, "battle", 2, battle_pose_for(cfg))
    if cfg.get("battle_set"):   # battle clips (tools/blender/attacks.py, 2026-10-13)
        attacks.bake(kit, rig, cfg["battle_set"], attacks.bird_stance(quad.ik2, cfg))
    with open(out_blend.replace(".blend", ".stance"), "w") as f:
        f.write(cfg.get("stance") or stance_spec_default())
    return rig
