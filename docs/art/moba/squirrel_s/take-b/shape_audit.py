"""Anatomical landmarks read by eye from take B; no sprite drawing."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
lens=[(196,106,14),(255,176,46),(255,241,196)]
counts={}
for d in ['ne','nw']:
 a=np.array(Image.open(P/'views'/f'{d}.png').convert('RGBA'))
 counts[d]=int(sum(((a[...,:3]==c).all(2)&(a[...,3]>0)).sum() for c in lens))
text=f'''Anatomical spans are manual crop-local landmarks, +/-2px; inclusive endpoints. See landmark-review.png.
East tail y6..63 = 58px; non-tail body including ears y0..70 = 71px; tail/body = {58/71:.3f}.
East body excluding ears, helmet crown through soles y12..70 = 59px; tail/body without ears = {58/59:.3f}.
East ear plate y0..18 = 19px; helmet head excluding teeth y12..30 = 19px; ear/head = 1.000.
East/south height = 71/72 = {71/72:.3f}; north/south = 72/72 = 1.000.
Amber eye pixels (all three lens colours): ne {counts['ne']}; nw {counts['nw']}.
South: ear-tip top y0; tail top approximately y14; tail lower by 14px (PASS).
North: ear-tip top y0; tail top approximately y15; tail lower by 15px (PASS).
By eye all eight tail tops remain below ear tips. Tail is a C-hook rather than a strong S; four fan ends are not distinct.
Rear diagonals 72px versus front diagonals 71px: 1px taller, FAIL literal no-taller rule, within 5%.
'''
(P/'shape.txt').write_text(text)
print(text)
