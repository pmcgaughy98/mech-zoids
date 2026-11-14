"""Phone video and board for the gorilla strike: idle still, strike F0-F4 (sheet columns 2-6), back to idle."""
import sys, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
RUN = Path(sys.argv[1]); VIEWS = sys.argv[2].split(','); OUT = Path(sys.argv[3])
STILLS = Path('D:/dev/new-mech-rpg/docs/art/moba/ape_l/take-a/views_cam35_touchup')
S = 4; BG = (46, 52, 44, 255)
still = {v: Image.open(STILLS / f'{v}.png').convert('RGBA') for v in VIEWS}
strike = {v: [Image.open(RUN / 'frames' / f'{v}_f{c}.png') for c in range(1, 6)] for v in VIEWS}
def frame(sel):
    im = Image.new('RGBA', (160 * S * len(VIEWS), 160 * S + 40), BG); d = ImageDraw.Draw(im)
    d.line([(0, 130 * S + S), (im.width, 130 * S + S)], fill=(70, 78, 66, 255), width=2)
    for i, v in enumerate(VIEWS):
        src = still[v] if sel is None else strike[v][sel]
        im.alpha_composite(src.resize((160 * S, 160 * S), Image.Resampling.NEAREST), (i * 160 * S, 0))
    return im.convert('RGB')
TICK = 0.091  # 100 ms ticks played at 1.1x: contact (F2) at about 0.18 s, done at about 0.45 s
seq = []
for speed, loops in [(1.0, 4), (0.25, 1)]:
    for _ in range(loops):
        seq += [(None, 0.6)] + [(k, TICK / speed) for k in range(5)] + [(None, 0.4)]
fps = 50; tmp = Path('D:/dev/_scratch/attack/ape_s1_vid'); n = 0
for sel, dur in seq:
    im = frame(sel)
    for _ in range(max(1, round(dur * fps))): im.save(tmp / f'{n:05d}.png'); n += 1
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', str(tmp / '%05d.png'), '-c:v', 'libx264',
                '-crf', '27', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(OUT)], check=True)
for p in tmp.glob('*.png'): p.unlink()
# board: still then F0-F4, contact F2 marked
B = 4; W = 160 * B; board = Image.new('RGBA', (W * 6, (160 * B + 30) * len(VIEWS)), (58, 60, 70, 255)); d = ImageDraw.Draw(board)
for r, v in enumerate(VIEWS):
    y = r * (160 * B + 30)
    for c, im in enumerate([still[v]] + strike[v]):
        board.alpha_composite(im.resize((W, W), Image.Resampling.NEAREST), (c * W, y + 30))
        d.text((c * W + 10, y + 8), (f'{v} still' if c == 0 else f'F{c-1}' + ('  CONTACT' if c == 3 else '')), fill=(230, 230, 230, 255))
    d.line([(0, y + 30 + 130 * B + B), (board.width, y + 30 + 130 * B + B)], fill=(90, 96, 110, 255), width=2)
board.convert('RGB').save(RUN / 'board_strike_4x.png'); print(n, 'video frames;', OUT, board.size)
