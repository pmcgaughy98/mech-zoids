import hashlib,json,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/anyklo-tail-mallet-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'];assert p['joint_count']==37 and p['original_controls_tested']==37 and len(p['poses'])+len(p['no_surface_motion'])==41
assert 'MODEL REPAIR CHECK PASS: anyklo, 2 comparison versions, original/review sheets, 37-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'];gap=max(x['coincident_surface_gap_m'] for x in p['poses']+p['no_surface_motion']);assert gap<1e-6
report={'passed':True,'date':'2026-11-14','name':'anyklo','previous_export_name':'cyber tortoise','tested_sha256':r['output_sha256'],'triangles':25960,'joint_count':37,'original_controls_tested':37,'pitch_and_tail_yaw_checks':41,'tests_above_1mm_surface_motion':len(p['poses']),'tests_below_1mm_surface_motion':len(p['no_surface_motion']),'maximum_seam_gap_m':gap,'boundary_edges':0,'over_shared_edges':2,'collapsed_triangles':0,'local_triangle_inversions':0,'modified_triangles_tested':a['modified_triangles_tested'],'rear_panel_alignment':a['rear_panel_alignment'],'original_reference_sha256':a['original_reference_sha256'],'source_sha256':r['source_sha256'],'all_original_weights_uvs_skeleton_rest_binds_materials_textures_preserved':True,'all_positions_normals_outside_tail_head_unchanged':True,'native_runtime_check':'Two native versions, original/review sheets, 37-joint rig and actual ChaseCamera3D','screenshots':'res://reports/model_catalog/anyklo-tail-mallet-v1','intact_pre_remesh_available':False,'limits':'Downloaded generation texture roughness and approximate original skinning remain. No authored gait/swing clips or gameplay installation.'}
(OUT/'final-review-verification.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# anyklo: tail mallet correction

Completed November 14, 2026, at Preston's direction. The export named cyber tortoise is the ankylosaur objective, renamed **anyklo** in its new GLB, editable workspace, Workshop lineup and comparison sheets. The separate Tortoise is preserved.

![Tail mallet before and after](tail-before-after.png)

## Shape correction

The generated hammer's two lobes splayed at opposing angles. Their original rear cyan panels measured +20.27 and -20.77 degrees from horizontal. Local three-dimensional lobe rotations of approximately 21.70 and 22.17 degrees now align both panels to one transverse axis; the actual exported panels measure {a['rear_panel_alignment'][0]['after_angle_xy_degrees']:.3f} and {a['rear_panel_alignment'][1]['after_angle_xy_degrees']:.3f} degrees. Rear, top, side and three-quarter close-ups were inspected. The result reads as a crosswise twin-lobed mallet attached to the tail.

A continuous transition around the existing central collar keeps it connected. Only 2,532 tail-head position/normal rows changed; all 35,170 other rows remain exact. Maximum local movement is {r['maximum_local_vertex_displacement_m']:.6f} m in the 1.7 m-high source. Jacobian-based normal correction preserves local shading; all 2,030 affected triangles pass the independent inversion check. Minimum sampled determinant at triangle centers is {a['minimum_centroid_jacobian_determinant']:.6f}, positive throughout the sampled vertices/centers. No remesh, new geometric vertices, new material or replacement texture.

Fifteen malformed triangles were also removed: twelve single flaps, a two-face fragment and another single malformed face. All 25,960 healthy source triangles retain their exact connectivity, including the original closed four-face part. Export topology has zero open edges and zero collapsed triangles; two original balanced four-face assembly contacts are retained. All four legs/paws, head/eyes, dorsal capacitor ribs, body armor, tail shaft and center attachment remain.

## Rig and runtime checks

The original **37-joint skeleton, hierarchy, rest transforms, inverse binds, scene nodes, UVs, skin weights and texture/material records remain exact**. The original binary remains an exact prefix. Only position/normal accessors and cleaned triangle connectivity are appended. The original download is archived unchanged.

All 37 controls were tested in pitch, with four tail controls additionally tested in yaw: 41 checks, {len(p['poses'])} above the 1 mm surface-movement threshold and {len(p['no_surface_motion'])} below it. Maximum measured coincident-surface separation is {gap:.9g} m. Nineteen full posed views and two tail-swing close-ups were inspected. Native workspace is saved in rest pose with all four exact downloaded generation PNGs packed. These small diagnostic bends establish local continuity, not a finished walk or combat swing.

Godot 4.7.2's native Workshop check passed: two comparison versions, original/review sheets, 37-joint rig and current ChaseCamera3D. All seven final screenshots were inspected. The objective lineup now has anyklo alongside Golden Beetle and Wyvern; 30 total catalog entries, with all prior 29 entries preserved.

## Sources and comparison limits

The only located 3D source is the actual remeshed, rigged cyber-tortoise download. No intact pre-remesh GLB was located locally or in the connected MeshForge library. C and the four revised sheets therefore show downloaded rig / corrected anyklo, explicitly labeled. The original downloaded generation PNGs remain available with R. A reduced proxy or duplicate rig was not presented as an intact original.

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 25,975 triangles, 37 joints, no authored clips. Exact copy: `art/model_catalog/sources/Meshy_AI_cyber_tortoise_remeshed_25k_20261111_character.glb`.

Output: `anyklo-rigged-tail-mallet-v1.glb`; SHA256 `{r['output_sha256']}`. Editable: `anyklo-rigged-tail-mallet-v1.blend`.

References: exact `D:/user/Downloads/power_ankylosaur_front/left/back/right.png`, copied unchanged to `art/model_catalog/references/anyklo/`. The project concept's related tightly cropped sheets informed identification; they are not claimed hash-identical to these downloaded PNGs.

- `repair-verification.json`, `independent-export-audit.json`: local geometry, alignment and preservation.
- `panel-measurements.json`, `measure_panels.py`: original textured panel measurements.
- `visual-deformation-check.json`, `pose-proof.png`, `tail-pose-*.png`: rig diagnostics.
- `tail-before-after.png`, `review-front/left/back/right.png`: matched visual comparisons.
- `final-review-verification.json`, `godot-review.log`: final native runtime evidence.

Canonical scripts are in `D:/dev/_scratch/mech-art-direction/anyklo-review-2026-11-14/`, with snapshots here. Run diagnosis/panel measurement, local repair, independent audit, renders, pose checks and packaging in sequence. Project Blender-export, rigging and optimization guides informed the checks. Existing baked roughness and original automatic skin limits remain. No paid generation, commits, new rig, gameplay/map replacement or edits to the separate Tortoise.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''anyklo tail mallet correction completed November 14. Preston identified the cyber-tortoise export as the ankylosaur and requested the spelling anyklo. Added it as a separate objective entry; Tortoise and all other 29 catalog entries preserved. Two skewed hammer lobes aligned to a crosswise mallet, reducing the rear panel angles from about +20/-21 degrees to below 0.1 degree. Local collar transition stays connected; only 2,532 tail-head position/normal rows changed. All UVs, skin weights, original 37-joint hierarchy/rest/binds/scenes/materials/textures remain exact. Fifteen malformed triangles removed; final 25,960 triangles, zero open/collapsed triangles, two protected original assembly contacts and zero local face inversions. Forty-one pitch/tail-yaw diagnostics passed with maximum seam gap {gap:.9g} m; nineteen full poses and two tail close-ups inspected. Native Godot two-version/original-review-sheet/37-joint/ChaseCamera3D check passed; all final screenshots inspected. Intact pre-remesh GLB unavailable, so comparison correctly shows archived downloaded rig before repaired anyklo. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14/README.md. Original source/downloads and generation PNGs preserved; no authored clips, paid generation or gameplay installation.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;s=path.read_text(encoding='utf-8')
 if note not in s:
  head,tail=s.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));assert len(cat['entries'])==30;others=[x for x in cat['entries'] if x['id']!='anyklo'];entry=next(x for x in cat['entries'] if x['id']=='anyklo');entry['review_provenance']['runtime_report']='res://docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14/final-review-verification.json';assert [x for x in cat['entries'] if x['id']!='anyklo']==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n');shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(report,indent=2))
