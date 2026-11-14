import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;R1=R.parent/'run1'
sys.path.insert(0,str(R1));import build as old
b=old.b;Y,X=old.Y,old.X;load=old.load
GOLD=['fff4d6','f0d27a','b8923a']
def gold(a):return np.logical_or.reduce([np.all(a[:,:,:3]==list(bytes.fromhex(h)),axis=2)&(a[:,:,3]>0) for h in GOLD])
def save(a,p):Image.fromarray(a).save(R/p)
def report(s):
 p=R/'REPORT.txt';p.write_text(p.read_text()+s+'\n')
def layers(v,f):return {n:load(R1/f'walk/layers/{v}_{n}_f{f}.png') for n in ['LH','LF','RH','RF']}
def repair_ne():
 ref,parts,body,tail=old.sources('ne');counts=[];changes=[]
 for f in range(8):
  prev=load(R1/f'walk/frames/ne_f{f}.png');ll=layers('ne',f);a=np.zeros_like(ref)
  for n in ['LH','LF']:b.comp(a,ll[n])
  b.comp(a,b.shift(tail,0,int(f in [1,5])));b.comp(a,b.shift(body,0,int(f in [0,4])))
  for n in ['RH','RF']:b.comp(a,ll[n])
  # Only replace the defective tail/upper far-hind area. Preserve run1 joins elsewhere.
  region=(X>=58)&(X<=100)&(Y>=124)&(Y<=149)
  out=prev.copy();out[region]=a[region]
  # Restore closed socket paint without filling open spaces between feet.
  holes=b.fill_holes(out[:,:,3]>0)&(out[:,:,3]==0)
  st=b.shift(ref,0,int(f in [0,4]))
  for yy,xx in zip(*np.where(holes)):
   out[yy,xx]=prev[yy,xx] if prev[yy,xx,3] else (st[yy,xx] if st[yy,xx,3] else old.P['2e1a6e'])
  save(out,f'walk/frames/ne_f{f}.png')
  counts.append(int((np.logical_or.reduce([np.all(out[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['e0c8ff','a46bff']])&(X>=58)&(X<=91)&(Y>=128)&(Y<=149)).sum()))
  changes.append(int(np.any(out!=prev,axis=2).sum()))
  for n in ll:save(ll[n],f'walk/layers/ne_{n}_f{f}.png')
 print('ne light counts',counts,'changed',changes)
 report('Part 1 ne: far LH/LF, whole native tail, pinned body, near RH/RF; foot layers unchanged.')
 report('ne tail light pixels in x58-91/y128-149 f0-7: '+str(counts)+'; threshold 63 '+('PASS' if min(counts)>=63 else 'FAIL')+'.')
 return counts

def repair_e():
 ref,parts,body,tail=old.sources('e');rig=json.loads((R1/'rig.json').read_text())['e']
 # Recover the fixed chest plate, with a native-colour continuation beneath the shoulder.
 # Its right silhouette, row bands, and seam come from the still.
 plate=np.zeros_like(ref)
 for y,lo,hi in [(129,117,120),(130,115,122),(131,114,123),(132,114,123),(133,114,123),(134,114,123),(135,114,122),(136,114,121),(137,114,121),(138,115,120),(139,115,119),(140,116,118),(141,116,118)]:
  for x in range(lo,hi+1):
   c=ref[y,x]
   if gold(ref)[y,x] or (x>=119 and c[3]):plate[y,x]=c
   else:plate[y,x]=old.P['f0d27a'] if y<138 else tuple(bytes.fromhex('b8923a'))+(255,)
  plate[y,lo-1]=old.P['141218']
 # Native highlight/base/shadow rows continued into the uncovered left edge.
 plate[132,116:119]=old.P['fff4d6'];plate[133,116:118]=old.P['f0d27a']
 save(plate,'source/e_chest.png');sizes=[]
 for f in range(8):
  prev=load(R1/f'walk/frames/e_f{f}.png');out=prev.copy();ll=layers('e',f);dip=int(f in [0,4])
  # The native knee extraction had included shadow-gold chest pixels. Remove those
  # from both the near knee and its reconstructed far counterpart at their moved positions.
  affected=np.zeros((192,192),bool)
  for n in ['RF','LF']:
   m=gold(ll[n]);affected|=m
   for yy,xx in zip(*np.where(m)):
    ll[n][yy,xx]=old.P['2e1a6e']
  fresh=np.zeros_like(ref)
  b.comp(fresh,b.shift(tail,0,int(f in [1,5])))
  for n in ['LF','LH']:b.comp(fresh,ll[n])
  b.comp(fresh,b.shift(body,0,dip));b.comp(fresh,b.shift(plate,0,dip))
  for n in ['RF','RH']:b.comp(fresh,ll[n])
  pm=b.shift(plate,0,dip)[:,:,3]>0;affected|=pm
  out[affected]=fresh[affected]
  # Remove only isolated gold remnants from the shoulder's former moving paint.
  pieces=b.pieces(gold(out));chestpcs=[c for c in pieces if any(110<=x<=130 and 129+dip<=y<=143+dip for y,x in c)]
  chestpcs.sort(key=len,reverse=True)
  for c in chestpcs[1:]:
   for y,x in c:out[y,x]=old.P['2e1a6e']
  out[:131+dip]=prev[:131+dip]
  save(out,f'walk/frames/e_f{f}.png');sizes.append([len(c) for c in b.pieces(gold(out))])
  for n in ll:save(ll[n],f'walk/layers/e_{n}_f{f}.png')
 print('e gold pieces',sizes)
 report('Part 2 e: pinned native chest bands/seam continued behind front shoulder; moving knee gold contamination removed.')
 report('e gold components f0-7: '+str([len(s) for s in sizes])+'; minimum piece '+str(min(min(s) for s in sizes))+'px; '+('PASS' if all(len(s)==4 and min(s)>4 for s in sizes) else 'FAIL')+'.')

def repair_board():
 bg=(92,94,101,255);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
 board=Image.new('RGBA',(9*230,4*230),bg)
 for row,(v,run,box) in enumerate([('ne',R1,(57,123,103,163)),('ne',R,(57,123,103,163)),('e',R1,(104,126,140,161)),('e',R,(104,126,140,161))]):
  for j in range(9):
   a=load(R/f'stills/{v}.png') if j==0 else load(run/f'walk/frames/{v}_f{j-1}.png')
   tile=Image.fromarray(a).crop(box);tile=tile.resize((tile.width*5,tile.height*5),Image.Resampling.NEAREST)
   board.alpha_composite(tile,(j*230,row*230+25));ImageDraw.Draw(board).text((j*230+3,row*230+3),f'{v} '+('run1' if run==R1 else 'run2')+' '+('still' if not j else f'f{j-1}'),font=font,fill='white')
 board.convert('RGB').save(R/'repairs.png')
if __name__=='__main__':
 if sys.argv[1]=='ne':repair_ne()
 if sys.argv[1]=='e':repair_e();repair_board()
