from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from collections import Counter
import json

OUT=Path(__file__).resolve().parent
REF=OUT/'refs'
(OUT/'frames').mkdir(exist_ok=True)
HEX=['141218','211E27','3D3A44','7A4A06','58555E','FF3A2A','D18A0A','9D9BA2','FFCF1F','D6D6DC','FFE6D8','FFF4A8']
PAL=np.array([tuple(bytes.fromhex(h)) for h in HEX],dtype=np.uint8)
INK,BODY,DEEP,BROWN,SHADOW,RED,OCHRE,GREY,GOLD,WHITE,GLINT,CREAM=range(12)

def read(v,i): return np.array(Image.open(REF/f'{v}_f{i}.png').convert('RGBA'))
def ids(a):
    return np.argmin(((a[:,:,:3].astype(int)[:,:,None]-PAL.astype(int))**2).sum(3),axis=2)
def erode(m):
    p=np.pad(m,1)
    return m&p[:-2,1:-1]&p[2:,1:-1]&p[1:-1,:-2]&p[1:-1,2:]
def stroke(patch,pts,c,width=1):
    im=Image.fromarray(patch,'I'); ImageDraw.Draw(im).line(pts,fill=c,width=width);patch[:]=np.asarray(im)
def poly(patch,pts,c):
    im=Image.fromarray(patch,'I');ImageDraw.Draw(im).polygon(pts,fill=c);patch[:]=np.asarray(im)
def body_patch(v,a):
    q=np.full((192,192),-1,np.int32); c=ids(a)
    if v=='front':
        # Existing brow plates: deepen only their recessed folds.
        stroke(q,[(84,109),(85,107),(88,106),(92,106)],BROWN)
        stroke(q,[(101,106),(105,106),(108,108),(109,110)],BROWN)
        # Shoulder over upper arm, a short stepped overlap seam on the shadow side.
        stroke(q,[(73,111),(74,115),(76,118),(79,119)],INK)
        stroke(q,[(73,110),(73,114),(75,117)],OCHRE)
        stroke(q,[(115,111),(115,115),(113,118),(111,119)],INK)
        stroke(q,[(116,111),(116,115),(114,118)],BROWN)
        # Segmented shoulder cuffs, following the existing lower plate edge.
        stroke(q,[(62,133),(65,135),(72,135),(75,133)],BROWN)
        stroke(q,[(64,134),(67,136),(73,136)],INK)
        stroke(q,[(118,133),(120,135),(126,135),(130,133)],BROWN)
        stroke(q,[(118,136),(125,136),(129,134)],INK)
        # A lit edge on the existing central horn plane, and its shadow-side bevel.
        horn=np.zeros((192,192),bool);horn[105:136,90:104]=True
        horn &= np.isin(c,[SHADOW,GREY,WHITE])
        yy,xx=np.indices(c.shape)
        q[horn&(xx>=100)]=SHADOW
        q[horn&(xx==99)&(yy>=116)&(yy<=128)]=GREY
        q[horn&(xx>=94)&(xx<=95)&(yy>=116)&(yy<=127)]=WHITE
        q[horn&(xx==93)&(yy>=120)&(yy<=126)]=GREY
        stroke(q,[(101,116),(102,121),(103,127),(102,131),(100,134),(98,135),(94,135),(92,134),(91,132)],INK)
        # Compact almond sockets, preserving two red irises and their glints.
        for mirror in [False,True]:
            def pt(x,y):return (193-x if mirror else x,y)
            poly(q,[pt(x,y) for x,y in [(83,128),(85,128),(88,130),(88,132),(85,132),(83,130)]],INK)
            for x,y,col in [(85,129,GLINT),(85,130,RED),(86,130,RED),(86,131,RED)]:
                px,py=pt(x,y);q[py,px]=col
        # Side cheek overlap stops above the moving legs.
        stroke(q,[(84,134),(87,136),(90,137)],BROWN)
        stroke(q,[(109,134),(107,136),(104,137)],BROWN)
    elif v=='back':
        # Existing horizontal neck/upper-shell overlap, with lit lip above dark recess.
        stroke(q,[(82,105),(89,105),(99,105),(105,104),(111,104)],OCHRE)
        stroke(q,[(82,106),(89,106),(99,106),(105,105),(111,105)],INK)
        stroke(q,[(83,107),(91,107),(100,107),(106,106),(111,106)],BROWN)
        # Shell side bevels, light from upper left; no invented centre seam.
        stroke(q,[(76,113),(74,118),(74,124),(75,128),(79,130),(87,130)],BROWN)
        stroke(q,[(75,115),(73,120),(73,126),(74,129)],INK)
        stroke(q,[(118,113),(121,118),(121,124),(120,128),(118,130),(105,130)],BROWN)
        stroke(q,[(122,115),(123,121),(122,127),(120,130)],INK)
        stroke(q,[(76,113),(75,118),(75,122)],GOLD)
        # Small tail-root plate has the same shaded rim and inked attachment as SE.
        stroke(q,[(94,124),(92,125),(92,129),(94,132),(98,133),(100,131)],INK)
        stroke(q,[(95,125),(93,127),(93,129)],CREAM)
        stroke(q,[(99,127),(100,130),(98,132),(95,132)],BROWN)
        # The distant horn already exists: retain its shape and bevel its dark side.
        stroke(q,[(96,87),(97,91),(97,92)],DEEP)
    else:
        # NE already carries good modelling. Reinforce only existing overlaps.
        stroke(q,[(84,102),(93,102),(101,102),(106,104),(110,106)],INK)
        stroke(q,[(85,101),(94,101),(101,101)],OCHRE)
        stroke(q,[(108,108),(111,112),(114,114),(117,115)],INK)
        stroke(q,[(109,108),(112,111),(115,113)],BROWN)
        stroke(q,[(110,119),(111,124),(110,129),(108,132)],BROWN)
        stroke(q,[(111,120),(112,125),(111,130)],INK)
        # Horn collar and the recessed line behind the head plate, never an eye.
        stroke(q,[(124,103),(126,105),(130,105),(132,103)],INK)
        stroke(q,[(124,102),(127,104),(130,104)],DEEP)
        stroke(q,[(123,96),(123,100),(124,102)],GREY)
        stroke(q,[(130,94),(130,99),(129,102)],SHADOW)
        stroke(q,[(64,121),(66,119),(71,119),(74,121)],BROWN)
        stroke(q,[(73,123),(73,128),(71,131),(67,132)],INK)
    # Never touch a silhouette edge, or existing black exterior line.
    safe=erode(a[:,:,3]>0)
    q[~safe]=-1
    return q

