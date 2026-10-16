"""Package review projections and reproduce rectangular opening masks without installs."""
from pathlib import Path
import json, hashlib, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'art/rooms/hangar_bay/evidence'
SKILL=Path('C:/Users/pmcga/.codex/plugins/cache/openai-curated-remote/build-3d-game-rooms/0.3.3/skills/build-3d-game-rooms')
def write(name,value):
    (P/name).write_text(json.dumps(value,indent=2)+'\n')
def read(name):return json.loads((P/name).read_text())
try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
except OSError:font=ImageFont.load_default()

# Make monochrome outline projections from actual rendered meshes, not category boxes.
for path in (P/'plans').glob('*.png'):
    im=Image.open(path).convert('RGBA')
    original=path.with_name(path.stem+'-projection-source.png')
    im.save(original)
    arr=np.asarray(im).astype(np.int16)
    rgb=arr[:,:,:3];alpha=arr[:,:,3:4]/255
    gray=(rgb.mean(axis=2)*alpha[:,:,0]+255*(1-alpha[:,:,0])).astype(np.int16)
    local_min=gray.copy();local_max=gray.copy()
    for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,-1)]:
        shifted=np.roll(gray,(dy,dx),(0,1))
        local_min=np.minimum(local_min,shifted);local_max=np.maximum(local_max,shifted)
    lines=(local_max-local_min)>7
    clean=np.full_like(gray,255,dtype=np.uint8);clean[lines]=20
    Image.fromarray(clean).save(path)

# Reference contact sheet. Titles are outside each isolated image.
assets=read('props.json')['assets']
sheet=Image.new('RGB',(1600,850),'#eef0f2')
draw=ImageDraw.Draw(sheet)
for i,a in enumerate(assets):
    x,y=(i%4)*400,(i//4)*425
    draw.text((x+14,y+12),a['id'],fill='#1b2025',font=font)
    draw.text((x+14,y+42),' x '.join(map(str,a['dimensionsMeters']))+' m',fill='#454a50',font=font)
    im=Image.open(P/a['image']['source']).convert('RGBA');im.thumbnail((390,340))
    sheet.paste(im,(x+(400-im.width)//2,y+75),im)
sheet.save(P/'images/prop-contact-sheet.png')

tracer_status=[]
for a in read('openings.json')['openings']:
    door=a['kind']=='door'
    # Physical mask canvas includes retained wall margins; white aperture matches schedule.
    ext_w=a['widthMeters']+.4
    ext_h=a['heightMeters']+(.3 if door else .4)
    w,h=round(ext_w*100),round(ext_h*100)
    mask=Image.new('L',(w,h),0)
    x0,x1=20,w-21
    y0=30 if door else 20
    y1=h-1 if door else h-21
    ImageDraw.Draw(mask).rectangle((x0,y0,x1,y1),fill=255)
    mask.save(P/a['mask'])
    cmd=[sys.executable,str(SKILL/'scripts/trace_opening_mask.py'),str(P/a['mask']),'--id',a['id'],'--kind',a['kind'],'--width-m',str(ext_w),'--height-m',str(ext_h),'--out',str(P/a['cutter']),'--preview',str(P/'masks'/f'{a["id"]}-trace.png')]
    if not door:cmd+=['--sill-m',str(a['sillMeters'])]
    result=subprocess.run(cmd,capture_output=True,text=True)
    tracer_status.append({'opening':a['id'],'tool':'trace_opening_mask.py','exitCode':result.returncode,'diagnostic':result.stderr.strip()})
    if result.returncode:
        # No OpenCV is installed. Rectangles have one exact connected component;
        # derive its pixel boundary reproducibly with Pillow/NumPy instead of a download.
        arr=np.asarray(mask)
        ys,xs=np.nonzero(arr==255)
        assert len(xs)==(x1-x0+1)*(y1-y0+1)
        assert np.all((arr==0)|(arr==255))
        points=[[x0/w,1-(y1+1)/h],[(x1+1)/w,1-(y1+1)/h],[(x1+1)/w,1-y0/h],[x0/w,1-y0/h]]
        payload={'schema':'game-room.opening-cutter.v1','id':a['id'],'kind':a['kind'],'widthMeters':ext_w,'heightMeters':ext_h,'sillMeters':a.get('sillMeters',0),'depthMeters':.3,'source':Path(a['mask']).name,'sourceSha256':hashlib.sha256((P/a['mask']).read_bytes()).hexdigest(),'imageSize':[w,h],'whitePixelRatio':float((arr==255).mean()),'contours':[{'role':'outer','points':points}],'traceMethod':'Exact rectangular white-component boundary, Pillow/NumPy fallback; official tracer attempted but cv2 missing','apertureMeters':[a['widthMeters'],a['heightMeters']]}
        write(a['cutter'],payload)
write('opening-tracer-status.json',tracer_status)
opening_sheet=Image.new('RGB',(1200,650),'white');d=ImageDraw.Draw(opening_sheet)
for i,a in enumerate(read('openings.json')['openings']):
    x=i*400
    d.text((x+12,14),a['id']+' ('+a['kind']+')',fill='black',font=font)
    d.text((x+12,45),f'{a["widthMeters"]} x {a["heightMeters"]} m',fill='black',font=font)
    d.text((x+12,76),f'{a["wall"]} wall; sill {a.get("sillMeters",0)} m',fill='black',font=font)
    im=Image.open(P/a['mask']).convert('RGB');im.thumbnail((360,440))
    opening_sheet.paste(im,(x+(400-im.width)//2,120))
    d.text((x+12,590),'Black: retained wall',fill='black',font=font)
    d.text((x+12,620),'White: clear aperture',fill='black',font=font)
opening_sheet.save(P/'masks/opening-contact-sheet.png')

# Run the plugin's validator unchanged and preserve its honest pending result.
result=subprocess.run([sys.executable,str(SKILL/'scripts/validate_room.py'),str(P),'--gate','function'],capture_output=True,text=True)
(P/'function-gate-validation.txt').write_text(result.stdout+result.stderr)
prep=[]
for a in assets:
    assert (P/a['image']['source']).is_file()
    assert a['productionMethod']=='Blender procedural; no Meshy'
    prep.append(a['id']+': reference and dimensions recorded')
for a in read('openings.json')['openings']:
    c=read(a['cutter'])
    assert c['sourceSha256']==hashlib.sha256((P/a['mask']).read_bytes()).hexdigest()
    assert c['apertureMeters']==[a['widthMeters'],a['heightMeters']]
    prep.append(a['id']+': mask and contour aperture verified')
stats=read('function-measurements.json')
assert stats['prototypeTriangles']+stats['heroTriangleReserve']<stats['roomBudgetTriangles']
prep.append('Prototype geometry plus 11000-triangle hero reserve is below 40000')
write('function-preflight.json',{'status':'Prepared for human review; Function NOT approved','checks':prep,'paidCreditsUsed':0,'pluginGatePassed':False,'validatorPolicyMismatch':'Bundled validator requires Meshy for every prop and a positive paid budget. CODEX_TASKS_3D_ROOMS.md explicitly prefers free procedural props; no paid budget or approval fabricated.','maskDependencyFallback':'Bundled tracer attempted for all three masks; cv2 absent. Exact rectangle boundary fallback verified without installations.'})
print('FUNCTION_PREFLIGHT_READY: 8 prop families, 3 exact aperture masks, budget checked; explicit approval pending')
