# Mech skill-up handoff for the mech Claude session (written in the Hollowtide session, 2026-10-12)

Preston did the mech skill-ups in the Hollowtide Claude session on 2026-10-11 and 2026-10-12. This file hands over
what was learned, the method, the tools, the measured targets and the open work, so the mech session continues
without re-learning any of it. The pass-by-pass log is `docs/plan/3d-pivot-2026-10-11.md` (passes 4 to 24); read
its last five entries after this file.

## Synthesis, as Preston defines it
Use everything on hand: MCPs, connectors, installed skills and the reference files he sent. Take stock of the tools
first, measure the references, then build, look, score and repeat. Report what each tool contributed. Study the
references by taking them apart and replicating pieces; never copy their art, colours or layouts into the game.
Reference files stay outside the project. The shape target is Preston's sprite
(`docs/art/ape-rd-2026-10-11/source_preston_pick.webp`); the finish target is Fall of Cybertron; Zoids are the core.
Construction first, animation waits (Preston, 2026-10-12): every part rides one bone by name, so building never
breaks the five clips, and each build re-checks them.

## State of the gorilla at handoff
- `tools/blender/build_ape_l_v2.py` builds everything: parts, texture bake, rig, five clips, export, renders.
  Run: `"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_ape_l_v2.py`
  (about six minutes; the last line prints dims and triangles).
- Pass 24 (feet, final): 17,502 triangles, 70% crisp edges, outline 0.734, paint 66 / 25 / 9, lab passes. The toes
  stand in front of a lowered foot lip (`docs/art/3d/ape_l_foot_v24.png`). Orange is 9% against the sprite's 18%
  because the new heel pad is dark where the old orange heel blocks showed from the rear: first fix for the mech
  session is an orange heel or toe-top plate.
- Backups of the build script per pass sit in the Hollowtide session scratchpad only; the repo file is current.
- Verification after every build, in this order: `tools/blender/probe_hard_edges.py` (crisp edges),
  `tools/blender/score_ape_vs_sprite.py` (outline and paint split), Godot `--headless --import`, then
  `HT_FINISH=metal godot --path . --script res://tools/debug/model_lab_check.gd` (windowed: saves four stills to
  `docs/art/3d/model_lab_000.png` and so on). Compose the stills into `ape_l_lab_metal_vNN.png`.

## The build toolkit (functions in build_ape_l_v2.py)
- `profile_solid(name, mat, center, side_yz, front_xz, chamfer, top_xy)`: one sculpted mass from two or three
  outlines (exact boolean intersect of extruded profiles, then an angle-limited chamfer). The single biggest
  shape lesson: boxes with planks read as "shapes put together"; one profile solid reads as one sculpted piece.
- `limb_solid(name, mat, a, b, outward, depth, width, chamfer, grooves)`: a profile solid built along a limb from
  thickness and width profiles, with optional panel lines cut in local space, then turned into place.
