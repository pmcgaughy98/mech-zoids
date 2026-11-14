# Golden Beetle objective repair v1

Superseded for the front legs by [v2](../front-leg-restoration-v2-2026-11-13/README.md). Preston identified duplicated shins/feet that the initial local-topology pass missed. V1 is retained as historical evidence.

Completed November 13, 2026 after the usage interruption. This is the coin-shell Golden Beetle objective, separate from the roster's Bombardier Beetle. The four downloaded coin_beetle reference views support six walking legs, paired steel mandibles, round coin armor and a stack magazine. Those features remain.

## Files and provenance

- Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_coinclaw_mech_remeshed_25k_20261111_character.glb`, SHA256 `100b37f26e5f279080350e7111df45f2bd7539f1937a9123165d5ea5d14b7946`.
- Exact input archive: `art/model_catalog/sources/Meshy_AI_coinclaw_mech_remeshed_25k_20261111_character.glb`.
- Result: `gold_beetle-objective-repaired-v1.glb`, SHA256 `50833a9affe40bbb55d541987babef09d9233bfca9dd7bb47bb874d24d45ca19`.
- Editable native file: `gold_beetle-objective-repaired-v1.blend`, with four exact reference PNGs packed and provenance text inside.
- Exact downloaded PNGs: `art/model_catalog/references/gold_beetle/{front,left,back,right}.png`. Hashes and original paths are in `catalog-entry.json`. Creature identity and limb intent were checked visually; the PNGs do not hash-match the older project reference packs, so an exact historical generation-job link is not claimed.

The true pre-remesh generated GLB was not found in the supplied folders or available MeshForge library. The map's reduced/scaled runtime copy is derived from this same rigged input, so it is not a substitute for a pre-remesh original. Workshop and revised sheets honestly show two versions: downloaded rig, then repair. Original PNGs and archived GLB bytes remain unchanged.

## Geometry and rig

Removed 30 malformed triangles, including a tiny 22-face inside-out coin-shell blister, and closed one local coin-rim opening using existing vertices/texture corners. Output is 25,866 triangles versus 25,895 in the input. All 25,865 healthy original main-body faces remain. No new vertices or shape changes were introduced.

Only the triangle indices changed. Every original position, normal, UV, joint-index and weight row is byte-identical. The complete original binary buffer is retained as an exact prefix; replacement indices are appended. Original nodes, skeleton hierarchy, rest transforms, inverse binds, 23 bound joints, scene, materials and embedded textures are unchanged. No animation clips were present.

Independent final-file audit found zero boundary edges and zero collapsed triangles. Two original four-face contacts between closed assembly surfaces remain, with balanced face winding; these are explicitly protected and are not presented as globally manifold topology. Removing healthy coin/head surfaces merely to reach a zero over-shared count was avoided. See `repair-verification.json` and `independent-export-audit.json`.

## Review and limits

Matched front, both sides, back, top, underside and three-quarter renders were made. Coin closure, both stack magazines and mandibles were checked in `local-proof.png`. Nine independent native-joint tests cover all six legs, head, mandibles and shell, with zero measured separation between coincident surface copies. Pose evidence is in `pose-proof.png` and `visual-deformation-check.json`, tied to the final GLB hash. These are diagnostic bends, not a finished gait.

Workshop access: select Golden Beetle in the Objectives row. C compares native versions; R switches immutable source PNGs and labeled rendered review sheets. Godot's final native comparison, 23-joint import, original/review sheets and current ChaseCamera3D fixture check passed. The expanded lineup, comparison and chase-camera screenshots were inspected in `reports/model_catalog/gold-beetle-objective-v1/`.

This is a local repair at the rigged download's resolution. Baked texture roughness and lost pre-remesh detail remain. No new generation, rerig, remesh, authored map replacement or gameplay hookup was performed. Existing map assets and other models were preserved.

## Reproduction

Canonical scripts/configuration: `D:/dev/_scratch/mech-art-direction/objective-repair-2026-11-11/`. Run `repair_objectives.py`, Blender `review_objective.py -- gold_beetle`, then `audit_objectives.py` and `package_objectives.py --publish`. Both objective inputs and their saved diagnosis/configuration are required. Local script snapshots here record the implementation; their original scratch-root dependencies are intentional. Blender 5.2.2 and local Python/Godot were used. Relevant project-local rigging/export/render/optimization guides informed the existing review workflow. No paid tools, credential access or commits.
