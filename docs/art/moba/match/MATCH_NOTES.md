# The playable match, 2026-11-04 (game feel lane)

Preston asked to "Hook it up so it feels legit." What follows is the 3 v 3 one-lane match in `scenes/moba3d/arena_play.tscn`.

## Play it
Open arena_play and run it. Keys:
- WASD moves.
- 1 to 4 are the kit.
- Space or left mouse attacks.
- B recalls.
- Tab swaps machine.
- Enter replays after a win.

`--sandbox` gives the old dummy field.

## Video
- `push_demo_2026-11-04.mp4`: 59 s, 1280x720, with game sound. `_phone.mp4` is the same clip at 15 MB.
- 0:05: two drone waves meet at the plaza.
- From 0:27: blue pushes into the red tower's range.
- From 0:45: the red tower takes damage and is down to about 65% by the end.
- How the take was made: `-- --push-demo` sets the first wave at 1 s. The red bots are held at their base, and your rhino runs on the bot autopilot so the push reaches the tower inside a minute. In a normal match all six machines fight, and the first 130 s ended in a stalemate at the plaza.

## Later the same day
- Body collision: machines, minions and camp monsters no longer walk through each other. See `scripts/moba3d/match_bodies.gd`.
  - A walk slides round whatever is in its way.
  - Bodies that end up overlapping (spawns, tosses, the kits' charges and leaps) are eased apart, and the lighter one gives way more.
  - A machine in the middle of an ability holds its ground.
  - Placeholders: weights machine 4, monster 3, minion 1; easing at 3 m/s.
- The map is now Preston's pick, Foundry. `push_demo_foundry_2026-11-04.mp4` (and `_phone`) is the same push on it, with collision on.
- Tower and core bars now sit at 4.2 m and 4.4 m, over the new turret heads (3.98 m) and reactors (4.35 m).
- Fog of war is live (the map lane's arena.vision).
  - Enemies outside blue's vision are hidden, along with their health bars.
  - Towers and cores always show.
  - Your attack and every bot only pick targets their own team can see.
  - Units pop into view at the edge of vision; they don't fade in.

## Camera-angle sprite test (Mech-Zoids, 2026-11-04)
Preston: "lets try keeping 2D sprites but with that". This is a test only, and nothing in the game changed.
- `DirectionalSprite3D.tilt_to_camera` is off by default. When it's on, the quad faces the camera fully: it leans back by the camera's pitch and pivots on the feet row.
- To run it: arena_play with `-- --cam-angle-test --out=<dir>` (`scripts/moba3d/cam_angle_test.gd`). No match starts, and the stand-ins take turns on the player's spot.
- The files are in `cam_angle_test/`:
  - `board_2026-11-04.png`: views s, se, e, ne and n of the drone and the rhino, today's upright next to tilted.
  - `camera_turn_2026-11-04.mp4`: 8 s. Real Q presses turn the camera a full circle, then E turns it half back.
  - Two full frames of the rhino's front view.
- Views drawn from 30 degrees on the tilted quad read as solid bodies seen from above: the rhino's back and the top of its head show, and so does the drone's dome.
- Views with no cam30 drawing show the approved view on the tilted quad. That only removes the squash, so the top still doesn't show.
  - On a turn, the machine pops at every such view: smaller and without its top, then big and topped again.
- The rhino's front view stands about 30% taller on screen tilted (about 142 to 185 px, measured).
- Unverified, from the numbers only:
  - The 1.9 m health bar would sit on the tilted rhino's head.
  - The tilted top leans about 0.9 m behind the feet, so a wall or tower there could cut into it.

### Second run: the drone's full 35-degree set (views_cam35)
- To run it: arena_play with `-- --cam-angle-set-test --drone-views=<dir> --out=<dir>` (`scripts/moba3d/cam_angle_set_test.gd`). The files are `drone35_board_2026-11-04.png` and `drone35_camera_turn_2026-11-04.mp4` in `cam_angle_test/`.
- The drone is tested in three spots, each as close as it can stand: open floor, in front of the blue tower, and inside the base wall. The HUD's own bar is drawn into every frame.
- Turning on open floor:
  - All five views and their mirrors keep the dome top.
  - The drawing heights step from 56 px (s) to 48 px (n), and no view pops.
- The bar:
  - At 1.3 m, the bar sits on the tilted drone when it's low on the screen: up to 89 px into the art, measured from 4 m nearer the camera to 14 m farther.
  - `MatchMinion.BAR_H_TILTED` (1.5 m) clears every view by 2 px or more. The HUD asks `bar_height()`, so an upright drone keeps 1.3 m.
- Lean-back:
  - The tallest view leans 0.52 m back, but a drone can stand 0.35 m from a wall.
  - Against the tower, the top of the dome was cut in s, se and e.
  - Against the base wall, it was cut in every view.

### Upright-depth fix and per-animation tilt (2026-11-04)
- Correction: I first proposed giving the sprite its feet's depth. That was wrong: a quad facing the camera already has its feet's depth everywhere. The wall above about 0.6 m really is nearer the camera than the feet.
- The fix that works is `scripts/moba3d/tilted_sprite_3d.gdshader`.
  - It draws the tilted image, but with roughly the depth today's upright sprite would have at that height.
  - Correction: "each row" was too strong. The quad has four corners, so the upright depth is exact only at the top. The bottom edge keeps the feet's depth, and the rows between are blended. That leaves the rhino's feet row about 0.3 to 0.4 m nearer the camera than its anchor, which is why a foot drawn a few rows below the anchor isn't hidden by the floor.
  - Things behind stay behind, and things in front still hide it.
  - The shader also pivots on the feet, so the node never moves between tilted and upright.
- Rerun: the drone's dome and the rhino are whole against the tower and the wall (`drone35_depthfix_*`, `rhino35_*`).
- Per-animation tilt: a SpriteFrames meta `tilt_anims` (names without the view, e.g. `["idle"]`) tilts only those animations; the rest stand upright.
  - The rhino lane installed the rhino's 35-degree idle with `tilt_anims = ["idle"]` (Preston: "Swap now").
  - Machines without the meta are unchanged.
  - Check: `tools/debug/tilt_check.gd`.
- The rhino's 35-degree set on its own turns a full circle with no pops.
  - It shows a mild drift: e reads a little lower, and ne and n a little steeper.
- The rhino as installed (`rhino_installed_*`) pops hard on every walk start and stop.
  - Its tilted idle back view stands about 1.6 times taller than the old upright walk.
  - This is expected while the walk and moves are still at the old angle.
- The gorilla's 35-degree set (fleet lane, `ape35_*`, run with `--who=ape`) turns a full circle with no pops.
  - Its drawings are 77 to 79 px tall in every view (approved: 70 to 72).
  - The side view shows the top of the back like its neighbours.
  - It is whole against the tower and the wall.
  - Rerun at 21:23 after the extra arm was removed from ne, with the same result.
  - At game size, the se visor reads small: a few pixels at the head's edge.
  - The far feet sit above the contact shadow rather than on it, the floating look the camera-angles lane is fixing.
  - Its bar clears at 1.9 m from the player's spot outward and needs 2.4 m in the worst case.
  - Its views are on a 160 canvas, but the game's ape sheet uses 192 cells (size scale 1.0). Packing them into 192 cells keeps its body radius and bar where they are.
  - Take 2 (Preston: "Reads from above"; `ape35_take2_*`) also turns with no pops: s 83, se 88, e 89, ne 85, n 84 px, with steps of 5 px at most.
    - Its bar needs 2.0 m from the player's spot outward and 2.6 m in the worst case.
    - Packed into 192 cells, its tilted bar sits at 2.3 m and clears. Packed at 160, it would drop to 1.92 m and sit on its head.
- Correction: while adding the tilt, I removed the line that made upright sprites turn to face the camera. From about 20:45 to 21:11 on 2026-11-04, upright machines went edge-on when the camera turned.
  - The line is back, and tilt_check now checks for it.
  - Clips from that window show the bug only in their upright panels during turns; boards and tilted panels are unaffected.
- Bars:
  - Over a machine whose frames carry `tilt_anims`, the HUD bar sits at `MACHINE_BAR_TILTED` = 2.3 m (times size scale).
  - 2.3 m clears every view from the player's spot outward.
  - A machine well below the player on screen would need 2.9 m.

- The fennec's 35-degree set (take B, `fennec35_*`) turns with no break, but it grows as it turns away.
  - Drawing heights: s 63, se 68, e 68, ne 76, n 82 px. The approved set is 72 to 77.
  - se to e is even. e to ne is the biggest step (+8 px), and the tail goes from lying flat to angled down, which shows on the turn.
  - Preston accepted the growth ("Looks fine, keep it", via the fleet lane).
  - The eyes were hard to see in s and se. The fleet lane has since repainted them, which I haven't checked at game size yet.
  - Its bar clears at 1.5 m from the player's spot outward and needs 2.1 m in the worst case. The HUD's tilted bar for an S machine is 2.3 x 0.8 = 1.84 m.

## Fennec blink gate, slot 2 (2026-11-04)
Preston: "Build blink gate", the first slice of the Janus kit in `docs/plan/moba-kits.md`. The code is in `scripts/moba3d/fennec_kit.gd`.
- To play it: open arena_play, press Tab twice to reach the fennec, then press 2 to blink. Press 2 again inside the window to snap back through the gate.
- It blinks toward the facing and leaves a gate at the start. The blink is a wall-sliding shape cast, so it stops on the near side of a wall.
- In a match, the cooldown starts with the blink, and the recast skips it.
- Bots blink toward an enemy within 4 m and snap back after 1.5 s.
- The HUD names slot 2 "blink gate". Ear burst stays as a function for the reveal and fennec3d_check, with no key.
- Placeholders: range 4 m, window 3 s, bot snap back after 1.5 s. The cooldown tier, short-medium, comes from MatchRules.
- The gate is a plain cyan ring with no art. The blink shows as two dust puffs.
- Check: `tools/debug/blink_gate_check.gd`, 14/14 passing. Clip: `blink_gate/blink_gate_2026-11-04.mp4`, made by `tools/debug/blink_gate_shot.gd`.

## Steep ult camera and the tilt shader (2026-11-04)
- At 70 and 85 degrees, tilted sprites vanished: the depth push of t x tan(pitch) went past the camera.
- The shader now caps the slope at tan 55 and holds the push to 80% of the distance to the camera.
- The camera-angles lane's rerun, as heights against the same view at 30 degrees:
  - 70: 87 to 92%.
  - 85: 85 to 92%.
  - 55: unchanged, 91 to 95%.
- By that lane's eye, 70 starts to read as a standee and 85 clearly does.
- **Preston's decision (2026-11-04, via the hub): "55 to 60, no new art".** Any ult that lifts the camera rises to 55 to 60 degrees, with tilt on, using today's 35-degree drawings. The falcon's sky barrage is the obvious one. Nothing is built yet.
- Sheet: `cam_angle_test/rhino_ult_rise_shaderfix_sheet_2026-11-04.png`.
- The camera-angles lane keeps its own notes (plant fix, contact shadow, ult rise) in its own file in `cam_angle_test/`, not here.

## Existing issue: camera behind the base wall
When the camera turns to the far side of the base wall, the camera clamp holds it behind the wall. The machine is then out of sight. This happens with today's upright sprites too. It's noted only; nothing will be done unless Preston asks.

## What is in
- Waves: drone minions every 30 s, walking the lane on the nav mesh.
- Towers: they target minions first and switch to a machine that hits an ally under the tower. When a tower aims at you there's a red beam, a ring at your feet, and "TOWER TARGETING YOU".
- Cores: a core can only be hit after its tower falls. Win or lose screen.
- Four jungle camps: they fight back, leash at 10 m and respawn after 60 s.
- Death and base: a respawn timer, healing at base, and a 4 s recall.
- Bots: they follow the wave and use their kits.
- HUD: health bars, cooldowns, kill feed, and tower and core health.
- Sound: signals use the sound lane's names. The sound in the video is theirs.

## Placeholders (all of them)
- Every number is in `scripts/moba3d/match_rules.gd`, each with its source.
- The drone is the sprite factory's placeholder design.
- Camp monsters are an olive stand-in.
- The side pit is only a marker labelled "open choice 4".
- The HUD uses flat bars and the default font.
- The basic attack is a stand-in shot.

## Not verified
- Whether a full 3 v 3 match with nobody held back ends inside a sensible time.

## Checks (headless, all pass)
- match_check: 67/67, including 8 body collision checks and 8 fog checks
- arena_check, rhino3d_check, ape3d_check, fennec3d_check: 0 failures each
- check_map_audio and check_kit_audio: PASS

## Wolf take B at 35, turn test (2026-11-04)

Asked by the wolf lane; Preston chose "Turn test, then fix". The wolf has no game frames yet, so the test builds idle frames from a views folder (`frames_of` in `cam_angle_test.gd`); KINDS "wolf" points at `wolf_m/take-b/fixed` as the upright comparison. Size M, canvas 192, feet edge 161 (same as approved, no VIEW_CANVAS entry), body radius 0.72 m, bar 1.71 m.

- Board `cam_angle_test/wolf35_board_2026-11-04.png`, turn clip `wolf35_turn_2026-11-04.mp4`, swap frames `wolf35_swaps_2026-11-04.png` (frame before and after each of the eight view changes, tilted above, approved below).
- Verdict: passes, no pop. The feet stay on the shadow at all eight swaps, and the head and tail stay on their sides.
- The e/ne step (58 to 91 px; it shows at the w/nw and ne/e swaps) is the biggest change in the circle and is visible on the swap frame. It reads as the body turning into depth, not a jump. A box the wolf's size (n minus e = 38 px = (L - W) x sin 35, so L is about 102 with W 36) gives 58 - 36 x sin 35 + 0.707 x 138 x sin 35 = about 93 px at ne; ne is 91. It is the same front-to-back growth Preston accepted on the fennec.
- Soft spot, not blocking: se (72) is short of the same estimate. Allowing for the head's height (n 96 vs s 85), se would sit at about 80 to 93, so it is roughly 8 to 20 px short. That is why the step gathers at e/ne instead of spreading over se/e too. If he wants a smoother turn, raise se; don't lower ne.
- Bar: the run log puts today's tilted HUD bar (2.3 x 0.9 = 2.07 m) above the art from the player's spot outward (1.95 m needed there). Clearing a drone 4 m nearer would take 2.55 m.
- Known flaw, visible at game size: the cyan pixel on the ne ear tip (row 71). The wolf lane removes it; the outline and heights don't change.

## Rhino walk at 35, installed turn test (2026-11-04)

The animation lane packed the 35-degree walk (`tilt_anims` = ["idle", "walk"]). Run: `--cam-angle-set-test --who=rhino --drone-views=installed`, which ends its clip with 1 s of walk (n view). The test gained a floor check for installed frames (`_walk_feet` in `cam_angle_set_test.gd`): every walk frame at every drawn view, captured four ways (everything, everything but the machine, the machine alone, nothing). A pixel the machine draws alone but that doesn't change the full scene is hidden by the floor. The floor (`arena_blockout.gd`, "Floor" under the arena's root) is hidden in the last two captures.

- Idle to walk: the tilt jump is gone. The quad stays tilted through the switch (clip frames 239/240 and 269/270), and height, feet and outline hold. One drawing difference shows: the n back plate is lighter and flatter in walk_n than in idle_n, so the back flickers lighter as it starts and stops. Passed to the animation lane; not a tilt issue.
- Toes below the pivot (s/n to row 163, se/ne to 162): 0 machine pixels hidden by the floor in all 40 walk frames (5 views x 8), checked from 60 px above to 79 px below the anchor. They don't sink. The shader's interpolated depth keeps the feet row about 0.3 to 0.4 m nearer than the anchor, so a few rows below it still draw in front of the floor.
- Pace: the test walks in place at the frames' 8 fps, so it doesn't judge stride against ground speed. At the 3.5 m/s placeholder, full_speed_walk_rate = 3.5 / 0.48 = 7.3x the drawn rate. That stays Preston's call with the move speed.
- Files in `cam_angle_test/`: `rhino35_walk_installed_board_2026-11-04.png`, `rhino35_walk_installed_turn_2026-11-04.mp4`, `rhino35_walk_feet_2026-11-04.png`, `rhino35_idle_walk_switch_2026-11-04.png`.

## Paused (2026-11-04, end of day)

Game feel lane paused on the hub's relay of Preston's "pause everybody for now". Nothing was cut off mid-run; the wolf and rhino walk results above are complete and reported. Open items when work resumes:
- Wolf: install its frames (the turn test used the views folder), then rerun the test with `--drone-views=installed`.
- Rhino: stride vs ground speed (7.3x at the 3.5 m/s placeholder) waits on Preston's move speed. The back-plate shading: the animation lane found the walk used the pre-touch-up colours (all five views), repacked it with the touch-up colours (walk35_touchup.py; rhino3d_check 0 failures). My in-game recheck of the idle-to-walk switch at n is held for the pause; run the installed rhino turn test again when work resumes.
- Bar: the tilted HUD bar (2.3 x size scale) clears from the player's spot outward, but not for a drone a few metres nearer.

## Resumed 2026-11-05: hippo take B at 35, turn test

Pause lifted (hub, Preston: "alright im back you can unpause everyone"). Asked by the wolf/fleet lane; Preston said "Turn test, then accept". KINDS "hippo" builds the upright comparison from `hippo_l/take-b/views` (capped ink; no installed frames yet). Size L, canvas 192, feet edge 161, radius 0.8 m, bar 1.9 m.
- Files in `cam_angle_test/`: `hippo35_board_2026-11-05.png`, `hippo35_swaps_2026-11-05.png`, `hippo35_turn_2026-11-05.mp4`.
- Verdict: passes, no pop, so the hippo is accepted. The feet stay on the shadow at all eight swaps, the top stays in front of the tower and the wall, and the HUD's tilted bar (2.3 m) clears from the player's spot outward (2.15 m needed).
- The e/ne step (71 to 99, 28 px) reads as the body turning into depth, like the wolf's 33 px, which passed. se (88) held this time.
- Soft spot, not blocking: e is 110 long against the approved 123 (89%) and 71 tall against the lane's 82 guide. At guide size the e/ne step would be about 17 px.

## Drone rebuilt at 35, installed, in game (2026-11-05)

Hub's ask: the drone rebuilt on its 35 views with tilt on all five animations (`tilt_anims` = idle, walk, attack, hit, death; Preston: "Yes, rebuild drone", "Keep as is"). Run: `--who=drone --drone-views=installed`. The test gained an actions clip for installed frames (`_actions_clip` in `cam_angle_set_test.gd`): each action in tilt_anims beyond idle and walk, played once at every drawn view, camera still.
- Files in `cam_angle_test/`: `drone35_rebuilt_board_2026-11-05.png`, `drone35_rebuilt_turn_2026-11-05.mp4` (turn plus 1 s of walk), `drone35_rebuilt_actions_2026-11-05.png` (start, middle and end of each action per view), `drone35_rebuilt_actions_2026-11-05.mp4` (labelled).
- Reads well. All five animations stay on the tilted quad: no size or position jump between idle and any action, and the top stays in front of the tower and the base wall. The floor hides 0 drone pixels across its 20 walk frames.
- Hit opens with a full white flash frame; death rolls the drone onto its side and holds there. Attack shows only as the eye brightening, which is small at game size (a drawing note for its lane, not a tilt issue).
- The test's raised bar is 1.55 m; today's 1.3 m (red outline) also clears the dome at the player's spot. In the wall clip the bar overlaps by 39 px at some frames, which is the known camera-behind-the-base-wall issue, not the drone.

## Rhino walk recolour, rerun (2026-11-05)

After the animation lane gave the walk the touch-up colours (`walk35_touchup.py`), the installed rerun shows idle_n and walk_n with the same back-plate shading through the switch (clip frames 238 to 241 and 268 to 271). The flicker is gone, and the floor still hides 0 pixels across the 40 walk frames. Files: `rhino35_idle_walk_switch_recolour_2026-11-05.png`, `rhino35_walk_recolour_turn_2026-11-05.mp4`.

## Kangaroo cam35 take 2 (fixed), turn test (2026-11-05)

Asked by the fleet lane after Preston picked "Free fixes first"; Preston said "Yes, run it". Views: `kangaroo_m/take-a/cam35/take2/fixed/` (eyes 2+2 px, one despeckle). KINDS "kangaroo" builds the upright comparison from `kangaroo_m/take-a/fixed` (the approved views' touch-up). Size M, canvas 160, feet edge 141. Radius 0.45 m (long side of the 69 x 55 footprint, the wolf's rule: 0.72 x 69 / 110), look 0.8 m, bar 1.71 m (the wolf's).
- Files in `cam_angle_test/`: `kangaroo35_board_2026-11-05.png`, `kangaroo35_swaps_2026-11-05.png`, `kangaroo35_turn_2026-11-05.mp4`.
- Verdict: passes. All 8 view swaps in a full turn change the picture by about the same amount (14.8 to 16.5 mean px difference; se/e 15.4, e/ne 15.3), and the feet row holds at each. e (77 tall against the guide's 83) reads as the side view turning into depth, not a pop.
- Correction: I first reported that the head turns away early because e showed no eye. Wrong: the eye renders (9 eye-glow px on the tilted e cell, 8 on the upright), I missed it in a downscaled strip. The fleet lane caught it. No soft spot.
- Bar: from the player's spot outward the tilted bar needs 1.70 m; the HUD's tilted bar for an M (2.3 x 0.9 = 2.07 m) clears it. At the wall spot the bar sits on the art (-20.6 px), as for the other machines. Every drone distance tested (4 m nearer to 14 m farther) would need 2.35 m.

## Match HUD handed to the map lane (2026-11-05)

Preston picked "Map lane takes it": the map lane owns the whole match HUD, `scripts/moba3d/match_hud.gd` included, for the SMITE-style rethink. This lane no longer edits it. Keep `BARS` in `cam_angle_set_test.gd` in step with any bar change the map lane makes. Notes handed over: `docs/plan/hud-notes-game-feel-2026-11-05.md`.

## Aim at the mouse (2026-11-05)

Preston: "fix battle camera and that feel as well... hold multiple movement keys... to point ne nw etc then hit one of my abilites", then picked "B: aim at the mouse" (the camera keeps its angle; the camera lane keeps the camera). Built in `machine_test_player.gd` only, no kit changed:
- An ability key (1-5) turns the machine to the aim point in `_input`, which runs before the kits' `_unhandled_key_input`, so every kit fires along the aim. A slot on cooldown, a busy or stunned machine and bots don't turn. The sprite switches view on the press, so the cast starts in the aim's view.
- Aim point: the mouse cast from the current camera onto the floor at the feet; a gamepad's right stick wins when pushed (6 m out). `aim_point()`, `aim_dir()`; checks set `aim_screen_override`.
- For 0.4 s after a cast (`aim_face_time`) walking doesn't turn the machine back; it walks where the keys say (movement now uses the key direction, not facing).
- A plain ring at the aim point and a faint line out to it, player only. Placeholder look; the HUD's look is the map lane's.
- Check: `tools/debug/aim_check.gd` (rhino, key 1 at four points around it): facing error 0.0 deg at all four, views e, n, w (e mirrored), se, horn toss cast each time. Board: `aim/aim_check_2026-11-05.png`.
- Not checked: the real mouse path (the check stands in for it), a gamepad, how a walk-while-aiming looks. Not built: per-ability shapes on a held key with cast on release.
- Backup: `D:\dev\_scratch\game_feel\machine_test_player.gd.bak_2026-11-05`.

## Gorilla tilted walk, foot-swap check (2026-11-05)
After the animation lane packed the gorilla's 35-degree idle and walk, `tools/debug/walk_turn_check.gd -- --who=ape` turned it a full circle while walking. Result: 3 mirror flips, 0 foot swaps (ne mirrored at frame 5, s at frame 0, e mirrored at frame 0, physical step unchanged each time). The `_plant` errors in the log are the known no-camera noise. Not checked: how it looks in the arena. Flip frames: `D:\dev\_scratch\game_feel\walk_turn_ape_tilt_2026-11-05\`.


## Rhino kit feel: dash toss and tremor (2026-11-05)
Preston: rhino 1 "a short dash forward then pluck back", "feels plain and can't really feel the move", and the ground move "a bigger circle like cabrakan where its stomping on the ground trembling and slowing those in the circle".
- Key 1, `scripts/moba3d/rhino_kit.gd`: a 0.15 s head-down, then a 3.5 m dash at 14 m/s. The first target within 1.6 m in front is caught, the flick frame holds 0.08 s (hitstop), and it is thrown 3 m behind the rhino, stunned. A miss runs the full dash and flicks at the air.
- Key 2: the slam at 0.7 s (the art's wind-up), then 4 stomps every 0.4 s in place (frames 5 then 4, timed in code), over a 4 m circle (was 2.2). Everyone inside is slowed while it lasts plus 0.8 s. One damaging hit, on the slam. The rhino is rooted about 2.8 s. The stampede finale is unchanged, one stun slam.
- Feel, `scripts/moba3d/kit_feel.gd` (new): camera shake on the kits' impact signal through the camera's h_offset/v_offset, which nothing else sets. That works under chase_camera_3d.gd without editing it. Only the player's own machine shakes it. Strengths: catch 0.5, landing 0.4, slam 0.7, stomp 0.35, finale 1.0 (up to about 7 px). A flat ground ring runs out to the 4 m edge on each stomp; the gp_ring art only reaches about 0.8 m.
- Before this nothing listened to impact for the camera, so no ability shook the screen.
- Check: `tools/debug/rhino_feel_check.gd` (field_test). Catch at 0.40 s after 3.27 m, dummy lands 3.0 m behind, stunned. Miss runs 3.50 m. Tremor slows the dummies at 1.5 and 3.5 m for 2.6 s and not the one at 5.0 m. Stomps 0.43 s apart. rhino3d_check 0 failures and match_check 67/67, after both checks were made to wait for the longer pound.
- Clip: `docs/art/moba/match/rhino_feel/rhino_dash_toss_and_tremor_2026-11-05.mp4`.
- Not checked: how it feels with a mouse and keys in hand, and the stomp thud sound (only the first slam has one).

## Tilted machines vanished in the match (2026-11-05)
The match builds its bots with duplicate() from the player, which copied the player's tilted ShaderMaterial by reference. Every tilted copy then drew from whichever sheet synced last, so the player's rhino drew the fennec's sheet and disappeared. Found by the map lane. `directional_sprite_3d.gd` now makes and keeps its own material per sprite. Probe: the rhino uses rhino_kit_sheet.png and the gorilla ape_sheet.png, and the rhino draws at spawn. rhino3d, ape3d and fennec3d checks: 0 failures.

## Basic attacks and the shared kit API (2026-11-05)
Preston: "we need basic attacks. Rhino, gorilla will be melee", and the mech sessions build their own. The hook, in the shared code:
- A kit defines `func basic_attack(target: Node3D) -> bool`, plus optional `basic_cooldown` and `basic_range` (edge to edge, `MatchTeams.edge_distance`). Space and left click go through `arena_play.player_attack` to `director.basic_attack(player, null)`; the kit aims with `player.aim_dir()`. Bots call `director.basic_attack(m, target)` after walking to `basic_range_of(m) - 0.4`. The director keeps the gates and sets `attack_cd`. A kit without one keeps the stand-in shot.
- Damage: `target.hit(by, damage / MatchRules.kit_hit_damage)`; minions, dummies and machines take the scale.
- Also added for the kits: `heal(amount, by)` with a `healed` signal, `boost(mult, t, key)` speed boosts that stack by key and clear on respawn, `move_dir()`, and the beacon hook (a taken beacon switches the other team's tower off for `MatchRules.beacon_tower_off`, 30 s).
- Kits with a basic so far: ape, falcon, fennec, hippo, hummingbird, rhino, shoebill, squirrel, wolf.
- `machine_kind` names: rhino (default), gorilla, fennec, wolf, kangaroo, squirrel, hippo, shoebill. The falcon and hummingbird kits have no class_name, so they read as "rhino" and their TIERS rows go unused until they get one.
- Tab in arena_play: rhino, gorilla, fennec, wolf, squirrel. Swap treats a kit without `current` as idle and puts the starting canvas back before each install (the rhino after the squirrel drew at 0.83).
- Checks: `tools/debug/kit_api_check.gd` 0 failures, `tools/debug/beacon_hook_check.gd` 8/8, match_check 67/67.
- Waiting on Preston: which of kangaroo, hummingbird, shoebill, falcon and hippo go into the match.

## Lobster take-g, 35-degree views turn test (2026-11-05)
For the lobster session: `--cam-angle-set-test --who=lobster --drone-views=res://docs/art/moba/lobster_l/take-g/views_cam35`, windowed at 30 fps.
- Views s, se, e, ne, n on a 192 canvas, feet on row 160 in all five. Art heights 105, 95, 70, 96, 106 rows, so the turn drops 25 rows into e and climbs 26 out of it.
- View swaps: not measured. Correction, same day: the swap figures first given here (five jumps of 10.9 to 12.3) came from the board script's 2x2 composite frames, which I had written into `floor_tilted` by passing it as the clip output folder, so the crop sat where the four panels meet. On the raw frames the camera and floor move across the whole frame and the walk cycle makes the biggest jumps (every 15 frames), so a frame difference can't single out the swaps. The view heights and the bar numbers come from the view PNGs and the test log and stand. The labelled 2x2 clip is now in `lobster35\clip`.
- HP bar: at the test's 1.9 m, the upright drawing clears it by 77.7 px, but the tilted drawing runs into it. From the player's spot outward a tilted lobster needs the bar at 2.3 m; the test raised it to 2.9 m to clear at every drone distance. The tilted art leans back 1.06 m at its tallest view.
- Board: `D:\dev\_scratch\game_feel\lobster35\board_lobster35.png`. Clip: `lobster35\clip`. Log: `lobster35\log.txt`.
- Not checked: how the turn looks to a person, and the west views (they fall back on the approved take-g views).

## Hummingbird into the match (2026-11-06)
Preston, in the hummingbird session: "Yes, into the match". Wired in the shared code; the team rosters are unchanged (no slot was named).
- Tab: rhino, gorilla, fennec, wolf, squirrel, hummingbird. `machine_kind` reads "hummingbird" from the kit's script path (the kit has no class_name). The director can build a hummingbird bot (`_make_bot(team, "hummingbird", i)`), but no roster names one yet.
- Draws at size S on its own 160 canvas, feet row 153 (hover gap), not tilted, so it sits at the old low angle beside the 35-degree machines until the hover redraw. Known and accepted.
- Space: its basic, 6 m, 0.9 s, through the director. Key 1: needle. Keys 2-4 aren't built. Bots would only use the basic: match_bot's PLAN has no hummingbird row and the needle needs the bot to face its target first.
- Probe `D:\dev\_scratch\game_feel\probe\hummingbird_tab_probe.gd`: 10/10 (Tab, kind, draw, reach and cooldown, tiers, Space hit, red bot, Tab round to the rhino with its 192 / 161 canvas back). kit_api_check 0 failures, match_check 67/67, fennec3d 0 failures.

## Lobster into the match (2026-11-06)
Preston, in the lobster session: "Yes, install it". Same wiring as the hummingbird, loaded by path (LobsterKit is new to the class cache); rosters unchanged.
- Tab: rhino, gorilla, fennec, wolf, squirrel, hummingbird, lobster. `machine_kind` reads "lobster" from the script path. `_make_bot(team, "lobster", i)` builds one; no roster names it.
- Size L, canvas 192, feet row 161; the HP bar at 2.3 m, as the 35-degree turn test asked. Walk is the still for now, so it glides.
- Space: the lobster's claw snap (melee, 2.0 m, 1.1 s), through the director. No abilities, no `current` (so bots only use the basic) and no TIERS row (slots would fall back on medium).
- Probe `D:\dev\_scratch\game_feel\probe\lobster_tab_probe.gd`: 9 pass, 1 expected fail (written before the claw landed, it still expects the stand-in; the hit it logged was the claw). kit_api_check 0 failures, match_check 67/67, fennec3d 0, lobster_frames_check 0 fail.

## Chameleon take-b, 35-degree views turn test (2026-11-06)
Preston picked "Lens fix, then turn test". `--cam-angle-set-test --who=chameleon --drone-views=res://docs/art/moba/chameleon_m/take-b/cam35/fixed`, windowed at 30 fps; new rows in cam_angle_test (approved take-b views, canvas 160, feet 141, M) and cam_angle_set_test (bar 1.71 m, radius 0.6 m, which is a guess until the kit exists, look 0.8).
- Feet on row 140 in all five views of both sets. Heights, 35-degree fixed: s 78, se 76, e 51, ne 76, n 79 rows (25 down into e and 25 back up). The approved low-camera views: 65, 62, 59, 62, 63, so e is 14% shorter than approved and the rest are 17-23% taller.
- HP bar: at 1.71 m the upright art clears it by 71.2 px; from the player's spot outward the tilted art needs 1.70 m, so 1.71 just clears there. Over the whole drone range it needs 2.25 m. The tilted art leans back 0.71 m at its tallest view. Turn clips: smallest bar gap 55.3 px on the floor and at the tower; -11.4 px at the wall spot, as for the other machines there.
- View swaps not measured (see the lobster entry: a frame difference can't single them out). Board `D:\dev\_scratch\game_feel\chameleon35\board_chameleon35.png`, labelled clip `chameleon35\clip`, log `chameleon35\log.txt`.