- `groove(ob, a, b, normal, w, d, mat)`: a dark panel line cut into any solid (boolean difference keeping the
  cutter's material), applied before the chamfer so the seam edges get chamfered too. Works on the planar strips
  of a profile solid; a straight groove cannot follow a curved strip.
- `plate(..., bend, taper, recess, rim)`: a thin armour sheet with real thickness and one crisp bevel; `recess`
  makes a framed panel (centre sunk inside a raised rim). `plate_along` places one along a limb.
- `drum` (barrel pod), `glow_ring` (segmented ring in a trench), `light_housing` (round light in a dark ring),
  `inlay` (glow strip), `disc` (grey joint disc with orange ring and glow), `segment` (tapered chamfered box
  between two joints: fingers, toes), `fuse` (boolean union with fillet; unused since pass 24), `mirror_x`.
- `sharpen(ob)`: marks sharp edges in the mesh (40 degrees) and applies a Weighted Normal modifier (face area,
  weight 50, keep sharp). Required: the export keeps modifiers off so the rig stays live, so auto-smooth as a
  modifier never reached the game file. Found on 2026-10-12: 10,881 hard edges, none crisp. Now 70%.
- `bake_atlas(ob, 2048)`: smart-project plus concave pack onto an "atlas" UV layer; bakes colour, AO (128 samples),
  a high-to-low normal map (bevelled copy, selected-to-active, cage 0.03, ray 0.08), per-material roughness and
  metal through emission, and pointiness for edge wear; box-blurs the AO and curvature; writes
  `art/machines/ape_l/ape_l_atlas.png`, `_normal.png`, `_orm.png`. The glow parts get a fresh `ape_eye` emissive
  material after the bake (the bake rewires materials; the eyes once exported grey).
- Rig: `BONE_OF` maps part-name prefixes to bones; `bone_for()` strips `_hub/_ring/_glow/_housing/_lamp` and
  `HEAD_PARTS` go to the head. New part names need a `BONE_OF` entry or they ride the body. `clip()` measures the
  posed mesh every frame and lifts the body so the lowest point sits exactly on the floor (mute the NLA tracks and
  settle at rest before measuring, or the first frame reads the previous clip).
- Export: glTF with `export_apply=False`, skins, `NLA_TRACKS` so every clip exports under its own name.

## Measurement tools
In `tools/blender/`: `probe_hard_edges.py -- <glb|fbx>` (split-shaded share of hard edges), `disassemble_model.py
-- <file> <mesh prefix>` (pieces, edge mix, chamfer width, texel density; assumes a 1024 sheet), `score_ape_vs_sprite.py`
(outline overlap and paint split against the sprite's rear three-quarter view). Copied from scratch into
`tools/blender/study/`: `normal_detail.py` (normal-map detail at 1024/512/256 px), `list_parts.py` (how a model is
split into parts), `render_region.py` (close-ups of a region from three directions), `render_ends.py` and
`render_head.py` (ends of a machine; head crops guess the head position and often miss). Godot:
`tools/debug/model_lab_check.gd`, `tools/debug/room_check.gd`.

## Measured targets (from the real game files; trust these over any report)
- Fall of Cybertron: beast modes 6,800-14,000 triangles, robots 15,000-17,000. Colour maps muted and worn,
  saturation about 0.50, value about 0.44, flat clean blocks. Glow about 0.5% of surface. Grimlock's median chamfer
  edge 0.057 m at our scale. Texel density 171-502 px/m, reached by reusing the sheet about ten times (mirrored and
  repeated parts share texture space); ours is about 130 px/m with coverage 0.44 of a 2048 sheet.
- Hard edges shade crisp (split normals) on 77% (Grimlock), 83% (Megatron), 69-93% (Horizon files) of edges.
- Normal-map detail (mean gradient of red and green, x10, at 1024/512/256 px): Megatron 0.42/0.51/0.53,
  Combaticon chest 0.68/1.16/1.43, legs 0.56/0.92/1.06; ours after pass 23: 0.88/1.14/1.23. Finished maps hold or
  gain as the scale drops because their features are big. The old 0.176/0.100 numbers used another formula; retired.
- The Horizon Zero Dawn files Preston added are Sketchfab fan recreations (72k to 1.9M triangles, nearly all smooth
  edges): shape and part breakdown only, not budgets. Sawtooth, Thunderjaw, Watcher, Deathbringer, Tallneck and
  Corruptor are glTF; the Scorcher is FBX; the Behemoth is a .blend.

## Lessons, in the order they mattered
1. Hard edges must live in the mesh (see `sharpen`). Verify with the probe after every export.
2. One sculpted mass beats stacked boxes (profile solids for head, torso, limbs, snout, feet).
3. Armour is thin plates with thickness layered over a dark frame, with gaps where the frame shows.
4. Framed panels, inlays and light housings read as finished hard surface (replicated from Grimlock's chest).
5. Panel lines as cut grooves raised the panel-scale detail number from 0.98 to 1.23 in one pass.
6. Exposed machinery between plates: pistons half-sunk into the armour (offset along the surface profile; too far
   out they float, too far in only stubs show). Forearm cylinders took three builds to seat.
7. Fingers and toes as tapered segments with knuckle caps (Grimlock's hand: 522 triangles, many small pieces).
8. The head is a mechanical skull: dark core, cranium shell with grooves, brow bar, lens eyes in sockets, a
   sculpted snout with nostrils cut in, a separate hinged jaw with hinge discs and pistons, cheek plates, ear ports.
9. Texture: packing by outline changed coverage 0.43 to 0.44 only; thousands of tiny islands carry the margins.
   The real win is sharing UV space between the two halves and between repeated parts (next pass).
10. Look at close-ups of every change (`render_region.py`); the lab sheets hide small mistakes.

## Pitfalls hit (so they are not hit again)
- The Bash tool breaks on heredocs containing triple quotes: write patch scripts with the file tool, run them
  with a short command. Patches use `rep(old, new)` with asserts, on the current file text.
- GDScript has no `(a, b)` lists; use `[a, b]`. The room check caught it.
- Blender study collections left in a live Blender, and stray Godot processes from checks, exhausted the machine;
  stop them (`Get-Process Godot*`, Blender orphans).
- `docs/art/3d/ape_l_views/turnaround.png` and `face_pair.png` are stale (the build does not rewrite them);
  `face.png`, `face_side.png`, the eight view PNGs and the lab stills are current.
- The Blender MCP server (`blender`, ahujasid mcp-for-blender) gives live camera looks when it connects; it timed
  out on 2026-10-12, so headless renders were used. Reconnect it next session.
- The clips video (`HT_RECORD=clips`) records a frozen frame; the clips play fine. Unresolved.
- Gemini Deep Research reports cite the prompt as a source and get numbers wrong; use them as checklists only.

## Codex and the rooms
- Codex builds rooms with its Build 3D Game Rooms plugin. Its sheet is `docs/team/CODEX_TASKS_3D_ROOMS.md` (updated
  2026-10-12 with the measured targets, the palette and the room contract). The hangar is at its Form gate.
- Wiring: `scenes/room_stage_3d.tscn` loads any room from `art/rooms/<id>/<id>.glb`, stands the gorilla at the
  origin on its idle, applies the metal finish and lights; `tools/debug/room_check.gd` is the Runtime gate
  (`HT_ROOM=<id> godot --path . --script res://tools/debug/room_check.gd`, must print PASS). A stand-in room
  (`tools/blender/make_test_room.py`, `art/rooms/test_box`) passes. Codex has since extended both files with a
  per-room `<id>.runtime.json` (fixtures, camera) and a runtime evidence report; keep its changes.

## Open work, ranked
1. Check the pass 24b result (toes, orange share) and log pass 24 in the plan doc if not done.
2. Texture sharing: mirror the two halves and share islands between repeated parts, then re-measure texel density
   (target: Grimlock's 171-502 px/m band).
3. Knuckle shock pads and tracked pistons (Damped Track bones) once construction settles; more clips later.
4. Keep the big body plates in mind for grooves (the torso is mostly covered by plates; grooves need planar strips).
5. Reconnect the Blender MCP server; fix the clips video; the crown plate still sits a touch proud.
