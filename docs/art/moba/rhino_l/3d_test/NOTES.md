# Rhino 3D test

Question (Preston, 2026-11-04, through the hub): can the rhino be a 3D model that looks like the approved views just became 3D, seen from the game's chase camera?

## Paused (Preston's decision, 2026-11-04)
Preston has switched the plan to 2D sprites drawn from the game camera's angle, not 3D models (relayed by the hub). Work here stops, and everything is left as saved. Nothing is rigged and the walk is not built.
- **Where the model stands:** pass 5, about 4/10 from the chase camera. It is `rhino_parts.glb`, also copied to `_pass5/`.
- **Against the factory's game-camera views** (`take-a/views_cam30`), pass 5 drawn at 34 degrees:
  - silhouette IoU 0.73 to 0.83 (s 0.77, se 0.73, ne 0.73, n 0.83);
  - colour 30 to 41%, material 72 to 80%;
  - in s, the drawing's back deck reaches 13 rows higher (87 px tall against 72).
- **Pitch findings:**
  - Approved views: about 6 degrees (the carve plateau is 6 to 16; the feet say 1 to 4).
  - Game-camera views, read from the height the pass 5 model needs to match each one: se, ne and n about 38 degrees, s about 48.
  - e is far lower: the model at 34 is already 12 px taller than the drawn e. That agrees with the factory's own failed camera check on e.
  - The carve-at-each-pitch scan gave no usable answer for the rhino. s and se kept rising to the scan's 50 degree end, e and ne flattened near 46 to 48, and only n peaked (about 40). A 46 degree reading for e, which barely moved, shows the scan does not measure pitch here.
- **Shape search (`rhino_cam30.py`; not built):**
  - Method: at 34 degrees, with the drawing and the approved views weighted equally.
  - Score: 0.579 to 0.589 (drawing 0.556 to 0.571, approved 0.602 to 0.606).
  - Best set: rear deck 2 voxels higher and narrower on top, hump longer, shoulder plates 4 lower, head 2 lower and 1 narrower.
  - The numbers are in `rhino_cam30.json`. `rhino_build.py` now takes them in `SHAPE`, but still builds pass 5.

## Answer (3D test lane, pass 5, 2026-11-04)
- **Not yet. About 4/10 from the chase camera.** From the views' own low angle, the part-built voxel rhino matches the drawn outline fairly well (silhouette IoU 0.70 to 0.90). From the chase camera it reads as a yellow armoured shell, not as the sprite:
  - its broad, flat back is a top the sprites never drew;
  - the dark seams and shaded lower bands that define the sprite's plates sit on faces the camera barely sees, so from above the plates merge;
  - the head is small and low;
  - it stands 1.3 to 1.5 times the billboard's screen height.
- **It stopped improving after pass 4.** Pass 5 traded pass 4's stair-step stripes for blobbier plates. More passes of the same kind would be guesses about the top.
- **What would move it:** a drawn target from the game camera, like the drone's `views_cam30`. The back three views matter most, because the chase camera sits behind the player. The hub prices that job.

Board: `board_rhino_3d.png`. Rows: the approved views, the billboard from the chase camera, the model from the chase camera, and the model drawn back at the views' angle.

## Measured
- **Drawn pitch: low, about 1 to 16 degrees. The build uses 6.**
  - Carve fit (`rhino_pitch.py`, `pitch_fit.json`): flat from 6 to 16 degrees (0.905 to 0.911 explained, best at 12). 0 degrees gives 0.877.
  - Feet: the far feet are drawn 1 to 3 rows above the near ones, which says about 1 to 4 degrees.
  - Pass 1 used 12 and read the armour's upper bevels as top faces. That made a thin slab with too much top, so pass 2 dropped to 6.
- **The views disagree with each other more than the drone's did.**
  - The carved solid explains 91% of each silhouette, against 99% for the drone.
  - Heights are 67 (e), 70 (s) and 77 px (n, horn tip included).
  - The diagonal views are narrower than any solid with the s and e extents: se is 89 px wide and ne 77, against about 124 for a box as long as e and as wide as s. So se and ne can't match (IoU 0.70 to 0.79).
- **Model (pass 5):** 1.44 m wide, 1.36 m tall, 2.08 m long. 7,576 triangles, 0.020 m voxels, feet on the ground plane.
- **On screen at 1280 x 720:** the billboard is 103 to 120 px tall, the model 138 to 181 px (`screen_sizes.json`). As with the drone, this is the top showing.
- **Shade shares per part** were measured off the views (`rhino_report.json`, `shares`).
  - The rear armour is about half d18a0a and 42% ffcf1f.
  - The hump is 54% ffcf1f and 40% fff4a8.
  - The jaw is 63% dark grey.

## Passes
| pass | change | at the drawn angle: IoU / colour / material | chase cam |
|---|---|---|---|
| 1 | 12 degrees, armour as a thin slab | 0.64-0.86 / 25-34% / 54-67% | not rendered |
| 2 | 6 degrees, tall bevelled sides | 0.70-0.89 / 25-34% / 66-74% | not rendered |
| 3 | shades cut over the voxels the views see; dark gaps between plates | 0.70-0.89 / 28-39% / 65-76% | 3/10 |
| 4 | crease lines found from local fill; knee discs lower and bigger | 0.70-0.90 / 24-32% / 65-77% | 4/10 |
| 5 | crease lines only where one shade meets the next; narrower rear top | 0.70-0.90 / 28-37% / 64-76% | 4/10 |

