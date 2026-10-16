# Shared weapon and detail parts for the creature factory (Claude, 2026-10-13; Preston: "weaponize it up ... add
# weapons parts etc. wired up for later refinement"). Foundation pieces, not final art: each builder makes a weapon
# from the gorilla kit's primitives (build_ape_l_v2.py) and returns its muzzle points.
#
# A machine build lists its loadout and calls build_loadout() after its body, head and legs exist and before it
# tags parts for the rig:
#   LOADOUT = [{"slot": "fang", "move": "Fang Lunge", "kind": "blade", "prefix": "head_", "suffix": "",
#               "args": {...}}, ...]
#   weapons.build_loadout(kit, "wolf_m", LOADOUT)
# - Part names are <prefix>wpn_<slot>_<part><suffix>. The prefix and suffix pick the bone through the machine's own
#   tagger: "head_" rides the head, "front_shin_" with suffix "_1" rides the left forearm on the quadruped rig, no
#   prefix rides the body.
# - "move" names the roster weapon (scripts/data/machines.gd) the hardware serves. None marks a spare hardpoint:
#   DRAFT hardware with no move yet, Preston's to name.
# - Positions can come from anchor(name, (fx, fy, fz)): a point on an existing part's bounding box (0 to 1 on each
#   axis; y 0 is the front, -Y, z 1 is the top), so a loadout survives the part moving.
# - Writes docs/art/3d/<id>_weapons.json: each weapon's parts, kind, move and muzzle points at rest, for battle
#   effects and for the refinement pass.
# - MECH_WEAPONS=0 builds the machine bare (to score against references drawn without the weapons).
import bpy, json, math, os
from mathutils import Euler, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def enabled():
    return os.environ.get("MECH_WEAPONS", "1") != "0"


def _v(p):
    return Vector(p) if not isinstance(p, Vector) else p.copy()


def bbox(name):
    bpy.context.view_layer.update()
    o = bpy.data.objects[name]
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def anchor(name, f, off=(0, 0, 0)):
    lo, hi = bbox(name)
    return Vector((lo.x + (hi.x - lo.x) * f[0], lo.y + (hi.y - lo.y) * f[1], lo.z + (hi.z - lo.z) * f[2])) + Vector(off)


def on(k, name, f, outward=(0, 0, 1), standoff=0.02):
    """anchor(), then onto the part's real surface along outward (the kit's ray test), standoff off it."""
    return k.on_surface(bpy.data.objects[name], anchor(name, f), outward, standoff)


def _axes(d):
    d = d.normalized()
    side = d.cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
    up = side.cross(d).normalized()
    return d, side, up


def _glow(k):
    return "eye_src" if "eye_src" in k.MATS else "light"


# ---- weapon builders: each takes the kit, a name stem (parts become stem + "_" + part + suffix) and returns muzzles

def cannon(k, nm, sfx, base, direction, length=0.9, r=0.06, barrels=1, gap=None, housing=None, mat="frame",
           barrel_mat="frame_dark", tip_mat="accent", post=None):
    """A housing block with one or more parallel barrels and a muzzle collar on each. post: a point on the body the
    mount stands on; a pylon joins them (2026-10-13: the shoebill's head gun floated in the side view)."""
    base = _v(base)
    if post is not None:
        k.segment(nm + "_post" + sfx, "frame_dark", _v(post), base, 0.07, 0.1, 0.5)
    d, side, up = _axes(_v(direction))
    hs = housing or (r * 2.6 * barrels + 0.08, r * 6, r * 3.6)
    k.shell(nm + "_mount" + sfx, mat, base, hs, (math.degrees(-math.asin(max(-1, min(1, d.z)))), 0, 0), 0.6, levels=1)
    out = []
    for i in range(barrels):
        off = side * (i - (barrels - 1) / 2) * (gap or r * 2.6)
        a = base + off + d * hs[1] * 0.3
        b = a + d * length
        k.cyl(nm + "_barrel%d" % i + sfx, barrel_mat, a, b, r, 10)
        mz = k.cyl(nm + "_muzzle%d" % i + sfx, tip_mat, b - d * r * 1.8, b + d * r * 0.3, r * 1.4, 12)
        if getattr(k, "ROUND_JOINTS", False):   # gorilla model pass 1
            k.round_rim(mz, r * 0.4)
        out.append(b + d * r * 0.3)
    return out


