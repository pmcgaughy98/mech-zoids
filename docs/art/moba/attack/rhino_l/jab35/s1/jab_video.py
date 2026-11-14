"""Phone video and board for the rhino horn_jab at 35: idle still, jab F0-F5 with the kit's holds (2,2,1,2,1,1 ticks
of 100 ms, played at 2x), back to idle; then the same at quarter speed. Board: still then F0-F5, hit F2 marked."""
import sys, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
RUN = Path(sys.argv[1]); VIEWS = sys.argv[2].split(','); OUT = Path(sys.argv[3])
STILLS = Path('D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/views_cam35_touchup')
HOLDS = [2, 2, 1, 2, 1, 1]; SPEED = 2.0; HIT = 2
still = {v: Image.open(STILLS / f'{v}.png').convert('RGBA') for v in VIEWS}
C = next(iter(still.values())).width; S = 3; BG = (52, 50, 44, 255)
FEET = 160
jab = {v: [Image.open(RUN / 'frames' / f'{v}_f{c}.png') for c in range(6)] for v in VIEWS}
def frame(sel):
    im = Image.new('RGBA', (C * S * len(VIEWS), C * S), BG); d = ImageDraw.Draw(im)
    d.line([(0, FEET * S + S), (im.width, FEET * S + S)], fill=(78, 74, 64, 255), width=2)
    for i, v in enumerate(VIEWS):
        src = still[v] if sel is None else jab[v][sel]
        im.alpha_composite(src.resize((C * S, C * S), Image.Resampling.NEAREST), (i * C * S, 0))
    return im.convert('RGB')
seq = []
for slow, loops in [(1.0, 4), (4.0, 1)]:
    for _ in range(loops):
        seq += [(None, 0.6)] + [(k, h * 0.1 / SPEED * slow) for k, h in enumerate(HOLDS)] + [(None, 0.4)]
fps = 50; tmp = Path('D:/dev/_scratch/attack/jab_vid'); tmp.mkdir(exist_ok=True); n = 0
for p in tmp.glob('*.png'): p.unlink()
for sel, dur in seq:
    im = frame(sel)
    for _ in range(max(1, round(dur * fps))): im.save(tmp / f'{n:05d}.png'); n += 1
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', str(tmp / '%05d.png'), '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
                '-c:v', 'libx264', '-crf', '27', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(OUT)], check=True)
for p in tmp.glob('*.png'): p.unlink()
B = 3; W = C * B; board = Image.new('RGBA', (W * 7, (W + 24) * len(VIEWS)), (58, 60, 70, 255)); d = ImageDraw.Draw(board)
for r, v in enumerate(VIEWS):
    y = r * (W + 24)
    for c, im in enumerate([still[v]] + jab[v]):
        board.alpha_composite(im.resize((W, W), Image.Resampling.NEAREST), (c * W, y + 24))
        d.text((c * W + 8, y + 6), (f'{v} still' if c == 0 else f'F{c-1}' + ('  HIT' if c - 1 == HIT else '')), fill=(230, 230, 230, 255))
    d.line([(0, y + 24 + FEET * B + B), (board.width, y + 24 + FEET * B + B)], fill=(90, 96, 110, 255), width=2)
board.convert('RGB').save(RUN / 'board_jab_3x.png'); print(n, 'frames', OUT.name, board.size)
