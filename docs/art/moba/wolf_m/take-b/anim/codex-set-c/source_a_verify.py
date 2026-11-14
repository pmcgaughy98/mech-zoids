from finish import *
from collections import Counter
allchecks={};summaries={};edgecounts=Counter();counts=Counter();support=[]
for n in TIMES:
 checks=finalize(n);
 for c in checks:c.update(all_part_proportions_within_2px=None,complete_part_measurement_available=False,overall_art_gate_pass=False)
 (R/n/'checks.txt').write_text('Structural checks PASS. Overall art gate NOT PASSED: complete per-part measurements remain unresolved. Approved endpoints retain source holes.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 allchecks[n]=checks;g=json.loads((R/n/'grid.json').read_text());g['native_finishing']={'method':'Whole generated drawings, nearest-neighbour native pixel corrections, fixed palette and binary alpha. No approved part compositing. Exact endpoints copied byte for byte.','scripts':['../polish.py']+(['../gait_finish.py'] if n=='walk' else ['../details.py'] if n=='sprint' else []),'final_pixel_scale':1,'approved_canvas_offset':[0,0]}
 if n=='walk':g['support_edits']=[r for r in json.loads((R/'support_edits.json').read_text())]
 for c in g['cells']:
  c['final_canvas_offset']=[0,0];c['final_bottom']=next(z['bottom_row'] for z in checks if z['frame']==f"{c['view']}_f{c['frame']}")
 (R/n/'grid.json').write_text(json.dumps(g,indent=2)+'\n')
 assert all(c['structural_pass'] for c in checks)
 for c in checks:
  if c['required_exact_still']:assert c['png_bytes_identical'] and c['rgba_equal'] and c['silhouette_IoU']==1 and c['colour_IoU']==1
 for v in VIEWS:
  dims=[]
  for i in range(len(TIMES[n])):
   a=np.array(Image.open(R/n/'frames'/f'{v}_f{i}.png'));m=a[:,:,3]>0;edge=m&~ndi.binary_erosion(m);counts.update(map(tuple,a[m,:3]));edgecounts.update(map(tuple,a[edge,:3]));b=Image.fromarray(a).getbbox();dims.append([b[2]-b[0],b[3]-b[1]])
  summaries[f'{n}/{v}']={'silhouette_width_range':[min(d[0] for d in dims),max(d[0] for d in dims)],'silhouette_height_range':[min(d[1] for d in dims),max(d[1] for d in dims)],'per_frame_wh':dims}
 for v,zones in [('front',[(0,96),(96,192)]),('back',[(0,91),(101,192)])] if n=='walk' else []:
  for i in range(8):
   a=np.array(Image.open(R/n/'frames'/f'{v}_f{i}.png'));m=a[:,:,3]>0;vals=[]
   for lo,hi in zones:
    yy,xx=np.where(m[:,lo:hi]&(np.indices(m[:,lo:hi].shape)[0]>=130));bot=int(yy.max());groundx=np.where(m[bot,lo:hi])[0]+lo;vals.append({'lowest_row':bot,'clearance':160-bot,'lowest_row_x':groundx.tolist()})
   support.append({'view':v,'frame':i,'legs':vals})
(R/'verification.json').write_text(json.dumps(allchecks,indent=2)+'\n');(R/'support_checks.json').write_text(json.dumps(support,indent=2)+'\n')
lines=['hex opaque_pixels edge_pixels edge_fraction']
for p in PAL:
 t=tuple(p);lines.append(f'#{bytes(p).hex()} {counts[t]} {edgecounts[t]} {edgecounts[t]/counts[t]:.5f}')
(R/'palette.txt').write_text('\n'.join(lines)+'\n')
# Manually tagged visible reference axes. No reference texels are used to produce posed frames.
axes={'front':{'ear_left_axis':[[91,89],[92,101]],'ear_right_axis':[[103,89],[102,101]],'head_axis':[[96,100],[96,117]],'muzzle_axis':[[96,108],[96,117]],'torso_width':[[80,121],[112,121]],'torso_depth':[[96,117],[96,133]],'foreleg_axis':[[85,126],[87,138],[87,157],[87,160]],'shank_cross_section':[[84,145],[90,145]],'tail_axis':None},'side':{'ear_far_axis':[[119,97],[126,108]],'ear_near_axis':[[127,95],[137,108]],'head_axis':[[123,109],[150,118]],'muzzle_axis':[[136,112],[150,118]],'torso_length':[[69,118],[117,115]],'torso_depth':[[99,107],[99,129]],'foreleg_axis':[[115,121],[112,140],[115,157],[118,159]],'hindleg_axis':[[80,122],[69,140],[68,157],[71,159]],'shank_cross_section':[[105,145],[111,145]],'tail_axis':[[62,125],[42,154]]},'back':{'ear_left_axis':[[89,89],[89,102]],'ear_right_axis':[[101,89],[102,102]],'head_axis':[[95,98],[95,109]],'torso_width':[[78,119],[112,119]],'torso_depth':[[95,109],[95,137]],'hindleg_axis':[[83,128],[83,140],[83,155]],'shank_cross_section':[[81,145],[84,145]],'tail_axis':[[95,125],[95,160]]}}
lengths={v:{k:round(sum(np.linalg.norm(np.array(b)-a) for a,b in zip(p,p[1:])),2)+1 if p else None for k,p in parts.items()} for v,parts in axes.items()}
prop={'status':'NOT PASSED: complete per-part intrinsic measurements of every articulated drawing have not been established. Do not equate silhouette bounds with limb, ear or tail lengths.','reference_axes_native_pixels':axes,'reference_inclusive_axis_lengths':lengths,'whole_frame_measurements':summaries,'part_plate_count_status':'Generated plate boundaries vary; a full per-frame tail plate-count pass is not certified.','known_visual_risks':['Side walk has uneven diagonal timing and some excessive raised-paw clearance.','Sprint profile ears are repainted flat; streaming tail length and intrinsic per-part dimensions remain uncertified.','Bite foot extents were anchored but interior hind-limb contours still vary.','Some action torsos and muzzles differ from the still beyond the requested 2px tolerance; not certified for installation.'],'reference_tail_note':'Front tail occluded. Rear native tail tip is on row160; rear paw soles end on row155.'}
(R/'proportions.json').write_text(json.dumps(prop,indent=2)+'\n')
print(json.dumps({'frames':sum(map(len,allchecks.values())),'exact_endpoints':sum(c['required_exact_still'] for cs in allchecks.values() for c in cs),'all_structural_pass':True,'proportions_pass':False,'dimensions':summaries,'reference_axes':lengths},indent=2))
