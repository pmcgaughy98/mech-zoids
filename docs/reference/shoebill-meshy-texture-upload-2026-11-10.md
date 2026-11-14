# Shoebill textured upload workaround, 2026-11-10

Preston reports that Meshy's remesh repeatedly produces an untextured shoebill.
The source `D:/user/Downloads/shoebill_front - moon backplate fixed.glb` is intact:
three mesh objects, four materials, five embedded images, 50,638 triangles, no rig.
The service-side cause has not been confirmed. No paid job was submitted here.

Prepared a local Blender upload candidate with one mesh, one material, and three
embedded 4096px PNG maps: base color, tangent normal, and metallic/roughness.
It retains all 50,638 triangles and the source bounds. Base color and scalar maps
were baked without lighting. The original source is preserved. A reduced 25k
candidate was rejected after visible surface distortion; do not use that draft.

Verified the actual exported GLB by reimporting it and comparing front, side,
back, and underside renders. Local appearance is preserved at review scale;
Meshy's importer/rigging behavior is not yet verified. Suggested next attempt:
upload the single-material copy and Smart Rig directly, skipping Remesh.

Delivered filename: `D:/user/Downloads/shoebill_front - single material textured rig upload.glb`.
Build, reports, editable .blend, and review board:
`D:/dev/_scratch/shoebill-meshy-upload-2026-11-10/`.
Review: `review/shoebill/comparison.jpg` (source top, upload candidate bottom).

Official documentation consulted:
- https://docs.meshy.ai/en/webapp/guides/3d-model/remesh
- https://docs.meshy.ai/en/api/remesh
- https://docs.meshy.ai/en/webapp/guides/3d-model/rigging

These docs do not establish the cause of this specific white remesh. This is a
local texture-packaging workaround, not a confirmed Meshy bug fix.
