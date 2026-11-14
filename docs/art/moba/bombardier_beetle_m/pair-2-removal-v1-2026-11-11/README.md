# Bombardier Beetle: walking pair 2 removal

Superseded by `../joint-restoration-v2-2026-11-11/`: Preston identified that this v1 cut damaged the retained front ball joint and left a poor shoulder closure. V2 restores the original joint and shared shoulder armor, keeps six legs and closes the removed leg at its own narrower fitting. The v1 checks below are historical and did not establish correct retained anatomy.

November 11, 2026. Preston explicitly selected pair 2 in the numbered underside diagram. Pairs 1, 3 and 4 remain: six walking legs. The paired antennae, mandibles and forward shoulder nozzles are retained. The original archive and downloaded rig both had an extra walking pair; the archive remains a quality reference, not approved anatomy.

## Exact inputs and output

Actual downloaded rig: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bombardier_beetle_remeshed_25k_20261108_character.glb`, SHA256 `4ab1d8eac7802448813f95edc29e3be959c075268d4b6a28ca149897d3fcb0a1`. It has 64 bound joints, 25,642 triangles and no clips.

Intact pre-remesh archive: `art/model_catalog/sources/bombardier_beetle_front - Hunyuan 3D v3.1 Pro.glb`, SHA256 `84c287011472b8cc2a8ec68ad4369cedb61d8a02f86840a9b9ba021a4d5b8b49`, 499,604 triangles. All four generation sheets were inspected and establish a six-legged design. The exact historical Meshy upload is not independently established by this archive.

Repaired model: `bombardier-beetle-six-legs-rigged-v1.glb`, SHA256 `131af5a83628e25b2656453c605c43eed7e9441a102392e8189973b6ebc16978`, 23,698 triangles. Editable review scene: `bombardier-beetle-six-legs-rigged-v1.blend`.

## Local repair and rig preservation

Four malformed folded triangles were removed first, eliminating eight open edges and four edges shared by more than two faces. This staged cleanup preserved all original vertex/rig/material bytes. The pair-2 cut then used the existing native joint influences to identify the selected pair: Bone_034 through Bone_043. The classification field was smoothed four times without smoothing source geometry, then cut at a continuous level of .250001. This removes 2,257 source triangles, clips 210 more and closes two socket contours with 206 cap triangles. No cut-created scraps remained.

The first nonplanar closure protruded from the body. Only newly created contour vertices were locally faired and recessed to X = +/-0.69 metres. This produces flat closed sockets without moving any original vertex position. The maximum adjustment of a new cut vertex was 19.46 cm; original source positions, normals and UV values remain unchanged. One local dark-blue closure material was appended; original materials and embedded textures remain intact.

The full original binary buffer remains a prefix of the repaired file. Original skeleton nodes, hierarchy, rest transforms, inverse binds, skin, scene and animation declarations are retained exactly. No rerig or remesh occurred. There are 27,399 original attribute rows, plus 492 new contour/cap rows. Residual deleted-chain influence in 3,098 retained original skin rows was reassigned to the existing body parent Bone_001; 24,301 original skin rows remain unchanged. New contour weights are interpolated from the original boundary, normalized to four influences, then subjected to the same removed-chain cleanup. The ten unused leg joints remain in the preserved skeleton but have no positive weight on any rendered surface vertex.

`repair-verification.json` records the exact changes and affected skin rows. `export-topology-audit.json` checks the actual exported primitives together: zero boundary edges, zero over-shared edges, zero collapsed triangles, outward-facing socket triangles, finite normalized weights and valid joint indices. The source rig, archive and original generation sheets remain immutable.

## Visual and deformation review

Seven matched textured views show front, both sides, back, top, underside and three-quarter. Socket close-ups are supplied separately. `visual-deformation-check.json` identifies the exact tested hash and ten independent native-joint tests: six retained legs, head, body and both unused removed-leg controls. All ten passed with zero measured UV-split seam separation; both unused controls produced exactly zero rendered-surface movement. The pose harness restores a saved copy of every imported rest-pose matrix between tests, retaining the importer's small scale compensation, and measures only vertices used by rendered faces, excluding unused archived vertex rows. These diagnostic poses do not establish polished gait, contact or independent mechanical controls.

Godot's final Workshop check passed with all three native versions, original/revised sheets, the expected 64 joints and the current ChaseCamera3D fixture. Comparison and actual-camera screenshots in `reports/model_catalog/beetle-six-legs-v1/` were inspected. Log: `D:/dev/_scratch/mech-art-direction/beetle-review-2026-11-11/godot-review.log`. This fixture does not substitute for a full playable match or animation-contact validation.

The Workshop comparison and revised sheets show intact pre-remesh quality archive / downloaded eight-leg rig / repaired six-leg model. The archive's extra pair is explicitly unapproved. R switches original generation sheets and revised model-comparison sheets; C toggles the three native versions. This is a local anatomy and topology correction at the current rigged-input resolution, not a full-detail source reconstruction or gameplay installation.

Local tools: Blender 5.2.2, Python/NumPy/SciPy/Pillow and Godot 4.7.2, following project rigging/export/render guidance. No paid tools, rerigging, remeshing, new clips, source overwrites or commits. Reproduction scripts use absolute input paths. `walking-pair-choice-BEFORE.png` preserves the pre-cut numbered diagram.
