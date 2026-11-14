import hashlib, json, shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent
OUT=BASE/'docs/art/moba/scorpion_m/local-repair-v1-2026-11-14'
r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text())
log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/scorpion-local-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256']
assert len(p['poses'])+len(p['no_surface_motion'])==52
assert 'MODEL REPAIR CHECK PASS: scorpion, 3 comparison versions, original/review sheets, 52-bone rig, current ChaseCamera3D' in log
assert not any(token in log for token in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
names=['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']
for name in names:assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256']
gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
evidence={'passed':True,'tested_sha256':r['output_sha256'],'triangles':23970,'joint_count':52,'native_joint_tests_with_surface_motion':len(p['poses']),'native_joint_tests_without_surface_motion':p['no_surface_motion'],'maximum_seam_gap_m':gap,'godot_check':'Three native GLB versions, original/revised sheets, supplied 52-joint rig and current ChaseCamera3D','screenshots':'res://reports/model_catalog/scorpion-local-v1','intact_archive_sha256':a['intact_archive_sha256'],'original_reference_sha256':a['original_reference_sha256'],'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'healthy_source_triangles_retained':23970,'all_original_vertex_and_skin_rows_preserved':True,'initial_static_file_superseded_by':'Meshy_AI_scorpion_remeshed_25k_20261114_character.glb'}
(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Scorpion local topology repair

Completed November 14, 2026, using Preston's newly supplied rigged export. Removed 21 single-triangle flaps and one two-triangle folded fragment, preserving all 23,970 healthy source faces. Eight walking legs, both pincers, two side vessels, eyes and the complete raised tail are retained.

![Three-stage review](review-front.png)

The Workshop lineup and revised front/left/back/right sheets now use `scorpion-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches original generation PNGs and revised comparison sheets. The intact archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Correct input and preservation

The initial `Meshy_AI_scorpion_front_Huny_1111013939_texture.glb` has no skeleton or skin weights. Preston supplied `Meshy_AI_scorpion_remeshed_25k_20261114_character.glb`; that is the actual repair input, with 52 joints and no clips. The static inspection was not published as a rigged repair. Its audit remains under the scratch directory's `static-input-inspection/`.

The repaired GLB contains 23,970 triangles and the exact supplied 52-joint hierarchy/rest transforms/inverse binds. Every original position, normal, UV and skin row, material, texture, scene and original binary prefix remains unchanged. Only a new index accessor excludes the 23 malformed triangles. No remesh, rerig, transferred weights, added vertex, material or texture.

Independent actual-file audit reports zero open edges, zero over-shared edges and zero collapsed triangles. All three healthy closed surface components are retained, including the two separate 580/668-face components; these were not misclassified as scraps.

All 52 native joints were tested with small rotations. {len(p['poses'])} tests produced measurable surface motion, while {len(p['no_surface_motion'])} had no measurable motion. Maximum measured coincident-surface gap: {gap:.9g} m, below the one-micrometre tolerance. Twenty-one representative pose renders were inspected. The editable Blender scene is saved in rest pose with all four immutable reference PNGs packed. These diagnostics do not establish independent control of every appendage or finished walking/tail animations.

Textured front/back/both sides/top/underside/three-quarter views and head/tail/leg close-ups were inspected. Native Godot 4.7.2 Workshop verification passed for all three models, original/revised sheets, the 52-joint rig and actual ChaseCamera3D. All seven final screenshots were inspected in `reports/model_catalog/scorpion-local-v1/`.

Existing baked surface roughness/detail loss and grouped rig controls remain. No gameplay/map replacement or authored clips were added. Earlier roster work and Hornet/Jellyfish's separate native-check pending states remain preserved.

## Exact files and evidence

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 23,993 triangles, 52 joints, no clips. Exact raw copy archived in `art/model_catalog/sources/`.

Final: `scorpion-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Native editable file: `scorpion-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: topology and preservation checks.
- `visual-deformation-check.json`, `pose-proof.png`: 52 native-joint diagnostics and 21 representative views.
- `before-after.png`, `review-front/left/back/right.png`: matched local close-ups and three-stage sheets.
- `final-review-verification.json`, `godot-review.log`: final native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/scorpion-review-2026-11-14/`, with snapshots here. Guides applied: project `blender-export-pipeline`, `atlas-rigging`, `atlas-asset-optimization`. Blender 5.2.2 and independent Python GLB audits provided geometry/rig checks. Original archives/reference PNGs are preserved. No paid generation, commits or next model selection.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Scorpion local repair completed November 14 using Preston's new 52-joint character export. Initial texture-only static input was superseded and was not published as rigged. Removed 23 malformed triangles (21 single flaps and one two-face fold), retaining all 23,970 healthy faces, eight walking legs, both pincers and full raised tail. Every original vertex/skin row, material/texture, source binary prefix and 52-joint hierarchy/rest/bind remains exact. Actual-file audit has zero open/over-shared/collapsed triangles. {len(p['poses'])} moving-joint checks passed with maximum seam gap {gap:.9g} m; {len(p['no_surface_motion'])} original controls had no measured surface motion. Textured views and 21 representative poses inspected. Native Godot three-version/original-review-sheet/52-joint/ChaseCamera3D check passed and final screenshots inspected. Lineup and sheets include intact model before the downloaded remesh and repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/scorpion_m/local-repair-v1-2026-11-14/README.md. Existing baked roughness/grouped rig limits remain; no authored clips or gameplay replacement. Earlier roster work preserved. No next model selected.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
    path=BASE/rel;text=path.read_text(encoding='utf-8');head,tail=text.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
catalog_path=BASE/'art/model_catalog/catalog.json';catalog=json.loads(catalog_path.read_text(encoding='utf-8'));others=[e for e in catalog['entries'] if e['id']!='scorpion'];entry=next(e for e in catalog['entries'] if e['id']=='scorpion');entry['review_provenance']['runtime_report']='res://docs/art/moba/scorpion_m/local-repair-v1-2026-11-14/final-review-verification.json';assert [e for e in catalog['entries'] if e['id']!='scorpion']==others;catalog_path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(evidence,indent=2))
