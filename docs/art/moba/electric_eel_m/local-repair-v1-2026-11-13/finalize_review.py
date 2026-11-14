import json,hashlib,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/electric-eel-local-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'] and len(p['poses'])==18
assert 'MODEL REPAIR CHECK PASS: electric_eel, 3 comparison versions, original/review sheets, 56-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
cat=json.loads((BASE/'art/model_catalog/catalog.json').read_text(encoding='utf-8'));e=next(x for x in cat['entries'] if x['id']=='electric_eel');assert e['review_provenance']['repaired_sha256']==r['output_sha256']
source=BASE/e['source_model']['path'].removeprefix('res://');assert hashlib.sha256(source.read_bytes()).hexdigest()=='23d480d94c3c50c987c9ed59cba69162961b589cbfe300ae12d857c37c6ee127'
refs={k:hashlib.sha256((BASE/v['path'].removeprefix('res://')).read_bytes()).hexdigest() for k,v in e['views'].items()}
evidence={'passed':True,'tested_sha256':r['output_sha256'],'godot_check':'Three native versions, original/revised sheets, 56-joint skeleton and current ChaseCamera3D','godot_log':'D:/dev/_scratch/mech-art-direction/electric-eel-review-2026-11-13/godot-review.log','screenshots':'res://reports/model_catalog/electric-eel-local-v1','intact_archive_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'original_reference_sha256':refs,'joint_tests':18,'maximum_seam_gap_m':max(x['coincident_surface_gap_m'] for x in p['poses']),'removed_upper_controls_max_surface_movement_m':max(x['max_displacement_m'] for x in p['poses'] if x['label'].startswith('removed-'))}
(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Electric Eel two-prong tail and local repair

Completed November 13, 2026. Preston selected upper prong 1 for removal. The two lower prongs remain, with the upper opening closed by a fitted blue mounting plate. Both lower prongs and their source attachment geometry are retained; 197 guarded lower-prong faces remain exact.

![Upper prong removal, matched view](tail-before-after.png)

The Workshop lineup and revised sheets now use `electric-eel-rigged-local-repair-v1.glb`. C compares the intact generated quality archive, downloaded three-prong rig and repaired two-prong model. R switches between the original four reference PNGs and revised comparisons. The archive's extra upper prong is labeled unapproved. Exact historical Meshy-upload identity is not independently verified for the intact quality archive.

## Geometry and rig preservation

The final actual GLB contains {r['final_triangles']:,} triangles and the original 56-joint hierarchy. Six pre-existing gaps were closed and 69 malformed triangles removed. The upper prong was removed back to its mounting collar; its closure uses two clean planar faces. All original position, normal and UV rows remain unchanged, as do the original materials, texture data, rest transforms and inverse bind matrices. The original GLB and intermediate surface-stage binaries remain exact prefixes in the append-only export.

Residual weights from Bone_046/047/048 were reassigned only to their existing ancestor Bone_033. Other joint influences are preserved. The deleted controls remain in the skeleton for compatibility and produce zero rendered-surface movement. No remesh or rerig occurred.

Topology audit reports zero open edges and zero collapsed triangles. One original balanced four-face contact with a tiny closed positive-volume assembly detail is deliberately protected. This is not a globally zero-over-shared-edge claim. The sixth local body closure has three duplicated UV corners sampling a healthy bronze patch from the original texture; adjoining source bake roughness remains.

## Verification and evidence

Independent actual-file preservation/topology/skin audit passed. Eighteen native-joint diagnostics passed with maximum measured coincident-surface gap {evidence['maximum_seam_gap_m']:.9g} m, including three deleted-control tests with zero surface movement. Native pose diagnostics check local deformation; no finished movement clips are claimed.

Textured head, eyes, fins, profile, both tail prongs, all six repaired patches and diagnostic poses were inspected. Godot's native three-version comparison, original/revised sheet, 56-bone and current ChaseCamera3D check passed. Final lineup, front/back comparison, enlarged sheet and chase-camera screenshots were inspected under `reports/model_catalog/electric-eel-local-v1`.

- `repair-verification.json`: geometry scope and source identities.
- `independent-export-audit.json`: actual exported file and preservation audit.
- `visual-deformation-check.json`, `pose-proof.png`: 18 actual native-joint tests.
- `tail-before-after.png`, `local-proof-A.png`, `local-proof-B.png`: matched close-ups.
- `review-front/left/back/right.png`: intact quality archive / downloaded rig / repaired comparison sheets.
- `electric-eel-rigged-local-repair-v1.blend`: editable native scene with packed original references and restored rest pose.
- `final-review-verification.json`, `godot-review.log`: runtime evidence and source/reference hashes.

## Exact files

Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_electric_eel_remeshed_25k_20261108_character.glb`; SHA256 `{r['source_sha256']}`; 23,367 triangles, 56 bound joints, no animation clips. Exact copy retained under `art/model_catalog/sources/`.

Final GLB: `electric-eel-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`.

The prior surface-only stage is archived as `electric-eel-surface-only-staged.glb` with `surface-only-verification.json`; it still contains all three prongs and is not the active Workshop display. The original quality archive and reference PNGs are unchanged. Canonical reproducible scripts: `D:/dev/_scratch/mech-art-direction/electric-eel-review-2026-11-13/`; snapshots are alongside this file. Run `repair_model.py` only to reconstruct the archived surface stage, then `remove_upper.py` for the final anatomy. The final audit, native renders/poses and packaging follow in that order.

This is a local anatomy/topology repair. Pre-existing texture-bake roughness and remesh detail loss remain. Other roster entries and gameplay/map assets are preserved. No paid generation, commits or next-model change.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Electric Eel two-prong repair completed November 13 after Preston selected upper prong 1. Both lower prongs and 197 guarded source faces retained; upper opening closed at the collar with a blue mounting plate. Six pre-existing gaps closed and 69 malformed triangles removed. Final {r['final_triangles']:,}-triangle export has zero open/collapsed triangles and one protected original balanced four-face assembly contact. Original 56-joint hierarchy/rest/binds, source position/normal/UV rows and original materials/textures preserved; deleted-chain residual weights reassigned locally to existing Bone_033. Eighteen native diagnostics passed with zero measured seam gaps; all three removed controls have zero surface movement. Textured close-ups, motion and final Godot three-version/original-review-sheet/56-joint/chase-camera screenshots inspected. Workshop lineup and revised sheets now show intact quality archive (extra upper prong unapproved), downloaded three-prong rig and two-prong repair. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13/README.md. Original archive/reference PNGs and all previous roster repairs preserved. Existing bake roughness/detail loss remains; no finished gait or gameplay replacement claimed. The earlier staged/selection-pending state is resolved. No next model selected in this completion.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;text=path.read_text(encoding='utf-8');parts=text.split('\n\n');matches=[i for i,v in enumerate(parts) if v.startswith('Electric Eel is the current repair target, November 13.')];assert len(matches)==1,(rel,matches);parts[matches[0]]=note;path.write_text('\n\n'.join(parts),encoding='utf-8')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);print(json.dumps(evidence,indent=2))
