from repair import *
chars={tuple(bytes.fromhex(c)):k for c,k in [('141218','#'),('211e27','d'),('2e1a6e','v'),('3d3a44','g'),('6a3cc8','P'),('9d9ba2','s'),('a46bff','L'),('b8923a','b'),('d6d6dc','w'),('e0c8ff','h'),('f0d27a','Y'),('3fe8b0','t'),('c8fff0','T'),('fff4d6','C'),('f6fffb','W')]}
for m,v,i,box in [('walk','se',0,(88,120,129,138)),('walk','ne',0,(92,121,115,136)),('sand_kick','ne',1,(81,133,108,151)),('pop_out','ne',1,(83,145,114,161))]:
 a=np.array(Image.open(files(m,v)[i]).convert('RGBA'));x0,y0,x1,y1=box
 print(m,v,i); print('    '+''.join(str(x//10%10) for x in range(x0,x1))); print('    '+''.join(str(x%10) for x in range(x0,x1)))
 for y in range(y0,y1): print(f'{y:3} '+''.join(chars.get(tuple(a[y,x,:3]),'?') if a[y,x,3] else '.' for x in range(x0,x1)))