def missile_pod(k, nm, sfx, center, size=(0.36, 0.4, 0.3), rows=2, cols=2, rot=(0, 0, 0), mat="frame", cap="accent"):
    """A box launcher; its tube mouths on the local front face (-Y), the whole pod turned by rot (degrees)."""
    c = _v(center)
    R = Euler(tuple(math.radians(a) for a in rot)).to_matrix()
    k.shell(nm + "_box" + sfx, mat, c, size, rot, 0.6, levels=1)
    d = (R @ Vector((0, -1, 0))).normalized()
    u, v = R @ Vector((1, 0, 0)), R @ Vector((0, 0, 1))
    face = c + d * size[1] / 2
    cw, ch = size[0] / cols, size[2] / rows
    rad = min(cw, ch) * 0.3
    out = []
    for i in range(rows):
        for j in range(cols):
            p = face + u * (j - (cols - 1) / 2) * cw + v * (i - (rows - 1) / 2) * ch
            k.cyl(nm + "_rim%d%d" % (i, j) + sfx, cap, p - d * 0.02, p + d * 0.035, rad * 1.3, 8)
            k.cyl(nm + "_tube%d%d" % (i, j) + sfx, "frame_dark", p - d * 0.01, p + d * 0.045, rad, 8)
            out.append(p + d * 0.045)
    return out


def gatling(k, nm, sfx, base, direction, length=0.7, n=6, r=0.03, ring=0.08, mat="frame", tip_mat="accent"):
    """A rotary cannon: a drum, a ring of barrels and a front collar."""
    base = _v(base)
    d, side, up = _axes(_v(direction))
    drum = k.cyl(nm + "_drum" + sfx, mat, base - d * 0.06, base + d * length * 0.32, ring * 1.6, 12)
    if getattr(k, "ROUND_JOINTS", False):   # gorilla model pass 1 (2026-10-16): a rounded front rim reads as a drum
        k.round_rim(drum, ring * 0.35)
    for i in range(n):
        t = 2 * math.pi * i / n
        off = (side * math.cos(t) + up * math.sin(t)) * ring
        k.cyl(nm + "_barrel%d" % i + sfx, "frame_dark", base + off + d * length * 0.3, base + off + d * length, r, 6)
    k.cyl(nm + "_collar" + sfx, tip_mat, base + d * length * 0.82, base + d * length * 0.9, ring + r * 1.8, 12)
    return [base + d * length]


def emitter(k, nm, sfx, center, direction, r=0.09, mat="frame", rim="accent"):
    """A beam or sonic emitter: a housing, a coloured rim and a glowing lens facing direction."""
    c = _v(center)
    d = _v(direction).normalized()
    k.cyl(nm + "_housing" + sfx, mat, c - d * r * 0.9, c + d * r * 0.25, r * 1.35, 12)
    k.cyl(nm + "_rim" + sfx, rim, c + d * r * 0.15, c + d * r * 0.35, r * 1.15, 12)
    k.cyl(nm + "_lens" + sfx, _glow(k), c + d * r * 0.3, c + d * r * 0.45, r * 0.85, 12)
    return [c + d * r * 0.45]


def blade(k, nm, sfx, center, w=0.12, h=0.5, rot=(0, 0, 0), mat="accent"):
    """A tapered blade or fin, edge out."""
    k.plate(nm + "_blade" + sfx, mat, _v(center), w, h, 0.035, rot, bend=0.05, taper=0.15, bevel=0.006)
    return [_v(center)]


