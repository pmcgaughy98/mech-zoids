"""Archive Preston's downloaded MeshForge exports and exact generation views.
No network, credentials, source editing, or paid tools. Reruns verify existing copies.
"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'art/model_catalog'
DOWNLOADS = Path('D:/user/Downloads')
SHEETS = Path('C:/Users/pmcga/Downloads')
VIEWS = ('front', 'left', 'back', 'right')


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def archive(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)
    assert sha(src) == sha(dst), f'Archive mismatch: {dst}'
    return {'path': 'res://' + dst.relative_to(ROOT).as_posix(),
            'source': str(src), 'sha256': sha(dst), 'bytes': dst.stat().st_size}


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / 'sources').mkdir(exist_ok=True)
    (DEST / 'sources/.gdignore').write_text('# Originals preserved; display copies are imported instead.\n')
    png_index = {}
    for path in (ROOT / 'docs/art/moba').rglob('*.png'):
        if path.parent.name in ('white_views', 'hunyuan_uploads_v1'):
            png_index.setdefault(sha(path), []).append(path.relative_to(ROOT).as_posix())
    entries = []
    for src in sorted(DOWNLOADS.glob('*Hunyuan 3D*.glb'), key=lambda p: p.name.lower()):
        key = src.name.split(' - ')[0].lower().removesuffix('_front').removesuffix('_s')
        key = key.replace('electric_eel_front_hunyuan', 'electric_eel')
        alternate = 'correct moon plate' in src.name
        entry_id = key + ('_back_plate_reference' if alternate else '')
        name = key.replace('_', ' ').title() + (' (back plate reference)' if alternate else '')
        entry = {'id': entry_id, 'name': name, 'source_model': archive(src, DEST/'sources'/src.name),
                 'display_model': f'res://art/model_catalog/display/{entry_id}.glb',
                 'artist_workspace': f'res://art/model_catalog/workspaces/{entry_id}.blend',
                 'status': 'Source static export; unrigged. Display proxy is not final game geometry.',
                 'reference_only': alternate, 'views': {}}
        if alternate:
            entry['status'] = 'Alternate shoebill: back moon plate reference ONLY. Primary shoebill is the other model.'
        for view in VIEWS:
            sheet_name = f'{key}_{view}' + ('_hunyuan' if key == 'electric_eel' else '') + '.png'
            sheet = SHEETS / sheet_name
            assert sheet.exists(), f'Missing exact downloaded sheet: {sheet}'
            item = archive(sheet, DEST/'references'/entry_id/f'{view}.png')
            item['project_matches'] = png_index.get(item['sha256'], [])
            assert item['project_matches'], f'No project provenance for {sheet}'
            entry['views'][view] = item
        entries.append(entry)
    assert len(entries) >= 26, f'Unexpected inventory: {len(entries)}'
    manifest = {'version': 1, 'date': '2026-11-07',
                'generation_chat': '01a1b3d2-bd2d-78f1-922f-9db2d803864e',
                'purpose': 'Shared in-game model/reference archive. Gallery display does not approve roster or polish.',
                'entries': entries}
    (DEST/'catalog.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Archived {len(entries)} models and {len(entries)*4} exact reference views.')
    for e in entries:
        print(e['id'], '=>', e['views']['front']['project_matches'])


if __name__ == '__main__':
    main()
