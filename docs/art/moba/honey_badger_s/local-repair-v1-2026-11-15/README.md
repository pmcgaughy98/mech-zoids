# Honey Badger: first local repair pass

Completed November 15, 2026, in Preston's new Creature Factory batch. Four legs, long front claws, hind paws, head/eyes, dorsal armor, shoulder mechanisms and short tail retained.

![Downloaded rig and local repair](review-front.png)

Removed 17 malformed triangles and closed 0 small openings. Final export: 25,532 triangles; zero open edges and zero collapsed triangles. All 25,532 retained source triangles remain exact, including closed source components. 1 balanced original assembly contacts remain. No anatomy removal, remesh or rerig.

All original position/normal/UV/skin rows remain exact; no duplicate rows were needed. The original 37-joint hierarchy, rest transforms, inverse binds, scene nodes, materials and textures are unchanged. Original binary remains an exact prefix.

All 37 original controls were tested: 37 above the 1 mm visual-movement threshold, 0 below it. Maximum measured coincident-surface separation: 0 m. 19 representative poses, any local closure close-ups, and textured front/back/both sides/top/underside/three-quarter views were inspected. Native workspace is saved in rest pose with four packed immutable reference PNGs. These diagnostics do not establish finished authored movement.

The native Godot Workshop two-version/original-review-sheet/37-joint/ChaseCamera3D check passed. All seven final screenshots were inspected. Existing entries remain preserved. New compact selector rows and fitted overview framing keep the growing lineup visible.

## Source and limits

Existing generated/baked surface detail remains; authored movement and final visual polish remain. No gameplay installation, paid generation or new rig. No intact pre-remesh GLB was located. The two-version comparison explicitly shows archived downloaded rig before local repair; no proxy or duplicate rig is presented as an intact original. Four original generation PNGs remain separate from revised model sheets. Concept projection differences are reconciled conservatively; no new kit, names or gameplay rules were selected.

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_honeybadger_remeshed_25k_20261114_character.glb`, SHA256 `f3273da9b09c2174e78ee9796494998414c19bc03e5161d37e4535726a5a4a17`; 25,549 triangles, 37 joints, zero authored clips. Exact copy archived in `art/model_catalog/sources/` under the original filename.

Output: `honey-badger-rigged-local-repair-v1.glb`, SHA256 `3d5d7dc32bc212a82eeb06ccd77b5d8bcea41d5f63df581bcb77e1d0e80b6e24`. Editable native file has the same basename with `.blend`.

Evidence: `repair-verification.json`, `independent-export-audit.json`, `visual-deformation-check.json`, `pose-proof.png`, four `review-*.png` sheets, `final-review-verification.json`, and `godot-review.log`. Canonical scripts: `D:/dev/_scratch/mech-art-direction/honey_badger-review-2026-11-15/`, with snapshots here. Project Blender-export, rigging and optimisation guides informed the checks. Original downloads/reference PNGs, existing authored lanes and previous repairs remain unchanged. No commits.