def jet(k, nm, sfx, a, b, r=0.08, mat="frame", tip_mat="accent"):
    """A thruster: body a->b, a ringed nozzle flaring at b."""
    a, b = _v(a), _v(b)
    d = (b - a).normalized()
    k.cyl(nm + "_body" + sfx, mat, a, b, r, 10)
    k.cyl(nm + "_ring" + sfx, tip_mat, b - d * r * 0.4, b + d * r * 0.1, r * 1.2, 10)
    k.cyl(nm + "_nozzle" + sfx, "frame_dark", b, b + d * r * 0.7, r * 1.05, 10)
    return [b + d * r * 0.7]


def spikes(k, nm, sfx, points, length=0.18, r=0.04, direction=(0, 0, 1), mat="accent"):
    """A row of short spikes (rams, knuckle studs, bill teeth)."""
    d = _v(direction).normalized()
    out = []
    for i, p in enumerate(points):
        p = _v(p)
        k.segment(nm + "_spike%d" % i + sfx, mat, p, p + d * length, r, r * 0.6, 0.5)
        out.append(p + d * length)
    return out


KINDS = {"cannon": cannon, "missile_pod": missile_pod, "gatling": gatling, "emitter": emitter, "blade": blade,
         "jet": jet, "spikes": spikes}


# ---- detail builders: the "more pieces" layer (hydraulics, vents, antennas); names are the caller's

def piston(k, nm, a, b, r=0.04, sfx=""):
    a, b = _v(a), _v(b)
    k.cyl(nm + "_sleeve" + sfx, "frame_dark", a, a.lerp(b, 0.55), r, 8)
    k.cyl(nm + "_rod" + sfx, "light", a.lerp(b, 0.45), b, r * 0.55, 8)


def vent(k, nm, center, w, h, rot=(0, 0, 0), slats=3, mat="frame_dark", slat_mat="trim"):
    c = _v(center)
    R = Euler(tuple(math.radians(a) for a in rot)).to_matrix()
    k.plate(nm, mat, c, w, h, 0.03, rot, bend=0.0, bevel=0.006)
    for i in range(slats):
        p = c + R @ Vector((0, (i - (slats - 1) / 2) * h / (slats + 0.5), 0.02))
        k.plate(nm + "_slat%d" % i, slat_mat, p, w * 0.82, h / (slats * 2.6), 0.02, rot, bend=0.0, bevel=0.004)


def antenna(k, nm, base, tip, r=0.018, tip_mat="accent"):
    base, tip = _v(base), _v(tip)
    k.cyl(nm, "frame_dark", base, tip, r, 6)
    k.shell(nm + "_bead", tip_mat, tip, (r * 3, r * 3, r * 3), (0, 0, 0), 0.5, levels=0)


def cable(k, nm, pts, r=0.025, mat="frame_dark"):
    pts = [_v(p) for p in pts]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        k.cyl(nm + "_%d" % i, mat, a, b, r, 6)


# ---- the loadout

def build_loadout(k, machine, loadout, out_json=None):
    """Build every weapon in the loadout and write the manifest. Returns the manifest (empty when MECH_WEAPONS=0)."""
    if not enabled():
        print("WEAPONS off (MECH_WEAPONS=0): %s built bare" % machine)
        return []
    manifest = []
    for w in loadout:
        before = set(o.name for o in bpy.data.objects)
        stem = "%swpn_%s" % (w.get("prefix", ""), w["slot"])
        muzzles = KINDS[w["kind"]](k, stem, w.get("suffix", ""), **w.get("args", {}))
        parts = sorted(set(o.name for o in bpy.data.objects) - before)
        manifest.append({"slot": w["slot"], "move": w.get("move"), "draft": w.get("move") is None, "kind": w["kind"],
                         "note": w.get("note", ""), "parts": parts,
                         "muzzles": [[round(c, 3) for c in m] for m in muzzles]})
    path = out_json or os.path.join(ROOT, "docs", "art", "3d", "%s_weapons.json" % machine)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"machine": machine, "weapons": manifest}, f, indent=1)
    print("WEAPONS %s: %d weapons, %d parts -> %s" % (machine, len(manifest), sum(len(m["parts"]) for m in manifest), path))
    return manifest
