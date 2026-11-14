from finish import *
def detail(name):
 N=COUNTS[name];canvas=Image.new('RGB',((N+1)*400,2*440+40),'#656d78');d=ImageDraw.Draw(canvas)
 d.text((8,8),f'{name} / native pixels 4x / cyan y160',fill='white')
 for r,n in enumerate(NAMES):
  for c in range(-1,N):
   fr=approved(n) if c==-1 else Image.open(ROOT/name/'frames'/f'{n}_f{c}.png')
   tile=fr.crop((40,60,140,164)).resize((400,416),Image.Resampling.NEAREST);x=(c+1)*400;y=48+r*440
   canvas.paste(tile,(x,y),tile);d.text((x+5,y-15),f'{n} STILL' if c==-1 else f'{n} f{c}',fill='white');d.line((x,y+404,x+399,y+404),fill='#55cccc')
 canvas.save(ROOT/name/'detail_board.png');canvas.resize((min(2000,canvas.width),round(canvas.height*min(2000,canvas.width)/canvas.width)),Image.Resampling.NEAREST).save(ROOT/name/'detail_small.png')
def tails_and_eyes(name):
 if name!='death':return
 logs=[]
 for n in NAMES:
  box=(48,128,74,141) if n=='se' else (51,128,80,141)
  tail=REFS[n].crop(box)
  for c in [4,5,6]:
   path=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr);bb=fr.getbbox()
   # Source late columns overlap; replace their truncated tail with one rigid native piece.
   tx=bb[0]-2;ty=148
   a[148:161,:tx+tail.width-3]=0;fr=Image.fromarray(a);fr.alpha_composite(tail,(tx,ty));fr=clean(clipped(fr));a=np.array(fr)
   if c==6:
    for j in [11,12,14]:a[np.all(a[:,:,:3]==PAL[j],2)&(a[:,:,3]>0),:3]=PAL[2]
   Image.fromarray(a).save(path);logs.append(f'{n}_f{c}: native straight tail {box} at {tx},{ty}; final eyes dark={c==6}')
 (ROOT/'tail_finish_log.txt').write_text('\n'.join(logs)+'\n')

if __name__=='__main__':
 import sys
 for name in sys.argv[1:] or COUNTS:tails_and_eyes(name);board(name);detail(name)
