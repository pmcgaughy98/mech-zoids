"""Builds the Codex job that redraws the wolf's walk as a real trot, side view first (Claude, animation lane, 2026-11-04).

Preston on set A's walk: "Legs will need fixing as it looks like they are backpedaling", "For walking only", then,
after it was reversed, "Not really ... Not how a wolf gait would look". foot_lock_test.py showed why: the paws never
travel back under the body (hind paws stay at x 67-90, fore paws at x 103-121 in every frame); they lift and land in
the same spot, so in the game every paw slides. This job draws the trot to an exact foot path and passes only if
foot_lock_test.py shows each planted paw as a dot. Preston: "Yes" (side view first, then the other four views).
Writes codex-walk2/brief.txt and refs/. Launch Codex with the brief.
"""
from pathlib import Path

from PIL import Image

ANIM = Path(__file__).resolve().parent
STILLS = ANIM.parent / "fixed"
OUT = ANIM / "codex-walk2"
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\wolf_m\take-b\anim"
DESIGN = (ANIM / "common.txt").read_text(encoding="utf8").strip()
SELOUT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py"

# Body-relative x offset of each paw from where it stands in the still (+ = forward, toward the head), and its lift
# above the ground in px. Stride 40 px a cycle: a planted paw moves back 5 px a frame, so at 10 fps and 0.018 m a
# texel the planted pace is 5 x 10 x 0.018 = 0.90 m/s. A swinging paw moves forward 3 px a frame relative to the body.
PAIR_A = [(+8, 0), (+3, 0), (-2, 0), (-7, 0), (-4, 2), (-1, 4), (+2, 4), (+5, 2)]
PAIR_B = PAIR_A[4:] + PAIR_A[:4]


def table():
    rows = ["frame | pair A (near fore + far hind) | pair B (far fore + near hind)"]
    for i, (a, b) in enumerate(zip(PAIR_A, PAIR_B)):
        fmt = lambda p: f"{p[0]:+d} px, " + ("ON THE GROUND" if p[1] == 0 else f"lifted {p[1]} px")
        rows.append(f"f{i}    | {fmt(a):28} | {fmt(b)}")
    return "\n".join(rows)


def brief():
    out = ROOT + "\\codex-walk2"
    return f"""You are redrawing a pixel-art walk cycle for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Another Codex job may be writing anim\\codex-set-d; do not touch it or any other
folder. Do not touch assets, art or tools, and do not commit.

{DESIGN}

Why: you drew the wolf's walk in set A (anim\\codex-set-a\\walk; read its prompt, REPORT.txt and gait_finish.py).
Preston, the game's owner, says it is "not how a wolf gait would look". The cause is measured: the paws never travel
back under the body. In every frame the hind paws stay at about x 67-90 and the fore paws at x 103-121; each paw only
lifts and lands in the same spot, so the wolf marches in place with high prancing lifts, and in the game, where the
sprite moves across the ground, every paw slides. Run anim\\foot_lock_test.py on set A to see it:
  python {ROOT}\\foot_lock_test.py codex-set-a/walk/frames side 1.0 check_old {out}
(the last argument is the output folder; it writes check_old.png and .mp4 there).
A paw that is really planted leaves its yellow footprints on one spot; set A's leave one long streak.

Job: redraw the SIDE VIEW walk only (8 frames, 100 ms each, looping), as a real trot. Facing right, like
{ROOT}\\..\\fixed\\e.png. In the still the hind paws stand at about x 63-80 and the fore paws at about x 107-125 on the
ground row 160 (measure each paw yourself). Diagonal pairs move together: pair A = the near foreleg and the far hind
leg, pair B = the far foreleg and the near hind leg. Each paw follows this path, as an x offset from where that paw
stands in the still (+ = forward) and a lift above the ground:
{table()}
So a planted paw slides back exactly 5 px a frame under the body (it stays still on the ground while the body moves
forward over it), and a lifted paw swings forward to land ahead. The legs swing from the hip and shoulder and bend at
the knee, hock and wrist: a planted leg slants forward when it lands (f0 for pair A) and slants back before it lifts
(f3); a lifting fore paw folds back at the wrist, then reaches forward before landing. Leg lengths and thickness stay
the still's. The body stays level, dipping 1 px at f1 and f5; the head stays steady; the tail keeps the still's angle
and thickness with a 1-2 px sway (see anim\\codex-tailfix).

Method: one sheet from your image tool, 8 columns, the side view only, the approved still attached
(refs\\e_6x.png). First build a pose guide with Python (not the image tool): 8 columns showing the still faded with a
coloured mark at each paw's target position for that frame; attach it second and describe the trot beat by beat in
the prompt. Generate exactly ONE image; no redo. Then finish every frame at the still's native pixel scale, snapped to
the colours, and correct the legs by hand until every paw meets its target in the table within 1 px. Do NOT paste
still parts onto generated frames (that caused cutoffs Preston rejected); redraw legs pixel by pixel, whole and joined.

Pass marks (report each):
- foot_lock_test.py on your frames at the planted pace: python {ROOT}\\foot_lock_test.py
  codex-walk2/walk/frames side 0.90 check_new {out}. Every planted paw's footprints stay within 2 px over its 4 ground
  frames (measure the world x of each paw's contact on each of its ground frames and report the spread).
- Every paw's x and lift per frame against the table, within 1 px.
- 192x192 transparent frames, feet on row 160, nothing below it, the stills' 12 colours, binary alpha, dark outline,
  no holes, no stray pixels, nothing touching the canvas edge; proportions within 2 px of the still.
- Judge the boards with the game's sel-out ({SELOUT}, function selout, OUTLINE #141418) at 4x.

Output in {out}: walk\\frames\\side_f0-7.png, sheet_raw.png, the pose guide, grid.json, checks.txt, a preview gif (100
ms, loop), the foot-lock pngs and mp4s, board.png (the still, set A's row, then your row, sel-out, 4x), and REPORT.txt
(under 30 lines): tokens if known, the table check, the foot-lock spreads, and by eye: does it read as a wolf trotting
forward, diagonal pairs together, no prancing, whole legs, no cutoffs?
"""


def main():
    (OUT / "refs").mkdir(parents=True, exist_ok=True)
    im = Image.open(STILLS / "e.png").convert("RGBA")
    im.save(OUT / "refs" / "e.png")
    crop = im.crop(im.getbbox())
    big = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST)
    bg = Image.new("RGBA", (big.width + 96, big.height + 96), (255, 0, 255, 255))
    bg.alpha_composite(big, (48, 48))
    bg.convert("RGB").save(OUT / "refs" / "e_6x.png")
    (OUT / "brief.txt").write_text(brief(), encoding="utf8")
    print(table())


if __name__ == "__main__":
    main()
