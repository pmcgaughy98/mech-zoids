"""Builds the Codex cleanup job for rhino walk35 run 1 (Claude, animation lane, 2026-11-04).

Run 1 (e, se, ne; 102,921 tokens) has the motion right: feet planted, body equal to the still. But the legs' pixel
finish is rough at 4x (walk35/claude-legs-4x.png): rotation noise (dark specks, scratches) on the gold cuffs, thin
dark slivers under the body, and ne's fore foot under the head a noisy jumble. Preston: "Yes, clean up" (estimate
40-80k tokens; run 1 stays inside the 135-210k he approved). Writes walk35/clean/brief.txt. Run 1's frames are not
touched; the cleaned frames go to walk35/clean/walk/frames.
"""
from pathlib import Path

ANIM = Path(__file__).resolve().parent
OUT = ANIM / "walk35" / "clean"
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a"


def brief():
    w = ROOT + r"\anim\walk35"
    out = w + r"\clean"
    return f"""You are cleaning pixel-art walk frames for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Do not touch any other folder (not even {w}\\walk), assets, art or tools, and do
not commit.

You drew the yellow L rhino's walk at 35 degrees in {w} (read REPORT.txt, build.py, rig.json, verify.py, checks.txt):
e, se and ne, 8 frames each, from the approved stills in {ROOT}\\views_cam35. Preston, the game's owner, accepts the
motion: the feet stay planted and the body equals the still. The cleanup is the leg finish, which at 4x is not at his
bar. See {w}\\claude-legs-4x.png (the legs of all 24 frames, sel-out, 4x; rows: e f0-3, e f4-7, se f0-3, se f4-7,
ne f0-3, ne f4-7). What I saw:
- rotation noise on the legs: dark specks and broken dark scratch lines across the gold cuffs and shanks, worst in
  e f0 and f1. The still's cuffs are clean: flat gold bands, a dark outline, no interior specks.
- thin dark slivers hanging under the body that are not a leg part (e f2 and f6, se f6; check every frame).
- ne: the fore foot under the head (RF) is a noisy jumble in most frames, and ne f2's hind foot looks smeared.
Look at all 24 frames yourself at 4x with sel-out and fix every case, not only these.

Fix, at native pixels, no image tool:
- Rebuild each leg part from the still's own pixels, translated, never rotated: the foot block with its grey sole, the
  gold cuff, the knee disc. Where a leg leans, step the part 1 px per row or redraw the shank by hand in the still's
  colours and bands. No rotated or resampled pixels anywhere.
- Every join (knee disc to cuff, cuff to foot, leg to body) is drawn by hand: clean outline, no seams, no gaps, no
  part ending abruptly.
- Remove the slivers. If one is meant to be a far leg peeking out, draw it as a clean part of that leg.
- Redraw ne's RF foot as the still's foot block under the head, clean, in the place your targets put it.
Keep exactly: every foot's ground contact (sole centre within 0.5 px of run 1, same lowest row), every lift, the
body, head, horn, plates and tail pixel for pixel (run 1 already equals the still after the dip), frame count and
timing (8 frames, 125 ms).

Pass marks (report each):
- Foot contacts against run 1: max difference per foot per view, and your foot-lock spreads re-measured from the new
  frame pixels (within 2 px; run 1 was under 0.9).
- Upper body: % of pixels differing from run 1 above the legs (target 0).
- Noise: count of isolated dark pixels (a dark pixel whose 4 neighbours are all gold or grey) inside the legs, run 1
  against yours, per frame (target 0 in yours).
- 192x192 transparent frames, the stills' colours, binary alpha, dark outline, no holes, no stray pixels, nothing
  touching the canvas edge.

Output in {out}: walk\\frames\\<view>_f0-7.png for e, se and ne, a preview gif per view, board.png (per view: the
still, run 1's 8 frames, then yours; legs only, sel-out, 4x), checks.txt and REPORT.txt (under 25 lines): tokens if
known, the checks, and by eye: are the legs as clean as the still's, every frame, every view?
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "brief.txt").write_text(brief(), encoding="utf8")
    print("walk35/clean/brief.txt written")


if __name__ == "__main__":
    main()
