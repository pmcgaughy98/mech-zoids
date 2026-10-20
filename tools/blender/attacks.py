# Battle clip foundations for the starters (Claude, 2026-10-13; Preston: "Use the synthesis. Build Attack animation
# foundations for our starters"). The gorilla's clips (build_ape_l_v2.py: punch, slam, throw) were the first; this
# module gives the other five the same set: idle, three attacks (one per roster weapon in scripts/data/machines.gd,
# named by its "clip"), hit and death.
#
# The rules come from reports/Gorilla mech animation foundation.md: anticipation, action, reaction; heavy reads as a
# long held anticipation, one fast strike and a settle in parts; the contact frame is skipped (the first strike frame
# is already past the target); a machine never squashes, its mass moves as a unit and sub-parts arrive late; weight
# rocks back before a heavy action. Phase times below (fractions of a 36-frame clip) follow its 40-50 % anticipation,
# 10-15 % strike, 35-50 % recovery split.
#
# Every clip starts and ends on the machine's battle stance (the pose its installed sprites show), so the battle's idle
# and its attacks agree. A pose here is the kit's format: {bone: (rx, ry, rz) degrees, "body_move": (x, y, z) metres};
# rotations are added on top of the stance. Feet stay planted while the body moves (their IK targets shift against the
# body), unless a clip lets them travel. Sign conventions (checked on renders): on a bone pointing forward (body, head)
# negative rx lifts the front; on a tail bone positive rx lifts it; rz on body or tail swings it sideways.
import math
import os

ANT, HOLD, HIT, OVER, REC = 0.42, 0.5, 0.56, 0.62, 0.85   # anticipation peak, held, first strike frame, past, recovered
ATTACK_FRAMES = 36


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def env(t, keys):
    """Value at t from keys [(t, value)]: eased between keys, held outside. Values are numbers or tuples."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            if isinstance(v0, tuple):
                return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return keys[-1][1]


def strike(ant, hit, over=None, rec=None, hold=None):
    """The usual five-key attack curve for one channel: rest, anticipation (held), strike, past the target, recovery."""
    hold = ant if hold is None else hold
    over = hit if over is None else over
    zero = tuple(0.0 for _ in ant) if isinstance(ant, tuple) else 0.0
    rec = zero if rec is None else rec
    return [(0.0, zero), (ANT, ant), (HOLD, hold), (HIT, hit), (OVER, over), (REC, rec), (1.0, zero)]


def X(a):   # a pitch-only rotation
    return (float(a), 0.0, 0.0)


def Z(a):   # a yaw-only rotation
    return (0.0, 0.0, float(a))


# ---- the stance each clip starts from ----------------------------------------------------------------------------

def quad_stance(ik2, cfg):
    """Legs of a quadruped's battle stance (cfg["battle_feet"], as quad_rig.battle_pose_for), with every foot target
    shifted by `shift` (body-space metres, positive back) plus per-limb extras, so planted feet stay put."""
    J, crouch, feet = cfg["joints"], cfg.get("crouch", 0.04), cfg.get("battle_feet", {})
    legs = {"arm": ("upper_arm", "sh", "el", "wr", "forearm", "hand") + tuple(cfg["front_path"]),
            "leg": ("thigh", "hp", "kn", "an", "shin", "foot") + tuple(cfg["hind_path"])}
    # 2026-10-19 (wolf v94, Codex's stalking sprite): cfg["battle_body"] pitches the body in every battle clip, about the
    # body bone's head (positive is nose down), with each foot target turned back by the same angle so the feet stay
    # where they stood; cfg["battle_head"] adds to the head. Both default to none.
    th = math.radians(cfg.get("battle_body", (0, 0, 0))[0])
    pv = cfg["body_bone"][0]

    def fn(t, shift, extra):
        p = {}
        for side in ("L", "R"):
            for kind, (upper, j0, j1, j2, lower, end, back, down, lift_h, curl) in legs.items():
                r, m, e = J["%s.%s" % (j0, side)], J["%s.%s" % (j1, side)], J["%s.%s" % (j2, side)]
                a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
                key = "%s_%s" % (side, kind)
                dy, dz = feet.get(key, (0.0, 0.0))
                ex = extra.get(key, (0.0, 0.0))
                tgt = (a[0] + b[0] + back + dy + shift + ex[0], a[1] + b[1] + crouch + down + dz + ex[1])
                if th:   # the target in the pitched body's frame (turned by -th about the pivot)
                    wy, wz = r.y + tgt[0] - pv[1], r.z + tgt[1] - pv[2]
                    tgt = (wy * math.cos(th) + wz * math.sin(th) + pv[1] - r.y, -wy * math.sin(th) + wz * math.cos(th) + pv[2] - r.z)
                w1, w2 = ik2(a, b, tgt)
                p[upper + "." + side] = (w1, 0, 0)
                p[lower + "." + side] = (w2 - w1, 0, 0)
                p[end + "." + side] = (-w2 - math.degrees(th), 0, 0)
        if th:
            p["body"] = (math.degrees(th), 0, 0)
        if cfg.get("battle_head"):
            p["head"] = tuple(cfg["battle_head"])
        return p
    return fn


def bird_stance(ik2, cfg):
    """Legs and head of a bird's battle stance (cfg["battle_legs"], as bird_rig.battle_pose_for), planted the same way."""
    J, crouch = cfg["joints"], cfg.get("crouch", 0.04)
    back = cfg.get("leg_path", (0.0, 0.12, 25))[0]
    legs = cfg.get("battle_legs", {})

    def fn(t, shift, extra):
        p = {}
        for side in ("L", "R"):
            dy, dz, splay = legs.get(side, (0.0, 0.0, 0.0))
            ex = extra.get(side + "_leg", (0.0, 0.0))
            r, m, e = J["hp." + side], J["kn." + side], J["an." + side]
            a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
            w1, w2 = ik2(a, b, (a[0] + b[0] + back + dy + shift + ex[0], a[1] + b[1] + crouch + dz + ex[1]))
            sgn = 1 if side == "L" else -1
            p["thigh." + side] = (w1, 0, sgn * splay)
            p["shin." + side] = (w2 - w1, 0, 0)
            p["foot." + side] = (-w2, 0, -sgn * splay)
        p["head"] = tuple(cfg.get("battle_head", (0, 0, 0)))
        return p
    return fn


