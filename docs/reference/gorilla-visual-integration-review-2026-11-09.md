# Gorilla visual integration review — 2026-11-09

Playable, isolated visual review in the existing industrial arena. Main match registration is unchanged. Art approval remains separate from passing technical checks.

## Watch / play

- `gorilla-visual-review.mp4`: native Godot 1280×720, 30 fps, about 38 seconds; body-only and effects-on basic chain, self/ally shield, Drive hit/miss, grab-slam quarter view and body-only side view, chest-beat/cage and interrupted casts.
- `grab-slam-half-speed.mp4`: uniform 0.5× replay of the same native quarter-view footage, including its sound; no interpolation or alternate motion.
- Double-click `launch-review.cmd`. WASD, hold LMB basics, 1 shield, 2 grab-slam, 3 Shield Drive, 4 chest-beat/cage, F visual-effects toggle, I interrupt, R reset, right-drag camera, Esc close. Starts with the training enemy in reach. Aim toward it for the two-body grab. This is a review arena, not a multiplayer/balance implementation.

## What is wired

Review body adapter explicitly maps existing clips. Actual ApeKit runs the alternating basics/third slam, self/ally shield and cage rules. Review-owned subclass adds interruption guards to the chest-beat staging and replaces its legacy sprite impact puff. Existing shape-following HexShield is reused. A review-owned copy of its dome shader reduces dense cell opacity and uses larger cells so the fight remains visible; shared shader is unchanged. Damage, panel health, shield duration and other existing provisional numbers are not retuned here.

Selected local Shield Drive and grab-slam controllers are used unchanged. Drive goes brace > travel > collision or brake. Actual collision triggers one contact effect/sound. Grab/Fling preserves the lunge/lift opening, holds the articulated target, then drives it down: grab 0.18 s, ground impact 0.60 s, finish 1.00 s plus local impact hold. This does not use the old backward toss. The original opening through 0.325 s remains intact. No release-frame change was adopted from Gemini's unverified measurements.

Small mesh hex outlines/chips and brief material emission pulses reinforce confirmed contacts. They do not replace skeletal movement. Basic contact FX are driven by actual target damage, not an animation event that can miss. Shield-up occurs after the real shield exists. Chest sounds follow the four authored chest contacts; the three kit stages remain at 0.42, 0.75, 1.27 seconds, and the cage appears at the final ground contact. Body-only takes suppress the added effects/audio while keeping actual damage.

## Assets and ownership

Review code: `D:/dev/new-mech-rpg/tools/debug/gorilla_visual_review_2026_11_09/`.

`review-model.glb` is a hash-identical copy of the existing grab-slam trial GLB. No geometry, weights, proportions, armor, eye textures, material source assets, rest bones or animation curves were changed in this pass. Source Blender/export reports remain under `D:/dev/_scratch/gorilla/codex-grab-slam-trial-2026-11-09/`. Previous trials remain intact. No paid generation, donor download or external model upload was performed.

Shared `ape_kit.gd`, `mech_model_3d.gd`, `hex_shield.gd` and `kit_audio.gd` hashes match `shared-files-before.json`. Review subclass/material copies keep these changes out of other owners' paths.

## Validation

- `integration-15fps.json`, `integration-60fps.json`, `integration-120fps.json`: all 21 functional checks pass at each rate. Includes pre-contact basic interruption; shield before/after release; actual ally shield; pre-cage interruption; grab before/after capture; exact attachment and floor settling; once-only slam damage; control release; misses; Drive brace interruption and real StaticBody3D wall stop with shield-front clearance; body-only retains damage and suppresses contact effects.
- `native-results.json` and `verification.json`: 24 recorded event/source preservation checks pass. Three-hit chain remains 28/28/42. One Drive hit, one grab impact, no false miss contacts, four chest contacts before one cage, no interrupted irreversible casts. The native grab ground event samples exactly 0.60 s. Standard body events are polled on rendered frames, so release/beat timestamps may be up to one frame after their source threshold.
- Godot Movie Maker used NVIDIA GTX 1660 SUPER/OpenGL and recorded around real time. Final lift, contact and calm-cage PNGs were inspected. FFmpeg encoded H.264/AAC and created the uniform half-speed excerpt.

## Limits / next review

The training victim is a controlled articulated mannequin, not a general physics ragdoll or a complete enemy animation system. An interrupted held victim uses the existing safe prone fallback. Existing armor/casing intersections are not certified clear by these checks. Direct rear game camera can hide close two-body contact, so quarter and side diagnostic views accompany it. Existing cage healing/taunt/panel numbers remain proposals in shared gameplay code, not approved balance.

Native Movie Maker finishes with 48 ObjectDB / 14 resources-in-use shutdown warnings, retained in `native.log`; it has no script errors and the capture completes. Some headless runs also print the environment certificate-store warning. These are not a production-clean certification. Review input uses a single training target and does not implement final targeting/network authority. Main match still uses its existing registered model/old Fling route until a separately reviewed integration replaces it.

Consulted the corrected Gemini `REVIEW.md` on 2026-11-09. Retained phase/contact/support/preservation guidance; did not adopt unsupported millimeter clearances, gait schedules, two-frame release changes, zero-penetration certification or incorrect Godot API suggestions.

## Subsequent donor decision

The separately authorized single Meshy Prime test completed for 10 credits and was rejected after raw and arm-only-fit review. See `docs/reference/gemini-animation-research-2026-11-09/MESHY_TRIAL_RESULT.md`. It did not provide a better protective cast; no donor curves, runtime export or event changes are adopted here. Keep the authored cast and 0.25-second release. No further paid generation is authorized by that completed trial.
