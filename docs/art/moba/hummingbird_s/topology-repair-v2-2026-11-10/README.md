# Hummingbird topology repair v2

Continues the verified straight-needle v1. Removed 78 malformed flap triangles and closed four small triangular openings. Several flaps are tessellated strips; they were traced as small face components attached along over-shared edges, rather than removing neighboring armor indiscriminately. One wing opening became apparent after removing its folded strip.

Final candidate: `hummingbird-rigged-needle-topology-v2.glb`, SHA256 `7f747017c931de61224a94914b342b33b0b62a70b6db40b47173cbe30797fcff`. Editable scene: `hummingbird-needle-topology-v2.blend`.

The position-matched geometric audit changes from 139 boundary edges and 63 over-shared edges to zero of either, with no collapsed triangles. Triangle count changes from 22,236 to 22,162. No source vertex was moved, added, welded or reweighted during this pass. It only appends a replacement triangle-index accessor. The entire v1 buffer remains as an unchanged binary prefix, including the repaired needle positions, original joint indices/weights, bind matrices, normals, UVs and embedded textures. Skeleton hierarchy, 21 joints, rest/node transforms, materials, scenes and any animation metadata are unchanged. No rerig or remesh.

Closed faces reuse existing vertex/UV data, with outward winding checked against neighboring normals. The needle length and downward aim remain as in v1. The original generated archive, raw rigged download, needle v1 and original four generation sheets are all preserved.

The final wing closure initially sampled an unrelated red atlas area. All three corner indices were reselected from existing coincident-position UV copies to keep the triangle in a compact green island. No original UV or image was edited. The corrected green closure was freshly rendered and visually inspected before delivery.

## Evidence

`repair-verification.json` records exact input/output hashes, changed triangle IDs, patch bounds and preservation assertions. `visual-deformation-check.json` records a fresh import of the exact delivered hash. Textured front, both sides, back, underside and three-quarter views, four local before/after close-ups, and actual head/left-wing/right-wing poses were rendered for inspection. The diagnostic joints are Bone_005 (+10 degrees local X), Bone_016 (+15 local X) and Bone_020 (-15 local X). These are diagnostic poses, not new animation clips.

Godot review PASSED on the final export: `-- --model-repair-check --review-model=hummingbird --review-output=res://reports/model_catalog/hummingbird-topology-v2`. This verifies native version comparison, original/revised sheets, the 21-bone import and current ChaseCamera3D fixture; it is not a playable kit/match test. The Workshop's Hummingbird entry is on v2; C compares intact/remeshed/repaired models, R switches original/revised sheets.

This repairs local topology, not every possible proportion, eye, texture or normal issue. Intact-versus-remesh comparison remains available for further visual review; final needle length is still an independent design judgment. No gameplay model or other mech was replaced.

## Reproduction

Run `repair_topology.py` with local Python/NumPy/SciPy. Run `review_topology.py` in background Blender 5.2.2, then `package_topology.py` with Python/Pillow. Absolute source paths are embedded. The original donor archive is read-only; the previous needle correction is the repair input. Local rigging/export/render guides were followed; no paid tools, generation, installs or commits. Blender's optional thumbnail-cache write outside workspace may fail while the scene itself saves correctly.
