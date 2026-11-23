# Hornet six-leg surface restoration

Restored November 14, 2026, after Fennec. The previously pending native Workshop check was completed after Wolf. Hornet's downloaded 51-joint rig had widespread missing surface across the head, wings, joints and body. The documented six-leg pre-rig touch-up also contained widespread cracks. An intact-source reconstruction was required instead of broad hole filling.

![Damaged rig and restored surface](before-after.png)

The current Workshop displays the restored **six-leg** layout, with four wings, two antennae, twin front barrels, abdomen and stinger retained. No new anatomy choice was inferred: the exact prior approved cut mask FL1/FL2/FR1/FR2/L2/L4/R2/R4 was reproduced. It removes the four floating claw pieces and the four tucked-under legs, retaining front/middle/rear on each side. The mask matched all 4,939 previously removed faces on the 40k classification proxy.

## Four-version comparison

C shows all four stages at matched scale: intact generated quality archive (extra limbs explicitly unapproved), accepted six-leg pre-rig touch-up (cracked surface), downloaded rig (damaged surface), and current restoration. The four-version camera is widened; existing two/three-version views retain their prior sizes. R switches between the immutable four generation PNGs and revised four-stage comparison sheets.

The accepted pre-rig file is the one prescribed for rigging by `docs/team/LINEUP_MODEL_RIG_AUDIT_2026-11-10.md`. Exact historical Meshy upload identity is not independently verified. Neither that touch-up nor the damaged rig is mislabeled as an intact quality source.

## Restoration and rig preservation

The intact generated source starts with 500,000 triangles and closed topology. The approved proxy classification was projected onto its geometry and smoothed only as a cut field; the source surface itself was not remeshed or broadly smoothed. New cut roots were closed. Two verified cut-created remnants, 441 and 277 vertices, were removed; their cut-field and position evidence is preserved under the scratch inspection files. They were leftovers of approved removals, not healthy limbs or armor.

The actual restored GLB contains **445,372 triangles**, zero open edges, zero over-shared edges and zero collapsed triangles. The independent audit verifies actual exported geometry, normals and UVs against the restored static staging asset. Original generator materials/textures are used, plus a local gunmetal cut-root finish. Original generation archive, pre-rig touch-up, damaged rig and all reference PNGs remain unchanged.

The downloaded rig's **51-joint hierarchy, rest transforms, inverse binds, scene nodes and clips** remain exact. Its original binary and original material/image records remain archived inside the append-only export. Skin was transferred from the actual downloaded rig using four nearest samples with inverse fourth-power weighting, normalized to the strongest four influences. Identical UV-seam positions receive identical queries. Original downloaded weights are preserved in the archive, not claimed byte-identical on the new surface. Transfer distances are recorded in `rig-transfer-verification.json`; missing donor regions make the transfer approximate.

Twenty-four actual native-joint diagnostics passed with maximum measured coincident-surface gap 0 m, below the one-micrometre tolerance. Tests cover body/head/lower-front control groups, both antenna roots/tips, existing leg-control chains, both wing-control chains, abdomen and stinger. The source control grouping is preserved; independent six-leg gait/four-wing flight articulation is not claimed. The native scene is saved with restored rest pose and four packed immutable reference images.

![Six-leg underside and closures](underside-proof.png)

Textured front/side/back/top/underside/three-quarter views, both eyes, head, wings, antennae, six-leg layout, cut areas, abdomen/stinger and motion proofs were inspected. Godot's four-version comparison, original/revised sheets, 51-bone skeleton and current ChaseCamera3D check passed. Final lineup, front/back comparison, enlarged sheet and chase-camera screenshots were inspected in `reports/model_catalog/hornet-restoration-v1`.

This is a **high-detail review asset**. Optimisation and authored gait/flight remain; no gameplay/map replacement or performance approval is claimed.

## Exact sources and evidence

Intact generated archive: `art/model_catalog/sources/hornet_front - Hunyuan 3D v3.1 Pro.glb`, SHA256 `1abdd53ffe957aa022deb629644ca5f0e7c6d357bedc1998565ea627773240c1`.

Accepted pre-rig touch-up: `D:/user/Downloads/hornet_front - 6 legs touchup.glb`, SHA256 `84622e39a7a46413ab9676789fcac12a9599da71614f5c12462550d220837bb2`; exact copy preserved under `art/model_catalog/sources/`.

Downloaded rig: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_hornet_touchup_remeshed_25k_20261111_character.glb`, SHA256 `02e61d1695fca6a5cf80591de4f4a1ebffe9a427f50ad556df1c81f76ba4b8a0`; 21,743 triangles, 51 joints, no clips; exact archive copy retained.

Final: `hornet-rigged-local-repair-v1.glb`, SHA256 `483471b77e49fb6983ce026c6217014f3d3a3853c8b90949ccbe650b90a82762`; native `hornet-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: actual-file checks and preservation scope.
- `surface-report.json`, `accepted-cut-mask.npz`, `rig-transfer-verification.json`: restoration, approved-cut and transferred-weight evidence.
- `visual-deformation-check.json`, `pose-proof.png`: 24 native-joint diagnostics.
- `review-front/left/back/right.png`: four-stage comparison sheets.
- `final-review-verification.json`, `godot-review.log`: runtime evidence and final hashes.
- `restored-six-leg-surface-STATIC-STAGING.glb`, `.blend`: geometry-only intermediate, not the active rigged display.

Canonical scripts and logs: `D:/dev/_scratch/mech-art-direction/hornet-review-2026-11-14/`, with snapshots here. Run approved-mask export, intact-surface reconstruction, bind transfer, independent actual-file audit, renders/poses and packaging in that order. Diagnostic topology counts in `input-audit.json` and `baseline-geometry-audit.json` describe damaged inputs and must not be treated as current output counts.

Fennec and all earlier roster work are preserved. No paid generation, commits or next model selection in this completion.

## Earlier Summer review

Summer Engine 0.7.0 independently passed its isolated four-version/51-joint review, with seven inspected 1600x900 views. That evidence remains in `summer-review-verification.json` and `summer-review/`. Its original pending-Workshop wording records the state at that earlier capture; the native Godot check is now resolved by `final-review-verification.json`. Model geometry and skin were not changed for this completion.
