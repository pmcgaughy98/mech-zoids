# Sloth: first local repair pass

Completed November 15, 2026, as the first of Preston's five newly rigged Creature Factory models. The approved take B olive-armored Sloth design remains, with two long forearms, six hooked digits, two shorter hind legs/feet, face and eyes, paired forearm reels, chest core, dorsal growth recesses and short tail.

![Downloaded rig and local repair](review-front.png)

## Repair and preservation

Removed eleven malformed triangles in open fragments and closed one small chest opening with an original-corner triangle. The actual export contains 25,556 triangles and zero open edges or collapsed triangles. All 25,555 other source triangles remain, including the separate closed 4/4/30/4-face source components; three balanced four-face assembly contacts remain after closure.

All original positions, normals, UV rows, joints and skin weights remain exact. The full 52-joint hierarchy, rest transforms, inverse binds, scene nodes, materials and textures are unchanged. Original binary is an exact prefix. Appended accessors replace triangle connectivity and add three duplicate corner rows for the new chest closure. Those rows copy original positions, normals, joints and weights exactly; their UVs sample one healthy neighboring texture island, preventing the closure from spanning unrelated atlas regions. No new geometric position, rerig, remesh, new material or texture.

Actual-file audit and matched chest/head/reel/dorsal and front/back/both sides/top/underside/three-quarter renders were inspected. All 52 native control rotations produced measurable surface movement and passed the one-micrometre seam tolerance. Maximum measured coincident-surface separation: 0 m. Twenty-four representative posed renders cover body, face, forearms, hook groups and hind limbs. The native workspace is saved in rest pose with all four immutable downloaded reference images packed.

Godot 4.7.2's native two-version/original-review-sheet/52-joint/ChaseCamera3D check passed. All seven final screenshots were inspected. Sloth is in the Workshop with four revised before/after sheets. The selector now fits five compact button rows above Objectives, leaving room for the five new designs as their passes are completed. The overview camera fits the actual model bounds with padding so the added row does not clip the top or objective rows. Prior 31 catalog entries are preserved.

## Visual limits and source provenance

The baked moss detail inside the dorsal recesses is faint compared with the reference sheets. It remains a later visual/material pass; this repair does not claim complete restoration of reference foliage or finished animation. Original automatic skin/control grouping is retained. No gameplay installation or performance/animation approval is claimed.

No intact pre-remesh Sloth GLB was located in the local source search. The two-version comparison explicitly shows exact downloaded remeshed rig / local repair. The source archive is not mislabeled as intact pre-remesh geometry. Original generation PNGs remain available separately with R. Downloaded PNGs visually match the approved take B identity; their exact bytes do not match the project's packaged copies, so no false hash match is claimed.

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_mecha_sloth_guardian_remeshed_25k_20261114_character.glb`; SHA256 `f01c3719f38134ffcbae9fcf029b49ee9590d24552aa173bf1227ac1b7604030`; 25,566 triangles, 52 joints, zero clips. Exact copy is archived in `art/model_catalog/sources/` under its original filename.

Final: `sloth-rigged-local-repair-v1.glb`; SHA256 `a2f838dbfe557bff2f8671fcd050af1813d1f64f04950be4740e0b53062725ad`. Editable: `sloth-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: topology and exact data preservation.
- `fix_patch_uv.py`: local closure UV mapping; original attribute rows retained.
- `visual-deformation-check.json`, `pose-proof.png`: 52 native diagnostics, 24 representative views.
- `before-after.png`, `review-front/left/back/right.png`: patch and matched whole-model comparisons.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/sloth-review-2026-11-15/`, with snapshots here. Reproduce with diagnosis, local repair, UV correction, independent audit, renders/poses and packaging. Project Blender-export, rigging and optimization guides informed the workflow. No paid generation, commits or edits to existing authored lanes.

Cat, Owl, Honey Badger and Axolotl have verified rigged inputs and four references, queued for individual repair passes in `docs/art/moba/CREATURE_FACTORY_REPAIR_QUEUE_2026-11-15.md`. Their geometry has not yet been repaired by this pass.
