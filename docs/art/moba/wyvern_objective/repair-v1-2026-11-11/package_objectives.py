"""Archive immutable inputs and build labeled review sheets; --publish adds catalog entries."""
import sys,json,hashlib,shutil,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent; BASE=Path('D:/dev/new-mech-rpg')
FONT='C:/Windows/Fonts/arial.ttf'
def font(n): return ImageFont.truetype(FONT,n)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def res(p): return 'res://'+p.relative_to(BASE).as_posix()
def archive(src,dst,expected):
    assert sha(src)==expected
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists(): assert sha(dst)==expected
    else: shutil.copy2(src,dst)
    assert sha(dst)==expected
def sheet(out,name,view,title):
    im=Image.new('RGB',(1440,870),'#14212c'); d=ImageDraw.Draw(im)
    d.text((22,12),name+' / '+title,font=font(28),fill='white')
    d.text((22,55),'DOWNLOADED RIG / BEFORE REPAIR',font=font(23),fill='#b8d8ee')
    d.text((742,55),'REPAIRED / SAME NATIVE SKELETON',font=font(23),fill='#93efbb')
    for i,v in enumerate(['before','after']):im.paste(Image.open(out/f'{v}-{view}.png').convert('RGB'),(i*720,91))
    d.text((22,820),'True pre-remesh GLB unavailable. These compare the rigged download with its local repair.',font=font(22),fill='#f2cb84')
    dest=out/f'review-{view}.png';im.save(dest);return dest
def montage(out,files,name,dest,cols=3,cell=340):
    rows=math.ceil(len(files)/cols);im=Image.new('RGB',(cols*cell,rows*(cell+30)+48),'#14212c');d=ImageDraw.Draw(im)
    d.text((12,10),name,font=font(24),fill='white')
    for i,p in enumerate(files):
        x=i%cols*cell;y=48+i//cols*(cell+30)
        pic=Image.open(p).convert('RGB');pic.thumbnail((cell,cell));im.paste(pic,(x+(cell-pic.width)//2,y))
        d.text((x+8,y+cell+3),p.stem,font=font(18),fill='white')
    im.save(out/dest)
entries=[]
for mid in ['gold_beetle','wyvern']:
    cfg=json.loads((ROOT/mid/'input-audit.json').read_text());name=cfg['name'];out=BASE/f'docs/art/moba/{mid}_objective/repair-v1-2026-11-11'
    check=json.loads((out/'independent-export-audit.json').read_text());assert check['passed']
    report=json.loads((out/'repair-verification.json').read_text());final=Path(report['output'])
    src=Path(cfg['input']);saved=BASE/'art/model_catalog/sources'/src.name
    archive(src,saved,cfg['sha256'])
    views={}
    for view,ref in cfg['references'].items():
        original=Path(ref['path']);target=BASE/f'art/model_catalog/references/{mid}/{view}.png'
        archive(original,target,ref['sha256'])
        views[view]={'path':res(target),'source':str(original),'sha256':ref['sha256'],'bytes':target.stat().st_size,'project_matches':ref['project_matches'],'provenance_note':'Exact downloaded reference; creature identity and limb intent visually checked. No exact historical generation-job linkage verified.'}
    review={}
    for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]:
        p=sheet(out,name,view,key.upper());review[key]={'path':res(p),'kind':'Labeled rigged-download/local-repair comparison; true pre-remesh original unavailable'}
    sheet(out,name,'three-quarter','THREE-QUARTER')
    montage(out,sorted(out.glob('pose-*.png')),name+' / independent native joint tests','pose-proof.png')
    closeups=['patch-1','coin-stack-left','coin-stack-right','mandibles'] if mid=='gold_beetle' else ['underchest','wing-joint-left','wing-joint-right','head']
    montage(out,[out/f'{v}-{s}.png' for s in closeups for v in ['before','after']],name+' / matched local before and after','local-proof.png',cols=2,cell=380)
    span=max(cfg['bounds_first_primitive'][1][i]-cfg['bounds_first_primitive'][0][i] for i in [0,2]);scale=min(2.9/span,2.6/1.7)
    note='Six legs retained; local folds and coin-shell gap repaired. Original 23-joint rig and weights.' if mid=='gold_beetle' else 'Extra chest forelegs removed: two hind legs plus two wing arms. Original 46-joint rig retained.'
    entry={'id':mid,'name':name,'category':'objective','reference_only':False,
        'source_model':{'path':res(saved),'source':str(src),'sha256':cfg['sha256'],'bytes':saved.stat().st_size,'kind':'rigged_download','source_stage':'remeshed/rigged input; not an intact pre-remesh original'},
        'display_model':res(final),'status':note,'views':views,'artist_workspace':res(final.with_suffix('.blend')),
        'review_models':[{'label':'DOWNLOADED RIG\nBefore local repair','path':res(saved),'display_scale':scale},{'label':f'REPAIRED\nSame {cfg["joint_count"]}-joint skeleton','path':res(final),'display_scale':scale}],
        'review_views':review,'review_provenance':{'date':'2026-11-13','report':res(out/'repair-verification.json'),'independent_audit':res(out/'independent-export-audit.json'),'joint_count':cfg['joint_count'],'rigged_input_sha256':cfg['sha256'],'repaired_sha256':report['output_sha256'],'intact_pre_remesh_available':False,'scope':report['anatomy']+' Original hierarchy/rest/binds/materials retained. True pre-remesh source unavailable; two-version comparison only. Review asset, no authored-map or gameplay replacement.'}}
    (out/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n');entries.append(entry)
    for filename in ['repair_objectives.py','review_objective.py','audit_objectives.py','package_objectives.py']:
        shutil.copy2(ROOT/filename,out/filename)
    print(mid,'packaged',report['final_triangles'],'triangles',cfg['joint_count'],'joints')
im=Image.new('RGB',(1200,670),'#14212c');d=ImageDraw.Draw(im)
for i,entry in enumerate(entries):
    out=BASE/f'docs/art/moba/{entry["id"]}_objective/repair-v1-2026-11-11'
    pic=Image.open(out/'after-three-quarter.png').convert('RGB').resize((600,600))
    im.paste(pic,(600*i,50));d.text((600*i+16,12),entry['name']+' / repaired',font=font(26),fill='white')
im.save(ROOT/'both-repaired-preview.png')
if '--publish' in sys.argv:
    path=BASE/'art/model_catalog/catalog.json';cat=json.loads(path.read_text(encoding='utf-8'))
    # Preserve all existing entries, adding only the requested objectives.
    before=[e for e in cat['entries'] if e['id'] not in [x['id'] for x in entries]]
    cat['entries']=before+entries
    path.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Catalog published:',len(cat['entries']),'entries')
