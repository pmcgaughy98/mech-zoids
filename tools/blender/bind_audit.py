"""Bone-binding audit for every factory machine (Claude, 2026-10-16, creature factory pass).

Each machine is built from named parts that a rule tags to a bone by name (quad_rig.bone_for, bird_rig.bone_for, the
gorilla's own), then joined into one skinned mesh. A rule that misreads a name binds a part to the wrong bone, and the
fault only shows when that bone moves: Codex found the shoebill's far-shoulder bolts riding the near arm and the
pangolin's tail scales riding the wrong tail segment (its roll forks the tail); the kangaroo's far-leg discs did the
same on 2026-10-15. This finds them all at once instead of one finish at a time.

Splits the skinned mesh into its pieces (connected islands), takes each piece's bone (the vertex group most of its
vertices weigh on) and flags:
- side: a piece on a left/right bone whose vertices lie mostly on the other side of the body (the near side is .R,
  x < 0; the far side .L, x > 0);
- chain: a piece on a bone of a chain (tail.*, upper_arm/forearm/hand, thigh/shin/foot on one side) that sits much
  nearer another bone of the same chain (by its centre's distance to each bone's segment, rest pose). Skipped for a
  folded limb (a bird's wing lies forearm-back-along-upper-arm, so its covert plates sit near all three bones and the
  nearest one says nothing about where they belong).

  blender -b docs/art/3d/<id>.blend -P tools/blender/bind_audit.py -- <out.json>
Prints a summary line per finding and BIND_AUDIT_DONE <count>.
"""
import json
import re
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line

SIDE_MARGIN = 0.04     # m: a piece this close to the middle has no side
SIDE_SHARE = 0.8       # share of its vertices on the wrong side
CHAIN_GAP = 0.12       # m: how much nearer the other bone must be
CHAINS = (("upper_arm", "forearm", "hand"), ("thigh", "shin", "foot"))
# Reviewed and right as built (2026-10-16): (blend name, bone, piece centre). The gorilla's fists are rams far longer than
# their hand bone, so a fist and its bolts and piston sit nearer the forearm or upper arm and still belong to the hand;
# the hippo's hind knee caps sit 12 cm above the knee on the shin (1 to 2 sprite pixels of drift at its leg angles).
KNOWN = [("ape_l_v2", "hand.%s" % s, (x * k, -1.081, z)) for s, k in (("R", -1), ("L", 1)) for x, z in ((1.24, 0.677), (1.24, 1.109))] +     [("ape_l_v2", "hand.%s" % s, (x * k, y, z)) for s, k in (("R", -1), ("L", 1)) for x, y, z in ((1.869, -0.971, 0.849), (1.926, -1.055, 0.805), (1.926, -1.037, 0.828))]   # v76 (2026-10-19): the fist wheel's light cap, on the hand, nearer the forearm line +     [("hippo_m", "shin.R", (-0.52, 0.676, 0.757)), ("hippo_m", "shin.L", (0.52, 0.476, 0.757))]


def seg_dist(p, a, b):
    t = intersect_point_line(p, a, b)[1]
    t = max(0.0, min(1.0, t))
    return (a.lerp(b, t) - p).length


def folded(segs):
    """A limb folded on itself at rest: two adjacent segments' midpoints much closer than a straight limb's would be."""
    for (a0, a1), (b0, b1) in zip(segs, segs[1:]):
        straight = ((a1 - a0).length + (b1 - b0).length) / 2
        if ((a0 + a1) / 2 - (b0 + b1) / 2).length < 0.5 * straight:
            return True
    return False


def chain_of(bone):
    m = re.match(r"tail\.(\d+)$", bone)
    if m:
        return "tail"
    for chain in CHAINS:
        for b in chain:
            if bone.startswith(b + "."):
                return chain, bone[-1]
    return None


def main():
    out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
    rig = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
    if rig is None:
        print("BIND_AUDIT_DONE 0 (no armature)")
        return
    bones = {b.name: (rig.matrix_world @ b.head_local, rig.matrix_world @ b.tail_local) for b in rig.data.bones}
    findings = []
    pieces = 0
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not any(m.type == "ARMATURE" for m in ob.modifiers):
            continue
        names = {g.index: g.name for g in ob.vertex_groups}
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.verts.ensure_lookup_table()
        seen = set()
        mw = ob.matrix_world
        for v0 in bm.verts:
            if v0.index in seen:
                continue
            island, stack = [], [v0]
            seen.add(v0.index)
            while stack:   # flood fill over edges: one original part (or a fused group of them)
                v = stack.pop()
                island.append(v.index)
                for e in v.link_edges:
                    w = e.other_vert(v)
                    if w.index not in seen:
                        seen.add(w.index)
                        stack.append(w)
            pieces += 1
            votes = {}
            pts = []
            for i in island:
                mv = ob.data.vertices[i]
                pts.append(mw @ mv.co)
                if mv.groups:
                    g = max(mv.groups, key=lambda x: x.weight)
                    votes[names.get(g.group, "?")] = votes.get(names.get(g.group, "?"), 0) + 1
            if not votes:
                continue
            bone = max(votes, key=votes.get)
            c = sum(pts, Vector()) / len(pts)
            rec = {"object": ob.name, "verts": len(island), "bone": bone, "center": [round(x, 3) for x in c]}
            if bone.endswith((".L", ".R")) and abs(c.x) > SIDE_MARGIN:
                wrong = sum(1 for p in pts if (p.x < -0.01 if bone.endswith(".L") else p.x > 0.01))
                if wrong >= SIDE_SHARE * len(pts):
                    rec["issue"] = "side"
                    rec["should"] = bone[:-1] + ("R" if bone.endswith(".L") else "L")
                    findings.append(rec)
                    continue
            ch = chain_of(bone)
            if ch is not None and bone in bones:
                if ch == "tail":
                    sibs = [b for b in bones if b.startswith("tail.")]
                else:
                    sibs = [b + "." + ch[1] for b in ch[0] if b + "." + ch[1] in bones]
                if ch != "tail" and folded([bones[b] for b in sibs]):
                    continue
                d = {b: seg_dist(c, *bones[b]) for b in sibs}
                near = min(d, key=d.get)
                if near != bone and d[bone] - d[near] > CHAIN_GAP:
                    rec["issue"] = "chain"
                    rec["should"] = near
                    rec["dist"] = {bone: round(d[bone], 3), near: round(d[near], 3)}
                    findings.append(rec)
        bm.free()
    name = bpy.path.basename(bpy.data.filepath).rsplit(".", 1)[0]
    known = [f for f in findings if any(n == name and b == f["bone"] and all(abs(p - q) < 0.02 for p, q in zip(c, f["center"])) for n, b, c in KNOWN)]
    findings = [f for f in findings if f not in known]
    for f in findings:
        print("BIND %s %s: %s -> %s (%d verts at %s)" % (f["issue"], f["object"], f["bone"], f["should"], f["verts"], f["center"]))
    if out:
        with open(out, "w") as fh:
            json.dump({"pieces": pieces, "findings": findings}, fh, indent=1)
    print("BIND_AUDIT_DONE %d of %d pieces (%d reviewed and right, in KNOWN)" % (len(findings), pieces, len(known)))


main()
