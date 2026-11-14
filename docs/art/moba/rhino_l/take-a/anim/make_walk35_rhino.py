"""Free prep for the rhino walk on the 35-degree stills (Claude, animation lane, 2026-11-04). Nothing here is paid.

Hub: Preston, "Whenever rhino is ready get walking animations going for it again"; the rhino is the pilot for frames
at 35 degrees. Stills: ../views_cam35/{s,se,e,ne,n}.png, approved ("Thats it looks good"), installed as the idle.
Writes walk35/: refs/, targets.json, guide_<view>.png (the still faded, a box where each visible foot's sole goes on
each of the 8 frames), brief_run1.txt (e, se, ne) and brief_run2.txt (s, n). The briefs are NOT launched: paid
generation waits for Preston's yes on the price.

The gait is the approved one (retro-walk/pixellab/front_skeleton.py, from the Retro side walk Preston approved): a
four-beat walk; each foot swings 3 frames and a new foot starts every 2, so one foot is up on even frames
and two on odd frames (my first wording, "one foot in the air at a time", was wrong; Codex run 1 caught it). Left fore swings f1-f3, left hind f3-f5, right fore f5-f7, right hind
f7-f1. A planted foot slides back P px a frame (side view) for 5 frames, offsets +2P, +P, 0, -P, -2P; a swinging
foot moves forward through -P, 0, +P lifted 2, 3, 2 px. P = 3: at 8 fps and 0.020 m a texel the planted pace is
3 x 8 x 0.020 = 0.48 m/s, today's rhino walk pace (playbook section 6).
How the path shows in each view comes from the game camera, not from the still's drawing: 35 degrees down, view yaw
0/45/90/135/180. A step d along the body shows on screen as d * f * u:
  e  u (1, 0)            f 1.0
  se u (0.867, 0.497)    f 0.815  (cos45 = 0.707 across, sin45 x sin35 = 0.406 down)
  ne u (0.867, -0.497)   f 0.815
  s  u (0, 1)            f 0.574  (sin35: toward the camera is down the screen)
  n  u (0, -1)           f 0.574
Lift shows straight up the screen. Near side: facing e, se or ne the rhino's right side is toward the camera.
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ANIM = Path(__file__).resolve().parent
STILLS = ANIM.parent / "views_cam35"
OUT = ANIM / "walk35"
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a"
SELOUT = ROOT + r"\anim\selout_rhino.py"
P, FPS, M_PER_TX, N = 3, 8, 0.020, 8
SWING_START = {"LF": 1, "LH": 3, "RF": 5, "RH": 7}
STANCE = (2, 1, 0, -1, -2)          # x P, frames after the swing
SWING = ((-1, 2), (0, 3), (1, 2))   # (offset x P, lift px)
A = math.radians(35)
AXIS = {"e": ((1, 0), 1.0), "s": ((0, 1), math.sin(A)), "n": ((0, -1), math.sin(A))}
for v, sy in (("se", 1), ("ne", -1)):
    dx, dy = math.cos(math.radians(45)), sy * math.sin(math.radians(45)) * math.sin(A)
    AXIS[v] = ((dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)), math.hypot(dx, dy))
# Visible feet in each still, measured 2026-11-04 (x span of the sole, sole row). se/ne names are my reading of the
# stills; Codex confirms them. Feet not listed are hidden by the body in the still.
FEET = {
    "e": {"RH": (52, 75, 160), "RF": (92, 114, 160)},
    "s": {"RF": (63, 86, 160), "LF": (104, 128, 160)},
    "n": {"LH": (64, 87, 160), "RH": (105, 128, 160)},
    "se": {"LH": (54, 76, 143), "RH": (77, 100, 160), "RF": (108, 133, 155)},
    "ne": {"LH": (54, 76, 150), "RH": (77, 101, 160), "RF": (105, 127, 139)},
}
COL = {"LF": (255, 80, 80), "RF": (80, 160, 255), "LH": (255, 200, 40), "RH": (120, 230, 120)}


def path(leg):
    """(offset in side px, lift px) for frames 0-7."""
    out = [None] * N
    s = SWING_START[leg]
    for k, (o, lift) in enumerate(SWING):
        out[(s + k) % N] = (o * P, lift)
    for k, o in enumerate(STANCE):
        out[(s + 3 + k) % N] = (o * P, 0)
    return out


def targets():
    t = {"P_side_px": P, "fps": FPS, "planted_pace_m_s": round(P * FPS * M_PER_TX, 3), "gait": SWING_START,
         "paths": {leg: path(leg) for leg in SWING_START}, "views": {}}
    for v, ((ux, uy), f) in AXIS.items():
        feet = {}
        for leg, (x0, x1, row) in FEET[v].items():
            fr = []
            for i, (d, lift) in enumerate(path(leg)):
                fr.append({"frame": i, "offset": d, "lift": lift, "sole_centre": [round((x0 + x1) / 2 + d * f * ux, 2),
                           round(row + d * f * uy - lift, 2)]})
            feet[leg] = {"still_sole": [x0, x1, row], "frames": fr}
        t["views"][v] = {"u": [round(ux, 4), round(uy, 4)], "f": round(f, 4),
                         "planted_step_px": [round(-P * f * ux, 3) + 0.0, round(-P * f * uy, 3) + 0.0],
                         "visible_feet": feet}
    return t


def guide(v, t):
    a = np.asarray(Image.open(STILLS / f"{v}.png").convert("RGBA")).copy()
    a[..., 3] = (a[..., 3] > 0) * 110
    K, box = 3, (30, 40, 162, 172)
    w, h = (box[2] - box[0]) * K, (box[3] - box[1]) * K
    img = Image.new("RGB", (N * w + (N - 1) * 4, h + 24), (70, 80, 76))
    dr = ImageDraw.Draw(img)
    still = Image.fromarray(a).crop(box).resize((w, h), Image.NEAREST)
    for i in range(N):
        x0 = i * (w + 4)
        img.paste(still, (x0, 24), still)
        dr.text((x0 + 4, 4), f"{v} f{i}", fill=(240, 240, 240))
        dr.line([(x0, 24 + (160 - box[1]) * K + K), (x0 + w, 24 + (160 - box[1]) * K + K)], fill=(150, 140, 110))
        for leg, d in t["views"][v]["visible_feet"].items():
            sx0, sx1, _ = d["still_sole"]
            cx, cy = d["frames"][i]["sole_centre"]
            half = (sx1 - sx0) / 2
            r = [x0 + (cx - half - box[0]) * K, 24 + (cy - 3 - box[1]) * K, x0 + (cx + half - box[0]) * K,
                 24 + (cy - box[1] + 1) * K]
            dr.rectangle(r, outline=COL[leg], width=2 if d["frames"][i]["lift"] == 0 else 1)
            dr.text((r[0] + 2, r[1] - 12), leg + ("" if d["frames"][i]["lift"] == 0 else f" +{d['frames'][i]['lift']}"),
                    fill=COL[leg])
    img.save(OUT / f"guide_{v}.png")


def brief(views, run, t):
    out = ROOT + r"\anim\walk35"
    rows = "\n".join(f"  {v}: u = ({t['views'][v]['u'][0]}, {t['views'][v]['u'][1]}), f = {t['views'][v]['f']}; a planted "
                     f"foot moves ({t['views'][v]['planted_step_px'][0]:+.2f}, {t['views'][v]['planted_step_px'][1]:+.2f})"
                     f" px a frame on the canvas (x, y; y down)" for v in views)
    extra = ("" if run == 1 else """