def fixed_stance(pose_fn, t0):
    """A rig without a stance solver (the kangaroo's hop): its stance frame, held. Feet ride the body."""
    base = pose_fn(t0)

    def fn(t, shift, extra):
        return {k: v for k, v in base.items()}
    return fn


def compose(stance, channels, plant=True):
    """A clip from a stance and channels {bone: keys, "move": keys, "feet": {limb: keys of (dy, dz)}}."""
    def pose(t):
        move = env(t, channels["move"]) if "move" in channels else (0.0, 0.0, 0.0)
        extra = {limb: env(t, keys) for limb, keys in channels.get("feet", {}).items()}
        p = stance(t, -move[1] if plant else 0.0, extra)
        base_move = p.pop("body_move", (0.0, 0.0, 0.0))
        for bone, keys in channels.items():
            if bone in ("move", "feet"):
                continue
            rot = env(t, keys)
            p[bone] = tuple(a + b for a, b in zip(p.get(bone, (0.0, 0.0, 0.0)), rot))
        p["body_move"] = tuple(a + b for a, b in zip(base_move, move))
        return p
    return pose


# ---- shared clips: idle, hit, death ------------------------------------------------------------------------------

def idle(stance):
    """Breathing on the stance: the body rises and settles 1.5 cm, the head lags a little."""
    def pose(t):
        w = 2 * math.pi * t
        p = stance(t, 0.0, {})
        p.pop("body_move", None)
        p["body"] = tuple(a + b for a, b in zip(p.get("body", (0, 0, 0)), X(-0.8 * math.sin(w))))
        p["head"] = tuple(a + b for a, b in zip(p.get("head", (0, 0, 0)), X(1.5 * math.sin(w - 0.7))))
        p["body_move"] = (0.0, 0.0, 0.015 * math.sin(w))
        return p
    return pose


