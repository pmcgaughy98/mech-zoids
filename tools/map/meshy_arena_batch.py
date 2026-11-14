"""Meshy text-to-3D batch for the 3v3 arena's Foundry kit (Preston, 2026-11-14: "use meshy.ai ... use our credits").

Same provider, model and style words as Codex's 5v5 batch (tools/map5v5/meshy_batch.py), so the two maps share one
kit. Differences: the 3v3 pieces, a 300-credit cap, and previews run side by side instead of one at a time.

Safety, as in the 5v5 batch: the key comes only from MESHY_API_KEY and is never written or printed. An intent file is
written before every paid POST and the task id is saved before any poll, so a stage is never posted twice; a POST
that fails in an unknown way leaves the intent behind and that asset is skipped for a person to reconcile. A 429
(rate limit, nothing created) waits and tries again.

  python tools/map/meshy_arena_batch.py balance
  python tools/map/meshy_arena_batch.py run        # previews, then refines, then downloads; resumes where it stopped
  python tools/map/meshy_arena_batch.py run wall_run rock_cold   # only these
"""
import datetime, hashlib, json, os, pathlib, sys, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'art/environment/arena_3v3/source'
CAP = 300
COST = {'preview': 20, 'refine': 10}
STYLE = ('Stylized industrial science fiction MOBA Foundry environment piece. Broad clean beveled armor forms, '
         'dark blue charcoal steel, warm worn iron inset plates, small amber light strips, sparse yellow hazard trim. '
         'Strong readable silhouette, no text, no logos, no characters, no ground, isolated single object, flat bottom. ')
ROCK = ('Stylized industrial science fiction MOBA Foundry environment piece. Strong readable silhouette, broad simple '
        'forms, no text, no logos, no characters, no ground plane, isolated single object, flat bottom. ')
TEXTURE = ('Cohesive stylized Foundry steel: blue charcoal armor, warm iron inset plates, small amber luminous strips, '
           'sparse yellow hazard trim. Broad clean color blocks and gentle edge wear. No text or logos. Neutral material '
           'illumination, not baked shadows.')
ROCK_TEXTURE = ('Stylized dark slag basalt with soft blue-grey highlights, rusty warm iron scrap, a thin glowing amber '
                'seam. Broad clean color blocks, gentle wear. No text or logos. Neutral illumination, no baked shadows.')
WALL_TEXTURE = ('Dark blue charcoal steel plate, darker than mid grey, warm iron plinth band, one thin amber light line, '
                'sparse yellow hazard marks on the plinth. Broad clean colour blocks, gentle edge wear. No pale or white '
                'panels, no text or logos. Neutral illumination, no baked shadows.')
COLD_TEXTURE = ('Dark cold basalt in blue grey and charcoal, dull grey steel plates, a little dark rust. No orange, no glow, '
                'no lava. Broad clean colour blocks, gentle wear. No text or logos. Neutral illumination, no baked shadows.')
