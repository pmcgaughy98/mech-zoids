# Codex: 3D rooms with your Build 3D Game Rooms plugin (from Claude, 2026-10-11)

Preston: "codex has a build 3D game rooms with blender plugin ... give him his tasks." The machines are now 3D, so
the places they stand in are 3D rooms, and that is what your plugin does. You lead rooms and environments; Claude
leads the machines (models, rigs, animation) and the Godot model lab. Read this file, then `docs/plan/3d-pivot-2026-10-11.md`
(the bottom sections), then start Task R1.

## Update 2026-10-12 (from Claude): where things stand, and the wiring
- **Your hangar is at the Form gate,** waiting for Preston's approval. Ask him for it in chat; "next" counts, as it
  did for Function.
- **The Runtime gate is wired for you.** You export one file and run one command:
  1. Export the room to `art/rooms/hangar_bay/hangar_bay.glb`, following the contract below.
  2. Run `HT_ROOM=hangar_bay "C:/Users/pmcga/Games/Tools/Godot_v4.7.2/Godot_v4.7.2-stable_win64.exe" --path . --script res://tools/debug/room_check.gd`
  3. It must print `room_check: PASS`. It also saves `docs/art/3d/room_hangar_bay.png`, the still to show Preston.
  Behind it, `scenes/room_stage_3d.tscn` (`scripts/scenes/room_stage_3d.gd`) loads any room from
  `art/rooms/<id>/<id>.glb`, stands the gorilla at the origin playing its idle, gives room and machine the same
  metal finish and calibrated lights, and looks in from the game camera. A stand-in room (`art/rooms/test_box`,
  built by `tools/blender/make_test_room.py`) passes the check today, so you have a known-good file to compare with.
- **The room contract** (what the check tests):
  - metres; the machine's stand point is the origin; a mesh named `floor*` has its top face at y = 0
  - the machine faces +Z in Godot (Blender -Y), so the bay door faces +Z and the camera looks in from +Z, high
  - plain materials with base colours, or a baked colour atlas plus normal and ORM maps; the finish is applied by
    the stage, so do not shade in Blender
  - under 40,000 triangles; meshes only (no lights or cameras needed in the file)
- **The look changed since this file was first written:** the default finish is the metal one (`metal_finish()`:
  worn painted metal, sky reflections, a warm key and a cool rim light, glow, contact shadow, a thin ink line),
  not cel. Cel still exists behind `HT_FINISH=cel`. Rooms get whichever the stage applies.
- **The gorilla today:** about 17,000 triangles, 2.78 m tall, 3.14 m across the fists, 3.04 m long, five clips (walk,
  idle, punch, hit, death), a 2048 px texture set (colour, normal, ORM).
- **What the synthesis measured, so you can aim at the same targets without the study files** (those stay in
  Claude's scratch folder and never enter the project):
  - Finished Cybertron colour maps are muted and worn: saturation about 0.50, value about 0.44. Flat clean
    blocks, no speckle.
  - Surface-detail (normal map) strength 0.176 on their maps; ours is 0.10. Seams, rivets and vents are real grooves.
  - Glowing surface is about 0.5% of the total. Lights are small and few.
  - Chamfers: the median chamfer edge is 0.057 m on Grimlock at our scale; one crisp bevel per edge, no soft rounding.
  - Hard edges shade crisp (split normals) on 70-93% of edges in finished files. Ours shipped at 0% until today,
    now 69%. Tool: `tools/blender/probe_hard_edges.py -- <file.glb>`. Run it on your export; aim above 60%.
  - Texture density: Grimlock reaches 171-502 px/m by letting mirrored and repeated parts share texture space
    (his sheet is used ten times over). Share atlas space between repeated props.
  - Budgets: Cybertron beast modes 6,800-14,000 triangles, robots 15,000-17,000. The Horizon files Preston added
    are fan recreations (205k to 1.9M triangles): good for shape and part breakdown, not for budgets.
  - `tools/blender/disassemble_model.py -- <file> <mesh prefix>` reports pieces, edge mix, chamfer width and texel
    density for any export; use it on your room props.
- **Palette (the build script is the source of truth):** green 5c804a, dark green 3e5a33, orange d98a40, grey
  8a8d92, dark grey 45474c, face grey 4a4b50, teal 1fb8c4. Rooms avoid the greens as main colours.

## What you need to know about the machines
- **The gorilla:** `art/machines/ape_l/ape_l.glb`, built by `tools/blender/build_ape_l_v2.py`.
  - **Size:** 2.78 m tall, 3.14 m across the fists, 3.04 m long. In Blender it faces -Y (Godot +Z).
  - **Animation:** walk, idle, punch, hit and death.
- **The look:** the metal finish (`metal_finish()` in `scripts/scenes/model_lab_3d.gd`), applied by the room stage
  to the room and the machine alike. See the 2026-10-12 update above for the measured targets.
  - **Render size:** the game draws at 320x180 and scales up by whole numbers, so 3D comes out chunky, like pixel art.
- **The machine's colours:** the palette in the update above.
  - **Rooms must not use the machine's green as a main colour,** so the machine pops.
  - **Use for rooms:** gunmetal and concrete greys, warm work lights, orange hazard trim and teal screen glow.
- **What finished mechs taught us (measured):** the numbers in the update above. For rooms: chunky, readable shapes,
  few materials, clean flat blocks of colour, one crisp chamfer per edge.

## Ground rules
- **Use your plugin's gates as written:** Function, then Form, then Runtime, with Preston's explicit approval at each.
- **No paid Meshy generation unless Preston approves that specific spend.** Prefer props built procedurally in Blender. They suit the chunky style and cost nothing.
- **Synthesis:** study how finished human-made games build hangars and machine bays, then make our own. Never copy Zoids or any other game's art, layouts or colours. Reference models Preston sent stay in a scratchpad and never go into the project.
- **Files:**
  - Room sources: `art/rooms/<room_id>/`, holding the `.blend`, the plugin's evidence package and the exported `.glb`.
  - Godot scene: `scenes/rooms/<room_id>.tscn`.
  - Leave `scenes/base.tscn` (the 2D base) alone until Preston decides how the 3D room plugs in.
- **Your Blender:** do not edit Claude's build scripts in `tools/blender/build_ape_l*.py`. Preston's open Blender may have Claude's working collections in it (`ape_l_v2`, `STUDY_ONLY_not_for_game`); leave them be.

## Textures: paint them in code, the Hollowtide way (Preston asked, 2026-10-11)
Preston wants the rooms textured the way Hollowtide's interiors were: painted in code, pixel by pixel, no
generated art. You already worked inside that system there (your hall fixtures sit on the painted room footprints).
- **Read these for the method (structure, not to copy) in `C:/Users/pmcga/dev/hollowtide`:**
  - `scripts/town/room_painter.gd`: every piece is a block of its own colours with a lit top-left, a shaded bottom-right and a dark ink outline, plus cast shadows and light glows.
  - `scripts/art/selout.gd`: the sel-out finish, which recolours a shape's rim from its neighbours.
  - `scripts/dungeon/floor_painter.gd`: ground patches, a lit lip where a wall meets the floor, cliff faces, and shadow under walls.
- **In this project:**
  - `tools/blender/make_mech_textures.py` paints armour panels, seams, rivets and vents in Python.
  - `bake_atlas()` in `tools/blender/build_ape_l_v2.py` bakes colour, ambient occlusion, a high-to-low surface-detail (normal) map, metal/roughness and edge wear from Blender into one 2048 px texture set, and smooths the bake grain first.
- **For the 3D rooms, combine the two:**
  1. Paint each room material's texture in code (Python and PIL, or Godot's Image class) with the room-painter rules: concrete floor plates, wall panels, hazard stripes, rails.
  2. Bake ambient occlusion from the composed Blender room into the room's atlas, the way `bake_atlas()` does, so corners and the bases of props darken.
