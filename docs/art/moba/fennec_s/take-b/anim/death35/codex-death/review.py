"""Read local candidate frames; write review artifacts only beside this script."""
from pathlib import Path
import json, hashlib, importlib.util, sys
sys.dont_write_bytecode=True
import numpy as np
from scipy import ndimage as nd
from PIL import Image, ImageDraw

P=Path(__file__).parent
HEX='141218 211e27 2e1a6e 3d3a44 3fe8b0 6a3cc8 9d9ba2 a46bff b8923a c8fff0 d6d6dc e0c8ff f0d27a f6fffb fff4d6'.split()
PAL=np.array([list(bytes.fromhex(h)) for h in HEX],np.uint8)
MS=[300,100,130,140,160,180,1400]
spec=importlib.util.spec_from_file_location('selout_readonly',P.parents[4]/'rhino_l/take-a/anim/selout_rhino.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def load(p):return np.array(Image.open(p).convert('RGBA'))
still=load(P/'refs/still_s.png')
new=[load(P/f'frames/front_f{f}.png') for f in range(7)]
live=[load(P.parent/f'frames/front_f{f}.png') for f in range(7)]
def equal(a,c):return np.all(a[:,:,:3]==c,axis=2)&(a[:,:,3]>0)
def metric(a,target):
    mask=a[:,:,3]>0;old=target[:,:,3]>0
    edge=mask&~nd.binary_erosion(mask);oe=old&~nd.binary_erosion(old)
    haus=max(nd.distance_transform_edt(~oe)[edge].max(),nd.distance_transform_edt(~edge)[oe].max())
    share={h:round(float(equal(a,c).sum()/mask.sum()*100),2) for h,c in zip(HEX,PAL)}
    gold=np.any([equal(a,PAL[i]) for i in (8,12,14)],axis=0)
    gl,n=nd.label(gold);sizes=np.bincount(gl.ravel())[1:]
    # Independent angle estimator, explicitly NOT claimed equivalent to the unspecified refs metric.
    # Fit palette brightness rank = b*x + c*y + intercept over each material family.
    yy,xx=np.indices(mask.shape);angles={}
    for name,ids in [('violet',[2,5,7,11]),('gold',[8,12,14]),('steel',[3,6,10])]:
        rank=np.full(mask.shape,-1.)
        for r,i in enumerate(ids):rank[equal(a,PAL[i])]=r
        m=rank>=0
        b=np.linalg.lstsq(np.column_stack([xx[m],yy[m],np.ones(m.sum())]),rank[m],rcond=None)[0]
        angles[name]=round(float(np.degrees(np.arctan2(-b[1],b[0]))),1)
    return dict(px=int(mask.sum()),iou=round(float((mask&old).sum()/(mask|old).sum()),5),outline_px=round(float(haus),3),
                share_percent=share,ink=share[HEX[0]],cap=share[HEX[11]],light_proxy_deg=angles,
                gold_mean_cluster=round(float(sizes.mean()),1),gold_clusters=sizes.tolist(),
                eyes=int(sum(equal(a,PAL[i]).sum() for i in (4,9,13))),bottom=int(np.where(mask)[0].max()),
                components=int(nd.label(mask,np.ones((3,3)))[1]),holes=int((nd.binary_fill_holes(mask)&~mask).sum()))

records=[metric(a,b) for a,b in zip(new,live)]
baseline=metric(still,still)
def shown(a):return Image.fromarray(module.selout(a)[0])
bg=(90,96,88)
box=(26,70,116,144);w,h=360,296;pitch=w+12;rh=h+32
board=Image.new('RGB',(8*pitch+12,2*rh+12),bg);dr=ImageDraw.Draw(board)
approved=shown(still).crop(box).resize((w,h),Image.Resampling.NEAREST)
board.paste(approved,(12,32+rh//2),approved);dr.text((12,18+rh//2),'APPROVED STILL',fill='white')
for row,seq in enumerate([live,new]):
    for f,a in enumerate(seq):
        im=shown(a).crop(box).resize((w,h),Image.Resampling.NEAREST);x=12+(f+1)*pitch;y=12+row*rh
        dr.text((x,y),f'{"LIVE" if row==0 else "NEW"} f{f}  {MS[f]} ms',fill='white');board.paste(im,(x,y+20),im)
board.save(P/'board.png')
close_seq=[('STILL',still),('LIVE f3',live[3]),('NEW f3',new[3]),('LIVE f5',live[5]),('NEW f5',new[5])]
cropped=[(lab,Image.fromarray(a).crop(Image.fromarray(a).getbbox())) for lab,a in close_seq]
cw=sum(im.width*7+28 for _,im in cropped)+14;ch=max(im.height*7 for _,im in cropped)+44
close=Image.new('RGB',(cw,ch),bg);dr=ImageDraw.Draw(close);x=14
for lab,im in cropped:
    dr.text((x,10),lab,fill='white');im=im.resize((im.width*7,im.height*7),Image.Resampling.NEAREST)
    close.paste(im,(x,ch-14-im.height),im);x+=im.width+28
close.save(P/'close_7x.png')
gif=[]
for a in new:
    im=shown(a).resize((480,480),Image.Resampling.NEAREST)
    flat=Image.new('RGB',im.size,bg);flat.paste(im,mask=im.getchannel('A'));gif.append(flat)
gif[0].save(P/'preview_front.gif',save_all=True,append_images=gif[1:],duration=MS,disposal=2,optimize=False)

lines=['Candidate raw frames: independent checks; no live build/check scripts executed.',
       'Coordinates zero-based. Outline distance is symmetric Euclidean Hausdorff on 4-neighbour boundaries.',
       'IoU is binary alpha intersection/union against LIVE front frame, before sel-out.',
       'Colour shares: exact RGB counts / opaque pixels; gold clusters: 4-connected union of all three gold colours.',
       'Light proxy: least-squares plane fit to 0..N-1 palette brightness rank, all pixels of each family;',
       'angle atan2(-dy,dx). This does NOT reproduce the undefined light_deg method in refs/measure.json.',
       'Proxy baseline violet/gold/steel: '+str(baseline['light_proxy_deg']),
       'Supplied baseline light_deg violet=115 gold=117 steel=-46; comparison is NOT interchangeable.','']
palette=set(map(tuple,PAL))
for f,(a,m) in enumerate(zip(new,records)):
    op=a[:,:,3]>0
    assert a.shape==(160,160,4)
    assert set(np.unique(a[:,:,3]))<={0,255}
    assert set(map(tuple,a[op,:3]))<=palette
    assert m['components']==1 and m['holes']==0 and m['bottom']==140
    assert not(op[0].any() or op[-1].any() or op[:,0].any() or op[:,-1].any())
    assert m['iou']>=.90 and m['outline_px']<=2
    assert 4<=m['ink']<=6.5
    lines += [f'f{f}: 160x160 / binary alpha / palette / one 8-component / no holes / no stray component / clear edges / bottom 140: PASS',
              f"  px {m['px']}; IoU {m['iou']:.5f}; outline {m['outline_px']:.3f}px; ink {m['ink']:.2f}%; cap {m['cap']:.2f}%; eyes {m['eyes']}",
              f"  light PROXY {m['light_proxy_deg']}; gold mean cluster {m['gold_mean_cluster']:.1f} px; clusters {m['gold_clusters']}",
              '  shares% '+json.dumps(m['share_percent'])]
assert (P/'frames/front_f0.png').read_bytes()==(P/'refs/still_s.png').read_bytes()
expected=new[5].copy();eye=np.any([equal(expected,PAL[i]) for i in (4,9,13)],axis=0);expected[eye,:3]=PAL[2]
assert np.array_equal(expected,new[6])
g=Image.open(P/'preview_front.gif');dur=[]
for f in range(g.n_frames):g.seek(f);dur.append(g.info.get('duration'))
assert dur==MS and 'loop' not in g.info
lines += ['', 'f0 byte-for-byte approved PNG: PASS; f6 exact f5 with ALL three eye colours -> #2E1A6E: PASS.',
          'GIF 3x, exact selout function with #141218; durations '+str(dur)+'; no loop extension: PASS.',
          'Board 4x with exact selout; close-ups 7x without outline; both #5A6058.',
          'Cap target is approximately 2.32%; see measured deviations above. No colour quotas enforced.',
          'Structural assertions pass. Visual artist-match and supplied light_deg equivalence are NOT certified.']
(P/'checks.txt').write_text('\n'.join(lines)+'\n')
(P/'measurements.json').write_text(json.dumps({'still_proxy':baseline,'frames':records},indent=2)+'\n')
print('\n'.join(lines[:8]))
for f,m in enumerate(records):print(f,m['ink'],m['cap'],m['light_proxy_deg'],m['gold_mean_cluster'],m['eyes'])

