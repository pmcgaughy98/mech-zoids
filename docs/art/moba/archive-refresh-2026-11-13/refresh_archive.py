"""Snapshot verified authored game exports for stale static archive entries only."""
from pathlib import Path
import hashlib
import json
import shutil
import struct

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
VERSIONS = {'gorilla': 'v38', 'rhino': 'v57', 'kangaroo': 'r12', 'hippo': 'r13', 'pangolin': 'r10'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

catalog_path = ROOT / 'art/model_catalog/catalog.json'
catalog = json.loads(catalog_path.read_text())
profiles = json.loads((ROOT / 'art/arena_models/authored_profiles.json').read_text())
models = OUT / 'models'
models.mkdir(exist_ok=True)
(models / '.gdignore').write_text('')
audit = []
for identity, version in VERSIONS.items():
    entry = next(e for e in catalog['entries'] if e['id'] == identity)
    source = ROOT / f'art/arena_models/{identity}.glb'
    authored = Path(profiles[identity]['source_file'])
    assert source.is_file() and authored.is_file()
    assert sha(source) == sha(authored), f'{identity}: deployed/source mismatch'
    raw = source.read_bytes()
    length, kind = struct.unpack_from('<II', raw, 12)
    gltf = json.loads(raw[20:20 + length])
    assert gltf.get('skins') and gltf.get('animations')
    assert all('uri' not in image for image in gltf.get('images', [])), 'External textures need packaging'
    target = models / f'{identity}-{version}.glb'
    if not target.exists():
        shutil.copy2(source, target)
    assert sha(target) == sha(source), f'{identity}: snapshot differs; preserve existing file'
    old_path = entry.get('runtime_archive_provenance', {}).get('previous_display_model', entry['display_model'])
    record = {'id': identity, 'version': version, 'source': str(source), 'authored_source': str(authored),
              'sha256': sha(source), 'snapshot': str(target), 'previous_display_model': old_path,
              'joint_count': len(gltf['skins'][0]['joints']), 'animation_count': len(gltf['animations'])}
    # Existing proxy-builder respects a completed target/report pair.
    target.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
    entry['display_model'] = 'res://' + target.relative_to(ROOT).as_posix()
    entry['status'] = f'Current authored game export {version}; {record["joint_count"]} joints, {record["animation_count"]} clips. Original design sheets retained; C compares the old proxy. Archive snapshot, not a new readiness approval.'
    entry['runtime_archive_provenance'] = record
    entry['review_models'] = [
        {'label': 'OLD STATIC PROXY\nHistorical archive display', 'path': old_path},
        {'label': f'CURRENT GAME EXPORT {version}\nRig and animations retained', 'path': entry['display_model']},
    ]
    audit.append(record)
catalog_path.write_text(json.dumps(catalog, indent=2) + '\n')
(OUT / 'sync-manifest.json').write_text(json.dumps(audit, indent=2) + '\n')
print(json.dumps(audit, indent=2))
