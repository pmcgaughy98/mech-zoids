"""Falcon sky barrage effect, first pass (falcon session, 2026-11-05).

Draws every piece by code, pixel by pixel, in the falcon's own 16 colours:
  dart_00/27/45/63.png  feather dart pointing down at the four clean pixel angles (mirror and flip for the rest)
  impact_spark_strip.png  8 frames, upright (faces the camera): flash, burst, feather bits, the dart left stuck in
  impact_dust_strip.png   6 frames, flat on the ground: a dust ring
  ring.png / ring_open_strip.png  the area ring, flat on the ground, 3.5 m radius at 50 texels per metre
Then mocks the barrage at the ult camera (57.5 deg, middle of Preston's 55 to 60) and at the normal 35 deg camera
everyone else sees, as GIFs and a board, and scores the result against the measured targets.
Run: python build_sky_barrage.py   (no Godot; nothing outside this folder and D:/dev/_scratch/falcon is written)
"""
import glob, json, math, os, random
from PIL import Image, ImageDraw, ImageFont

MAIN = 'D:/dev/new-mech-rpg'
OUT = os.path.dirname(os.path.abspath(__file__))
SCR = 'D:/dev/_scratch/falcon'
os.makedirs(SCR, exist_ok=True)
TPM = 50  # texels per metre, house size rule

def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
P = {k: hx(v) for k, v in dict(CR_HI='ff6a72', CR='e01e3c', CR_MID='9c0f26', CR_DK='520716', IV='ece6d6',
     IV_MID='b8ae98', ST_LT='c9c8cf', ST='8a8892', ST_DK='3d3a44', FR='211e27', FR_DK='141218', YL='ffc21a',
     YL_DK='c4820a', YL_LT='ffe680', GR='6aff6a', WH='ffffff').items()}

# measured falcon palette, from the approved stills
FALCON = set()
for v in ('s', 'se', 'e', 'ne', 'n'):
    im = Image.open(f'{MAIN}/docs/art/moba/falcon_m/take-b/views/{v}.png').convert('RGBA')
    FALCON |= {p[:3] for p in im.getdata() if p[3] > 0}
assert all(c[:3] in FALCON for c in P.values()), 'palette constant not in the stills'

