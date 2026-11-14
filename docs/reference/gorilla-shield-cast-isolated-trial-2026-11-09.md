# Gorilla shield-cast isolated trial — 2026-11-09

This implements Preston's ally/self shield-cast trial approved in Mech Hub and handed to Mech Gorilla Animations. Read the Hub's recent turns (including “Thats it!” accepting the chest-beat exit), the actual user/assistant text in Claude gorilla session e6f19606-6979-4619-953d-11a8b9ee3717, and game-feel session 11ba832c-d1e6-4c20-856f-0202442642cb before building. Claude's latest v26/v27 revisions and failed review outcomes supersede this chat's older v16/v17 state. Do not treat earlier builder scores as independent approval.

## Watch and run

- `shield-cast-review.mp4`: 23.77 s, normal front/side, half-speed front, ally/self game-camera casts in the industry map. Body-only sections precede the existing effect.
- `ally-shield-gameplay.mp4` and `self-shield-gameplay.mp4`: shorter gameplay excerpts.
- Editable `shield-cast-trial.blend`; interchange `shield-cast-trial.glb`.
- `launch-review.cmd`: runs the isolated review using shared project resources, without editing production scenes, kits, shaders or models.

Two new clips: `Gorilla_Shield_Ally_CodexTrial` and `Gorilla_Shield_Self_CodexTrial`, each 0.60 s at 120 fps. Release key F30 = 0.25 s. These are presentation starting points, not balance changes. Small mass transfer toward the supporting right knuckle precedes the left forearm lift. Ally variant presents the shield outward; self variant draws it inward without turning. The approved bulk limits how far the shield can cross the chest without collision, so this pass guards the front quarter rather than forcing a narrow cross-body pose. There is no attack hitstop or camera shake.

## Source and preservation

Base is `../codex-chestbeat-trial-2026-11-09/exit-trial.blend`, preserving the approved synchronized exit after the last chest beat. All original action curves, mesh positions/topology/UV/weights/material assignments, rest bones and packed texture image bytes match that base. The accepted chest-beat clip remains 1.866667 s, with its original timings. No geometry or armor redesign, rig replacement, paid tools, downloaded assets, commits or changes to original archives.

`pre-export-validation.json`: 69 source mesh objects, 26,365 triangles, 34 bones, finite coordinates, no unweighted skinned vertices. No decimation or material merge was appropriate to this preservation-only trial; Claude's atlas/armor work remains separate.

Clean GLB reimport verifies 34 bones and all 14 clips. Blender's importer lists 70 mesh objects including its scratch Icosphere; the GLB scene contains the intended source mesh nodes. Exported right-knuckle digit contact patches and foot-tip patches move at most 0.0000007291 m during either cast. Maximum bone-length deviation is 0.0000005364 m; clip endpoints match exactly. Source IK records zero overreach clamps. These measurements cover stationary authored cast support, not moving recovery on uneven terrain. Baseline ground heights and original contact geometry remain unchanged.

## Event contract / actual existing behavior

`cast_controller.gd` adds an Animation method key at 0.25 s to a runtime duplicate of each imported clip. It advances the 3D player and uses a per-cast latch; there is no sprite-frame polling, wall-clock timer or frame-number equality check. Callback delivery is quantized to the playback tick that crosses the key (e.g. native 30 fps observed 0.266667 s); shield, slow cleanse and sound execute together in that callback. Replay/duplicate callback traversals cannot apply twice.

The preview reads the real ApeKit target picker and defaults without installing its sprite/aura hooks: nearest ally within 6.0 m, self fallback, shield life 3.0 s. It uses existing `ApeKit.shield_on` and `HexShield.shield`, ends a prior shield, clears `slowed`, and requests existing `audio/sfx/ape/shield_up.wav` once. An invalid selected ally at release receives no effect; there is no invented retarget rule. It preserves existing hex cells rising from the feet, activation flash, calm rim, expiration and shader ownership. No new overlay or replacement VFX.

Movement requests are denied before release; after release they crossfade to the existing Walk v25 and cannot release a second shield. An interruption before release grants no shield. Actual production input arbitration, stun/death hooks, cooldown routing and 3D match spawning remain separate work. Main match still spawns sprites; this trial does not change that.

## Tests and visual verdict

`event-validation.json`: 27 cases passed. Tested 15/30/60/120 fps animation deltas with 0.5/1/1.75 time-scale multipliers for ally and self, repeated method callback, blocked restart during commitment, nearest/in-range and 6.01 m out-of-range fallback, slow cleanse, unchanged 3 s duration, pre-release interruption, post-release movement cancellation, and selected target freed before release. These are sampled delta tests, not a claim of a benchmark at every real display rate. Each valid cast applies one effect and one sound request. Native review logs eight visual release events, with two actual effect applications and two activation sound requests in the two effect-enabled sections.

Viewed actual native front/game/calm frames and source front/side release poses, as well as the accepted chest-beat comparison. The body visibly shifts support, lifts one shield-bearing forearm, briefly presents it, and lowers it. Preston accepted the trial in Mech Gorilla Animations on 2026-11-09. Preserve this presentation and release contract. Acceptance does not close the separately documented armor intersections or promote it into the production match.

**Unresolved armor:** the first pass clipped the thumb into the head; that path was rejected. Current 146-pose audit finds no hand-digit/thumb or shield-cell/frame/backplate crossings with the body, but the forearm casing has 121 triangle-pair overlaps at the baseline seam and up to 247 during motion. The shield mount also has up to 10 pairs during recovery. Counts are triangle-pair crossings, not penetration depth. Do not call this a clean armor pass. Fixing rigid ownership/attachment seams belongs with the ongoing armor work; this trial preserves its source model instead of silently rebuilding it.

Reports/scripts are adjacent: `build_shield.py`, `render_audit.py`, `validate_export.py`, `build-report.json`, `clearance-audit.json`, `export-validation.json`, `test_events.gd`, `review-events.json`. Native video is deterministic Godot Movie Maker output encoded with FFmpeg, including existing activation audio. Headless logs contain the environment root-certificate warning and exit resource warnings; tested scripts have no remaining parse/runtime failures.

