"""Adapted from A verification; distinguish structural checks from failed art gates."""
from finish import *
from collections import Counter
allchecks={};summary={};edges=Counter();counts=Counter();support=[]
for n in TIMES:
 cs=finalize(n);allchecks[n]=cs;g=json.loads((R/n/'grid.json').read_text())
 for c in cs:
  assert c['structural_pass'],c
  if c['required_exact_still']:assert c['png_bytes_identical'] and c['silhouette_IoU']==1 and c['colour_IoU']==1
  c.update(all_part_proportions_within_2px=None,tail_plate_count_certified=False,overall_art_gate_pass=False)
  cell=next(x for x in g['cells'] if f"{x['view']}_f{x['frame']}"==c['frame']);cell['extraction_placement']=cell['placement'];cell['final_placement']=c['bounds'][:2];cell['final_bottom_row']=c['bottom_row'];cell['native_finishing']=['polish.py']+(['gait_finish.py'] if n=='walk' else [])+['details.py']
  cell['effective_whole_scale']=cell['scale']*({'se':.88,'ne':.94}[cell['view']] if n=='sprint' else 1)
  cell['whole_x_correction']=.96 if n=='lunge' and cell['view']=='se' and not c['required_exact_still'] else 1
 g['finishing_notes']={'palette':'shared exact 12 colours','alpha':'binary','no_reference_part_compositing':True,'exact_endpoints':'copied byte for byte from fixed','pose_corrections':'whole-cell nearest sampling and native material cleanup','walk_support_gate':'FAILED: diagonal phases, fixed contacts and 3-5px lift not fully solved','strict_per_part_2px_gate':'NOT CERTIFIED','raw_edge_contact':'walk se f7 touches raw right edge; final muzzle inspected at4x' if n=='walk' else None}
 (R/n/'grid.json').write_text(json.dumps(g,indent=2)+'\n')
 (R/n/'checks.txt').write_text('STRUCTURAL PASS. ART GATE NOT PASSED: proportions/tail plate counts uncertified; walk gait fails. Exact endpoints preserve original holes.\n'+'\n'.join(json.dumps(c) for c in cs)+'\n')
 for v in VIEWS:
  dims=[];bounds=[]
  for i in range(len(TIMES[n])):
   a=np.array(Image.open(R/n/'frames'/f'{v}_f{i}.png'));m=a[:,:,3]>0;b=Image.fromarray(a).getbbox();bounds.append(list(b));dims.append([b[2]-b[0],b[3]-b[1]])
   counts.update(map(tuple,a[m,:3]));edge=m&~ndi.binary_erosion(m);edges.update(map(tuple,a[edge,:3]))
   if n=='walk':
    # Actual lower-leg components, not intended targets. Tail may touch a projected hind leg.
    mm=m.copy();mm[:145]=0;mm[:,:64 if v=='se' else 73]=0;lab,k=ndi.label(mm,np.ones((3,3)));parts=[]
    for sl in ndi.find_objects(lab):
     if sl and int(mm[sl].sum())>4:parts.append({'bounds':[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop],'bottom':sl[0].stop-1,'distance_to_row160':161-sl[0].stop})
    support.append(dict(view=v,frame=i,actual_lower_components=parts,pass_all_support_requirements=False))
  summary[f'{n}/{v}']={'per_frame_wh':dims,'per_frame_bounds':bounds,'width_range':[min(d[0] for d in dims),max(d[0] for d in dims)],'height_range':[min(d[1] for d in dims),max(d[1] for d in dims)]}
  # All 4x panels put the same approved still at left.
  b=Image.open(R/n/f'review_{v}.png')
  for st in range(0,len(TIMES[n]),2):
   out=Image.new('RGB',(1536,432),(84,92,88));out.paste(b.crop((0,0,512,432)),(0,0));out.paste(b.crop(((st+1)*512,0,min((st+3)*512,b.width),432)),(512,0));out.save(R/n/f'panel_{v}_{st//2}.png')
# Approximate visible reference axes hand-tagged at native scale; hidden anatomy is not inferred.
axes={
 'se':{'near_ear':[[115,91],[119,105]],'far_ear':[[124,91],[127,103]],'head':[[117,103],[136,116]],'muzzle':[[126,109],[136,116]],'torso_length':[[79,117],[108,118]],'torso_depth':[[96,110],[96,130]],'near_fore_shank':[[100,138],[103,156]],'near_fore_shank_cross_section':[[100,148],[105,148]],'tail_visible_axis':[[77,124],[56,150]],'tail_cross_section':[[60,135],[67,141]]},
 'ne':{'near_ear':[[130,92],[126,105]],'far_ear':[[121,91],[116,104]],'head':[[122,104],[132,114]],'muzzle':'mostly occluded','torso_length':[[90,122],[116,111]],'torso_depth':[[103,118],[103,137]],'near_hind_shank':[[90,141],[91,156]],'near_hind_shank_cross_section':[[88,150],[93,150]],'tail_visible_axis':[[88,128],[59,156]],'tail_cross_section':[[67,141],[75,149]]}}
lengths={v:{k:round(sum(np.linalg.norm(np.array(b)-a) for a,b in zip(p,p[1:])),2)+1 if isinstance(p,list) else p for k,p in ps.items()} for v,ps in axes.items()}
proportions={'status':'NOT PASSED: per-frame intrinsic ears/head/muzzle/torso/limb/tail measurements within2px and tail plate counts are not certified. Silhouette bounds do not establish this gate.','reference_axes_approximate_native_pixels':axes,'reference_inclusive_axis_lengths_approximate':lengths,'actual_whole_frame_measurements':summary,'tail_plate_count_status':'Not certified; no thin rods observed at4x, but plate divisions and apparent length vary.','risks':['Walk support phases repeat; fixed contacts and3-5px lifts not met.','Sprint ears are not fully flattened in every cell; tail plate count and individual limb lengths vary.','Lunge crouch/air silhouette has generated head/torso proportion variation.','Bite lower paw spans reanchored; torso and tail interior drawing varies.']}
(R/'proportions.json').write_text(json.dumps(proportions,indent=2)+'\n');(R/'verification.json').write_text(json.dumps(allchecks,indent=2)+'\n');(R/'support_checks.json').write_text(json.dumps(support,indent=2)+'\n')
(R/'palette.txt').write_text('hex opaque_pixels edge_pixels\n'+'\n'.join(f'#{bytes(p).hex()} {counts[tuple(p)]} {edges[tuple(p)]}' for p in PAL)+'\n')
print(json.dumps({'frames':sum(map(len,allchecks.values())),'structural_pass':all(c['structural_pass'] for cs in allchecks.values() for c in cs),'exact_endpoints':sum(c['required_exact_still'] for cs in allchecks.values() for c in cs),'strict_art_gate':False,'dimensions':summary,'reference_axes_approximate':lengths},indent=2))