def offset(a,b,box,radius=4):
    x0,y0,x1,y1=box
    mask=np.zeros((192,192),bool);mask[y0:y1,x0:x1]=True;mask &= a[:,:,3]>0
    # The upper body is static or translates by a texel; exclude the moving legs.
    scores=[]
    for dy in range(-radius,radius+1):
        for dx in range(-radius,radius+1):
            z=np.roll(b,(-dy,-dx),(0,1))
            score=np.sum(np.all(a==z,axis=2)&mask)
            scores.append((int(score),-abs(dx)-abs(dy),-abs(dy),dx,dy))
    best=max(scores);return best[-2:]

# Grey discs are shaded in their own moving local coordinates. Nothing below a
# joint is repainted: feet, ankle plates, leg silhouettes and motion are retained.
JOINTS={'front':[(69,142),(123,141)],'back':[(73,140),(121,135)],'ne':[(64,137),(95,132),(125,137)]}
def joint_patch(v,base,a):
    q=np.full((192,192),-1,np.int32);c=ids(a)
    for cx,cy in JOINTS[v]:
        dx,dy=offset(base,a,(cx-6,cy-6,cx+7,cy+7),12)
        x,y=cx+dx,cy+dy
        # Existing disc geometry supplies the contour. A bounded ellipse excludes
        # adjacent underbody and ankles even if their grey components touch.
        yy,xx=np.indices(c.shape)
        disc=(((xx-x)/6.0)**2+((yy-y)/6.0)**2<=1)&np.isin(c,[GREY,WHITE,SHADOW])
        # Do not paint very dark connecting struts.
        inside=erode(disc);ring=disc&~inside
        q[ring]=SHADOW
        q[ring&(xx+yy<x+y-2)]=WHITE
        q[ring&(xx+yy>x+y+2)]=DEEP
        q[inside]=GREY
        centre=inside&(((xx-x)/2.2)**2+((yy-y)/2.5)**2<=1)
        q[centre]=SHADOW
        q[centre&(xx<x)&(yy<y)]=GREY
    q[~erode(a[:,:,3]>0)]=-1
    return q

