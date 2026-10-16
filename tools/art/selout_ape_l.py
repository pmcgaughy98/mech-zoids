"""Native-pixel, material-preserving finish for the approved v31 gorilla views.

Hand-selected per-facing regions live in REGIONS; alpha/footprint never changes.
This finishes rendered pixels, never generates or re-renders a new silhouette.
"""
from pathlib import Path
import json,sys,hashlib
from collections import Counter,deque
import numpy as np
from PIL import Image,ImageDraw
from sprite_quality import measure

ROOT=Path(__file__).resolve().parents[2]
SLOTS=ROOT/'art/machines/ape_l/views'
OUT=ROOT/'docs/art/2d/ape_l/selout-2026-10-12'
BEFORE=OUT/'before'
DIRS=['e','ne','n','nw','w','sw','s','se']
RAMPS={
 'green':'1f2a1b 303e29 3b5a31 4c713c 598644 6c9b4a 79ac54 8eb960 9fc96f b3d686'.split(),
 'grey':'181f1c 1c2129 272d38 2a2c31 3f3e43 4c4b52 5a585f 69686f 828188 9a9aa2 b4b5bb c9cbd2'.split(),
 'orange':'4a2f17 704c2b 8c5626 aa692c d4853b eba655 f6c27c'.split(),
 'teal':'1f6e66 5fe1d0 bff7ef'.split(),
 'shadow':'2c2838 403a52'.split()}
COLORS={key:np.array([tuple(int(h[i:i+2],16) for i in (0,2,4)) for h in ramp],np.uint8) for key,ramp in RAMPS.items()}
LOOKUP={tuple(rgb):(family,i) for family,ramp in COLORS.items() for i,rgb in enumerate(ramp)}

# Rectangles are selected by inspecting each native facing at 6x with a coordinate grid.
# RGB-family masks constrain them to their actual plate/fist pixels, never the silhouette.
PLATES={
 'e':[(51,39,70,56),(55,59,76,73),(76,40,95,58),(81,29,102,41),(99,30,127,56),(118,52,144,79),(129,14,153,42)],
 'ne':[(59,40,81,67),(58,73,75,85),(83,36,105,58),(87,60,115,90),(96,24,127,45),(132,21,157,46),(137,43,175,74)],
 'n':[(73,20,99,61),(101,23,137,57),(143,19,165,60),(85,60,112,89),(127,61,151,91),(104,4,134,22)],
 'nw':[(31,18,60,41),(96,35,131,62),(19,43,51,74),(76,22,116,43),(71,47,102,91),(117,45,141,83)],
 'w':[(97,28,122,56),(74,8,98,31),(88,51,111,83),(126,22,156,48),(150,57,178,89),(81,28,93,56)],
 'sw':[(40,12,72,37),(80,27,106,53),(79,50,108,81),(20,43,52,67),(103,28,123,56),(113,47,142,87)],
 's':[(39,17,77,36),(13,22,40,43),(80,22,105,48),(13,42,41,60),(3,58,30,73),(80,51,110,80),(28,60,45,77),(70,59,89,78)],
 'se':[(112,21,141,40),(80,28,105,55),(50,44,73,77),(76,52,109,79),(131,56,161,79),(139,41,151,61)]}
FISTS={
 'e':[(132,77,154,93,[138,143,148]),(123,75,138,86,[128,133])],
 'ne':[(152,71,178,83,[158,164,170]),(112,63,121,74,[116])],
 'n':[(63,70,89,83,[69,76,83]),(153,65,174,75,[158,164,170])],
 'nw':[(18,71,47,87,[25,32,39]),(66,56,78,72,[71])],
 'w':[(88,81,104,96,[93,98]),(73,58,90,78,[78,84])],
 'sw':[(81,80,112,95,[89,97,105]),(20,61,42,81,[26,33,39])],
 's':[(3,71,31,91,[9,16,23]),(85,82,114,96,[91,98,105])],
 'se':[(82,78,113,95,[89,97,105]),(131,76,161,93,[138,146,154])]}
JOINTS={
 'e':[(114,46,8),(135,31,4),(64,79,4)],
 'ne':[(148,37,7),(74,55,3),(100,76,4)],
 'n':[(92,57,3),(138,57,3)],
 'nw':[(43,32,7),(82,75,4),(121,81,3)],
 'w':[(112,40,8),(88,24,4),(161,79,4)],
 'sw':[(106,36,7),(132,68,4),(46,37,3)],
 's':[],
 'se':[(90,42,7),(44,72,4),(112,34,3)]}

