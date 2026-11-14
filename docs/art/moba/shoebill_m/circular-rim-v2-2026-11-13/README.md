# Shoebill circular moon rim v2

November 13, 2026. Preston requested a correct circular shape covering the exposed grey backing and confirmed: circular rim, keeping the moon visible. This adds a continuous blue circular casing and rolled silver rim over the previous fitted plate. The moon face, brass mounts, body, wings and original source geometry/weights remain unchanged.

![Circular rim before and after](before-after-plate-three-quarter.png)

Result: `shoebill-circular-moon-rim-v2.glb`, SHA256 `d6e52a3b322ef0bd3d5f65823c337eb7dc34f46a41ae30a5caa8f26d3f5de6f4`. Editable native file: `shoebill-circular-moon-rim-v2.blend`.

The frame has 192 segments, a 0.290 m outer radius and a 0.230 m open moon window. Its rear profile follows the existing mounting sleeve, covering the exposed grey cuff. Smooth hardware recesses retain the original brass mounts. Two new materials provide the silver lip and blue casing. The complete model has 30,186 triangles; the new closed annular frame adds 4,224.

The new frame is rigidly bound to the existing Bone_003 plate/body control, preserving its circular shape during motion. No skeleton nodes, hierarchy, rest transforms, inverse binds or original skin weights changed. Previous primitives, materials, textures and binary buffer are retained exactly; the frame is appended in separate primitives. Its source is [backplate repair v1](../backplate-repair-v1-2026-11-13/README.md), which remains archived.

Independent exported-file checks confirm zero open edges, over-shared edges and collapsed triangles, finite normalized weights, and sampled outer-vertex radius deviation below 0.000000054 m. Original moon artwork and baked body detail remain unchanged. Fourteen native-joint diagnostic poses passed with zero measured coincident-surface gaps. Final Godot three-version/original-review-sheet/38-joint/chase-camera check passed; its back comparison and actual-camera screenshots were inspected. Evidence is in `visual-deformation-check.json`, `pose-proof.png` and `godot-verification.json`, with screenshots in `reports/model_catalog/shoebill-circular-rim-v2/`. These assets are for review; no authored gameplay/map model is replaced.

Workshop: select Shoebill. C compares the original body archive, downloaded fitted rig and current circular rim; R switches original reference PNGs and labeled review sheets. The intact body archive has the earlier backplate and is labeled accordingly. The fitted moon design stays visible in the current version.

Scripts are included as implementation snapshots. Canonical configuration and diagnosis remain in `D:/dev/_scratch/mech-art-direction/shoebill-review-2026-11-13/`. Blender/Python/Godot only; no paid tools, new generation or rerigging.
