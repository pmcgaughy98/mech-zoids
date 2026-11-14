"""Builds the wolf's remaining Codex jobs (Claude, animation lane, 2026-11-04).

Preston, after set A's boards: "When you are done making animations show me a video with all animations. Also number
them so I can tell you what models are wrong or have issues."
- codex-tailfix: set A's side walk and side sprint drew the tail as a thin level rod; redraw only those tails.
- codex-set-c: se and ne for walk, sprint, lunge, bite (column text from codex-set-a's prompts).
- codex-set-d: se and ne for hamstring, howl, death (column text from codex-set-b's prompts; launch after set B).
The se and ne idles are already built from the stills by idle/make_idle.py. Same method as the fennec's
make_codex_diag_fennec.py. Run make_codex_wolf.py first (it writes common.txt).
"""
from pathlib import Path

import numpy as np
from PIL import Image

ANIM = Path(__file__).resolve().parent
STILLS = ANIM.parent / "fixed"
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\wolf_m\take-b\anim"
SELOUT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py"
DESIGN = (ANIM / "common.txt").read_text(encoding="utf8").strip()
SETS = {"codex-set-c": [("walk", "codex-set-a", 8), ("sprint", "codex-set-a", 6), ("lunge", "codex-set-a", 7),
                        ("bite", "codex-set-a", 5)],
        "codex-set-d": [("hamstring", "codex-set-b", 6), ("howl", "codex-set-b", 6), ("death", "codex-set-b", 7)]}
TIMING = {"walk": "100 ms each, loop", "sprint": "70 ms each, loop", "lunge": "120, 180, 80, 120, 90, 160, 200",
          "bite": "100, 120, 80, 140, 160", "hamstring": "120, 120, 80, 100, 160, 200",
          "howl": "160, 160, 200, 500, 250, 220", "death": "300, 100, 130, 140, 160, 180, 1400"}
LAYOUT = (
    "Layout: a grid of 2 rows and N columns of equal cells, one whole wolf per cell, nothing crossing a cell edge, "
    "no labels, no text, no grid lines. Row 1 is the three-quarter front view facing down and to the right, exactly "
    "the camera angle of the first attached sprite: we see its face, muzzle, fangs and cyan eyes. Row 2 is the "
    "three-quarter back view facing up and to the right, exactly the camera angle of the second attached sprite: we "
    "see its back, the fins and the backs of its ears, and its head points away. Every cell in a row keeps that row's "
    "angle: never turn it to a straight front, side or back view, and never mirror it. Each column is one moment seen "
    "from two angles, so the two rows match frame for frame. The wolf is the same size in every cell and the ground "
    "line is at the same height in every cell.")
TAIL = ("The tail keeps the still's thickness, plate count and red tip in every frame (never a thin rod). In the walk it "
        "keeps the still's angle, its root moving with the body and its tip swaying 1-2 px with the trot; in the sprint "
        "it may stream back closer to level, at the same thickness.")


def size(v):
    a = np.asarray(Image.open(STILLS / f"{v}.png").convert("RGBA"))[..., 3] > 0
    ys, xs = np.nonzero(a)
    return f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1} px (x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()})"


def refs(out, views):
    (out / "refs").mkdir(parents=True, exist_ok=True)
    for v in views:
        im = Image.open(STILLS / f"{v}.png").convert("RGBA")
        im.save(out / "refs" / f"{v}.png")
        crop = im.crop(im.getbbox())
        big = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST)
        bg = Image.new("RGBA", (big.width + 96, big.height + 96), (255, 0, 255, 255))
        bg.alpha_composite(big, (48, 48))
        bg.convert("RGB").save(out / "refs" / f"{v}_6x.png")


