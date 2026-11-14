"""Rebuild the local arena registry. No generation/API calls; originals remain untouched."""
import argparse,json,hashlib,shutil,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'art/arena_models'
SPECIAL={
 'gorilla':Path('D:/dev/_scratch/gorilla/codex-move-visuals-2026-11-09/review-model.glb'),
 'rhino':Path('D:/dev/_scratch/rhino-donor-2026-11-08/armor-seam-polish-v38/rhino-polish-v38.glb')}
FLY={'dragonfly','falcon','hornet','hummingbird','jellyfish','shark','electric_eel'}
LARGE={'gorilla','rhino','hippo','bison','tortoise'}
SMALL={'fennec','squirrel','hummingbird','dragonfly','hornet','spider'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gltf(p):
 b=p.read_bytes();return json.loads(b[20:20+struct.unpack('<I',b[12:16])[0]])
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');ap.add_argument('--dry-run',action='store_true');ap.add_argument('--inspect',type=Path);ap.add_argument('--register');ap.add_argument('--source',type=Path);ap.add_argument('--profile',type=Path);args=ap.parse_args()
 if args.inspect:
  j=gltf(args.inspect);print(json.dumps({'file':str(args.inspect),'sha256':sha(args.inspect),'meshes':len(j.get('meshes',[])),'joints':[[j['nodes'][n].get('name',str(n)) for n in s.get('joints',[])] for s in j.get('skins',[])],'clips':{a.get('name','unnamed'):max(j['accessors'][s['input']].get('max',[0])[0] for s in a['samplers']) for a in j.get('animations',[])}},indent=2));return
 overrides_path=OUT/'authored_profiles.json'
 overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
 if args.register:
  assert not args.check and args.source and args.profile,'--register needs --source and --profile'
  body=json.loads(args.profile.read_text());j=gltf(args.source)
  clips={a.get('name',''):max(j['accessors'][s['input']].get('max',[0])[0] for s in a['samplers']) for a in j.get('animations',[])}
  assert j.get('skins') and clips,'Authored upgrade needs a rig and animation'
  assert body.get('idle') and body.get('walk'),'Profile needs idle and walk role names'
  mapping=body.get('clips',{})
  for role,full in mapping.items():assert full in clips,(role,full)
  for role in [body['idle'],body['walk']]:assert mapping.get(role,role) in clips,role
  for role,events in body.get('events',{}).items():
   assert mapping.get(role,role) in clips,role
   duration=clips[mapping.get(role,role)]
   assert all(0<=e[1]<=duration for e in events),role
  overrides[args.register]={'source_file':str(args.source.resolve()),'body':body}
 catalog=json.loads((ROOT/'art/model_catalog/catalog.json').read_text())
 valid_ids={e['id'] for e in catalog['entries'] if not e.get('reference_only') and e['id']!='gorilla_rigged'}
 if args.register:assert args.register in valid_ids,'Register a catalog design ID, not a new identity'
 entries=[]
 for e in catalog['entries']:
  k=e['id']
  if e.get('reference_only') or k=='gorilla_rigged':continue
  size='L' if k in LARGE else 'S' if k in SMALL else 'M'
  p=ROOT/e['display_model'].removeprefix('res://');assert p.is_file(),p
  row={'id':k,'name':e['name'],'glb':e['display_model'],'stage':'base_proxy','size_class':size,'height_cap':{'L':2.0,'M':1.65,'S':1.1}[size],'span_cap':{'L':3.4,'M':2.8,'S':1.8}[size],'hover':.45 if k in FLY else 0,'forward_yaw':0,'references':{v:d['path'] for v,d in e['views'].items()},'workspace':e.get('artist_workspace'),'source_sha256':e['source_model']['sha256'],'notes':'Static display proxy; no authored gait or final ability clips. Root presentation only.'}
  if k in SPECIAL or k in overrides:
   src=Path(overrides[k]['source_file']) if k in overrides else SPECIAL[k];assert src.is_file(),src
   dest=OUT/(k+'.glb');j=gltf(src)
   row.update(glb='res://art/arena_models/'+k+'.glb',stage='authored_trial',source_file=str(src),runtime_sha256=sha(src),clips=[a['name'] for a in j.get('animations',[])],notes='Current completed local animation trial; art and final kit polish remain open.')
   if k in overrides:
    row['body']=overrides[k]['body'].copy();row['body']['glb']=row['glb']
   if not args.check and not args.dry_run:
    OUT.mkdir(parents=True,exist_ok=True)
    if not dest.exists() or sha(dest)!=row['runtime_sha256']:shutil.copy2(src,dest)
   assert not args.check or (dest.exists() and sha(dest)==row['runtime_sha256']),dest
  entries.append(row)
 result={'version':1,'purpose':'Arena base roster and authored upgrade contract, not final art approval','entries':entries}
 if not args.check and not args.dry_run:
  OUT.mkdir(exist_ok=True);(OUT/'roster.json').write_text(json.dumps(result,indent=2)+'\n')
  if args.register:overrides_path.write_text(json.dumps(overrides,indent=2)+'\n')
 elif args.check:
  existing=json.loads((OUT/'roster.json').read_text());assert existing==result,'Registry stale: run builder without --check'
 print(json.dumps({'models':len(entries),'authored':[e['id'] for e in entries if e['stage']=='authored_trial'],'mode':'check' if args.check else 'dry-run' if args.dry_run else 'build'}))
if __name__=='__main__':main()
