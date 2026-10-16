# The detail pass for every machine (Claude, 2026-10-14). Preston: "add parts and pieces so that the image codex
# generates give you an awesome reference ... you don't have to make it look too pretty. Do that for all." Zoids Legacy
# sprites are dense with small mechanism (docs/reference/sprite-rules-legacy-2026-10-14-gap.md, point 5); our parts were
# bare boxes. A build calls run() after its parts and weapons exist and before it tags parts to bones.
#
# On every large part: a raised panel (or a vent) on each outward side face with bolts at its corners, a layer plate on
# top, and on long limb parts a piston riding alongside. Each new piece is renamed "<host>_9NN" (digits only, so every
# rig's side rule still reads it) and kept only if the build's bone rule puts it on the host's bone; anything else is
# removed, so nothing ever floats off a moving limb. MECH_GREEBLES=0 builds without it.
import bpy, os
import numpy as np
from mathutils import Vector

SKIP = ("claw", "eye", "glow", "lens", "lamp", "tooth", "fang", "tusk", "rivet", "seam", "stripe", "spine", "cable",
        "pst", "_rod", "_sleeve", "slat", "bead", "nail", "toe", "finger", "ear", "_9", "barrel", "muzzle", "nostril")


def _shape(o):
    """World-space centre, principal axes (longest first), extents along them, and the world box."""
    M = o.matrix_world
    pts = np.array([tuple(M @ v.co) for v in o.data.vertices])
    c = pts.mean(0)
    w, V = np.linalg.eigh(np.cov((pts - c).T))
    V = V[:, w.argsort()[::-1]]
    proj = (pts - c) @ V
    return Vector(c), [Vector(V[:, i]) for i in range(3)], proj.max(0) - proj.min(0), pts.min(0), pts.max(0)


def run(kit, weapons, bone_for=None, min_long=0.3, min_mid=0.16, skip_prefix=()):
    """skip_prefix: part names a build keeps bare (the pangolin's scales already are its detail)."""
    if os.environ.get("MECH_GREEBLES") == "0":
        return 0
    scene = bpy.context.scene
    inv = {m.name: k for k, m in kit.MATS.items()}
    has = lambda k: k in kit.MATS
    hosts = sorted((o for o in scene.objects if o.type == "MESH" and len(o.data.vertices) >= 8
                    and not any(s in o.name for s in SKIP) and not o.name.startswith(tuple(skip_prefix))), key=lambda o: o.name)
    kept = dropped = 0
    for hi, o in enumerate(hosts):
        key = inv.get(o.data.materials[0].name) if o.data.materials else None
        if key is None:
            continue
        c, axes, ext, lo, up = _shape(o)
        if ext[0] < min_long or ext[1] < min_mid:
            continue
        dx, dy, dz = up - lo
        bone = bone_for(o.name) if bone_for else None
        bolt = key   # bolts in the part's own colour: bumps the light catches (dark ones read as noise on the hippo, p25)
        count = [0]

        def adopt(fn):
            """Run one builder; rename what it made after the host and keep it only on the host's bone."""
            nonlocal kept, dropped
            before = set(scene.objects.keys())
            fn()
            for ob in [x for x in scene.objects if x.name not in before]:
                ob.name = "%s_9%02d" % (o.name, count[0])
                count[0] += 1
                if bone_for and bone_for(ob.name) != bone:
                    bpy.data.objects.remove(ob, do_unlink=True)
                    dropped += 1
                else:
                    kept += 1

        long_part = ext[0] > 2.2 * ext[1]
        sides = [s for s in (-1, 1) if c.x * s > -0.03]   # outward faces only (a mirrored part's inner face hides)
        for s in sides:
            out = Vector((s, 0, 0))
            w, h = (0.4 * dy, 0.55 * dz) if not long_part else (0.5 * dy, 0.4 * dz)
            if w < 0.08 or h < 0.07 or dx < 0.06:
                continue
            if hi % 3 == 2 and not long_part and has("frame_dark"):   # a vent: dark plate, light slats
                adopt(lambda: kit.plate_on(o, "g", "frame_dark", c, out, w, h, 0.02, standoff=0.012, bevel=0.005))
                for i in range(3):
                    adopt(lambda i=i: kit.plate_on(o, "g", "trim" if has("trim") else bolt, c + Vector((0, 0, (i - 1) * h / 3.3)),
                                                   out, w * 0.8, h / 7.5, 0.02, standoff=0.03, bevel=0.004))
            else:   # a raised panel, framed every other time, bolted at the corners
                adopt(lambda: kit.plate_on(o, "g", key, c, out, w, h, 0.03, standoff=0.014, bevel=0.008,
                                           recess=0.01 if hi % 2 else 0.0, rim=0.025))
                for by, bz in ((-0.38, -0.36), (0.38, 0.36)):
                    aim = c + Vector((0, by * w, bz * h))
                    hit = kit.surface_hit(o, aim + out * 3.0, -out)
                    if hit:   # only where the bolt lands on the part (misses floated beside the shoebill's feet, p68)
                        p = hit[0] + hit[1] * 0.04
                        adopt(lambda p=p: kit.shell("g", bolt, p, (0.05, 0.05, 0.05), (0, 0, 0), 0.5, levels=0))
        if dz > 0.18 and dx > 0.16 and dy > 0.16 and not long_part:   # a layer plate on top, an accent one in four
            adopt(lambda: kit.plate_on(o, "g", "accent" if hi % 4 == 1 and has("accent") else key, Vector((c.x, c.y, up[2])),
                                       (0, 0, 1), 0.55 * dx, 0.55 * dy, 0.03, standoff=0.012, bevel=0.008))
        if long_part and abs(c.x) > 0.05 and abs(axes[0].x) < 0.5:   # a piston alongside a limb, on its outer side; not on
            # a part running left to right (the gorilla's fists stuck rods out sideways at the floor, v67)
            s = 1 if c.x > 0 else -1
            off = Vector((s * (dx / 2 + 0.05), 0, 0))
            a, b = c - axes[0] * 0.32 * ext[0] + off, c + axes[0] * 0.32 * ext[0] + off
            adopt(lambda: weapons.piston(kit, "g", a, b, 0.035))
    print("GREEBLES kept %d, dropped %d (off the host's bone)" % (kept, dropped))
    return kept
