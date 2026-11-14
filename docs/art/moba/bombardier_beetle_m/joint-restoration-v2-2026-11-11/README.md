# Beetle front ball-joint and shoulder restoration v2

November 11, 2026. Preston identified two defects in v1: the removed-leg area was ragged, and the cut took part of the retained front leg's ball joint. The previous weight-based cut crossed shared shoulder armor. V2 rebuilds this area from the untouched rigged input, protects the retained front ball joints explicitly and removes pair 2 at its own narrower distal joint. Six walking legs remain.

## Verified source and result

Source rig: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bombardier_beetle_remeshed_25k_20261108_character.glb`, SHA256 `4ab1d8eac7802448813f95edc29e3be959c075268d4b6a28ca149897d3fcb0a1`, 64 bound joints, 25,642 triangles, no animation clips. The four previously repaired malformed folds stay removed in the staged input.

Result: `bombardier-beetle-joints-restored-v2.glb`, SHA256 `430d478ef15416b45805c2396894ac57e8c3e602c44d833c5435c8f8119b598a`, 24,806 triangles. Editable review scene: `bombardier-beetle-joints-restored-v2.blend`. V1 remains archived in `../pair-2-removal-v1-2026-11-11/` and is superseded by this correction.

`restored-joint-verification.json` compares actual exported triangles against the untouched staged source and v1. All 1,899 protected front-joint source faces are present intact; 110 of these were missing or clipped in v1 and are restored. Across the shoulder region, 1,065 original source faces are restored relative to v1. Original source position, normal and UV rows remain byte-identical. The independent low-foot connected-surface audit finds six feet, also checked visually from the underside.

## Repair boundaries and finish

The original blue upper mounting panels and gold shoulder fittings are retained as body armor. The cut uses only the distal portions of pair 2's native chains, with an independent geometric guard around both retained front-leg upper joints. It no longer relies on the full removed-chain weight field to establish the shoulder boundary.

The two new narrow cut rings are rounded in their own joint planes, finished with small gold bevels and closed by blue disks inset 12 mm. Only newly introduced contour positions are adjusted, with a maximum offset of 3.32 cm. The original ball joints and torso positions are not moved, shrunk or broadly smoothed. Two local finish materials are appended; original materials and embedded textures remain unchanged.

The source skeleton nodes, hierarchy, rest transforms, inverse binds, skin, scenes and original binary buffer are preserved. Residual removed-chain weights are reassigned to existing body parent Bone_001, including the restored fixed shoulder armor. Affected original skin rows: 4,117; unchanged original skin rows: 23,282. New contour/cap/bevel rows: 413. The unused pair-2 joints remain in the hierarchy with no positive rendered-surface weight. This is a local skin adjustment on the existing rig, not a rerig.

`export-topology-audit.json` checks all three exported primitives together: zero boundary edges, zero over-shared edges, zero collapsed triangles, finite normalized weights, valid joint indices and outward-facing closure disks. Topology checks alone did not catch v1's anatomical mistake; the source-face restoration check and matched close-ups address that separately.

## Review artifacts

The fixed-camera `prior-joint-*.png` and `after-joint-*.png` images compare v1's damaged ball/shoulder area against v2. `before-joint-*.png` shows the untouched rigged input. Seven full textured views, original-quality comparisons, native-joint poses and a native editable scene are included. The final pose report identifies the exact tested GLB hash, six retained leg tests, head/body tests and both unused removed-leg controls. Tests restore saved imported rest matrices between poses and exclude unused archived vertices.

All ten final native-joint checks passed with zero measured seam separation. Both unused removed-leg controls produce exactly zero rendered-surface movement. Additional close-ups show the restored front joints during their native leg bends. The exact-hash source-face regression and six-foot checks also passed.

Godot's final Workshop check passed with three native comparison versions, original/revised sheets, the expected 64 bound joints and current ChaseCamera3D settings. Comparison and camera screenshots in `reports/model_catalog/beetle-joints-v2/` were inspected. Log: `D:/dev/_scratch/mech-art-direction/beetle-review-2026-11-11/godot-joints-v2.log`.

The Workshop and revised model sheets retain three versions: intact pre-remesh quality archive, original eight-leg rigged download and current six-leg v2. Original generation sheets and all input GLBs remain unchanged. The intact archive still has unapproved extra legs; it is clearly labeled as a quality reference. R toggles source/review sheets and C toggles native versions.

No new clips, full playable-match validation, gameplay installation, source remesh, rerig, paid generation or commits. Reproduction scripts use absolute local paths. Local Blender/Python/Godot tools only.
