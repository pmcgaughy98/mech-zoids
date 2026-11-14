from pathlib import Path
P=Path(__file__).resolve().parent; p=P/'audit.py'; s=p.read_text()
s=s.replace("'se':{'near':140,'far':[123,127]}","'se':{'near':140,'far':123}").replace("'ne':{'near':140,'far':[117,125]}","'ne':{'near':140,'far':118}").replace("'n':{'near':140,'far':109}","'n':{'near':140,'far':108}")
s=s.replace("shape.append('Foot bottoms", "shape.append('Approved feet: s/n far pair occluded, not reliably separable; se near row 140 / identifiable far 138; e near 140 / identifiable far 138; ne near 139 / identifiable far 137. Low-camera rises only 2 rows.')\nshape.append('Foot bottoms")
p.write_text(s)
