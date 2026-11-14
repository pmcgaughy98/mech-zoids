# MOBA perspective, world and art remaster: synthesis (Claude, 2026-11-04)

Preston, 2026-11-04:
- (sending a Pokebonk reel) "this is how I want the MOBA to play perspective and world wise too."
- "Change our texture, shaders, style, detail outlines, sel out is what I meant. Originally was built based off
  GBA game's mystery dungeon and zoids legacy which i like the art style to a point but needs to be updated as if
  it was remastered for a moba today with our art style."
- "If there are any dissassemblys or anything on github ... we could add to repo for this too."

## What was read
**Read today:**
- **The reel:** Pokebonk, a free browser fan game in the style of Megabonk and Vampire Survivors. I looked at
  12 keyframes and the Whisper transcript.
  - World: low-poly 3D geometry with pixel-art textures (a tower room with walls, carpets and an altar; grass
    fields; water).
  - Camera: perspective, a chase camera behind and above the player at a low pitch (I estimate 25 to 35
    degrees). The horizon is visible and the player stands in the lower middle of the screen.
  - Characters: flat 2D pixel sprites standing upright in the 3D world. While the player runs away from the camera
    you see the sprite's back. A glowing ring sits on the ground under the player.
  - UI: a top bar with the run timer and wave count, plus small pickup prompts.
