# Bombardier Beetle input review

Decision resolved: Preston selected pair 2. The current verified six-leg model is in `../joint-restoration-v2-2026-11-11/`, which repairs the front-joint/shoulder damage Preston identified in the earlier v1 cut. Statements about waiting below describe the pre-cut inspection stage.

November 11, 2026. Preston requested the next model after Bison. Actual downloaded input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bombardier_beetle_remeshed_25k_20261108_character.glb`, SHA256 `4ab1d8eac7802448813f95edc29e3be959c075268d4b6a28ca149897d3fcb0a1`. It has a bound 64-joint skeleton, 25,642 triangles and no clips. The catalog's static/unrigged statement is historical.

The intact pre-remesh original is `art/model_catalog/sources/bombardier_beetle_front - Hunyuan 3D v3.1 Pro.glb`, SHA256 `84c287011472b8cc2a8ec68ad4369cedb61d8a02f86840a9b9ba021a4d5b8b49`, 499,604 triangles, closed topology. All four original generation sheets were inspected. They establish a six-leg machine with two antennae, paired mandibles and forward-facing shoulder nozzles.

Front/side/back/top/underside/three-quarter renders of the actual rig expose eight walking legs, arranged in four pairs. The additional pair is also present in the intact original. Do not blindly restore the archive's anatomy. `walking-pair-choice.png` labels 1 front, 2 second, 3 third and 4 rearmost. A choice was requested from Preston; pair 2 was recommended to retain front/middle/rear spacing. No pair has been removed without his answer.

Independent local cleanup has been staged: four malformed flap triangles removed, reducing 25,642 to 25,638 triangles. Position-matched boundaries drop from eight to zero and over-shared edges from four to zero. No cap or new vertex is needed. All original vertex attributes, weights, nodes, skeleton/binds, materials/textures and original binary bytes are preserved. Exact staged output and hashes are in `local-cleanup-verification.json`. This is not a completed six-leg repair or Workshop promotion; anatomy choice, final cut, diagnostic poses, visual review and Godot verification remain.

Working files and initial renders: `D:/dev/_scratch/mech-art-direction/beetle-review-2026-11-11/`. The original rigged download, intact source and generation sheets remain unchanged. No paid tools, rerigging, remeshing, gameplay replacements or commits.
