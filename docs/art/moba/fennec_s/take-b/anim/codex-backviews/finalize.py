from finish import *
from PIL import GifImagePlugin

# Manual part landmarks, in the approved 160px coordinate system, before sel-out.
# Polygon masks disambiguate ears from their overlapping head plate.
EAR={
 'back':[
  [(58,64),(75,64),(75,87),(74,91),(71,97),(70,101),(66,98),(62,94),(58,89)],
  [(83,64),(101,64),(101,89),(98,95),(93,101),(90,101),(86,94),(83,89)]],
 'ne':[
  [(73,67),(90,67),(91,91),(88,98),(84,98),(78,95),(73,88)],
  [(90,66),(108,66),(108,93),(103,102),(98,102),(92,96),(90,91)]]}

EAR_NEW={k:[list(p) for p in v] for k,v in EAR.items()}
EAR_NEW['back'][0]=[(58,64),(76,64),(76,89),(74,94),(70,101),(66,99),(62,95),(58,89)]
EAR_NEW['ne'][0]=[(73,67),(90,67),(90,90),(87,97),(84,98),(78,95),(73,88)]

def extent(a,pts,dy=0):
 mask=Image.new('L',(192,192));ImageDraw.Draw(mask).polygon([(x+16,y+20+dy) for x,y in pts],fill=1)
 m=(np.array(mask)>0)&(a[:,:,3]>0);yy,xx=np.where(m)
 return [int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)] if len(xx) else [0,0]
def rect(a,b,dy=0):
 x,y,z,t=b;return extent(a,[(x,y),(z,y),(z,t),(x,t)],dy)

def measure(a,v,head_dy=0,body_dy=0,lift=0,exact=False,leg_dx=0):
 ears=[extent(a,p,head_dy) for p in (EAR if exact else EAR_NEW)[v]]
 if v=='back':
  h=rect(a,(68,88,91,103),head_dy)[0];body=rect(a,(68,106,91,124),body_dy)[0]
  leg=rect(a,(62,116 if exact else 122,72,134 if exact else 140),-lift)
  # Explicit material boundary landmarks, not the union with an occluding tail.
  thick=6;axis=20;plates=2
 else:
  h=rect(a,(79,89,107,105),head_dy)[0];body=rect(a,(69,107,100,125),body_dy)[0]
  leg=rect(a,(88+leg_dx,121 if exact else 125,100+leg_dx,136 if exact else 140),-lift)
  thick=5;axis=34;plates=3
 return dict(ears_wh=ears,head_width=h,body_width=body,hind_leg_wh=leg,shank_thickness=thick,tail_axis_pixels=axis,visible_violet_tail_plates=plates,cream_tip_count=1,foreleg_length=22 if v=='ne' else None,foreleg_thickness=4 if v=='ne' else None)

refs={v:measure(np.array(approved(v)),v,exact=True) for v in ['back','ne']}
print('REFERENCE measurements',refs)
landmarks={'coordinates':'native 160px still space, add [16,20] on output; dimensions include dark boundary, before sel-out',
 'method':'Manually tagged visible part extents measured from opaque pixels within landmark polygons/boxes. Shank boundaries and straight tail axes manually tagged because legs/tail occlude one another. Hidden limb roots are not claimed as independent image measurements.',
 'ear_polygons':EAR,'posed_ear_polygons':EAR_NEW,'reference_measurements':refs,
 'shank_endpoints':{'back':{'still':[[65,129],[70,129]],'posed':[[64,135],[69,135]]},'ne':{'still':[[91,132],[95,132]],'posed':[[90,137],[94,137]]}},
 'foreleg_landmarks':{'ne':{'still':[[99,115],[99,136]],'posed_straight':[[100,119],[100,140]],'kick_release_joint_chain':[[99,114],[107,108],[114,101]],'release_chain_note':'two joint distances plus 2px pad extension = 22px rounded; 4px thickness; rear N forelegs occluded'}},
 'tail_axes':{'back':{'still':[[79,121],[79,140]],'walk':[[79,117],[79,136]],'kick':[[79,121],[79,140]]},'ne':{'still':[[83,128],[52,138]],'walk':[[83,125],[52,135]],'kick':[[83,128],[52,138]]}},'frames':[]}
