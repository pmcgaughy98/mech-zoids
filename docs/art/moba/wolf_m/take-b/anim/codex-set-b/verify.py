from finish import *
allchecks={};support={};palcount=np.zeros(12,int);edgecount=np.zeros(12,int)
for name,ts in TIMES.items():
 checks=finalize(name);allchecks[name]=checks;grid=json.loads((R/name/'grid.json').read_text())
 for c in checks:
  p=R/name/'frames'/f"{c['frame']}.png";a=np.array(Image.open(p));m=a[:,:,3]>0
  assert a.shape==(192,192,4) and c['bottom_row']==160 and c['palette_ok'] and c['binary_alpha'] and c['below160']==0 and not c['edge'] and c['components']==1,c
  if c['exact_still']:assert c['file_byte_identical'] and c['silhouette_IoU']==c['colour_IoU']==1
  else:assert c['holes']==0
  for j,col in enumerate(PAL):
   hits=np.all(a[:,:,:3]==col,2)&m;palcount[j]+=hits.sum();edgecount[j]+=(hits&m&~ndi.binary_erosion(m)).sum()
  view,fi=c['frame'].split('_f');entry=next(e for e in grid['cells'] if e['view']==view and e['frame']==int(fi));entry['final_path']=str(p.relative_to(R/name));entry['final_bbox']=c['bbox'];entry['final_canvas']=[192,192];entry['ground_row']=160
  if name=='death' and int(fi) in (5,6):entry['finishing_source_frame']=4;entry['whole_drawing_roll_degrees']={'front':-20,'side':5,'back':40}[view]
 grid['preview_ms']=ts;grid['finishing']='whole drawing native-scale correction; no still parts pasted; see ../pixel_edits.json';grid['empty_gutter_cuts']=not any(c['touches_cut'] for c in grid['cells']);(R/name/'grid.json').write_text(json.dumps(grid,indent=2))
 for v in V:
  gif=Image.open(R/name/f'preview_{v}.gif');dur=[]
  for i in range(gif.n_frames):gif.seek(i);dur.append(gif.info['duration']);gif.convert('RGB').load()
  assert gif.n_frames==len(ts) and dur==ts
# Quantify actual hind ground contact span drift, rather than declaring a fixed plant by eye.
for i in range(6):
 a=np.array(Image.open(R/'hamstring/frames'/f'side_f{i}.png'));m=a[156:161,55:85,3]>0;yy,xx=np.where(m);support[str(i)]=dict(hind_ground_centroid=[float(xx.mean()+55),float(yy.mean()+156)],pixels=int(m.sum()))
# Last death drawing must differ only in eye RGB, never silhouette or body.
for v in V:
 a=np.array(Image.open(R/'death/frames'/f'{v}_f5.png'));b=np.array(Image.open(R/'death/frames'/f'{v}_f6.png'));changed=np.any(a!=b,2);cyan=np.all(a[:,:,:3]==PAL[8],2)&(a[:,:,3]>0)
 assert np.array_equal(changed,cyan) and not (np.all(b[:,:,:3]==PAL[8],2)&(b[:,:,3]>0)).any()
(R/'verification.json').write_text(json.dumps(allchecks,indent=2));(R/'support_checks.json').write_text(json.dumps(support,indent=2))
(R/'palette.txt').write_text('\n'.join(f'#{bytes(c).hex()} count={int(n)} edge={int(e)}' for c,n,e in zip(PAL,palcount,edgecount)))
print('PASS 57 native PNGs; 15 exact file-byte endpoints/IoU1; 42 clean posed frames; 9 GIFs exact timing.');print('Hind support',support)
