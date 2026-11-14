from pathlib import Path
import urllib.request,json,hashlib,struct
ROOT=Path('D:/dev/_scratch/gorilla-free-animation')
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/ape_l/free-animation-test-2026-11-07')
OUT.mkdir(parents=True,exist_ok=True)
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-free-animation-test'}),timeout=60).read()
commit=json.loads(get('https://api.github.com/repos/Mesh2Motion/mesh2motion-app/commits/main'))['sha']
assetcommit=json.loads(get('https://api.github.com/repos/Mesh2Motion/mesh2motion-assets/commits/main'))['sha']
base=f'https://raw.githubusercontent.com/Mesh2Motion/mesh2motion-app/{commit}/'
records=[]
files=['README.md','static/assets/kaiju/model.glb','static/assets/kaiju/skeleton.glb']+[f'static/assets/kaiju/animations/{n}.glb' for n in ['attack','death','hit','idle','roar','swim','tail-attack','walk','walk-rm']]
for file in files:
    data=get(base+file);p=ROOT/'upstream'/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    r={'file':file,'url':base+file,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    if file.endswith('.glb'):
        magic,version,total,size,kind=struct.unpack_from('<IIIII',data)
        assert magic==0x46546c67 and version==2 and total==len(data) and kind==0x4e4f534a
        doc=json.loads(data[20:20+size]);clips=[]
        for a in doc.get('animations',[]):
            inputs=[doc['accessors'][s['input']] for s in a['samplers']]
            clips.append({'name':a.get('name'),'seconds':max(x['max'][0] for x in inputs)-min(x['min'][0] for x in inputs),'channels':len(a['channels'])})
        r.update(clips=clips,skins=[len(s['joints']) for s in doc.get('skins',[])],nodes=[n.get('name') for n in doc.get('nodes',[])])
    records.append(r);print(file,len(data),r.get('clips',[]),flush=True)
licenseurl=f'https://raw.githubusercontent.com/Mesh2Motion/mesh2motion-assets/{assetcommit}/LICENSE'
(OUT/'Mesh2Motion-assets-CC0.txt').write_bytes(get(licenseurl))
(OUT/'upstream-README.md').write_bytes(get(base+'README.md'))
(OUT/'source-clip-manifest.json').write_text(json.dumps({'app_commit':commit,'asset_commit':assetcommit,'asset_license':'CC0-1.0','software_license':'MIT per README','license_url':licenseurl,'files':records},indent=2))
