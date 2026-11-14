# Gorilla readable idle v14

User found v13 effectively motionless at gameplay distance and asked to study Rampage again. v13 kept the Chest bone neutral and animated only tiny shoulder/head motion, leaving the main visible torso armor almost still. v14 replaces that review idle with sampled Rampage upper-body timing and a visibly larger pose range.

## Actual reference study

Read the user-supplied `D:/user/Downloads/paragon_rampage_elemental_20_animations.glb`. Its `Idle` is 7.666666 seconds. Imported the actual action into Blender and sampled 121 phases of pelvis, chest, shoulders, head, hand, and foot transforms; inspected four rendered poses. World-space ranges in the supplied model: chest lateral 6.41cm, head lateral 25.74cm, shoulders lateral 6.88–10.46cm, with much smaller hand motion. Chest rotation reaches roughly 9.93 degrees from its starting orientation; head roughly 29.58 degrees. The read is a long alert torso/shoulder weight transfer with head follow-through, not a four-second tiny symmetric sine breath.

Study evidence: scratch `v14/rampage-idle-study.json` and `rampage-idle-{0,30,60,90}.png`; reproducible `study_rampage_idle_v14.py`. No donor geometry or materials were added to our model.

## New asset

`art/model_catalog/workspaces/gorilla_idle_v14.blend` and `.glb`, action `Gorilla_Idle_v14`, 460 frames at 60fps, 7.666667 seconds. This is a separate idle-only asset; the previous v12 walk asset/test remains unchanged.

Adapted donor world chest translation at 95% and world chest rotation delta at 85%. Shoulder offsets use donor motion relative to its chest. Head rotation delta uses 75% with the destination neck hierarchy. The wider mech shoulders yield a more readable shoulder envelope. Arm IK fixes each fist's world position and orientation. Feet and hips remain stationary; no scale or proportions change. Tiny donor endpoint rounding is removed for exact loop closure.

Only in the new idle asset, redirected 645 lower rear body vertices' Chest weight portions to Hips, with a narrow blend at the upper connector. Other influences are retained. This prevents upper torso movement from dragging the pelvis. This is a binding correction, not reshaping: all vertex coordinates, mesh object names, and topology exactly match v12. This does not claim to solve the independent walk pelvis/thigh conflict.

## Validation

Across 461 authored poses: hand-joint drift under 0.006mm, feet zero drift, no arm reach clamps, first/last pose matrix difference zero. Chest lateral range 6.09cm; head 22.30cm; shoulder heads about 16.94cm from the wider destination hierarchy. No root locomotion.

Across 116 evaluated phases, all 1,003 sampled lower rear armor vertices had zero surface displacement from rest. Rest geometry/topology comparison against v12 passed for every mesh. Source validation: scratch `v14/idle-validation.json` and `pelvis-geometry-validation.json`. This contact measurement is not a general collision/terrain guarantee.

Blender front and rear pose views inspected at four phases; a full front inspection loop rendered at 24fps. Godot 4.7.2 industry test loads the idle at 7.6666665 seconds. Headless startup retains the environment certificate-store diagnostic and exit resource warnings; visible recording log is inspected separately. No production gameplay blending was implemented or claimed.

## Review media

Scratch root: `D:/dev/_scratch/gorilla/meshforge-2026-11-08`.

- Front animation preview: `v14/gorilla-idle-front-v14.mp4`.
- FFmpeg industry capture: `industry-idle-v14/gorilla-idle-rampage-v14.mp4`.
- Additive review scene: `tools/debug/gorilla_idle_industry_test.tscn`, now using v14, same 1.0 model scale and SMITE-led chase camera. No camera orbit.
- Source/build/render scripts: `build_idle_v14.py`, `audit_idle_v14.py`, `render_idle_v14.py`.

Future review: production idle/walk transitions still need the separate walk pelvis fix and compatible state blending. Do not restore v13 as the default idle; the user rejected its lack of visible motion.

Additional runtime verification: fixed-60fps headless playback logged clip time advancing through the 7.67-second wrap and changing Chest poses (industry-idle-v14/playback-check.log). Visible recorded frames at 5s and 10s differ in 4,830 character-region pixels by more than 20/255; the back-cell region alone changes in 2,418 pixels. This confirms actual rendered armor motion, beyond simply having an animation track. Blender visible-motion audit measures maximum back-cell displacement 9.91cm and shoulder-bulk displacement 17.64cm; evidence v14/visible-motion-audit.json. Final recordings: industry 18 seconds at 1280x720; front one full cycle at 24fps, 960x720. FFprobe verified both durations/resolutions.

