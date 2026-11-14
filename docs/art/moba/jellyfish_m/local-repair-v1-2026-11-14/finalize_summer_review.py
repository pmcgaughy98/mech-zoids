import hashlib, json, shutil
from pathlib import Path
from PIL import Image

BASE = Path('D:/dev/new-mech-rpg')
ROOT = Path(__file__).parent
OUT = BASE/'docs/art/moba/jellyfish_m/local-repair-v1-2026-11-14'
PROJECT = Path('D:/dev/_scratch/mech-art-direction/jellyfish-summer-review-2026-11-14')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((OUT/'repair-verification.json').read_text())
a = json.loads((OUT/'independent-export-audit.json').read_text())
p = json.loads((OUT/'visual-deformation-check.json').read_text())
log = (ROOT/'summer-runtime.log').read_text(encoding='utf-8',errors='replace')
assert a['passed'] and a['tested_sha256']==p['tested_sha256']==r['output_sha256']
assert sha(Path(r['output']))==sha(PROJECT/'assets/repaired-jellyfish.glb')==r['output_sha256']
assert len(p['poses'])==49 and not p['no_surface_motion']
assert 'SUMMER JELLYFISH REVIEW PASS: three native versions, original 49-joint rig, seven runtime frames' in log
assert not any(token in log for token in ['SCRIPT ERROR:', 'ERROR:', 'Assertion failed', 'Parse Error'])
gap = max(x['coincident_surface_gap_m'] for x in p['poses'])
assert gap<1e-6
evidence = OUT/'summer-review'
evidence.mkdir(exist_ok=True)
(evidence/'.gdignore').write_text('')
frames = []
for name in ['comparison-front','comparison-back','repaired-front','repaired-back','repaired-left','repaired-right','repaired-underside']:
    source = PROJECT/'evidence'/(name+'.png')
    assert Image.open(source).size==(1600,900)
    shutil.copy2(source,evidence/source.name)
    frames.append({'file':'summer-review/'+source.name,'sha256':sha(source),'resolution':[1600,900],'visually_inspected':True})
for name in ['jellyfish_review.gd','jellyfish_review.tscn','project.godot']:
    shutil.copy2(PROJECT/name,evidence/name)
