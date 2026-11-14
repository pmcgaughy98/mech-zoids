from pathlib import Path
p=Path(__file__).parent/'refinish.py'
s=p.read_text()
s=s[:s.index('lines = []')]
s=s.replace('from pathlib import Path','from pathlib import Path\nimport sys, json, hashlib\nfrom PIL import ImageDraw')
s=s.replace('SRC = Path(__file__).resolve().parent.parent\nOUT = Path(__file__).resolve().parent', 'ROOT = Path(__file__).resolve().parent\nNAME = sys.argv[1]\nN = {"idle":5,"walk":7,"horn-jab":6,"horn-toss":7}[NAME]\nSRC = OUT = ROOT / NAME')
s=s.replace('SRC / "refs"','ROOT / "refs"')
s=s.replace('pal = np.array([c for c in allpal if tuple(int(v) for v in c) not in EYE])','pal = allpal\nnon_eye = np.array([c for c in allpal if tuple(int(v) for v in c) not in EYE])')
s=s.replace('np.linspace(0, W, 7)', 'np.linspace(0, W, N+1)')
s=s.replace('assert len(bands) == 3, "row gutters not found"', '''if len(bands) != 3:
    (OUT/'checks.txt').write_text(f'FAIL: found {len(bands)} row bands instead of 3. No finishing.\\n')
    (OUT/'grid.json').write_text(json.dumps({'clean':False,'bands':[(b.start,b.stop) for b in bands]}))
    raise SystemExit(2)''')
s=s.replace('rim = alpha & ~ndi.binary_erosion(alpha)', 'rim = alpha & ~ndi.binary_erosion(alpha, structure=np.ones((3,3),bool))')
s=s.replace('    fin = np.dstack', '''    # Eye colours are legal only with all eight neighbours opaque.
    edge_eye = rim & np.any(np.all(quant[:,:,None,:] == np.array(list(EYE))[None,None,:,:],axis=3),axis=2)
    v = small[edge_eye].astype(np.int32)
    quant[edge_eye] = non_eye[((v[:,None,:]-non_eye.astype(np.int32)[None,:,:])**2).sum(2).argmin(1)]
    fin = np.dstack''')
p.write_text(s)
