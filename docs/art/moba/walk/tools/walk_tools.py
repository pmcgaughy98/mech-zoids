#!/usr/bin/env python3
"""Walk lane tools (free, local). Read ../WALK_PLAYBOOK.md first.

  stride    drawn ground speed, natural walk speeds (Froude), and what the game's move_speed asks for
  soles     list the sole segments (bottom-contour plateaus) on stills or frames, to label feet
  gait      foot paths, per-view targets.json, guide strips and a plan GIF, from a feet.json label file
  footlock  measure finished frames against targets.json: foot lock, lowest row, palette, alpha, pieces, edge
  seams     find (and with --fix, fill) slits a limb leaves when it slides back from the pinned body
  mirror    which physical foot is up in all 8 views, with and without the +4 mirror offset

Writes only where --out points. Started 2026-11-05 by the walk lane.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

TEXEL_M = {'L': 0.020, 'M': 0.018, 'S': 0.016}
YAW_DEG = {'e': 0.0, 'se': 45.0, 's': 90.0, 'ne': -45.0, 'n': -90.0}
VIEWS = ['s', 'se', 'e', 'ne', 'n']
GRAVITY = 9.81
# Swing start frame per foot. A foot swings for len(lifts) frames (k = 0, 1, 2 in the rhino scheme) and is planted
# for the rest of the 8.
GAITS = {
    'lateral4': {'LF': 1, 'LH': 3, 'RF': 5, 'RH': 7},  # rhino, approved at 35
    'diagonal': {'RF': 5, 'LH': 5, 'LF': 1, 'RH': 1},  # trot or knuckle walk in diagonal pairs
    'biped': {'L': 5, 'R': 1},
    # wolf trot, approved at the old side angle (wolf_m/take-b/anim/codex-walk2/brief.txt): pair A (near fore + far
    # hind = RF + LH) planted f0-f3, pair B (LF + RH) planted f4-f7, 4-frame swing, lifts 2, 4, 4, 2, P 5 at 10 fps.
    'trot4': {'RF': 4, 'LH': 4, 'LF': 0, 'RH': 0},
    # six legs, 1 = front: alternating tripods. A (L1, R2, L3) planted f0-f3, B (R1, L2, R3) f4-f7. Lobster, Preston
    # 2026-11-06: "Tripod, 3 legs at once".
    'tripod6': {'L1': 4, 'R2': 4, 'L3': 4, 'R1': 0, 'L2': 0, 'R3': 0},
}
# Per-gait options. lifts: default lifts (their count is the swing length). dips: body dip frames, when they are not
# the fore landings. shift: side px added to every path offset (trot4: +0.5 gives the old table's whole px, +8 to -7).
GAIT_OPTS = {'trot4': {'lifts': [2, 4, 4, 2], 'dips': [1, 5], 'shift': 0.5},
             'tripod6': {'lifts': [2, 3, 3, 2], 'dips': [0, 4], 'shift': 0.5}}
COLOURS = {'LF': (235, 80, 80), 'RF': (255, 175, 40), 'LH': (80, 140, 255), 'RH': (60, 225, 200),
           'L': (235, 80, 80), 'R': (60, 225, 200),
           'L1': (235, 80, 80), 'L2': (255, 140, 200), 'L3': (80, 140, 255),
           'R1': (255, 175, 40), 'R2': (180, 255, 90), 'R3': (60, 225, 200)}


# ---------------------------------------------------------------- shared
def view_vec(view, pitch):
    """Screen px per side-view px of travel along the body axis (= f * u)."""
    a, p = math.radians(YAW_DEG[view]), math.radians(pitch)
    return (math.cos(a), math.sin(a) * math.sin(p))


def foot_path(start, P, lifts, shift=0.0):
    """(offset along body in side px, lift px) per frame. Planted frames step back P each; the swing returns evenly.
    Matches the rhino's paths at P 3, lifts 2,3,2, and the old wolf trot table at P 5, lifts 2,4,4,2, shift 0.5."""
    S = len(lifts)
    half = (8 - S - 1) * P / 2
    out = []
    for f in range(8):
        k = (f - start) % 8
        if k < S:
            out.append((-half + (k + 1) * 2 * half / (S + 1) + shift, lifts[k]))
        else:
            out.append((half - (k - S) * P + shift, 0))
    return out


