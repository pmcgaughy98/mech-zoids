"""Builds the Codex job that redraws the fennec's back (n) and ne walk and sand kick (Claude, animation lane, 2026-11-04).

Preston: "Do walks in retro and sand kick there too as too many cutoffs and misproportions. mainly backviews.", then,
after the Retro rows: "Nvm retry with codex". The live frames are the previous Codex rows again (the Retro ones stay in
anim/retro/, not used). Writes codex-backviews/brief.txt and refs/; launch Codex with the brief.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ANIM = Path(__file__).resolve().parent
VIEWS = ANIM.parent / "views"
OUT = ANIM / "codex-backviews"
DESIGN = (ANIM / "common.txt").read_text(encoding="utf8").split("\n\n")[0]
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\fennec_s\take-b"
SELOUT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py"


def measure(v):
    a = np.asarray(Image.open(VIEWS / f"{v}.png").convert("RGBA"))[..., 3] > 0
    ys, xs = np.nonzero(a)
    return f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1} px (x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()})"


def refs():
    (OUT / "refs").mkdir(parents=True, exist_ok=True)
    for v in ("n", "ne"):
        im = Image.open(VIEWS / f"{v}.png").convert("RGBA")
        im.save(OUT / "refs" / f"{v}.png")
        crop = im.crop(im.getbbox())
        big = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST)
        bg = Image.new("RGBA", (big.width + 96, big.height + 96), (255, 0, 255, 255))
        bg.alpha_composite(big, (48, 48))
        bg.convert("RGB").save(OUT / "refs" / f"{v}_6x.png")


def brief():
    out = ROOT + r"\anim\codex-backviews"
    return f"""You are redrawing pixel-art animation frames for a game. Write only inside {out}.
Read anything under D:\\dev\\new-mech-rpg\\docs\\art\\moba. Do not write anywhere else, do not touch assets, art or
tools, and do not commit.

Why: Preston, the game's owner, looked at the fennec fox mech's back views and said "too many cutoffs and
misproportions. mainly backviews." That is the walk and the sand kick in the straight back view (n; frames back_f<i> in
anim\\codex-set-a) and the three-quarter back view (ne; frames ne_f<i> in anim\\codex-set-c). A Retro Diffusion redo
(anim\\retro) was rejected: "Nvm retry with codex". This job redraws those four rows: walk n, walk ne, sand_kick n,
sand_kick ne. You made the current rows: read your briefs, REPORT.txt and scripts in codex-set-a and codex-set-c, then
look at the current frames with the sel-out outline at 4x next to the stills to see the problems.

What went wrong last time, so do not repeat it:
- Cutoffs came from pasting native parts of the approved stills (head, ears, haunches, tail pieces, joint discs) onto
  the generated bodies. Where a pasted part and the body did not line up, frames show straight cut edges, parts ending
  abruptly, leftover generated pieces beside a pasted part, see-through gaps and seams. This time do NOT paste still
  parts onto generated frames. Each frame is one whole drawing: the generated cell, scaled to the stills' pixel scale,
  snapped to the 15 colours and cleaned by hand pixel by pixel. Fix drift by redrawing pixels, never by pasting.
- Misproportions: parts changed size between frames and against the stills (tail too long in ne, body too narrow or too
  squat in the back view, legs stubby or stretched). Every frame keeps the still's proportions: ear size, head width,
  body width, leg length and thickness, tail segment count and length, within 2 px. Measure them on the stills and on
  every frame and report the numbers.

{DESIGN}

Approved stills, updated today with a little detail ink (use these, not views_pre_ink): n.png and ne.png in
{ROOT}\\views, 160x160, feet on row 140, placed at +16 x and +20 y in the 192 canvas. Sizes: n {measure('n')};
ne {measure('ne')}. Copies with 6x enlargements on magenta are in codex-backviews\\refs; attach refs\\n_6x.png then
refs\\ne_6x.png, in that order. The other views (s, se, e) are in the same folder if you need to see the design.

Method: one sheet per move from your image tool, 2 rows. Row 1 is the straight back view, exactly the angle of the
first attached sprite (we see its back and the backs of both ears, no face). Row 2 is the three-quarter back view
facing up and to the right, exactly the angle of the second attached sprite. Each column is one moment in both rows.
Same size and the same ground line in every cell, generous gutters, nothing crossing a cell edge, no labels, no grid
lines, transparent or flat magenta background. Generate exactly ONE image per move (two images in all). Never make a
second image or a redo; if one fails, say so in the report and go on. Keep each move's prompt in
codex-backviews\\prompts\\<move>.txt.
- walk: 8 columns, the standing trot on all four short legs, NOT seated, looping, preview 100 ms a frame. Keep the
  beats of anim\\codex-set-a\\prompts\\walk.txt (diagonal pairs: f0 pair A planted and pair B lifting, through f7 pair
  A landing into the loop) and match the side trot already drawn (anim\\codex-set-a\\walk\\frames\\side_f0-7.png) beat
  for beat. Planted feet keep their coordinates (no sliding), as in codex-set-a's gait_finish.py. Each lifted foot
  clears the ground by 2-4 px. Head steady, ears upright, straight tail held back, slightly raised, tiny sway.
- sand_kick: 6 columns, the beats of anim\\codex-set-a\\prompts\\sand_kick.txt: f0 seated still, f1 rises onto all
  fours and crouches, f2 both front paws dig, f3 both front paws fling up and forward as the release while the hind
  feet stay planted, f4 follow-through settling, f5 seated still. From behind the front paws are mostly hidden by the
  body: show the dig and the fling through the head dipping and the shoulders and haunches working, and the paws where
  the angle shows them. No sand. Preview ms 260, 130, 130, 90, 160, 280.

Output, in codex-backviews\\<move>:
- frames\\back_f<i>.png and ne_f<i>.png on 192x192 transparent canvases, at the stills' pixel scale (never resize the
  design per frame), placed like the still (+16, +20), feet on row 160, nothing below row 160, nothing touching the
  canvas edge.
- sand_kick frames 0 and 5 must be byte-identical to the approved still at (+16, +20) (IoU 1.0); those two frames are
  the only place the still itself is used. The walk does not start on the still.
- Snap every pixel to the 15 colours; binary alpha; a dark outline like the stills; no anti-aliasing, no stray pixels,
  no enclosed holes, no see-through seams, no straight cut edges, no part ending abruptly. The tail stays straight.
- The game adds a one-texel sel-out outline at pack time ({SELOUT}, function selout, OUTLINE #141218). Judge every
  board with it applied, at 4x or more.
- Keep sheet_raw.png, grid.json (cut edges, scale, each frame's placement), checks.txt, a preview gif per view with the
  listed timing, and board.png: per view the approved still leftmost, the current live row (codex-set-a back_f or
  codex-set-c ne_f) and your new row under it, sel-out on, 4x.
Also write codex-backviews\\REPORT.txt (under 40 lines): tokens used if known, each sheet's size and hash, the checks
and their results, the proportion numbers per frame against the stills, and by eye per move and view: whole parts, no
cutoffs? proportions held? the angle held in every cell? the move as asked? Look at your boards before finishing and
fix anything still cut off or out of proportion.
"""


def main():
    refs()
    (OUT / "prompts").mkdir(exist_ok=True)
    text = brief()
    (OUT / "brief.txt").write_text(text, encoding="utf8")
    print("codex-backviews/brief.txt written,", len(text), "chars")


if __name__ == "__main__":
    main()
