# Gorilla / rhino Unreal comparison handoff

Decision update, November 15: Preston approved migration after this comparison.
The destination is now `D:/dev/mech-moba-unreal/MechMoba.uproject`. Read its
`Migration/DECISION.md`. The main-Godot recommendation below describes the earlier
comparison stage; Godot is now the preserved behavior reference.

Preston approved a separate playable comparison following Gemini's engine report.
The Godot game remains the main build. Do not migrate or freeze authoring lanes
based on this note.

Trial: `D:/dev/unreal-mech-trial`. Open `Launch Trial.cmd`. F2 switches gorilla and
rhino. See `COMPARISON_CONTROLS.md`, `COMPARISON_RESULTS_2026-11-15.md`,
`comparison-check.json` and `comparison-network-check.json` there.

Verified: 15 selected source clips imported with preserved durations, hand-following
green shield faces, ring effects and a copied Epic Niagara burst. Standalone actual
contacts/block math, single damaging pound pulse and brace interruption passed.
Two clients completed the scripted sequence with engine-confirmed 60ms outgoing
delay / 3% outgoing loss per process; they received non-default shield updates and
rhino action state. No duplicate Drive contact per activation was observed.

Important lessons:

- Source FPS is a time base, not an arbitrary speed control. 120Hz export/import
  preserves half-frame boundaries in this 60fps source; do not retime masters.
- Gorilla uses a -90 degree visual yaw adapter; this rhino uses +90. A global
  skeletal-mesh rotation override is wrong for the pair.
- Save every FBX-generated animation and skeleton explicitly. Saving the import
  task's primary skeletal mesh alone did not preserve the generated packages here.
- Keep wall probing separate from victim contact geometry. A channel trace can
  encounter enemy geometry and misclassify it as terrain.
- Plain CharacterMovement walking velocity caps a scripted Drive. Our swept
  server movement is a prototype, not a complete predicted network movement mode.
- Rhino hook/rip/gore all deal 30 in current Godot. CHAIN_STRENGTH changes feel,
  not damage. Gorilla's swat is 28; Drive is 24. Blocked hits use 50% damage.
- The native shield's internal 100 is an active flag for three seconds, not a
  100HP absorb pool. Earlier November 14 trial notes describe obsolete behavior.
- Editor Python successfully handled batching and creating materials / test map.
  Niagara template loading required a direct load / registry scan. Epic's MCP
  descriptors exist locally, but the first-party live MCP has not been enabled
  or functionally evaluated. Do not infer tool capabilities from their names.

Original v40 gorilla and v61 rhino GLBs were rehashed unchanged. Source manifest
and export copies are under the trial's SourceAssets folder. No live Godot scene,
model, script, balance value or approved rig was modified by this comparison.

Limits: selected mechanics only, approximate capsules/ranges, incomplete kit,
no full Godot feel parity, no GAS / Control Rig / Motion Warping, no visual lag
reconciliation certification, no ten-client/minion or shipping-server benchmark.
The fixed-clock recording is for animation review, not FPS evidence.

Research review: `docs/reference/GEMINI_ENGINE_MIGRATION_REVIEW_2026-11-14.md`.
Keep full-art/animation work portable and use measured behavior to decide whether
further Unreal work pays off.
