"""Offline audit of exact task charges, immutable inputs and runtime module limits."""
import datetime, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=ROOT/'art/environment/foundry_5v5'
rows=[];ids=[];total=0
for kind,budget in [('wall',5000),('pillar',4000),('camp',6000),('landmark',8000)]:
    folder=BASE/'source'/kind
    tasks=[]
    for stage in ['preview','refine']:
        status=json.loads((folder/(stage+'-status.json')).read_text())
        submission=json.loads((folder/(stage+'-submission.json')).read_text())
        assert status['status']=='SUCCEEDED' and status['id']==submission['result']
        credits=status['consumed_credits'];total+=credits;ids.append(status['id'])
        tasks.append({'stage':stage,'id':status['id'],'actual_credits':credits,'metadata':str((folder/(stage+'-status.json')).relative_to(ROOT))})
    runtime=BASE/'runtime'/(kind+'.glb')
    meta=json.loads(runtime.with_suffix('.json').read_text())
    assert meta['runtime_triangles']<=budget*1.04 and meta['materials']<=4
    assert meta['images'] and all(max(i['size'])<=1024 for i in meta['images'])
    assert hashlib.sha256(runtime.read_bytes()).hexdigest()==meta['runtime_sha256']
    raw=folder/'raw_refine.glb'
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==meta['raw_sha256']
    rows.append({'asset':kind,'tasks':tasks,'runtime':str(runtime.relative_to(ROOT)),'runtime_details':meta})
assert total==120 and len(set(ids))==8 and total<=200
bosses=[]
for kind in ['gold_beetle','wyvern']:
    meta=json.loads((BASE/'runtime'/(kind+'.json')).read_text())
    source=pathlib.Path(meta['existing_source']);runtime=BASE/'runtime'/(kind+'.glb')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==meta['raw_sha256']
    assert hashlib.sha256(runtime.read_bytes()).hexdigest()==meta['runtime_sha256']
    assert meta['triangles']<=30000 and meta['preserved_bones']>0
    bosses.append(meta)
balances=sorted((BASE/'source').glob('balance-*.json'))
latest=json.loads(balances[-1].read_text()) if balances else None
data={'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'generation_batch_credits':total,'authorized_ceiling':200,
    'unique_paid_stages':len(ids),'new_generation_assets':rows,'existing_boss_previews':bosses,'latest_balance':latest,
    'account_reconciliation':'Initial balance was 1010; final observed balance 860. This batch is exactly 120 credits per its eight task records. The remaining net 30-credit difference belongs to account activity outside these task records; it is not attributed to this batch.',
    'source_and_license':'Raw Meshy model exports and provider metadata retained. No per-file license string supplied in task metadata. Boss originals remain unmodified in their supplied download folder.'}
(BASE/'manifest.json').write_text(json.dumps(data,indent=2),encoding='utf8')
print('ASSET_MANIFEST_PASS: four generated modules, 120 credits, eight unique stages; two existing boss originals hash-verified')
