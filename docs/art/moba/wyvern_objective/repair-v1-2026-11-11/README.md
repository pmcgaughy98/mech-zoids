# Wyvern objective repair v1

Completed November 13, 2026 after the usage interruption. The four downloaded Wyvern reference views specify two hind legs and two wing forelimbs. The rigged download additionally contained two independent walking forelegs under the chest. Those extra legs were removed, preserving both wing shoulders, wing hands, hind legs, chest, jaw and tail.

## Files and provenance

- Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_Cyber_Wyvern_Sentinel_1110211655_texture.glb`, SHA256 `de6feb0f20655e289e8cae2de8ad6f9589050c93acb2feecd0e073194cd8d512`.
- Exact input archive: `art/model_catalog/sources/Meshy_AI_Cyber_Wyvern_Sentinel_1110211655_texture.glb`.
- Result: `wyvern-objective-repaired-v1.glb`, SHA256 `400b4030afb72959a5d265a97cf992c2ecee6e6ab417fb4e237ab0fd98ba09d9`.
- Editable native file: `wyvern-objective-repaired-v1.blend`, with four exact reference PNGs packed and provenance text inside.
- Exact downloaded PNGs: `art/model_catalog/references/wyvern/{front,left,back,right}.png`. Hashes and original paths are in `catalog-entry.json`. Creature identity and limb intent were checked visually; no exact historical generation-job linkage was established because the downloaded PNGs do not hash-match older project packs.

Despite its `_texture` filename, the source actually has 46 bound joints. It has no animation clips. No true pre-remesh GLB was found in the supplied folders or accessible MeshForge library. Existing map runtime/workspace copies derive from this same input and are not pre-remesh originals. Workshop and sheets therefore show two honestly labeled versions: downloaded rig, then repair. All source PNGs and archived GLB bytes are unchanged.

## Anatomy correction and preservation

Removed the two closed extra foreleg components, 1,354 and 1,418 triangles, plus 18 malformed flap triangles. No cutting through the chest or wing/hind-leg attachment surfaces was required, and no caps were added. All 22,970 original healthy main-body faces and the small closed six-triangle jaw detail remain exact. Output is 22,976 triangles versus 25,766 in the input.

All original positions, normals and UV rows are unchanged. Nodes, original 46-joint hierarchy, rest transforms, inverse binds, scene, materials and textures remain exact. Removed-leg controls Bone_028 through Bone_037 are retained in the hierarchy. Residual influence from those chains on 9,490 used surface rows was reassigned to their existing common parent Bone_002. Bone_038 and the wing chains were preserved. The complete original binary buffer remains an exact prefix; replacement indices and the documented local skin arrays are appended.

Independent exported-file checks confirm zero boundary edges, zero collapsed triangles, finite normalized weights and no remaining used-surface influence from the removed foreleg chains. Eight original balanced four-face contacts between closed assembly surfaces remain, including the closed jaw detail. These are explicitly protected original contacts; a globally manifold-zero-contact claim is not made. See `repair-verification.json` and `independent-export-audit.json`.

## Review and limits

Matched textured views include front, both sides, back, top, underside and three-quarter. Chest underside, both wing shoulders and head were compared in `local-proof.png`. Ten independent native-joint tests cover both wing arms, both hind legs, neck, jaw, tail root/middle and both removed foreleg controls. Every test has zero measured coincident-surface separation; both removed controls produce exactly zero rendered-surface displacement. Evidence is in `pose-proof.png` and `visual-deformation-check.json`, tied to the final export hash.

Workshop access: select Wyvern in the Objectives row. C compares native versions; R switches unchanged original reference PNGs and labeled repair sheets. Godot's final native comparison, original/review sheets, expected 46-joint import and current ChaseCamera3D fixture check passed. Final screenshots were inspected in `reports/model_catalog/wyvern-objective-v1/`.

These diagnostic bends do not establish polished wing flight, walking or foot contact. Original remesh/bake roughness remains, and the unavailable pre-remesh surface detail has not been reconstructed. This pass does not replace authored foundry map assets or install gameplay animation. No new generation, retexture, remesh or rerig was used.

## Reproduction

Canonical scripts/configuration: `D:/dev/_scratch/mech-art-direction/objective-repair-2026-11-11/`. Run `repair_objectives.py`, Blender `review_objective.py -- wyvern`, then `audit_objectives.py` and `package_objectives.py --publish`. Both objective inputs and saved diagnosis/configuration are required. Script snapshots here preserve the implementation with its original scratch-root dependencies. Local Blender 5.2.2/Python/Godot only; relevant project-local rigging/export/render/optimization guides informed the existing workflow. No paid tools, credentials or commits.
