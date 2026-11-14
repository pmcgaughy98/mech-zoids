# Drone 3D test

Question (Preston, 2026-11-04): can a 3D model, seen from the chase camera, look like the approved sprite just became 3D?

## Paused (Preston's decision, 2026-11-04)
Preston has switched the plan to 2D sprites drawn from the game camera's angle, not 3D models. The hub relayed his reason: from the camera above, a 3D model reads flat, "like paper mario". Work here stops, and everything is left as saved.
- **Where the model stands:**
  - Pass 3 is the approved model (`_pass3_approved/`).
  - Pass 5 is the latest: `drone_parts_blue.glb` and `_red`. It leans toward the factory's game-camera drawing, about 6 to 7/10 against it.
  - Pass 4 is in `_pass4/`.
  - Passes 4 and 5 are not approved. The game still uses the billboard.
- **Pitch findings:**
  - The approved views were drawn from about 9 degrees above level.
  - The chase camera looks down 30 degrees, about 35 at a machine.
  - The cam30 drawing is consistent with 35 to 45 degrees. At 35 degrees a solid drone is only about 1.15 to 1.2 times as tall as the 9 degree drawing.
  - An upright billboard seen from there is squashed by about 18%.

## Answer so far (3D test lane, 2026-11-04)
- **Not automatically from the sprites.** Carving the five views gives the right outline at the drawn angle but a blob from the game camera. Score 2/10.
- **A model built by hand to the views can read as the same drone.** Part-built in voxels, it scored 5/10 after one free pass and 6/10 after three: same parts, palette and plan proportions, but not yet the sprite. Getting closer is hand work, like the ape: more look-and-score passes per machine.
- **The camera angle limits any model.** The views were drawn from about 9 degrees above level, and the chase camera looks down at 30 degrees (about 35 to the drone). From the game camera, any 3D model shows a top the sprites never drew, so that top has to be designed.
- **The animated .glb works in Godot.** The Lite hover_idle clip loads, plays and moves.

Board: `board_3d_test.png`. Animation frames: `anim_strip.png`.

**Approved (Preston, 2026-11-04), see `APPROVED.txt`:**
- model B pass 3 as the drone's 3D model for now;
- asking the factory lane to draw s and se at 30 degrees.

The game still uses the billboard.

## Model B against the cam30 drawing (2026-11-04)
The factory drew s and se for the game camera (`views_cam30/`). Preston has not judged that drawing, so this lists where B and the drawing disagree. B is unchanged.

Board: `board_cam30_score.png`. Numbers: `cam30_score.json`. Script: `cam30_score.py`.

- **The drawing is not flatter than 35 degrees.**
  - Method: at each pitch, the approved views (at 9 degrees) were carved together with the two cam30 views and se's mirror, then scored on how much of every silhouette the joint solid explains.
  - Result: the fit climbs steadily from 0.925 at 9 degrees to 0.965 at 34, peaks at 0.971 at 41.5, and is flat after. So the drawing is consistent with 35 to 45 degrees.
  - Its height (56 px, 1.22 times the approved 46) is what a solid shows at that angle. B drawn at 35 degrees is 53 px, and at 41.5 degrees 55 px.
- **They agree on the outline.**
  - At 35 degrees, silhouette IoU is 0.87 (s) and 0.84 (se), and the widths match (69/69, 59/61).
  - Exact colour match is 30 to 33% and material match 62 to 69%, in the same range as B against the approved views.
- **They disagree on four parts:**
  - **Shell.** The drawing's dome is taller and rounder: its top is 4 rows higher, and it holds about 30% more blue pixels (1,233 against 908 in s). B keeps the approved flatter cap. The factory names this as drawing drift.
  - **Lens.** B shows 2 to 2.4 times the drawing's lens pixels (234 against 97 in s, 177 against 92 in se). That is also more than the factory's tilt estimate (about 185), because pass 2 enlarged B's lens on purpose so the visor would not hide it from above.
  - **Barrels.** From above, B's barrels hang below the face as two long grey blocks that read as legs. The drawing shows short tubes. B's length comes from the approved side view, so the drawing foreshortens them more than the approved geometry allows.
  - **Pods.** The drawing's pods sit higher, with caps level with the lower dome. B's pods sit lower, beside the face.
- **Score: B pass 3 against the drawing, about 5/10.** It has the same parts and outline, with a different dome, lens and barrels.
  - If Preston accepts the drawing, B would need a taller, rounder dome (about 4 rows), half the lens, shorter barrels and higher pods.
  - If he prefers the approved views, the drawing's dome and lens would need redrawing.