- **Doom source** (`id-Software/DOOM`, GPL-2.0, cloned for study to
  `D:\Program Files (x86)\Game assets\game-source\doom\`).
  - `r_things.c` line 523 picks which of 8 drawings to show from the angle between the viewer and the thing's
    facing, rounded to 45-degree sectors.
  - Rotations without their own drawing reuse a mirrored one through a per-rotation `flip` table. That is the same
    scheme as ours: 5 drawn views, with w, sw and nw mirrored.
- **Godot's 3D sprites demo** (`godotengine/godot-demo-projects`, `3d/sprites` only, MIT, cloned to
  `game-source\godot-demo-sprites\`). Only the file list was read: an `AnimatedSprite3D` player, shaders and
  textures. The bodies are not read yet.
- **Shotcaller** `move_action.gd` line 68 (already cloned): the walk animation's speed scales with the unit's
  current movement speed, so the feet don't slide.
- **Hollowtide sel-out shader** (`sel_out.gdshaderinc`): its detail-ink rule. Today's front fix uses part of it
  (below).
- **Search results, not opened:** a Godot forum thread and the framesprite.com guide on choosing the 8-way view
  relative to the camera, and a godotshaders.com directional billboard shader.

**General knowledge, not checked today:**
- HD-2D games (Octopath Traveler, Triangle Strategy, Live A Live remake): pixel sprites in a lit 3D diorama world,
  with depth of field, bloom and sprite shadows. This is the best-known "GBA look, remastered" route.
- Sea of Stars: modern pixel art with dynamic light.
- PMD Rescue Team DX: the actual remaster of the GBA game. It went painterly 3D and dropped pixels.
- Ragnarok Online: a 3D map with 8-direction sprite characters.
- Megabonk: commercial Unity game with 3D characters and no source. Pokebonk shows no public source that I found.

## Synthesis proposal (nothing here is canon)
**Perspective and world (from the reel, and SMITE's camera):**
1. The machines stay 2D pixel sprites. They become upright billboards in a 3D world: they turn only around the
   vertical axis, use nearest filtering and alpha scissor, and pivot on the feet (row 160 of the 192 canvas).
2. A chase camera sits behind and above the player at about 30 degrees.
   - The player sees their own machine mostly from behind, so the back and back three-quarter walks (n, ne, nw)
     are the most-seen frames.
3. Which view to show = the machine's facing minus the camera's yaw, rounded to 45 degrees (the Doom rule).
   - s, se, e, ne and n are drawn; sw, w and nw are those mirrored.
4. Walk playback speed follows movement speed (the Shotcaller pattern).
5. The world is low-poly 3D with pixel-art textures at 50 texels per metre (0.02 m a texel).
   - Target to start from: the rhino is about 140 sprite pixels long. If it is 3 m long, one texel is about
     0.02 m, so world textures are drawn at 50 texels per metre.
   - Machines, changed 2026-11-04: Preston picked size option B, "B, per-class size". Each class has its own texel
     size: L 0.020 m (the same grid as the world: rhino, gorilla), M 0.018 m, S 0.016 m. The stills stay as drawn,
     and the engine applies the factor. This replaces the earlier "world and machines share one pixel grid". The
     class list is in `docs/art/moba/ROSTER.md`, under "Size in the 3D world".

**Art remaster ("as if remastered for a MOBA today", our style):**
1. Keep the palettes, the 192 px sprites and the sel-out outline: one texel in #141218 outside the silhouette.
2. **Detail ink**, matched per view to the walks Preston likes. The `contour` rule in `anim/detail_ink.py` puts a
   one-pixel black line where dark body meets a bright plate. Today it is on the front and back walks only.
3. **Light from the world:** a normal map per sprite, so the sun and lamps shade the machines.
   - The PixelLab MCP has a `create_normal_map` tool; its cost is not checked yet.
4. **Readability, MOBA-style:** a rim light or outline tint in team colour, a contact shadow and a ground ring
   under each machine (the reel has the ring), and health bars above.
5. **Post effects:** gentle bloom on emissive parts (eyes, effects) and distance fog. Depth of field stays off
   during play.

**Alternatives:**
- (a) Keep the approved 2D top-down arena (2026-11-03) and do the remaster only on sprites with a 2D shader.
- (b) Full 3D models (the Megabonk and SMITE way), which retires the sprite work.
- (c) A fixed or rotating isometric 3D camera, Ragnarok-style, instead of a chase camera.

**This changes an approved decision:** the 2026-11-03 skeleton is a 2D top-down arena (`scenes/moba/arena.tscn`,
`Camera2D`). Moving to 3D means unit positions become `Vector3`. The lane, tick and match logic carries over.

## One first slice
`scenes/moba3d/rhino_walk_test.tscn` contains:
- a flat ground plane with one pixel-art tile texture at 50 texels per metre, plus a sun;
- the chase camera;
- the rhino as an `AnimatedSprite3D`, using a `SpriteFrames` resource built from
  `codex-set-a/walk/frames_selout`:
  - `walk_s`, `walk_se`, `walk_e`, `walk_ne` and `walk_n`, 8 frames each at 8 fps;
  - the idle still as `idle_*`;
- WASD movement, with the view chosen relative to the camera and the walk speed tied to movement speed.

**Headless check:**
1. With the camera fixed, turn the rhino through 8 headings and assert the animation name and `flip_h` for each:
   sw shows se mirrored, w shows e mirrored, nw shows ne mirrored.
2. Assert that the sprite's foot row sits on the ground plane.
3. Assert the run printed no errors.
4. One screenshot for Preston to look at.

## Walk changes made today (anim/codex-set-a/walk)
- **New walk swapped in, sel-out rerun:** 8 frames in each of the 5 views. The old 7-frame set is kept in
  `walk/frames_pre_retro/` and `walk/frames_selout_pre_retro/`.
- **Reel updated:** `rhino_reel.py` now plays all 8 walk frames.
- **Front shoulders, geometry:** `retro-walk/pixellab/fix_front_shoulders.py` puts the approved still's shoulder
  plates back. PixelLab had stretched them into the knee; the legs keep PixelLab's step.
- **Front shoulders, ink:** `anim/detail_ink.py` adds black contour lines on the flat views.
  - It runs only on views whose interior ink share is below the lowest of the se and side walks (5.8%).
  - Front: 1.6% before, 5.2% after. Back: 5.7% before, 10.0% after.
  - The shader's full rule measured 22% and 28%: it blacked out the underbody, so it was not kept.
- **Not fixed:**
  - The shoulder-plate-to-knee-disc edge has no line, because both are light colours.
  - The front and back forward foot sits 1 to 5 px below the ground line. The reel's ground check lists those
    frames. In a 3D world that sinks a foot up to about 0.1 m into the ground. Clamping it is a one-line choice.

## Sprite tools on hand for the remaster
Preston, 2026-11-04: "We have tools that would help with this too now maybe like aseprite etc. sprite tools ... Also
codex used to help a lot with sel-outs too." The synthesis stock-take in CLAUDE.md now names them.

**Free:**
- **Aseprite MCP (local):**
  - hand-inks where a rule can't, such as the shoulder-plate-to-knee-disc edge;
  - locks the palette (`quantize_to_palette`);
  - `outline_native` to compare against our sel-out;
  - onion skin and `audit_animation` to check for sliding feet;
  - `export_spritesheet` for the engine.
- **Our own scripts:** `selout_rhino.py`, `detail_ink.py`, the ground check in `rhino_reel.py`, and
  `gait_check.py`.

**Free daily generations, then paid:**
- **PixelLab MCP:**
  - pose-guided animation (`animate_with_skeleton_v3`) for the diagonals the other 7 animations lack;
  - `create_normal_map` so the world's light shades the machines;
  - `pixelart_workbench` for exact pixel edits, which costs nothing.
  - Cost: 20 free generations a day, 9 left today. The cost of `create_normal_map` is not checked.

**Paid:**
- **Retro Diffusion MCP:**
  - the walking style (the side and se walks came from it);
  - `fix_pixel_art` and the palette tools for cleanup.
  - Cost: balance $1.61; the edit tools are $0.001 to $0.01 per run.
- **SpriteCook:**
  - background removal;
  - its Godot character export, to check our `SpriteFrames` format against.
  - Cost: credits not checked.

**Codex (no cost listed):** did the earlier sel-out and finish passes (codex-set-a, codex-set-b, the ground pound).
It could do the remaster finish on the rhino's frames once Preston rules on the open question: do this rhino's own
earlier frames count as "old art" Codex must not see?

## First slice built (2026-11-04, Preston: "yes go 3D")
- **Scene:** `scenes/moba3d/rhino_walk_test.tscn` contains:
  - a flat 60 m ground and five stone pillars, using our own 32 px grass and stone tiles at 50 texels per metre
    (world triplanar);
  - a sun with shadows, a sky, and light distance fog;
  - the rhino with a blue ground ring and a contact shadow;
  - the chase camera: 6.5 m back, 30 degrees pitch, Q/E or right-drag to turn.
- **Scripts:**
  - `scripts/moba3d/directional_sprite_3d.gd` (`DirectionalSprite3D`): picks the view by the Doom sector rule and
    mirrors sw, w and nw. A turn mid-walk keeps the step.
  - `scripts/moba3d/chase_camera_3d.gd` (`ChaseCamera3D`).
  - `scripts/moba3d/machine_test_player.gd`: WASD or arrow keys move relative to the camera. The walk speed
    follows movement speed.
- **Sprites:** `tools/art/pack_rhino_3d.py` packs the live walk and the idle stills into
  `art/machines/rhino/rhino_sheet.png` and `rhino_frames.tres` (`walk_s`, `walk_se`, `walk_e`, `walk_ne`,
  `walk_n` at 8 fps, plus `idle_*`). Rerun it after any frame change, such as the Codex pass.
- **Check:** `tools/debug/rhino3d_check.gd`, run headless, passes 23 of 23:
  - every walk has 8 frames and every view has an idle;
  - all 8 headings plus 2 off-axis headings show the right view and mirror;
  - the feet sit on the ground (0.0000 m);
  - the sprite is at 50 texels per metre.
  - Run with a window and `-- --shot`, it saves `anim/rhino3d-slice-behind.png` and `rhino3d-slice-side.png`.
- **Still open:**
  - matching move speed to the stride (3.5 m/s is a placeholder);
  - normal maps and lighting on the sprites (they are unshaded now);
  - the arena, lanes and units moving to 3D;
  - world art beyond placeholder tiles.

## Gorilla kit, started 2026-11-04
- **Codex set A** (idle, knuckle walk, chest beat, hex shield throw): front, side and back, made from the
  approved stills. Brief and log are in `docs/art/moba/ape_l/take-a/anim/codex-set-a/`.
- **Set B** is next: bound (leap and land), hex dome cast, death.
- **Hex shield, Preston's look:** a green hexagon circle shield around the machine that gets it. He first asked for
  three copies of the gorilla's hex gems orbiting it, then the same day: "also Remove the three shield things that
  rotate on gorilla shields". The gems are gone; only the hex shell remains.
  - Code: `scripts/moba3d/hex_shield.gd`, `shaders/hex_shell.gdshader`.
  - Art: `tools/art/pack_ape_fx.py` draws the 24x14 pixel hex tile. It also still cuts the gem images, but nothing
    loads them now.
- **Hex dome:** the same shell, 3.2 m and cut at the ground.
- **Shots:** `tools/debug/hex_shield_shot.gd` writes the shield and dome shots into `ape_l/take-a/anim/`. The gorilla
  there now plays its packed frames.
- **Where it stands (end of 2026-11-04):**
  - Set A is done. `seam_fill.py` closed the one-texel gaps left by moved parts.
  - `tools/art/pack_ape_3d.py` writes `art/machines/ape/ape_frames.tres`: 16 animations, outlined with #141a16.
  - Set B (bound, hex dome slam, death) is running on Codex in `codex-set-b/`.
  - `ape_kit.gd`, its check and the reveal are with the game feel lane.
- **Lanes:** the work is now split across four sessions started from Mech-Zoids Game:
  - sprite factory: stills;
  - animation: frames, sheets and packs;
  - MOBA game feel: kits, effects, checks and reveals;
  - map design: the world.