def tailfix_brief():
    out = ROOT + "\\codex-tailfix"
    return f"""You are fixing pixel-art animation frames for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Other Codex jobs are writing sibling folders under anim at the same time; do not
touch them, and do not change anything in anim\\codex-set-a. Do not touch assets, art or tools, and do not commit.

{DESIGN}

Job: you made the wolf's set A (anim\\codex-set-a: read its brief.txt, REPORT.txt, scripts and boards). In the side
view of the walk (walk\\frames\\side_f0-7.png) and the sprint (sprint\\frames\\side_f0-5.png) the tail came out as a thin
straight rod held level, thinner than the approved side still ({ROOT}\\..\\fixed\\e.png, {size('e')}); the walk
frames are 118-120 px wide against the still's 110 because of it. Redraw only those tails, 14 frames in all. Every
other pixel of each frame stays exactly as it is, except the few rump pixels where the new tail joins the body.

The tail is the still's tail: the same thickness, plate count and plate pattern, the red tip, and the same length
within 2 px; a straight line of plates (Preston: "no curved tails as they are hard to rotate").
- walk: the still's tail angle. Its root follows the body's rise and fall; its tip sways 1-2 px with the trot, in step
  with the legs. Frame 0 should read like the still so idle-to-walk does not jump.
- sprint: the tail streams back between level and the still's angle (steady, a 1-2 px flick at most), at the still's
  thickness.
This is a pixel edit, not a new drawing: do not use the image tool. You may start from the still's tail pixels, moved
to each frame's tail root (and for the sprint turned to the new angle and redrawn clean at native pixels), but the join
must be redrawn by hand: no seam, no straight cut edge, no gap, and no leftover pixel of the old thin tail. Snap to the
stills' colours, binary alpha, dark outline like the still, nothing below row 160, nothing touching the canvas edge.

Output in {out}:
- walk\\frames\\side_f<i>.png and sprint\\frames\\side_f<i>.png, 192x192, same placement as set A's frames.
- A preview gif per move (walk 100 ms a frame, sprint 70 ms, looping) and board.png: the approved still leftmost, then
  set A's row, then the new row under it, with the game's sel-out applied ({SELOUT}, function selout, OUTLINE
  #141418), at 4x.
- REPORT.txt (under 25 lines): tokens used if known; per frame the tail's thickness, length and plate count against
  the still; the number of pixels changed outside the tail; the checks; and by eye: whole tail, clean join, no
  cutoffs, walk sway in step, sprint streaming. Look at your board before finishing and fix anything still thin or cut.
"""


