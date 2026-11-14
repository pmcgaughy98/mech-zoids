"""Review boards and requested lane commands, all outputs inside run2."""
import sys
sys.dont_write_bytecode=True
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
import build as m
R=m.R
def reviews():
    checks=json.loads((R/'verification.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    for v in ['s','n']:
        box=(48,110,144,166);board=Image.new('RGB',(1440,930),(65,73,80));d=ImageDraw.Draw(board)
        paths=[R/f'stills/{v}.png']+[R/f'walk/frames/{v}_f{f}.png' for f in range(8)]
        for i,p in enumerate(paths):
            a=Image.open(p).convert('RGBA');outlined=Image.fromarray(m.b.load_selout()(m.np.array(a))[0]);tile=outlined.crop(box).resize((480,280),Image.Resampling.NEAREST)
            x=(i%3)*480;y=(i//3)*310;board.paste(tile,(x,y+25),tile);d.text((x+8,y+3),v+' '+('STILL' if i==0 else f'f{i-1}'),font=font,fill='white')
        board.save(R/f'{v}_audit5x.png')
        # Flag exact raw pixels for review; no flagged gap is filled.
        flags=Image.new('RGB',(1440,930),(65,73,80));d=ImageDraw.Draw(flags)
        for i,p in enumerate(paths):
            a=Image.open(p).convert('RGBA')
            if i:
                for x,y in checks[v]['structure'][i-1]['seams']:a.putpixel((x,y),(255,50,50,255))
            tile=a.crop(box).resize((480,280),Image.Resampling.NEAREST);x=(i%3)*480;y=(i//3)*310;flags.paste(tile,(x,y+25),tile);d.text((x+8,y+3),v+' '+('STILL' if i==0 else f'f{i-1}'),font=font,fill='white')
        flags.save(R/f'{v}_seams_review.png')
def commands():
    tool=R.parents[1]/'tools/walk_tools.py'
    common=['--targets',str(R/'targets.json'),'--frames',str(R/'walk/frames'),'--views','s','n','--still-dir',str(R/'stills')]
    logs=[]
    for mode,extra in [('footlock',['--out',str(R/'footlock.json')]),('seams',['--body','a990e0','7258b4','4a347e','26183f'])]:
        cmd=[sys.executable,'-B',str(tool),mode]+common+extra
        p=subprocess.run(cmd,capture_output=True,text=True,cwd=R)
        text='COMMAND '+' '.join(cmd)+'\n'+p.stdout+p.stderr+f'EXIT {p.returncode}\n';logs.append(text)
        (R/f'{mode}_tool.txt').write_text(text);print(text)
        if p.returncode:raise RuntimeError(mode)
    with (R/'checks.txt').open('a') as out:out.write('\n'+'\n'.join(logs))
if __name__=='__main__':reviews();commands()
