# Gorilla structural cleanup

Preston selected the middle 100k-triangle / 2K option. This pass keeps that target and the refined D finish, while correcting a structural problem found during articulation inspection.

Recommended next working copy: gorilla-connected-100k-2k.glb. It has 100,000 triangles, the same three 2K texture images as the selected reduction, and is 12.8 MB. It is still static, with no rig or weights. No model has been installed into the game.

![Controlled comparison](cleanup-comparison.png)

## What was wrong and what changed

The first reduction was made from glTF import vertices split at texture/normal seams. Simplifying those separate vertices independently preserved the static silhouette but left open geometry seams. That version is a visual reference, not a rig-ready mesh.

The corrected process starts again from the preserved current MeshForge source, joins coincident positions within 0.000001 source units before reduction, keeps the corner-domain UVs and custom split normals, and then reduces the connected surface to the chosen 100k target. No smoothing, remeshing, new armor, detail generation or global normal recalculation was applied.

| Structural test | Selected reduction | Connected cleanup |
|---|---:|---:|
| Triangles | 99,999 | 100,000 |
| Connected surfaces after accounting for seam splits | 119 | 1 |
| Boundary edges after accounting for seam splits | 77,539 | 0 |
| Non-manifold edges after accounting for seam splits | 77,539 | 0 |
| Zero-area faces | 0 | 0 |
| Lowest silhouette overlap with original, five tested views | 99.9449% | 99.9594% |

These topology counts were measured on imported geometry after a positional weld at the same small tolerance. Raw GLB vertex splits at UV/normal boundaries are expected and are not themselves holes. The corrected editable Blender mesh has 49,994 connected vertices; its exported GLB re-imports with 78,140 seam-split vertices, which reconnect to the same 49,994 positions and a closed single surface. The selected reduction did not reconnect to a closed surface.

The source import had 306,875 seam-split vertices and 499,148 faces. The weld made it 249,568 vertices with no boundary or non-manifold edges, before reduction. Corner normals were stored in a CORNER-domain vector attribute through the weld and restored, leaving UV layers intact. The new 100k reduction remains closed. This method is now the required starting point for testing other reduced generated models, followed by per-model visual review.

## Visual evidence

Fifteen color captures and fifteen silhouette masks compare the 499k/4K source, selected 100k/2K reduction and connected 100k/2K cleanup at the same foundry arena, camera, static pose, 2 m test height and refined material. Views: front, both three-quarter angles, rear, and 8 m farther away. Resolution 1280x720, camera FOV 60, pitch 30, distance 6.5 m and look height 1.2 m. No new light, exposure, floor, shadow or renderer settings.

The cleanup retains the bulky silhouette and large hex panels. Its visible differences are modest, principally structural. Near-three-quarter mean absolute RGB difference from the source is 4.11/255 versus 4.43/255 for the selected reduction. These image metrics are not perceptual guarantees and say nothing about successful deformation or frame rate.

The GLB was exported and re-imported into a fresh Blender process for the topology audit. Front, three-quarter, rear and distant rendered images were inspected. The interactive comparison window was captured and inspected; keys 1/2/3 and Right were sent through Godot's input pipeline, with rotation asserted. Test exited successfully and no Godot renderer was left running.

## Play and edit

Run open-preview.ps1 with PowerShell, with other Godot renderers closed.

- 1: original 499k/4K source.
- 2: Preston's selected earlier 100k/2K reduction.
- 3: connected 100k/2K cleanup, the default.
- Left/right rotates; up/down changes distance; Escape quits.

The preview applies the refined D shader; the GLB alone keeps the source PBR material definition. Refined material response is not baked into the GLB.

gorilla-connected-cleanup.blend is an editable clean 100k mesh with packed original 4K textures. The separate recommended GLB contains the 2K textures. Source coordinates and scale are retained; uniform 2 m scale is applied only in the review.

## Articulation finding and next boundary

The mesh is now one closed shell, but its shoulders, elbows, torso, hips and hands are still fused into that shell. Closed topology is not articulated topology. For rigid mecha armor, deliberate separation and joint coverage must precede weighting so plates do not stretch like skin. This pass does not create bones, skin weights, animation clips or a successful articulation claim.

Next slice: separate and inspect one shoulder/arm assembly on an isolated copy, preserving overlapping armor coverage and the hex forearm plate. Verify its closed rest appearance and a small hinge test before extending the method. That is a geometry articulation test, not a roster-wide rig or replacement of the animation lane's work.

## Audit and provenance

- topology-audit.json: the selected reduction, inspected read-only.
- cleanup-report.json: source import, pre-reduction weld and connected reduction counts.
- exported-topology-audit.json: fresh import of the final 2K GLB.
- screen-space-report.json and capture-manifest.json: camera, per-view masks and image comparison.
- verification.json: source hashes, exact texture retention, capture sizes and preview completion.
- clean_reduce_in_blender.py, audit_selected_in_blender.py, audit_export_in_blender.py, capture.gd and review.py: reproducible steps.

No source download, selected earlier GLB, rig, animation output, shared game code or global renderer setting was overwritten. This pass does not touch the existing open Blender process. All Blender work used separate background processes. No paid tool, installation, purchase, commit, peer message or account-key inspection.

Blender could not write its optional thumbnail cache but saved the editable file and exported the GLB. Godot again reported certificate-store and shader-cache-write errors, plus resource cleanup warnings; render and preview checks nevertheless completed. No crowd performance test was done.
