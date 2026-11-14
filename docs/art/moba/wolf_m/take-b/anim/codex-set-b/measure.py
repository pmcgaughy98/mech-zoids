"""Manual visible landmarks. These are measurements, not assumed design constants.
No hidden limb roots or foreshortened true lengths are certified from a 2D raster.
"""
from finish import *
from math import hypot
# Side: visible ear axis, full head axis, muzzle, torso axis, torso-depth cross-section,
# near foreleg joint chain, hindleg chain, tail axis, tail thickness cross-section.
ref={
'ear':[(130,108),(128,95)],'head':[(124,110),(149,118)],'muzzle':[(138,114),(149,118)],
'body_length':[(77,120),(112,117)],'body_depth':[(95,109),(95,126)],
'foreleg':[(112,123),(108,138),(111,157)],'hindleg':[(81,125),(69,139),(67,157)],
 'tail_length':[(74,124),(43,153)],'tail_thickness':[(57,136),(63,142)]}
# Read directly against measurement_side.png. Joint-chain values are visible estimates;
# upper roots overlap torso, so they carry uncertainty rather than a fabricated pass.
pose={
'hamstring':{
1:{'ear':[(130,120),(127,106)],'head':[(125,123),(149,130)],'muzzle':[(138,126),(149,130)],'body_length':[(77,126),(111,126)],'body_depth':[(95,119),(95,135)],'foreleg':[(111,127),(113,146),(126,158)],'hindleg':[(82,129),(67,140),(67,157)],'tail_length':[(73,129),(42,153)],'tail_thickness':[(55,139),(61,145)]},
2:{'ear':[(130,130),(120,119)],'head':[(123,130),(149,136)],'muzzle':[(138,133),(149,136)],'body_length':[(77,129),(110,132)],'body_depth':[(94,123),(94,138)],'foreleg':[(108,131),(108,147),(126,158)],'hindleg':[(82,131),(67,141),(67,157)],'tail_length':[(73,131),(42,153)],'tail_thickness':[(55,140),(61,146)]},
3:{'ear':[(132,137),(121,123)],'head':[(124,139),(148,147)],'muzzle':[(137,143),(148,147)],'body_length':[(77,130),(109,134)],'body_depth':[(93,123),(93,140)],'foreleg':[(108,134),(109,149),(126,157)],'hindleg':[(82,132),(67,141),(67,157)],'tail_length':[(74,131),(43,153)],'tail_thickness':[(56,140),(62,146)]},
4:{'ear':[(130,116),(123,101)],'head':[(123,116),(147,122)],'muzzle':[(136,119),(147,122)],'body_length':[(77,125),(110,125)],'body_depth':[(94,116),(94,134)],'foreleg':[(112,126),(112,143),(125,158)],'hindleg':[(82,128),(68,140),(68,157)],'tail_length':[(74,128),(44,153)],'tail_thickness':[(57,139),(63,145)]}},
'howl':{
1:{'ear':[(130,115),(120,103)],'head':[(124,117),(148,125)],'muzzle':[(137,121),(148,125)],'body_length':[(77,127),(111,124)],'body_depth':[(94,120),(94,136)],'foreleg':[(112,125),(111,142),(113,158)],'hindleg':[(80,130),(88,146),(71,155)],'tail_length':[(74,131),(44,153)],'tail_thickness':[(57,141),(63,147)]},
2:{'ear':[(128,107),(116,98)],'head':[(123,108),(147,115)],'muzzle':[(136,112),(147,115)],'body_length':[(78,126),(112,119)],'body_depth':[(95,119),(98,136)],'foreleg':[(113,122),(111,140),(114,158)],'hindleg':[(82,131),(88,146),(72,155)],'tail_length':[(75,131),(44,154)],'tail_thickness':[(58,142),(64,148)]},
3:{'ear':[(122,108),(111,106)],'head':[(119,109),(134,88)],'muzzle':[(128,98),(134,88)],'body_length':[(78,126),(111,116)],'body_depth':[(95,120),(100,137)],'foreleg':[(113,122),(112,140),(115,158)],'hindleg':[(82,131),(89,146),(72,155)],'tail_length':[(75,131),(44,154)],'tail_thickness':[(58,142),(64,148)]},
4:{'ear':[(130,108),(119,97)],'head':[(124,110),(148,118)],'muzzle':[(137,114),(148,118)],'body_length':[(78,125),(111,120)],'body_depth':[(95,117),(97,135)],'foreleg':[(112,124),(112,141),(114,158)],'hindleg':[(82,131),(79,144),(74,157)],'tail_length':[(75,130),(45,153)],'tail_thickness':[(58,141),(64,147)]}},
'death':{
1:{'ear':[(129,106),(118,100)],'head':[(124,106),(147,109)],'muzzle':[(136,108),(147,109)],'body_length':[(78,123),(113,119)],'body_depth':[(96,114),(97,132)],'foreleg':[(112,123),(109,141),(112,158)],'hindleg':[(82,128),(73,142),(73,158)],'tail_length':[(75,129),(45,153)],'tail_thickness':[(57,140),(63,146)]},
2:{'ear':[(129,120),(127,107)],'head':[(124,120),(150,131)],'muzzle':[(138,126),(150,131)],'body_length':[(77,130),(113,127)],'body_depth':[(96,117),(96,136)],'foreleg':[(112,131),(110,146),(125,157)],'hindleg':[(82,133),(71,144),(75,158)],'tail_length':[(74,133),(42,155)],'tail_thickness':[(54,143),(60,149)]},
3:{'ear':[(132,142),(132,126)],'head':[(126,142),(149,151)],'muzzle':[(139,146),(149,151)],'body_length':[(77,143),(114,143)],'body_depth':[(96,131),(96,151)],'foreleg':[(114,142),(110,153),(133,156)],'hindleg':[(82,144),(68,149),(75,158)],'tail_length':[(75,142),(42,155)],'tail_thickness':[(54,146),(58,153)]},
4:{'ear':[(133,149),(132,132)],'head':[(126,146),(143,156)],'muzzle':[(137,151),(143,156)],'body_length':[(78,142),(116,144)],'body_depth':[(96,135),(96,150)],'foreleg':None,'hindleg':None,'tail_length':[(75,146),(45,156)],'tail_thickness':[(55,147),(57,154)]},
5:{'ear':None,'head':None,'muzzle':None,'body_length':None,'body_depth':None,'foreleg':None,'hindleg':None,'tail_length':None,'tail_thickness':None},
6:{'ear':None,'head':None,'muzzle':None,'body_length':None,'body_depth':None,'foreleg':None,'hindleg':None,'tail_length':None,'tail_thickness':None}}}
def length(pts):return round(sum(hypot(x2-x1,y2-y1) for (x1,y1),(x2,y2) in zip(pts,pts[1:]))+1,2) if pts else None
refs={k:length(p) for k,p in ref.items()};records=[]
tail_log={(t['move'],t['frame']):t for t in json.loads((R/'tail_landmarks.json').read_text())}
for name,ts in TIMES.items():
 for v in V:
  rb=Image.open(REF[v]).getbbox()
  for i in range(len(ts)):
   im=Image.open(R/name/'frames'/f'{v}_f{i}.png');bb=im.getbbox();exact=i==0 or (name!='death' and i==len(ts)-1)
   item=dict(move=name,view=v,frame=i,whole_bbox=list(bb),whole_wh=[bb[2]-bb[0],bb[3]-bb[1]],still_wh=[rb[2]-rb[0],rb[3]-rb[1]],interpretation='bbox varies with pose; not a part-size test')
   if v=='side':
    pts=ref.copy() if exact else pose[name][i].copy()
    if (name,i) in tail_log:
     t=tail_log[(name,i)];pts['tail_length']=[t['root'],t['tip']]
    values={k:length(p) for k,p in pts.items()};deltas={k:round(values[k]-refs[k],2) if values[k] is not None else None for k in refs}
    item.update(landmarks=pts,visible_axis_px=values,reference_axis_px=refs,delta_px=deltas,flagged_over_2px=[k for k,val in deltas.items() if val is not None and abs(val)>2],annotation_uncertainty_px=2,certified_proportion_pass=exact)
    if name=='death' and i>=5:item['measurement_note']='same generated f4 drawing rigidly rotated: lengths inherited, visibility and pixel rasterization change; limb roots occluded'
   else:item['part_measurement_status']='front/back overlap and foreshortening: no full axial-length certification; whole extents recorded, visually compared on 4x boards'
   records.append(item)
(R/'proportions.json').write_text(json.dumps(dict(method='Manually tagged visible side-view axes/cross-sections and joint chains, Euclidean polyline distance +1 native pixel. These are projected extents, not recovered hidden anatomy. 2px annotation uncertainty. Flags are retained, not converted to automatic passes.',reference_side=refs,frames=records),indent=2))
for name in TIMES:
 subset=[f for f in records if f['move']==name and f['view']=='side'];print(name,{k:[min(vals),max(vals)] for k in refs if (vals:=[f['visible_axis_px'][k] for f in subset if f['visible_axis_px'][k] is not None])})
