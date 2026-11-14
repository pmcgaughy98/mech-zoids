"""Report retained sheets and verified results, without generating any images."""
from finish import *
v=json.loads((ROOT/'verification.json').read_text())
lines=[
'APE L / CODEX SET D / 2026-11-04',
'50 transparent native-scale 192x192 frames: bound 18, hex_dome 16, death 16; views se/ne.',
'Tokens used: unavailable. Exactly THREE built-in image calls, ONE sheet per move; no redo or failed call.',
'Copied and adapted set B finish.py, polish.py, gems.py, final_pose.py, seam_fill.py, gem_cleanup.py and verify.py; read set A method.',
'Prompts preserve set B column descriptions verbatim and use the requested two-row layout; refs attached se_6x then ne_6x.'
]
for name,a in v['animations'].items():
 g=json.loads((ROOT/name/'grid.json').read_text())
 lines.append(f"{name}: sheet {a['raw_size'][0]}x{a['raw_size'][1]}, clean 2x{COUNTS[name]} grid, zero cut contacts; SHA256 {a['raw_sha256']}")
lines += [
'Cuts use empty gutters per row; grid.json records all cuts, fixed row factors, source bounds, placement, final bounds and lifts.',
'No independent per-pose resizing. Approved native face/eye, back-gem and gauntlet-gem/bezel patches fitted inside generated silhouettes.',
'All 50: approved 15-colour palette only, binary alpha, zero pixels below row160, zero edge contacts and zero tiny stray components.',
'All frame0s and bound/hex_dome final frames equal approved stills at (+16,+30): silhouette AND exact-colour IoU 1.000000 in both views.',
'Bound f3/f4/f5 bottom rows 144/132/148: exact lifts 16/28/12. All other frames bottom row160.',
'Set B seam-run check and enclosed-hole flood fill run; zero remaining seams or enclosed holes in any frame, including exact endpoints.',
'checks.txt records per-frame geometry, colours, alpha, IoU and holes/seams found and filled; all six GIF frame counts/timings verified.',
'Viewed all final two-view boards against approved stills and set B boards. Approved still is at the left of each review row.',
'Corrected bound gauntlet clipping with row-specific cuts; restored opaque cap highlights; fixed misplaced prone face patch.',
'Bound by eye: same gorilla in both rows; crouch/push/rise/peak/fall/low two-fist landing/recovery match column by column and set B beats.',
'Hex dome by eye: same gorilla; both fists overhead in f2/f3, together down into f5, recovery; two rows and set B beats match.',
'Death by eye: same gorilla; recoil/stagger/buckle/forward sink/prone progression matches rows and set B; f7 body settles 1px with contacts fixed.',
'Death f6/f7: face eyes use approved darkest faceplate grey; gauntlet and back gems stay green.',
'Angles by eye: se stays down-right with asymmetric face/eyes; ne stays up-right with back gem and head away; no straight-view switch or mirror.',
'Limbs by eye: short heavy proportions retained, with no obvious length stretch. Extreme poses retain small generated armour-contour differences.',
'No effects. Raw sheets, slices, prompts, refs, frames, grids, checks, GIFs, review boards and adapted scripts retained in codex-set-d.',
'Rebuild: finish.py; polish.py; gems.py; final_pose.py; seam_fill.py; gem_cleanup.py; verify.py; report.py.',
'All requested deliverables are inside codex-set-d. No sibling, assets or art changes; no commit.'
]
assert len(lines)<30
(ROOT/'REPORT.txt').write_text('\n'.join(lines)+'\n')
print('REPORT.txt:',len(lines),'lines')
