import hashlib,json,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/shark_l/local-repair-v1-2026-11-14'
r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace')
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256']
assert len(p['poses'])+len(p['no_surface_motion'])==19 and len(r['holes_closed'])==7
assert 'MODEL REPAIR CHECK PASS: shark, 3 comparison versions, original/review sheets, 19-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
shots=BASE/'reports/model_catalog/shark-local-v1'
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256']
gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
evidence={'passed':True,'tested_sha256':r['output_sha256'],'triangles':23252,'joint_count':19,'native_joint_tests_with_surface_motion':len(p['poses']),'native_joint_tests_without_surface_motion':p['no_surface_motion'],'maximum_seam_gap_m':gap,'godot_check':'Three native GLB versions, original/revised sheets, original 19-joint rig and actual ChaseCamera3D','screenshots':'res://reports/model_catalog/shark-local-v1','intact_archive_sha256':a['intact_archive_sha256'],'original_reference_sha256':a['original_reference_sha256'],'boundary_edges':0,'over_shared_edges':1,'protected_contact':'One balanced original four-face closed-surface assembly contact retained.','collapsed_triangles':0,'healthy_source_triangles_retained':23245,'all_original_vertex_and_skin_rows_preserved':True,'duplicate_uv_corner_rows':3}
(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Shark local topology repair

Completed November 14, 2026, after Scorpion. Removed 56 malformed triangles and closed seven small surface openings. Mouth and teeth, both eyes, dorsal fin, paired pectoral and underside fins, tail lobes and armor remain.

![Three-stage review](review-left.png)

The Workshop lineup and four revised sheets use `shark-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and repaired model. R switches original generation PNGs and revised sheets. The archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Changes and preservation

Removed 40 single-triangle flaps, three three-triangle fragments and seven folded triangles beside the seven openings. Closed those openings with seven triangles using original vertex corners, with winding and original-normal alignment checked. Final count: 23,252 triangles. All 23,245 healthy source faces remain exact, including the original closed four-face assembly contact; small closed geometry was not deleted indiscriminately.

The original 19-joint hierarchy, rest transforms, inverse binds, scenes, positions, normals, UVs, weights, materials and textures are unchanged. The source binary remains an exact prefix. An appended index accessor replaces triangle connectivity; appended attribute accessors contain the unchanged source rows plus the three UV seam duplicates. Closure 4 has three duplicate corner rows copied from the original positions/normals/joints/weights, with local UVs sampled from one healthy neighboring island to remove atlas color bleed. All original attribute rows remain exact. No remesh, rerig, transferred weights, new geometric position, texture or material.

Independent actual-file audit: zero open edges, zero collapsed triangles. One balanced original four-face assembly contact remains. All seven closure close-ups and textured head, tail, front/back/both sides/top/underside/three-quarter views were inspected.

All 19 joints were tested with small native rotations: {len(p['poses'])} produced measurable motion and {len(p['no_surface_motion'])} had no measurable motion. Maximum measured coincident-surface gap: {gap:.9g} m, below one-micrometre tolerance. Eleven representative pose renders cover body, mouth, both pectoral fins and both tail lobes. Native Blender scene is saved in rest pose with four packed immutable references. These diagnostics do not establish a finished swim or bite animation.

Godot 4.7.2's native Workshop three-version/original-review-sheet/19-joint/ChaseCamera3D check passed. All seven final screenshots were inspected in `reports/model_catalog/shark-local-v1/`.

Existing baked texture roughness and source detail loss remain. No gameplay/map replacement or authored clips. Earlier roster work and Hornet/Jellyfish's distinct pending native checks remain preserved.

## Exact files and evidence

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 23,301 triangles, 19 joints, zero clips. Exact raw copy is archived under `art/model_catalog/sources/`.

Final: `shark-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Native: `shark-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: scope, topology and source preservation.
- `visual-deformation-check.json`, `pose-proof.png`: 19 native-joint diagnostics, eleven representative views.
- `all-closures.png`, `before-after.png`: all seven matched patch close-ups and selected larger views.
- `review-front/left/back/right.png`: original quality / downloaded rig / local repair.
- `final-review-verification.json`, `godot-review.log`: actual native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/shark-review-2026-11-14/`, with snapshots here. Reproduce geometry with `repair_model.py` then `fix_patch_uv.py` before the audit/render/pose/package stages. Guides applied: project `blender-export-pipeline`, `atlas-rigging` and `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry and skin checks. Original source/reference PNGs are unchanged. No paid generation, commits or next model selection.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Shark local repair completed November 14 after Scorpion. Removed 56 malformed triangles and closed seven small gaps, yielding 23,252 triangles. Mouth/teeth, eyes, dorsal/paired fins, tail and armor retained. All 23,245 healthy source faces and every original vertex/skin row, material/texture, source binary prefix and 19-joint hierarchy/rest/bind remain exact. Actual export has zero open/collapsed triangles; one balanced original closed-surface assembly contact retained. {len(p['poses'])} moving-joint checks passed with maximum measured seam gap {gap:.9g} m; {len(p['no_surface_motion'])} original controls had no measured motion. All closure close-ups and eleven representative poses inspected. Native Godot three-version/original-review-sheet/19-joint/ChaseCamera3D check passed and all final screenshots inspected. Lineup and sheets include intact model before downloaded remesh and repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/shark_l/local-repair-v1-2026-11-14/README.md. Existing texture-bake roughness remains; no authored swim clips or gameplay replacement. Earlier roster work preserved. No next model selected.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
    path=BASE/rel;text=path.read_text(encoding='utf-8');head,tail=text.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));others=[x for x in cat['entries'] if x['id']!='shark'];e=next(x for x in cat['entries'] if x['id']=='shark');e['review_provenance']['runtime_report']='res://docs/art/moba/shark_l/local-repair-v1-2026-11-14/final-review-verification.json';assert [x for x in cat['entries'] if x['id']!='shark']==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(evidence,indent=2))