def hit(stance):
    """Jolt back from the hit, the head snapping up a beat later, then home (the flash and shake are Godot's)."""
    return compose(stance, {"move": [(0.0, (0, 0, 0)), (0.2, (0, 0.12, 0.02)), (0.55, (0, 0.06, 0)), (1.0, (0, 0, 0))],
                            "body": [(0.0, X(0)), (0.2, X(-5)), (1.0, X(0))],
                            "head": [(0.0, X(0)), (0.3, X(-10)), (1.0, X(0))]})


def death(stance, side_fall=True):
    """Sinks and tips: the body drops and noses down, the head last; held on the final frame."""
    return compose(stance, {"move": [(0.0, (0, 0, 0)), (0.35, (0, 0.05, -0.12)), (1.0, (0, 0.08, -0.3))],
                            "body": [(0.0, (0, 0, 0)), (0.35, (6, 0, 0)), (1.0, (14, 0, 12 if side_fall else 0))],
                            "head": [(0.0, X(0)), (0.5, X(5)), (1.0, X(28))]}, plant=False)


# Pangolin p45 (2026-10-20): its tail is 1.3 times longer, so the same curl stood the cone 13 rows above a 320x180 screen
# in the roll (5 allowed): the body dives nose down and the tail points up. Less curl (0.8) stood it straighter, 18 rows;
# a tighter curl wraps the longer tail over the back into the ball and brings the tip down. PANGOLIN_P45=0 restores both.
RC = 1.4 if os.environ.get("PANGOLIN_P45", "1") == "1" else 1.0

# ---- the attacks, one set per machine ----------------------------------------------------------------------------

def wolf(stance):
    return {
        # Fang Lunge: weight back on the haunches, head down on the target, spring; jaws already past the bite
        "lunge": compose(stance, {"move": strike((0, 0.22, -0.06), (0, -0.5, 0.02), (0, -0.58, 0), (0, -0.12, 0)),
                                  "body": strike(X(-4), X(6), X(7)),
                                  "head": strike(X(8), X(-12), X(-14), X(-3), hold=X(10)),
                                  "feet": {"R_arm": strike((0, 0), (-0.25, 0.04), (-0.28, 0), (-0.08, 0)),
                                           "L_arm": strike((0, 0), (-0.18, 0.02), (-0.2, 0), (-0.06, 0))}}),
        # Howl Burst: head thrown back, chest up, then the blast snaps the head level and kicks the body back
        "howl": compose(stance, {"move": strike((0, 0.1, -0.03), (0, 0.2, 0), (0, 0.22, 0), (0, 0.05, 0)),
                                 "body": strike(X(-6), X(-2), X(-1)),
                                 "head": strike(X(-28), X(4), X(6), X(-4), hold=X(-30))}),
        # Shadow Dash: the deepest crouch, then a full-length pass forward with the legs stretched out
        "dash": compose(stance, {"move": strike((0, 0.3, -0.1), (0, -0.55, 0.05), (0, -0.62, 0), (0, -0.2, 0), hold=(0, 0.32, -0.11)),   # travel within the camera frame; the battle stage moves the sprite further
                                 "body": strike(X(3), X(-4), X(-2)),
                                 "head": strike(X(10), X(-6), X(-6))}),
    }


def hippo(stance):
    return {
        # Gape Crush: the head rears up as the jaw opens, then the whole head slams down past the target
        "gape": compose(stance, {"move": strike((0, 0.12, 0), (0, -0.3, 0), (0, -0.34, 0), (0, -0.05, 0)),
                                 "body": strike(X(-4), X(5), X(6)),
                                 "head": strike(X(-32), X(14), X(16), X(2), hold=X(-34))}),
        # Pressure Jets: braced low, the valves aim, the jets kick the body back and the head up
        "jets": compose(stance, {"move": strike((0, 0.04, -0.04), (0, 0.16, 0), (0, 0.18, 0), (0, 0.04, 0)),
                                 "head": strike(X(-10), X(-16), X(-17), X(-4))}),
        # Wake Charge: rocks back, then surges head-down through the target
        "charge": compose(stance, {"move": strike((0, 0.25, -0.06), (0, -0.5, 0.02), (0, -0.56, 0), (0, -0.15, 0)),   # within the camera frame
                                   "body": strike(X(-3), X(6), X(6)),
                                   "head": strike(X(6), X(14), X(14), X(3))}),
    }


