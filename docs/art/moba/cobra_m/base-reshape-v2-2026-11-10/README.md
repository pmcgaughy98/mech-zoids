# Cobra left-base restoration v2

Preston identified the malformed left side at the bottom of the upright body, where the generated extra side tail had joined. The earlier tail removal closed a cut through that junction, leaving an oversized flat slab and missing the opposite side's curved armor. Topology repair v1 did not correct that proportion error.

This version replaces the damaged left lower-body patch with mirrored geometry and UV mapping from the healthy right side of the actual rigged model. It restores the rounded transition, gray/gold armor, green plates and cyan detail. The original generated sheets were checked: the side views support a continuous armored bend into one tail, with corresponding side fittings. This is local anatomical reconciliation; the curved tail is not symmetrized.

## Files

- `cobra-rigged-base-reshape-v2.glb`: delivered candidate, SHA256 `7996566b080693278f24e26a104618fea5f4e8eb8fa697edacafd1bbfa0bc12e`.
- `cobra-base-reshape-v2.blend`: editable scene with the actual imported rig, reset to rest pose.
- `left-base-before-after.png`: damaged left side, restored left side, healthy right side mirrored only for visual comparison.
- `review-*.png`: labeled intact pre-remesh / downloaded rigged input / repair v2, in matched views. Original generation sheets remain separate and unchanged.
- `base-rig-proof.png`: four diagnostic poses around the repaired base and tail root.
- `verification.json`, `patch-topology.json`, `deformation-check.json`: construction, preservation and deformation evidence.

## Rig and source preservation

Started from the versioned rigged topology repair v1, not the static pre-remesh model. Skeleton nodes, 21-joint hierarchy, rest transforms, inverse bind matrices, original materials and original embedded textures remain unchanged. The complete original GLB binary payload is retained as the new buffer's prefix. No clips existed in the input; none is fabricated here.

The replacement patch reuses the opposite surface's UV layout and transfers its weights onto the same existing joints. The cut ring is conformed/resampled to the donor contour, and local weights fade to the retained body's existing weights over 10 cm. Both sides of each UV seam use the same boundary weights. New/interpolated weights keep the strongest four influences and normalize them. Outside the affected patch and stitch, 23,145 original vertex rows are reused byte-for-byte, including their original joint order and weight values. The maximum cut-ring displacement is about 7.1 cm. No source file was overwritten, no skeleton was rerigged, and no body-wide remesh was used.

Final mesh: 25,510 triangles and 27,353 attribute vertices. Position-matched audit at 1 micrometre: zero boundary edges, zero over-shared edges, zero collapsed triangles. Two tiny stitch-corner triangles under a 3 mm bounding size were explicitly closed after resampling. Original intact and unrepaired rigged comparison models remain available.

## Validation

The exact delivered hash was freshly imported in Blender. Bone_001 was bent by +8/-8 degrees and Bone_014 by +10/-10 around their local X axes. All evaluated positions remain finite, and sampled UV-split positions remain coincident in all four tests (maximum measured gap zero). The 99th percentile edge-stretch ratio remains below 1.037; the worst individual ratio is about 1.208 at the negative tail-root bend. These are basic seam/deformation checks, not finished animation clips or exhaustive extreme-pose validation.

Inspected textured close-ups and full front, side, opposite side, back, underside and three-quarter renders, plus the four deformation captures. The approved bounded Godot review passed with three native model versions, original/review sheets, a 21-bone Skeleton3D and the current ChaseCamera3D fixture at FOV 60. Screenshots: `reports/model_catalog/cobra-base-repair-v2/`. This is model import/view validation, not a full playable cobra match test.

Only the Cobra Workshop display/review fields were advanced to v2. C shows the three model versions; R switches original generation sheets and revised comparison sheets. The pre-remesh comparator includes the earlier tail cut and is a quality baseline, not an approved anatomy target. The original two-tail archive is preserved as well. No gameplay/controller assets or other lanes were changed.

## Tools and reproduction

Local Blender 5.2.2, Python/NumPy/SciPy/Pillow, Godot 4.7.2; project rigging, optimization, Blender export and render skills. No generation, purchases, installs or commits. Blender's optional thumbnail-cache write outside workspace failed; the editable file itself saved successfully.

Run `mirror_patch.py` with system Python, `review_base_v2.py` with background Blender (then `-- --final` for the exact final export and pose evidence), then `package_base_v2.py` with Python. Source/output paths are recorded in the scripts. A preceding radial-shrink trial was rejected because it retained the slab and stretched texture; `REJECTED-radial-shrink-projection.json` is historical diagnosis, not the delivered construction. Blender backup files are not delivery targets.
