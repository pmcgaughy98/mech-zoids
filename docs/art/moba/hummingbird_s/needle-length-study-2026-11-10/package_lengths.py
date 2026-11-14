from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,json
BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/hummingbird_s/needle-length-study-2026-11-10';ROOT=Path(__file__).parent
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27);canvas=Image.new('RGB',(2160,1540),'#17202a');draw=ImageDraw.Draw(canvas)
for i,(name,label) in enumerate([('current','CURRENT'),('shorter-20','SHAFT 20% SHORTER'),('shorter-30','SHAFT 30% SHORTER')]):
 for row,view in enumerate(['side','whole']):canvas.paste(Image.open(OUT/f'{name}-{view}.png').convert('RGB'),(i*720,row*770+45))
 draw.text((i*720+20,8),label,font=font,fill='white');draw.text((i*720+20,780),'Same head/body/rig; review copy',font=font,fill='white')
canvas.save(OUT/'needle-length-comparison.png')
for filename in ['length_study.py','render_lengths.py','package_lengths.py']:shutil.copy2(ROOT/filename,OUT/filename)
(OUT/'README.md').write_text('''# Hummingbird needle length study

Current topology-repaired v2 is preserved as the Workshop version. Two isolated review copies shorten only the shaft (beyond glTF Z=.30) by 20% and 30%, preserving its straight axis/downward aim and all body positions, rig, weights, textures and materials. These are proportion options, not promoted production versions. No new rig or paid generation.

Both original side sheets were inspected. Approximate left-sheet landmarks: shaft tip X102, shaft/collar junction X275, skull front X325 and back X492. This gives shaft/skull length about 1.04. In the matched orthographic current model crop, shaft length is about 304 pixels against skull length about 192 (ratio 1.58); 20% gives about 1.27 and 30% about 1.11. These are manual image landmarks, not calibrated anatomy measurements, and the collar remains unchanged. The 30% shorter shaft is closest to that reference proportion; current is still a valid intentionally long-needle option if Preston prefers it.

needle-length-comparison.png shows same-camera side and whole-model views. candidate-verification.json records hashes and source-preservation checks. The copies were imported and rendered in Blender; deformation/gameplay/engine checks are pending selection. No catalog or gameplay model was switched to an unselected length.
''')
print('Packaged three-way proportion review; Workshop v2 retained.')
