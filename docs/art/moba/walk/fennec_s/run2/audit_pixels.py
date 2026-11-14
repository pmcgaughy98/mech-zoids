exec(open('bootstrap.py',encoding='utf-8-sig').read().split("for d in")[0])
chars={'141218':'#','211e27':'o','2e1a6e':'D','3d3a44':'c','6a3cc8':'v','9d9ba2':'g','a46bff':'V','d6d6dc':'S','e0c8ff':'L','f0d27a':'Y','fff4d6':'H','b8923a':'y','ffffff':'W','57ffb5':'t','00bf83':'t'}
for v in ['s','n','e']:
 a=old.load(R/f'stills/{v}.png');print('\n',v)
 x0,x1=(78,114) if v!='e' else (106,131)
 print('    '+''.join(str(x//10%10) for x in range(x0,x1)));print('    '+''.join(str(x%10) for x in range(x0,x1)))
 for y in range(119,164):print(str(y)+' '+''.join('.' if not a[y,x,3] else chars.get(bytes(a[y,x,:3]).hex(),'?') for x in range(x0,x1)))