def encode(a):
    family=np.full(a.shape[:2],'',object);index=np.full(a.shape[:2],-1,int)
    for y,x in zip(*np.where(a[:,:,3]>0)):
        rgb=tuple(a[y,x,:3]);value=LOOKUP.get(rgb)
        if value is None:raise ValueError(f'Input off approved palette: {rgb}')
        family[y,x],index[y,x]=value
    return family,index

def finish(direction):
    original=np.array(Image.open(BEFORE/(direction+'.png')).convert('RGBA'))
    a=original.copy();family,index=encode(original);solid=original[:,:,3]>0
    H,W=solid.shape;edited=index.copy();notes={}
    select=np.zeros_like(solid)
    for x0,y0,x1,y1 in PLATES[direction]:select[y0:y1+1,x0:x1+1]=True
    # Median only within the same green material and on the same side of real dark seams.
    # Two restrained passes remove fine texture crosshatching but retain macro light/shade.
    smooth=edited.copy()
    for repeat in range(2):
        next_pass=smooth.copy()
        for y,x in zip(*np.where(select & (family=='green') & (index>0))):
            values=[]
            for yy in range(max(0,y-2),min(H,y+3)):
                for xx in range(max(0,x-2),min(W,x+3)):
                    if family[yy,xx]=='green' and index[yy,xx]>0:
                        values.append(smooth[yy,xx])
            if len(values)>=12:
                med=int(np.median(values))
                # Only low-contrast texture; strong form changes and intentional highlights stay.
                if abs(med-smooth[y,x])<=2:next_pass[y,x]=med
        smooth=next_pass
    edited[select & (family=='green')]=smooth[select & (family=='green')]
    notes['plateGridPixelsChanged']=int(((edited!=index)&select&(family=='green')).sum())

    # Repaint selected orange fist faces into broad planes and deliberate finger dividers.
    fist_changed=0
    for x0,y0,x1,y1,dividers in FISTS[direction]:
        mask=(family[y0:y1+1,x0:x1+1]=='orange')
        if not mask.any():continue
        ys,xs=np.where(mask);top=y0+int(ys.min());bottom=y0+int(ys.max())
        for local_y,local_x in zip(ys,xs):
            y,x=y0+local_y,x0+local_x
            t=(y-top)/max(1,bottom-top)
            if t<.18:shade=5
            elif t<.58:shade=4
            elif t<.82:shade=3
            else:shade=1
            if x>x0+(x1-x0)*.78 and t>=.18:shade=max(1,shade-1)
            if x in dividers and t>.5:shade=0 if t>.8 else 1
            # A single upper knuckle ridge, constrained to already orange pixels.
            if y==top+2 and x<x0+(x1-x0)*.70:shade=6
            # Raised front knuckle row and curled fingertip row, not a featureless box.
            knuckle_y=top+max(3,int((bottom-top)*.54))
            if y==knuckle_y and x not in dividers:shade=5
            if y==knuckle_y+1 and x not in dividers:shade=4
            if t>.83 and x not in dividers:shade=2
            if edited[y,x]!=shade:fist_changed+=1
            edited[y,x]=shade
    notes['fistPixelsChanged']=fist_changed

    # Material-aware sel-out of the silhouette. Use the nearest lit interior for dark edge pixels.
    edge_count=0;edge_edits=0
    body_ys=np.where(solid&(family!='shadow'))[0]
    body_bottom=int(body_ys.max())
    boundary=np.zeros_like(solid)
    def filled(y,x):return 0<=y<H and 0<=x<W and solid[y,x]
    for y,x in zip(*np.where(solid & (family!='shadow') & (family!='teal'))):
        empty=[not filled(y-1,x),not filled(y+1,x),not filled(y,x-1),not filled(y,x+1)]
        if not any(empty):continue
        boundary[y,x]=True;edge_count+=1
        f=family[y,x];rank=edited[y,x]
        candidates=[]
        for radius in range(1,5):
            for yy in range(max(0,y-radius),min(H,y+radius+1)):
                for xx in range(max(0,x-radius),min(W,x+radius+1)):
                    ff=family[yy,xx]
                    if ff not in ['green','grey','orange'] or not solid[yy,xx]:continue
                    ii=edited[yy,xx]
                    if (ff=='grey' and ii<3) or (ff=='green' and ii<1):continue
                    if f!='grey' and ff!=f:continue
                    distance=abs(xx-x)+abs(yy-y)
                    if distance and not any(not filled(yy+dy,xx+dx) for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]):
                        candidates.append((distance,ff,ii))
            if candidates:break
        if not candidates:continue
        candidates.sort(key=lambda c:c[0]);closest=candidates[0][0]
        near=[c for c in candidates if c[0]<=closest+1]
        # Near-black grey outlines can belong to green armor; infer only those, not actual steel.
        if f=='grey' and rank<3:
            chosen=Counter(c[1] for c in near).most_common(1)[0][0]
            f=chosen
        ranks=[c[2] for c in near if c[1]==f]
        if not ranks:continue
        ref=int(np.median(ranks));current_rgb=COLORS[family[y,x]][rank]
        dark=int(current_rgb.astype(int).sum())<120
        if empty[0]:
            # Existing bright top rims remain; lift only a dark edge into its own material.
            target=min(len(COLORS[f])-1,ref+1) if dark else rank
        elif empty[1]:
            if dark and not empty[0]:target=0 if f!='grey' else 1
            elif y>=body_bottom-4:target=0 if f!='grey' else 1
            else:target=max(1 if f!='grey' else 3,ref-3)
        elif empty[2]:target=max(1 if f!='grey' else 3,ref-2)
        else:target=max(1 if f!='grey' else 3,ref-3)
        if f==family[y,x] and empty[0] and not dark:target=rank
        if f!=family[y,x] or target!=rank:edge_edits+=1
        family[y,x]=f;edited[y,x]=target
    notes['materialEdgePixelsChanged']=edge_edits

    # Joint discs are individual per-facing edits. The hubs and real seams stay intentionally dark.
    joint_edits=0
    for cx,cy,radius in JOINTS[direction]:
        for y in range(max(0,cy-radius),min(H,cy+radius+1)):
            for x in range(max(0,cx-radius),min(W,cx+radius+1)):
                rr=((x-cx)**2+(y-cy)**2)**.5/radius
                if rr>1 or family[y,x]!='grey' or boundary[y,x]:continue
                if rr<.30:shade=3
                elif rr>.82:shade=0
                else:shade=7 if x+y<cx+cy-1 else (5 if x+y<cx+cy+3 else 4)
                if x==cx-1 and y==cy-1:shade=10
                if edited[y,x]!=shade:joint_edits+=1
                edited[y,x]=shade
    notes['jointPixelsChanged']=joint_edits

    # Remove isolated low-contrast shading specks, never eyes, seams, or deliberate pale highlights.
    cleaned=edited.copy();stray_fixes=0
    for y,x in zip(*np.where(solid & ~boundary)):
        f=family[y,x];i=edited[y,x]
        if f in ['teal','shadow'] or i==0 or i>=len(COLORS[f])-2:continue
        nb=[edited[yy,xx] for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if 0<=yy<H and 0<=xx<W and family[yy,xx]==f]
        if len(nb)>=3 and i not in nb:
            target,count=Counter(nb).most_common(1)[0]
            if count>=3 and abs(target-i)<=2:cleaned[y,x]=target;stray_fixes+=1
    edited=cleaned;notes['isolatedShadePixelsFixed']=stray_fixes
    # Three-step eye ramp stays in exactly the existing teal locations.
    visited=set();eye_edits=0
    for y,x in zip(*np.where(family=='teal')):
        if (y,x) in visited:continue
        q=deque([(y,x)]);component=[];visited.add((y,x))
        while q:
            yy,xx=q.popleft();component.append((yy,xx))
            for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
                p=(yy+dy,xx+dx)
                if 0<=p[0]<H and 0<=p[1]<W and family[p]=='teal' and p not in visited:
                    visited.add(p);q.append(p)
        component.sort(key=lambda p:(p[0],p[1]))
        for k,p in enumerate(component):
            shade=2 if k==0 and len(component)>1 else (0 if k==len(component)-1 and len(component)>2 else 1)
            if edited[p]!=shade:eye_edits+=1
            edited[p]=shade
    notes['eyeRampPixelsChanged']=eye_edits
    for y,x in zip(*np.where(solid)):a[y,x,:3]=COLORS[family[y,x]][edited[y,x]]
    assert a.shape==original.shape and np.array_equal(a[:,:,3],original[:,:,3])
    assert np.array_equal(a[~solid],original[~solid])
    Image.fromarray(a).save(OUT/(direction+'.png'))
    notes['totalRGBPixelsChanged']=int(np.any(a[:,:,:3]!=original[:,:,:3],axis=2).sum())
    notes['alphaPixelsChanged']=0
    return notes

