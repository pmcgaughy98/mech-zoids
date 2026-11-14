import hashlib, json, shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent
OUT=BASE/'docs/art/moba/pistol_shrimp_l/local-repair-v1-2026-11-14'
r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text())
log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/pistol-shrimp-local-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256']
assert len(p['poses'])+len(p['no_surface_motion'])==53
assert 'MODEL REPAIR CHECK PASS: pistol_shrimp, 3 comparison versions, original/review sheets, 53-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:
    assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256']
gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
evidence={'passed':True,'tested_sha256':r['output_sha256'],'triangles':25626,'joint_count':53,'native_joint_tests_with_surface_motion':len(p['poses']),'native_joint_tests_without_surface_motion':p['no_surface_motion'],'maximum_seam_gap_m':gap,'godot_check':'Three native GLB versions, original/revised sheets, original 53-joint rig and current ChaseCamera3D','screenshots':'res://reports/model_catalog/pistol-shrimp-local-v1','intact_archive_sha256':a['intact_archive_sha256'],'original_reference_sha256':a['original_reference_sha256'],'boundary_edges':0,'over_shared_edges':2,'protected_contacts':'Two balanced original closed-surface assembly contacts on large claw; not open gaps.','collapsed_triangles':0,'healthy_source_triangles_retained':25625,'all_original_vertex_and_skin_rows_preserved':True}
(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Pistol Shrimp local topology repair

Completed November 14, 2026, after Jellyfish. Removed ten verified single-triangle flaps and closed one tiny opening on the large snapping claw using original vertex corners. The asymmetric snapping/small claws, eight walking legs, two antennae, two dorsal vessels and tail fan remain.

![Local repair](before-after.png)

The Workshop lineup and four revised sheets now use `pistol-shrimp-rigged-local-repair-v1.glb`. C compares the intact generated model before the downloaded remeshed rig and local repair. R switches between original generation PNGs and revised comparison sheets. The intact archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Preservation and checks

The actual export has 25,626 triangles and the original 53 joints. All 25,625 healthy source triangles remain exact. Every original position, normal, UV and skin row is unchanged, as are the hierarchy, rest transforms, inverse binds, materials, textures, scenes and original binary prefix. Only triangle connectivity changed: ten stray triangles excluded and one closure added. No remesh, rerig, new material/texture, vertex, or transferred skin.

Independent actual-file audit: zero open edges, zero collapsed triangles. Two balanced original four-face assembly contacts remain on the claw. They were checked for balanced orientation and are documented rather than removing healthy source faces to eliminate those contacts.

All 53 joints were tested with small native rotations. {len(p['poses'])} tests produced measurable surface motion; {len(p['no_surface_motion'])} had no measurable surface motion. Maximum measured coincident-surface gap was {gap:.9g} m, below one-micrometre tolerance. Seventeen representative pose renders were inspected. The editable Blender scene is saved in rest pose with four packed immutable reference images. These tests do not establish independently articulated limbs or finished walking/snapping animations; the input has no authored clips.

Textured front/back/both sides/top/underside/three-quarter views, claw/head/tail close-ups and the small closure were inspected. Godot 4.7.2's actual Workshop three-version/original-review-sheet/53-joint/ChaseCamera3D check passed, and all seven final screenshots were inspected.

Existing baked texture roughness and source detail loss remain. This is a local topology repair, with no gameplay/map replacement. Earlier roster work, including Hornet and Jellyfish's separate pending native checks, is preserved.

## Exact files and reproduction

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 25,635 triangles, 53 joints, zero clips. Exact raw copy archived under `art/model_catalog/sources/`.

Final: `pistol-shrimp-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Native: `pistol-shrimp-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: geometry, original-data preservation and protected contacts.
- `visual-deformation-check.json`, `pose-proof.png`: actual-joint diagnostics.
- `before-after.png`, `review-front/left/back/right.png`: matched close-ups and three-stage review sheets.
- `final-review-verification.json`, `godot-review.log`: native runtime evidence; screenshots in `reports/model_catalog/pistol-shrimp-local-v1/`.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/pistol-shrimp-review-2026-11-14/`, with snapshots here. Project guides used: `blender-export-pipeline`, `atlas-rigging` and `atlas-asset-optimization`; Blender 5.2.2 and independent Python GLB audits provided geometry/rig checks. Original archives and generation references remain unchanged. No paid generation, commits or next model selection.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Pistol Shrimp local repair completed November 14 after Jellyfish. Removed ten malformed triangles and closed one tiny snapping-claw opening, yielding 25,626 triangles. Both asymmetric claws, eight walking legs, two antennae, dorsal vessels and tail fan retained. All 25,625 healthy source faces and every original vertex/skin row, texture/material, source binary prefix and 53-joint hierarchy/rest/bind preserved. Actual export has zero open/collapsed triangles; two balanced original closed-surface contacts on the claw remain documented. {len(p['poses'])} moving-joint diagnostics passed, with maximum seam gap {gap:.9g} m; {len(p['no_surface_motion'])} original controls had no measured surface motion. Textured close-ups and seventeen representative poses inspected. Native Godot three-version/original-review-sheet/53-joint/ChaseCamera3D check passed and all final screenshots inspected. Workshop and sheets include intact model before remeshed download and repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/pistol_shrimp_l/local-repair-v1-2026-11-14/README.md. Existing texture-bake roughness/grouped rig limits remain; no authored clips or gameplay replacement. Earlier roster work and Hornet/Jellyfish's distinct native-check pending states preserved. No next model selected.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
    path=BASE/rel;text=path.read_text(encoding='utf-8');head,tail=text.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
catalog_path=BASE/'art/model_catalog/catalog.json';catalog=json.loads(catalog_path.read_text(encoding='utf-8'));others=[e for e in catalog['entries'] if e['id']!='pistol_shrimp'];entry=next(e for e in catalog['entries'] if e['id']=='pistol_shrimp');entry['review_provenance']['runtime_report']='res://docs/art/moba/pistol_shrimp_l/local-repair-v1-2026-11-14/final-review-verification.json';assert [e for e in catalog['entries'] if e['id']!='pistol_shrimp']==others;catalog_path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n')
shutil.copy2(Path(__file__),OUT/Path(__file__).name)
print(json.dumps(evidence,indent=2))
