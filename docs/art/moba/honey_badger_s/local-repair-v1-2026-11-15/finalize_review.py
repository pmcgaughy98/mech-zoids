import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');c=json.loads((ROOT/'batch-config.json').read_text());OUT=BASE/f"docs/art/moba/{c['folder']}/local-repair-v1-2026-11-15";e=json.loads((OUT/'catalog-entry.json').read_text());r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/f"reports/model_catalog/{c['id']}-local-v1"
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'];assert len(p['poses'])+len(p['no_surface_motion'])==c['joints'];assert f"MODEL REPAIR CHECK PASS: {c['id']}, 2 comparison versions, original/review sheets, {c['joints']}-bone rig, current ChaseCamera3D" in log;assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'];gap=max(x['coincident_surface_gap_m'] for x in p['poses']+p['no_surface_motion']);assert gap<1e-6
report={'passed':True,'date':'2026-11-15','tested_sha256':r['output_sha256'],'triangles':c['final'],'joint_count':c['joints'],'native_joint_tests':c['joints'],'controls_above_1mm_motion':len(p['poses']),'controls_below_1mm_motion':len(p['no_surface_motion']),'maximum_seam_gap_m':gap,'boundary_edges':0,'over_shared_edges':c['contacts'],'collapsed_triangles':0,'healthy_source_faces_retained':c['healthy'],'original_attribute_and_skin_rows_preserved':True,'duplicate_uv_corner_rows':r.get('new_attribute_rows',0),'original_skeleton_rest_binds_materials_textures_preserved':True,'original_reference_sha256':a['original_reference_sha256'],'downloaded_input_sha256':r['source_sha256'],'intact_pre_remesh_available':False,'native_runtime_check':'Two native versions, original/review sheets, source skeleton and actual ChaseCamera3D','screenshots':'res://'+shots.relative_to(BASE).as_posix(),'limits':c['limits']};(OUT/'final-review-verification.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
uv_note='All original position/normal/UV/skin rows remain exact; no duplicate rows were needed.' if not r.get('uv_repair') else 'All original position/normal/UV/skin rows remain exact. Three duplicate original corners copy positions/normals/joints/weights, with local UV mapping only for the new closure.'
readme=f'''# {e['name']}: first local repair pass

Completed November 15, 2026, in Preston's new Creature Factory batch. {c['retained']}

![Downloaded rig and local repair](review-front.png)

Removed {c['remove']} malformed triangles and closed {c['caps']} small openings. Final export: {c['final']:,} triangles; zero open edges and zero collapsed triangles. All {c['healthy']:,} retained source triangles remain exact, including closed source components. {c['contacts']} balanced original assembly contacts remain. No anatomy removal, remesh or rerig.

{uv_note} The original {c['joints']}-joint hierarchy, rest transforms, inverse binds, scene nodes, materials and textures are unchanged. Original binary remains an exact prefix.

All {c['joints']} original controls were tested: {len(p['poses'])} above the 1 mm visual-movement threshold, {len(p['no_surface_motion'])} below it. Maximum measured coincident-surface separation: {gap:.9g} m. {len(p['rendered_poses'])} representative poses, any local closure close-ups, and textured front/back/both sides/top/underside/three-quarter views were inspected. Native workspace is saved in rest pose with four packed immutable reference PNGs. These diagnostics do not establish finished authored movement.

The native Godot Workshop two-version/original-review-sheet/{c['joints']}-joint/ChaseCamera3D check passed. All seven final screenshots were inspected. Existing entries remain preserved. New compact selector rows and fitted overview framing keep the growing lineup visible.

## Source and limits

{c['limits']} No gameplay installation, paid generation or new rig. No intact pre-remesh GLB was located. The two-version comparison explicitly shows archived downloaded rig before local repair; no proxy or duplicate rig is presented as an intact original. Four original generation PNGs remain separate from revised model sheets. Concept projection differences are reconciled conservatively; no new kit, names or gameplay rules were selected.

Input: `{r['source']}`, SHA256 `{r['source_sha256']}`; {r['before_triangles']:,} triangles, {c['joints']} joints, zero authored clips. Exact copy archived in `art/model_catalog/sources/` under the original filename.

Output: `{c['filename']}`, SHA256 `{r['output_sha256']}`. Editable native file has the same basename with `.blend`.

Evidence: `repair-verification.json`, `independent-export-audit.json`, `visual-deformation-check.json`, `pose-proof.png`, four `review-*.png` sheets, `final-review-verification.json`, and `godot-review.log`. Canonical scripts: `{ROOT.as_posix()}/`, with snapshots here. Project Blender-export, rigging and optimisation guides informed the checks. Original downloads/reference PNGs, existing authored lanes and previous repairs remain unchanged. No commits.
''';(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f"{e['name']} first local repair completed November 15 in the new Creature Factory batch. Removed {c['remove']} malformed triangles and closed {c['caps']} small gaps; {c['final']:,} triangles, zero open/collapsed triangles, {c['contacts']} balanced source assembly contacts. {c['retained']} Original {c['joints']}-joint hierarchy/rest/binds and original attribute/skin/material/texture rows preserved. All {c['joints']} diagnostic controls passed under one-micrometre seam tolerance (maximum {gap:.9g} m); {len(p['rendered_poses'])} representative poses and textured model views inspected. Native Godot two-version/original-review-sheet/{c['joints']}-joint/ChaseCamera3D check passed; all final screenshots inspected. Original rig archived; intact pre-remesh GLB not located and comparison correctly labeled. {c['limits']} SHA256 {r['output_sha256']}. Evidence: docs/art/moba/{c['folder']}/local-repair-v1-2026-11-15/README.md. Existing catalog entries preserved; no paid generation, new rig, gameplay replacement or commits."
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;text=path.read_text(encoding='utf-8')
 if note not in text:
  head,tail=text.split('\n',1);path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
queue=BASE/'docs/art/moba/CREATURE_FACTORY_REPAIR_QUEUE_2026-11-15.md';lines=queue.read_text(encoding='utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('| ') and f"| {e['name']} |" in line:
  cells=line.split('|');cells[-2]=' First local geometry/rig/Workshop pass complete; visual limits recorded ';lines[i]='|'.join(cells)
queue.write_text('\n'.join(lines)+'\n',encoding='utf-8')
intake=Path('D:/dev/_scratch/mech-art-direction/creature-factory-intake-2026-11-15/new-rigged-exports.json');rows=json.loads(intake.read_text());row=next(x for x in rows if x['id']==c['id']);row.update({'state':'first_local_repair_pass_complete','repaired_sha256':r['output_sha256'],'runtime_report':'res://'+(OUT/'final-review-verification.json').relative_to(BASE).as_posix(),'remaining':c['limits']});intake.write_text(json.dumps(rows,indent=2)+'\n');shutil.copy2(intake,BASE/'docs/art/moba/CREATURE_FACTORY_REPAIR_INTAKE_2026-11-15.json')
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));others=[x for x in cat['entries'] if x['id']!=c['id']];entry=next(x for x in cat['entries'] if x['id']==c['id']);entry['review_provenance']['runtime_report']='res://'+(OUT/'final-review-verification.json').relative_to(BASE).as_posix();assert [x for x in cat['entries'] if x['id']!=c['id']]==others;catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n');shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(e['name'],'FINAL PASS',r['output_sha256'])
