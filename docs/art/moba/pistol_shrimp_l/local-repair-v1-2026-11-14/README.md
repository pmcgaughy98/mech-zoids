# Pistol Shrimp local topology repair

Completed November 14, 2026, after Jellyfish. Removed ten verified single-triangle flaps and closed one tiny opening on the large snapping claw using original vertex corners. The asymmetric snapping/small claws, eight walking legs, two antennae, two dorsal vessels and tail fan remain.

![Local repair](before-after.png)

The Workshop lineup and four revised sheets now use `pistol-shrimp-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches between original generation PNGs and revised comparison sheets. The intact archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Preservation and checks

The actual export has 25,626 triangles and the original 53 joints. All 25,625 healthy source triangles remain exact. Every original position, normal, UV and skin row is unchanged, as are the hierarchy, rest transforms, inverse binds, materials, textures, scenes and original binary prefix. Only triangle connectivity changed: ten stray triangles excluded and one closure added. No remesh, rerig, new material/texture, vertex, or transferred skin.

Independent actual-file audit: zero open edges, zero collapsed triangles. Two balanced original four-face assembly contacts remain on the claw. They were checked for balanced orientation and are documented rather than removing healthy source faces to eliminate those contacts.

All 53 joints were tested with small native rotations. 53 tests produced measurable surface motion; 0 had no measurable surface motion. Maximum measured coincident-surface gap was 0 m, below one-micrometre tolerance. Seventeen representative pose renders were inspected. The editable Blender scene is saved in rest pose with four packed immutable reference images. These tests do not establish independently articulated limbs or finished walking/snapping animations; the input has no authored clips.

Textured front/back/both sides/top/underside/three-quarter views, claw/head/tail close-ups and the small closure were inspected. Godot 4.7.2's actual Workshop three-version/original-review-sheet/53-joint/ChaseCamera3D check passed, and all seven final screenshots were inspected.

Existing baked texture roughness and source detail loss remain. This is a local topology repair, with no gameplay/map replacement. Earlier roster work, including Hornet and Jellyfish's separate pending native checks, is preserved.

## Exact files and reproduction

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_pistol_shrimp_remeshed_25k_20261111_character.glb`; SHA256 `999b901e08ad73df77f908dab8aa4159609e624fb961a45ce03d516501618d43`; 25,635 triangles, 53 joints, zero clips. Exact raw copy archived under `art/model_catalog/sources/`.

Final: `pistol-shrimp-rigged-local-repair-v1.glb`; SHA256 `823c26de99e963c6486cc8d92b31b41a6649018e4c7cfcac1e0c6b87a2b9349c`. Native: `pistol-shrimp-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: geometry, original-data preservation and protected contacts.
- `visual-deformation-check.json`, `pose-proof.png`: actual-joint diagnostics.
- `before-after.png`, `review-front/left/back/right.png`: matched close-ups and three-stage review sheets.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence; screenshots in `reports/model_catalog/pistol-shrimp-local-v1/`.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/pistol-shrimp-review-2026-11-14/`, with snapshots here. Project guides used: `blender-export-pipeline`, `atlas-rigging` and `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry/rig checks. Original archives and generation references remain unchanged. No paid generation, commits or next model selection.
