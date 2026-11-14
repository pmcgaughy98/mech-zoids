# Hummingbird needle straightening v1

Preston identified an uneven/bent needle and was uncertain about length. This first hummingbird slice straightens the shaft and regularizes its pointed taper while retaining its forward extent and slight downward aim. The four original sheets were inspected; both side sheets support a straight needle with a small downward angle. Length is deliberately unchanged pending a separate proportion review.

Output: `hummingbird-rigged-straight-needle-v1.glb`, SHA256 `a85b4f4df6c1936b67aed5b0be2549f751e41ec9520f9e3c6fd2e50988af2429`. Editable source: `hummingbird-straight-needle-v1.blend`. `needle-before-after.png` shows matched side/top close-ups. `review-*.png` compares the intact pre-remesh source, downloaded rigged input and needle repair. The original four generation sheets are unchanged and separately available in the Workshop.

## Change and preservation

Used the actual current Meshy rigged download, with 21 bound joints and 22,236 triangles. Adjusted 580 shaft vertices by at most 1.91 cm, using a straight tapered diamond section and a short blend into the untouched collar. Shaft starts at glTF Z=.30 and retains tip Z=1.355058789. The head, collar, body, wings, feet and tail have zero position change. Only position data and affected normals are appended; the entire original binary buffer is retained as a prefix. Skeleton hierarchy, node/rest transforms, inverse binds, joint indices, weight values, UVs, material definitions and embedded textures are preserved exactly. No rerig, weight transfer, new clips or blanket remesh.

## Validation and remaining work

Fresh Blender import and inspected textured front, side, opposite side, back, underside, three-quarter, needle side and needle top captures. Diagnostic poses rotate Bone_005 +10 degrees about local X and -10 about local Z, and Bone_004 -8 about local X. These are the actual head joints influencing the shaft; evaluated vertices remain finite and the needle remains attached in the inspected captures. Exact tested output hash is recorded in `visual-deformation-check.json`. This is a basic pose check, not exhaustive animation validation.

Godot model-review check passed: three native comparison versions, original/review sheets, 21-bone Skeleton3D and current ChaseCamera3D fixture. Screenshots are in `reports/model_catalog/hummingbird-needle-v1/`. Cobra's viewer behavior remains supported; comparison models now have a wrapper for optional source orientation, and the review check accepts an explicit model ID/output directory.

This is a needle pass, not full hummingbird restoration. The downloaded remesh has other topology defects: the position-matched audit reports 139 boundary edges and 63 over-shared edges, unchanged by this local repair. Wing/body/eye/foot surface quality, those defects, and final needle length remain in the hummingbird review queue. Original input and intact model remain available for that work. No gameplay model was installed.

## Reproduction

Local Python/NumPy/SciPy/Pillow, Blender 5.2.2 and Godot 4.7.2. Same project rigging/export/render guides as the Cobra repair. No paid tools, installs, generation or commits. Run `repair.py`, run `review.py` in background Blender, then `package.py`. Source/output paths are recorded. Blender's optional thumbnail-cache write failed outside workspace; the editable file saved successfully. Godot used an approved bounded outside-sandbox review run and left no renderer running.
