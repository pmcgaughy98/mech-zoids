import json,hashlib,shutil
from pathlib import Path
BASE=Path('D:/dev/new-mech-rpg');ROOT=Path(__file__).parent;OUT=BASE/'docs/art/moba/hornet_m/local-repair-v1-2026-11-14';r=json.loads((OUT/'repair-verification.json').read_text());a=json.loads((OUT/'independent-export-audit.json').read_text());p=json.loads((OUT/'visual-deformation-check.json').read_text());log=(ROOT/'godot-review.log').read_text(encoding='utf-8',errors='replace');shots=BASE/'reports/model_catalog/hornet-restoration-v1'
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256'] and len(p['poses'])==24
assert 'MODEL REPAIR CHECK PASS: hornet, 4 comparison versions, original/review sheets, 51-bone rig, current ChaseCamera3D' in log
assert not any(x in log for x in ['SCRIPT ERROR:','Assertion failed','Parse Error:'])
for name in ['lineup','review','original','comparison','comparison-back','review-sheet','actual-chase-camera']:assert (shots/(name+'.png')).stat().st_size>10000
cat=json.loads((BASE/'art/model_catalog/catalog.json').read_text(encoding='utf-8'));entry=next(x for x in cat['entries'] if x['id']=='hornet');assert entry['review_provenance']['repaired_sha256']==r['output_sha256'] and len(entry['review_models'])==4;assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'];gap=max(x['coincident_surface_gap_m'] for x in p['poses']);assert gap<1e-6
evidence={'passed':True,'tested_sha256':r['output_sha256'],'joint_count':51,'native_joint_tests':24,'maximum_seam_gap_m':gap,'godot_check':'Four native versions, original/revised sheets, 51-joint skeleton and current ChaseCamera3D','screenshots':'res://reports/model_catalog/hornet-restoration-v1','intact_archive_sha256':a['intact_archive_sha256'],'accepted_pre_rig_touchup_sha256':a['accepted_touchup_sha256'],'original_reference_sha256':a['original_reference_sha256'],'final_triangles':r['final_triangles'],'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'source_skeleton_rest_binds_scenes_clips_preserved':True,'summer_review_report':'res://docs/art/moba/hornet_m/local-repair-v1-2026-11-14/summer-review-verification.json','skin_scope':'Transferred from damaged downloaded rig onto restored geometry; original downloaded weights remain archived.','readiness':'High-detail review asset. Optimisation, authored gait/flight and independent appendage control work remain.'};(OUT/'final-review-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');shutil.copy2(ROOT/'godot-review.log',OUT/'godot-review.log')
readme=f'''# Hornet six-leg surface restoration

Restored November 14, 2026, after Fennec. The previously pending native Workshop check was completed after Wolf. Hornet's downloaded 51-joint rig had widespread missing surface across the head, wings, joints and body. The documented six-leg pre-rig touch-up also contained widespread cracks. An intact-source reconstruction was required instead of broad hole filling.

![Damaged rig and restored surface](before-after.png)

The current Workshop displays the restored **six-leg** layout, with four wings, two antennae, twin front barrels, abdomen and stinger retained. No new anatomy choice was inferred: the exact prior approved cut mask FL1/FL2/FR1/FR2/L2/L4/R2/R4 was reproduced. It removes the four floating claw pieces and the four tucked-under legs, retaining front/middle/rear on each side. The mask matched all 4,939 previously removed faces on the 40k classification proxy.

## Four-version comparison

C shows all four stages at matched scale: intact generated quality archive (extra limbs explicitly unapproved), accepted six-leg pre-rig touch-up (cracked surface), downloaded rig (damaged surface), and current restoration. The four-version camera is widened; existing two/three-version views retain their prior sizes. R switches between the immutable four generation PNGs and revised four-stage comparison sheets.

The accepted pre-rig file is the one prescribed for rigging by `docs/team/LINEUP_MODEL_RIG_AUDIT_2026-11-10.md`. Exact historical Meshy upload identity is not independently verified. Neither that touch-up nor the damaged rig is mislabeled as an intact quality source.

## Restoration and rig preservation

The intact generated source starts with 500,000 triangles and closed topology. The approved proxy classification was projected onto its geometry and smoothed only as a cut field; the source surface itself was not remeshed or broadly smoothed. New cut roots were closed. Two verified cut-created remnants, 441 and 277 vertices, were removed; their cut-field and position evidence is preserved under the scratch inspection files. They were leftovers of approved removals, not healthy limbs or armor.

The actual restored GLB contains **{r['final_triangles']:,} triangles**, zero open edges, zero over-shared edges and zero collapsed triangles. The independent audit verifies actual exported geometry, normals and UVs against the restored static staging asset. Original generator materials/textures are used, plus a local gunmetal cut-root finish. Original generation archive, pre-rig touch-up, damaged rig and all reference PNGs remain unchanged.

The downloaded rig's **51-joint hierarchy, rest transforms, inverse binds, scene nodes and clips** remain exact. Its original binary and original material/image records remain archived inside the append-only export. Skin was transferred from the actual downloaded rig using four nearest samples with inverse fourth-power weighting, normalized to the strongest four influences. Identical UV-seam positions receive identical queries. Original downloaded weights are preserved in the archive, not claimed byte-identical on the new surface. Transfer distances are recorded in `rig-transfer-verification.json`; missing donor regions make the transfer approximate.

Twenty-four actual native-joint diagnostics passed with maximum measured coincident-surface gap {gap:.9g} m, below the one-micrometre tolerance. Tests cover body/head/lower-front control groups, both antenna roots/tips, existing leg-control chains, both wing-control chains, abdomen and stinger. The source control grouping is preserved; independent six-leg gait/four-wing flight articulation is not claimed. The native scene is saved with restored rest pose and four packed immutable reference images.

![Six-leg underside and closures](underside-proof.png)

Textured front/side/back/top/underside/three-quarter views, both eyes, head, wings, antennae, six-leg layout, cut areas, abdomen/stinger and motion proofs were inspected. Godot's four-version comparison, original/revised sheets, 51-bone skeleton and current ChaseCamera3D check passed. Final lineup, front/back comparison, enlarged sheet and chase-camera screenshots were inspected in `reports/model_catalog/hornet-restoration-v1`.

This is a **high-detail review asset**. Optimisation and authored gait/flight remain; no gameplay/map replacement or performance approval is claimed.

## Exact sources and evidence

Intact generated archive: `art/model_catalog/sources/hornet_front - Hunyuan 3D v3.1 Pro.glb`, SHA256 `{r['intact_archive_sha256']}`.

Accepted pre-rig touch-up: `D:/user/Downloads/hornet_front - 6 legs touchup.glb`, SHA256 `{r['accepted_touchup_sha256']}`; exact copy preserved under `art/model_catalog/sources/`.

Downloaded rig: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_hornet_touchup_remeshed_25k_20261111_character.glb`, SHA256 `{r['source_sha256']}`; 21,743 triangles, 51 joints, no clips; exact archive copy retained.

Final: `hornet-rigged-local-repair-v1.glb`, SHA256 `{r['output_sha256']}`; native `hornet-rigged-local-repair-v1.blend`.

- `repair-verification.json`, `independent-export-audit.json`: actual-file checks and preservation scope.
- `surface-report.json`, `accepted-cut-mask.npz`, `rig-transfer-verification.json`: restoration, approved-cut and transferred-weight evidence.
- `visual-deformation-check.json`, `pose-proof.png`: 24 native-joint diagnostics.
- `review-front/left/back/right.png`: four-stage comparison sheets.
- `final-review-verification.json`, `godot-review.log`: runtime evidence and final hashes.
- `restored-six-leg-surface-STATIC-STAGING.glb`, `.blend`: geometry-only intermediate, not the active rigged display.

Canonical scripts and logs: `D:/dev/_scratch/mech-art-direction/hornet-review-2026-11-14/`, with snapshots here. Run approved-mask export, intact-surface reconstruction, bind transfer, independent actual-file audit, renders/poses and packaging in that order. Diagnostic topology counts in `input-audit.json` and `baseline-geometry-audit.json` describe damaged inputs and must not be treated as current output counts.

Fennec and all earlier roster work are preserved. No paid generation, commits or next model selection in this completion.
''';(OUT/'README.md').write_text(readme,encoding='utf-8')
note=f'''Hornet surface restoration completed November 14 after Fennec. The downloaded 51-joint rig and accepted six-leg pre-rig touch-up both had widespread surface cracks. Restored the intact 500k source using the exact approved FL1/FL2/FR1/FR2/L2/L4/R2/R4 cut mask (4,939 proxy faces), closed cut roots and removed only two verified cut-created remnants. Six legs, four wings, antennae, barrels, abdomen and stinger retained. Actual final {r['final_triangles']:,}-triangle export has zero open/over-shared/collapsed triangles. Original 51-joint hierarchy/rest/binds/scenes/clips preserved; skin transferred from the actual damaged rig, not claimed unchanged. Twenty-four native diagnostics passed with maximum measured seam gap {gap:.9g} m, below one-micrometre tolerance. Textured anatomy/local/motion views and final Godot four-version/original-review-sheet/51-joint/chase-camera screenshots inspected. Workshop and sheets show intact archive (extra limbs unapproved), accepted cracked pre-rig touch-up, damaged rig and restoration; four-version camera widened while prior two/three-version sizes are unchanged. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/hornet_m/local-repair-v1-2026-11-14/README.md. High-detail review asset; optimisation and authored gait/flight remain. Original archives/reference PNGs and all prior repairs preserved. No gameplay replacement or next model selection claimed.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
 path=BASE/rel;s=path.read_text(encoding='utf-8');parts=s.split('\n\n');matches=[i for i,v in enumerate(parts) if v.startswith('Hornet surface restoration completed November 14 after Fennec.') or v.startswith('Hornet restoration is the current target, November 14.') or v.startswith('Hornet restoration and its isolated Summer review, November 14:')]
 if matches:parts[matches[0]]=note;s='\n\n'.join(parts)
 elif s.startswith('# '):head,tail=s.split('\n',1);s=head+'\n\n'+note+'\n\n'+tail.lstrip('\n')
 else:s=note+'\n\n'+s
 path.write_text(s,encoding='utf-8')
shutil.copy2(Path(__file__),OUT/Path(__file__).name);shutil.copy2(ROOT/'surface-component-inspection.json',OUT/'removed-remnant-inspection.json');print(json.dumps(evidence,indent=2))

# Resolve the pending native check while retaining its original context and Summer evidence.
pending_path=OUT/'runtime-review-pending.json'
pending=json.loads(pending_path.read_text(encoding='utf-8'))
if 'previous_pending_state' not in pending:
    pending={'previous_pending_state':pending}
pending.update({'status':'Resolved: native Godot Workshop check passed and screenshots inspected','tested_sha256':r['output_sha256'],'native_godot_status':'passed; four versions, original/review sheets, 51-joint rig and current ChaseCamera3D','runtime_report':'res://docs/art/moba/hornet_m/local-repair-v1-2026-11-14/final-review-verification.json','summer_review':'passed; summer-review-verification.json preserved','remaining_native_check':None})
pending_path.write_text(json.dumps(pending,indent=2)+'\n',encoding='utf-8')
readme_path=OUT/'README.md'
readme_text=readme_path.read_text(encoding='utf-8')
readme_text+='\n## Earlier Summer review\n\nSummer Engine 0.7.0 independently passed its isolated four-version/51-joint review, with seven inspected 1600x900 views. That evidence remains in `summer-review-verification.json` and `summer-review/`. Its original pending-Workshop wording records the state at that earlier capture; the native Godot check is now resolved by `final-review-verification.json`. Model geometry and skin were not changed for this completion.\n'
readme_path.write_text(readme_text,encoding='utf-8')
catpath=BASE/'art/model_catalog/catalog.json'
cat=json.loads(catpath.read_text(encoding='utf-8'))
assert len(cat['entries'])==29
others=[x for x in cat['entries'] if x['id']!='hornet']
entry=next(x for x in cat['entries'] if x['id']=='hornet')
entry['review_provenance']['runtime_report']='res://docs/art/moba/hornet_m/local-repair-v1-2026-11-14/final-review-verification.json'
assert [x for x in cat['entries'] if x['id']!='hornet']==others
catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(__file__),OUT/Path(__file__).name)
print('Hornet pending native status resolved; Summer evidence and other entries preserved.')
