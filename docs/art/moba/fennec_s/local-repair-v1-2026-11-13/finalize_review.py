import json,hashlib,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/fennec_s/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/fennec-local-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'] and len(p['poses'])==19
assert 'MODEL REPAIR CHECK PASS: fennec, 3 comparison versions, original/review sheets, 44-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
cat=json.loads((BASE/'art/model_catalog/catalog.json').read_text(encoding='utf-8'));e=next(x for x in cat['entries'] if x['id']=='fennec');assert e['review_provenance']['repaired_sha256']==r['output_sha256'];assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'];gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
evidence={'passed':True,'tested_sha256':r['output_sha256'],'joint_count':44,'native_joint_tests':19,'maximum_seam_gap_m':gap,'godot_check':'Three native versions, original/revised sheets, 44-joint skeleton and current ChaseCamera3D','screenshots':'res://reports/model_catalog/fennec-local-v1','intact_archive_sha256':a['intact_archive_sha256'],'original_reference_sha256':a['original_reference_sha256'],'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'all_original_vertex_and_skin_rows_preserved':True};(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Fennec local topology repair

Completed November 13, 2026, after Falcon. Removed 52 malformed triangles and closed two small gaps on the tail armor and beside the left eye. Four legs, two ears, two eyes, one segmented tail, shoulder rings and hip mechanisms remain. No duplicate limbs were found or removed.

![Both local repairs](before-after.png)

The Workshop lineup and revised sheets now use `fennec-rigged-local-repair-v1.glb`. C compares the intact generated quality archive, downloaded rig and repaired model at matched display scale. R switches between the original four reference PNGs and revised comparison sheets. The original generated archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Preservation and export

The actual final GLB contains 23,722 triangles and the original 44-joint skeleton. All 23,720 healthy main-body source faces remain exact; two original-corner triangle closures were added. Every original position, normal, UV and skin row remains byte-identical, as do materials, textures, hierarchy, rest transforms and inverse binds. Only triangle connectivity was replaced, appended after the exact original source binary. No remesh, rerig, transferred skin, new material or new vertex was used.

Independent actual-file audit reports **zero open edges, zero over-shared edges and zero collapsed triangles**. Geometry stays within the downloaded 25k class, with one original primitive/material and no new texture data. Input has no animation clips. Separate staged Grok Fennec foundation/draft clips are unchanged and were not merged into this local repair.

Nineteen actual-joint diagnostics passed, covering the body, neck/head/muzzle, both ear roots and tips, all four leg/ankle chains, and tail root/mid/tip. Maximum measured coincident-surface gap is {gap:.9g} m, below the one-micrometre check tolerance. These are local deformation diagnostics, not finished walking or ability animations. The native scene is saved in its restored rest pose with four packed immutable original reference images.

Textured front/side/back/top/underside/three-quarter views, ears, both eyes, tail and both repair close-ups were inspected. Godot's native three-version comparison, original/revised sheets, 44-bone skeleton and current ChaseCamera3D check passed. Final lineup, front/back comparison, enlarged sheet and chase-camera screenshots were inspected in `reports/model_catalog/fennec-local-v1`.

Existing source texture-bake roughness and remesh detail loss remain. This is a local topology repair, not full-detail reconstruction or a gameplay/map replacement.

## Exact files and evidence

Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_fennec_remeshed_25k_20261108_character.glb`; SHA256 `{r['source_sha256']}`; 23,772 triangles, 44 joints, no clips. Exact raw copy retained under `art/model_catalog/sources/`.

Final GLB: `fennec-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Editable scene: `fennec-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: scope and actual-file preservation/topology checks.
- `visual-deformation-check.json`, `pose-proof.png`: 19 native diagnostics.
- `before-after.png`: matched close-ups of both repaired gaps.
- `review-front/left/back/right.png`: quality archive / downloaded rig / local repair.
- `final-review-verification.json`, `godot-review.log`: runtime evidence and source/reference hashes.

Canonical reproducible scripts: `D:/dev/_scratch/mech-art-direction/fennec-review-2026-11-13/`, with snapshots here. Original source GLB/reference PNGs, Falcon and all earlier roster work are preserved. No paid generation, commits or next model selection in this completion.
''';(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Fennec local repair completed November 13 after Falcon. Removed 52 malformed triangles and closed two small tail/eye-area gaps, yielding 23,722 triangles. Four legs, two ears, two eyes, one segmented tail and shoulder/hip mechanisms retained; no duplicate limbs found or removed. All 23,720 healthy main-body source faces retained. Every original vertex/skin row, material/texture, source binary and 44-joint hierarchy/rest/bind preserved; only triangle indices replaced. Actual-file audit has zero open/over-shared/collapsed triangles. Nineteen native-joint diagnostics passed with maximum measured seam gap {gap:.9g} m, below one-micrometre tolerance. Textured local close-ups, anatomy, motion and final Godot three-version/original-review-sheet/44-joint/chase-camera screenshots inspected. Workshop lineup and revised sheets now show intact quality archive, unrepaired download and local repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/fennec_s/local-repair-v1-2026-11-13/README.md. Original archive/reference PNGs, separate Grok drafts and all earlier roster repairs preserved. Existing bake roughness/detail loss remains; no finished walk, gameplay replacement or next model selection claimed.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;s=path.read_text(encoding='utf-8');parts=s.split('\n\n');matches=[i for i,v in enumerate(parts) if v.startswith('Fennec local repair completed November 13 after Falcon.')]
 if matches:parts[matches[0]]=note;s='\n\n'.join(parts)
 elif s.startswith('# '):head,tail=s.split('\n',1);s=head+'\n\n'+note+'\n\n'+tail.lstrip('\n')
 else:s=note+'\n\n'+s
 path.write_text(s,encoding='utf-8')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(evidence,indent=2))
