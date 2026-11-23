import json,hashlib,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/sloth_m/local-repair-v1-2026-11-15';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/sloth-local-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'];assert p['joint_count']==52 and len(p['poses'])==52 and not p['no_surface_motion'] and len(p['rendered_poses'])==24
assert 'MODEL REPAIR CHECK PASS: sloth, 2 comparison versions, original/review sheets, 52-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'];gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
report={'passed':True,'date':'2026-11-15','tested_sha256':r['output_sha256'],'triangles':25556,'joint_count':52,'native_joint_tests_with_surface_motion':52,'maximum_seam_gap_m':gap,'boundary_edges':0,'over_shared_edges':3,'collapsed_triangles':0,'healthy_source_faces_retained':25555,'original_vertex_attribute_and_skin_rows_preserved':True,'duplicate_uv_corner_rows':3,'original_skeleton_rest_binds_materials_textures_preserved':True,'original_reference_sha256':a['original_reference_sha256'],'downloaded_input_sha256':r['source_sha256'],'intact_pre_remesh_available':False,'native_runtime_check':'Two native versions, original/review sheets, 52-joint rig and actual ChaseCamera3D','screenshots':'res://reports/model_catalog/sloth-local-v1','selector_layout':'Five compact rows fit above the objective buttons. Overview camera fits actual model bounds with padding.','limits':'Local geometry repair. Baked moss detail in dorsal recesses remains faint; authored motion and final visual polish remain.'}
(OUT/'final-review-verification.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Sloth: first local repair pass

Completed November 15, 2026, as the first of Preston's five newly rigged Creature Factory models. The approved take B olive-armored Sloth design remains, with two long forearms, six hooked digits, two shorter hind legs/feet, face and eyes, paired forearm reels, chest core, dorsal growth recesses and short tail.

![Downloaded rig and local repair](review-front.png)

## Repair and preservation

Removed eleven malformed triangles in open fragments and closed one small chest opening with an original-corner triangle. The actual export contains 25,556 triangles and zero open edges or collapsed triangles. All 25,555 other source triangles remain, including the separate closed 4/4/30/4-face source components; three balanced four-face assembly contacts remain after closure.

All original positions, normals, UV rows, joints and skin weights remain exact. The full 52-joint hierarchy, rest transforms, inverse binds, scene nodes, materials and textures are unchanged. Original binary is an exact prefix. Appended accessors replace triangle connectivity and add three duplicate corner rows for the new chest closure. Those rows copy original positions, normals, joints and weights exactly; their UVs sample one healthy neighboring texture island, preventing the closure from spanning unrelated atlas regions. No new geometric position, rerig, remesh, new material or texture.

Actual-file audit and matched chest/head/reel/dorsal and front/back/both sides/top/underside/three-quarter renders were inspected. All 52 native control rotations produced measurable surface movement and passed the one-micrometre seam tolerance. Maximum measured coincident-surface separation: {gap:.9g} m. Twenty-four representative posed renders cover body, face, forearms, hook groups and hind limbs. The native workspace is saved in rest pose with all four immutable downloaded reference images packed.

Godot 4.7.2's native two-version/original-review-sheet/52-joint/ChaseCamera3D check passed. All seven final screenshots were inspected. Sloth is in the Workshop with four revised before/after sheets. The selector now fits five compact button rows above Objectives, leaving room for the five new designs as their passes are completed. The overview camera fits the actual model bounds with padding so the added row does not clip the top or objective rows. Prior 31 catalog entries are preserved.

## Visual limits and source provenance

The baked moss detail inside the dorsal recesses is faint compared with the reference sheets. It remains a later visual/material pass; this repair does not claim complete restoration of reference foliage or finished animation. Original automatic skin/control grouping is retained. No gameplay installation or performance/animation approval is claimed.

No intact pre-remesh Sloth GLB was located in the local source search. The two-version comparison explicitly shows exact downloaded remeshed rig / local repair. The source archive is not mislabeled as intact pre-remesh geometry. Original generation PNGs remain available separately with R. Downloaded PNGs visually match the approved take B identity; their exact bytes do not match the project's packaged copies, so no false hash match is claimed.

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 25,566 triangles, 52 joints, zero clips. Exact copy is archived in `art/model_catalog/sources/` under its original filename.

Final: `sloth-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Editable: `sloth-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: topology and exact data preservation.
- `fix_patch_uv.py`: local closure UV mapping; original attribute rows retained.
- `visual-deformation-check.json`, `pose-proof.png`: 52 native diagnostics, 24 representative views.
- `before-after.png`, `review-front/left/back/right.png`: patch and matched whole-model comparisons.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/sloth-review-2026-11-15/`, with snapshots here. Reproduce with diagnosis, local repair, UV correction, independent audit, renders/poses and packaging. Project Blender-export, rigging and optimization guides informed the workflow. No paid generation, commits or edits to existing authored lanes.

Cat, Owl, Honey Badger and Axolotl have verified rigged inputs and four references, queued for individual repair passes in `docs/art/moba/CREATURE_FACTORY_REPAIR_QUEUE_2026-11-15.md`. Their geometry has not yet been repaired by this pass.
''';(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Sloth first local repair completed November 15, first of the new Creature Factory batch. Removed eleven malformed triangles and closed a small chest gap, final 25,556 triangles. Six hooked digits, forearm reels, face/eyes, hind feet, chest core, dorsal recesses and tail retained. All original position/normal/UV/skin rows, 52-joint hierarchy/rest/binds and materials/textures remain exact; three duplicate corner/skin rows provide local UV mapping only for the closure. Export has zero open/collapsed triangles and three balanced assembly contacts. All 52 native controls move the surface and pass with maximum seam gap {gap:.9g} m; 24 representative poses and matched texture/detail views inspected. Native Godot two-version/original-review-sheet/52-joint/ChaseCamera3D check passed; all final screenshots inspected. Workshop selector fits five compact rows above Objectives, and the overview camera fits the actual models to keep every row visible. All previous 31 catalog entries preserved. No intact pre-remesh GLB located, so downloaded rig / repair are explicitly labeled. Baked moss detail remains faint; later visual and authored-animation work remain. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/sloth_m/local-repair-v1-2026-11-15/README.md. Cat, Owl, Honey Badger and Axolotl inputs are verified and queued; they are not yet repaired. No paid generation, new rig or gameplay replacement.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;s=path.read_text(encoding='utf-8')
 if note not in s:
  head,tail=s.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
queue=BASE/'docs/art/moba/CREATURE_FACTORY_REPAIR_QUEUE_2026-11-15.md';s=queue.read_text(encoding='utf-8').replace('Local repair and native checks in progress','Local geometry/rig/Workshop checks passed; faint baked moss detail remains');queue.write_text(s,encoding='utf-8')
intake=Path('D:/dev/_scratch/mech-art-direction/creature-factory-intake-2026-11-15/new-rigged-exports.json');rows=json.loads(intake.read_text());row=next(x for x in rows if x['id']=='sloth');row.update({'state':'first_local_repair_pass_complete','repaired_sha256':r['output_sha256'],'runtime_report':'res://docs/art/moba/sloth_m/local-repair-v1-2026-11-15/final-review-verification.json','remaining':'Faint baked moss detail and final visual/authored-animation polish'});intake.write_text(json.dumps(rows,indent=2)+'\n');shutil.copy2(intake,BASE/'docs/art/moba/CREATURE_FACTORY_REPAIR_INTAKE_2026-11-15.json')
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));assert len(cat['entries'])==32;others=[x for x in cat['entries'] if x['id']!='sloth'];entry=next(x for x in cat['entries'] if x['id']=='sloth');entry['review_provenance']['runtime_report']='res://docs/art/moba/sloth_m/local-repair-v1-2026-11-15/final-review-verification.json';assert [x for x in cat['entries'] if x['id']!='sloth']==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n');shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(report,indent=2))
