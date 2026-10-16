"""Install generated source art at the named native game resolutions."""
import json
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--replace-generated', action='store_true')
args = parser.parse_args()
manifest = json.loads((ROOT / 'docs/team/art-generation-2026-10-11.json').read_text())
tiles = []
for asset in manifest['assets']:
    dst = ROOT / 'art' / asset['path']
    if dst.exists() and not args.replace_generated:
        raise FileExistsError(f'Asset already exists: {dst}')
    im = Image.open(asset['source']).convert('RGBA')
    target = (asset['width'], asset['height'])
    if asset['transparent']:
        alpha = im.getchannel('A')
        if alpha.getextrema()[0] == 255:
            raise ValueError(f'Missing generated transparency: {asset["path"]}')
        # Generated alpha can include nearly invisible pixels far outside the subject.
        # Crop around visible pixels without changing the alpha of the retained image.
        box = alpha.point(lambda value: 255 if value > 128 else 0).getbbox()
        im = im.crop(box)
        # Use the whole tiny character canvas; retain breathing room around machines.
        margin = 2 if asset['path'].startswith('machines/') else 0
        scale = min((target[0] - margin * 2) / im.width, (target[1] - margin * 2) / im.height)
        size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
        im = im.resize(size, Image.Resampling.NEAREST)
        canvas = Image.new('RGBA', target)
        canvas.alpha_composite(im, ((target[0] - im.width) // 2, target[1] - margin - im.height))
        im = canvas
    else:
        im = im.resize(target, Image.Resampling.NEAREST)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst)
    assert Image.open(dst).size == target
    print(f'{asset["path"]}: {target[0]}x{target[1]}, alpha {im.getchannel("A").getextrema()}')
    tile = Image.new('RGB', (660, 400), '#20252f')
    preview = im.copy()
    scale = min(640 // target[0], 350 // target[1])
    preview = preview.resize((target[0] * scale, target[1] * scale), Image.Resampling.NEAREST)
    tile.paste(preview, ((660 - preview.width) // 2, 32), preview)
    ImageDraw.Draw(tile).text((10, 10), asset['path'], fill='white')
    tiles.append(tile)
sheet = Image.new('RGB', (1980, 1600), '#20252f')
for i, tile in enumerate(tiles):
    sheet.paste(tile, ((i % 3) * 660, (i // 3) * 400))
sheet.save(ROOT / 'docs/team/art-contact-sheet.png')
