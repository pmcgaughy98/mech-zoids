# Wolf local topology repair

Completed November 14, 2026, after Tortoise. Removed 40 malformed triangles and closed two small openings. Four legs and paws, head and eyes, muzzle and teeth, ears, shoulder and rib armor, lights and the complete segmented tail remain.

![Three-stage review](review-front.png)

The Workshop lineup and four revised sheets use `wolf-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches original generation PNGs and revised sheets. The archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Changes and preservation

Removed 38 attached single-triangle flaps and two folded triangles beside small openings. Two original-corner closures yield 24,346 triangles. All 24,344 healthy source faces remain exact, including one closed four-face component; small closed source pieces were not removed indiscriminately.

The original 46-joint hierarchy, rest transforms, inverse binds, scenes, positions, normals, UV rows, weights, materials and textures remain unchanged. Original binary is an exact prefix. One appended index accessor replaces triangle connectivity. All vertex and UV rows remain exact; no duplicate corner rows were needed. No remesh, rerig, weight reassignment, new vertex, texture or material.

Independent actual-file audit: zero open edges and zero collapsed triangles. One balanced original four-face assembly contact remains, retaining underlying source surfaces. Both repair close-ups and textured head/tail/body/front/back/both sides/top/underside/three-quarter views were inspected.

All 46 original joints were tested with small rotations: 46 produced measurable surface motion and 0 stayed below the 1 mm visual-movement threshold. Maximum measured coincident-surface gap: 0 m, below one-micrometre tolerance. Twenty-seven representative posed renders were inspected, covering the body, head, four legs and tail controls. Native Blender scene is saved in rest pose with four packed immutable reference images. These diagnostics do not establish a finished walk or combat animation.

Godot 4.7.2's native Workshop three-version/original-review-sheet/46-joint/ChaseCamera3D check passed. All seven final screenshots were inspected in `reports/model_catalog/wolf-local-v1/`.

Existing baked texture roughness and source detail loss remain. No anatomy removal, gameplay/map replacement or authored clips. Earlier roster work and Hornet/Jellyfish's distinct pending native checks remain preserved.

## Exact files and reproduction

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_wolf_remeshed_25k_20261108_character.glb`; SHA256 `cb0fb5981637c29f62d89536d5b21e150a531c3bb6a3fabd5fd85f163e9f45fd`; 24,384 triangles, 46 joints, zero clips. Exact raw copy is archived in `art/model_catalog/sources/`.

Final: `wolf-rigged-local-repair-v1.glb`; SHA256 `c6e9f18355b10bf1207c717d346166b3595f591454c1706f9933e6da90ee2372`. Native: `wolf-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: geometry and source-data preservation.
- `visual-deformation-check.json`, `pose-proof.png`: 46 native-joint diagnostics, 27 representative views.
- `all-closures.png`, `before-after.png`: both matched patch close-ups and selected larger views.
- `review-front/left/back/right.png`: original quality / downloaded rig / local repair.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/wolf-review-2026-11-14/`, with snapshots here. Reproduce geometry with `repair_model.py`, followed by audit/render/pose/package stages. Guides applied: project `blender-export-pipeline`, `atlas-rigging`, `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry and skin checks. Source archives/reference PNGs remain unchanged. No paid generation, commits or next model selection.
