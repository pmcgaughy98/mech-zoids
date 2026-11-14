# Falcon four-toe feet and local repair

Completed November 13, 2026, after Preston approved removing the marked outer rear toe 1 on both feet. Each foot now has **three forward claws and one rear claw**. Both cuts have closed gunmetal mounting surfaces; the neighboring rear claws and original foot pads remain.

![Both corrected feet](feet-before-after.png)

The Workshop lineup and revised sheets now use `falcon-rigged-local-repair-v1.glb`. C compares the intact generated quality archive, downloaded five-toe rig and four-toe repair. R switches between the four original reference PNGs and revised comparison sheets. The archive's extra rear toes are explicitly labeled unapproved. The intact archive's exact historical Meshy-upload identity is not independently verified.

## Geometry and rig

The final actual GLB contains 23,252 triangles and the original 45-joint hierarchy. The earlier chest gap closure and removal of 26 malformed triangles are retained. Source regression verifies 2,294 guarded neighboring toe faces and 22,978 surface-stage faces unchanged. All original positions, normals and UV rows remain exact, as do the original materials, texture data, rest transforms and inverse binds. The raw source and surface-stage binary data remain exact prefixes of the append-only export.

Only residual influences from Bone_027/028 were moved to existing foot parent Bone_009, and Bone_037/038 to Bone_013. Other joint influences are retained. The removed controls remain in the skeleton for compatibility and produce zero visible surface movement. No remesh or rerig occurred.

The closures follow the actual cut contours, using concave-polygon triangulation to prevent folded cap faces. No original pad vertex was moved. The audit confirms zero open edges, zero collapsed triangles and zero inverted projected closure faces. One protected original balanced four-face contact with a tiny closed positive-volume assembly detail remains, so this is not a globally zero-over-shared-edge claim. New gunmetal finish is a single added material; original textures are unchanged.

![Both mounting areas](socket-before-after.png)

## Verification

Independent actual-file topology, geometry, skin and skeleton preservation audit passed. Twenty-four native-joint diagnostics passed with maximum measured coincident-surface gap 1.22878123e-07 m. Tests cover the body, tail, both wings, neck/head/beak, legs, ankles, feet, forward toes, both retained rear claws and all four unused removed-toe controls. Removed-control surface movement is 0 m. The native scene was saved with its rest pose restored and four original references packed.

Textured front/side/back/top/underside/three-quarter views, both eyes, tail, both feet, both closure close-ups and diagnostic poses were inspected. Godot's three-version comparison, original/revised sheet, 45-bone skeleton and current ChaseCamera3D check passed. Final lineup, front/back comparisons, enlarged sheet and chase-camera screenshots were inspected under `reports/model_catalog/falcon-local-v1`.

![Original chest gap closure](before-after.png)

These are local deformation diagnostics, not finished flight/walk clips. The input has no animations. Separate Grok foundation/draft-clip files were inspected for lineage and left unchanged. Existing source bake roughness and remesh detail loss remain; no gameplay/map replacement or full-detail restoration is claimed.

## Exact files and evidence

Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_falcon_remeshed_25k_20261108_character.glb`, SHA256 `245e6242746f7e4daf179299621fac0f372bfe6b0b9bef0edbfdf394b5f3db37`; 23,579 triangles, 45 joints, no clips. Exact copy archived under `art/model_catalog/sources/`.

Final GLB: `falcon-rigged-local-repair-v1.glb`; SHA256 `4d189d5083c141b424a282e1e68a87701c65338870bf2ee36b38e89d03f49807`. Editable scene: `falcon-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: scope and actual-file preservation/topology checks.
- `visual-deformation-check.json`, `pose-proof.png`: 24 native diagnostics.
- `final-review-verification.json`, `godot-review.log`: final hashes and runtime evidence.
- `feet-before-after.png`, `socket-before-after.png`, `before-after.png`: matched anatomy and local closure proofs.
- `review-front/left/back/right.png`: intact quality archive / downloaded rig / four-toe repair.
- `falcon-surface-only-staged.glb`, `surface-only-verification.json`: earlier surface-only stage with all five toes, preserved for provenance.

The earlier `anatomy-review-pending.json` is a historical checkpoint, resolved by Preston's yes to removing toe 1 on both feet. Original source GLBs/reference PNGs, Electric Eel and other roster work are preserved. Canonical scripts: `D:/dev/_scratch/mech-art-direction/falcon-review-2026-11-13/`, with snapshots here. Reconstruct the surface stage with `repair_model.py`; `inspect_toe.py` supplies the field data, `remove_toes.py` makes the anatomy correction, then audit, render, native checks and packaging follow. No paid generation or commits. No next model selected in this completion.
