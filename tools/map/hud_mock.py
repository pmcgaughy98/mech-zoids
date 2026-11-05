"""HUD mock-up, draft A. Map design lane, 2026-11-05 (docs/plan/moba-hud-reimagine-2026-11-05.md).

Paints the proposed match HUD as pixel art at the 320 x 180 base over two chase-camera frames from
tools/map/hud_mock_shot.gd, then scales 4x with nearest neighbour.
  Panel A: minimap upper right (SMITE's corner).  Panel B: minimap bottom right (today's corner).
5 v 5 is shown (4 allies, 5 enemies). Portraits are sprite frames scaled down; ability icons are stand-ins.
Layout only: the look is ours (steel plates, rivets, hazard trim), nothing copied from SMITE.

python tools/map/hud_mock.py <shot_dir> <out.png>
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

W, H, S = 320, 180, 4
PLATE, PLATE_HI, PLATE_LO, EDGE = (26, 29, 37), (60, 66, 80), (14, 15, 20), (6, 7, 10)
RIVET = (110, 116, 132)
HAZ_Y, HAZ_K = (236, 184, 38), (24, 24, 26)
BLUE, RED, GOLD = (89, 158, 255), (255, 87, 71), (255, 199, 77)
GREEN, WHITE, DIM, GREY = (107, 255, 115), (240, 240, 240), (150, 156, 168), (100, 102, 108)
BAR_BG = (10, 10, 13)

FONT = {
    'A': ["010", "101", "111", "101", "101"], 'B': ["110", "101", "110", "101", "110"],
    'C': ["011", "100", "100", "100", "011"], 'D': ["110", "101", "101", "101", "110"],
    'E': ["111", "100", "110", "100", "111"], 'F': ["111", "100", "110", "100", "100"],
    'G': ["011", "100", "101", "101", "011"], 'H': ["101", "101", "111", "101", "101"],
    'I': ["111", "010", "010", "010", "111"], 'J': ["001", "001", "001", "101", "010"],
    'K': ["101", "101", "110", "101", "101"], 'L': ["100", "100", "100", "100", "111"],
    'M': ["101", "111", "101", "101", "101"], 'N': ["110", "101", "101", "101", "101"],
    'O': ["010", "101", "101", "101", "010"], 'P': ["110", "101", "110", "100", "100"],
    'Q': ["010", "101", "101", "110", "011"], 'R': ["110", "101", "110", "101", "101"],
    'S': ["011", "100", "010", "001", "110"], 'T': ["111", "010", "010", "010", "010"],
    'U': ["101", "101", "101", "101", "111"], 'V': ["101", "101", "101", "101", "010"],
    'W': ["101", "101", "101", "111", "101"], 'X': ["101", "101", "010", "101", "101"],
    'Y': ["101", "101", "010", "010", "010"], 'Z': ["111", "001", "010", "100", "111"],
    '0': ["111", "101", "101", "101", "111"], '1': ["010", "110", "010", "010", "111"],
    '2': ["110", "001", "010", "100", "111"], '3': ["110", "001", "010", "001", "110"],
    '4': ["101", "101", "111", "001", "001"], '5': ["111", "100", "110", "001", "110"],
    '6': ["011", "100", "111", "101", "111"], '7': ["111", "001", "010", "010", "010"],
    '8': ["111", "101", "111", "101", "111"], '9': ["111", "101", "111", "001", "110"],
    ':': ["0", "1", "0", "1", "0"], '/': ["001", "001", "010", "100", "100"],
    '.': ["0", "0", "0", "0", "1"], ',': ["0", "0", "0", "1", "1"], '-': ["000", "000", "111", "000", "000"],
    '>': ["100", "010", "001", "010", "100"], '+': ["000", "010", "111", "010", "000"],
    '!': ["1", "1", "1", "0", "1"], ' ': ["00", "00", "00", "00", "00"],
}

DIG = {  # 4 x 6, cooldown seconds only
    '0': [".##.", "#..#", "#..#", "#..#", "#..#", ".##."], '1': [".#..", "##..", ".#..", ".#..", ".#..", "###."],
    '2': [".##.", "#..#", "..#.", ".#..", "#...", "####"], '3': ["###.", "...#", ".##.", "...#", "...#", "###."],
    '4': ["#..#", "#..#", "####", "...#", "...#", "...#"], '5': ["####", "#...", "###.", "...#", "...#", "###."],
    '6': [".##.", "#...", "###.", "#..#", "#..#", ".##."], '7': ["####", "...#", "..#.", ".#..", ".#..", ".#.."],
    '8': [".##.", "#..#", ".##.", "#..#", "#..#", ".##."], '9': [".##.", "#..#", "#..#", ".###", "...#", ".##."],
}


def dw(s):
    return len(s) * 5 - 1


ICONS = {  # 9 x 9 stand-ins for the rhino's kit
    "horn": ["........#", ".......##", "......##.", ".....##..", "....###..",
             "...###...", "..####...", ".#####...", "#######.."],
    "pound": ["...###...", "...###...", "...###...", ".#######.", "..#####..",
              "...###...", "....#....", ".........", "#########"],
    "brace": ["#########", "#.......#", "#.#####.#", "#.#####.#", "#.#####.#",
              ".#.###.#.", ".#.###.#.", "..#.#.#..", "....#...."],
    "stampede": [".........", "#...#....", ".#...#...", "..#...#..", "...#...#.",
                 "..#...#..", ".#...#...", "#...#....", "........."],
}
SMALL = {  # 5 x 5
    "attack": ["..#..", "..#..", "##.##", "..#..", "..#.."],
    "recall": ["..#..", ".###.", "#####", ".#.#.", ".###."],
    "up": ["..#..", ".###.", "#.#.#", "..#..", "..#.."],
    "shield": ["#####", "#####", "#####", ".###.", "..#.."],
    "slow": ["..#..", "..#..", "#.#.#", ".###.", "..#.."],
}


def tw(s):
    return sum(len(FONT[c][0]) + 1 for c in s) - 1


def text(img, x, y, s, col, shadow=True, k=1, outline=False, font=None):
    font = font or FONT
    for c in s:
        g = font[c]
        for r, row in enumerate(g):
            for q, bit in enumerate(row):
                if bit in "1#":
                    for a in range(k):
                        for b in range(k):
                            if outline:
                                for ox, oy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
                                    put(img, x + q * k + a + ox, y + r * k + b + oy, EDGE)
                            elif shadow:
                                put(img, x + q * k + a + 1, y + r * k + b + 1, EDGE)
        for r, row in enumerate(g):
            for q, bit in enumerate(row):
                if bit in "1#":
                    for a in range(k):
                        for b in range(k):
                            put(img, x + q * k + a, y + r * k + b, col)
        x += (len(g[0]) + 1) * k


def put(img, x, y, col):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), col)


def glyph(img, x, y, rows, col):
    for r, row in enumerate(rows):
        for q, ch in enumerate(row):
            if ch == "#":
                put(img, x + q, y + r, col)


def plate(d, x, y, w, h, trim=False, rivets=True):
    d.rectangle([x - 1, y - 1, x + w, y + h], fill=EDGE)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=PLATE)
    d.line([x, y, x + w - 1, y], fill=PLATE_HI)
    d.line([x, y + h - 1, x + w - 1, y + h - 1], fill=PLATE_LO)
    if rivets and w >= 30 and h >= 14:
        for rx, ry in [(x + 2, y + 2 + (2 if trim else 0)), (x + w - 3, y + 2 + (2 if trim else 0)),
                       (x + 2, y + h - 3), (x + w - 3, y + h - 3)]:
            d.point((rx, ry), fill=RIVET)
    if trim:
        for xx in range(x, x + w):
            for yy in (y, y + 1):
                d.point((xx, yy), fill=HAZ_Y if ((xx + yy) // 2) % 2 == 0 else HAZ_K)


def bar(d, x, y, w, h, share, col):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=BAR_BG)
    n = round(w * max(0.0, min(1.0, share)))
    if n > 0:
        d.rectangle([x, y, x + n - 1, y + h - 1], fill=col)
        hi = tuple(min(255, int(c * 0.6 + 255 * 0.4)) for c in col)
        d.line([x, y, x + n - 1, y], fill=hi)
        if h >= 3:
            lo = tuple(int(c * 0.7) for c in col)
            d.line([x, y + h - 1, x + n - 1, y + h - 1], fill=lo)


def shade(img, box, k):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            if 0 <= xx < img.width and 0 <= yy < img.height:
                r, g, b = img.getpixel((xx, yy))
                img.putpixel((xx, yy), (int(r * k), int(g * k), int(b * k)))


def grey(img, box):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            r, g, b = img.getpixel((xx, yy))
            v = int(0.3 * r + 0.59 * g + 0.11 * b) // 2 + 30
            img.putpixel((xx, yy), (v, v, v + 4))


def load_port(path, size):
    im = Image.open(path).convert("RGBA")
    bb = im.getchannel("A").getbbox()
    if bb:
        im = im.crop(bb)
    w, h = im.size
    side = min(w, h)
    im = im.crop(((w - side) // 2, 0, (w - side) // 2 + side, side))
    im = im.resize((size, size), Image.LANCZOS)
    bg = Image.new("RGBA", (size, size), (44, 48, 60, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB").quantize(12).convert("RGB")


def portrait(img, d, port, x, y, size, rim, state=""):
    d.rectangle([x, y, x + size - 1, y + size - 1], fill=rim)
    img.paste(port.resize((size - 2, size - 2), Image.NEAREST), (x + 1, y + 1))
    inner = (x + 1, y + 1, x + size - 2, y + size - 2)
    if state == "low":
        grey(img, inner)
    elif isinstance(state, int):
        grey(img, inner)
        shade(img, inner, 0.45)
        s = str(state)
        text(img, x + (size - tw(s)) // 2, y + (size - 5) // 2, s, WHITE)


def diamond(img, x, y, share, col):
    rows = ["..#..", ".###.", "#####", ".###.", "..#.."]
    for r, row in enumerate(rows):
        for q, ch in enumerate(row):
            if ch == "#":
                lit = (4 - r) / 4.0 < share or share >= 1.0
                put(img, x + q, y + r, col if lit else (60, 58, 52))
    if share >= 1.0:
        put(img, x + 2, y + 1, WHITE)


def slot(img, d, x, y, n, key, icon, cd_share=0.0, cd_left=0, ready_flash=False, small=False):
    d.rectangle([x - 1, y - 1, x + n, y + n], fill=EDGE)
    d.rectangle([x, y, x + n - 1, y + n - 1], fill=(40, 44, 54))
    d.line([x, y, x + n - 1, y], fill=PLATE_HI)
    if not small:
        glyph(img, x + 3, y + 3, ICONS[icon], (214, 218, 228))
    if cd_share > 0:
        cx, cy = x + n / 2.0, y + n / 2.0
        for yy in range(y, y + n):
            for xx in range(x, x + n):
                a = (math.degrees(math.atan2(xx + 0.5 - cx, -(yy + 0.5 - cy))) + 360.0) % 360.0
                if a < cd_share * 360.0:
                    r, g, b = img.getpixel((xx, yy))
                    img.putpixel((xx, yy), (int(r * 0.3), int(g * 0.3), int(b * 0.34)))
        s = str(cd_left)  # while cooling, the seconds replace the key label so "2" and "4" never read as 24
        text(img, x + (n - dw(s)) // 2, y + (n - 6) // 2, s, WHITE, outline=True, font=DIG)
    elif key and not small:
        text(img, x + 1, y + 1, key, GOLD)
    if small:
        text(img, x + (n - tw(key)) // 2, y + (n - 5) // 2, key, GOLD, shadow=False)
    if ready_flash:
        d.rectangle([x - 1, y - 1, x + n, y + n], outline=WHITE)


def dotted(img, a, b, col):
    (x0, y0), (x1, y1) = a, b
    n = int(max(abs(x1 - x0), abs(y1 - y0)))
    for i in range(n + 1):
        if (i // 2) % 2 == 0:
            t = i / max(n, 1)
            put(img, round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), col)


def hud(frame, anchors, ports, map_corner):
    img = frame.copy()
    d = ImageDraw.Draw(img)
    vx = anchors["viewport"][0]
    k = W / vx

    # tower aggro: a line from red's tower to you (feel rule), drawn under the HUD
    if anchors.get("tower"):
        t = (anchors["tower"][0] * k, max(anchors["tower"][1] * k, 34))
        c = (anchors["bar"][0] * k, anchors["bar"][1] * k - 3)
        dotted(img, t, c, RED)
    # your overhead bar
    bx, by = round(anchors["bar"][0] * k) - 8, round(anchors["bar"][1] * k)
    d.rectangle([bx - 1, by - 1, bx + 16, by + 2], fill=EDGE)
    bar(d, bx, by, 16, 2, 0.62, GREEN)

    # top centre, kept thin: the lane ahead (and the tower you are pushing) sits right under it in a chase camera
    sx, sw = 122, 76
    plate(d, sx, 2, sw, 10, rivets=False)
    text(img, 160 - tw("14:32") // 2, 4, "14:32", WHITE, shadow=False)
    text(img, sx + 3, 4, "7", BLUE, shadow=False)
    text(img, sx + sw - 3 - tw("5"), 4, "5", RED, shadow=False)
    for col, x0 in ((BLUE, sx + 9), (RED, sx + sw - 19)):
        d.rectangle([x0, 5, x0 + 2, 8], fill=col)  # tower pip
        glyph(img, x0 + 4, 4, ["..#..", ".###.", "#####", ".###.", "..#.."], col)  # core pip
    text(img, 160 - tw("WAVE 0:18") // 2, 14, "WAVE 0:18", DIM, outline=True)
    # the nearby structure's health, only when near, no plate
    text(img, 160 - tw("RED TOWER") // 2, 22, "RED TOWER", RED, outline=True)
    d.rectangle([130, 28, 189, 31], fill=EDGE)
    bar(d, 131, 29, 58, 2, 0.7, RED)

    # kill messages near the centre, fading
    kills = [((("FENNEC", BLUE), (" > ", WHITE), ("WOLF", RED)), 1.0),
             ((("TOWER", RED), (" > ", WHITE), ("KANGAROO", BLUE)), 0.55)]
    for i, (parts, fade) in enumerate(kills):
        s = "".join(p for p, _ in parts)
        x = 5
        y = 75 + i * 8
        shade(img, (x - 2, y - 1, x + tw(s) + 1, y + 5), 0.45)
        for p, col in parts:
            text(img, x, y, p, tuple(int(c * fade) for c in col), shadow=False)
            x += tw(p) + 1

    # top left: allies (4 in 5 v 5), portrait, health, ultimate pip
    allies = [("ape", 0.8, 1.0, ""), ("fennec", 0.45, 0.6, ""), ("hippo", 1.0, 1.0, ""), ("kangaroo_m", 0.0, 0.3, 9)]
    for i, (kind, hp, ult, state) in enumerate(allies):
        y = 3 + i * 17
        plate(d, 3, y, 42, 15, rivets=False)
        portrait(img, d, ports[kind], 4, y + 1, 13, BLUE, state)
        bar(d, 19, y + 5, 18, 3, hp, BLUE)
        diamond(img, 39, y + 4, ult, GOLD)

    # top right: enemies (5), portrait greys at low health, respawn timer when down
    enemies = [("pangolin_m", ""), ("shoebill_m", "low"), ("wolf_m", 18), ("hippo_m", ""), ("ape_l", "")]
    ex = W - 3 - (5 * 15 - 2)
    plate(d, ex - 1, 2, 5 * 15, 15, rivets=False)
    for i, (kind, state) in enumerate(enemies):
        portrait(img, d, ports[kind], ex + i * 15, 3, 13, RED, state)

    # bottom centre: the player bar with hazard trim, buffs above it
    px0, py0, pw, ph = 98, 149, 124, 29
    plate(d, px0, py0, pw, ph, trim=True)
    portrait(img, d, ports["rhino"], px0 + 3, py0 + 5, 21, GREEN)
    hx, hw = px0 + 27, pw - 31
    s = "620/1000"
    bar(d, hx, py0 + 4, hw - tw(s) - 3, 7, 0.62, GREEN)
    text(img, hx + hw - tw(s), py0 + 5, s, WHITE, shadow=False)
    sy = py0 + 14
    slot(img, d, hx, sy, 13, "1", "horn", ready_flash=True)
    slot(img, d, hx + 16, sy, 13, "2", "pound", 0.55, 4)
    slot(img, d, hx + 32, sy, 13, "3", "brace")
    slot(img, d, hx + 48, sy, 13, "4", "stampede", 0.8, 38)
    slot(img, d, hx + 66, sy + 2, 11, "SP", "attack", small=True)
    slot(img, d, hx + 80, sy + 2, 11, "B", "recall", small=True)
    # tower-aggro icon on your own bar (feel rule)
    glyph(img, px0 + 18, py0 - 4, ["...#...", "..###..", "..#.#..", ".##.##.", ".#####.", "##.#.##", "#######"], RED)
    # buffs left, debuffs right, above the bar
    for x, icon, col in ((hx, "up", GREEN), (hx + 8, "shield", BLUE), (px0 + pw - 8, "slow", RED)):
        d.rectangle([x - 1, py0 - 10, x + 7, py0 - 2], fill=EDGE)
        d.rectangle([x, py0 - 9, x + 6, py0 - 3], fill=PLATE)
        glyph(img, x + 1, py0 - 8, SMALL[icon], col)

    # bottom left: kills, deaths, assists; item slots reserved for when items exist
    plate(d, 3, 156, 52, 21, rivets=False)
    text(img, 5, 158, "2/0/1", WHITE, shadow=False)
    text(img, 53 - tw("KDA"), 158, "KDA", DIM, shadow=False)
    for i in range(6):
        x = 5 + i * 8
        for q in range(7):
            if q % 2 == 0:
                for p in ((x + q, 166), (x + q, 172), (x, 166 + q), (x + 6, 166 + q)):
                    put(img, p[0], p[1], GREY)
    return img


def base(path):
    im = Image.open(path).convert("RGB")
    return im if im.size == (W, H) else im.resize((W, H), Image.NEAREST)


def main():
    shot, out = sys.argv[1], sys.argv[2]
    anchors = json.load(open(os.path.join(shot, "anchors.json")))
    ports = {}
    for f in os.listdir(shot):
        if f.startswith("port_"):
            ports[f[5:-4]] = load_port(os.path.join(shot, f), 21)
    have = sorted(ports)  # machines without a <kind>_frames.tres borrow the ones that have one, in turn
    wanted = ["rhino", "ape", "fennec", "hippo", "kangaroo_m", "pangolin_m", "shoebill_m", "wolf_m", "hippo_m", "ape_l"]
    for i, kind in enumerate(k for k in wanted if k not in ports):
        ports[kind] = ports[have[(i + 1) % len(have)]]
    a = hud(base(os.path.join(shot, "frame_a.png")), anchors, ports, "upper")
    b = hud(base(os.path.join(shot, "frame_b.png")), anchors, ports, "lower")
    cap, foot = 40, 34
    board = Image.new("RGB", (W * S, 2 * (H * S + cap) + foot), (14, 15, 19))
    bd = Image.new("RGB", (W, 1))
    for i, (im, label) in enumerate(((a, "A  MINIMAP UPPER RIGHT, LIKE SMITE"), (b, "B  MINIMAP BOTTOM RIGHT, AS TODAY"))):
        y = i * (H * S + cap)
        text(board, 16, y + 10, label, WHITE, shadow=False, k=4)
        board.paste(im.resize((W * S, H * S), Image.NEAREST), (0, y + cap))
    note = "5 V 5 SHOWN. 3 V 3 DROPS TWO ALLY AND TWO ENEMY FRAMES. PORTRAITS AND ICONS ARE STAND-INS."
    text(board, 16, board.height - foot + 10, note, DIM, shadow=False, k=2)
    board.save(out)
    a.resize((W * S, H * S), Image.NEAREST).save(out.replace(".png", "_a.png"))
    print("saved", out, board.size)


if __name__ == "__main__":
    main()
