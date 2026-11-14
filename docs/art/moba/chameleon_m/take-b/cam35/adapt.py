from pathlib import Path
P=Path(__file__).resolve().parent
p=P/'finish.py'
s=p.read_text(); start=s.index('# Amber seeds'); end=s.index('colours=json.loads',start)
s=s[:start]+'''# Lens regions on this generated sheet: amber-ringed circles on steel turrets.
# Gold jaw, throat and belly are outside these regions and remain on the gold ramp.
r,g,bl=rgb.astype(float).transpose(2,0,1)
yy,xx=np.indices(vis.shape); u=xx/b.shape[1]*1254; v=yy/b.shape[0]*1254
zone=np.zeros(vis.shape,bool)
for x0,y0,x1,y1 in [(319,577,354,614),(900,577,935,614),(240,1034,278,1074),(978,1034,1016,1074),(551,1021,585,1061),(668,1021,701,1061)]:
 zone|=(u>=x0)&(u<=x1)&(v>=y0)&(v<=y1)
lens=zone&vis&(r>155)&(g>75)&((bl<160)|((r>220)&(g>210)))
lens_regions=[]
''' +s[end:]; p.write_text(s)
