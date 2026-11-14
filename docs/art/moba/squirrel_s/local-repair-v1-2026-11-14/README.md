# Squirrel local topology repair

Completed November 14, 2026, after Shark. Removed 58 malformed triangles and closed five small openings. Both arms/paws, legs/feet, ears and eyes, the muzzle/teeth and complete plated tail remain.

![Three-stage review](review-front.png)

The Workshop lineup and four revised sheets use `squirrel-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches original generation PNGs and revised sheets. The archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Changes and preservation

Removed 48 attached single-triangle flaps, one isolated triangle, a two-triangle fragment, a three-triangle fragment, and four folded triangles beside openings. Five original-corner closures yield 22,504 triangles. All 22,499 healthy source faces remain exact, including the separate closed 6/4/440-face components; small closed source pieces were not removed indiscriminately.

The original 26-joint hierarchy, rest transforms, inverse binds, scenes, positions, normals, UV rows, weights, materials and textures remain unchanged. Original binary is an exact prefix. Appended accessors replace triangle connectivity and include three duplicate corner rows for the paw closure's UV mapping. Those rows copy the original positions/normals/joints/weights exactly; only their UVs sample one healthy neighboring island to avoid atlas color bleed. No remesh, rerig, weight reassignment, new geometric position, texture or material.

Independent actual-file audit: zero open edges and zero collapsed triangles. Two balanced four-face assembly contacts remain after closure, retaining underlying source surfaces. All five repair close-ups and textured head/tail/front/back/both sides/top/underside/three-quarter views were inspected.

All 26 original joints were tested with small rotations: 26 produced measurable surface motion and 0 had no measurable motion. Maximum measured coincident-surface gap: 0 m, below one-micrometre tolerance. Twenty-one representative posed renders were inspected, covering the body, head, paws, feet and both tail controls. Native Blender scene is saved in rest pose with four packed immutable reference images. These diagnostics do not establish a finished run, jump or tail animation, or independent ear articulation.

Godot 4.7.2's native Workshop three-version/original-review-sheet/26-joint/ChaseCamera3D check passed. All seven final screenshots were inspected in `reports/model_catalog/squirrel-local-v1/`.

Existing baked texture roughness and source detail loss remain. No gameplay/map replacement or authored clips. Earlier roster work and Hornet/Jellyfish's distinct pending native checks remain preserved.

## Exact files and reproduction

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_squirrel_remeshed_25k_20261107_character.glb`; SHA256 `63a164377740ac29db9f31dc4bbec2ba929c233426f0d17af3240942dd9da1f8`; 22,557 triangles, 26 joints, zero clips. Exact raw copy is archived in `art/model_catalog/sources/`.

Final: `squirrel-rigged-local-repair-v1.glb`; SHA256 `0427c30992c70e6ea1e74289618a032aa3b59fc3852667ddc95c82ca16d3d1c3`. Native: `squirrel-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: geometry and source-data preservation.
- `visual-deformation-check.json`, `pose-proof.png`: 26 native-joint diagnostics, 21 representative views.
- `all-closures.png`, `before-after.png`: all five matched patch close-ups and selected larger views.
- `review-front/left/back/right.png`: original quality / downloaded rig / local repair.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/squirrel-review-2026-11-14/`, with snapshots here. Reproduce geometry with `repair_model.py`, then `fix_patch_uv.py`, followed by audit/render/pose/package stages. Guides applied: project `blender-export-pipeline`, `atlas-rigging`, `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry and skin checks. Source archives/reference PNGs remain unchanged. No paid generation, commits or next model selection.