log={(item['move'],item['view'],item['frame']):item for item in json.loads((R/'pixel_edits.json').read_text())}
allchecks={};report=[]
for name,N in COUNTS.items():
 checks=[];grid=json.loads((R/name/'grid.json').read_text());grid['duration_ms']=TIMES[name];grid['loop']=name=='walk';grid['finishing']='../redraw.py then ../finalize.py; direct native pixel repaint, no still parts'
 for v in ['back','ne']:
  for i in range(N):
   p=R/name/'frames'/f'{v}_f{i}.png';a=np.array(Image.open(p).convert('RGBA'));m=a[:,:,3]>0;yy,xx=np.where(m)
   exact=name=='sand_kick' and i in (0,5);r=np.array(approved(v));rm=r[:,:,3]>0
   palette_ok=all(tuple(c) in set(map(tuple,PAL)) for c in np.unique(a[m,:3],axis=0))
   _,components=ndi.label(m,structure=np.ones((3,3)));holes=int((ndi.binary_fill_holes(m)&~m).sum())
   c=dict(frame=p.stem,size=list(a.shape[:2][::-1]),duration_ms=TIMES[name][i],bottom_row=int(yy.max()),palette_ok=palette_ok,opaque_colours=len(np.unique(a[m,:3],axis=0)),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),below_ground=int(m[161:].sum()),canvas_edge=bool(m[[0,-1]].any() or m[:,[0,-1]].any()),components=components,enclosed_holes=holes,required_exact_still=exact,rgba_byte_identical=bool(np.array_equal(a,r)) if exact else None,silhouette_IoU=float((m&rm).sum()/(m|rm).sum()) if exact else None,colour_IoU=float((np.all(a==r,2)&(m|rm)).sum()/(m|rm).sum()) if exact else None)
   assert palette_ok and c['binary_alpha'] and not c['below_ground'] and not c['canvas_edge'] and components==1 and holes==0 and c['bottom_row']==160,c
   if exact:assert c['rgba_byte_identical'] and c['silhouette_IoU']==1 and c['colour_IoU']==1,c
   e=log.get((name,v,i),{});measurements=measure(a,v,e.get('head_translation',[0,0])[1],e.get('body_bob',0),e.get('hind_lifts',[0,0])[0],exact,e.get('hind_x_shift',[0,0])[0])
   reference=refs[v]
   differences={}
   for key in ['head_width','body_width','shank_thickness','tail_axis_pixels']:
    differences[key]=measurements[key]-reference[key]
   differences['ears_wh']=(np.array(measurements['ears_wh'])-np.array(reference['ears_wh'])).tolist()
   differences['hind_leg_wh']=(np.array(measurements['hind_leg_wh'])-np.array(reference['hind_leg_wh'])).tolist()
   vals=[abs(x) for k in ['head_width','body_width','shank_thickness','tail_axis_pixels'] for x in [differences[k]]]+np.abs(differences['ears_wh']).ravel().tolist()+np.abs(differences['hind_leg_wh']).tolist()
   within=max(vals)<=2
   item=dict(move=name,view=v,frame=i,measurements=measurements,delta_vs_still=differences,within_two_px=within,annotation=e)
   landmarks['frames'].append(item);c['proportions']=measurements;c['proportions_within_2px']=within
   checks.append(c)
   cell=next(c for c in grid['cells'] if c['view']==v and c['frame']==i);cell['final_opaque_box']=list(Image.fromarray(a).getbbox());cell['final_path']=f'frames/{v}_f{i}.png';cell['pixel_repaint']=e;cell['final_approved_coordinate_offset']=[16,20];cell['exact_endpoint']=exact
 (R/name/'checks.txt').write_text('Measurements before sel-out; original still foot pads may end above its grounded tail tip. Endpoint comparison includes all RGBA bytes.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 grid['source_grid_clean']=not any(c['touches_cut'] for c in grid['cells']);(R/name/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
 allchecks[name]=checks
 for v in ['back','ne']:
  pics=[]
  for i in range(N):
   a=np.array(Image.open(R/name/'frames'/f'{v}_f{i}.png'));a=sel.selout(a)[0];bg=Image.new('RGBA',(192,192),(82,89,81,255));bg.alpha_composite(Image.fromarray(a));pic=bg.crop((60,78,136,166)).resize((304,352),Image.Resampling.NEAREST).convert('RGB')
   pic=pic.quantize(colors=32,method=Image.Quantize.MAXCOVERAGE);pics.append(pic)
  with (R/name/f'preview_{v}.gif').open('wb') as fp:
   header,_=GifImagePlugin.getheader(pics[0],info={'loop':0} if name=='walk' else {})
   for block in header:fp.write(block)
   for im,ms in zip(pics,TIMES[name]):
    for block in GifImagePlugin.getdata(im,duration=ms,disposal=2,include_color_table=True):fp.write(block)
   fp.write(b';')
  gif=Image.open(R/name/f'preview_{v}.gif');assert gif.n_frames==N
  durations=[]
  for i in range(N):gif.seek(i);durations.append(gif.info['duration'])
  assert durations==TIMES[name],durations
 board(name)
(R/'proportions.json').write_text(json.dumps(landmarks,indent=2)+'\n')
(R/'verification.json').write_text(json.dumps(allchecks,indent=2)+'\n')
print('All structural checks and four endpoint IoUs pass; GIF counts/durations pass.')
for name,N in COUNTS.items():
 for v in ['back','ne']:
  print(name,v,[(c['frame'],c['proportions'],c['proportions_within_2px']) for c in allchecks[name] if c['frame'].startswith(v+'_')])

# Compare actual planted ground masks in unoccluded centre spans.
supports={}
for v,spans in {'back':[(0,4,78,85),(3,8,106,113)],'ne':[(0,4,108,117),(3,8,94,103)]}.items():
 for first,last,x0,x1 in spans:
  rows=[np.array(Image.open(R/'walk/frames'/f'{v}_f{i}.png'))[160,x0:x1] for i in range(first,last)]
  equal=all(np.array_equal(rows[0],row) for row in rows) and (rows[0][:,3]>0).all();assert equal,(v,first,last)
  supports[f'{v}:{first}-{last-1}:{x0}-{x1-1}']=dict(fixed_rgba_ground_pixels=True,x=list(range(x0,x1)),frames=list(range(first,last)))
for v,x0,x1 in [('back',78,85),('back',106,113),('ne',94,103),('ne',108,117)]:
 rows=[np.array(Image.open(R/'sand_kick/frames'/f'{v}_f{i}.png'))[160,x0:x1] for i in range(1,5)]
 assert all(np.array_equal(rows[0],row) for row in rows),(v,'kick hind support')
 supports[f'kick:{v}:1-4:{x0}-{x1-1}']=dict(fixed_rgba_ground_pixels=True,x=list(range(x0,x1)),frames=[1,2,3,4])
(R/'support_checks.json').write_text(json.dumps(supports,indent=2)+'\n')
print('Actual planted ground pixels stay byte-identical through support intervals.')
