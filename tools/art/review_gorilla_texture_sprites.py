"""Use the factory's exact pixelizer/settings and build a nearest-neighbor review sheet."""
from pathlib import Path
import os
import subprocess
import sys
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
JOB = ROOT / 'docs/art/3d/gorilla-texture-2026-10-13'
env = os.environ.copy()
env['PIXEL_EYE_FLAT'] = '1'
env['PIXEL_HIGHLIGHT_RANK'] = '0.93,0.975'
env.pop('PIXEL_PALETTE', None)
env.pop('PIXEL_NO_CROP', None)
shots = ['e', 's', 'se']
sprites = {}
for version in ('before', 'after'):
    output = JOB / version / 'sprites'
    output.mkdir(exist_ok=True)
    for shot in shots:
        src = JOB / version / 'sprite-renders' / (shot + '.png')
        dest = output / (shot + '.png')
        subprocess.run([sys.executable, str(ROOT / 'tools/art/pixelize_render.py'), str(src), str(dest), 'x4.4'],
                       cwd=ROOT, env=env, check=True)
        sprites[version, shot] = Image.open(dest).convert('RGBA')
checks = []
for version in ('before', 'after'):
    assert len({sprites[version, shot].tobytes() for shot in shots}) == len(shots), 'Camera directions did not turn'
for shot in shots:
    a, b = sprites['before', shot], sprites['after', shot]
    equal = a.size == b.size and np.array_equal(np.array(a.getchannel('A')), np.array(b.getchannel('A')))
    assert equal, 'Unexpected shape/position change in ' + shot
    checks.append({'view': shot, 'size': list(a.size), 'same_alpha_and_position': equal})
scale = 4
cell_w = max(s.width for s in sprites.values()) * scale + 32
cell_h = max(s.height for s in sprites.values()) * scale + 40
sheet = Image.new('RGB', (cell_w * 3, cell_h * 2), '#dedede')
draw = ImageDraw.Draw(sheet)
for row, version in enumerate(('before', 'after')):
    for col, shot in enumerate(shots):
        sprite = sprites[version, shot]
        x, y = col * cell_w, row * cell_h
        label = ('Original texture' if version == 'before' else 'New texture preview') + ' / ' + {'e':'side', 's':'front', 'se':'three-quarter'}[shot]
        draw.text((x + 12, y + 8), label, fill='#222222')
        big = sprite.resize((sprite.width * scale, sprite.height * scale), Image.Resampling.NEAREST)
        sheet.paste(big, (x + (cell_w - big.width)//2, y + cell_h - big.height - 12), big)
sheet.save(JOB / 'pixel-before-after-4x.png')
hero = sprites['after', 'se']
hero.resize((hero.width*6, hero.height*6), Image.Resampling.NEAREST).save(JOB / 'pixel-preview-three-quarter-6x.png')
(JOB / 'pixel-audit.json').write_text(json.dumps({'settings': {'scale': 'x4.4', 'eye_flat': True, 'highlight_rank': [.93, .975],
    'stance': 'base=19;R_leg=16;L_leg=3;L_arm=27'}, 'views': checks, 'preview_only': True}, indent=2) + '\n')
print('PIXEL_TEXTURE_PREVIEW_PASS', JOB / 'pixel-before-after-4x.png')
