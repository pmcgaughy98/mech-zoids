from finish import *
v=json.loads((ROOT/'verification.json').read_text());lines=[
'APE L / CODEX SET C / 2026-11-04',
'54 transparent native-scale 192x192 frames: idle 10, walk 16, chest_beat 16, hex_shield 12.',
'Tokens used: unavailable. Built-in imagegen: exactly ONE sheet per requested move (3 calls); no redo; NO generated idle.',
'Method: copied/adapted A/B finish, polish, gems, final_pose, seam_fill, gem_cleanup, verify; refs attached se_6x then ne_6x.',
'Prompts retain each original column description verbatim and use the requested two-row layout.']
for name in ['walk','chest_beat','hex_shield']:
 s=v['animations'][name];g=json.loads((ROOT/name/'grid.json').read_text())
 lines.append(f"{name}: sheet {s['raw_size'][0]}x{s['raw_size'][1]}, SHA256 {s['raw_sha256']}")
 lines.append(f"{name} grid: correct 2x{COUNTS[name]}; NOT pristine raw (saturated fringe debris/tight gutters); no main-component cut contacts; cleaned slices separate.")
lines += [
'Idle sheet_raw.png is a labelled-in-grid native contact sheet, not a generated source; 960x384, SHA256 '+v['animations']['idle']['raw_sha256'],
'Idle lifts upper body 0,1,2,1,0 px; native lower contacts fixed. Walk uses native approved part masks and the generated diagonal action plan.',
'Walk: planted support coordinates fixed per phase; swing pairs lift 2/3/1 px. SE far support gauntlet extends down 2 px in f4-f7 to ground row160.',
'All frame0s and chest_beat/hex_shield final frames: exact approved still at (+16,+30), silhouette AND exact-colour IoU 1.000000 for se and ne.',
'54/54: 15 approved opaque colours only; binary alpha; lowest row160; zero below-ground pixels, edge contacts, tiny stray components or enclosed transparent holes.',
'Set B seam-run and flood-fill hole checks applied. Per-frame found/filled counts in checks.txt and seam_log.json; native face/back-gem and gauntlet gem/bezel patches restored.',
'All 8 GIFs verified frame-by-frame against requested durations; loop enabled. Approved still is leftmost in each review.png row.',
'Viewed final boards against approved stills and set A front/side/back boards; no effects in final frames.',
'Idle by eye: same gorilla in both rows; matching breath, native limb lengths; se down-right and ne up-right throughout, neither straight nor mirrored.',
'Walk by eye: same gorilla; diagonal swing/bob matches set A phases column for column; native short limbs; three-quarter directions stay locked, no mirroring.',
'Chest beat by eye: same gorilla; rise, alternating f2/f3/f4 beats, lower and native settle match set A beats. NE alternation is partly occluded and less legible than SE.',
'Chest beat angles remain three-quarter front/back, not straight or mirrored; frame1 rise is milder than set A. No obvious limb elongation; raised armour contours vary slightly.',
'Hex shield by eye: same gorilla; lift, wind-back f2, forward release f3, retract f4 match set A columns; se/ne angles maintained, not straight or mirrored; short heavy arms retained.',
'Visual limitation: generated ability armour/gauntlet contours vary modestly from the stills during extreme poses despite native palette, face, gem and bezel restoration.',
'Rebuild in order: python finish.py; python polish.py; python gems.py; python final_pose.py; python seam_fill.py; python gem_cleanup.py; python verify.py; python report.py.',
'All deliverables confined to codex-set-c; no sibling, asset installation or commit. Bound/hex_dome/death belong to the other job and are not generated here.'
]
assert len(lines)<30
(ROOT/'REPORT.txt').write_text('\n'.join(lines)+'\n')
print('REPORT.txt',len(lines),'lines')
