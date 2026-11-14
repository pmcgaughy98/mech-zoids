from pathlib import Path
import json,hashlib,math
from PIL import Image
import numpy as np
R=Path(r'D:/dev/new-mech-rpg/docs/art/moba/wolf_m/take-b/anim/codex-walk2')
g=json.loads((R/'grid.json').read_text());g['raw_sha256']=hashlib.sha256((R/'sheet_raw.png').read_bytes()).hexdigest();g['generation_calls']=1;g['approved_reference']='../../fixed/e.png';g['reference_order']=['refs/e_6x.png','pose_guide.png'];g['finishing']='Each complete generated cell extracted at common0.447 scale; generated cell4 upper drawing held steady throughout, no approved still pixels pasted. Whole legs and four-plate tail redrawn with native contours and integer articulated joint corrections.'
for cell in g['cells']:
 f=cell['frame'];cell['final_upper_generated_source_cell']=4;cell['final_path']=f'walk/frames/side_f{f}.png';cell['final_bbox']=list(Image.open(R/cell['final_path']).getbbox());cell['duration_ms']=100;cell['body_dip']=int(f in [1,5]);cell['head_steady']=True
(R/'grid.json').write_text(json.dumps(g,indent=2)+'\n')
p=json.loads((R/'proportions.json').read_text());v=json.loads((R/'verification.json').read_text())
shapes=[(c['bbox'][2]-c['bbox'][0],c['bbox'][3]-c['bbox'][1]) for c in v['structural']]
checks=(R/'checks.txt').read_text();checks+='PROPORTIONS PASS: projected upper axes max change0.854px; all32 rounded leg chains and upper/lower links within2px; max whole-chain change1.708px.\n'
checks+='Tail PASS:4 plates including red tip; straight axis36.228px, reference36.228; widths10.95/12.95/10.95px vs reference12.15/12.15/10.95 (max1.20px). Rigid1px lateral sway, no curvature.\n'
checks+='Head PASS: native x130..191,y0..131 region pixel-identical across eight frames. Torso dip1px atf1/f5.\n'
checks+=f'Actual whole silhouette sizes: {shapes}; still110x66.\n'
(R/'checks.txt').write_text(checks)
report='''WOLF M TAKE B / CODEX WALK2 / SIDE TROT / 2026-11-04
Tokens used: unavailable. Built-in image tool: exactly ONE sheet call, no redo. Actual prompt: prompt.txt.
All task-authored files are in codex-walk2; other animation folders, assets and tools untouched; no commit.
Inputs: approved fixed/e.png identity through refs/e_6x.png; Python pose_guide.png attached second. No views/ inputs.
Measured still paw centers: near fore114, far fore120, near hind68, far hind79. Far sole row158 normalized to gameplay row160.
8 transparent192x192 frames,100ms each, looping. Raw sheet2172x724 retained as sheet_raw.png.
Method: common0.447 native extraction; generated cell4 whole upper held steady; complete joined legs/tail redrawn at native pixels, palette snapped. No still parts pasted.
TABLE PASS32/32: measured sole-center x error0px, lift error0px. Full per-paw/per-frame values in checks.txt and verification.json.
PAIR A ground f0-3: near fore x122,117,112,107; far hind87,82,77,72. Recovery: -4/-1/+2/+5, lift2/4/4/2.
PAIR B ground f4-7: far fore x128,123,118,113; near hind76,71,66,61. Recovery: -4/-1/+2/+5, lift2/4/4/2.
FOOT LOCK PASS at0.90m/s: +5 bodypx/frame cancels each planted paw's -5px/frame. Both supplied commands run.
Near fore ground world x122/122/122/122: spread0px. Far hind87/87/87/87: spread0px.
Far fore ground world x148/148/148/148: spread0px. Near hind96/96/96/96: spread0px.
Each corresponding pixel of the11px sole locks too; max spread at the diagnostic's actual stamp instants0px across10cycles.
FILE PASS8/8: approved12-colour palette, binary alpha, bottom160, below160=0, edge contacts0, connected body1, holes0, strays0.
PROPORTIONS PASS measured projected axes/joint chains: whole silhouette109-111x66 vs still110x66; upper-axis max change0.854px; leg-chain max1.708px.
All32 upper/lower leg links also within2px of reference; native7px near shanks/6px far shanks. Details: proportions.json, articulation.json.
TAIL PASS:4 broad plates incl red tip; straight36.228px axis vs36.228; widths10.95/12.95/10.95 vs12.15/12.15/10.95 (max1.20px); rigid1px sway.
HEAD PASS: pixel-steady across all8; body dips1px atf1/f5; head unaffected.
BOARD: approved still, set A row, new row; supplied selout() with OUTLINE#141418, nearest4x. Eye review used this ordered board.
EYE: reads as a low robot-wolf forward trot; diagonal pairs together, paws move back under body, no high prancing. Whole connected legs and tail; no cutoffs.
GIF reopened:8 frames,100ms each, loop0. preview.gif; check_old/new.png and .mp4; board.png. No live-player review claimed.
'''
assert len(report.splitlines())<30
(R/'REPORT.txt').write_text(report)
print('Report lines',len(report.splitlines()),'sizes',shapes)
print('Required files:')
for name in ['sheet_raw.png','pose_guide.png','grid.json','checks.txt','preview.gif','board.png','REPORT.txt','check_old.png','check_old.mp4','check_new.png','check_new.mp4']:
 p=R/name;assert p.is_file();print(name,p.stat().st_size)
print('Frames',len(list((R/'walk/frames').glob('side_f*.png'))))
