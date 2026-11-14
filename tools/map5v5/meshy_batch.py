"""Explicit one-stage CLI for the authorized November 10 environment batch.

No key is written to disk. A submitted stage is never posted a second time.
Network failures on POST leave an intent marker requiring manual reconciliation.
"""
import argparse, datetime, hashlib, json, os, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'art/environment/foundry_5v5/source'
COMMON = ('Original stylized industrial science fiction MOBA Foundry environment module. '
          'Broad clean beveled armor forms, dark blue charcoal steel, warm worn iron inset plates, '
          'small amber luminous strips, restrained diagonal yellow hazard trim. '
          'Strong readable silhouette, manufactured mechanical details, no text, no logos, no characters, '
          'no terrain, no background, isolated single object. ')
ASSETS = {
 'wall': {'size_m':[6,2.6,1.6], 'polys':6000, 'prompt':COMMON + 'One straight modular armored barrier, long rectangular horizontal profile, about four times wider than thick. Flat vertical end sockets, heavy low plinth, three large armor panels, small recessed vent. Flat bottom. Not a ruin or building.'},
 'pillar': {'size_m':[2.4,4,2.4], 'polys':5000, 'prompt':COMMON + 'One square modular armored wall end pillar, stout upright four-sided tower post. Broad foot, chamfered square shaft with four inset steel panels, compact capped top, amber vertical locator strips on all four sides. Flat bottom. No thin wires.'},
 'camp': {'size_m':[3.6,3.2,3.6], 'polys':7000, 'prompt':COMMON + 'One neutral camp power installation: squat cylindrical repair capacitor with three thick armored supports, heavy circular foot, a compact amber energy canister at center, visible industrial cooling vents. All mechanical, no creatures, no flag. Not a walkable platform.'},
 'landmark': {'size_m':[5.2,5,5.2], 'polys':9000, 'prompt':COMMON + 'One neutral major objective reactor landmark, a broad octagonal industrial machine plinth supporting a tall split armored reactor housing, large amber luminous core exposed between two heavy upright jaws. Imposing solid silhouette. Flat bottom. No stairs, no creature, no traversable floor.'},
}

def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    temp=p.with_suffix(p.suffix+'.tmp'); temp.write_text(json.dumps(obj,indent=2),encoding='utf8'); temp.replace(p)

def api(path, body=None):
    key=os.environ.get('MESHY_API_KEY')
    if not key: raise SystemExit('MESHY_API_KEY missing; no credentials searched.')
    req=urllib.request.Request('https://api.meshy.ai/openapi/'+path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=60) as res: return json.load(res)

def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['balance','preview','refine','status','download']); p.add_argument('asset',nargs='?',choices=ASSETS); a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if a.action=='balance':
        b=api('v1/balance'); save(OUT / ('balance-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json'),b); print(json.dumps(b)); return
    if not a.asset: p.error('asset required')
    folder=OUT/a.asset; folder.mkdir(parents=True,exist_ok=True)
    spec=ASSETS[a.asset]; save(folder/'brief.json',spec)
    if a.action in ['preview','refine']:
        stage=a.action; taskfile=folder/(stage+'-submission.json'); intent=folder/(stage+'-intent.json')
        if taskfile.exists() or intent.exists(): raise SystemExit('Stage already submitted or uncertain; do not repeat POST. Reconcile existing id.')
        spent=0
        for f in OUT.glob('*/*-intent.json'): spent+=json.loads(f.read_text())['reserved_credits']
        cost=20 if stage=='preview' else 10
        if spent+cost>200: raise SystemExit('200 credit hard cap')
        for f in OUT.glob('*/*-submission.json'):
            prev=json.loads(f.read_text())['result']; statusfile=f.with_name(f.name.replace('-submission','-status'))
            status=api('v2/text-to-3d/'+prev); save(statusfile,status)
            if status['status'] not in ['SUCCEEDED','FAILED','CANCELED']: raise SystemExit('Another job is active; one at a time.')
        balance=api('v1/balance')
        if balance['balance']<cost: raise SystemExit('Not enough existing credits')
        body={'mode':stage,'ai_model':'meshy-6','target_formats':['glb']}
        if stage=='preview': body.update(prompt=spec['prompt'],should_remesh=True,topology='triangle',target_polycount=spec['polys'])
        else:
            prior=json.loads((folder/'preview-submission.json').read_text())['result']
            if api('v2/text-to-3d/'+prior)['status']!='SUCCEEDED': raise SystemExit('Preview not succeeded')
            body.update(preview_task_id=prior,texture_resolution='2k',enable_pbr=True,remove_lighting=True,
                texture_prompt='Cohesive stylized Foundry steel: blue charcoal armor, warm iron inset plates, small amber luminous strips, sparse yellow hazard trim. Broad clean color blocks and gentle edge wear. No text or logos. Neutral material illumination, not baked shadows.')
        save(intent,{'request':body,'reserved_credits':cost,'balance_before':balance,'submitted_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        result=api('v2/text-to-3d',body)
        save(taskfile,result) # persist id before any GET/poll
        print(a.asset,stage,json.dumps(result),'reserved credits',cost)
    else:
        stage='refine' if (folder/'refine-submission.json').exists() else 'preview'
        task=json.loads((folder/(stage+'-submission.json')).read_text())['result']
        data=api('v2/text-to-3d/'+task); save(folder/(stage+'-status.json'),data)
        print(a.asset,stage,data['status'],data.get('progress'))
        if a.action=='download' and data['status']=='SUCCEEDED':
            for name,url in [('raw_'+stage+'.glb',data.get('model_urls',{}).get('glb')),('thumbnail_'+stage+'.png',data.get('thumbnail_url'))]:
                if url:
                    path=folder/name
                    if not path.exists(): urllib.request.urlretrieve(url,path)
                    save(folder/(name+'.sha256.json'),{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'source_url':url})

if __name__=='__main__': main()
