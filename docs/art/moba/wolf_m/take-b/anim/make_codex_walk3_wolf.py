"""Builds the Codex job that redraws the side trot's legs to match the still (Claude, animation lane, 2026-11-04).

codex-walk2 fixed the gait (foot_lock_test.py: every planted paw stays put at 0.90 m/s) but drew the legs heavier
than the approved still: bigger grey upper-leg blocks, thick red lower legs like posts, and flat block paws without
the still's claws. Preston: "Fix legs first" (before the other four views). Writes codex-walk3/brief.txt.
"""
from pathlib import Path

ANIM = Path(__file__).resolve().parent
OUT = ANIM / "codex-walk3"
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\wolf_m\take-b\anim"
DESIGN = (ANIM / "common.txt").read_text(encoding="utf8").strip()
SELOUT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py"


def brief():
    out = ROOT + "\\codex-walk3"
    return f"""You are correcting pixel-art animation frames for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Do not touch any other folder, assets, art or tools, and do not commit.

{DESIGN}

Job: you drew the wolf's side-view trot in anim\\codex-walk2 (read its REPORT.txt, targets.json, checks.txt,
articulation.json and scripts). The motion is right and stays: the foot-lock test passes (every planted paw keeps one
spot on the ground at 0.90 m/s) and each paw meets the foot path in targets.json. Preston, the game's owner, agreed the
gait but the legs no longer look like the approved still ({ROOT}\\..\\fixed\\e.png); see
{ROOT}\\codex-walk2\\claude-still-vs-frames.png (the still top left, then your 8 frames, sel-out on, 3x). Compared
with the still, the legs are drawn heavier:
- the grey upper legs (thigh and shoulder) are bigger, blockier plates than the still's;
- the red lower legs are thick straight posts; the still's are narrower, with the still's joints and plate lines;
- the paws are flat red blocks; the still's paws are clawed, with separate toes and the claw shapes the still shows.
Redraw all four legs in all 8 frames so each leg is the still's leg in a new pose: the same widths (measure the
still's upper legs, shanks and paws and stay within 1 px), the same plate shapes and colour bands, the same paw and
claw drawing, bending at the still's joints. Pixel work at the native scale; do not use the image tool. You may take
each leg segment's shape from the still and turn it to the pose (a 2D rig), but every joint and every join with the
body must be redrawn by hand: no seams, no straight cut edges, no gaps, no part ending abruptly, nothing pasted that
does not join (that caused the cutoffs Preston rejected before). The body, head, fins and tail stay exactly as in
codex-walk2, except the few pixels where a leg meets the body.

Keep the motion exactly:
- Every paw's ground contact (its sole's x span on row 160) and its lift stay as in codex-walk2 within 1 px, so the
  foot path in targets.json still holds.
- foot_lock_test.py must still pass at 0.90 m/s:
  python {ROOT}\\foot_lock_test.py codex-walk3/walk/frames side 0.90 check_new {out}
  (report each planted paw's world-x spread over its ground frames; it must be 2 px or less).
- 192x192 transparent frames, feet on row 160, nothing below it, the stills' 12 colours, binary alpha, dark outline,
  no holes, no stray pixels, nothing touching the canvas edge.
- Judge the boards with the game's sel-out ({SELOUT}, function selout, OUTLINE #141418) at 4x, the still beside them.

Output in {out}: walk\\frames\\side_f0-7.png, a preview gif (100 ms, loop), check_new.png/.mp4, board.png (the still,
codex-walk2's row, then your row, sel-out, 4x), checks.txt, and REPORT.txt (under 25 lines): tokens if known; per leg
the still's widths against yours (upper leg, shank, paw); the contact and lift check against targets.json; the
foot-lock spreads; and by eye: do the legs look like the still's legs, clawed paws included? whole legs, clean joints,
no cutoffs? does it still read as a wolf trotting forward?
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "brief.txt").write_text(brief(), encoding="utf8")
    print("codex-walk3/brief.txt written")


if __name__ == "__main__":
    main()