Front and back are the hard views: on this rhino, five earlier straight front/back walks from prompted tools
(Codex twice, Retro twice, PixelLab once) stacked the legs, moved both together, stretched them or grew parts. Do not
describe the walk to a tool; pose the still's own legs to the foot path below by hand. At 35 degrees the legs no
longer stack: a foot's travel shows as up-down movement on screen (0.57 of its length), so a planted fore foot in s
slides UP the screen as it goes back under the body, and a swinging foot comes down the screen as it reaches forward.
The far legs are hidden by the body in these stills: draw them only where the new pose shows them.
Run 1 (e, se, ne) is done and approved: its frames in walk\\frames are final, so do not change or delete them; its
report and boards are kept in walk35\\run1. Match its leg drawing (cuffs, discs, soles) in s and n.""")
    return f"""You are making pixel-art walk frames for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Do not touch any other folder, assets, art or tools, and do not commit.

The machine: the yellow L rhino (mech), approved stills at 35 degrees in {ROOT}\\views_cam35 (s, se, e, ne, n), 192x192,
lowest foot on row 160, 12 colours. Preston, the game's owner, approved these stills; they are the idle in the game,
so the walk must match them exactly above the legs or the switch from idle to walk pops. Read
D:\\dev\\new-mech-rpg\\docs\\art\\moba\\ANIMATION_PLAYBOOK.md sections 1, 4, 5 and 9 first, and
D:\\dev\\new-mech-rpg\\docs\\art\\moba\\wolf_m\\take-b\\anim\\codex-walk4 (REPORT.txt, build.py, verify.py): the method that
worked last, a wolf trot re-posed from its stills to a foot path with a 2D foot-lock check.