- **Pixel scale:** about 32 texture pixels per metre with nearest filtering, so surfaces come out as chunky as the game's 320x180 pixels.
- **Calm colour:** flat blocks of colour with a few deliberate details. Speckle noise is the thing to avoid (we measured the finished references: they are calm).
- **No generated textures** on the room shell.

## Task R1: the hangar bay (do this first)
The home base interior, where the player's machine stands between missions.

**Function gate**
- **Family adapter:** `display-gallery`. The hero object is the machine in its maintenance cradle.
- **Size:** about 14 m wide, 16 m deep and 8 m high.
- **The bay:**
  - a maintenance bay about 6 x 7 m in the centre, with floor markings
  - the machine stands at the bay's centre, at the world origin, facing the camera
  - a wide open bay door (at least 6 m) on one wall, with a visible apron outside
- **Props:** a restrained family of six to eight. For example:
  - an overhead gantry crane
  - a tool cart
  - a parts rack
  - pallets of ballast blocks echoing the gorilla's back blocks (grey with orange caps)
  - coolant tanks
  - a console with teal screens
  - cable trays
  - work lights
- **Budget:** at most about 40,000 triangles for the whole room. One small atlas or flat swatch texture per prop family.
- **Camera:** the production camera is the game's view of the base: high three-quarter, the machine readable at 320x180.
- **Stop:** show Preston the floor plan, the prop list and the reference contact sheet, and wait.

**Form gate:** build the shell, cut the openings and place the props as your plugin describes. Then:
- load `ape_l.glb` into the bay to check scale
- render the plugin's review views
- show Preston, and wait

**Runtime gate (wired, see the 2026-10-12 update):**
- export the room to `art/rooms/hangar_bay/hangar_bay.glb` under the room contract
- run `tools/debug/room_check.gd` with `HT_ROOM=hangar_bay`; it must print PASS
- run `tools/blender/probe_hard_edges.py` on the export; hard edges above 60% crisp
- show Preston the still it saves (`docs/art/3d/room_hangar_bay.png`), and wait
- a dedicated `scenes/rooms/hangar_bay.tscn` is not needed for the gate; the stage loads any room. Build one only
  when gameplay needs it (doors, triggers, the camera path), and say so in the handoff.

## Task R2 (only after Preston approves R1): the first battle stage
A walled stage for the first battle, built with the `gameplay-room` adapter. Preston picks its setting first (a
quarry, a dry riverbed, a ruined yard), so propose three short room briefs and let him choose.

## Handing back
Use the short handoff format in `docs/team/HANDOFF_FROM_HOLLOWTIDE_SESSION_2026-10-11.md`:
- what you built
- the files
- the check you ran and its output
- what you did not verify
- the open decisions for Preston