def img_from(px, w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for (x, y), c in px.items():
        if 0 <= x < w and 0 <= y < h: im.putpixel((x, y), P[c])
    return im

def line(x0, y0, x1, y1):
    pts = []; dx = abs(x1 - x0); dy = -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1: return pts
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy

def circle_pts(r):
    pts = set(); x = r; y = 0; err = 1 - r
    while x >= y:
        for a, b in ((x, y), (y, x), (-y, x), (-x, y), (-x, -y), (-y, -x), (y, -x), (x, -y)): pts.add((a, b))
        y += 1
        if err < 0: err += 2 * y + 1
        else: x -= 1; err += 2 * (y - x) + 1
    return pts

# ---------------------------------------------------------------- dart
def dart_feats():
    f = {}
    def put(s, w, c): f[(s, w)] = c
    for s in range(-38, -14):          # speed trail, fades back to a dither
        d = -15 - s
        if d < 6: put(s, 0, 'CR_HI')
        elif d < 14: put(s, 0, 'CR')
        elif s % 2 == 0: put(s, 0, 'CR_MID')
    for s in range(-18, -14): put(s, -1, 'CR_HI')
    for s in (-15, -17, -19, -21): put(s, 1, 'CR_DK')
    for s in range(-14, -8):           # fletching: lit vane left, shadow vane right, widest at the back
        k = 1 + (-9 - s) // 2
        for w in range(1, k + 1):
            put(s, -w, 'CR_HI' if w == k else 'CR')
            put(s, w, 'CR_DK' if w == k else 'CR_MID')
    for s in range(-14, -3): put(s, 0, 'IV')      # quill shaft
    for s in range(-9, -4): put(s, 1, 'IV_MID')
    put(-2, 0, 'ST_LT'); put(-3, 0, 'ST_LT'); put(-3, -1, 'ST_LT'); put(-4, 0, 'ST')   # steel point
    put(-3, 1, 'FR'); put(-4, 1, 'FR')
    put(-1, 0, 'YL_LT'); put(0, 0, 'WH')         # hot tip
    return f

SLOPES = {'00': (0, 1), '27': (1, 2), '45': (1, 1), '63': (2, 1)}
ANG = {'00': 0.0, '27': math.degrees(math.atan2(1, 2)), '45': 45.0, '63': math.degrees(math.atan2(2, 1))}
def make_dart(key):
    dx, dy = SLOPES[key]; px = {}
    for (s, w), c in dart_feats().items():
        p = (math.floor(s * dx / dy) + w, s) if dy >= dx else (s, math.floor(s * dy / dx) + w)
        px[p] = c
    mx = min(p[0] for p in px); my = min(p[1] for p in px)
    W = max(p[0] for p in px) - mx + 1; H = max(p[1] for p in px) - my + 1
    im = img_from({(x - mx, y - my): c for (x, y), c in px.items()}, W, H)
    return im, (-mx, -my)  # image, tip pixel

DARTS = {k: make_dart(k) for k in SLOPES}

# ---------------------------------------------------------------- impact spark (upright)
SPK = 32; G = (16, 27); C = (16, 25)
def spark_frames():
    out = []
    STUB = [((0, -1), 'IV_MID'), ((0, -2), 'IV'), ((0, -3), 'IV'), ((0, -4), 'IV'), ((0, -5), 'IV'), ((0, -6), 'IV'),
            ((1, -1), 'ST_DK'), ((1, -2), 'IV_MID'), ((-1, -4), 'CR'), ((-1, -5), 'CR'), ((-2, -6), 'CR_HI'),
            ((-2, -7), 'CR_HI'), ((1, -4), 'CR_MID'), ((1, -5), 'CR_MID'), ((2, -6), 'CR_DK'), ((2, -7), 'CR_DK')]
    DIM = {'CR_HI': 'CR_MID', 'CR': 'CR_MID', 'CR_MID': 'CR_DK', 'CR_DK': 'CR_DK'}
    def stub(px, dim=False, fade=False):
        for i, ((dx, dy), c) in enumerate(STUB):
            if fade and i % 2: continue
            px[(G[0] + dx, G[1] + dy)] = DIM.get(c, c) if dim else c
    def ray(px, d, a, b, col):
        for k in range(a, b + 1): px[(C[0] + d[0] * k, C[1] + d[1] * k)] = col(k)
    def dots(px, pts):
        for (x, y), c in pts: px[(C[0] + x, C[1] + y)] = c
    UP, L, R, UL, UR, DL, DR = (0, -1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)
    f = {}; dots(f, [((0, 0), 'WH'), ((1, 0), 'WH'), ((-1, 0), 'WH'), ((0, 1), 'WH'), ((0, -1), 'WH')] +
                 [((x, y), 'YL_LT') for x, y in ((2, 0), (-2, 0), (0, -2), (0, 2), (1, 1), (-1, 1), (1, -1), (-1, -1))])
    out.append(f)
    f = {}
    for x in (-1, 0, 1):
        for y in (-1, 0, 1): f[(C[0] + x, C[1] + y)] = 'WH'
    for d in (L, R): f[(C[0] + 2 * d[0], C[1] - 1)] = 'WH'           # wider core (pass 1b)
    ray(f, UP, 2, 10, lambda k: 'YL_LT' if k <= 5 else 'YL'); ray(f, L, 2, 8, lambda k: 'YL' if k >= 7 else 'YL_LT')
    ray(f, R, 2, 8, lambda k: 'YL' if k >= 7 else 'YL_LT'); ray(f, UL, 2, 6, lambda k: 'YL'); ray(f, UR, 2, 6, lambda k: 'YL')
    ray(f, DL, 2, 2, lambda k: 'YL_DK'); ray(f, DR, 2, 2, lambda k: 'YL_DK'); out.append(f)
    f = {}; dots(f, [((0, 0), 'YL_LT'), ((1, 0), 'YL'), ((-1, 0), 'YL'), ((0, -1), 'YL')])
    ray(f, UP, 5, 13, lambda k: 'YL' if k <= 8 else 'YL_DK'); ray(f, L, 4, 10, lambda k: 'YL' if k <= 7 else 'YL_DK')
    ray(f, R, 4, 10, lambda k: 'YL' if k <= 7 else 'YL_DK'); ray(f, UL, 4, 8, lambda k: 'YL_DK'); ray(f, UR, 4, 8, lambda k: 'YL_DK')
    dots(f, [((-6, -8), 'CR'), ((-5, -8), 'CR'), ((7, -9), 'CR_MID'), ((8, -9), 'CR_MID')]); stub(f); out.append(f)
    f = {}; dots(f, [((0, -12), 'YL_DK'), ((0, -14), 'YL_DK'), ((-10, 0), 'YL_DK'), ((-12, 0), 'YL_DK'), ((10, 0), 'YL_DK'),
                     ((12, 0), 'YL_DK'), ((-8, -8), 'YL_DK'), ((8, -8), 'YL_DK'), ((-8, -11), 'CR_MID'), ((-7, -11), 'CR_MID'),
                     ((9, -12), 'CR_DK')]); stub(f); out.append(f)
    f = {}; dots(f, [((0, -15), 'YL_DK'), ((-13, 0), 'YL_DK'), ((13, 0), 'YL_DK'), ((-9, -12), 'CR_MID'), ((10, -11), 'CR_DK'),
                     ((11, -11), 'CR_DK')]); stub(f); out.append(f)
    f = {}; dots(f, [((-9, -9), 'CR_DK'), ((10, -8), 'CR_DK')]); stub(f); out.append(f)
    f = {}; stub(f, dim=True); out.append(f)
    f = {}; stub(f, dim=True, fade=True); out.append(f)
    return [img_from(px, SPK, SPK) for px in out]

# ---------------------------------------------------------------- dust ring (flat)
DST = 48  # pass 1b: bigger and two pixels thick early, so it reads on the floor
def dust_frames():
    out = []
    for i, (r, c) in enumerate(zip((4, 8, 12, 15, 18, 20), ('IV', 'IV', 'IV_MID', 'IV_MID', 'ST', 'ST'))):
        px = {}
        for rr in ((r, r - 1) if i < 3 else (r,)):
            for (x, y) in circle_pts(rr):
                if i >= 4 and (x + y) % 2: continue
                px[(24 + x, 24 + y)] = c
        out.append(img_from(px, DST, DST))
    return out

# ---------------------------------------------------------------- area ring (flat)
R_M = 3.5; R = int(R_M * TPM); RS = 2 * R + 10
def ring_px(r, chevrons):
    c = RS // 2; px = {}
    for (x, y) in circle_pts(r): px[(c + x, c + y)] = 'CR_MID'
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            d = math.hypot(x, y)
            if r - 4.5 <= d < r - 2.5 and math.degrees(math.atan2(y, x)) % 15 < 9: px[(c + x, c + y)] = 'CR'
    if chevrons:  # eight feather chevrons pointing in: keen sight
        for k in range(8):
            a = math.radians(k * 45 + 22.5); u = (math.cos(a), math.sin(a)); p = (-u[1], u[0])
            for sgn, col in ((1, 'IV'), (-1, 'IV_MID')):
                for t_in, t_out in ((16, 8), (15, 7)):
                    T = (round(c + (r - t_in) * u[0]), round(c + (r - t_in) * u[1]))
                    A = (round(c + (r - t_out) * u[0] + sgn * 5 * p[0]), round(c + (r - t_out) * u[1] + sgn * 5 * p[1]))
                    for q in line(*T, *A): px.setdefault(q, col)
            px[(round(c + (r - 16) * u[0]), round(c + (r - 16) * u[1]))] = 'WH'
    return px
RING_OPEN = [img_from(ring_px(round(R * s), i >= 2), RS, RS) for i, s in enumerate((0.6, 0.8, 0.95, 1.0))]
RING = RING_OPEN[-1]

# ---------------------------------------------------------------- write pieces
SPARK = spark_frames(); DUST = dust_frames()
for k, (im, tip) in DARTS.items(): im.save(f'{OUT}/dart_{k}.png')
def strip(frames):
    w, h = frames[0].size; s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.paste(f, (i * w, 0))
    return s
strip(SPARK).save(f'{OUT}/impact_spark_strip.png'); strip(DUST).save(f'{OUT}/impact_dust_strip.png')
RING.save(f'{OUT}/ring.png'); strip(RING_OPEN).save(f'{OUT}/ring_open_strip.png')
pieces = {
    'texels_per_metre': TPM, 'fps': 30,
    'dart': {k: {'size': list(DARTS[k][0].size), 'tip': list(DARTS[k][1]), 'angle_from_straight_down': round(ANG[k], 2)}
             for k in DARTS},
    'dart_use': 'billboard; pick the drawn angle nearest the on-screen travel direction, mirror for leftward, flip for upward',
    'impact_spark': {'cell': [SPK, SPK], 'ground_point': list(G), 'frames': len(SPARK), 'billboard': True},
    'impact_dust': {'cell': [DST, DST], 'centre': [DST // 2, DST // 2], 'frames': len(DUST), 'flat_on_ground': True},
    'ring': {'size': [RS, RS], 'radius_m': R_M, 'open_frames': 4, 'open_frame_time_s': round(2 / 30, 3), 'flat_on_ground': True},
}

# ---------------------------------------------------------------- mock barrage
def stills():
    pick = []
    for name in ('hippo_l', 'fennec_s', 'kangaroo_m', 'ape_l', 'rhino_l'):
        for ap in sorted(glob.glob(f'{MAIN}/docs/art/moba/{name}/take-*/APPROVED.txt')):
            d = os.path.dirname(ap)
            for sub in ('views_cam35_touchup', 'views'):
                f = f'{d}/{sub}/s.png'
                if os.path.exists(f): pick.append((name, f)); break
            break
    out = []
    for name, f in pick[:3]:
        im = Image.open(f).convert('RGBA'); bb = im.getbbox(); im = im.crop(bb)
        out.append((name, f.replace(MAIN + '/', ''), im, (im.width // 2, im.height - 1)))
    return out
MACH_IMG = stills()
MACH_POS = [(-1.3, -0.8), (1.25, -0.3), (0.1, 1.2)][:len(MACH_IMG)]

frames_found = glob.glob(os.path.expandvars('%APPDATA%').replace('\\', '/') + '/Godot/app_userdata/*/ult_view_test/f0045.png')
frames_found += glob.glob(f'{MAIN}/docs/art/moba/match/**/f0045.png', recursive=True)
CAM_FRAME = frames_found[0] if frames_found else None
FLOOR = (74, 80, 72)
if CAM_FRAME:
    cf = Image.open(CAM_FRAME).convert('RGB'); w, h = cf.size
    patch = sorted(cf.crop((int(w * .45), int(h * .86), int(w * .55), int(h * .93))).getdata(), key=sum)
    FLOOR = patch[len(patch) // 2]

W, H, CX, CY = 400, 350, 200, 195; S = TPM
def proj(p, th): return (CX + p[0] * S, CY + p[2] * S * math.sin(th) - p[1] * S * math.cos(th))
def flat(im, th): return im.resize((im.width, max(1, round(im.height * math.sin(th)))), Image.NEAREST)

def make_sim(seed=7, T=3.0):
    rng = random.Random(seed); out = []; t = 0.25; i = 0
    while t < T:
        for j in range(3 if i % 2 == 0 else 4):
            phi = 2 * math.pi * t / 4.0
            st = (6 * math.cos(phi), 12.0, 6 * math.sin(phi))
            if rng.random() < 0.6:
                m = rng.choice(MACH_POS); r = 0.7 * math.sqrt(rng.random()); a = rng.random() * 2 * math.pi
                en = (m[0] + r * math.cos(a), 0.0, m[1] + r * math.sin(a))
            else:
                r = 3.3 * math.sqrt(rng.random()); a = rng.random() * 2 * math.pi; en = (r * math.cos(a), 0.0, r * math.sin(a))
            t0 = t + j * 0.02
            out.append({'t0': t0, 't1': t0 + math.dist(st, en) / 24.0, 's': st, 'e': en})
        t += 0.25; i += 1
    return out
SIM = make_sim()

def dart_sprite(vx, vy):
    a = math.degrees(math.atan2(abs(vx), vy)); up = a > 90
    if up: a = 180 - a
    k = min(ANG, key=lambda q: abs(ANG[q] - a)); im, tip = DARTS[k]
    if vx < 0: im = im.transpose(Image.FLIP_LEFT_RIGHT); tip = (im.width - 1 - tip[0], tip[1])
    if up: im = im.transpose(Image.FLIP_TOP_BOTTOM); tip = (tip[0], im.height - 1 - tip[1])
    return im, tip

def render(t, th, cache):
    if 'base' not in cache:
        b = Image.new('RGBA', (W, H), FLOOR + (255,)); d = ImageDraw.Draw(b)
        g = tuple(max(0, c - 9) for c in FLOOR) + (255,)
        for k in range(-6, 7):
            d.line([proj((k, 0, -6), th), proj((k, 0, 6), th)], fill=g); d.line([proj((-6, 0, k), th), proj((6, 0, k), th)], fill=g)
        cache['base'] = b; cache['ring'] = [flat(r, th) for r in RING_OPEN]
        cache['dust'] = [flat(x, th) for x in DUST]
    im = cache['base'].copy()
    rf = cache['ring'][min(3, int(t * 15))]
    im.alpha_composite(rf, (round(CX - rf.width / 2), round(CY - rf.height / 2)))
    upright = []; air = []; n_air = n_imp = 0
    for dd in SIM:
        if dd['t0'] <= t < dd['t1']:
            u = (t - dd['t0']) / (dd['t1'] - dd['t0']); p = tuple(a + (b - a) * u for a, b in zip(dd['s'], dd['e']))
            a0 = proj(dd['s'], th); a1 = proj(dd['e'], th); spr, tip = dart_sprite(a1[0] - a0[0], a1[1] - a0[1])
            x, y = proj(p, th); air.append((spr, (round(x - tip[0]), round(y - tip[1])))); n_air += 1
        k = int((t - dd['t1']) * 30)
        if 0 <= k < len(SPARK):
            n_imp += 1; x, y = proj(dd['e'], th)
            if k < len(DUST):
                ds = cache['dust'][k]; im.alpha_composite(ds, (round(x - ds.width / 2), round(y - ds.height / 2)))
            upright.append((dd['e'][2], SPARK[k], (round(x - G[0]), round(y - G[1]))))
    for (gx, gz), (_, _, mi, foot) in zip(MACH_POS, MACH_IMG):
        x, y = proj((gx, 0, gz), th); upright.append((gz, mi, (round(x - foot[0]), round(y - foot[1]))))
    for _, spr, pos in sorted(upright, key=lambda e: e[0]): im.alpha_composite(spr, pos) if inside(spr, pos) else clip(im, spr, pos)
    for spr, pos in air: clip(im, spr, pos)
    return im, n_air, n_imp
def inside(spr, pos): return pos[0] >= 0 and pos[1] >= 0 and pos[0] + spr.width <= W and pos[1] + spr.height <= H
def clip(im, spr, pos):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.paste(spr, pos, spr); im.alpha_composite(layer)

T_TOTAL, FPS = 3.0, 30
stats = {}; board_frames = {}
for name, deg in (('ult_57', 57.5), ('normal_35', 35.0)):
    th = math.radians(deg); cache = {}; frames = []; air = []; imp = []
    for f in range(int(T_TOTAL * FPS)):
        t = f / FPS; im, na, ni = render(t, th, cache)
        frames.append(im.convert('RGB').resize((W * 2, H * 2), Image.NEAREST))
        if t >= 1.0: air.append(na); imp.append(ni)
        if f == 48: board_frames[name] = frames[-1]
    frames[0].save(f'{OUT}/barrage_{name}.gif', save_all=True, append_images=frames[1:], duration=33, loop=0)
    stats[name] = {'pitch_deg': deg, 'ground_squash': round(math.sin(th), 3), 'darts_in_air_avg': round(sum(air) / len(air), 1),
                   'impacts_showing_avg': round(sum(imp) / len(imp), 1)}

# ---------------------------------------------------------------- score
def lum(c): return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255
lands = sorted(d['t1'] for d in SIM); steady = [x for x in lands if 1.0 <= x < 3.0]
clusters = [];
for x in lands:
    if not clusters or x - clusters[-1][-1] > 0.1: clusters.append([x])
    else: clusters[-1].append(x)
gaps = sorted(b[0] - a[0] for a, b in zip(clusters, clusters[1:]))
body_r = Image.open(f'{MAIN}/docs/art/moba/falcon_m/take-b/views/s.png').getbbox()
body_r_m = (body_r[2] - body_r[0]) / 2 / TPM
piece_files = [f'{OUT}/{n}' for n in os.listdir(OUT) if n.endswith('.png') and not n.startswith('board')]
off, nonbin = 0, 0
for pf in piece_files:
    im = Image.open(pf).convert('RGBA')
    for p in im.getdata():
        if p[3] not in (0, 255): nonbin += 1
        if p[3] and p[:3] not in FALCON: off += 1
dart_len_m = DARTS['00'][0].height / TPM
score = [
    ('time between hits', '0.25 s (both references)', f'{gaps[len(gaps) // 2]:.2f} s median', abs(gaps[len(gaps) // 2] - 0.25) <= 0.03),
    ('darts per second', '12 to 16 (clusters of 3 per 0.25 s; camera test 14)', f'{len(steady) / 2.0:.1f}', 12 <= len(steady) / 2.0 <= 16),
    ('area radius in body radii', '5.4 to 8.9 (350/65, 580/65)', f'{R_M / body_r_m:.1f} ({R_M} m / {body_r_m:.2f} m)', 5.4 <= R_M / body_r_m <= 8.9),
    ('warning before first hit', '0.25 s or more (cast time 0.25)', f'{lands[0] - 0.2:.2f} s after the ring is full', lands[0] - 0.2 >= 0.25),
    ('impact life', '0.3 s or less (camera test flash)', f'{len(SPARK) / 30:.2f} s', len(SPARK) / 30 <= 0.3),
    ('dart length with trail', '0.7 m +/- 25% (camera test box)', f'{dart_len_m:.2f} m', 0.525 <= dart_len_m <= 0.875),
    ('impact width (dust ring)', '0.55 m or more (half the camera test flash, 1.1 m)', f'{(2 * 20 + 1) / TPM:.2f} m', (2 * 20 + 1) / TPM >= 0.55),
    ('colours outside the falcon', '0', str(off), off == 0),
    ('see-through pixels', '0 (binary alpha)', str(nonbin), nonbin == 0),
    ('tip vs floor brightness', '0.3 or more', f'{abs(lum(P["WH"]) - lum(FLOOR)):.2f}', abs(lum(P['WH']) - lum(FLOOR)) >= 0.3),
    ('trail vs floor brightness', 'info', f'{abs(lum(P["CR_HI"]) - lum(FLOOR)):.2f}', None),
]
json.dump({'pieces': pieces, 'mock': stats, 'floor_rgb': FLOOR, 'camera_lane_frame': CAM_FRAME,
           'stills_used': [m[1] for m in MACH_IMG], 'score': [dict(zip(('check', 'target', 'measured', 'pass'), s)) for s in score]},
          open(f'{OUT}/metrics.json', 'w'), indent=1)

# ---------------------------------------------------------------- board
try: FONT = ImageFont.load_default(size=15); FONT_B = ImageFont.load_default(size=19)
except TypeError: FONT = FONT_B = ImageFont.load_default()
BW, BH = 1660, 1760; bd = Image.new('RGB', (BW, BH), (28, 28, 33)); dr = ImageDraw.Draw(bd)
def up(im, k): return im.resize((im.width * k, im.height * k), Image.NEAREST)
def put(im, xy, bg=(46, 46, 52)):
    dr.rectangle([xy[0] - 2, xy[1] - 2, xy[0] + im.width + 1, xy[1] + im.height + 1], fill=bg)
    bd.paste(im.convert('RGB') if im.mode != 'RGBA' else im, xy, im if im.mode == 'RGBA' else None)
dr.text((20, 14), 'Falcon sky barrage, pass 1 (2026-11-05). Pieces drawn in the falcon\'s own 16 colours. A proposal: nothing is in the game.', font=FONT_B, fill=(235, 235, 235))
dr.text((20, 50), 'Feather dart, 4 drawn angles at 4x (mirror and flip cover the rest)', font=FONT, fill=(200, 200, 200))
x = 20
for k in ('00', '27', '45', '63'):
    im = up(DARTS[k][0], 4); put(im, (x, 76)); dr.text((x, 76 + im.height + 6), f'{ANG[k]:.0f} deg', font=FONT, fill=(170, 170, 170)); x += im.width + 30
dr.text((20, 290), 'Impact, upright, 8 frames at 30 fps, 3x: flash, burst, feather bits, the dart left stuck in', font=FONT, fill=(200, 200, 200))
put(up(strip(SPARK), 3), (20, 314))
dr.text((20, 432), 'Impact dust, flat on the ground, 6 frames, 3x', font=FONT, fill=(200, 200, 200))
put(up(strip(DUST), 3), (20, 456))
dr.text((1240, 50), f'Area ring, flat, 1x: {R_M} m radius', font=FONT, fill=(200, 200, 200)); put(RING, (1240, 76))
dr.text((910, 456), 'Ring opening, 4 frames, 0.5x preview', font=FONT, fill=(200, 200, 200))
put(strip(RING_OPEN).resize((RS * 2, RS // 2), Image.NEAREST), (910, 480))
y2 = 700
dr.text((20, y2 - 28), 'Ult camera, 57.5 deg, the falcon player (2x, frame 48 of 90)', font=FONT, fill=(200, 200, 200))
dr.text((840, y2 - 28), 'Normal camera, 35 deg, everyone else (2x, same moment)', font=FONT, fill=(200, 200, 200))
put(board_frames['ult_57'], (20, y2)); put(board_frames['normal_35'], (840, y2))
y3 = y2 + H * 2 + 24
for i, (c, tg, m, ok) in enumerate(score):
    mark = 'PASS' if ok else ('info' if ok is None else 'FAIL')
    dr.text((20, y3 + i * 22), f'{mark:5}  {c}: {m}   target {tg}', font=FONT, fill=(150, 220, 150) if ok else (230, 170, 120) if ok is None else (240, 110, 110))
dr.text((20, y3 + len(score) * 22 + 10), 'Machines are approved stills (' + ', '.join(m[0] for m in MACH_IMG) + '), not re-angled. Flat pieces squashed by sin(pitch) as the engine would.', font=FONT, fill=(170, 170, 170))
if CAM_FRAME:
    cf = Image.open(CAM_FRAME).convert('RGB'); cf.thumbnail((560, 300)); put(cf, (BW - cf.width - 20, y3))
    dr.text((BW - cf.width - 20, y3 + cf.height + 6), 'Camera lane test frame (placeholder boxes), for comparison', font=FONT, fill=(170, 170, 170))
bd.save(f'{OUT}/board.png')
print(json.dumps({'mock': stats, 'floor': FLOOR, 'cam_frame': CAM_FRAME, 'stills': [m[1] for m in MACH_IMG],
                  'dart_sizes': {k: DARTS[k][0].size for k in DARTS}}, indent=1))
for s in score: print(('PASS ' if s[3] else 'info ' if s[3] is None else 'FAIL ') + f'{s[0]}: {s[2]} (target {s[1]})')
