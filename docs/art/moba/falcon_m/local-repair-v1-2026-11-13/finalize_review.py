import json,hashlib,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/falcon_m/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/falcon-local-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'] and len(p['poses'])==24 and r['toes_per_foot']==4
assert 'MODEL REPAIR CHECK PASS: falcon, 3 comparison versions, original/review sheets, 45-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
cat=json.loads((BASE/'art/model_catalog/catalog.json').read_text(encoding='utf-8'));e=next(x for x in cat['entries'] if x['id']=='falcon');assert e['review_provenance']['repaired_sha256']==r['output_sha256']
source=BASE/e['source_model']['path'].removeprefix('res://');assert hashlib.sha256(source.read_bytes()).hexdigest()==e['source_model']['sha256']=='34d77973b951d096ff136061a7c820378e09fdc4c8b97c402b2989c0ed509947'
refs={}
for k,v in e['views'].items():
 value=hashlib.sha256((BASE/v['path'].removeprefix('res://')).read_bytes()).hexdigest();assert value==v['sha256'];refs[k]=value
removed=[x for x in p['poses'] if x['label'].startswith('removed-')];assert len(removed)==4 and max(x['max_displacement_m'] for x in removed)<1e-7
evidence={'passed':True,'tested_sha256':r['output_sha256'],'godot_check':'Three native versions, original/revised sheets, 45-joint skeleton and current ChaseCamera3D','screenshots':'res://reports/model_catalog/falcon-local-v1','intact_archive_sha256':e['source_model']['sha256'],'original_reference_sha256':refs,'joint_tests':24,'maximum_seam_gap_m':max(x['coincident_surface_gap_m'] for x in p['poses']),'removed_controls_max_surface_movement_m':max(x['max_displacement_m'] for x in removed),'toes_per_foot':4,'guarded_source_faces_retained':r['retained_toe_guard_faces']};(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Falcon four-toe feet and local repair

Completed November 13, 2026, after Preston approved removing the marked outer rear toe 1 on both feet. Each foot now has **three forward claws and one rear claw**. Both cuts have closed gunmetal mounting surfaces; the neighboring rear claws and original foot pads remain.

![Both corrected feet](feet-before-after.png)

The Workshop lineup and revised sheets now use `falcon-rigged-local-repair-v1.glb`. C compares the intact generated quality archive, downloaded five-toe rig and four-toe repair. R switches between the four original reference PNGs and revised comparison sheets. The archive's extra rear toes are explicitly labeled unapproved. The intact archive's exact historical Meshy-upload identity is not independently verified.

## Geometry and rig

The final actual GLB contains {r['final_triangles']:,} triangles and the original 45-joint hierarchy. The earlier chest gap closure and removal of 26 malformed triangles are retained. Source regression verifies {r['retained_toe_guard_faces']:,} guarded neighboring toe faces and {r['staged_faces_retained_exactly']:,} surface-stage faces unchanged. All original positions, normals and UV rows remain exact, as do the original materials, texture data, rest transforms and inverse binds. The raw source and surface-stage binary data remain exact prefixes of the append-only export.

Only residual influences from Bone_027/028 were moved to existing foot parent Bone_009, and Bone_037/038 to Bone_013. Other joint influences are retained. The removed controls remain in the skeleton for compatibility and produce zero visible surface movement. No remesh or rerig occurred.

The closures follow the actual cut contours, using concave-polygon triangulation to prevent folded cap faces. No original pad vertex was moved. The audit confirms zero open edges, zero collapsed triangles and zero inverted projected closure faces. One protected original balanced four-face contact with a tiny closed positive-volume assembly detail remains, so this is not a globally zero-over-shared-edge claim. New gunmetal finish is a single added material; original textures are unchanged.

![Both mounting areas](socket-before-after.png)

## Verification

Independent actual-file topology, geometry, skin and skeleton preservation audit passed. Twenty-four native-joint diagnostics passed with maximum measured coincident-surface gap {evidence['maximum_seam_gap_m']:.9g} m. Tests cover the body, tail, both wings, neck/head/beak, legs, ankles, feet, forward toes, both retained rear claws and all four unused removed-toe controls. Removed-control surface movement is {evidence['removed_controls_max_surface_movement_m']:.9g} m. The native scene was saved with its rest pose restored and four original references packed.

Textured front/side/back/top/underside/three-quarter views, both eyes, tail, both feet, both closure close-ups and diagnostic poses were inspected. Godot's three-version comparison, original/revised sheet, 45-bone skeleton and current ChaseCamera3D check passed. Final lineup, front/back comparisons, enlarged sheet and chase-camera screenshots were inspected under `reports/model_catalog/falcon-local-v1`.

![Original chest gap closure](before-after.png)

These are local deformation diagnostics, not finished flight/walk clips. The input has no animations. Separate Grok foundation/draft-clip files were inspected for lineage and left unchanged. Existing source bake roughness and remesh detail loss remain; no gameplay/map replacement or full-detail restoration is claimed.

## Exact files and evidence

Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_falcon_remeshed_25k_20261108_character.glb`, SHA256 `{r['source_sha256']}`; 23,579 triangles, 45 joints, no clips. Exact copy archived under `art/model_catalog/sources/`.

Final GLB: `falcon-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Editable scene: `falcon-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: scope and actual-file preservation/topology checks.
- `visual-deformation-check.json`, `pose-proof.png`: 24 native diagnostics.
- `final-review-verification.json`, `godot-review.log`: final hashes and runtime evidence.
- `feet-before-after.png`, `socket-before-after.png`, `before-after.png`: matched anatomy and local closure proofs.
- `review-front/left/back/right.png`: intact quality archive / downloaded rig / four-toe repair.
- `falcon-surface-only-staged.glb`, `surface-only-verification.json`: earlier surface-only stage with all five toes, preserved for provenance.

The earlier `anatomy-review-pending.json` is a historical checkpoint, resolved by Preston's yes to removing toe 1 on both feet. Original source GLBs/reference PNGs, Electric Eel and other roster work are preserved. Canonical scripts: `D:/dev/_scratch/mech-art-direction/falcon-review-2026-11-13/`, with snapshots here. Reconstruct the surface stage with `repair_model.py`; `inspect_toe.py` supplies the field data, `remove_toes.py` makes the anatomy correction, then audit, render, native checks and packaging follow. No paid generation or commits. No next model selected in this completion.
''';(OUT/'README.md').write_text(readme,encoding='utf-8')
pending_path=OUT/'anatomy-review-pending.json';pending=json.loads(pending_path.read_text());pending['status']='Resolved: user approved removal of toe 1 on both feet';pending['historical_checkpoint_only']=True;pending['resolution_report']='final-review-verification.json';pending_path.write_text(json.dumps(pending,indent=2)+'\n')
note=f'''Falcon four-toe repair completed November 13 after Preston approved removing marked outer rear toe 1 on both feet. Each foot has three forward claws and one rear claw; closed gunmetal mounts preserve both foot pads and the neighboring rear claws. Source regression retains all {r['retained_toe_guard_faces']:,} guarded neighboring toe faces. Chest gap and 26 malformed triangles also repaired. Final {r['final_triangles']:,}-triangle export has zero open/collapsed triangles and zero inverted projected closure faces; one protected original balanced four-face assembly contact remains. Original 45-joint hierarchy/rest/binds, source position/normal/UV rows and original textures/materials preserved; removed-chain residual weights reassigned locally to existing foot parents Bone_009/Bone_013. Twenty-four native diagnostics passed with maximum measured seam gap 0.000000123 m, below the one-micrometre tolerance; all four unused removed controls have zero surface movement. Textured close-ups, motion and final Godot three-version/original-review-sheet/45-joint/chase-camera screenshots inspected. Workshop lineup and revised sheets now show intact quality archive (extra rear toes unapproved), downloaded five-toe rig and four-toe repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/falcon_m/local-repair-v1-2026-11-13/README.md. Separate Grok draft assets, original archive/reference PNGs and all earlier roster work preserved. No finished flight/walk clips, gameplay replacement or next model selection claimed. Earlier toe-selection-pending state is resolved.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;text=path.read_text(encoding='utf-8');parts=text.split('\n\n');matches=[i for i,v in enumerate(parts) if v.startswith('Falcon is the current repair target, November 13,')];assert len(matches)==1,(rel,matches);parts[matches[0]]=note;path.write_text('\n\n'.join(parts),encoding='utf-8')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(evidence,indent=2))
