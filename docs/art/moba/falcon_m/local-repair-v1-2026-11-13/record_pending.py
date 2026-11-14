import json,hashlib,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/falcon_m/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'] and len(p['poses'])==18
cat=json.loads((BASE/'art/model_catalog/catalog.json').read_text(encoding='utf-8'));e=next(x for x in cat['entries'] if x['id']=='falcon');assert e['display_model']=='res://art/model_catalog/display/falcon.glb'
source=BASE/e['source_model']['path'].removeprefix('res://');assert hashlib.sha256(source.read_bytes()).hexdigest()==e['source_model']['sha256']
for key,v in e['views'].items():assert hashlib.sha256((BASE/v['path'].removeprefix('res://')).read_bytes()).hexdigest()==v['sha256'],key
for name in ['falcon-surface-only-staged.glb','surface-only-verification.json']:
 src=Path(r['output']) if name.endswith('.glb') else OUT/'repair-verification.json';dest=OUT/name
 if not dest.exists():shutil.copy2(src,dest)
gap=max(x['coincident_surface_gap_m'] for x in p['poses']);anatomy={'status':'Awaiting user toe selection','current_toes_per_foot':5,'current_forward_toes_per_foot':3,'current_rear_toes_per_foot':2,'recommended_action':'Remove labeled outer rear toe 1 on both feet; retain three forward toes and one rear toe each.','selection_image':'foot-extra-toe-labeled.png','proposed_removed_chains':['Bone_028/Bone_027','Bone_038/Bone_037'],'proposed_existing_parents':['Bone_009','Bone_013'],'no_anatomy_cut_yet':True,'catalog_unchanged':True,'source_model_sha256':e['source_model']['sha256'],'reference_sha256':{k:v['sha256'] for k,v in e['views'].items()},'independent_skin_rig_audit_passed':True,'native_joint_tests':18,'max_coincident_surface_gap_m':gap,'staged_sha256':r['output_sha256'],'staged_grok_foundation_scope':'Separate staged Falcon foundation and its draft clips inspected for lineage only; neither modified nor merged. Current downloaded source and local repair have no animation clips.'};(OUT/'anatomy-review-pending.json').write_text(json.dumps(anatomy,indent=2)+'\n')
readme=f'''# Falcon local repair, anatomy selection pending

November 13, 2026. Next repair after Electric Eel. The current downloaded 45-joint rig has been compared with the intact generated quality archive and all four original reference PNGs. Two legs, folded wings, two eyes, beak, three-column layered tail fan and paired backpack fins are retained.

## Toe decision

The actual mesh has **five toes on each foot: three forward claws plus two rear claws**. The marked outer rear toe is recommended for removal on both sides, leaving three forward and one rear. This is an anatomy decision requiring Preston's choice; no toe has been cut, no deleted-chain skin has been reassigned, and no final Workshop promotion is claimed.

![Five-toe foot and recommended removal](foot-extra-toe-labeled.png)

The marked digit corresponds to Bone_028/027 on the positive-X foot and Bone_038/037 on the negative-X foot. Existing parent controls are Bone_009 and Bone_013. The retained central rear toe is Bone_026/025 and Bone_036/035. Read-only candidate-contour measurements are in the scratch directory; do not interpret them as an accepted anatomy change.

## Completed independent repair

Removed 26 malformed triangles and closed one small chest opening using the existing triangle corners. The actual staged file has **23,554 triangles**, zero boundary edges and zero collapsed triangles. A tiny original closed four-face assembly detail and its balanced four-face contact are deliberately retained. This is not a globally zero-over-shared-edge claim.

All original vertex attribute rows, skin weights, materials, textures, 45-joint hierarchy, rest transforms and inverse binds remain exact. The source binary is an exact prefix of the append-only export. No vertex was moved, no skin was transferred and no remesh/rerig occurred. Independent actual-file audit confirms 23,549 healthy main-body faces retained.

Eighteen actual-joint diagnostics passed with maximum measured coincident-surface gap {gap:.9g} m, covering the body, tail, both wings, neck/head/beak, legs, ankles, feet and central toes. Joint roles were checked against the source bind locations. Pose images are diagnostic bends, not finished movement animations. Rest poses are restored in the saved native workspace.

Textured front/side/back/top/underside/three-quarter views, eyes/head, tail, brightened underside foot and chest closure were inspected. The layered tail uses three primary columns; overlapping center plates are retained as armor rather than inferred extra limbs. Surface bake roughness and reduced-detail armor still remain.

![Chest closure](before-after.png)

## Files and resume point

- `falcon-rigged-local-repair-v1.glb`: current staged result, SHA256 `{r['output_sha256']}`.
- `falcon-rigged-local-repair-v1.blend`: native workspace with four packed immutable original references.
- `falcon-surface-only-staged.glb`, `surface-only-verification.json`: preserved topology stage before any toe surgery.
- `repair-verification.json`, `independent-export-audit.json`, `visual-deformation-check.json`: actual-file and deformation evidence.
- `pose-proof.png`, `review-front/left/back/right.png`: prepared diagnostics and matched quality archive/download/repair sheets.
- `catalog-entry.json`: prepared candidate only; live Falcon catalog entry remains unchanged.
- `anatomy-review-pending.json`: selection, source/reference hashes and next-step scope.

Raw input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_falcon_remeshed_25k_20261108_character.glb`, SHA256 `{r['source_sha256']}`, 23,579 triangles, 45 bound joints, no animation clips. An exact raw copy is preserved in `art/model_catalog/sources/`. The intact generated archive SHA256 is `{e['source_model']['sha256']}`; its exact historical Meshy-upload identity is not independently verified.

Separate Grok Falcon foundation/draft-clip files were inspected for lineage and left unchanged. They are staged work, not an accepted substitute for the current downloaded repair source. No gameplay or other roster assets were changed.

Canonical scripts: `D:/dev/_scratch/mech-art-direction/falcon-review-2026-11-13/`. If Preston selects removal, use the preserved surface stage, cut only the marked rear toe pair, preserve the other four toes and their joints, close both sockets and reassign only residual deleted-chain weights to the two existing foot parents. Then audit the actual final GLB, rerun native deformations including unused removed controls, regenerate views/sheets, promote only Falcon's catalog entry and run/inspect the Godot comparison/sheet/45-joint/chase-camera check. If he chooses five toes, record that decision before promotion and runtime review.

No final Godot acceptance has been run while the toe choice is pending. No paid generation, commits or new model selection.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Falcon is the current repair target, November 13, after Electric Eel. An isolated copy has 26 malformed triangles removed and one chest gap closed, yielding 23,554 triangles. Actual-file audit confirms all original vertex/skin rows, materials/textures, source binary and 45-joint hierarchy/rest/binds preserved; 23,549 healthy main-body source faces retained. Zero open/collapsed triangles; one protected original balanced four-face contact remains. Eighteen native-joint diagnostics passed with zero measured surface seam gaps; textured head, wings, tail, feet, chest closure and motion inspected. Close-up revealed five toes per foot: three forward and two rear. Awaiting Preston's choice: remove labeled outer rear toe 1 on both feet (recommended) or keep five. No toe cut inferred, live catalog unchanged, no final Godot completion claimed. Prepared quality archive/download/repair sheets and candidate catalog entry are in docs/art/moba/falcon_m/local-repair-v1-2026-11-13/. Staged SHA256 {r['output_sha256']}. Resume from its README and D:/dev/_scratch/mech-art-direction/falcon-review-2026-11-13/. Separate staged Grok foundation/draft clips were inspected and left unchanged. Electric Eel and all previous roster repairs remain current.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;s=path.read_text(encoding='utf-8');parts=s.split('\n\n');matches=[i for i,v in enumerate(parts) if v.startswith('Falcon is the current repair target, November 13,')]
 if matches:parts[matches[0]]=note;s='\n\n'.join(parts)
 elif s.startswith('# '):head,tail=s.split('\n',1);s=head+'\n\n'+note+'\n\n'+tail.lstrip('\n')
 else:s=note+'\n\n'+s
 path.write_text(s,encoding='utf-8')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);shutil.copy2(ROOT/'inspect_toe.py',OUT/'inspect_toe.py');print(json.dumps(anatomy,indent=2))