def pangolin(stance):
    return {
        # Scale Rake: the tail winds to one side and sweeps through, each joint later than the one before
        "rake": compose(stance, {"tail.0": strike(Z(-20), Z(25), Z(30), Z(8)),
                                 "tail.1": strike(Z(-18), Z(18), Z(32), Z(10)),
                                 "tail.2": strike(Z(-15), Z(10), Z(30), Z(12)),
                                 "body": strike(Z(6), Z(-8), Z(-9), Z(-2))}),
        # Scale Shot: the back arches to stand the scales up, then snaps and flings them (the scales are an overlay)
        "shot": compose(stance, {"move": strike((0, 0.02, 0), (0, 0.1, 0), (0, 0.11, 0), (0, 0.02, 0)),
                                 "body": strike(X(-8), X(4), X(5)),
                                 "head": strike(X(12), X(-6), X(-6))}),
        # Ball Roll: head tucked and tail curled over, then the tumble forward
        "roll": compose(stance, {"move": strike((0, 0.1, -0.05), (0, -0.5, 0.05), (0, -0.56, 0), (0, -0.15, 0)),
                                 "body": strike(X(8), X(18), X(20), X(4)),   # a curl, not a dive (40 stood it on its head)
                                 "head": strike(X(40), X(45), X(45), X(10)),
                                 "tail.0": strike(X(30 * RC), X(40 * RC), X(40 * RC), X(8)),
                                 "tail.1": strike(X(30 * RC), X(40 * RC), X(40 * RC), X(8)),
                                 "tail.2": strike(X(30 * RC), X(40 * RC), X(40 * RC), X(8))}, plant=False),
    }


def kangaroo(stance):
    return {
        # Impact Boxing Gloves: the near glove cocks back with a body twist, then the jab lands past the target
        "jab": compose(stance, {"move": strike((0, 0.05, 0), (0, -0.12, 0), (0, -0.14, 0)),
                                "upper_arm.R": strike(X(30), X(-40), X(-42), X(-10), hold=X(32)),   # -70 read as an uppercut
                                "forearm.R": strike(X(-50), X(30), X(30), X(-10)),
                                "upper_arm.L": strike(X(10), X(-10), X(-12)),
                                "body": strike(Z(8), Z(-10), Z(-11), Z(-2))}),
        # Pouch Flak Gun: leans back to open the hatch, fires, the recoil rocks it further back
        "flak": compose(stance, {"move": strike((0, 0.03, 0), (0, 0.08, 0), (0, 0.09, 0)),
                                 "body": strike(X(-12), X(-16), X(-17), X(-4)),
                                 "head": strike(X(6), X(8), X(8)),
                                 # p72 (2026-10-19): the stomach hatch swings up, the gun flips forward through it,
                                 # fires, starts back in on the recovery, then both close (bones only on kangaroo p72)
                                 "hatch": strike(X(-110), X(-110), X(-110), X(-110), hold=X(-110)),
                                 "cannon": strike(X(60), X(90), X(84), X(25), hold=X(90))}),   # stowed pointing up
        # Tail Spring: leans back onto the tail, then both feet kick forward past the target
        "kick": compose(stance, {"move": strike((0, 0.15, 0.05), (0, 0.05, 0.12), (0, 0.04, 0.12), (0, 0.04, 0.02)),
                                 "body": strike(X(-25), X(-30), X(-30), X(-6)),
                                 "thigh.L": strike(X(15), X(55), X(58), X(10)),   # positive swings the feet forward on this rig (negative tucked them under)
                                 "thigh.R": strike(X(15), X(55), X(58), X(10)),
                                 "shin.L": strike(X(20), X(40), X(40), X(5)),
                                 "shin.R": strike(X(20), X(40), X(40), X(5)),
                                 "tail.0": strike(X(-15), X(-18), X(-18))}, plant=False),
    }