records=[];offsets={};outframes={}
for v in ['front','back','ne']:
    base=read(v,0);patch=body_patch(v,base);offsets[v]=[]
    for i in range(8):
        a=read(v,i);b=a.copy();dx,dy=offset(base,a,(50,83,140,130 if v=='front' else 122))
        offsets[v].append([dx,dy])
        p=np.roll(patch,(dy,dx),(0,1));safe=erode(a[:,:,3]>0)
        hit=(p>=0)&safe
        b[hit,:3]=PAL[p[hit]]
        jp=joint_patch(v,base,a);hit=(jp>=0)&safe;b[hit,:3]=PAL[jp[hit]]
        # Check the delivered artifact, not just the in-memory candidate.
        dest=OUT/'frames'/f'{v}_f{i}.png';Image.fromarray(b).save(dest)
        b=np.array(Image.open(dest).convert('RGBA'));outframes[v,i]=Image.fromarray(b)
        aa=a[:,:,3]>0;bb=b[:,:,3]>0
        iou=(aa&bb).sum()/(aa|bb).sum()
        unique=np.unique(b[bb,:3],axis=0)
        bottom=int(np.where(bb)[0].max());changed=int(np.any(a!=b,axis=2).sum())
        assert a.shape==b.shape==(192,192,4)
        assert np.array_equal(a[:,:,3],b[:,:,3])
        assert np.array_equal(a[150:],b[150:]),'Foot colour or geometry changed'
        assert all(tuple(x) in set(map(tuple,PAL)) for x in unique)
        assert set(np.unique(b[:,:,3])).issubset({0,255})
        edge=aa&~erode(aa);assert np.array_equal(a[edge],b[edge])
        interior=erode(bb)
        ink=float(np.mean(np.all(b[interior,:3]==PAL[INK],axis=1)))
        top5=sum(sorted(Counter(map(tuple,b[bb,:3])).values(),reverse=True)[:5])/bb.sum()
        records.append((v,i,iou,len(unique),bottom,changed,ink,top5))

# Full canvases, exactly 3x, every frame. Labels sit outside the image cells.
BG=(61,67,80);K=3;CELL=192*K;LABEL=110;HEAD=28
rows=[('SE reference','se',False),('Front before','front',False),('Front after','front',True),('Back before','back',False),('Back after','back',True),('NE before','ne',False),('NE after','ne',True)]
board=Image.new('RGB',(LABEL+8*CELL,HEAD+7*CELL),BG);dr=ImageDraw.Draw(board)
for i in range(8):dr.text((LABEL+i*CELL+12,8),f'Frame {i}',fill='white')
for j,(label,v,after) in enumerate(rows):
    dr.text((6,HEAD+j*CELL+20),label,fill='white')
    for i in range(8):
        im=outframes[v,i] if after else Image.fromarray(read(v,i))
        im=im.resize((CELL,CELL),Image.Resampling.NEAREST)
        board.paste(im,(LABEL+i*CELL,HEAD+j*CELL),im)
board.save(OUT/'board.png')
# GIF uses an explicit palette so the sprite colours are not quantized or dithered.
gif=[]
for i in range(8):
    im=Image.new('RGB',(4*384,410),BG);d=ImageDraw.Draw(im)
    for j,v in enumerate(['se','front','ne','back']):
        spr=Image.fromarray(read(v,i)) if v=='se' else outframes[v,i]
        spr=spr.resize((384,384),Image.Resampling.NEAREST)
        im.paste(spr,(j*384,26),spr);d.text((j*384+12,8),v.upper(),fill='white')
    pal=Image.new('P',(1,1));cols=[*BG,*[int(t) for t in PAL.flatten()],255,255,255];pal.putpalette(cols+[0]*(768-len(cols)))
    gif.append(im.quantize(palette=pal,dither=Image.Dither.NONE))