### Pass 4 (Preston on the board: "it looks good though getting close keep refining")
- **Method:** `refine_b.py` rebuilt B from seven shape numbers and scored each set against both targets at once:
  - the approved views at 9 degrees;
  - the cam30 drawing at 35 degrees.
  - Score per view: silhouette IoU plus material IoU for blue, glow, steel and dark. Coordinate search from pass 3; it converged in two rounds (`refine_b.json`).
- **Kept:**
  - the dome 2 voxels taller and 6% wider;
  - the barrels 3 voxels shorter;
  - the pods 1.5 voxels higher.
  - The lens stayed at radius 8, because every smaller lens scored worse against the approved views. This matches the factory's own caution that its lens came out small.
- **Combined score:** 0.643 to 0.656. Approved views 0.628 to 0.633, drawing 0.658 to 0.679.
- **Against the drawing at 35 degrees:**

  | view | silhouette IoU | colour | material | blue shell px |
  |---|---|---|---|---|
  | s | 0.872 to 0.875 | 30 to 35% | 62 to 64% | 908 to 1,022 (drawing 1,233) |
  | se | 0.84 to 0.87 | 33 to 38% | 69 to 72% | not measured |

- **At the approved 9 degrees:** IoU 0.81-0.94 became 0.80-0.91, colour 20-36% became 24-35%, material 55-66% became 60-64%. The best silhouette dips a little; the weakest colour and material views improve.
- **From the chase cam:** the barrels no longer hang like legs, and the dome is fuller. I score it about 6/10 against the drawing (up from 5); against "the sprite became 3D" it holds at 6/10.
- **Still short:**
  - the dome is flatter and wider than the drawn one; a taller dome costs the approved views;
  - the lens is still about twice the drawn size;
  - the face around the lens is charcoal, as in the approved views, where the drawing shows lighter steel.
- **Files:** 8,410 triangles. Pass 4 files, shots and search are kept in `_pass4/`. The approved pass 3 files, shots and boards are kept in `_pass3_approved/`.

### Pass 5 (Preston: "Lean toward drawing")
- **Method:** the same search, with the drawing weighted 0.9 and the approved views 0.1 (`python refine_b.py 0.9 refine_b_pass5.json`). Two new options: a steel face round the lens, and the lens height. It started from pass 4.
- **Kept:**
  - the dome 2 voxels taller again (radius 23, pass 3 was 19);
  - a light steel face plate round the lens, as the drawing shows;
  - the lens 3 voxels lower and one voxel smaller (radius 7, pass 3 was 8);
  - the pods back at pass 3 height;
  - the barrels as in pass 4.
- **Search score:** 0.674 to 0.703. Drawing 0.679 to 0.716, approved views 0.633 to 0.590.
- **Against the drawing at 35 degrees:**

  | view | silhouette IoU | colour | material | lens px | blue shell px |
  |---|---|---|---|---|---|
  | s | 0.875 to 0.91 | 37% | 70% | 193 (drawing 97) | 1,053 (drawing 1,233) |
  | se | 0.869 to 0.883 | 39% | 77% | 133 (drawing 92) | 1,058 (drawing 1,182) |

- **At the approved 9 degrees (the cost):** IoU 0.80-0.91 became 0.79-0.87, colour 24-35% became 21-33%, material 60-64% became 58-62%.
- **From the chase cam:** the face now reads as the drawing's grey face with a lens in it, not the approved charcoal one. I score it about 6 to 7/10 against the drawing (up from 6). Against the approved views it slips a little, still about 5 to 6/10.
- **Still short:**
  - the drawing's shell wraps down round the sides of the face; B's dome still sits on top of a box, so the head reads as cap plus block;
  - the dome top is 2 rows lower than drawn and holds about 15% fewer blue pixels;
  - the lens is still 1.5 to 2 times the drawn size;
  - se is 5 px narrower than drawn (56 against 61);
  - the barrels still read as two blocks from above, not short tubes.
- **Next step if he wants more:** the shell wrap is a new part (side cheeks of blue that come down over the face), not a number change, so it needs a hand pass rather than the search.
- **Files:** 8,476 triangles, 1.09 x 0.78 x 0.90 m. Pass 5 is now `drone_parts_blue.glb` and `_red`, with `godot_shots/` and `board_cam30_score.png` (last column is pass 4 for comparison). `board_3d_test.png` and `anim_strip.png` in the main folder still show pass 3.

