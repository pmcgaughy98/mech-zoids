# Spider surface restoration v1

Preston supplied the actual rigged spider, Meshy_AI_spider_textured_25k_20261111_character.glb. It has one bound skin, 52 joints and no animation clips. Its render has widespread missing surface, not just a few isolated holes: the position-matched audit found 18,312 boundary edges and three over-shared edges. The older static eight-leg touch-up was also fragmented, so it was not used as replacement surface geometry.

Restored the intact high-detail original while retaining the accepted eight-leg anatomy. The original quality archive has extra generated limbs; it is labeled as a quality reference, not approved anatomy. The earlier accepted cut labels remove L1/R1 and L5/R5. Those exact labels were reproduced on the old proxy, transferred by nearest proxy surface to the intact source, and smoothed as a classification field only. A continuous level-set cut produces clean contours; only the five newly created leg-root openings were capped. Source surface positions were not broadly smoothed or remeshed. The original source was closed before the cuts; the result remains closed.

## Delivery

- `spider-restored-eight-legs-rigged-v1.glb`, SHA256 `23116d1f765452b7850f3d83007e3d1b7bea2137fd4a8535b4dfc15402f223f8`.
- `spider-restored-eight-legs-rigged-v1.blend`: editable restored model with the actual imported 52-joint rig, reset to rest pose.
- `spider-before-after.png`, `review-*.png`, `leg-pose-proof.png`: inspected textured evidence and version comparisons.
- `spider-damaged-rigged-input.glb`: unchanged downloaded input, SHA256 `b7b81dfbc4100d628ed1316ec3e4987e3745ac0e2139be546fbf1a94dd12128b`.

This is a high-detail review asset: 411,610 triangles, 252,010 attribute vertices. Optimisation is deliberately separate from surface restoration. It has not been installed as a gameplay model or crowd-performance-tested. The original archive, accepted static touch-up and raw rigged download remain available.

## Rig, materials and weights

Retained the downloaded skeleton's nodes, hierarchy, skin definition, rest transforms, inverse bind matrices and scene structure exactly. The entire original downloaded binary buffer is retained as the new buffer's prefix. No new skeleton or rigging service was used.

Because the damaged geometry was replaced, weights were transferred from the actual downloaded rig: four nearest samples weighted by inverse fourth-power distance, reduced to the strongest four joint influences and normalized. UV seam copies receive identical spatial queries. Mean transfer distance for the main surface is 1.55 cm, 99th percentile 5.63 cm, maximum 16.7 cm; root caps have mean 2.73 cm and maximum 9.60 cm. These distances and the diagnostic pose tests establish a usable review candidate, not final animation polish. Preserved the intact source's UV/material/texture detail, adding a local purple finish at removed-leg roots. Damaged downloaded materials/textures remain archived in the file; they were not repainted or regenerated.

## Verification

The actual exported GLB was audited across both primitives: zero geometric boundary edges, zero over-shared edges and zero collapsed triangles after accounting for UV/normal splits at 1 micrometre. Weights are finite; maximum sum error is 1.79e-7 and maximum joint index is 51. See export-topology-audit.json and rig-transfer-verification.json.

Inspected front, both sides, back, top, underside and three-quarter captures. Eight physical feet were counted in the top/underside views. Tested each of the eight native leg roots by +/-10 degrees around local X and the head root by 8 degrees, one at a time. All tests evaluate finite positions and zero measured UV-split seam separation. Details are in visual-rig-check.json; no authored walk or exhaustive extreme-pose test is claimed.

The Workshop entry compares the original quality archive (extra legs labeled), damaged rigged download and restored eight-leg rig. Original generation sheets remain unchanged and separately selectable with R; C toggles native model comparison. The final Godot model review PASSED, including native versions, original/revised sheets, actual 52-joint import and current ChaseCamera3D fixture. Screenshots in reports/model_catalog/spider-restoration-v1/ were inspected. This is not a full match/gait/performance test; the checker reads the entry's expected joint count instead of assuming a 21-joint bird/cobra rig.

## Reproduction and limits

Local Blender 5.2.2, Python/NumPy/SciPy/Pillow and Godot 4.7.2; same project modeling/rigging/export/render guides as preceding repairs. No paid tools, new generation, downloads, installs or commits.

Run export_cut_mask.py, then restore_surface.py in Blender, bind_restored.py in Python, review_restored.py in Blender, and package_restored.py in Python. The accepted-cut-mask.npz records the source proxy triangles and removal labels. Scripts retain absolute paths and reproduce only this isolated output. The first centroid-based cut trial left pinholes and was rejected; the delivered surface uses nearest-surface classification and continuous contours. Blender's optional thumbnail-cache write failed outside workspace; the actual .blend saved successfully.

Remaining review work includes optimisation, rigid-armor deformation polish, actual gait/contact tests, final eye/socket and proportion review. Original generation sheets are visual guides and do not justify restoring extra generated legs. No Gorilla/Rhino/Kangaroo authored assets were edited.
