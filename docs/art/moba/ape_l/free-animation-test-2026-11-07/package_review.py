from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil,hashlib,math
R=Path('D:/dev/_scratch/gorilla-free-animation')
O=Path('D:/dev/new-mech-rpg/docs/art/moba/ape_l/free-animation-test-2026-11-07')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
def frame(f):
    im=Image.new('RGB',(1200,1020),'#111a23');d=ImageDraw.Draw(im)
    d.text((24,14),'FREE CC0 MOTION TEST | Attack | 1.03 seconds',font=font,fill='#dceaf0')
    d.text((24,50),'Older local gorilla rig. Latest power-gorilla model is not available locally.',font=small,fill='#aabac7')
    for row,kind in enumerate(['gorilla','donor']):
        y=90+row*450
        title='LEGACY GORILLA: right-arm transfer + floor correction' if kind=='gorilla' else 'CC0 KAIJU DONOR: original attack (not a gorilla)'
        d.text((20,y),title,font=small,fill='#9ce0b5' if row==0 else '#e6c48c')
        for col,view in enumerate(['threequarter','side']):
            im.paste(Image.open(R/'renders'/kind/view/f'{f:03d}.png').convert('RGB'),(col*600,y+30))
    d.text((22,995),f'Frame {f:02d}/31 | fixed support hand + feet | rigid single-bone armor | unapproved experiment',font=small,fill='#bbcbd5')
    return im
frames=R/'video-frames';frames.mkdir(exist_ok=True)
seq=([0]*12+list(range(32))+[31]*14)*3
for i,f in enumerate(seq):frame(f).save(frames/f'{i:04d}.png')
board=Image.new('RGB',(1500,1080),'#111a23');d=ImageDraw.Draw(board)
d.text((20,14),'Attack samples: legacy gorilla / source donor',font=font,fill='white')
for col,f in enumerate([0,8,16,24,31]):
    d.text((col*300+15,58),f'{f/30:.2f}s',font=small,fill='white')
    for row,(kind,view) in enumerate([('gorilla','threequarter'),('gorilla','side'),('donor','threequarter'),('donor','side')]):
        im=Image.open(R/'renders'/kind/view/f'{f:03d}.png').convert('RGB');im.thumbnail((300,230));board.paste(im,(col*300,90+row*240))
board.save(O/'attack-contact-sheet.png')
data=json.loads((O/'contact-samples.json').read_text());summary={}
for name in ['hand.L','hand.R','foot.L','foot.R']:
    centers=[x[name]['center'] for x in data]
    summary[name]={'lowest_z_m':min(x[name]['min_z'] for x in data),'highest_min_z_m':max(x[name]['min_z'] for x in data),'max_center_displacement_m':max(math.dist(c,centers[0]) for c in centers)}
summary['armor_weight_check']='41,510 vertices, each assigned to exactly one bone; no scaling animated'
summary['sampling']='32 integer frames at 30fps; not a continuous collision or engine check'
(O/'verification.json').write_text(json.dumps(summary,indent=2))
for script in ['build_test.py','fetch_and_inspect.py','package_review.py']:
    shutil.copy2(R/script,O/script)
shutil.copy2(R/'local-model-inspection.json',O/'local-model-inspection.json')
p=Path('D:/dev/new-mech-rpg/docs/art/3d/ape_l_v2.blend')
(O/'target-manifest.json').write_text(json.dumps({'target':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rig_bones':14,'design':'legacy October gorilla, not take-b-power','donor_clip':'Attack','transfer':'world rotation changes relative to source first pose; right upper arm, forearm and hand only; 70% rotation; minimal floor-safe shoulder pitch; other bones at rest','source_duration_seconds':1.0333333,'fps':30,'frames':32,'output_blend':'legacy-gorilla-attack-test.blend','output_video':'free-attack-test.mp4'},indent=2))
print(json.dumps(summary,indent=2))