## Measured
- **Drawn pitch: about 9 degrees.**
  - Method: carve the five views plus their mirrors at each pitch from 4 to 16 degrees and keep the pitch where the solid explains most of every silhouette (`voxel_build.py`, `measure_pitch`).
  - Result: 9 degrees gives 0.9913. The fit is flat from 6 to 12 degrees (within 0.3%). 0 degrees gives 0.965 and 30 degrees gives 0.948.
  - No doc gives a number. The prompt sheet only says "the SAME low camera height".
- **Game camera:** `scripts/moba3d/chase_camera_3d.gd` and `scenes/moba3d/arena_blockout.tscn`: fov 60, 6.5 m back, 30 degrees pitch, aimed 1.2 m up.
- **On screen at 1280 x 720 (the game window):**
  - The billboard drone is 55 px tall, 1.2 px per texel.
  - A solid model of the same 0.736 m height covers about 1.5 times more screen height than the billboard, because its top shows.
  - Correction (2026-11-04): that 1.5 is against the billboard as it sits on screen, upright and so squashed to about 82% by the 35 degree view. Against the drawn 46 px, a solid seen at 35 degrees is only about 1.15 to 1.2 times as tall: model B drawn at 35 degrees is 53 px. The earlier wording let the factory read 1.5 as "1.5 times the drawing".
  - At 30 degrees the upright billboard is squashed by about 18% (cos 35).
- **The views disagree with each other in 3D.**
  - Colouring the carved solid from the south view alone matches south 100%.
  - Blending all views matches each view only 51 to 60% (`voxel_report.json`).
  - So no single coloured model can reproduce all five drawings pixel for pixel. The views are drawings, not projections of one object.

## Models
| | file | triangles | at the drawn 9 deg: silhouette IoU / colour / material | chase cam score |
|---|---|---|---|---|
| A. carved voxels | `drone_voxel_blue.glb`, `_red` | 15,108 | 0.97-0.99 / 34-42% / 63-80% | 2/10 |
| B. part-built voxels, pass 3 | `drone_parts_blue.glb`, `_red` | 7,964 | 0.81-0.94 / 20-36% / 55-66% | 6/10 |
| B pass 1 (kept for comparison) | `_pass1/drone_parts_blue.glb` | 8,114 | 0.82-0.94 / 19-33% / 52-63% | 5/10 |
| C. Retro Diffusion Lite | `drone_lite_anim.glb` | 666 | not measured | 3/10 |

- **A: carved from the sprite's own pixels.**
  - 0.016 m voxels, the interior dropped, faces merged.
  - The colour comes from a material vote across the views (blue, steel, charcoal, seam, glow), with shades re-banded from one fitted light (`colour_banded`). The raw per-shade vote was noisier.
  - From 30 degrees, the pods fuse with the body into a flared skirt, because no view sees the gap between them. The lens is squashed and the shell is mottled.
- **B: built from solids measured off the s and e views.**
  - The parts: dome, hull, brow, lens in a dark socket, twin barrels, pods with caps and glow rings, nozzle, back plate with vents.
  - The shading is banded from one light above, with a seam colour where parts meet.
  - Pass 1 fell short from the chase camera in six ways:
    - the dome dominated;
    - the pod caps overhung and hid the steel bands, so the pods read as blue balls;
    - the face read light grey (brow and cheek tops lit), where the sprite reads charcoal;
    - the lens was smaller and recessed;
    - the voxel steps showed on the dome;
    - the back view was weak.
  - **Pass 2** measured the shades the sprite uses on each part. Steel is mostly 8a8f9c and 5c6170 and never e2e4ea; the face is about half charcoal and seams; the shell is about half 3a8cff. Each part's shades are now cut from the light to those shares. Changes:
    - darker face;
    - cheek plates only on the lower front corners;
    - a narrower visor, cut from a +24 (the e view) to a +15. This is a deliberate change from the drawing: the full visor hides the top half of the lens from a 30 degree camera;
    - a bigger lens that stands out past the visor;
    - a dark steel back plate with vents.
  - **Pass 3:**
    - the shell shades in flat facets (8 sides by 4 tiers), like the drawn shell;
    - a smaller top highlight (15%), since the top shows more from 30 degrees;
    - pod caps reshaped as lids (6.3 tall on a taller band), because the drawn cap height includes about 2 rows of top seen at 9 degrees.
  - **Still short after pass 3:**
    - from above it is taller and boxier than the wide, flat sprite;
    - the pods still read as balls at game size;
    - voxel steps show on the shell edge.
    - Nobody has drawn the drone from 30 degrees, so "what the sprite would look like from up there" is a guess. A drawn s and se at 30 degrees would give a real target to score against.
  - `_pass2/` holds pass 2's Godot shots. Pass 1's shots were overwritten by mistake; its model is in `_pass1/`.
