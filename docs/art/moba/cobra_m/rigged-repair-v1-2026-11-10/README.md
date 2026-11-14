# Cobra rigged local repair v1

First repair slice, November 10, 2026. This closes local topology defects in the latest downloaded rigged cobra. It does not restore all detail or finish lost during remeshing. The flat side cap still has a visible shading/texture defect relative to the intact comparator; keep that on the next repair queue.

## What changed

The downloaded mesh had 32 small triangular fins attached to edges already shared by two surface triangles, plus four narrow openings with doubled-back triangular flaps. Removed 36 malformed triangles and closed the four resulting triangular openings using existing vertices. Triangle count: 23,712 to 23,680. The geometric audit, accounting for UV/normal splits with a temporary 1 micrometre position match, changes from 80 boundary edges and 32 edges shared by more than two triangles to zero of either. No actual source vertices were welded or moved.

The exported GLB appends a replacement triangle-index accessor. Every byte of the original binary buffer remains unchanged as its prefix, including positions, normals, UVs, joint indices, weights, inverse bind matrices and embedded textures. Node transforms, skeleton hierarchy, skins, materials, textures and scene definitions are unchanged. Original unused indices remain in the file. There are no new vertices and no weight transfer or Blender re-export. The source contains 21 joints and no animation clips; this repair does not add gameplay animations.

## Evidence and limitations

- `repair-verification.json`: source/output hashes, changed triangles, exact preservation assertions and topology audit.
- `visual-and-deformation-check.json`: fresh Blender import, matched display alignment, and actual rig pose tests. Bone_010 and Bone_008 were bent by positive/negative 12 degrees around their local X axes; Bone_016 by 8 degrees. These are diagnostic bends, not authored movement clips. Vertex positions remain finite; over 5,000 vertices move in each tail test and over 4,900 in the neck test.
- Textured front, side, back, right, underside, top and three-quarter captures; `patch-closeups.png` and `rig-deformation-proof.png` were visually inspected. Some repaired openings cross UV seams; patch triangles use existing UV values selected for a compact local island. Original texture files and all existing UVs remain intact.
- Godot Workshop check passed: three native comparison models, original/review-sheet switching, enlarged review sheet, 21-bone rig, and an isolated floor fixture using the actual current ChaseCamera3D script at FOV 60. This is a camera/import check, not a playable cobra kit or a full arena match test. Evidence: `reports/model_catalog/cobra-repair-v1/`.

The intact comparator is the accepted full-detail single-tail correction in the adjacent `tail-correction-2026-11-10` folder. Its shape aligns closely with the new rigged download at uniform scale 4.016615, with mean sampled nearest distance about 1 cm. It is the relevant pre-remesh quality reference; the exact upload transaction was not independently verified. The original generated two-tail source and its four generation sheets remain archived unchanged.

## Review in game

Open Mech Workshop and select Cobra. C toggles three-model comparison: intact before remesh, downloaded remeshed/rigged input, local repair v1. R switches original generation sheets and labeled rendered comparison sheets. Q/E turns the view. Click a sheet to enlarge it. Display scale is for comparison; production source transforms remain intact.

Only Cobra's review/display fields were updated in `art/model_catalog/catalog.json`. No gameplay model, controller, kit, other mech or original generation sheet was replaced. `cobra-remeshed-rigged-input.glb` preserves the unrepaired download. The repaired GLB and editable `.blend` are versioned here.

## Tools and reproduction

Local Blender 5.2.2, Python/NumPy/SciPy/Pillow, and Godot 4.7.2. Project skills: atlas-rigging, atlas-asset-optimization, blender-export-pipeline, dom-blender-render-automation. No paid services, generation, remeshing, rerigging, installs or commits.

Run `repair_cobra.py` with system Python; run `review_cobra.py` with background Blender, then with `-- --right-only`; run `package_review.py` and `register_review.py` with system Python. Scripts retain absolute source/output paths for reproducibility. Godot: open scenes/mech_catalog.tscn with `-- --cobra-repair-check`; use a writable log path. No second Godot renderer should be running. A sandboxed launch stalled on Windows certificate-store access; the approved outside-sandbox bounded run passed. Blender's optional thumbnail-cache write failed outside workspace, but the editable file saved successfully.
