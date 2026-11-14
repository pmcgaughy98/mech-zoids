# Approved hummingbird needle length v3

Preston selected the 30% shorter shaft. The straight shaft beyond glTF Z=.30 is now 70% of its v2 length; the collar and body are unchanged. Downward aim, width, straightening and all v2 topology repairs remain. This is a shaft-length change, not a 30% reduction of the entire beak including its collar.

Delivered GLB: `hummingbird-rigged-needle-length-v3.glb`, SHA256 `fc56b9f43e02c3c06e159b248e1d47746ebf494d9b5a12366fdf8d41f1083f34`. Editable source: `hummingbird-needle-length-v3.blend`. `approved-needle-before-after.png` and `review-*.png` provide matched proof. Previous versions and original generation sheets remain preserved.

The 21-joint skeleton, node/rest/bind transforms, weights, joint indices, UVs, materials and original texture bytes are unchanged. Positions outside the shaft are byte-identical to v2. Only shaft positions and corresponding transformed normals are appended. Seam-aware audit: zero boundaries and over-shared edges, no collapsed triangles; 22,162 triangles retained. `verification.json` records exact checks and tip extents.

Fresh import of the exact delivered hash was rendered in front, both sides, back, underside, three-quarter and needle close-ups. Actual head joints Bone_005 (+10 degrees local X and -10 local Z) and Bone_004 (-8 local X) were tested; all evaluated positions remain finite and inspected needle attachment stays intact. These diagnostic poses do not supply authored animation clips. Workshop comparison/sheets are advanced to v3. The final Godot model/chase-camera check is recorded in reports/model_catalog/hummingbird-length-v3/.

Local Python, Blender and Godot only; same rigging/export/render workflow as v2. No source overwrites, new rigging, texture generation, paid tools or gameplay-model installation. Reproduction scripts retain absolute source paths. The original shortened candidate was created by length_study.py, then selected and reviewed as v3.
