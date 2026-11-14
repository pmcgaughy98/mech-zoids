# Bison local topology repair v1

November 11, 2026. Next roster repair after Mantis. The four original generation sheets were inspected together with the downloaded rig and intact pre-remesh source. Four walking legs, two horns, a single segmented tail and the roof exhaust bank are retained. The mesh has four exhausts arranged in two rows; each original orthographic view shows two visible stacks, consistent with depth overlap. There was no extra-limb correction to make.

## Exact inputs and result

Downloaded rig: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bison_remeshed_25k_20261108_character.glb`, SHA256 `0a688dc0dc7b69f509ed427f0f9c78ab4f8503ec508e91aded136eac07eb80f0`. It has 47 bound joints, 22,181 triangles and no animation clips. The old Workshop statement that Bison was unrigged was stale.

Intact pre-remesh archive: `art/model_catalog/sources/bison_front - Hunyuan 3D v3.1 Pro.glb`, SHA256 `45586e24104722d455498fc882e945d1d5b23a091035d98f7df425b14c1c11ee`, 499,802 triangles. The archived source is closed. It is the original generated model, not an independently verified exact Meshy upload.

Result: `bison-rigged-local-repair-v1.glb`, SHA256 `23fc1f64d22ecab9fc70351cfcfd1b3323b504cbda45c394739579fa58690354`, 22,122 triangles. Editable native review scene: `bison-rigged-local-repair-v1.blend`.

## What changed

The position-matched audit found 115 boundary edges and 53 edges shared by more than two faces. The visible damage was small local folds, an isolated malformed triangle and two triangular openings, including defects beside the leg armor. Sixty-one malformed triangles were removed, including a tiny four-triangle closed flap attached to a hoof by one edge. Two local triangles close the remaining openings with outward winding. The first closure uses existing texture corners. The second closure crossed multiple texture islands and sampled striped orange detail; it now uses a separate local grey material on that one triangle. Total removed triangle area is 0.002402 square metres; the largest removed triangle is 0.0003915 square metres.

Triangle connectivity and the material assigned to one new closure changed. The entire downloaded binary buffer remains a byte-identical prefix in the repaired GLB. Existing positions, normals, UVs, joint indices and weights are byte-identical, with no added vertices. Skeleton nodes, hierarchy, rest transforms, inverse binds, original materials, images, samplers, textures, scenes and animation declarations are retained exactly. One grey closure material and an associated one-triangle primitive were appended, sharing the original vertex attributes and skin data. No weight transfer, rerigging, remeshing or Blender re-export was needed.

The final position-matched topology has zero boundaries, zero over-shared edges and zero collapsed triangles. Full-detail original geometry was used for comparison only; this local repair does not reconstruct detail lost during the original remesh or change the source model's existing shapes, texture bake or generic rig mapping.

## Review evidence

`repair-verification.json` records exact hashes, removed triangles, cap choices and preservation checks. `input-audit.json` records both inputs. `export-topology-audit.json` independently audits both exported primitives, including the separate closure. `visual-deformation-check.json` identifies the fresh-import tested hash, original-source display alignment and six diagnostic poses covering the four legs, head and tail. All six have zero measured UV-split seam separation. Diagnostic bends are not finished walking or contact animation.

Godot's final Workshop check passed with all three native model versions, original/revised sheets, 47 bound joints and the current ChaseCamera3D fixture. Screenshots in `reports/model_catalog/bison-repair-v1/` were inspected. Log: `D:/dev/_scratch/mech-art-direction/bison-review-2026-11-11/godot-review.log`. This is a review fixture, not full playable-match or contact-animation validation.

Textured front, both sides, back, top, underside and three-quarter renders use matched framing. `before-patch-*.png` and `after-patch-*.png` show the local gap repairs. `review-*.png` sheets and the Workshop native comparison visibly retain the intact pre-remesh original alongside the downloaded rig and repaired copy. Original source GLBs and generation sheets remain immutable. C toggles native versions; R toggles original generation sheets and revised comparison sheets.

Local tools: Blender 5.2.2, Python/NumPy/SciPy/Pillow and Godot 4.7.2, following project rigging, optimization, export and render guidance. No paid tools, downloads, installs, gameplay replacement or commits. Reproduction scripts use absolute source paths. Blender may report failure writing its optional thumbnail cache outside the workspace while still saving the actual scene successfully.
