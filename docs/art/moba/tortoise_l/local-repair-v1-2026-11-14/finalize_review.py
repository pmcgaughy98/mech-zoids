import hashlib,json,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/tortoise_l/local-repair-v1-2026-11-14'
r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace')
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256']
assert p['joint_count']==23 and len(p['poses'])+len(p['no_surface_motion'])==23 and len(r['holes_closed'])==2
assert 'MODEL REPAIR CHECK PASS: tortoise, 3 comparison versions, original/review sheets, 23-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
shots=BASE/'reports/model_catalog/tortoise-local-v1'
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256']
gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
evidence={'passed':True,'tested_sha256':r['output_sha256'],'triangles':22626,'joint_count':23,'native_joint_tests_with_surface_motion':len(p['poses']),'native_joint_tests_below_1mm_motion_threshold':p['no_surface_motion'],'maximum_seam_gap_m':gap,'godot_check':'Three native GLB versions, original/revised sheets, original 23-joint rig and actual ChaseCamera3D','screenshots':'res://reports/model_catalog/tortoise-local-v1','intact_archive_sha256':a['intact_archive_sha256'],'original_reference_sha256':a['original_reference_sha256'],'boundary_edges':0,'over_shared_edges':2,'protected_contacts':'Two balanced four-face assembly contacts remain after local closure; underlying healthy source surfaces retained.','collapsed_triangles':0,'healthy_source_triangles_retained':22624,'all_original_vertex_and_skin_rows_preserved':True,'duplicate_uv_corner_rows':3}
(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Tortoise local topology repair

Completed November 14, 2026, after Squirrel. Removed 53 malformed triangles and closed two small openings. Four legs and feet, head and eyes, shell and rim, top dome and lights, and short tail remain.

![Three-stage review](review-front.png)

The Workshop lineup and four revised sheets use `tortoise-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches original generation PNGs and revised sheets. The archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Changes and preservation

Removed 48 attached single-triangle flaps, a three-triangle fragment, one isolated triangle and one folded triangle beside an opening. Two original-corner closures yield 22,626 triangles. All 22,624 healthy source faces remain exact, including both closed four-face components; small closed source pieces were not removed indiscriminately.

The original 23-joint hierarchy, rest transforms, inverse binds, scenes, positions, normals, UV rows, weights, materials and textures remain unchanged. Original binary is an exact prefix. Appended accessors replace triangle connectivity and include three duplicate corner rows for the first closure's UV mapping. Those rows copy the original positions/normals/joints/weights exactly; only their UVs sample one healthy neighboring island to avoid atlas color bleed. No remesh, rerig, weight reassignment, new geometric position, texture or material.

Independent actual-file audit: zero open edges and zero collapsed triangles. Two balanced four-face assembly contacts remain after closure, retaining underlying source surfaces. Both repair close-ups and textured head/tail/front/back/both sides/top/underside/three-quarter views were inspected.

All 23 original joints were tested with small rotations: {len(p['poses'])} produced measurable surface motion and {len(p['no_surface_motion'])} stayed below the 1 mm visual-movement threshold. Maximum measured coincident-surface gap: {gap:.9g} m, below one-micrometre tolerance. Seventeen representative posed renders were inspected, covering the body, head, four legs and tail controls. Native Blender scene is saved in rest pose with four packed immutable reference images. These diagnostics do not establish a finished walk or combat animation.

Godot 4.7.2's native Workshop three-version/original-review-sheet/23-joint/ChaseCamera3D check passed. All seven final screenshots were inspected in `reports/model_catalog/tortoise-local-v1/`.

Existing baked texture roughness and source detail loss remain. No anatomy removal, gameplay/map replacement or authored clips. The separate cyber-tortoise download was not substituted or modified. Earlier roster work and Hornet/Jellyfish's distinct pending native checks remain preserved.

## Exact files and reproduction

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 22,677 triangles, 23 joints, zero clips. Exact raw copy is archived in `art/model_catalog/sources/`.

Final: `tortoise-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Native: `tortoise-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: geometry and source-data preservation.
- `visual-deformation-check.json`, `pose-proof.png`: 23 native-joint diagnostics, 17 representative views.
- `all-closures.png`, `before-after.png`: both matched patch close-ups and selected larger views.
- `review-front/left/back/right.png`: original quality / downloaded rig / local repair.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/tortoise-review-2026-11-14/`, with snapshots here. Reproduce geometry with `repair_model.py`, then `fix_patch_uv.py`, followed by audit/render/pose/package stages. Guides applied: project `blender-export-pipeline`, `atlas-rigging`, `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry and skin checks. Source archives/reference PNGs remain unchanged. No paid generation, commits or next model selection.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Tortoise local repair completed November 14 after Squirrel. Removed 53 malformed triangles and closed two small gaps, yielding 22,626 triangles. Four legs/feet, head/eyes, shell/rim, dome/lights and short tail retained. All 22,624 healthy source faces and every original vertex/skin row, material/texture, source binary prefix and 23-joint hierarchy/rest/bind remain exact. First closure uses three duplicate original corner/skin rows with local UV mapping. Actual export has zero open/collapsed triangles; two balanced four-face assembly contacts retained after closure. {len(p['poses'])} moving-joint checks passed with maximum measured seam gap {gap:.9g} m; {len(p['no_surface_motion'])} original controls stayed below the 1 mm visual-movement threshold. All closure close-ups and 17 representative poses inspected. Native Godot three-version/original-review-sheet/23-joint/ChaseCamera3D check passed and final screenshots inspected. Lineup and sheets put intact model before downloaded remesh and repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/tortoise_l/local-repair-v1-2026-11-14/README.md. Existing baked roughness and grouped rig limits remain; no authored clips or gameplay replacement. Earlier roster work preserved. No next model selected.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
    path=BASE/rel;text=path.read_text(encoding='utf-8');head,tail=text.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));others=[x for x in cat['entries'] if x['id']!='tortoise'];e=next(x for x in cat['entries'] if x['id']=='tortoise');e['review_provenance']['runtime_report']='res://docs/art/moba/tortoise_l/local-repair-v1-2026-11-14/final-review-verification.json';assert [x for x in cat['entries'] if x['id']!='tortoise']==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(evidence,indent=2))