- Pass 4 has more plate definition but stripes on every voxel step of the bevels.
- Pass 5 is cleaner but blobbier.
- `_pass1/` to `_pass4/` keep each pass's glb, report and sheet. Passes 3 and 4 also keep their Godot shots and board. The main folder holds pass 5.

## Where it falls short (pass 5)
- **The top.** From 30 degrees the rear armour is a wide flat deck and the hump a bright dome. The drawn views show neither top, so both are guesses.
- **Plate language.** The sprite's identity is its dark seams, orange lower bands and grey knee discs. Those live on sides and undersides, and from above the model is mostly light yellow. It is brighter overall than the billboard.
- **Head.** Small and low between the shoulder plates. From behind, only the horn tip shows (the drawn back view shows it too).
- **Voxel steps** show on the bevels, the hump and the horn.
- **Diagonals.** The se and ne views can't be matched without breaking s and e (see Measured).

## Walk plan (not built; costs below; nothing rigged)
1. **What the approved walk gives.**
   - The side walk (`take-a/anim/retro-walk/walk-final/`).
   - PixelLab keypoints per frame for front, back and ne (`take-a/anim/retro-walk/pixellab/*_keypoints.json`, labelled joints per leg).
   - From these: which feet are planted in each frame, the stride length in texels, the leg order, and the joint angles per frame. The 3D walk can then copy the approved timing instead of inventing one.
2. **Rig: the parts as nodes (recommended).**
   - Re-export the model as a node tree instead of one mesh:
     - body: armour, hump, core;
     - head: jaw, nose, horns, eyes;
     - tail;
     - per leg: an upper segment, the knee disc, and a lower segment (boot and sole).
   - Pivots: hip under the body (about 0.64 m up), knee at the disc centre (0.48 m), ankle at the boot base (0.14 m).
   - The legs are rigid mech parts, so a node hierarchy is a real rig. It needs no skin weights, and nothing stretches at the joints.
3. **Feet planted.**
   - Gait: a 4-beat walk (hind left, fore left, hind right, fore right), each foot down about 75% of the cycle.
   - Stance: each foot holds a fixed world target. Each frame, the two leg segments are solved to reach it with two-bone IK in the leg's plane (law of cosines).
   - Swing: the foot lifts about 0.06 m on an arc to its next target.
   - Body bob comes from the leg geometry.
   - Done in a Godot script, or baked into an AnimationPlayer clip.
4. **Speed (Preston's call, already open in the playbook).**
   - Stride per cycle times cycles per second must equal the move speed, or the feet skate.
   - At 3.5 m/s with about a 0.8 m stride, that is about 4.4 cycles a second, which looks frantic for this rhino.
   - Options: walk slower than full speed, switch to a run gait at speed, or accept some skate.
5. **Blender alternative (`mcp__blender__*`).**
   - Import the glb and add an armature: root, body, head, tail, and three bones per leg.
   - Bind each part rigidly to one bone, add IK constraints, key the walk, and export a skinned glb with the clip.
   - It is worth it if more clips (idle, charge, hit) come later or someone wants to edit in Blender. It takes more steps than nodes.
6. **Costs.**
   - Money: $0 either way (my scripts, Godot, Blender). Retro Diffusion's low-poly animate works on its own generated models, not this voxel one, so it does not apply. The balance stays $0.65.
   - Time, a rough guess: one working block (40 to 60 tool calls) for nodes plus the planted walk. Blender takes somewhat more.
7. **Check.**
   - Render the walk from the chase camera at four phases.
   - Log the foot world positions: a planted foot must stay within one texel (0.02 m) through its stance.

## Files
- **Scripts:**
  - `rhino_pitch.py`: the pitch fit.
  - `rhino_build.py`: the model, the reprojection and the scores.
  - `rhino_view.gd`: Godot shots, copied from the drone's `drone_view.gd`.
  - `make_board.py`: the board and the screen sizes.
- **Model:** `rhino_parts.glb` (unlit, palette texture `rhino_palette.png`). The rhino has no team colours, so there are no team copies.
- **Godot run** (needs a window): `Godot --path D:/dev/new-mech-rpg --script res://docs/art/moba/rhino_l/3d_test/rhino_view.gd`
  - It uses the arena's nature-theme sun, ambient, sky and fog values in its own scene. No game script was touched.
  - Output goes to `godot_shots/`.
- **Reports:** `rhino_report.json`, `pitch_fit.json`, `screen_sizes.json`.
- **Sheets:** `reproject_rhino.png` (views over the model drawn back at 6 degrees), `views_sheet.png` (the approved views side by side).

## Not verified
- **Editor import.** `docs/` is gdignored, so the glb loads at runtime through GLTFDocument.
- **The real arena.** The look inside arena_play, with other units and fog distance, was not checked.
- **Other window sizes.** Only 1280 x 720 was rendered.
- **Frame cost** of 7.6k triangles per rhino.
- **The pitch.** The evidence spans 1 to 16 degrees; the build uses 6.
- **Scores.** The chase-cam scores are mine, by eye. Preston has not seen the board.
- **The walk** is a plan only. The keypoint files were found, not parsed beyond their format.