def deliver_sheets(notes):
    S=4;W,H=Image.open(BEFORE/'e.png').size
    bg='#dce0e3';combined=Image.new('RGB',(W*S*2+36,(H*S+46)*8),bg)
    draw=ImageDraw.Draw(combined)
    metrics=[]
    for i,direction in enumerate(DIRS):
        b=Image.open(BEFORE/(direction+'.png')).convert('RGBA')
        a=Image.open(OUT/(direction+'.png')).convert('RGBA')
        y=i*(H*S+46)
        draw.text((12,y+10),direction+' BEFORE',fill='black')
        draw.text((W*S+30,y+10),direction+' AFTER',fill='black')
        pair=Image.new('RGB',(W*S*2+36,H*S+46),bg);pd=ImageDraw.Draw(pair)
        pd.text((12,10),direction+' BEFORE',fill='black');pd.text((W*S+30,10),direction+' AFTER',fill='black')
        for im,x in [(b,12),(a,W*S+24)]:
            enlarged=im.resize((W*S,H*S),Image.Resampling.NEAREST)
            pair.paste(enlarged,(x,30),enlarged)
        pair.save(OUT/(direction+'-before-after-4x.png'))
        combined.paste(pair,(0,y))
        metrics.append({'view':direction,'before':measure(BEFORE/(direction+'.png')),'after':measure(OUT/(direction+'.png')),'changes':notes[direction]})
    combined.save(OUT/'before-after-all-4x.png')
    contact=Image.new('RGB',(W*S*4,H*S*2+48),bg);cd=ImageDraw.Draw(contact)
    for i,d in enumerate(DIRS):
        im=Image.open(OUT/(d+'.png')).convert('RGBA').resize((W*S,H*S),Image.Resampling.NEAREST)
        x=(i%4)*W*S;y=(i//4)*(H*S+24)
        cd.text((x+8,y+5),d,fill='black');contact.paste(im,(x,y+24),im)
    contact.save(OUT/'after-contact-4x.png')
    (OUT/'map.json').write_text(json.dumps({d:d+'.png' for d in DIRS},indent=2))
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2))
    (OUT/'manifest.json').write_text(json.dumps({'task':'CODEX_SELOUT_APE_L_2026-10-12.md','method':'Native color-only edits, per-view selected plate/fist/joint regions; original alpha untouched','size':[W,H],'anchor':[95,97],'paletteRamps':RAMPS,'beforeSources':{d:{'path':str(BEFORE/(d+'.png')),'sha256':hashlib.sha256((BEFORE/(d+'.png')).read_bytes()).hexdigest()} for d in DIRS},'changes':notes},indent=2))

