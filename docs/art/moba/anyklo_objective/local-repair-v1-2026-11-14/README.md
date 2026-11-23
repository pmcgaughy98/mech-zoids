# anyklo: tail mallet correction

Completed November 14, 2026, at Preston's direction. The export named cyber tortoise is the ankylosaur objective, renamed **anyklo** in its new GLB, editable workspace, Workshop lineup and comparison sheets. The separate Tortoise is preserved.

![Tail mallet before and after](tail-before-after.png)

## Shape correction

The generated hammer's two lobes splayed at opposing angles. Their original rear cyan panels measured +20.27 and -20.77 degrees from horizontal. Local three-dimensional lobe rotations of approximately 21.70 and 22.17 degrees now align both panels to one transverse axis; the actual exported panels measure 0.046 and 0.069 degrees. Rear, top, side and three-quarter close-ups were inspected. The result reads as a crosswise twin-lobed mallet attached to the tail.

A continuous transition around the existing central collar keeps it connected. Only 2,532 tail-head position/normal rows changed; all 35,170 other rows remain exact. Maximum local movement is 0.184932 m in the 1.7 m-high source. Jacobian-based normal correction preserves local shading; all 2,030 affected triangles pass the independent inversion check. Minimum sampled determinant at triangle centers is 0.396722, positive throughout the sampled vertices/centers. No remesh, new geometric vertices, new material or replacement texture.

Fifteen malformed triangles were also removed: twelve single flaps, a two-face fragment and another single malformed face. All 25,960 healthy source triangles retain their exact connectivity, including the original closed four-face part. Export topology has zero open edges and zero collapsed triangles; two original balanced four-face assembly contacts are retained. All four legs/paws, head/eyes, dorsal capacitor ribs, body armor, tail shaft and center attachment remain.

## Rig and runtime checks

The original **37-joint skeleton, hierarchy, rest transforms, inverse binds, scene nodes, UVs, skin weights and texture/material records remain exact**. The original binary remains an exact prefix. Only position/normal accessors and cleaned triangle connectivity are appended. The original download is archived unchanged.

All 37 controls were tested in pitch, with four tail controls additionally tested in yaw: 41 checks, 41 above the 1 mm surface-movement threshold and 0 below it. Maximum measured coincident-surface separation is 0 m. Nineteen full posed views and two tail-swing close-ups were inspected. Native workspace is saved in rest pose with all four exact downloaded generation PNGs packed. These small diagnostic bends establish local continuity, not a finished walk or combat swing.

Godot 4.7.2's native Workshop check passed: two comparison versions, original/review sheets, 37-joint rig and current ChaseCamera3D. All seven final screenshots were inspected. The objective lineup now has anyklo alongside Golden Beetle and Wyvern; 30 total catalog entries, with all prior 29 entries preserved.

## Sources and comparison limits

The only located 3D source is the actual remeshed, rigged cyber-tortoise download. No intact pre-remesh GLB was located locally or in the connected MeshForge library. C and the four revised sheets therefore show downloaded rig / corrected anyklo, explicitly labeled. The original downloaded generation PNGs remain available with R. A reduced proxy or duplicate rig was not presented as an intact original.

Input: `D:\user\Downloads\Mecha Beast GLB Meshy Rigged\Meshy_AI_cyber_tortoise_remeshed_25k_20261111_character.glb`; SHA256 `a21fa4395da287cca07b06544fbab322e95086c43e63f1ece0eec0c8210dd951`; 25,975 triangles, 37 joints, no authored clips. Exact copy: `art/model_catalog/sources/Meshy_AI_cyber_tortoise_remeshed_25k_20261111_character.glb`.

Output: `anyklo-rigged-tail-mallet-v1.glb`; SHA256 `e8931b6b9da4702173fb11281dc6efc9079bad09791fc74ed274542a12bdf16f`. Editable: `anyklo-rigged-tail-mallet-v1.blend`.

References: exact `D:/user/Downloads/power_ankylosaur_front/left/back/right.png`, copied unchanged to `art/model_catalog/references/anyklo/`. The project concept's related tightly cropped sheets informed identification; they are not claimed hash-identical to these downloaded PNGs.

- `repair-verification.json`, `independent-export-audit.json`: local geometry, alignment and preservation.
- `panel-measurements.json`, `measure_panels.py`: original textured panel measurements.
- `visual-deformation-check.json`, `pose-proof.png`, `tail-pose-*.png`: rig diagnostics.
- `tail-before-after.png`, `review-front/left/back/right.png`: matched visual comparisons.
- `final-review-verification.json`, `godot-review.log`: final native runtime evidence.

Canonical scripts are in `D:/dev/_scratch/mech-art-direction/anyklo-review-2026-11-14/`, with snapshots here. Run diagnosis/panel measurement, local repair, independent audit, renders, pose checks and packaging in sequence. Project Blender-export, rigging and optimization guides informed the checks. Existing baked roughness and original automatic skin limits remain. No paid generation, commits, new rig, gameplay/map replacement or edits to the separate Tortoise.
