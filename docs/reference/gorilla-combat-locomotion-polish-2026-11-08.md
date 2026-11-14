# Gorilla combat locomotion polish — 2026-11-08

Latest candidate: `art/model_catalog/workspaces/gorilla_combat_locomotion_v6.blend` and `.glb`. Preserves the static/back-rim source and older animation candidates. Test only; no gameplay catalog or production controller promotion.

## Changes

Original combat stride v4 showed axial/bend-direction jumps during recovery. Replaced the direction-only shortest-rotation solve with a stable limb-plane frame and fixed twist offset. Added quaternion sign continuity, outward recovery arcs, and a quintic recovery trajectory whose contact velocity matches support velocity at takeoff and landing. Adjusted support timing/body compression to avoid overreaching. All sampled endpoints fit the limb reach with no upper reach clamps.

New original action `Gorilla_CombatLoco_v6`:0.6seconds,120fps bake, paired fore/hind loping pattern with0.03-cycle side offset and38% support windows. Rearward contact stroke0.798m over0.228s matches3.5m/s. Buff preview uses1.25x playback to match4.375m/s, preserving the spatial stroke. Geometry proportions, colors,34joints and25,757triangles unchanged.

Cleaned the main body's skinning: unified chest/back/shoulder-cap structural influences, removed stray small influences, strengthened dominant weights and made coincident UV-seam vertices agree.12,420 of24,001 main-body vertices and8,360 of17,529 body faces are now fully rigid. Remaining joint transitions retain deformation; custom hands, feet, forearm casings and shields keep their existing rigid attachments. This is targeted cleanup, not certification that every surface is rigid or every joint is production-finished.

Rejected split-face armor and hard spatial partition trials because they opened shell gaps or badly stretched boundary faces. They remain only in scratch; neither is delivered as the final candidate. The delivered body retains its original topology.

## Runtime check and recording

Scene `res://tools/debug/gorilla_walk_industry_test.tscn` uses the existing Foundry industry map and Player controller, driven by a deterministic movement override around the plaza. Candidate display scale1.0.3.5m/s base,4.375m/s illustrative+25% buff. Not a manual-input or full combat test.

Use `GLTFDocument.generate_scene(state,120.0)` in this test to retain the contact solve; the previous default30fps bake caused visible between-sample motion errors. Official [Godot GLTFDocument documentation](https://docs.godotengine.org/en/stable/classes/class_gltfdocument.html#class-gltfdocument-method-generate-scene) documents that the generate_scene argument overrides the state's bake FPS.

Evidence: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-polish-v6/`.

- `gorilla-refined-movement.mp4`: actual FFmpeg gdigrab capture of the game window,1280x720,30fps target,22seconds. Watched sampled frames including base/boost poses; engine log has no reported script errors.
- `runtime.csv`: positions, player speed, playback and FPS.
- `contacts.csv`, `contact-summary.json`: world-space support-joint movement between samples. On straight segments, after excluding startup, heading changes with a short buffer and speed-transition boundaries, worst adjacent movement was0.349mm. Base p95 is at most0.085mm; boosted p95 at most0.294mm. These measure joints, not a final mesh-surface/terrain collision guarantee. Turns are explicitly excluded; they still need foot locking/turn blending.

Private source: `../v6/contact-audit.json`, `armor-weight-report.json`, MeshForge side/front contact sheet, source/export. Build `refine_combat_v6.py`, weight cleanup `refine_weights_v6.py` in the scratch root. No paid generation or rerigging used.

## Remaining polish

Sharp direction changes still snap the actor's heading through the existing controller. Dedicated start/stop/turn blends and terrain-aware contacts remain. The run has been reviewed on the flat industry plaza; no complete shield/body collision certification or full gameplay-state integration is claimed. Preserve the earlier accepted gait as a slow-walk option.
