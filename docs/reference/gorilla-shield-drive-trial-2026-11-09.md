# Shield Drive — isolated playable trial, 2026-11-09

Preston rejected Servo Overdrive as a quickened sprint without sufficient impact, then selected **Shield Drive**. This trial uses the accepted shield-cast source, not the rejected sprint asset. The old Overdrive experiment remains intact for provenance and is not the recommended final ability.

## Watch / play

`shield-drive-review.mp4` (22.61 s, 1280x720) shows a hit from the normal game camera, a side-view hit, a miss, first-enemy-only behavior and a wall stop. A half-speed replay of the same side-view take closes the video so the target does not obscure the gorilla. Native Godot Movie Maker AVI is retained; FFmpeg trims/concatenates and uniformly slows that side take and its audio. The native source also contains a front slow-motion shot, but the target occluded the body, so it was excluded from the delivered review. No generated motion, optical flow or external assets.

Run `launch-review.cmd`: **WASD** move, **3** aim toward the mouse and drive, **R** reset targets, right-drag existing chase camera, Escape closes. Training targets are explicit 3D practice pylons with real local HP, flash and displacement; they are not production enemy models. This preview is separate from the shared match.

Editable source: `shield-drive-trial.blend`; interchange: `shield-drive-trial.glb`. `build_shield_drive.py` builds four new actions while preserving the accepted model and all prior clips:

- Brace: 29/120 = 0.241667 s, load the hind legs and bring both shield-bearing arms forward.
- Drive: 38/120 = 0.316667 s, compact guarded low burst; hind feet briefly trail and lift rather than playing a fast walk.
- Hit: 50/120 = 0.416667 s, compression and knuckle plant, then settle.
- Brake: 43/120 = 0.358333 s, a miss/wall braking plant.

The pose presents a paired shield guard; the plates remain separate and do not interpenetrate or mechanically weld together. The initial close inward recovery clipped the thumbs into the body and was rejected. The retained recovery opens outward before lowering; it preserves the existing fists and mass rather than remodeling them.

## Ability behavior / draft values

Preview tuning, not approved balance: 12 m/s drive, maximum 3.8 m root travel, 24 damage to the first enemy, 0.70 m short shove, 0.055 s local contact hold. These values are confined to the isolated component; production ApeKit balance is unchanged. There is no area damage, repeated collision damage, added shield, stun, CC immunity, teleport or roll transformation. The new short shove does not replace Fling's larger relocation.

Direction commits on activation. Wind-up and travel cannot be cancelled by movement; after the plant, movement can cancel remaining recovery (0.27 s into Hit / 0.23 s into Brake). Stun/death interrupt and release ownership. Damage occurs at the continuous collision crossing, not at a guessed sprite frame or an unconditional animation timer. A per-drive latch ensures one hit. The target recoil waits for the same local contact hold. Existing activation/contact audio and directional camera kick are reused; no random camera shake or global time-scale change.

`drive_controller.gd` sweeps an oriented front span against the candidate enemy circles. Forward reach 1.29904 m is measured from the exported shield geometry; half-width 0.64 m is a conservative draft collision width, not triangle-exact collision. It stops at the first valid enemy. Existing MatchBodies and ArenaMotion remain in the path, with an additional leading shield probe so the forearm shields do not penetrate a wall before the body stops. Existing cage rules are respected with additional shield clearance. Broken panel gaps still use `blocks_at`. Team filters prevent ally damage.

The preview currently supplies its training-target candidates. Production kit input, cooldown/resource handling, live target acquisition, full hit-status contracts and 3D match spawning remain separate integration work. A newer MechModel3D path now exists and points at gorilla_kit_v26.glb; this trial does not migrate kits or claim complete production integration. No cooldown balance was invented here. Existing slow state is not cleared; this fixed-speed dash does not use walk-speed buffs/slow multipliers, and that gameplay policy remains a tuning decision rather than CC immunity.

## Preservation and checks

Base: `../codex-shield-cast-trial-2026-11-09/shield-cast-trial.blend`. Clean source/export checks preserve all original action curves, vertices, topology, UVs, weights, material assignments, rest bones and packed texture bytes. Approved eyes, palette, proportions, shields, Fling, swats and accepted synchronized chest-beat timing remain unchanged. No source archives, shared game files, other lane's models or paid tools were touched. Source remains 69 mesh objects / 34 bones; export has 18 actions. Blender adds its scratch Icosphere on import, hence its 70-object mesh count.

- `controller-validation.json`: 21 cases pass. 15/30/60/120 fps deltas with 0.5/1/1.75 time-scale multipliers all hit the first target once, deal 24, leave the second untouched and stop at the same 2.40096 m contact position. Additional cases cover miss, ally, off-axis, behind, stun/death during brace and travel, rejected restart and movement before commitment ends, and recovery cancellation without repeated damage.
- `collision-validation.json`: actual Player + world collision stops before a wall with no shield intrusion. Wall center 1.6 m / front face 1.5 m: root stops at 0.200781 m; shield front reaches approximately 1.49982 m. A radius-2 m same-team cage_all holds the root at radius 0.70096 m, leaving the measured shield front inside radius 2. Neither wall nor cage allows damage to an enemy beyond it.
- `review-results.json`: native hits deal 24 once and shove 0.700000 m; second target takes zero. Miss travels 3.800001 m, with zero damage. Wall stops before contact. Half-speed diagnostic target motion uses the same actor rate in the native source; delivered slow side is a uniform replay of the normal take.
- `export-validation.json`: all preserved fields pass. Maximum wrist bend is 15.97 degrees from its rest relation; no flip, and well within the earlier 40-degree bound. No left/right shield intersections across all 164 authored poses. No source IK reach clamps. Foot-tip patches during stationary brace/hit/brake remain within 0.000000893 m; rigid bone-length variation stays below 0.000000537 m. Drive intentionally lifts the feet and moves the body: those planted-contact figures do not describe travel, runtime facing pivots or uneven ground.
- Full-body clearance audit has nonempty mesh groups and 164 samples. No hand digit/thumb/palm, shield-cell/frame/backplate/mount crossings remain. Existing forearm casing/body seams still cross: peaks 317 left / 288 right triangle pairs. No penetration depth was measured. This is unresolved armor ownership/attachment cleanup, not a clean whole-model armor certification.

Viewed actual native game, side, plant and slow-contact frames plus source front/side poses. The motion visibly closes the arms into a forward guard, translates rapidly into contact, compresses, opens and plants. These observations and technical passes do not constitute Preston's artistic approval. Broad model proportions and all accepted original clips remain intact. The remaining visual risks are the forearm seams, the short render-only ground-skimming lift and blending when activating toward a sharply different facing; the recorded straight tests do not certify every turn or terrain case.

Reports and scripts are adjacent. Headless logs include the existing environment certificate warning and exit resource warnings; current tested scripts have no remaining parse/runtime failures. No commits, downloads, paid generation or external uploads.

