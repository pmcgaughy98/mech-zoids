from pathlib import Path
p = Path(__file__).parent / 'refinish.py'
s = p.read_text()
s = s.replace('from pathlib import Path', 'from pathlib import Path\nimport json, hashlib\nfrom PIL import ImageDraw')
s = s.replace('SRC = Path(__file__).resolve().parent.parent\nOUT = Path(__file__).resolve().parent', 'SRC = Path(__file__).resolve().parent\nOUT = SRC / "walk"')
s = s.replace('pal = np.array([c for c in allpal if tuple(int(v) for v in c) not in EYE])', 'pal = allpal\nnon_eye = np.array([c for c in allpal if tuple(int(v) for v in c) not in EYE])')
s = s.replace('Image.open(SRC / "sheet_raw.png")', 'Image.open(OUT / "sheet_raw.png")')
s = s.replace('np.linspace(0, W, 7)', 'np.linspace(0, W, 8)')
s = s.replace('    fin = np.dstack', '''    interior = ndi.binary_erosion(alpha, structure=np.ones((3, 3), bool))
    eyehit = np.isin(quant.view('u1').reshape(nh,nw,3)[:,:,0], [255]) & np.any(np.all(quant[:,:,None,:] == np.array(list(EYE))[None,None,:,:], axis=3), axis=2)
    bad = eyehit & ~interior
    v = small[bad].astype(np.int32)
    quant[bad] = non_eye[((v[:,None,:]-non_eye.astype(np.int32)[None,:,:])**2).sum(2).argmin(1)]
    fin = np.dstack''')
s = s[:s.index('\nlines = []')]
p.write_text(s)
