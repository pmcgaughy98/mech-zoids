# Cobra single-tail correction, 2026-11-10

Delivered textured GLB:

D:/user/Downloads/cobra_front - single tail corrected.glb

Editable Blender copy:

D:/dev/new-mech-rpg/docs/art/moba/cobra_m/tail-correction-2026-11-10/cobra-single-tail-corrected.blend

![Tail correction](cobra-tail-before-after.png)

[Front, side, back and underside proof](four-view-proof.png)

## Correction and reference choice

The actual source has two complete tail branches at the base of its raised neck. Kept the continuous rearward branch along the spine (+Y in Blender Z-up) and removed the sideways generated copy (+X). This keeps the single rear-trailing body shown in the paired profile reference sheets. The front/back sheets draw the trail sideways and are not a mutually calibrated 3D turntable; they do not justify two physical tails.

Reviewed all four exact catalog generation sheets in art/model_catalog/references/cobra/. Source hash matches the catalog entry. The original full-detail downloaded model was used, not its reduced gallery proxy.

Removed the branch close to the body. Closed the local cuts and matched them with a green painted-metal closure and a small clamped outer bevel. Two local solid materials finish the new closure; no source atlas was repainted or generated. The cap is a local modeled repair, not source texture detail.

## Preservation and verification

- Original source remains unchanged at D:/user/Downloads/Mecha Beast GLB/cobra_front - Hunyuan 3D v3.1 Pro.glb, SHA256 af7353fcb7967f579bd715e64df339f52e6488958990dde25d652b47078bcfa3.
- Preserved a byte-identical source copy in D:/dev/_scratch/mech-art-direction/cobra-tail-2026-11-10/cobra-source.glb.
- All three embedded source PNG textures are byte-identical in the corrected GLB. Original material/UV intent and per-corner normals outside the local edit are retained.
- 205,635 protected source vertex samples outside the local cut region have zero position error. This covers the head/hood/raised neck and retained rear body. The cut region itself is intentionally reconstructed.
- Source: 500,000 triangles. Corrected export: 352,420 triangles, three materials and three original embedded textures. No global decimation or retexture.
- Fresh Blender re-import: zero boundary edges after accounting for UV splits, zero non-manifold edges, zero actual zero-area faces, and zero positive faces under 1e-12 source-unit squared area.
- Front, side, back, top, underside and three-quarter before/after images were rendered and inspected. Each before/after pair uses the same camera, scale, lighting and frame. Composite proof uses identical crop rectangles.
- Source and output both have zero glTF skins and no clips. No new rig or animation was created, and no deformation success is claimed.
- Delivery copy SHA256 is verified against the reviewed workspace export in verification.json.

The source archive, catalog, gallery proxy, shared runtime and other lanes' models were not overwritten. No Godot process, paid generation, retexture service, account credentials, commits or peer messages were used. Blender ran as separate background processes. Its optional thumbnail-cache write failed, but the editable save, exports, renders and fresh re-import checks completed.

## Exact paths and evidence

- Working/exported GLB: this folder/cobra_front - single tail corrected.glb
- Delivery: D:/user/Downloads/cobra_front - single tail corrected.glb
- Original download: D:/user/Downloads/Mecha Beast GLB/cobra_front - Hunyuan 3D v3.1 Pro.glb
- Immutable catalog source: D:/dev/new-mech-rpg/art/model_catalog/sources/cobra_front - Hunyuan 3D v3.1 Pro.glb
- Scripts and immutable scratch copy: D:/dev/_scratch/mech-art-direction/cobra-tail-2026-11-10/
- correction-report.json: source hash, local cut bounds, cap method, topology and protected-position checks.
- export-reimport-audit.json: actual exported topology.
- verification.json: texture equality, source/output/delivery hashes and image-size checks.
- correct_in_blender.py, render_before.py, render_after.py, package_review.py: reproducible local steps.

This is a geometry correction for the next rigging pass. It does not register the cobra into gameplay or establish a production animation/performance budget.
