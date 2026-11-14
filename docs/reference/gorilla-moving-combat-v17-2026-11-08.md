# Gorilla moving basic attack review v17 — 2026-11-08

Preston liked v16 as a jab, but questioned repeated jabs during held left click and strafing. This review establishes alternating compact left/right punches from a low raised guard, with independent combat footwork. Fists stay ready between held attacks; release blends back into knuckle-supported movement. SMITE remains primary; Paragon secondary. No heavier finisher or new combo/balance rule introduced.

## Assets and test

- Source/export: `art/model_catalog/workspaces/gorilla_moving_combat_v17.blend` and `.glb`.
- Interactive review: `tools/debug/gorilla_moving_combat_v17.tscn`; hold LMB or Space, move with WASD, release to return to normal movement. Existing mouse-ground aim and chase camera are used. Scripted recording fixes aim to demonstrate independent strafing.
- Runtime layers: `gorilla_moving_combat_v17.gd`, `gorilla_combat_feet_v17.gd`, `gorilla_quad_contacts_v17.gd` in `tools/debug`.
- Evidence/build scripts: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/`, particularly `build_combat_v17.py`, `v17/`, and `industry-combat-v17/`.
- Native industry-map recording: `industry-combat-v17/moving-combat-v17.mp4` (19 s, 1280x720).
- Close front loop: `v17/combat-loop-front-v17.mp4`.

Eleven clips: approved Idle v14 (7.6667 s), Walk v17 (0.6 s, original v12 walk), Ready (2 s), Enter/Exit (0.3 s each), Left/Right punches (0.6 s each), Forward/Back (0.4 s), StrafeLeft/StrafeRight (0.35 s). Punch contact is 22/120 s = 0.183333 s. Runtime plays punches once, alternating with the existing 1.0 s cooldown reference. Manifest endpoint-loop flags describe matching poses, not punch playback mode.

## Motion and preservation

Hip/chest drive leads the folded elbow and forward fist; recoil returns to guard. Actual movement drives a post-animation fixed-length leg solver with world-space stance anchors and lifted swing steps. Direction changes update swing landing targets and release a plant before overreach. Punch rhythm and aim remain independent of the foot cycle. Moving release crossfades directly to the original walk; stationary release uses Exit.

All 69 mesh objects retain v14 vertex positions, topology, UVs and material assignments; all 34 rest bones are identical. Existing solid-green painted eyes, removed brow markings, bulk, shields and original pelvis proportions are preserved. The intentional binding repair redirects residual lower-rear leg influences to Hips on 1,212 vertices with a narrow transition; no pelvis remodeling. Approved v14 idle and older source files remain separate.

## Validation and limits

Blender export contains 11 animations and a 34-joint skin. New source poses have no IK reach clamps; cyclic endpoints match. A targeted BVH audit sampled 146 left/right punch poses: zero shield/forearm surface crossings against the selected helmet and back-cell surfaces. This is a targeted clearance check, not whole-model collision certification.

Godot fixed-60 review completed the scripted stationary attacks, lateral reversals, forward/back motion, diagonal movement, release while moving and re-entry. Logged attacks alternate Left/Right at 1.0 s intervals. Sustained moving attacks reach 3.5 m/s and keep aim fixed. Final deterministic foot telemetry reports maximum planted-anchor error 0.0000016 m, consecutive plant displacement 0.000002 m, and no remaining reach clamp. These are solver metrics, not artistic approval. Native final recording was refreshed after the landed-foot locking correction and representative gameplay/front frames were inspected.

Production `ape_kit.gd` and its damage, hit-stop, feedback and cancellable backswing are untouched. The isolated review disables the original kit and logs visual attack/contact events; it does not prove production damage integration or production input arbitration. It preserves the existing 3.5 m/s movement and 1.0 s basic cooldown references. Further review should judge sustained rhythm, weight and readability from the normal gameplay camera before promotion. Existing exposed underside details in the raised forearms are model polish outside this animation pass.

Headless runs report the environment root-certificate-store message and exit resource warnings; no new script parse/runtime errors were observed. Reports: `v17/preservation-validation.json`, `v17/armor-clearance-audit.json`, `v17/combat-manifest.json`, `industry-combat-v17/headless-validation.json`, and associated CSVs/logs.
