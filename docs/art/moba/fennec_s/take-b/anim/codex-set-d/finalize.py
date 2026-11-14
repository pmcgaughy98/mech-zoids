"""Metadata and report delivery, adapted from the A/B finalization passes."""
from finish import *
verification=json.loads((ROOT/'verification.json').read_text())
allchecks={}
for name,N in COUNTS.items():
 out=ROOT/name;grid=json.loads((out/'grid.json').read_text());checks=[]
 for line in (out/'checks.txt').read_text().splitlines()[1:]:
  check=json.loads(line);n,c=check['frame'].rsplit('_f',1);c=int(c)
  a=np.array(Image.open(out/'frames'/f'{n}_f{c}.png'));m=a[:,:,3]>0
  gap=np.zeros_like(m);gap[:,1:-1]=~m[:,1:-1]&m[:,:-2]&m[:,2:];count=0
  for x in range(192):
   l,k=ndi.label(gap[:,x]);ss=np.bincount(l)[1:];count+=int(ss[ss>=4].sum())
  check['long_one_texel_seam_pixels']=count;assert count==0
  check['connected_components']=ndi.label(m,structure=np.ones((3,3)))[1]
  checks.append(check)
  cell=next(v for v in grid['cells'] if v['view']==n and v['frame']==c)
  cell['generated_placement']=cell['placement'];cell['final_opaque_box']=list(Image.fromarray(a).getbbox())
  if check['exact_still_required']:
   cell['placement']=[16,20];cell['source_override']='exact approved 160x160 still'
  elif name=='pop_out' and c==0:
   cell['placement']=[16,151-REFS[n].getbbox()[1]];cell['source_override']='native top 10 ear-tip rows; clipped y160'
  elif name=='dig' and c==5:
   cell['placement']=[91,155];cell['source_override']='native gold-cream tail tip, rigid 90-degree rotation; clipped y160'
  else:cell['native_part_placement_logs']=['../native_finish_log.txt','../detail_finish_log.txt','../tail_finish_log.txt']
 grid['raw_sha256']=hashlib.sha256((out/'sheet_raw.png').read_bytes()).hexdigest()
 grid['grid_clean']=verification['animations'][name]['grid_clean']
 grid['source_grid_note']='Clean gutters.' if grid['grid_clean'] else 'Four cell-edge contacts: late death tail tips overlap preceding columns. Native straight tails replace truncated source tails in f4-f6. No redo.'
 grid['scale_note']='One conversion factor per row, calibrated from seated source endpoint. No per-frame fitting. Restored native parts never resized.'
 (out/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
 (out/'checks.txt').write_text('Approved still at (+16,+20); IoUs count opaque union; long one-texel seam = vertical run >=4.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 allchecks[name]=checks
verification['checks']=allchecks
verification['long_one_texel_seam_pixels']=0
verification['source_grid_note']='dig/pop_out clean; death has four source cell-edge contacts repaired with native straight tails.'
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
pa=verification['palette_edge_audit']
(ROOT/'palette.txt').write_text('hex opaque_pixels edge_pixels fraction_of_colour_on_edge\n'+'\n'.join(f"#{h} {v['opaque_pixels']} {v['edge_pixels']} {v['edge_pixels']/max(1,v['opaque_pixels']):.6f}" for h,v in pa.items())+'\n')
lines=[
'FENNEC S / TAKE B / CODEX SET D / 2026-11-04',
'36 transparent 192x192 native-scale frames: dig 12, pop_out 10, death 14; se then ne.',
'Built-in image tool: exactly 3 sheets, one per move, se_6x.png then ne_6x.png attached; no redo. Tokens used: unavailable.',
'Adapted set B finish/polish/final_pass/verify and set A seam/details/finalize methods; prompts retain all set B column descriptions verbatim.'
]
for name in COUNTS:
 s=verification['animations'][name]
 lines.append(f"{name}: sheet {s['raw_size']}; SHA256 {s['raw_sha256']}; grid clean={s['grid_clean']}; cut contacts={s['source_cut_contacts']}.")
lines += [
'Death source grid defect: late f4/f5 tails overlap preceding columns in both rows. Native straight tail pieces repair final f4-f6; original sheet retained.',
'Per row one fixed generated-to-native conversion; no individual pose fitting. Native heads, eyes/muzzles, ear tips, discs and repaired tails are unscaled copies.',
'Exact stills at (+16,+20): dig se_f0/ne_f0, death se_f0/ne_f0, pop_out se_f4/ne_f4: silhouette IoU=1.0 AND exact-colour IoU=1.0 for EACH.',
'36/36: approved palette only, binary alpha, no below-y160 pixels, no canvas-edge contacts, no tiny debris, no enclosed holes, no long one-texel seams.',
'Lowest row: pop_out se_f2/ne_f2=145; every other frame=160. Ear-tip-only pop_out f0 and dig f3-f5 clipped at y160.',
'6/6 GIFs reopened: exact logical frame counts and requested durations; one-shot; death final hold=1400ms. grid.json records every duration and placement.',
'dig by eye: same fennec both rows; rise/dig/dive/rump/tip phases match each other and B front/side/back columns; se face/near eye and ne ear backs retained, no mirroring; limbs remain short.',
'pop_out by eye: same fennec both rows; native ear tips, emerge, airborne, four-foot landing, seated recovery match B beats; both retain their still angles without mirroring; no limb elongation.',
'death by eye: same fennec both rows; recoil, outward rigid-ear droop, buckle, side slump, dark-eye hold match B beats; se face and ne rear head remain angled, no mirroring; limbs fold without elongation.',
'Looked at all final boards beside approved stills and B boards. Repaired head/ear drift, native eye/muzzle plates and discs, underground clipping, truncated tails, seams and final eye highlights.',
'Changed-pose armour contours and drooped ears retain minor generated drawing variation; changed poses are not pixel-identical to stills. Tails stay straight.',
'Palette edge counts in palette.txt and verification.json include the requested near-black #141218 outline; zero magenta/background colours remain.',
'Deliverables per move: sheet_raw.png, slices/, frames/, grid.json, checks.txt, preview_se.gif, preview_ne.gif, review.png, review_small.png, detail_board.png, detail_small.png.',
'Rebuild: python finish.py; python polish.py; python details.py; python seam_fill.py; python final_pass.py; python verify.py; python finalize.py.',
'Only codex-set-d written by these scripts. Built-in generator used its managed cache; retained outputs copied here. Sibling codex-set-c untouched. No install or commit.'
]
assert len(lines)<30
(ROOT/'REPORT.txt').write_text('\n'.join(lines)+'\n')
print('Finalized',len(lines),'report lines; metadata and independent seam checks complete.')
