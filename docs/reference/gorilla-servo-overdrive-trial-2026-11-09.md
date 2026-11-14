# Servo Overdrive — isolated playable trial, 2026-11-09

Preston selected the proposed steerable knuckle sprint (“Do it”). This preview replaces the old bound/pounce concept only inside its own test. No production kit, shared model, match-spawn path or other lane's files were edited. No downloads, paid generation, commits or external uploads.

## Watch / play

- `servo-overdrive-review.mp4`: 23.2 seconds, 1280x720, industry map. Shows normal walk → acceleration → sprint → walk; a steered right turn; side view; sprint cancelled into the accepted shield cast; existing slow and stun; and stationary body-only half-speed diagnosis. Native Godot Movie Maker capture, encoded with FFmpeg.
- Run `launch-review.cmd`. WASD moves; **3** activates Overdrive; **1** ends it and performs the accepted shield cast with its real HexShield effect and activation sound. LMB, 2 and 4 demonstrate cancelling into existing swat/Fling/chest-beat motion clips only; those three buttons do not simulate production damage, targeting or ult effects. Escape closes.
- Source: `overdrive-trial.blend`; interchange: `overdrive-trial.glb`; controls: `overdrive.gd`, `review.gd`, `contacts.gd`. Original model/animation sources remain untouched.

## Prototype behavior

A 2.0-second window, with 0.30-second acceleration and a short tapered tail, reaches **6.0 m/s** from the existing **3.5 m/s** base. These are draft presentation/game-feel values, not approved balance numbers. Fully steerable; no compulsory forward charge, collision attack, teleport, terrain crossing, added shield, damage, stun, cleanse or CC immunity. No cooldown balance was introduced in this isolated review.

The component refreshes a uniquely keyed boost through the existing player's boost API. Ending removes only that key, preserving other buffs, the base speed and existing slow calculation. Attack/ability requests can end it; shield cancellation is exercised with the accepted 3D release event. Stun/death end it and reject activation. Ordinary world/body/cage collision still runs through the existing player controller.

The design takes acceleration from Geb's Roll Out, while keeping free steering and grounded knuckle movement instead of his collision/CC package. Primary reference read: https://www.smitegame.com/gods/geb. Animal/machine gait is authored for our own proportions, not copied Geb curves. See the existing local Geb study for animation evidence. Applicable animation action cards, playbook and Blender asset/export guidance were used. Local Blender builds/audits, Godot exercises real movement and collision, FFmpeg packages evidence; no generation service is needed.

## Animation and preservation

Based on the accepted `../codex-shield-cast-trial-2026-11-09/shield-cast-trial.blend`, which retains the accepted synchronized chest-beat exit. Three new actions:

- `Gorilla_Overdrive_Sprint_Trial`: 50 frames / 120 fps = 0.416667 s. Shorter contact windows, stronger swings, lower front posture, small body counter-motion; exact loop closure. Draft hand duty 0.34, foot duty 0.20, stagger 0.15 cycle.
- `Gorilla_Overdrive_Ignition_Trial`: 0.216667 s, a planted compression used when stationary.
- `Gorilla_Overdrive_Settle_Trial`: 0.25 s, planted return. Moving entry/exit blends to the appropriate gait rather than forcing stationary anticipation.

All original action curves, source mesh vertices/topology/UV/weights/material assignments, rest bones and packed texture bytes are identical to the accepted base. The source remains 69 mesh objects and 34 bones. GLB clean reimport has all 17 actions; Blender's importer adds its scratch Icosphere in its object count. Approved eyes, palette, proportions, shields, idle, walk, swats, Fling, shield casts and chest-beat timing are preserved. No material atlas or armor redesign was attempted.

## Checks and limits

- `controller-validation.json`: 18 cases pass, spanning 15/30/60/120 fps deltas at 0.5/1/1.75 time-scale multipliers, expiration, repeated activation rejection, preservation of another buff, and shield/basic/Fling/ult/stun/death cancellations with one end event. These are component delta tests, not a display-performance benchmark.
- `collision-validation.json`: actual Player + existing ArenaMotion stops at a wall (player Z 0.69989 m before wall center 1.6 m). Existing same-team `cage_all` confines its center to radius 1.2 m in a radius-2 m cage with body radius 0.8 m. The test explicitly assigns a match team, because the field's unteamed player does not use match dome restrictions.
- Native review reaches 6.0 m/s. Existing slow reduces it to 3.6 m/s; stun ends it. Cancelling into the accepted shield generates one release event. `runtime-validation.json` and CSVs record this.
- Source IK reports zero overreach clamps. A clean-GLB straight-travel test at 6 m/s across two cycles samples 112,302 visible knuckle/toe patch points: maximum stance drift 0.000002179 m, bone-length change 0.0000005364 m; contact heights remain essentially zero. This does not certify turns, transitions or uneven ground.
- Runtime contact correction resets on clip changes, stops and review teleports. Native locked-anchor error peaks at 0.0002746 m. Released endpoints require up to 0.0177679 m projection during transitions; the 60 fps headless route peaked at 0.0349045 m. Limbs retain rigid length, but the transition still deserves visual refinement if it reads as a small foot correction. Do not equate locked-anchor metrics with zero sliding over the whole animation.
- Original armor attachment issues remain. The 109-pose full-body audit finds no digit/thumb/palm, shield-cell/frame/backplate crossings. Forearm casing/body crossings peak at 359 left / 360 right triangle pairs, and right mount at 7. These include existing attachment seams and grow in the lowered pose; they are unresolved, not a clean armor certification. No intersection depth was measured. Coordinate with the armor lane rather than silently reshaping the accepted body.

Inspected actual native sprint, turning and side-view frames before delivery. They show a faster low knuckle-bound with the existing mass and clear model silhouette. This is a first playable mobility review, not Preston's artistic approval or production 3D match integration. Full-speed and half-speed evidence is provided for judging weight and rhythm. Headless logs include the environment root-certificate warning and exit resource warnings; tested scripts have no remaining parse/runtime failures.
