exec(open(str(OUT/'dump.py')).read().split('for args in')[0])
for args in [('ear_burst','side',2,(93,122,116,140)),('ear_burst','back',2,(79,124,113,138)),('sand_kick','front',1,(78,131,115,140)),('sand_kick','side',4,(80,132,111,143)),('death','front',1,(86,120,109,133)),('death','front',4,(112,137,132,155)),('pop_out','front',2,(76,127,115,149))]:dump(*args)
