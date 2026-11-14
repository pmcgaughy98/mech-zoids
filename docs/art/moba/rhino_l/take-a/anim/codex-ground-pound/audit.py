from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
P=Path(__file__).resolve().parent
lines=[]
for name in ['front','side','back']:
 for i in range(6):
  a=np.array(Image.open(P/'frames'/f'{name}_f{i}.png').convert('RGBA')); m=a[:,:,3]>0; edge=m&~ndi.binary_erosion(m)
  pale=(a[:,:,:3].mean(2)>180)&m
  lone=np.zeros(m.shape,bool)
  for col in np.unique(a[m,:3],axis=0):
   same=np.all(a[:,:,:3]==col,axis=2)&m
   neighbors=ndi.convolve(same.astype(int),np.ones((3,3),int),mode='constant')-same
   lone|=same&(neighbors==0)
  lines.append(f'{name}_f{i} lone pale rim pixels={int((lone&pale&edge).sum())}; lone-colour pixel share={float(lone.sum()/m.sum()):.4f}')
lines += [
 'Front-foot clearance F0..F5 (px, manual shoe-outline estimates from the generated image, +/-2px):',
 'front: 0, 8, 26, 30, 0, 0. F2/F3 clear quarter of idle body height (20px).',
 'side: 0, 5, 18, 24, 0, 1. F2/F3 clear quarter of idle body height (17.75px); F5 is 1px above target ground.',
 'back: N/A, N/A, N/A, N/A, N/A, N/A. Front feet are occluded; no visible lift can be verified. Visible rear feet clearance: 0,0,0,0,0,0.',
 'Back feet ground check: front and back rows bottom_y=160 throughout; side F1,F2,F5 bottom_y=159 (FAIL fixed ground), F0,F3,F4=160.',
 'Side faces RIGHT in all six columns (visual horn/face direction).',
 'Front/back cameras visually straight on, roughly bilateral; exact-colour mirror scores are below perfect symmetry.',
 'Identity by eye: recognizably the same yellow/dark-frame mech rhino, grey disc joints, flat grey shoes, two-tone horn, red eye and tail stub; exact approved proportions are NOT preserved.',
 'Synchronization by eye: idle/rise/peak/slam/recover beats broadly agree; rear view does NOT demonstrate front-leg lift, so full three-view match is unproven.',
 'Overall verdict: FAIL approval requirements. No generation retry, no per-frame recentering, no creature redrawing.',
 'By-eye findings use the image already returned by the generation tool. No generated file or preview was opened for visual inspection.'
]
with (P/'checks.txt').open('a') as f: f.write('\n'.join(lines)+'\n')
print('\n'.join(lines))