def diag_brief(set_name, moves):
    out = ROOT + "\\" + set_name
    table = "\n".join(
        f"- {m}: {n} columns; column text from anim\\{src}\\prompts\\{m}.txt; frames se/ne; preview ms {TIMING[m]}."
        for m, src, n in moves)
    if set_name == "codex-set-c":
        rules = ("- Frames 0 and 6 of the lunge and frames 0 and 4 of the bite must be the exact approved se or ne still.\n"
                 "- The walk is the standing trot like the drawn rows; f0 close to the still; planted paws keep their "
                 "coordinates (no sliding), as in set A's gait_finish.py; a lifted paw clears the ground by 3-5 px.\n"
                 "- The sprint's f2 is the one air frame, lowest row 148-156. The lunge's f3 is the air frame, lowest row "
                 "120-150, and the lunge is drawn IN PLACE: the lift stays in the cell, the body does not travel across "
                 "the cell (the game moves the wolf). Every other frame stands on row 160.")
        src = "anim\\codex-set-a (brief.txt, REPORT.txt, prompts\\, finish.py, polish.py, gait_finish.py, details.py, verify.py)"
    else:
        rules = ("- Frames 0 and 5 of the hamstring, frames 0 and 5 of the howl, and frame 0 of the death must be the "
                 "exact approved se or ne still.\n"
                 "- The hamstring is drawn in place: the head and shoulders reach, the wolf does not travel.\n"
                 "- Every frame stands on row 160 (the death lies on it); nothing below row 160 ever.")
        src = "anim\\codex-set-a and anim\\codex-set-b (brief.txt, REPORT.txt, prompts\\ and their scripts)"
    return f"""You are making pixel-art animation frames for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Other Codex jobs are writing sibling folders under anim at the same time; do not
touch them. Do not touch assets, art or tools, and do not commit.

Job: the wolf mech (wolf_m, take B) is drawn in front, side and back (sets A and B). This job adds its two
three-quarter views for the same moves: se (three-quarter front, facing down-right) and ne (three-quarter back, facing
up-right). Method: you made sets A and B. Read {src} and follow the method that worked: one sheet per move from your
image tool with the approved stills attached, slice it, finish every frame against the stills at their native pixel
scale, check, and board it. Copy and adapt those scripts; do not start over. Generate exactly ONE image per move. Never
make a second image or a redo; if one fails, report it and go on.

{DESIGN}

Approved stills for this job: se.png ({size('se')}) and ne.png ({size('ne')}) in
{ROOT}\\..\\fixed\\, 192x192, already placed with the feet on row 160 (copied with 6x enlargements on magenta in
{set_name}\\refs\\). Attach refs\\se_6x.png then refs\\ne_6x.png, in that order. Effects (scent trails, slow marks,
howl rings, blood, sparks) are made separately: draw the body only.

Do NOT paste still parts onto generated frames (on the fennec that caused the cutoffs Preston rejected). Each frame is
one whole drawing, cleaned by hand pixel by pixel. Proportions (ears, head and muzzle, body, legs, tail) stay within 2
px of the stills. {TAIL}

Prompts: for each move write {set_name}\\prompts\\<move>.txt from that move's existing prompt: change the sentence about
the attached images to say they are the approved se (three-quarter front, facing down-right) and ne (three-quarter
back, facing up-right) views, replace the layout part with this text word for word (N = the move's column count):
"{LAYOUT}"
and keep every column description word for word, so the new rows match the drawn rows beat for beat.

Moves:
{table}

Output for each move, in {set_name}\\<move>\\ :
- frames\\se_f<i>.png and ne_f<i>.png on 192x192 transparent canvases at the stills' pixel scale, placed like the
  stills (feet on row 160).
{rules}
- Report the IoU of every frame that must equal a still (it must be 1.0).
- Snap every pixel to the stills' 12 colours; binary alpha; a dark outline like the stills; no anti-aliasing, no stray
  pixels, no enclosed holes, no see-through seams, no straight cut edges, no part ending abruptly, nothing touching
  the canvas edge.
- The game adds a one-texel sel-out outline at pack time ({SELOUT}, function selout, OUTLINE #141418). Judge every
  board with it applied, at 4x or more, next to the stills.
- Keep sheet_raw.png, grid.json (cut edges, scale, every frame's placement and preview ms), checks.txt, a preview gif
  per view with the listed timing, and review.png with the approved still at the left of each row.
Also write {set_name}\\REPORT.txt (under 30 lines): tokens used if known, each sheet's size and hash, the checks, the
proportion numbers, and by eye per move: same wolf in both rows? the move as asked? rows matching column for column
and matching the drawn front/side/back frames? each row at its still's three-quarter angle in every cell, not turned
straight and not mirrored? whole parts, no cutoffs? the tail at the still's thickness? Look at your boards before
finishing and fix drift from the stills; the eyes, ears, fins and tail are where drift usually shows.
"""


def main():
    tf = ANIM / "codex-tailfix"
    refs(tf, ("e",))
    (tf / "brief.txt").write_text(tailfix_brief(), encoding="utf8")
    print("codex-tailfix written")
    for set_name, moves in SETS.items():
        out = ANIM / set_name
        if (out / "REPORT.txt").exists():
            print(set_name, "already run; brief kept")
            continue
        refs(out, ("se", "ne"))
        (out / "prompts").mkdir(exist_ok=True)
        (out / "brief.txt").write_text(diag_brief(set_name, moves), encoding="utf8")
        print(set_name, [m for m, _, _ in moves])


if __name__ == "__main__":
    main()
