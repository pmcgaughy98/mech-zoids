# Shoebill fitted backplate repair

Current Workshop version: [circular rim v2](../circular-rim-v2-2026-11-13/README.md), adding the user-confirmed circular cover over the grey backing. V1 remains the archived local repair beneath it.

November 13, 2026. Preston asked for the blue donor-feather geometry folding onto the fitted moon plate to be fixed, along with the usual model, topology, rig and review pass. The actual current rigged input supersedes the older missing-rig blocker. The main Shoebill body and approved moon-plate design are retained.

![Matched backplate correction](backplate-before-after.png)

## Exact files

- Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_shoebill_single_material_25k_20261111_character.glb`, SHA256 `c0afacfd4294556e98220d6e89996a6e246430ffaf58ec3805941bd8240cb4a0`. It contains 25,844 triangles, 31,049 attribute rows, 38 bound joints and no animation clips.
- Byte-identical input archive: `art/model_catalog/sources/Meshy_AI_shoebill_single_material_25k_20261111_character.glb`.
- Result: `shoebill-backplate-repaired-v1.glb`, SHA256 `19f929756d3fcfa9a2b8fa53a1385815af0e5cf5607c6e44ac47d14c22786cb0`, 25,962 triangles.
- Editable scene: `shoebill-backplate-repaired-v1.blend`, with four exact source reference PNGs packed and provenance inside.
- Original body quality archive: `art/model_catalog/sources/shoebill_front - Hunyuan 3D v3.1 Pro.glb`, SHA256 `0130e8e37491cb50f1aedcbd9a2c3c9e93fc2eeb160925765ed0b8bbeb5e7366`, 500,000 triangles and no rig. This archive has the earlier backplate, explicitly labeled in comparisons. It is not verified as the exact historical upload of the fitted composite. The current approved moon plate is preserved rather than replaced by that earlier design.

## Diagnosis and repair

Separate geometry inspection isolated a 4,410-triangle transferred plate, 120-triangle mounting sleeve and 21,286-triangle main body. The unwanted blue feather lobes and a folded rear closure belonged to the donor plate. They were not the main body's wing geometry. Isolated views and point/ray checks confirmed the folded closure intersecting the visible moon face.

Retained 1,820 original visible plate triangles, including the moon face, silver rim and brass mounts. Removed the unwanted donor geometry and old folded rear closure; built a shallow recessed rear shell from the retained surfaces, with closed side walls and one added gray metal finish. Source surface patches meeting only at a vertex have separate rear fans with 0.2 mm offsets, avoiding four-face shared edges in the new shell. The retained visible source positions, normals, UVs and weights are unchanged.

The normal topology pass removes 27 small open flap triangles, one disconnected tiny sole scrap and one folded triangle bordering a small four-edge head opening. That opening is closed locally. The two 60-edge mounting-sleeve ends are enclosed behind the visible moon plate and toward the body; they are not filled across the moon design. These sleeve closures and the head closure add 117 triangles. All 21,285 healthy main-body triangles remain exact, including the wings, legs, eyes, bill, tail and joint surfaces.

Every original attribute row and the original binary buffer remain stored unchanged in the output; removed geometry is unindexed. New rear-shell/cap vertices copy corresponding source skin rows. No original joint indices or weights were changed. Skeleton nodes, hierarchy, rest transforms, inverse binds, 38-joint skin, original material and embedded textures remain exact. New arrays and indices are appended. No remesh, rerig, generation or retexture was used.

## Verification and review

Independent inspection of the actual final GLB verifies zero open edges, zero edges shared by more than two faces, zero collapsed triangles, nonzero triangle areas and finite normalized skin weights with valid joint indices. The source had 181 boundary edges and 27 over-shared edges. Evidence: `repair-verification.json` and `independent-export-audit.json`.

Fourteen independent native-joint diagnostic poses cover the backplate/body, lower torso, head/bill, both wing roots/tips, both leg roots/knees and both feet. All have zero measured separation between coincident surface copies. Source rest-pose matrices are restored between tests. Plate/body and full-model motion views were inspected; see `visual-deformation-check.json` and `pose-proof.png`. These checks do not establish polished locomotion or flight animation.

Original body archive, downloaded fitted rig and repaired model are rendered at matched heights, camera framing and lighting in four comparison sheets. The render excludes hidden rig custom shapes from bounds. Front, both sides, back, top, underside, three-quarter and plate close-ups were inspected. Some original remesh faceting and baked edge roughness remain; this is not a high-detail body restoration.

Godot's final Workshop check passed with three native versions, original/revised sheets, 38 imported joints and the current ChaseCamera3D fixture. Native front/back comparison and actual-camera screenshots were inspected in `reports/model_catalog/shoebill-backplate-v1/`. Select Shoebill; C compares models and R switches immutable source reference PNGs and revised sheets. The alternate Shoebill remains backplate reference only, unchanged.

## Scope and reproduction

Only the main Shoebill catalog display/review entry is advanced. Source models, original reference PNGs, other roster work, Golden Beetle v2, Wyvern and authored map/gameplay assets are preserved. There are no new animation clips or gameplay hookups.

Canonical work: `D:/dev/_scratch/mech-art-direction/shoebill-review-2026-11-13/`. Implementation and diagnosis/configuration snapshots are included here. `rebuild_plate_shell.py` uses the input GLB plus `face-components.json` and `mesh-analysis.npz`; `audit_export.py` reopens the actual result. `render_review.py` renders before/after/intact versions, and `review_rig_and_source.py` creates native pose proof and packs references. `package_shoebill.py --publish` updates the review entry while preserving other catalog entries. Local Blender 5.2.2, Python and Godot 4.7.2 only; project modeling, rigging and export guides were used. No paid services, credentials or commits.
