"""Revision 4 schematic generated from the native scene's exported geometry."""
import json, math, pathlib
from PIL import Image, ImageDraw, ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/plan/foundry-5v5-2026-11-11-open-bosses'
data=json.loads((OUT/'layout.json').read_text())
review=json.loads((OUT/'native-review.json').read_text())
rotation=review['metrics']['objective_rotation']
im=Image.new('RGB',(1510,1180),'#111923');d=ImageDraw.Draw(im)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
def p(v):return (500+v[0]*3.8,590+v[1]*3.8)
def label(x,y,s,n=23,fill='#d4dde2'):d.text((x,y),s,font=font(n),fill=fill)
def box(center,size,fill,outline=None,yaw=0):
    x,z=center;w,h=size;c=math.cos(yaw);s=math.sin(yaw)
    pts=[p((x+u*c+v*s,z-u*s+v*c)) for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
    d.polygon(pts,fill=fill,outline=outline,width=2)
label(55,22,'FOUNDRY  /  OPEN BOSS APPROACHES',35,'#f0b855')
label(55,68,'November 11, 2026  |  Native scene geometry  |  Proposed 5v5 training layout',21)
box((0,0),[v*2 for v in data['half_size']],'#293339','#6b7d86')
for link in data['connectors']:
    d.line([p(v) for v in link['points']],fill='#52686c',width=round(link['width']*3.8),joint='curve')
for points in data['routes'].values():
    d.line([p(v) for v in points],fill='#879396',width=round(14*3.8),joint='curve')
    d.line([p(v) for v in points],fill='#394348',width=round(5.4*3.8),joint='curve')
for b in data['blockers']:box(b['center'],b['size'],'#0d1923','#354d5a',b.get('yaw',0))
for z,col in [(-102,'#93483f'),(102,'#25628b')]:
    x,y=p((0,z));r=17*3.8;d.ellipse((x-r,y-r,x+r,y+r),fill=col,outline='#a5b8c4',width=2)
for name,site in data['sites'].items():
    x,y=p(site['center']);r=site['radius']*3.8
    boss='GOLD' in name or 'WYVERN' in name
    col='#e8b64e' if 'GOLD' in name else ('#ad8ae9' if 'WYVERN' in name else '#b6c2c7')
    d.ellipse((x-r,y-r,x+r,y+r),fill='#263139',outline=col,width=3)
    if boss:
        text='BEETLE' if 'GOLD' in name else 'WYVERN';f=font(15)
        bounds=d.textbbox((0,0),text,font=f);d.text((x-(bounds[2]-bounds[0])/2,y-10),text,font=f,fill=col)
for ports in data['ports'].values():
    for v in ports.values():
        x,y=p(v);d.ellipse((x-5,y-5,x+5,y+5),fill='#f3f6e8')
for team,points in data['spawns'].items():
    for v in points:
        x,y=p(v);d.ellipse((x-4,y-4,x+4,y+4),fill='#54b8ff' if team=='blue' else '#ff7664')
label(980,145,'OPEN MID / JUNGLE FACES',25,'#f0b855')
for i,s in enumerate(['Beetle: west inner jungle','Wyvern: east inner jungle','Both between mid and outer lanes',f"Gate-to-gate walk: {rotation['between_seconds']:.1f} s"]):label(980,195+i*37,s,21)
label(980,395,'PLACEMENTS WITH A JOB',25,'#f0b855')
for i,s in enumerate(['Boss courts inside outer lanes','Broad mid-facing boss openings','North/south jungle connections','Four camp loops with return paths','Home roads behind jungle islands','Lane-side scouting recesses']):label(980,445+i*37,s,20)
label(980,710,'DRAFT / PLAYABLE FOUNDATION',24,'#f0b855')
for i,s in enumerate(['220 x 240 m footprint','14 m marked lanes; 7-12 m links','Walk speed: 3.5 m/s; no abilities','Current respawn: 8 s placeholder','Boss models are static previews','Clear times and rewards unbuilt']):label(980,760+i*37,s,20)
label(55,1094,'NORTH: RED  /  SOUTH: BLUE     Light routes: lanes   Dark masses: cover   White dots: boss entries',20)
label(55,1130,'Travel times measured on baked navigation with physics clearance checks. Match balance still needs real boss encounters.',19,'#94a7b3')
im.save(OUT/'layout-board.png')
print(OUT/'layout-board.png')
