# Gorilla grounded idle v13

New four-second looping idle for the approved v12 gorilla. Editable source and interchange asset: `art/model_catalog/workspaces/gorilla_idle_v13.blend` and `.glb`. Named action `Gorilla_Idle_v13`, 120fps, frames 0–480. The GLB also retains `Gorilla_CombatLoco_v12` at its original 0.6 seconds. Existing walk test remains unchanged.

The idle starts from the model's already grounded rest stance. Both knuckles and feet stay planted. Paired shoulder servo motion rises 4mm over a slow breathing cycle with 0.38-degree rotation, while the head makes a small alert scan (1.4-degree yaw, 0.55-degree pitch motion). Arm IK holds the original hand position and orientation. No bone scale animation, new geometry, material changes, or weight edits. Painted green eyes and original proportions are preserved.

Hips, chest, and leg transforms remain neutral throughout. This is intentional: the walk's unresolved mixed pelvis weights must not be exercised by a new exaggerated pelvis sway. This idle does not repair that separate walk defect. Its motion is deliberately restrained at gameplay distance.

Validation across all 481 authored poses: maximum hand-joint drift 0.0000007692m; both foot joints zero drift; no IK reach clamps; first/last pose matrix difference zero. These are joint measurements, not a terrain-collision guarantee. Blender front/rear renders at four phases were inspected. Godot 4.7.2 loaded both clips and confirmed the idle length at four seconds. Headless startup has the existing certificate-store diagnostic; visible gameplay run uses the NVIDIA compatibility renderer.

Additive industry review: `tools/debug/gorilla_idle_industry_test.tscn`. Uses the existing industry arena and original third-person chase camera; stationary 1.0-scale model. No production controller changes or new runtime contact modifier. Launch with `--record` to wait for scratch `industry-idle-v13/record.trigger` and auto-close after 14 seconds.

Evidence root: `D:/dev/_scratch/gorilla/meshforge-2026-11-08`. Build script `build_idle_v13.py`; measurements `v13/idle-validation.json`; exported clip durations `v13/exported-clips.json`; Blender previews `v13/idle-front-*.png` and `idle-back-*.png`; FFmpeg gameplay recording `industry-idle-v13/gorilla-idle-industry.mp4`.

Not implemented in this pass: idle-to-walk blending in production, combat ready/attack variants, or the separate pelvis skinning repair.