ASSETS = {
 'wall_piece': {'size_m': [2.0, 3.0, 1.2], 'polys': 3000, 'texture': TEXTURE, 'prompt': STYLE +
   'One short straight modular armored wall block, a little wider than tall, about twice as wide as thick. Heavy low '
   'plinth, two tall inset armor panels, a steel cap rail along the top, flat end faces so copies join in a row.'},
 'tower_base': {'size_m': [2.8, 2.95, 2.8], 'polys': 5000, 'texture': TEXTURE, 'prompt': STYLE +
   'One defense tower pedestal with no weapon: stepped octagonal plinth, four angled buttresses, a tapering faceted '
   'armored shaft and a flat round socket on top. Stout, a little taller than wide.'},
 'tower_head': {'size_m': [2.4, 0.9, 4.0], 'polys': 4000, 'texture': TEXTURE, 'prompt': STYLE +
   'One compact armored turret head on its own, no pedestal: wide faceted housing, front mantlet with twin short '
   'cannon barrels pointing forward, rear counterweight block, small sensor mast. Longer than wide, low.'},
 'core': {'size_m': [5.0, 4.35, 5.0], 'polys': 8000, 'texture': TEXTURE, 'prompt': STYLE +
   'One team base core machine: broad octagonal plinth, four heavy armored clamps holding a tall glowing energy '
   'reactor drum at the center, a cap ring on top. Imposing, about as wide as tall.'},
 'rock_slag': {'size_m': [7.0, 3.5, 7.0], 'polys': 6000, 'texture': ROCK_TEXTURE, 'prompt': ROCK +
   'One large slag rock outcrop: rough dark basalt boulders fused with a few broken steel girders and a cracked '
   'glowing amber seam. A low broad mound about twice as wide as tall.'},
 'rock_scrap': {'size_m': [6.0, 3.0, 6.0], 'polys': 6000, 'texture': ROCK_TEXTURE, 'prompt': ROCK +
   'One heap of industrial scrap on dark slag rock: stacked crushed armor plates, a tipped cargo container and thick '
   'bent pipes. A low broad mound about twice as wide as tall.'},
 'refinery': {'size_m': [10.0, 12.0, 10.0], 'polys': 6000, 'texture': TEXTURE, 'prompt': STYLE +
   'One distant refinery block for a far background: tall boxy factory hall with two smokestacks, pipe racks, '
   'catwalks and small amber windows. Big simple shapes.'},
 # Regenerated after the game feel and kit design reviews (docs/plan/meshy-arena-kit-review-2026-11-14.md): the first
 # wall read as separate pale locker slabs, the scrap rock as white debris.
 'wall_run': {'size_m': [2.0, 3.0, 1.2], 'polys': 3000, 'texture': WALL_TEXTURE, 'prompt': STYLE +
   'One section of a long continuous fortress wall: every line runs straight through both flat end faces so '
   'copies join seamlessly. Solid dark plate face, one horizontal plinth band, one thin horizontal light line '
   'across the full width. No vertical gaps, no separate slabs.'},
 'rock_cold': {'size_m': [6.0, 3.0, 6.0], 'polys': 6000, 'texture': COLD_TEXTURE, 'prompt': ROCK +
   'One compact solid boulder of dark cold fused rock, a single dense rounded blocky mass with two flat steel '
   'plates set flush into its surface. No loose shards, no thin pieces, no debris. Low and broad.'},
}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2), encoding='utf8')
    tmp.replace(p)


def load(p):
    return json.loads(p.read_text(encoding='utf8'))


