# Meshy Text to Motion trial, 2026-11-09

**Decision: keep the authored shield cast. This single generated donor does not improve it.**

Preston authorized the prepared trial with "do it". One standalone Prime task was submitted using the API, with the exact prompt in MESHY_TRIAL_PLAN.md, duration 2 seconds. No model was uploaded. No retries or extra generations ran.

## Cost and source

- Task: `01a1c37e-0476-7267-8608-da9b66219d69`.
- Status: SUCCEEDED. API-reported consumed credits: **10**.
- Balance before: **1,020**; after: **1,010**.
- Output: FBX, 16,711,424 bytes, archived locally with SHA-256 in download.json.
- Actual import: **52 bones**, including finger chains, action `Reference|SMPLH_Animation|Base Layer`, **30 fps**, frames **1–60**. FBX armature object scale is 0.01 and the evaluated character is approximately human size in Blender meters. Do not hard-code a 24-joint donor based on the Gemini report.
- [Official Text to Motion API documentation](https://docs.meshy.ai/en/api/text-to-motion) was checked before submission.

## What the sample did

The request called for a planted low stance, a right forearm draw across the chest, one decisive outward protective gesture and a return. Rendered samples show a leaning, low arm sweep with substantial whole-body movement, rather than that clear shield action. The initial and final pose do not match exactly.

Measured maximum displacement from the first frame: pelvis **0.367 m**, left ankle **0.168 m**, right ankle **0.339 m**. These are bone-head displacements, not a sole-contact or foot-sliding measurement. They establish that the requested stationary support pose was not maintained.

## Isolated local fit

An editable copy of shield-cast-trial.blend was used. The donor's right-arm segment directions were reflected across X and mapped to the native Left arm, matching the baseline's presentation side. Native upper/lower arm lengths were retained with a two-bone solve. Hand alignment follows the native forearm relationship.

The donor's root, torso, support arm and legs were deliberately discarded. Native support pose remained fixed. A 0.12-second entry blend and final 0.30-second exit blend reconnect to the native starting pose. This is an **arm-only salvage experiment**, not a full-body retarget or a claim that all donor motion transferred correctly.

Geometry, vertex weights, topology and material-slot hashes match before/after. Rest bones match. Support wrist and foot-head drift are zero in this fixed-support experiment; maximum evaluated bone-length numerical error is 0.00000197 m. No reach clamps occurred. These checks do **not** certify armor clearance. The candidate is rejected before a clearance/polish pass.

The fit still reads as a low sweep and prolonged gesture. Adapting it into the existing 0.6-second cast would require replacing the action's main poses and timing. No useful release phase justified retiming into the 0.25-second gameplay event. The two-second clip was therefore left at native duration for comparison. No runtime export, game hookup, release change or production asset replacement was made.

The scripted fit build took 3.34 seconds; development, inspection and rendering took additional session time and were not separately instrumented as hands-on cleanup. This trial does not demonstrate an authoring-time saving. No further polish was attempted after the intent failure.

## Playable evidence and reproduction

Scratch folder: `D:/dev/_scratch/meshy-motion-trial-2026-11-09`.

- `comparison-normal.mp4`: front-quarter then side, raw donor / arm-only fit / authored cast. Target panels share camera and framing. Original 0.6-second cast then holds its final pose until the two-second donor finishes.
- `comparison-half-speed.mp4`: same sequence, explicitly labelled 0.5x.
- `comparison-board.jpg`: four normal-time samples for quick comparison.
- `donor.blend`, `fitted.blend`: editable raw and isolated fitted scenes.
- `meshy_trial.py`, `request.json`, `submission.json`, `task.json`, `download.json`: API provenance and resumable polling. Submission guard prevents automatic resubmission. Do not run submit again.
- `inspect_donor.py`, `donor-inspection.json`, `donor-samples.json`: actual donor skeleton and sampled evaluated motion.
- `fit.py`, `fit-report.json`, `raw-metrics.json`: mapping and preservation checks.
- `render.py`, `assemble.py`: Workbench body-only render/comparison assembly; flat gray surfaces are deliberate for pose review, not new game materials.

Review used rendered time samples from both views, not just technical metrics. No Godot process was started for the rejected candidate.

## What to carry forward

Gemini research helps specify and judge the action, but that research is not a hidden conditioning input to Meshy. Meshy received only the 331-character prompt. This sample shows that a detailed brief does not guarantee precise action semantics, grounded support or game-ready timing.

Keep Meshy as a possible source of motion ideas, subject to a small scoped test. Continue authored poses, native-rig contact correction and engine review for our exact moves. One unsuccessful Prime sample does not establish that all Meshy motion fails, nor compare Prime with Swift. Any further paid sample requires its own authorized scope.
