exec(open('bootstrap.py',encoding='utf-8-sig').read().split('for d in')[0])
for v in ['s','n']:
 a=old.load(R/f'stills/{v}.png');print(v)
 for y in [130,134,138,140,142,146,147,148,149,150,154,159,160]:
  print(y,' '.join(f'{x}:{bytes(a[y,x,:3]).hex()}' for x in range(78,114) if a[y,x,3]))