def api(path, body=None):
    key = os.environ.get('MESHY_API_KEY')
    if not key:
        raise SystemExit('MESHY_API_KEY missing; no other credential is looked for.')
    req = urllib.request.Request('https://api.meshy.ai/openapi/' + path,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.load(res)


def get(path):
    for attempt in range(5): # reads are free and safe to repeat
        try:
            return api(path)
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 4:
                raise
            time.sleep(10)


def reserved():
    return sum(load(f)['reserved_credits'] for f in OUT.glob('*/*-intent.json'))


def submit(asset, stage, body):
    folder = OUT / asset
    sub, intent = folder / (stage + '-submission.json'), folder / (stage + '-intent.json')
    if sub.exists():
        return load(sub)['result']
    if intent.exists():
        print(asset, stage, 'UNCERTAIN: intent without submission; skipped, reconcile by hand')
        return None
    if reserved() + COST[stage] > CAP:
        print(asset, stage, 'skipped: would pass the', CAP, 'credit cap')
        return None
    save(intent, {'request': body, 'reserved_credits': COST[stage], 'at': now()})
    while True:
        try:
            result = api('v2/text-to-3d', body)
            break
        except urllib.error.HTTPError as e:
            if e.code == 429: # rate limited: nothing was created, so waiting and posting again is safe
                time.sleep(20)
                continue
            msg = e.read().decode(errors='replace')[:400]
            if 400 <= e.code < 500: # refused outright, nothing created or charged
                intent.unlink()
                print(asset, stage, 'REFUSED', e.code, msg)
                return None
            print(asset, stage, 'UNCERTAIN', e.code, msg)
            return None
        except Exception as e:
            print(asset, stage, 'UNCERTAIN', type(e).__name__, e)
            return None
    save(sub, result) # the id, before any poll
    print(asset, stage, 'submitted', result.get('result'))
    return result['result']


def wait(tasks, stage):
    """tasks: {asset: id}. Polls until every task ends; returns {asset: status json}."""
    done = {}
    t0 = time.time()
    while len(done) < len(tasks) and time.time() - t0 < 2400:
        for asset, tid in tasks.items():
            if asset in done:
                continue
            st = get('v2/text-to-3d/' + tid)
            save(OUT / asset / (stage + '-status.json'), st)
            if st['status'] in ('SUCCEEDED', 'FAILED', 'CANCELED', 'EXPIRED'):
                done[asset] = st
                print(asset, stage, st['status'], 'credits', st.get('consumed_credits'))
        if len(done) < len(tasks):
            time.sleep(15)
    return done


def fetch(asset, stage, st):
    folder = OUT / asset
    for name, url in [('raw_' + stage + '.glb', st.get('model_urls', {}).get('glb')),
                      ('thumbnail_' + stage + '.png', st.get('thumbnail_url'))]:
        if not url:
            continue
        p = folder / name
        if not p.exists():
            urllib.request.urlretrieve(url, p)
        save(folder / (name + '.sha256.json'), {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                                                'bytes': p.stat().st_size, 'at': now()})


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else 'balance'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '.gdignore').touch() # raw exports stay out of Godot's import
    bal = get('v1/balance')
    save(OUT / ('balance-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.json'), bal)
    print('balance', json.dumps(bal))
    if action != 'run':
        return
    only = sys.argv[2:]
    todo = {a: s for a, s in ASSETS.items() if not only or a in only}
    for asset, spec in todo.items():
        save(OUT / asset / 'brief.json', spec)
    previews = {}
    for asset, spec in todo.items():
        tid = submit(asset, 'preview', {'mode': 'preview', 'ai_model': 'meshy-6', 'target_formats': ['glb'],
                                        'prompt': spec['prompt'], 'should_remesh': True, 'topology': 'triangle',
                                        'target_polycount': spec['polys']})
        if tid:
            previews[asset] = tid
    pst = wait(previews, 'preview')
    refines = {}
    for asset, st in pst.items():
        if st['status'] != 'SUCCEEDED':
            continue
        fetch(asset, 'preview', st)
        tid = submit(asset, 'refine', {'mode': 'refine', 'ai_model': 'meshy-6', 'target_formats': ['glb'],
                                       'preview_task_id': previews[asset], 'texture_resolution': '2k',
                                       'enable_pbr': True, 'remove_lighting': True,
                                       'texture_prompt': ASSETS[asset]['texture']})
        if tid:
            refines[asset] = tid
    rst = wait(refines, 'refine')
    spent = 0
    for asset, st in rst.items():
        if st['status'] == 'SUCCEEDED':
            fetch(asset, 'refine', st)
    for f in OUT.glob('*/*-status.json'):
        spent += load(f).get('consumed_credits') or 0
    bal2 = get('v1/balance')
    save(OUT / ('balance-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.json'), bal2)
    summary = {'at': now(), 'balance_before': bal, 'balance_after': bal2, 'charged_by_task_records': spent,
               'preview': {a: s['status'] for a, s in pst.items()}, 'refine': {a: s['status'] for a, s in rst.items()}}
    save(OUT / 'batch-summary.json', summary)
    print('SUMMARY', json.dumps(summary))


if __name__ == '__main__':
    main()
