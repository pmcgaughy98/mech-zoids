# Chameleon local repair v1

November 11, 2026. Next roster repair after Beetle joint-restoration v2. Compared the actual rigged download with all four original generation sheets and the intact pre-remesh archive. Four legs, two large gold-rimmed eyes, muted prism panels and a single straight segmented tail are retained. No anatomy cut or proportion change was needed.

## Exact files

Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_chameleon_remeshed_25k_20261108_character.glb`, SHA256 `9cda17916f12b1b576a1a6b20ff48166bdf073bdbd56fc266dc046599d2f4ba4`, 23,932 triangles, 30,845 attribute vertices, 51 bound joints and no animation clips. The old static/unrigged catalog status was stale.

Intact quality archive: `art/model_catalog/sources/chameleon_front - Hunyuan 3D v3.1 Pro.glb`, SHA256 `9199eccfebf19216cad0e1100b9ba35236f0941394aed89d8ca090843e8770e4`, 500,000 triangles and closed topology. This is the original generated archive, not an independently verified exact historical Meshy upload.

Result: `chameleon-rigged-local-repair-v1.glb`, SHA256 `8672cbd2d2dc49b5b2bb8c6d69c10ba56d0ea3c445270bfa45298cc481d6e5b0`, 23,890 triangles. Editable native review scene: `chameleon-rigged-local-repair-v1.blend`.

## Changes and preservation

Removed 46 malformed flap triangles, including tessellated strips and a thin four-triangle closed flap attached to the roof rail by a single over-shared edge. Closed four small local gaps using existing vertices and nearby existing texture corners. The gaps were at the upper side, front foot, roof frame and snout. Total removed triangle area is 0.007593 square metres; largest removed triangle 0.0007824 square metres.

Only the triangle index list changed. The entire original binary buffer remains byte-identical at the beginning of the new GLB, and the replacement index list is appended. All original positions, normals, UVs, joint indices and skin weights remain byte-identical. Skeleton nodes, hierarchy, rest transforms, inverse binds, skin, scene, original materials, images, textures, samplers and animation declarations are retained exactly. No vertices, materials or skin data were added. No geometry smoothing, weight transfer, retexture, remesh or rerig occurred.

The source position-matched audit found 86 boundary edges and 35 edges shared by more than two faces. The actual exported result has zero boundary edges, zero over-shared edges and zero collapsed triangles. Skin weights remain finite and normalized, with valid joint indices. Detailed hashes, removed triangle IDs, cap choices and preservation checks are in `repair-verification.json`; independent exported-file checks are in `export-topology-audit.json`.

## Inspection and limits

Matched textured front, both sides, back, top, underside and three-quarter renders compare intact pre-remesh original / downloaded rig / repaired copy. Four local before/after gap close-ups, both eyes and the roof rail were inspected. The local proof montage enlarges the same crop in both versions for visibility; full original review frames remain available.

`visual-deformation-check.json` records the exact final hash and ten independent native-joint tests covering four legs, tail root and middle, head, snout, a front toe and body. All ten have zero measured UV-split seam separation. Tests restore saved imported rest-pose matrices between poses and measure only rendered-surface vertices. Original skin weights were not changed. These diagnostic tests do not establish polished gait or foot-contact animation.

Godot's final Workshop check passed with three native versions, original/review sheets, the expected 51 bound joints and current ChaseCamera3D settings. Comparison and actual-camera screenshots in `reports/model_catalog/chameleon-local-v1/` were inspected. Log: `D:/dev/_scratch/mech-art-direction/chameleon-review-2026-11-11/godot-review.log`.

This pass repairs local geometric defects at the rigged input's resolution. Original texture-bake roughness and lost pre-remesh surface detail are not reconstructed. The quality archive and original generation sheets remain unchanged and separately labeled. Workshop C compares the three native versions; R switches original generation sheets and revised rendered comparisons. No gameplay asset/controller installation is claimed.

Local Blender 5.2.2, Python/NumPy/SciPy/Pillow and Godot 4.7.2, following project rigging/export/render guidance. No paid tools, downloads, installs, source overwrites or commits. Reproduction scripts retain absolute input paths.
