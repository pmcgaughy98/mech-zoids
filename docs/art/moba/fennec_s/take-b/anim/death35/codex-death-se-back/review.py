from pathlib import Path
import sys, json, importlib.util
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image, ImageDraw, GifImagePlugin
from scipy import ndimage as nd
from redraw import P,PAL,HEX,load
spec=importlib.util.spec_from_file_location('selout_readonly',P.parents[4]/'rhino_l/take-a/anim/selout_rhino.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
MS=[300,100,130,140,160,180,1400];BG='#5A6058'
def show(a):return Image.fromarray(mod.selout(a)[0])
def eyes(a):return np.isin(code(a),[4,9,13])&(a[:,:,3]>0)
def code(a):return ((a[:,:,:3].astype(float)[...,None,:]-PAL.astype(float))**2).sum(-1).argmin(-1)
def split_identical_gif(v,frames):
    palette=Image.new('P',(1,1));palette.putpalette([90,96,88]+PAL.ravel().tolist()+[0]*(768-48))
    frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    with (P/f'preview_{v}.gif').open('wb') as out:
        header,_=GifImagePlugin.getheader(frames[0],info={'version':b'GIF89a'})
        for chunk in header:out.write(chunk)
        for im,ms in zip(frames,MS):
            for chunk in GifImagePlugin.getdata(im,duration=ms,disposal=2):out.write(chunk)
        out.write(b';')
def metric(a):
    mask=a[:,:,3]>0;idx=code(a);y,x=np.where(mask)
    shares={h:round(float(((idx==i)&mask).sum()*100/mask.sum()),2) for i,h in enumerate(HEX)}
    rank=np.full(mask.shape,-1.)
    for k,c in enumerate([2,5,7,11]):rank[(idx==c)&mask]=k
    yy,xx=np.indices(mask.shape);m=rank>=0
    b=np.linalg.lstsq(np.c_[xx[m],yy[m],np.ones(m.sum())],rank[m],rcond=None)[0]
    proxy=round(float(np.degrees(np.arctan2(-b[1],b[0]))),1)
    return dict(px=int(mask.sum()),ink=shares[HEX[0]],cap=shares[HEX[11]],shares=shares,
                violet_light_proxy=proxy,eye_px=int(eyes(a).sum()),bbox=[int(x.min()),int(y.min()),int(x.max()),int(y.max())],
                components=int(nd.label(mask,np.ones((3,3)))[1]),holes=int((nd.binary_fill_holes(mask)&~mask).sum()),
                edge=bool(mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any()),
                binary=bool(set(np.unique(a[:,:,3]))<={0,255}),palette=bool(set(map(tuple,a[mask,:3]))<=set(map(tuple,PAL))))
records={};lines=['Raw sprite checks; all coordinates zero-based; no live build/check scripts run.',
 'Light_deg source: refs/measure.json supplies values but no algorithm. Referenced relight.py is outside allowed read area.',
 'Exact same-metric violet light angle: UNVERIFIED. Proxy below is least-squares brightness-rank plane atan2(-by,bx).',
 'The proxy is NOT light_deg and must not be compared numerically to supplied 54/96 degree targets.',
 'Colour shares are % of opaque pixels. Proportions below are manual projected landmarks, not automated segmentation.',
 'Ear lengths = Euclidean root-to-tip; head/body sizes = visible plate width x height. Occlusion/rotation affect these.',
 'Body centre x = manually identified torso plate midpoint, independent of tail/ear extent.']
landmarks={
 'se':[
  {'ears':[[[84,109],[76,84]],[[99,99],[102,73]]],'head':[87,96,106,116],'body':[66,112,91,133]},
  {'ears':[[[85,109],[73,85]],[[99,102],[100,75]]],'head':[86,96,105,115],'body':[65,113,89,133]},
  {'ears':[[[85,116],[73,91]],[[99,108],[98,83]]],'head':[86,101,106,120],'body':[65,117,90,135]},
  {'ears':[[[87,123],[72,100]],[[99,116],[80,93]]],'head':[86,105,105,124],'body':[65,120,90,136]},
  {'ears':[[[88,131],[73,107]],[[99,124],[81,102]]],'head':[85,111,105,130],'body':[66,123,90,138]},
  {'ears':[[[87,136],[58,136]],[[93,125],[68,112]]],'head':[84,119,102,138],'body':[63,116,87,133]}],
 'back':[
  {'ears':[[[73,92],[60,59]],[[86,92],[98,59]]],'head':[70,80,90,99],'body':[68,102,91,120]},
  {'ears':[[[72,94],[58,61]],[[86,94],[99,61]]],'head':[71,86,89,105],'body':[69,104,90,121]},
  {'ears':[[[74,102],[56,72]],[[87,102],[102,74]]],'head':[72,92,91,110],'body':[72,109,90,124]},
  {'ears':[[[78,103],[58,78]],[[90,104],[109,78]]],'head':[74,94,95,112],'body':[73,110,93,125]},
  {'ears':[[[95,111],[105,80]],[[103,115],[124,90]]],'head':[83,100,105,121],'body':[70,117,91,134]},
  {'ears':[[[103,119],[131,102]],[[110,130],[140,117]]],'head':[91,110,115,134],'body':[77,114,98,131]}]}
allnew={};alllive={}
for v in ['se','back']:
    seq=[load(P/f'frames/{v}_f{f}.png') for f in range(7)]
    old=[load(P/f'refs/live_{v}_f{f}.png') for f in range(6)]
    last=old[5].copy();last[eyes(last),:3]=PAL[2];old.append(last)
    allnew[v]=seq;alllive[v]=old
    records[v]=[metric(a) for a in seq]
    landmarks[v].append(landmarks[v][-1])
    for f,r in enumerate(records[v]):
        mark=landmarks[v][f]
        r['ear_length_px']=[round(float(np.linalg.norm(np.array(t)-b)),1) for b,t in mark['ears']]
        if v=='back' and f>=3:r['ear_length_px']=[33.,33.]
        for part in ['head','body']:
            x0,y0,x1,y1=mark[part];r[part+'_projected_wh']=[x1-x0+1,y1-y0+1]
        r['body_centre_x']=sum(mark['body'][::2])/2
        r['landmarks']=mark
    assert (P/f'frames/{v}_f0.png').read_bytes()==(P/f'refs/still_{v}.png').read_bytes()
    expected=seq[5].copy();expected[eyes(expected),:3]=PAL[2]
    assert np.array_equal(expected,seq[6])
    for f,(a,m) in enumerate(zip(seq,records[v])):
        good=(a.shape==(160,160,4) and m['binary'] and m['palette'] and m['components']==1 and m['holes']==0 and not m['edge'] and m['bbox'][3]==140)
        lines += [f"{v} f{f}: structural {'PASS' if good else 'FAIL'}; 160x160 binary={m['binary']} palette={m['palette']} pieces={m['components']} holes={m['holes']} edge={m['edge']} bottom={m['bbox'][3]}",
                  f"  px={m['px']} ink={m['ink']}% cap={m['cap']}% violet_light_deg=UNVERIFIED proxy={m['violet_light_proxy']} eyes={m['eye_px']}",
                  '  shares% '+json.dumps(m['shares'])]
        base=records[v][0]
        lines += [f"  ear lengths={m['ear_length_px']} vs still={base['ear_length_px']}; head projected WH={m['head_projected_wh']} vs still={base['head_projected_wh']}; body projected WH={m['body_projected_wh']} vs still={base['body_projected_wh']}; body centre x={m['body_centre_x']}"]
        assert good,(v,f,m)
    gif=[]
    for a in seq:
        im=show(a).resize((480,480),Image.Resampling.NEAREST);flat=Image.new('RGB',im.size,BG);flat.paste(im,mask=im.getchannel('A'));gif.append(flat)
    gif[0].save(P/f'preview_{v}.gif',save_all=True,append_images=gif[1:],duration=MS,disposal=2,optimize=False)
    g=Image.open(P/f'preview_{v}.gif');dur=[]
    for f in range(g.n_frames):g.seek(f);dur.append(g.info['duration'])
    # Pillow merges identical back f5/f6; split those identical GIF images by using
    # an equivalent duplicate palette index, retaining exact displayed pixels.
    if dur!=MS:split_identical_gif(v,gif)
    g=Image.open(P/f'preview_{v}.gif');dur=[]
    for f in range(g.n_frames):g.seek(f);dur.append(g.info['duration'])
    assert dur==MS and 'loop' not in g.info,(v,dur)
    lines += [f'{v}: GIF seven frames, 3x exact selout, timings={dur}, no loop extension PASS.']
    lines += [f'{v}: f0 byte-identical still PASS; f6 exact f5 eyes-out PASS.']

# Board, still at left, live row then new row for each view; approved front last.
box=(25,52,147,145);w,h=488,372;pitch=w+12;rh=h+30
board=Image.new('RGB',(8*pitch+12,5*rh+12),BG);d=ImageDraw.Draw(board)
for k,v in enumerate(['se','back']):
    st=show(allnew[v][0]).crop(box).resize((w,h),Image.Resampling.NEAREST)
    board.paste(st,(12,k*2*rh+30),st);d.text((12,k*2*rh+10),v+' APPROVED STILL',fill='white')
    for j,seq in enumerate([alllive[v],allnew[v]]):
        for f,a in enumerate(seq):
            x=(f+1)*pitch+12;y=(2*k+j)*rh+10
            d.text((x,y),f'{v} {"LIVE" if j==0 else "NEW"} f{f}',fill='white')
            im=show(a).crop(box).resize((w,h),Image.Resampling.NEAREST);board.paste(im,(x,y+20),im)
for f in range(7):
    a=load(P.parent/f'frames/front_f{f}.png');im=show(a).crop(box).resize((w,h),Image.Resampling.NEAREST)
    x=(f+1)*pitch+12;y=4*rh+10;d.text((x,y),f'APPROVED LIVE FRONT f{f}',fill='white');board.paste(im,(x,y+20),im)
board.save(P/'board.png')
rows=[]
for v in ['se','back']:
    cells=[]
    for f in [0,3,5]:
        im=Image.fromarray(allnew[v][f]);im=im.crop(im.getbbox());im=im.resize((im.width*7,im.height*7),Image.Resampling.NEAREST);cells.append((f,im))
    rows.append((v,cells))
cw=max(sum(im.width+30 for _,im in cells) for _,cells in rows)+20
ch=sum(max(im.height for _,im in cells)+50 for _,cells in rows)
close=Image.new('RGB',(cw,ch),BG);d=ImageDraw.Draw(close);y=0
for v,cells in rows:
    rowh=max(im.height for _,im in cells)+50;x=15
    for f,im in cells:d.text((x,y+10),f'{v} '+('STILL' if f==0 else f'NEW f{f}'),fill='white');close.paste(im,(x,y+rowh-15-im.height),im);x+=im.width+30
    y+=rowh
close.save(P/'close_7x.png')
(P/'checks.txt').write_text('\n'.join(lines)+'\n')
(P/'measurements.json').write_text(json.dumps(records,indent=2)+'\n')
(P/'landmarks.json').write_text(json.dumps(landmarks,indent=2)+'\n')
for v,rr in records.items():
    for f,r in enumerate(rr):print(v,f,r['ink'],r['cap'],r['violet_light_proxy'],r['eye_px'],r['bbox'])
