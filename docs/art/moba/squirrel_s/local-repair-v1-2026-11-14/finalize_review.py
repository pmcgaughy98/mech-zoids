import hashlib,json,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/squirrel_s/local-repair-v1-2026-11-14'
r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace')
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256']
assert len(p['poses'])+len(p['no_surface_motion'])==26 and len(r['holes_closed'])==5
assert 'MODEL REPAIR CHECK PASS: squirrel, 3 comparison versions, original/review sheets, 26-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
shots=BASE/'reports/model_catalog/squirrel-local-v1'
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256']
gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
evidence={'passed':True,'tested_sha256':r['output_sha256'],'triangles':22504,'joint_count':26,'native_joint_tests_with_surface_motion':len(p['poses']),'native_joint_tests_without_surface_motion':p['no_surface_motion'],'maximum_seam_gap_m':gap,'godot_check':'Three native GLB versions, original/revised sheets, original 26-joint rig and actual ChaseCamera3D','screenshots':'res://reports/model_catalog/squirrel-local-v1','intact_archive_sha256':a['intact_archive_sha256'],'original_reference_sha256':a['original_reference_sha256'],'boundary_edges':0,'over_shared_edges':2,'protected_contacts':'Two balanced four-face assembly contacts remain after local closure; underlying healthy source surfaces retained.','collapsed_triangles':0,'healthy_source_triangles_retained':22499,'all_original_vertex_and_skin_rows_preserved':True,'duplicate_uv_corner_rows':3}
(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Squirrel local topology repair

Completed November 14, 2026, after Shark. Removed 58 malformed triangles and closed five small openings. Both arms/paws, legs/feet, ears and eyes, the muzzle/teeth and complete plated tail remain.

![Three-stage review](review-front.png)

The Workshop lineup and four revised sheets use `squirrel-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches original generation PNGs and revised sheets. The archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Changes and preservation

Removed 48 attached single-triangle flaps, one isolated triangle, a two-triangle fragment, a three-triangle fragment, and four folded triangles beside openings. Five original-corner closures yield 22,504 triangles. All 22,499 healthy source faces remain exact, including the separate closed 6/4/440-face components; small closed source pieces were not removed indiscriminately.

The original 26-joint hierarchy, rest transforms, inverse binds, scenes, positions, normals, UV rows, weights, materials and textures remain unchanged. Original binary is an exact prefix. Appended accessors replace triangle connectivity and include three duplicate corner rows for the paw closure's UV mapping. Those rows copy the original positions/normals/joints/weights exactly; only their UVs sample one healthy neighboring island to avoid atlas color bleed. No remesh, rerig, weight reassignment, new geometric position, texture or material.

Independent actual-file audit: zero open edges and zero collapsed triangles. Two balanced four-face assembly contacts remain after closure, retaining underlying source surfaces. All five repair close-ups and textured head/tail/front/back/both sides/top/underside/three-quarter views were inspected.

All 26 original joints were tested with small rotations: {len(p['poses'])} produced measurable surface motion and {len(p['no_surface_motion'])} had no measurable motion. Maximum measured coincident-surface gap: {gap:.9g} m, below one-micrometre tolerance. Twenty-one representative posed renders were inspected, covering the body, head, paws, feet and both tail controls. Native Blender scene is saved in rest pose with four packed immutable reference images. These diagnostics do not establish a finished run, jump or tail animation, or independent ear articulation.

Godot 4.7.2's native Workshop three-version/original-review-sheet/26-joint/ChaseCamera3D check passed. All seven final screenshots were inspected in `reports/model_catalog/squirrel-local-v1/`.

Existing baked texture roughness and source detail loss remain. No gameplay/map replacement or authored clips. Earlier roster work and Hornet/Jellyfish's distinct pending native checks remain preserved.

## Exact files and reproduction

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 22,557 triangles, 26 joints, zero clips. Exact raw copy is archived in `art/model_catalog/sources/`.

Final: `squirrel-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Native: `squirrel-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: geometry and source-data preservation.
- `visual-deformation-check.json`, `pose-proof.png`: 26 native-joint diagnostics, 21 representative views.
- `all-closures.png`, `before-after.png`: all five matched patch close-ups and selected larger views.
- `review-front/left/back/right.png`: original quality / downloaded rig / local repair.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/squirrel-review-2026-11-14/`, with snapshots here. Reproduce geometry with `repair_model.py`, then `fix_patch_uv.py`, followed by audit/render/pose/package stages. Guides applied: project `blender-export-pipeline`, `atlas-rigging`, `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry and skin checks. Source archives/reference PNGs remain unchanged. No paid generation, commits or next model selection.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Squirrel local repair completed November 14 after Shark. Removed 58 malformed triangles and closed five small gaps, yielding 22,504 triangles. Both paws/feet, ears/eyes, muzzle/teeth and plated tail retained. All 22,499 healthy source faces and every original vertex/skin row, material/texture, source binary prefix and 26-joint hierarchy/rest/bind remain exact. Paw closure uses three duplicate original corner/skin rows with local UV mapping. Actual export has zero open/collapsed triangles; two balanced four-face assembly contacts retained after closure. {len(p['poses'])} moving-joint checks passed with maximum measured seam gap {gap:.9g} m; {len(p['no_surface_motion'])} original controls had no measured motion. All closure close-ups and 21 representative poses inspected. Native Godot three-version/original-review-sheet/26-joint/ChaseCamera3D check passed and final screenshots inspected. Lineup and sheets put intact model before downloaded remesh and repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/squirrel_s/local-repair-v1-2026-11-14/README.md. Existing baked roughness and grouped rig limits remain; no authored clips or gameplay replacement. Earlier roster work preserved. No next model selected.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
    path=BASE/rel;text=path.read_text(encoding='utf-8');head,tail=text.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));others=[x for x in cat['entries'] if x['id']!='squirrel'];e=next(x for x in cat['entries'] if x['id']=='squirrel');e['review_provenance']['runtime_report']='res://docs/art/moba/squirrel_s/local-repair-v1-2026-11-14/final-review-verification.json';assert [x for x in cat['entries'] if x['id']!='squirrel']==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(evidence,indent=2))
