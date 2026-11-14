# Scorpion local topology repair

Completed November 14, 2026, using Preston's newly supplied rigged export. Removed 21 single-triangle flaps and one two-triangle folded fragment, preserving all 23,970 healthy source faces. Eight walking legs, both pincers, two side vessels, eyes and the complete raised tail are retained.

![Three-stage review](review-front.png)

The Workshop lineup and revised front/left/back/right sheets now use `scorpion-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches original generation PNGs and revised comparison sheets. The intact archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Correct input and preservation

The initial `Meshy_AI_scorpion_front_Huny_1111013939_texture.glb` has no skeleton or skin weights. Preston supplied `Meshy_AI_scorpion_remeshed_25k_20261114_character.glb`; that is the actual repair input, with 52 joints and no clips. The static inspection was not published as a rigged repair. Its audit remains under the scratch directory's `static-input-inspection/`.

The repaired GLB contains 23,970 triangles and the exact supplied 52-joint hierarchy/rest transforms/inverse binds. Every original position, normal, UV and skin row, material, texture, scene and original binary prefix remains unchanged. Only a new index accessor excludes the 23 malformed triangles. No remesh, rerig, transferred weights, added vertex, material or texture.

Independent actual-file audit reports zero open edges, zero over-shared edges and zero collapsed triangles. All three healthy closed surface components are retained, including the two separate 580/668-face components; these were not misclassified as scraps.

All 52 native joints were tested with small rotations. 52 tests produced measurable surface motion, while 0 had no measurable motion. Maximum measured coincident-surface gap: 0 m, below the one-micrometre tolerance. Twenty-one representative pose renders were inspected. The editable Blender scene is saved in rest pose with all four immutable reference PNGs packed. These diagnostics do not establish independent control of every appendage or finished walking/tail animations.

Textured front/back/both sides/top/underside/three-quarter views and head/tail/leg close-ups were inspected. Native Godot 4.7.2 Workshop verification passed for all three models, original/revised sheets, the 52-joint rig and actual ChaseCamera3D. All seven final screenshots were inspected in `reports/model_catalog/scorpion-local-v1/`.

Existing baked surface roughness/detail loss and grouped rig controls remain. No gameplay/map replacement or authored clips were added. Earlier roster work and Hornet/Jellyfish's separate native-check pending states remain preserved.

## Exact files and evidence

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_scorpion_remeshed_25k_20261114_character.glb`; SHA256 `0013e0c29cc4b65a780f1cec3edcda351fb38afa089772628b26f58088d30306`; 23,993 triangles, 52 joints, no clips. Exact raw copy archived in `art/model_catalog/sources/`.

Final: `scorpion-rigged-local-repair-v1.glb`; SHA256 `3cb9fa1f8c04fb2ca8348a151f4f56d57a6953e976f5f42493d2957a47186f73`. Native editable file: `scorpion-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: topology and preservation checks.
- `visual-deformation-check.json`, `pose-proof.png`: 52 native-joint diagnostics and 21 representative views.
- `before-after.png`, `review-front/left/back/right.png`: matched local close-ups and three-stage sheets.
- `final-review-verification.json`, `godot-review.log`: final native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/scorpion-review-2026-11-14/`, with snapshots here. Guides applied: project `blender-export-pipeline`, `atlas-rigging`, `atlas-asset-optimization`. Blender 5.2.2 and independent Python GLB audits provided geometry/rig checks. Original archives/reference PNGs are preserved. No paid generation, commits or next model selection.