shutil.copy2(ROOT/'summer-runtime.log',OUT/'summer-runtime.log')
report = {
    'passed':True, 'engine':'Summer Engine 0.7.0 / Compatibility',
    'tested_sha256':r['output_sha256'],'triangles':25912,'joint_count':49,
    'native_blender_joint_diagnostics':49,'maximum_measured_seam_gap_m':gap,
    'all_original_vertex_attribute_and_skin_rows_preserved':True,
    'all_healthy_source_faces_preserved':25912,'retained_tentacles':12,
    'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,
    'runtime_scope':'Isolated Summer scene: three native GLB versions, both rigged versions at 49 joints, seven rendered runtime views inspected.',
    'runtime_method':'Summer MCP batch editor saved the fixture. Its interrupted capture still produced seven frames; a separate installed Summer executable run then completed the same scene and logged the final PASS without errors.',
    'runtime_log':'summer-runtime.log','frames':frames,
    'native_godot_workshop_status':'pending; other Godot task remains active, no native Workshop/ChaseCamera3D pass claimed',
    'limitations':[r['limitations'],'Source archive exact historical Meshy-upload identity not independently verified.','No gameplay/map replacement or authored animation clips.'],
    'original_reference_sha256':a['original_reference_sha256'],'intact_archive_sha256':a['intact_archive_sha256']
}
(OUT/'summer-review-verification.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'final-review-verification.json').write_text(json.dumps(report,indent=2)+'\n')
pending = {'status':'Native Godot Workshop check pending; isolated Summer runtime review passed','tested_sha256':r['output_sha256'],'remaining':'When Godot is free, run and inspect Jellyfish three-version/original-review-sheet/49-joint/chase-camera check. Do not interrupt other runs.','summer_review':'summer-review-verification.json'}
(OUT/'runtime-review-pending.json').write_text(json.dumps(pending,indent=2)+'\n')
catalog_path = BASE/'art/model_catalog/catalog.json'
catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
others = [x for x in catalog['entries'] if x['id']!='jellyfish']
e = next(x for x in catalog['entries'] if x['id']=='jellyfish')
assert e['review_provenance']['repaired_sha256']==r['output_sha256'] and len(e['review_models'])==3
e['review_provenance']['summer_runtime_report'] = 'res://docs/art/moba/jellyfish_m/local-repair-v1-2026-11-14/summer-review-verification.json'
e['review_provenance']['native_workshop_check'] = 'Pending; isolated Summer review passed.'
assert [x for x in catalog['entries'] if x['id']!='jellyfish']==others
catalog_path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
readme = f'''# Jellyfish local triangle repair

Completed the local repair and isolated Summer review November 14, 2026. Removed seven verified stray single-triangle flaps; all 25,912 healthy source triangles remain. The twelve tentacles around the dome, rim, collars, armor and light details are retained. Front/back views show six tentacles each; the underside confirms twelve around the ring.

![Three-version runtime comparison](summer-review/comparison-front.png)

The Workshop catalog and four revised sheets now include the intact generated model before the downloaded remeshed rig and repaired version. C compares the three native models; R switches original/revised sheets. The source archive is the available quality baseline; its exact historical Meshy-upload identity is not independently verified.

## Rig and geometry preservation

The final GLB has 25,912 triangles and the original 49 joints. Every original position, normal, UV and skin row is unchanged. Hierarchy, rest transforms, inverse binds, scenes, materials, textures and original binary prefix remain exact. Only seven triangle records were excluded using a new index accessor. No remesh, rerig, weight transfer, new vertex, texture or material was introduced.

Independent actual-file audit: zero open edges, zero over-shared edges, zero collapsed triangles. All three healthy source surface components are retained. All 49 native-joint rotation diagnostics produce measurable surface movement and passed the one-micrometre seam tolerance. Maximum measured coincident-surface gap: {gap:.9g} m. Twelve representative posed renders were inspected. The native Blender scene is saved in rest pose with four packed immutable generation references. These checks do not establish twelve independently articulated tentacles or a finished swim animation.

## Runtime review and limits

Summer Engine 0.7.0 imported the actual three GLBs and verified 49 joints in both rigged versions. Its batch editor saved the comparison fixture. After the connector interrupted capture, the installed Summer executable completed a separate local run and logged `SUMMER JELLYFISH REVIEW PASS`. Seven 1600x900 runtime frames were inspected: front/back comparison, repaired front/back/both sides/underside. No script/assertion/render errors appear in the final run log.

The main Godot 4.7.2 Workshop/original-review-sheet/ChaseCamera3D check is still pending while another Godot task is active. No other run was stopped. This Summer evidence does not claim a native Workshop pass. Resume with the guarded command below when the Godot slot is free.

The existing baked dome is opaque and does not reproduce the reference sheets' clear window and visible internal canisters. Existing material-bake detail loss and grouped rig controls remain. This pass repairs local topology, with no gameplay/map replacement or authored clips. Original input and all four source sheets remain unchanged.

## Files and reproduction

Input: `{r['source']}`; SHA256 `{r['source_sha256']}`; 25,919 triangles, 49 joints, no animation clips. Exact copy is archived under `art/model_catalog/sources/`.

Final: `jellyfish-rigged-local-repair-v1.glb`; SHA256 `{r['output_sha256']}`. Editable native: `jellyfish-rigged-local-repair-v1.blend`.

Evidence: `repair-verification.json`, `independent-export-audit.json`, `visual-deformation-check.json`, `pose-proof.png`, `review-front/left/back/right.png`, `summer-review-verification.json`, `summer-runtime.log`, and seven images in `summer-review/`.

Canonical reproduction scripts: `D:/dev/_scratch/mech-art-direction/jellyfish-review-2026-11-14/`. Local Summer project: `D:/dev/_scratch/mech-art-direction/jellyfish-summer-review-2026-11-14/project.godot`; play `jellyfish_review.tscn`. Copies of that scene/script/config are saved with the evidence; GLBs remain in the local review project's `assets/` directory.

Tools applied: project `blender-export-pipeline`, `atlas-rigging` and `atlas-asset-optimization` guides, Blender 5.2.2, independent Python GLB audits, and Summer Engine. The desktop inspection helper timed out; no desktop changes were made through it. No paid generation or commits.

```powershell
if (@(Get-Process -Name 'Godot_v*' -ErrorAction SilentlyContinue).Count -eq 0) {{
    & 'C:/Users/pmcga/Games/Tools/Godot_v4.7.2/Godot_v4.7.2-stable_win64_console.exe' --path 'D:/dev/new-mech-rpg' --log-file 'D:/dev/_scratch/mech-art-direction/jellyfish-review-2026-11-14/godot-review.log' --rendering-method gl_compatibility --audio-driver Dummy --resolution 1280x720 --quit-after 1200 res://scenes/mech_catalog.tscn -- --model-repair-check --review-model=jellyfish --review-output=res://reports/model_catalog/jellyfish-local-v1
}}
```
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
note = f'''Jellyfish local triangle repair and Summer review completed November 14. Removed seven stray triangles, retaining all 25,912 healthy source faces and twelve tentacles. Every original vertex/skin row, material/texture, source binary prefix and 49-joint hierarchy/rest/bind remains exact. Export audit has zero open/over-shared/collapsed triangles. All 49 native Blender joint diagnostics move the surface and pass with maximum seam gap {gap:.9g} m. Textured views and twelve representative poses inspected. Summer's three-version/49-joint runtime review completed; seven 1600x900 front/back/side/underside frames inspected. Workshop catalog and revised sheets now put the intact generated model before the downloaded rig and local repair. Main Godot Workshop/ChaseCamera3D check remains pending while another task runs; no other run interrupted. Existing opaque baked dome, missing clear-window/internal-canister appearance and grouped rig controls remain; no authored swim clips or gameplay replacement claimed. SHA256 {r['output_sha256']}. Evidence: docs/art/moba/jellyfish_m/local-repair-v1-2026-11-14/README.md. Earlier roster work, including Hornet's separate native-Workshop pending state, preserved. No next model selected.'''
for rel in ['docs/art/moba/MODEL_WORKBENCH.md','docs/team/codex-lanes-2026-11-07/model-polish.md','docs/team/codex-lanes-2026-11-07/queued-roster-repair.md']:
    path = BASE/rel
    text = path.read_text(encoding='utf-8')
    text = text.replace('Hornet restoration is the current target, November 14.', 'Hornet restoration and its isolated Summer review, November 14:')
    head, tail = text.split('\n',1)
    path.write_text(head+'\n\n'+note+'\n\n'+tail.lstrip('\n'),encoding='utf-8')
shutil.copy2(Path(__file__),OUT/Path(__file__).name)
print(json.dumps({'passed':True,'joints':49,'tentacles':12,'summer_frames':7,'native_workshop':'pending','sha256':r['output_sha256']}))