def backup():
    BEFORE.mkdir(parents=True,exist_ok=True)
    for direction in DIRS:
        destination=BEFORE/(direction+'.png')
        if not destination.exists():destination.write_bytes((SLOTS/(direction+'.png')).read_bytes())
    meta=BEFORE/'views.json'
    if not meta.exists():meta.write_bytes((SLOTS/'views.json').read_bytes())

def grid_previews():
    for direction in DIRS:
        im=Image.open(BEFORE/(direction+'.png')).convert('RGBA')
        view=Image.new('RGB',(im.width*6,im.height*6),'#dadde1')
        view.paste(im.resize(view.size,Image.Resampling.NEAREST),(0,0),im.resize(view.size,Image.Resampling.NEAREST))
        d=ImageDraw.Draw(view)
        for x in range(0,im.width,10):
            d.line((x*6,0,x*6,view.height),fill='#7a829088',width=1)
            d.text((x*6+2,2),str(x),fill='red')
        for y in range(0,im.height,10):
            d.line((0,y*6,view.width,y*6),fill='#7a8290',width=1)
            d.text((2,y*6+2),str(y),fill='red')
        view.save(OUT/(direction+'-coordinate-study.png'))

if __name__=='__main__':
    backup()
    if '--grid' in sys.argv:grid_previews()
    else:
        notes={d:finish(d) for d in DIRS}
        deliver_sheets(notes)
        print('Eight native views finished on copies; alpha identical in all eight.')
        for record in json.loads((OUT/'metrics.json').read_text()):
            print(record['view'],{k:round(v,3) for k,v in record['after'].items()})
