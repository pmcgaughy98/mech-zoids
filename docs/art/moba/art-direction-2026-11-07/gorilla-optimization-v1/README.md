# Gorilla reduction pilot

Subsequent structural inspection found that this first reduction retained open geometry seams. It is preserved as Preston's selected visual reference. Use the corrected same-target 100k/2K working mesh and evidence in ../gorilla-cleanup-v1/README.md for further geometry work. The static image measurements below remain valid, but do not imply this older mesh is suitable for rigging.

Recommendation: use gorilla-100k-2k.glb as the next working mesh for cleanup and rig feasibility checks. It keeps the static silhouette and large hex panels close to the source at the tested match camera, with 80% fewer triangles and a 73% smaller file. Keep 40k/2K as a farther-distance candidate, not the main close-view mesh yet. No production budget, LOD switch or shared game asset has been installed.

![Controlled comparison](optimization-comparison.png)

![Farther away](distance-comparison.png)

## What changed

Blender 5.2.2 LTS collapse-decimated isolated copies to 99,999 and 40,000 triangles. No smoothing, remeshing, rigging, welding or topology repair was performed. The original source is preserved at ../gorilla-polish-v1/gorilla-source.glb and in Preston's Downloads.

Geometry and texture changes were tested separately before combining them:

| Test | Triangles | Texture size | File MB, decimal | Lowest static silhouette overlap |
|---|---:|---:|---:|---:|
| Source | 499,148 | 4K | 50.0 | 100% |
| Texture-only control | 499,148 | 2K | 24.9 | 100% |
| Geometry-only control | 99,999 | 4K | 38.5 | 99.9449% |
| Geometry-only lighter control | 40,000 | 4K | 35.8 | 99.8657% |
| Recommended working candidate | 99,999 | 2K | 13.4 | 99.9449% |
| Farther-distance candidate | 40,000 | 2K | 10.7 | 99.8657% |

For the 2K versions, albedo and packed metallic/roughness maps were downsampled; normal vectors were renormalized after filtering. Texture-only derivatives preserve geometry-buffer bytes exactly. The geometry-only 4K exports preserve the original three embedded PNGs byte for byte, and the material definition was inspected against the source. Blender gave a sampler-node warning during export; the texture-byte check and Godot render review confirmed the images retained for these tests.

## What the evidence shows

Thirty 1280x720 color frames and thirty matching white-on-black silhouette masks were captured in Godot Compatibility, using the actual foundry arena. Every variant uses the same refined D material, pose, camera and test scale. Four near angles (0, 45, 135 and 180 degrees) and one angle 8 m farther away were tested. Near camera remains FOV 60, pitch 30 degrees, distance 6.5 m, look height 1.2 m, model normalized uniformly to 2 m tall. Scale remains provisional.

The overlap percentage is intersection-over-union of screen-space silhouette masks against the source. It measures static projected shape only. It does not prove good topology, successful deformation, equivalent internal detail or universal visual similarity.

At the near three-quarter view, the texture-only 2K control changes mean absolute RGB by 0.62 on a 0-255 scale inside the common silhouette. The 100k/2K version changes it by 4.43; 40k/2K by 6.25. These are image differences, not perceptual pass thresholds. They include shading, normals, UV interpolation and texture changes. All per-angle measurements are in screen-space-report.json.

Visual inspection: the large shoulder masses, forearm hex panels and rear panel remain recognizable in both reduced candidates. The 100k version stays close enough to proceed with cleanup. The 40k version shows more disturbed shading around shoulder/arm surfaces and small panel edges; it is a candidate for distant use. Existing generated faceting and UV-heavy topology remain. The 2K reduction contributes much less visible change than the geometry reduction at the inspected distance.

No crowd or frame-time benchmark was run. Fewer triangles and texels are measured resource reductions, not an FPS claim. Single static character captures do not establish match performance.

## Play the comparison

Run open-preview.ps1 with PowerShell after closing any other Godot renderer. The launcher enforces the project's one-renderer rule.

- 1: source mesh with 4K maps.
- 2: 100k/2K candidate, the default.
- 3: 40k/2K candidate.
- Left/right rotates; up/down changes distance; Escape quits.

All three have the same refined material. The GLB files themselves retain PBR material definitions; the refined D shader is applied in the preview and is not baked into these GLBs. Use the shader and setup in ../gorilla-polish-v1/ when integrating later.

The preview check exercised 1, 2 and 3 through Godot's input pipeline, loaded each mesh, exercised Right and checked the resulting rotation, then restored 100k/2K for the inspected window screenshot. The process completed successfully and exited. Interactive-preview.png records the actual 1280x720 window.

## Files and verification

- gorilla-100k-2k.glb: recommended working candidate.
- gorilla-40k-2k.glb: farther-distance candidate.
- gorilla-source-2k.glb, gorilla-100k-4k.glb and gorilla-40k-4k.glb: controlled comparisons.
- reduction-report.json: Blender counts, bounds and export timings. Export timings are not game performance measurements.
- capture-manifest.json: every view and its camera/source settings.
- screen-space-report.json: masks, image differences and per-variant summaries.
- reduce_in_blender.py, resize_glb.py, capture.gd and measure.py: reproducible local steps.
- verification.json: source preservation and completion checks.

No source download, game asset, renderer setting, rig, weights or animation-lane outputs were changed. All work stays in this lane's scratch/results folders. No paid service, installation, commit or peer message was used. The same pre-existing root-certificate and shader-cache-write errors appeared in Godot, with cleanup warnings at exit. Exports, captures and preview checks completed despite those warnings.

## Next technical boundary

The candidate is still static and not retopologized for deformation. Before handing it into the animation workflow, inspect the shoulder, elbow and hip geometry for separation and articulation. Do not infer that successful decimation makes it safe to auto-weight. Keep the original source and this static comparison as rollback references.

Arena lighting was held fixed. Team readability, active shield VFX, cast/contact shadows, skinning and animation are not validated by this pass. Those remain separate from character mesh/material findings.
