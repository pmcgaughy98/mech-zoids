# Gorilla basic attack animation chain v15

User rejected the motion after review: it reads as swinging a limb, not punching. The technical clearance checks below did not establish convincing punch mechanics. Keep this as rejected comparison evidence; the current correction is the single-punch v16 study.

Following user approval of the Rampage-inspired v14 idle, created three in-place basic attack clips from the supplied Rampage quadruped melee set. Preserved the approved model, five-finger fists, knuckle stance, feet, shields, palette, painted green eyes, and original pelvis proportions.

## Deliverables

- `art/model_catalog/workspaces/gorilla_basic_attacks_v15.blend` — editable rig, approved idle and three attacks.
- `art/model_catalog/workspaces/gorilla_basic_attacks_v15.glb` — self-contained runtime asset, same 34-bone skeleton.
- `art/model_catalog/workspaces/gorilla_basic_attacks_v15.events.json` — nominal impact/cast times and durations.
- `tools/debug/gorilla_basic_attacks_industry_test.tscn` / `.gd` — additive industry-map review with a broad mechanical training post, timing markers, spring recoil, and idle transitions.

| Action | Active fist | Duration | Impact marker |
| --- | --- | --- | --- |
| Gorilla_Basic_A_v15 | Left | 0.90s | 0.345s |
| Gorilla_Basic_B_v15 | Right | 0.90s | 0.345s |
| Gorilla_Basic_C_v15 | Left, heavy finisher | 1.10s | 0.440s |

Also includes the unchanged `Gorilla_Idle_v14` action at 7.666667s. Walk remains in its separate existing asset; the production controller and walk test are unchanged.

## Motion decisions

Studied actual `Attack_Melee_A`, `Attack_Melee_B`, and `Attack_Melee_C` from user-supplied `D:/user/Downloads/paragon_rampage_elemental_20_animations.glb`. Sampled 121 phases per attack, including chest, head, shoulders, elbows, hands, and feet. Rendered donor anticipation, strike, follow-through, and recovery poses. A/B alternate hands, and C provides a broader follow-through. No donor mesh or materials added.

Adapted fist arcs to the destination anatomy and much larger forearm shields. Fists turn their gray knuckle faces toward the target during the strike and return to the original downward stance. The inactive fist braces on the ground; both feet remain fixed. Torso twist is fitted continuously to the support arm's available reach, with no bone length scaling. Active-hand targets are limited to the arm's reach. Head stays aimed toward the target. Both endpoints match the neutral stance, with quintic easing into and out of the action.

Directly copying the donor arcs made the broad mech forearm armor intersect its helmet. Corrected the windup/strike lanes, elbow direction, and forearm roll. Clearance depends on the whole forearm's length, not just the fist's location. The clips retain the source's anticipation/strike/follow-through timing with wider mech-specific paths. No geometry reshaping or new skin weights were introduced; v14's lower rear Chest-to-Hips correction is retained.

## Review controls and scope

In the standalone industry review, left click or Space starts an attack or buffers the next attack; holding left click continues the chain. It uses the existing industry arena, 1.0 model scale, and the approved SMITE-led third-person chase camera. `--record` waits for scratch `industry-attacks-v15/record.trigger`, then shows four chains with idle gaps and auto-closes after 24 seconds. Target flash/recoil is a pose-timed review marker, not production hit detection.

This pass delivers animation assets and an isolated test scene. The existing `ape_kit.gd` already has damage, contact hit-stop and cancellable backswing behavior; these were not changed or replaced. Connecting accepted skeletal animation to that existing gameplay remains separate from the review scene. Nominal impact times are exported for that integration; they are not new balance instructions.

## Evidence and reproducibility

Scratch root: `D:/dev/_scratch/gorilla/meshforge-2026-11-08`.

- `study_melee_v15.py`, `v15/rampage-melee-study.json`, and `v15/donor-*.png`: actual donor study.
- `build_attacks_v15.py`, `v15/attack-validation.json`: action generation, reach/contact/endpoint checks.
- `audit_attacks_v15.py`, `v15/geometry-contact-audit.json`: rest geometry/topology identity versus approved v14, evaluated pelvis/feet/scale and fist impact surfaces.
- `check_attack_clearance_v15.py`, `v15/armor-clearance-audit.json`: per-frame triangle-surface checks of active forearm casing and shield hardware against selected native helmet and back-cell surfaces. This is targeted clearance checking, not a general full-body collision proof.
- `render_attack_chain_v15.py`, `v15/gorilla-basic-attacks-front-v15.mp4`: front inspection, two complete chains at 24fps.
- `industry-attacks-v15/gorilla-basic-attacks-industry-v15.mp4`: FFmpeg window capture of actual Godot gameplay test.
- `industry-attacks-v15/playback-check.log`, `game.log`, `attack-events.csv`: actual clip playback, impact markers and recovery/idle transitions.

Godot 4.7.2 headless validation retains the environment's certificate-store diagnostic and exit resource-leak warnings. Do not describe that log as error-free. Visible game run uses the NVIDIA compatibility renderer. Earlier scratch preview renders/recordings were replaced after correcting mech-specific clearance; only the final media should be used for review.

Final verification: all 177 authored attack poses pass the targeted shield/forearm-to-helmet/back-cell triangle-surface check. Maximum bracing-hand joint drift is 0.0543mm; the sampled 1,003 rear pelvis vertices move less than 0.00011mm. Rest geometry/topology exactly matches the approved v14 model. Start/end attack matrices agree exactly. Final export contains A/B at 0.9s, C at 1.1s, and the original 7.666667s idle. Project GLB SHA-256 matches the final scratch export. Evidence: v15/final-validation-summary.json and exported-clips.json. Front recording: 7.791667s, 187 frames, 24fps, 960x800. Native industry recording: 20s, 1280x720. Training target uses an anchored spring pivot and is tall enough to read above the player from the approved camera.

