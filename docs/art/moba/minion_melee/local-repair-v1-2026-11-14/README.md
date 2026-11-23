# Melee Minion local topology repair

Completed November 14, 2026, after anyklo. Removed 136 malformed triangles and closed eight small openings. All four legs and feet, front impact bumper, cyan optic slit, dorsal armor plate and rear grille remain.

![Three-stage review](review-front.png)

The Workshop lineup and four revised sheets use `melee-minion-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches original generation PNGs and revised sheets. The archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Changes and preservation

Removed 131 malformed triangles in open fragments and five folded triangles beside small openings. Eight original-corner closures yield 19,668 triangles. All 19,660 healthy source faces remain exact, including ten closed four-face components and three closed six-face components; small closed source pieces were not removed indiscriminately.

The original 18-joint hierarchy, rest transforms, inverse binds, scenes, positions, normals, UV rows, weights, materials and textures remain unchanged. Original binary is an exact prefix. One appended index accessor replaces triangle connectivity. All vertex and UV rows remain exact; no duplicate corner rows were needed. No remesh, rerig, weight reassignment, new vertex, texture or material.

Independent actual-file audit: zero open edges and zero collapsed triangles. Ten balanced four-face assembly contacts remain after closure, retaining underlying healthy source surfaces. All eight repair close-ups and textured front/back/both sides/top/underside/three-quarter views were inspected.

All 18 original joints were tested with small rotations: 13 produced measurable surface motion and 5 stayed below the 1 mm visual-movement threshold. Maximum measured coincident-surface gap: 0 m, below one-micrometre tolerance. Eighteen representative posed renders were inspected, covering the body, front bumper and all four leg-control chains. Native Blender scene is saved in rest pose with four packed immutable reference images. These diagnostics do not establish a finished walk or combat animation.

Godot 4.7.2's native Workshop three-version/original-review-sheet/18-joint/ChaseCamera3D check passed. All seven final screenshots were inspected in `reports/model_catalog/melee-minion-local-v1/`.

Existing baked texture roughness and source detail loss remain. No anatomy removal, gameplay/map replacement or authored clips. The Workshop labels this unit as Melee Minion with category minion; it is not added to the playable champion roster. Earlier roster work and Jellyfish's pending native check remains preserved; Hornet's completed native check is preserved.

## Exact files and reproduction

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_minion_melee_remeshed_25k_20261111_character.glb`; SHA256 `d7d4d313fda8ed575b1ef0ead6a5bae8e1c9a0c84128fb7d0752b43d82f26b01`; 19,796 triangles, 18 joints, zero clips. Exact raw copy is archived in `art/model_catalog/sources/`.

Final: `melee-minion-rigged-local-repair-v1.glb`; SHA256 `585419e1022af21a47b06ceab8ad767864fbd806e4a62f7de6d24035293b5d81`. Native: `melee-minion-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: geometry and source-data preservation.
- `visual-deformation-check.json`, `pose-proof.png`: 18 native-joint diagnostics, 18 representative views.
- `all-closures.png`, `before-after.png`: all eight matched patch close-ups and selected larger views.
- `review-front/left/back/right.png`: original quality / downloaded rig / local repair.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/melee-minion-review-2026-11-14/`, with snapshots here. Reproduce geometry with `repair_model.py`, followed by audit/render/pose/package stages. Guides applied: project `blender-export-pipeline`, `atlas-rigging`, `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry and skin checks. Source archives/reference PNGs remain unchanged. No paid generation, commits or next model selection.
