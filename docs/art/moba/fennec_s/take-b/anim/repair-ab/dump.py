from repair import *
CH='0123456789ABCDE'
def dump(m,v,i,box):
 a=np.array(Image.open(files(m,v)[i]).convert('RGBA'));x0,y0,x1,y1=box
 print('\n',m,v,i,box);print('    '+''.join(str(x//10%10) for x in range(x0,x1)));print('    '+''.join(str(x%10) for x in range(x0,x1)))
 for y in range(y0,y1):print(f'{y:3} '+''.join('.' if a[y,x,3]==0 else CH[COL.index(tuple(a[y,x]))] for x in range(x0,x1)))
for args in [('idle','front',1,(80,128,111,146)),('idle','back',1,(79,130,113,148)),('walk','back',0,(78,123,116,145)),('walk','side',0,(85,127,116,148)),('sand_kick','front',2,(76,137,113,156)),('sand_kick','side',1,(81,129,114,150)),('sand_kick','back',3,(72,126,120,144)),('dig','side',2,(63,134,121,155)),('dig','front',2,(76,146,115,161)),('dig','back',2,(75,140,115,158)),('death','front',4,(123,145,151,154))]:dump(*args)
