# Axolotl: first local repair pass

Completed November 15, 2026, in Preston's new Creature Factory batch. Four legs/feet, six gill stalks, eyes, head, paired side cylinders, dorsal armor and complete tail retained.

![Downloaded rig and local repair](review-front.png)

Removed 21 malformed triangles and closed 1 small openings. Final export: 25,304 triangles; zero open edges and zero collapsed triangles. All 25,303 retained source triangles remain exact, including closed source components. 7 balanced original assembly contacts remain. No anatomy removal, remesh or rerig.

All original position/normal/UV/skin rows remain exact; no duplicate rows were needed. The original 31-joint hierarchy, rest transforms, inverse binds, scene nodes, materials and textures are unchanged. Original binary remains an exact prefix.

All 31 original controls were tested: 31 above the 1 mm visual-movement threshold, 0 below it. Maximum measured coincident-surface separation: 0 m. 16 representative poses, any local closure close-ups, and textured front/back/both sides/top/underside/three-quarter views were inspected. Native workspace is saved in rest pose with four packed immutable reference PNGs. These diagnostics do not establish finished authored movement.

The native Godot Workshop two-version/original-review-sheet/31-joint/ChaseCamera3D check passed. All seven final screenshots were inspected. Existing entries remain preserved. New compact selector rows and fitted overview framing keep the growing lineup visible.

## Source and limits

Existing generated/baked detail and automatic skin grouping remain; authored swim/walk and final visual polish remain. No gameplay installation, paid generation or new rig. No intact pre-remesh GLB was located. The two-version comparison explicitly shows archived downloaded rig before local repair; no proxy or duplicate rig is presented as an intact original. Four original generation PNGs remain separate from revised model sheets. Concept projection differences are reconciled conservatively; no new kit, names or gameplay rules were selected.

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_crimson_aXOltol_remeshed_25k_20261114_character.glb`, SHA256 `ac1315bed7f815b91de02f118acdc1e30111087066dc41c21b66e364b72a69f4`; 25,324 triangles, 31 joints, zero authored clips. Exact copy archived in `art/model_catalog/sources/` under the original filename.

Output: `axolotl-rigged-local-repair-v1.glb`, SHA256 `52c6f003c1061aa5b1c2876261f9af9951d397de5f9f641a5f32d76ccef42591`. Editable native file has the same basename with `.blend`.

Evidence: `repair-verification.json`, `independent-export-audit.json`, `visual-deformation-check.json`, `pose-proof.png`, four `review-*.png` sheets, `final-review-verification.json`, and `godot-review.log`. Canonical scripts: `D:/dev/_scratch/mech-art-direction/axolotl-review-2026-11-15/`, with snapshots here. Project Blender-export, rigging and optimisation guides informed the checks. Original downloads/reference PNGs, existing authored lanes and previous repairs remain unchanged. No commits.