# GIF centisecond timing cannot represent 125ms. Alternating 120/130 is exactly 8fps average.
gif[0].save(OUT/'preview.gif',save_all=True,append_images=gif[1:],duration=[120,130]*4,loop=0,disposal=2,optimize=False)
lines=['RHINO_L TAKE A: ONE DETAIL-CONSISTENCY PASS','',
'Edited supplied frames only. No image generation, installs, commits or asset integration.',
'All writes confined to this codex-consistency folder. References opened only from refs/.',
'Canvas 192x192, 8 frames per view, same order. Body edits made once in f0 coordinates,',
'carried by measured upper-body translation. Disc shading follows each moving joint locally.',
'No alpha, silhouette edge, outline, ankle/foot rows 150..191 or leg geometry changed.',
'Every per-frame alpha IoU is 1.000000. The exterior outline is byte-identical.',
'Feet/material and outline bottom remain at their exact input rows.',
'INPUT BASELINE DISCREPANCY: supplied opaque bottom rows range from 160 to 165,',
'not uniformly 161 as described in the brief. Each output keeps its input bottom row.',
'', 'Palette: '+', '.join('#'+h for h in HEX),
'Craft targets used: <=16 colours (job limit 12); broad clusters, upper-left light,',
'four armour tones where space permits; top-five share target >=0.65, no added texture.',
'3D/evolution/lore/full eight-direction judgement does not apply to this constrained walk edit.',
'', 'frame        alpha_IoU colours bottom_y changed_pixels interior_ink top5_share']
for v,i,iou,n,bot,ch,ink,t5 in records:
    lines.append(f'{v}_f{i:<1}     {iou:.6f}  {n:2}      {bot:3}      {ch:4}          {ink:.4f}       {t5:.4f}')
lines+=['','Body translations from f0 (dx,dy), frames 0..7:',json.dumps(offsets,indent=2),'',
'Changes: front has compact dark eye sockets with red irises/glints, a brighter horn',
'plane, dark horn attachment, shoulder/arm overlaps and cuff bevels. Back has a dark',
'upper-shell overlap, side bevels and tail-root attachment. NE receives restrained',
'plate-overlap and horn-collar definition. Grey joint discs receive a light upper-left',
'rim, dark lower-right rim and recessed centre, keeping the existing joint contour.',
'', 'Limitations / not fixed:',
'Underlying PixelLab body shapes and per-frame non-rigid variations remain. A single',
'body translation cannot eliminate those variations; no pose or plate shape was redrawn.',
'Front/back still have simpler armour geometry than SE. This pass adds volume to the',
'existing shapes; it does not invent SE-specific plates on unseen surfaces.',
'No eyes added to NE or back. No anatomy, gait, camera angle or silhouette corrections.',
'One pass only; no alternate generated takes.',
'', 'Artifacts: board.png = SE, front before/after, back before/after, NE before/after;',
'all 8 frames in columns at exactly 3x on #3D4350.',
'preview.gif = SE/front/NE/back, 2x nearest, 8fps average (alternating 120/130ms).',
'GIF palette is exact, without dithering.']
(OUT/'REPORT.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'metrics.json').write_text(json.dumps({'offsets':offsets,'records':records},indent=2),encoding='utf-8')
print('\n'.join(lines[0:15]));print('Changed pixels range:',min(r[5] for r in records),max(r[5] for r in records))
# Compact review of this job's output for visual inspection.
small=Image.new('RGB',(6*384,410),BG);d=ImageDraw.Draw(small)
for j,(v,after) in enumerate([('front',False),('front',True),('back',False),('back',True),('ne',False),('ne',True)]):
    im=outframes[v,0] if after else Image.fromarray(read(v,0))
    im=im.crop((48,80,144,164)).resize((384,336),Image.Resampling.NEAREST)
    small.paste(im,(j*384,50),im);d.text((j*384+12,12),v+(' after' if after else ' before'),fill='white')
small.save(OUT/'review.png')
