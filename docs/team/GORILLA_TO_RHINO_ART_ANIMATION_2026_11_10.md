# Gorilla → Rhino animation and spell-art handoff

Preston explicitly requested this handoff and asks Rhino Animation to make the same kind of move-art sheets for Rhino. This is knowledge transfer and a Rhino production request; Gorilla gameplay changes remain owned by the Gorilla chat.

## Art task to start now

Read Rhino's CURRENT kit, accepted model and donor/animation decisions first. Create original Rhino-specific ability art using the built-in image generator, using the imagegen skill. One coherent transparent atlas can hold several move components; separate frame sheets are only useful when an effect actually needs them. Inspect the result, preserve raw output and exact prompt, save final assets inside the project, then wire layers to real cast/contact/travel/recovery events and record in the industrial map. Do not stop at delivering an unused sheet. Preserve Rhino's accepted body, rig, proportions, locomotion and ability mechanics; art does not authorize a new kit or balance change.

Gorilla examples:
- `art/fx/gorilla/reactor-atlas-v1.png`, `reactor-atlas-v1-prompt.txt`, `README.md`.
- `scripts/moba3d/gorilla_painted_fx.gd`, `gorilla_targeting.gd`, `gorilla_targeting_overlay.gd`.
- `shaders/gorilla_painted_fx.gdshader`.
- `docs/art/moba/GORILLA_ABILITY_INDICATORS_2026_11_10.md`.
- `tools/debug/gorilla_targeting_2026_11_10/art_review.gd`, `art_run.gd`, `match_check.gd`, `launch-review.cmd`.
- Actual native recording: `D:/dev/_scratch/gorilla/ability-indicators-2026-11-10/painted-art.mp4` (our art, safe to show).

Preston's Instagram/Tripo reference: https://www.instagram.com/p/DbX99e5g6YK/ . Located in Mech Hub, then inspected through sampled frames of its public 35-second video. It shows image-derived spell circles/surface decoration assembled in Blender, a Tripo character workflow, then a finished scene with multiple animated spell-circle layers. Reuse the technique, not the video's imagery. Public research copy/frames are in the Gorilla scratch directory; do not redistribute them as project art. No Tripo generation was purchased or run.

Gorilla's atlas is 1774×887 RGBA, four columns/two rows, eight component textures: protective floor seal, fractured knuckle stamp, Drive crest, segmented ultimate perimeter, recipient crest, impact bloom, wake streaks, gate lock. Palette comes from the approved green/orange/silver Gorilla. Rhino should derive its own motifs from its horn/armor/reactor/accepted palette and each actual ability, not recolor Gorilla's shield honeycomb.

Use texture components as layers: scale, rotate, orient in 3D, assemble and dissolve. We combine ground decals and brief upright sigils, paint-driven UI selection crests, movement wakes and timed impact bursts. Readability comes before filling every available pixel with glow. Keep true gameplay boundaries legible and distinguish selection/valid/invalid/cast/contact/recovery. Invalid state needs shape/text feedback as well as color. The atlas has imperfect gutters/low-alpha haze: our shader fades cell edges and uses alpha^1.6 rather than destructively editing the PNG. Do not claim perfect isolated textures or zero bleed without inspecting at runtime. World-space sizes, negative space, alpha, UV orientation and small-camera readability all require native review.

## Animation lessons

SMITE 1 is Preston's main camera/combat-feel reference, Paragon secondary. Current shared camera defaults are distance 12 m, pitch 13°, look height 3.2 m; use actual current scene defaults rather than the older closer review camera. Record in the existing industrial map. Models were initially too large/slow; preserve accepted scale/speed and fix animation rather than reverting movement to disguise skating.

Use the actual skeleton. Meshy's SmartRig was a useful baseline. Preserve rest bones, skin weights, UVs, approved materials/silhouette and other clips. Gorilla's real data is 34 bones/69 skinned mesh nodes; Blender reimport can contain an extra helper mesh, so count actual GLB nodes too. Sprite anatomy mistakes motivated manual hands/feet/shields refinement; do not regenerate a good body to solve animation defects. Gorilla's approved eyes are painted solid green in their sockets, with no sticker eyes/eyebrow marks; that specific decision is not an instruction to change Rhino's face.