def swap_lr(name):
    return {'L': 'R', 'R': 'L'}[name[0]] + name[1:]


def load_rgba(path, offset=(0, 0), canvas=None):
    im = Image.open(path).convert('RGBA')
    if canvas and (tuple(offset) != (0, 0) or im.size != (canvas, canvas)):
        c = Image.new('RGBA', (canvas, canvas), (0, 0, 0, 0))
        c.paste(im, tuple(offset))
        im = c
    return np.array(im)


def bottom_profile(alpha):
    prof = np.full(alpha.shape[1], -1)
    for x in range(alpha.shape[1]):
        ys = np.nonzero(alpha[:, x])[0]
        if len(ys):
            prof[x] = ys.max()
    return prof


def count_pieces(alpha):
    H, W = alpha.shape
    seen = np.zeros((H, W), bool)
    sizes = []
    for y0, x0 in zip(*np.nonzero(alpha)):
        if seen[y0, x0]:
            continue
        stack, size = [(y0, x0)], 0
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            size += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and alpha[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
        sizes.append(size)
    return sorted(sizes, reverse=True)


# ---------------------------------------------------------------- stride
def cmd_stride(a):
    tex = TEXEL_M[a.size]
    drawn = a.P * a.fps * tex
    print(f'size {a.size}: texel {tex} m, P {a.P} px a frame at {a.fps} fps -> drawn ground speed {drawn:.3f} m/s')
    print(f'game move_speed {a.move_speed} m/s: playback x{a.move_speed / drawn:.2f}, '
          f'or P {a.move_speed / (a.fps * tex):.1f} px a frame at {a.fps} fps to plant')
    for leg_px in a.leg_px:
        h = leg_px * tex
        line = [f'leg {leg_px} px = {h:.2f} m:']
        for fr in (0.1, 0.25, 0.5):
            v = math.sqrt(fr * GRAVITY * h)
            line.append(f'Fr {fr} -> {v:.2f} m/s (P {v / (a.fps * tex):.1f})')
        line.append(f'| drawn Fr {drawn ** 2 / (GRAVITY * h):.3f}, move_speed Fr {a.move_speed ** 2 / (GRAVITY * h):.2f}')
        print('  ' + '  '.join(line))
    print('Fr about 0.25 is a comfortable walk; animals switch to a run near 0.5 (general knowledge, proposal).')


# ---------------------------------------------------------------- soles
def sole_segments(alpha, tol=1):
    prof = bottom_profile(alpha)
    segs, cur = [], []
    for x in range(len(prof)):
        if prof[x] < 0:
            if cur:
                segs.append(cur)
                cur = []
            continue
        if cur and abs(int(prof[x]) - int(prof[cur[-1]])) > tol:
            segs.append(cur)
            cur = []
        cur.append(x)
    if cur:
        segs.append(cur)
    out = []
    for s in segs:
        low = max(int(prof[x]) for x in s)
        cols = [x for x in s if prof[x] >= low - tol]
        out.append({'x0': min(cols), 'x1': max(cols), 'row': low, 'seg': [s[0], s[-1]]})
    return out


def cmd_soles(a):
    for path in a.images:
        rgba = load_rgba(path, a.offset, a.canvas)
        alpha = rgba[:, :, 3] > 0
        bottom = int(np.nonzero(alpha.any(axis=1))[0].max())
        segs = [s for s in sole_segments(alpha) if s['row'] >= bottom - a.depth]
        print(f'{os.path.basename(path)}: lowest row {bottom}')
        for s in segs:
            print(f"   sole x {s['x0']}-{s['x1']} (w {s['x1'] - s['x0'] + 1}) row {s['row']}  contour run {s['seg']}")


# ---------------------------------------------------------------- gait
def build_targets(feet, gait_name, P, fps, size, lifts, pitch):
    gait, opts = GAITS[gait_name], GAIT_OPTS.get(gait_name, {})
    paths = {foot: foot_path(start, P, lifts, opts.get('shift', 0.0)) for foot, start in gait.items()}
    fore = [f for f in gait if f.endswith('F')] or list(gait)
    dips = opts.get('dips') or sorted({(gait[f] + len(lifts)) % 8 for f in fore})
    t = {'P_side_px': P, 'fps': fps, 'size': size, 'planted_pace_m_s': round(P * fps * TEXEL_M[size], 3),
         'gait_name': gait_name, 'gait': gait, 'lifts': lifts, 'pitch': pitch, 'dip_frames': dips,
         'paths': {k: [list(p) for p in v] for k, v in paths.items()}, 'views': {}}
    for view, vfeet in feet['views'].items():
        vx, vy = view_vec(view, pitch)
        f = math.hypot(vx, vy)
        vt = {'u': [round(vx / f, 4), round(vy / f, 4)], 'f': round(f, 4),
              'planted_step_px': [round(-P * vx, 3), round(-P * vy, 3)], 'visible_feet': {}}
        for foot, (x0, x1, row) in vfeet.items():
            cx = (x0 + x1) / 2
            frames = []
            for i, (off, lift) in enumerate(paths[foot]):
                frames.append({'frame': i, 'offset': off, 'lift': lift,
                               'sole_centre': [round(cx + off * vx, 2), round(row + off * vy - lift, 2)]})
            vt['visible_feet'][foot] = {'still_sole': [x0, x1, row], 'frames': frames}
        t['views'][view] = vt
    return t


def panel(still, vt, frame, dips, scale):
    """Still at low strength, body dipped on dip frames, sole targets drawn on top."""
    H, W = still.shape[:2]
    img = Image.new('RGB', (W, H), (24, 22, 30))
    s = Image.fromarray(still)
    dim = Image.new('RGBA', s.size, (24, 22, 30, 150))
    s = Image.alpha_composite(s, dim)
    img.paste(s, (0, 1 if frame in dips else 0), s)
    img = img.resize((W * scale, H * scale), Image.NEAREST)
    d = ImageDraw.Draw(img)
    for foot, fd in vt['visible_feet'].items():
        x0, x1, row = fd['still_sole']
        w = x1 - x0 + 1
        fr = fd['frames'][frame]
        cx, cy = fr['sole_centre']
        col = COLOURS.get(foot, (255, 255, 255))
        box = [(cx - w / 2) * scale, (cy - 1) * scale, (cx + w / 2) * scale, (cy + 1) * scale]
        if fr['lift'] == 0:
            d.rectangle(box, fill=col)
        else:
            d.rectangle(box, outline=col, width=max(1, scale // 2))
            d.line([cx * scale, (cy + 1) * scale, cx * scale, (cy + 1 + fr['lift']) * scale], fill=col)
        d.text((box[0], box[3] + 2), foot, fill=col)
    d.text((4, 4), f"f{frame}{' dip' if frame in dips else ''}", fill=(230, 230, 230))
    return img


def cmd_gait(a):
    feet = json.load(open(a.feet))
    lifts = [int(v) for v in a.lifts.split(',')] if a.lifts else GAIT_OPTS.get(a.gait, {}).get('lifts', [2, 3, 2])
    t = build_targets(feet, a.gait, a.P, a.fps, a.size, lifts, a.pitch)
    os.makedirs(a.out, exist_ok=True)
    json.dump(t, open(os.path.join(a.out, 'targets.json'), 'w'), indent=1)
    canvas, offset = feet.get('canvas', 192), feet.get('offset', [0, 0])
    gif_frames, crops = [], {}
    stills = {v: load_rgba(os.path.join(a.views_dir, f'{v}.png'), offset, canvas) for v in t['views']}
    for v, st in stills.items():
        ys, xs = np.nonzero(st[:, :, 3])
        m = 14
        crops[v] = (max(0, xs.min() - m), max(0, ys.min() - m), min(canvas, xs.max() + m), min(canvas, ys.max() + m))
    for v, st in stills.items():
        strip = [panel(st, t['views'][v], i, t['dip_frames'], a.scale) for i in range(8)]
        c = [n * a.scale for n in crops[v]]
        strip = [p.crop(c) for p in strip]
        out = Image.new('RGB', (sum(p.width for p in strip), strip[0].height))
        x = 0
        for p in strip:
            out.paste(p, (x, 0))
            x += p.width
        out.save(os.path.join(a.out, f'guide_{v}.png'))
    order = [v for v in VIEWS if v in stills]
    for i in range(8):
        ps = []
        for v in order:
            c = [n * a.scale for n in crops[v]]
            ps.append(panel(stills[v], t['views'][v], i, t['dip_frames'], a.scale).crop(c))
        frame = Image.new('RGB', (sum(p.width for p in ps), max(p.height for p in ps) + 16), (24, 22, 30))
        x = 0
        d = ImageDraw.Draw(frame)
        for v, p in zip(order, ps):
            frame.paste(p, (x, 16))
            d.text((x + 4, 2), v, fill=(230, 230, 230))
            x += p.width
        gif_frames.append(frame)
    gif_frames[0].save(os.path.join(a.out, 'plan.gif'), save_all=True, append_images=gif_frames[1:],
                       duration=int(1000 / a.fps), loop=0)
    print(f"wrote targets.json, guide_<view>.png, plan.gif to {a.out}")
    print(f"gait {a.gait}, P {a.P}, {a.fps} fps, lifts {lifts}, dip frames {t['dip_frames']}, "
          f"drawn {t['planted_pace_m_s']} m/s")
    for v in order:
        print(f"  {v}: planted step {t['views'][v]['planted_step_px']} px a frame, feet {list(t['views'][v]['visible_feet'])}")


# ---------------------------------------------------------------- footlock
def measure_sole(alpha, cx, cy, w, side=3, up=6, down=4):
    H, W = alpha.shape
    xa, xb = max(0, int(math.floor(cx - w / 2 - side))), min(W - 1, int(math.ceil(cx + w / 2 + side)))
    ya, yb = max(0, int(cy) - up), min(H - 1, int(cy) + down)
    lows = {}
    for x in range(xa, xb + 1):
        ys = np.nonzero(alpha[ya:yb + 1, x])[0]
        if len(ys):
            lows[x] = ya + int(ys.max())
    if not lows:
        return None
    seed = min(lows, key=lambda x: abs(lows[x] - cy) + 0.5 * abs(x - cx))
    run = [seed]
    for step in (-1, 1):
        x = seed
        while (x + step) in lows and abs(lows[x + step] - lows[x]) <= 1 and lows[x + step] >= lows[seed] - 2:
            x += step
            run.append(x)
    row = max(lows[x] for x in run)
    cols = [x for x in run if lows[x] >= row - 1]
    return ((min(cols) + max(cols)) / 2, row)


def cmd_footlock(a):
    t = json.load(open(a.targets))
    report, ok_all = {}, True
    still_cols = None
    if a.still_dir:
        still_cols = {}
    for view in (a.views or list(t['views'])):
        vt = t['views'][view]
        frames = [load_rgba(os.path.join(a.frames, a.pattern.format(view=view, i=i))) for i in range(8)]
        alphas = [f[:, :, 3] > 0 for f in frames]
        step = vt['planted_step_px']
        vr = {'feet': {}, 'frames': []}
        print(f'== {view}: planted step {step}')
        for foot, fd in vt['visible_feet'].items():
            w = fd['still_sole'][1] - fd['still_sole'][0] + 1
            meas, err = [], 0.0
            for fr in fd['frames']:
                m = measure_sole(alphas[fr['frame']], fr['sole_centre'][0], fr['sole_centre'][1], w)
                meas.append(m)
                if m:
                    err = max(err, abs(m[0] - fr['sole_centre'][0]), abs(m[1] - fr['sole_centre'][1]))
            planted = [fr['lift'] == 0 for fr in fd['frames']]
            start = next(i for i in range(8) if planted[i] and not planted[(i - 1) % 8])
            run = []
            i = start
            while planted[i] and len(run) < 8:
                run.append(i)
                i = (i + 1) % 8
            corr = [(meas[i][0] - j * step[0], meas[i][1] - j * step[1]) for j, i in enumerate(run) if meas[i]]
            sx = max(c[0] for c in corr) - min(c[0] for c in corr) if corr else None
            sy = max(c[1] for c in corr) - min(c[1] for c in corr) if corr else None
            ok = corr and len(corr) == len(run) and sx <= 2 and sy <= 2
            ok_all &= bool(ok)
            vr['feet'][foot] = {'planted_frames': run, 'spread_px': [sx, sy], 'max_target_error_px': round(err, 2),
                                'measured': meas, 'pass': bool(ok)}
            print(f'   {foot}: planted f{run}, lock spread x {sx:.2f} y {sy:.2f} px, '
                  f'max off target {err:.2f} px -> {"pass" if ok else "CHECK"}')
        still = None
        if a.still_dir:
            still = load_rgba(os.path.join(a.still_dir, f'{view}.png'), a.still_offset, frames[0].shape[0])
            sc = still[still[:, :, 3] > 0][:, :3]
            still_set = {tuple(c) for c in sc}
        for i, (fr, al) in enumerate(zip(frames, alphas)):
            alpha_raw = fr[:, :, 3]
            lowest = int(np.nonzero(al.any(axis=1))[0].max())
            semi = int(((alpha_raw > 0) & (alpha_raw < 255)).sum())
            edge = bool(al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any())
            pieces = count_pieces(al)
            row = {'frame': i, 'lowest_row': lowest, 'semi_alpha_px': semi, 'canvas_edge': edge,
                   'pieces': len(pieces), 'stray_px': sum(pieces[1:])}
            if still is not None:
                fc = fr[al][:, :3]
                row['off_palette_px'] = int(sum(1 for c in map(tuple, fc) if c not in still_set))
            vr['frames'].append(row)
        print('   frames: ' + '; '.join(
            f"f{r['frame']} low {r['lowest_row']} pieces {r['pieces']}"
            + (f" stray {r['stray_px']}" if r['stray_px'] else '')
            + (f" semi {r['semi_alpha_px']}" if r['semi_alpha_px'] else '')
            + (' EDGE' if r['canvas_edge'] else '')
            + (f" offpal {r['off_palette_px']}" if r.get('off_palette_px') else '') for r in vr['frames']))
        report[view] = vr
    if a.out:
        json.dump(report, open(a.out, 'w'), indent=1)
    print('ALL FEET LOCKED' if ok_all else 'SOME FEET NEED A LOOK')


# ---------------------------------------------------------------- seams
BODY_GREENS = {(0x22, 0x30, 0x1d), (0x47, 0x69, 0x3a), (0x6c, 0x9b, 0x4a), (0x9c, 0xcb, 0x62)}  # gorilla body bands


def find_slits(fr, st, dip, n=6):
    """Pixels solid in the idle still (after the dip) but now transparent and enclosed within n px on all four sides:
    the gap a limb leaves when it slides back from a pinned body (gorilla run 1 and 2, 2026-11-05)."""
    a = fr[:, :, 3] > 0
    s = np.zeros_like(a)
    s[dip:] = st[:st.shape[0] - dip, :, 3] > 0
    out = []
    for y, x in zip(*np.nonzero(~a & s)):
        if a[y, max(0, x - n):x].any() and a[y, x + 1:x + 1 + n].any() and a[max(0, y - n):y, x].any() \
                and a[y + 1:y + 1 + n, x].any():
            out.append((int(x), int(y)))
    return out


def fill_colour(fr, st, dip, x, y, done, body):
    """The band on both sides if they agree, else the still's own body colour there, else the next body colour right."""
    row = fr[y]
    op = row[:, 3] > 0
    left = next((tuple(row[i, :3]) for i in range(x - 1, -1, -1) if op[i] or (i, y) in done), None)
    right = next((tuple(row[i, :3]) for i in range(x + 1, row.shape[0]) if op[i]), None)
    if left == right and left in body:
        return left
    sc = tuple(st[y - dip, x, :3]) if st[y - dip, x, 3] else None
    if sc in body:
        return sc
    for i in range(x + 1, row.shape[0]):
        if op[i] and tuple(row[i, :3]) in body:
            return tuple(row[i, :3])
    return right or left


def cmd_seams(a):
    t = json.load(open(a.targets))
    body = {tuple(bytes.fromhex(c)) for c in a.body} if a.body else BODY_GREENS
    if a.fix:
        os.makedirs(a.fix, exist_ok=True)
    for view in (a.views or list(t['views'])):
        st = load_rgba(os.path.join(a.still_dir, f'{view}.png'))
        counts = []
        for i in range(8):
            name = a.pattern.format(view=view, i=i)
            fr = load_rgba(os.path.join(a.frames, name))
            dip = 1 if i in t['dip_frames'] else 0
            sl = find_slits(fr, st, dip)
            counts.append(len(sl))
            if a.fix:
                done = set()
                for x, y in sorted(sl, key=lambda q: (q[1], q[0])):
                    fr[y, x, :3] = fill_colour(fr, st, dip, x, y, done, body)
                    fr[y, x, 3] = 255
                    done.add((x, y))
                Image.fromarray(fr).save(os.path.join(a.fix, name))
        print(f'{view}: enclosed slit px per frame {counts}' + (' (filled)' if a.fix else ''))
    print('Look at every slit before filling: a real gap between a limb and the body must stay open.')


# ---------------------------------------------------------------- mirror
def cmd_mirror(a):
    gait = GAITS[a.gait]
    swing = len(GAIT_OPTS.get(a.gait, {}).get('lifts', [2, 3, 2]))
    up = [sorted(f for f, s in gait.items() if (i - s) % 8 < swing) for i in range(8)]
    print(f'gait {a.gait}: feet up per frame in the drawn views (s, se, e, ne, n)')
    print('frame | drawn up | mirrored view, same frame (physical) | mirrored view at frame+4 (physical) | same?')
    same4 = True
    for i in range(8):
        m0 = sorted(swap_lr(f) for f in up[i])
        m4 = sorted(swap_lr(f) for f in up[(i + 4) % 8])
        same4 &= (m4 == up[i])
        print(f'  f{i}  | {",".join(up[i]) or "-":8} | {",".join(m0) or "-":36} | {",".join(m4) or "-":36} | '
              f'{"yes" if m4 == up[i] else "no"}')
    print('A turn from s to sw (or n to nw) keeps the frame index today, so the up foot swaps sides in one frame.')
    print('Offset +4 keeps the same physical foot up: ' + ('yes, for every frame' if same4 else 'NO, check the gait'))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('stride')
    s.add_argument('--size', choices=TEXEL_M, required=True)
    s.add_argument('--leg-px', type=float, nargs='+', required=True, help='hip or shoulder height above the feet row')
    s.add_argument('--P', type=float, default=3)
    s.add_argument('--fps', type=float, default=8)
    s.add_argument('--move-speed', type=float, default=3.5)
    s = sub.add_parser('soles')
    s.add_argument('images', nargs='+')
    s.add_argument('--offset', type=int, nargs=2, default=[0, 0])
    s.add_argument('--canvas', type=int, default=0)
    s.add_argument('--depth', type=int, default=24, help='list soles up to this many rows over the lowest row')
    s = sub.add_parser('gait')
    s.add_argument('--feet', required=True)
    s.add_argument('--views-dir', required=True)
    s.add_argument('--gait', choices=GAITS, required=True)
    s.add_argument('--P', type=float, default=3)  # float: the fennec trots at 3.5 px a frame
    s.add_argument('--fps', type=int, default=8)
    s.add_argument('--size', choices=TEXEL_M, required=True)
    s.add_argument('--lifts', help='default 2,3,2, or the gait own lifts (trot4: 2,4,4,2)')
    s.add_argument('--pitch', type=float, default=35)
    s.add_argument('--scale', type=int, default=3)
    s.add_argument('--out', required=True)
    s = sub.add_parser('footlock')
    s.add_argument('--targets', required=True)
    s.add_argument('--frames', required=True)
    s.add_argument('--pattern', default='{view}_f{i}.png')
    s.add_argument('--views', nargs='*')
    s.add_argument('--still-dir')
    s.add_argument('--still-offset', type=int, nargs=2, default=[0, 0])
    s.add_argument('--out')
    s = sub.add_parser('seams')
    s.add_argument('--targets', required=True, help='for the views and dip frames')
    s.add_argument('--frames', required=True)
    s.add_argument('--still-dir', required=True, help='stills already on the frame canvas')
    s.add_argument('--pattern', default='{view}_f{i}.png')
    s.add_argument('--views', nargs='*')
    s.add_argument('--body', nargs='*', help='hex colours a fill may use (default: the gorilla greens)')
    s.add_argument('--fix', help='write filled frames to this folder (never over the input)')
    s = sub.add_parser('mirror')
    s.add_argument('--gait', choices=GAITS, required=True)
    a = p.parse_args()
    {'stride': cmd_stride, 'soles': cmd_soles, 'gait': cmd_gait, 'footlock': cmd_footlock, 'seams': cmd_seams,
     'mirror': cmd_mirror}[a.cmd](a)


if __name__ == '__main__':
    main()