Job, run {run}: an 8-frame walk, 125 ms a frame (8 fps), looping, in these views: {", ".join(views)}. The gait is the
one Preston approved for this rhino: a four-beat walk; each foot swings 3 frames and a new foot starts every 2,
so one foot is up on even frames and two on odd frames. Left fore swings f1-f3, left
hind f3-f5, right fore f5-f7, right hind f7-f1. Each foot's path (offset along the body in side-view px, + = forward,
and lift) is in {out}\\targets.json "paths"; per view the path turns into screen px as offset * f * u, lift straight up:
{rows}
So a planted foot keeps one spot on the ground while the body moves forward. targets.json "views" gives the sole
centre of every foot visible in each still for every frame; guide_<view>.png shows them (the still faded, a box per
foot per frame, thick = planted, thin = lifted). The se/ne foot names are my reading of the stills; check them and
say if one is wrong. A foot hidden in the still: draw it only where the new pose shows it.{extra}

Method: no image tool, native pixels, the way codex-walk4 did it. The body, head, horn, plates and tail are the
approved still, pixel for pixel, dipping 1 px on f0 and f4 (a fore foot lands). The legs are the still's own legs
re-posed: thigh or shoulder plate, knee disc, cuff, foot block, each the still's own pixels TRANSLATED, never
rotated or resampled (run 1 rotated its shanks and the rotation left dark specks and slivers that a 78k-token cleanup
had to remove; see anim\\walk35\\clean\\REPORT.txt and cleanup.py, and work the way the cleanup did). Where a leg leans,
step the parts 1 px per row or redraw the shank by hand in the still's colours and bands. Every joint and every join with the body is redrawn by
hand: no seams, no straight cut edges, no gaps, no part ending abruptly (pasted parts that did not join are what
Preston rejected before). The legs are short: keep each leg's length within 1 px of the still's.

Pass marks (report each):
- Foot lock: for each foot, its sole centre on its k-th planted frame (k = 0 to 4 in order, wrapping past f7) minus
  k times the planted step above stays within 2 px in x and y. Measure from the frame pixels, not from your targets.
  Write a footprint picture per view.
- Each visible foot meets its target in targets.json within 1 px; lifts exact.
- Above the legs every frame equals the still (after the 1 px dip): report the % of differing pixels per frame.
- 192x192 transparent frames, the stills' 12 colours, binary alpha, dark outline, no holes, no stray pixels, nothing
  touching the canvas edge. A planted foot nearer the camera than in the still may sit below row 160 (perspective);
  report each frame's lowest row.
- Judge boards with the game's sel-out ({SELOUT}, function selout) at 4x, the still beside them.

Output in {out}: walk\\frames\\<view>_f0-7.png for {", ".join(views)}, a preview gif per view (125 ms, loop),
footprint pictures, board.png (per view: the still, then your 8 frames, sel-out, 4x), checks.txt, and REPORT.txt
(under 30 lines): tokens if known, the foot names you used, the foot-lock spreads, target errors, upper-body match,
lowest rows, and by eye: does each view read as this rhino walking forward in the four-beat walk, legs like the still,
whole and clean?
"""


def main():
    (OUT / "refs").mkdir(parents=True, exist_ok=True)
    for v in AXIS:
        Image.open(STILLS / f"{v}.png").save(OUT / "refs" / f"{v}.png")
    t = targets()
    (OUT / "targets.json").write_text(json.dumps(t, indent=1), encoding="utf8")
    for v in AXIS:
        guide(v, t)
    (OUT / "brief_run1.txt").write_text(brief(("e", "se", "ne"), 1, t), encoding="utf8")
    (OUT / "brief_run2.txt").write_text(brief(("s", "n"), 2, t), encoding="utf8")
    for v in ("e", "se", "ne", "s", "n"):
        print(v, t["views"][v]["u"], t["views"][v]["f"], "step", t["views"][v]["planted_step_px"])
    print("pace", t["planted_pace_m_s"], "m/s; paths", t["paths"])


if __name__ == "__main__":
    main()