def shoebill(stance):
    return {
        # Apex Decapitation (2026-10-19 pivot to the real bird: its hooked bill crushes and decapitates): the head rises,
        # the bill drives down past the target, then wrenches sideways (positive rx tips the bill down)
        "clamp": compose(stance, {"move": strike((0, 0.02, 0), (0, -0.1, -0.02), (0, -0.11, -0.02)),
                                  "body": strike(X(-3), X(6), X(6)),
                                  "head": strike(X(-14), (28.0, 0.0, 14.0), (30.0, 0.0, -16.0), X(6), hold=X(-16)),
                                  "jaw": strike(X(34), X(0), X(0), X(0), hold=X(36))}),   # p94: gapes on the wind-up, slams shut on the bite
        # Bill Clatter (the real bird slams its bill together and it sounds like machine-gun fire): the head snaps shut
        # and open on every sampled frame of the burst (the battle plan samples t .31 .42 .50 .58 .64), the body rocks
        "lance": compose(stance, {"move": [(0.0, (0, 0, 0)), (0.17, (0, 0.02, 0)), (0.31, (0, 0.04, 0)), (0.5, (0, 0.06, 0)),
                                           (0.64, (0, 0.07, 0)), (0.78, (0, 0.03, 0)), (1.0, (0, 0, 0))],
                                  "head": [(0.0, X(0)), (0.17, X(-6)), (0.31, X(-14)), (0.42, X(4)), (0.5, X(-14)),
                                           (0.58, X(4)), (0.64, X(-14)), (0.78, X(-4)), (1.0, X(0))],
                                  "body": [(0.0, X(0)), (0.31, X(-2)), (0.42, X(1)), (0.5, X(-2)), (0.58, X(1)),
                                           (0.64, X(-2)), (0.78, X(0)), (1.0, X(0))],
                                  # p94: the lower bill claps open and shut against the head's snaps (shoebill only)
                                  "jaw": [(0.0, X(0)), (0.17, X(10)), (0.31, X(30)), (0.42, X(0)), (0.5, X(30)),
                                          (0.58, X(0)), (0.64, X(30)), (0.78, X(6)), (1.0, X(0))]}),
        # Sentry Lunge (it stands motionless like a statue, then a lightning-fast ballistic lunge): dead still for the
        # first three sampled frames, a short draw back, then the whole body and bill shoot forward
        "buffet": compose(stance, {"move": [(0.0, (0, 0, 0)), (0.31, (0, 0, 0)), (0.42, (0, 0.06, 0.01)), (0.5, (0, -0.48, -0.04)),
                                            (0.64, (0, -0.52, -0.04)), (0.78, (0, -0.2, 0)), (1.0, (0, 0, 0))],
                                   "head": [(0.0, X(0)), (0.31, X(0)), (0.42, X(-12)), (0.5, X(30)), (0.64, X(32)),
                                            (0.78, X(8)), (1.0, X(0))],
                                   "body": [(0.0, X(0)), (0.31, X(0)), (0.42, X(-5)), (0.5, X(14)), (0.64, X(14)),
                                            (0.78, X(4)), (1.0, X(0))],
                                   # p94: the bill opens as it shoots forward and bites shut at contact
                                   "jaw": [(0.0, X(0)), (0.31, X(0)), (0.42, X(8)), (0.5, X(32)), (0.64, X(2)),
                                           (0.78, X(0)), (1.0, X(0))]}),
    }


SETS = {"wolf_m": wolf, "hippo_m": hippo, "pangolin_m": pangolin, "kangaroo_m": kangaroo, "shoebill_m": shoebill}


def clips(machine, stance):
    """{clip name: (frames, pose)} for the machine: b_idle, its three attacks, b_hit and b_death."""
    out = {"b_idle": (48, idle(stance)), "b_hit": (12, hit(stance)), "b_death": (36, death(stance))}   # b_: the rigs already key "idle", "hit", "death" for the field
    for name, pose in SETS[machine](stance).items():
        out[name] = (ATTACK_FRAMES, pose)
    return out


def bake(kit, rig, machine, stance):
    """Key every clip on the rig (the kit's clip() grounds each frame: the lowest point stays on the floor)."""
    for name, (frames, pose) in clips(machine, stance).items():
        kit.clip(rig, name, frames, pose)
    return list(clips(machine, stance))
