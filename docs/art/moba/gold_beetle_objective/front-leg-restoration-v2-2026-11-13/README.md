# Golden Beetle front-leg correction v2

November 13, 2026. Preston identified the duplicated front legs missed in the first pass. Each side had two gold shin plates and overlapping feet fused into a broad front assembly. This version reconstructs one front leg on each side from the same model's healthy middle legs, retaining three walking legs per side and matching the reference views.

![Matched front-leg comparison](front-leg-before-after.png)

## Files

Result: `gold_beetle-front-legs-restored-v2.glb`, SHA256 `e0c071ba0b6af6f9b9f38e4d974fd99ec3c12a0ec41e3cb659422709020017a5`. Editable native file: `gold_beetle-front-legs-restored-v2.blend`. The previous v1 repair and original rigged download remain immutable in their existing paths. No true pre-remesh GLB has been located.

## Local reconstruction

The source front-leg regions were identified with native-chain weights, then checked in textured side, underside and close-up views. Their original body-side contours were retained and interpolated exactly at the cut. Healthy middle-leg surfaces were copied, aligned by the original bind-joint positions, and their gray root collars blended into those contours. The copied region excludes the donor's copper magazine frame. Small connecting collars use one added gray metal material; original materials and embedded textures are unchanged.

Donor chains Bone_005/006/007 map to existing front Bone_011/012/013, and Bone_008/009/010 map to Bone_014/015/016. Residual donor-body influences map to the existing body parent Bone_001. No skeleton nodes, hierarchy, rest transforms or inverse binds changed. The foot geometry retains the healthy donor's scale and floor height. All original attribute rows and the entire input binary buffer remain stored unchanged; removed fused-leg rows are unindexed archival data. Intersections, donor vertices, weights and replacement indices are appended locally.

Independent exported-file audit verifies 25,430 triangles, 23 joints, six distinct connected ground-contact feet, zero boundary edges and zero collapsed triangles. Both original protected four-face assembly contacts remain. All 23,445 source triangles outside the front-leg influence region remain exact. See `independent-export-audit.json` and `repair-verification.json`.

## Verification

Eleven independent native-joint poses cover both front roots and ankles, all four other legs, head, mandibles and shell. Maximum measured coincident-surface separation is approximately 0.000000207 m, below the one-micrometre tolerance. Front-joint close-ups, opposite side, underside, matched before/after and `pose-proof.png` were inspected. Leaf endpoint bones are preserved without inventing new weighted controls. These diagnostic bends do not establish a polished walking animation.

Godot's final Workshop native-version comparison, original/revised sheets, 23-joint import and current ChaseCamera3D fixture check passed. Final comparison and actual-camera screenshots were inspected in `reports/model_catalog/gold-beetle-front-v2/`. Select Golden Beetle in Objectives; C compares the original rigged download with v2, and R switches source/reference sheets. The local review sheets compare the previous fused copy with v2.

The original pre-remesh surface remains unavailable, and baked texture roughness is retained. This pass changes only the Golden Beetle review/display entry; Wyvern and other roster models, source archives and authored map/gameplay assets are preserved. Script snapshots document the local reconstruction and review workflow. No paid generation, remesh, rerig or commits.