- **C** is as the first test found:
  - faceted dome, flat octagon lens, stub barrels, no centre thruster;
  - from 30 degrees the facets read strongly;
  - its glb carries its own point light (KHR_lights_punctual), which the test removes.
- **Red team:** both voxel models have red copies made by swapping the 16 x 1 palette texture. The red mapping is read from `views_red`. They are built but not rendered.
- **Lighting:** voxel models are unlit (KHR_materials_unlit), like the game's billboards (`shaded = false`). The painted bands are the shading.

## Animation (the $0.08 run)
- **Job:** Retro Diffusion `start_lowpoly_animate` on asset `3991f3d2-0e91-4651-a7b5-6dc44a82f490`, prompt "gentle hover idle...".
  - Charged $0.08; the rig was included.
  - Balance $0.73 before, **$0.65 left**.
- **Clip:** `hover_idle`, 3.0 s.
- **Files:**
  - Export `drone_lite_anim.glb`: 22 meshes on 35 nodes, no skin. The animation moves rigid parts (33 channels in the file, 10 tracks in Godot).
  - `lite_hover_idle.gif` is the service's preview.
- **In Godot 4.7.2:**
  - `GLTFDocument` loads it and makes an AnimationPlayer with `hover_idle`.
  - Seeking moves the drone: the bounds centre rises 4.6 cm at 0.75 s and returns at 1.5 s.
  - It came in with loop_mode 0 (no loop), so the game would set loop on import or in code.
- **Voxel models:** a hover bob needs no rig. `anim_strip.png` row 2 is B moved and tilted in code. Separate moving parts (pods, barrels) would need each part exported as its own node. The part ids already exist in `part_build.py`; this is not done.

## Files
- **Scripts:**
  - `voxel_build.py`: pitch fit, carve, colour, glb writer, reprojection. `--fast` skips the 2-minute pitch scan.
  - `part_build.py`: model B. Its colouring now sits in `colour()`, so `cam30_score.py` can reuse it. The model is unchanged: same glb checksum, 52d34fce.
  - `cam30_score.py`: the cam30 pitch fit and B's score against the cam30 drawing.
  - `drone_view.gd`: the Godot scene.
  - `make_board.py`: the boards.
- **Godot run** (needs a window):
  `Godot --path D:/dev/new-mech-rpg --script res://docs/art/moba/minion_s/take-a/3d_test/drone_view.gd`.
  - It uses the arena's nature-theme sun, ambient, sky and fog values, copied into its own scene. arena_play is untouched.
  - Shots go to `godot_shots/`, with `godot_log.txt`.
- **Reports:** `voxel_report.json`, `parts_report.json`.
- **Reprojections:** `reproject.png` (A) and `reproject_parts.png` (B) show the model drawn back at 9 degrees under the views. The `_reproject_*.png` files are A's single cells.
- **First test:** `render.png`, `turntable.png`, `drone_lite.glb`, `compare_board.png`.

## Not verified
- **Editor import of the .glb files.** `docs/` has `.gdignore`, so the test loads them at runtime through GLTFDocument, the same parser the importer uses. The importer's own steps (compression, LOD, loop settings) did not run.
- **The real arena.** The look was not tested inside arena_play with towers, fog distance or other minions.
- **Other window sizes.** Only 1280 x 720 was rendered. At larger windows a model's edges get finer than a texel while the billboard stays blocky; a fixed low-resolution 3D pass would hold the look, but it was not built.
- **Frame cost.** 8 to 15 thousand triangles per voxel drone is heavy for many minions; a lower-poly rebuild would be needed. This was not measured.
- **Red copies and the voxel bob.** The red copies were not rendered. The voxel bob was only seen in stills.
- **Scores for B.** Pass 2 and 3 scores are by eye against the billboard and the drawn views. There is no drawn 30 degree view to score against.

## First test (hub, 2026-11-04)
- **Run:** Retro Diffusion Low-Poly `rd_lowpoly__detailed_lite`, size 64, $0.10.
  - Inputs: four approved blue views (s, se, e, n), cropped at 1x on white and quantised to 32 colours.
  - The asset_id is above.
- **Kept:**
  - the blue top shell;
  - two side pods with blue caps and cyan glows;
  - one big front lens;
  - twin barrels;
  - the charcoal hull and the palette.
- **Drifted:**
  - a faceted shell;
  - taller pods;
  - a flat octagonal lens;
  - stub barrels;
  - no centre nozzle;
  - a bulkier body.
- **Verdict then:** too loose to render straight into game sprites.