Measure actual visible support patches, bone/parent-child lengths, hand rotation and contact surfaces, not just bone-head positions. Lock support during planted phases and use plausible shoulder-centered hand arcs to avoid folded-IK singularities. Prepare wrist/knuckle orientation BEFORE impact, hold contact briefly, lift before recovery and match the ready pose at clip boundaries. Numeric checks do not replace full/half-speed visual inspection from front/side/game camera, including strafing and sharp turns. Armor-pair checks do not certify all armor/body clearance.

Gorilla compact finisher candidate: `D:/dev/_scratch/gorilla/combat-polish-2026-11-10/combat-polish.blend` and `.glb`, `build.py`, `export.py`, `validate.py`, `build-report.json`, `export-validation.json`; playable review `tools/debug/gorilla_combat_polish_2026_11_10/`. New clip `Gorilla_Slam_Compact_Trial` keeps .95 s duration and 50/120 s contact; all 19 old action curves/mesh/rest rig preserved. Rear support drift is below 1 µm, ready-pose seam zero, and max spine parent-child spacing change falls from about .188 m to below 1 µm. It is shorter-reaching/lower than the original. Preston liked it; production GLB had not been replaced during the art pass. Do not assume a scratch clip is registered live.

Play actual held basics/three-hit chain, moving casts and sharp reversals against real match units. Validate exact damage counts and event ordering at coarse and fine frame rates; hitstop, interruptions, death, walls, target loss, CC immunity and cleanup all matter. A pretty mannequin-only clip is insufficient. Make and inspect native Godot recordings with FFmpeg; deliver an inline video and a usable absolute-path fallback link because the user previously could not see clips. GPU capture/real-time MovieMaker is useful; avoid AI frame interpolation when evaluating timing.

## Cascadeur finding

Cascadeur Free's Python API does not unlock restricted export. Native .casc saves and FK pose edit/restore worked; generic control-rig assignment distorted support/helpers. Imported-baseline comparison was not a new physics improvement. It has been set aside in favor of the local Blender/Godot workflow. Do not restart a Cascadeur/license-bypass effort on the strength of that earlier trial.

## Current Gorilla gameplay status — IMPORTANT

The previous art pass passed 25 targeting checks, six art-event/lifetime checks and seven real-match checks. Those results apply to that completed version, not to the new rework below. Native exit resource warnings were intermittent; no full clean-shutdown certification was made.

Preston's NEW instruction (currently being implemented and NOT YET validated) is to merge Shield Drive and Grab Slam into ONE automatic Drive→takedown move, freeing a slot. Gorilla chat is prototyping Fault Line in slot 2: a short ground rupture/slow patch, while slot 3 owns Drive+Slam on one cooldown. Do not copy the old separate Grab slot or assume new code is tested. Do not edit Gorilla files during your Rhino work. Earlier diagnosis: .7 m shove plus .42 s recovery pushed targets out of 1.6 m grab selection; ability mechanics should complement each other. Do not add reach/stretch/teleport as a substitute for a proper transition.

## Tool/workflow constraints

**Later Gorilla update:** the merge/Fault Line prototype is now implemented. See `docs/plan/GORILLA_MERGED_KIT_2026_11_10.md` for exact scope and current checks. Twenty-five merged-move cases pass at 15/60 FPS, twelve actual-match cases pass, and the previous 25 input/targeting cases pass. This is a prototype kit direction, not an instruction to give Rhino the same mechanics. Your own Rhino art production is independent.

Built-in image generation is the authorized art route, not a separately billed external service. No purchases, paid Meshy/Tripo jobs, saved fal.ai credentials, commits or unrelated changes. Preserve raw prompts and sources. Godot engine executable: `C:/Users/pmcga/Games/Tools/Godot_v4.7.2/Godot_v4.7.2-stable_win64_console.exe`; Blender `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`; FFmpeg is installed via WinGet. Shared engine limit: ONE actual Godot process at a time (godot-ai MCP helpers do not count). Gorilla is actively implementing/testing now; begin with atlas/reference work and wait for an idle engine before native review. Headless editor imports can log blocked global help/settings-cache writes while workspace texture import succeeds; inspect the actual import result. Keep Rhino work in new Rhino-specific paths and consult its own latest guidance.
