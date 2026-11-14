"""Builds the Codex job for the wolf's se and ne trot (Claude, animation lane, 2026-11-04).

The side trot (codex-walk2 for the gait, codex-walk3 for the legs) is approved and installed in codex-set-a/walk.
Preston: "Yes, do se and ne". This job draws the same trot, beat for beat, in the two three-quarter views, the way
codex-walk3 finished the side view: from the approved still with the legs re-posed to a foot path, no image tool.
Writes codex-walk4/brief.txt and refs/. Ran 2026-11-04: 116,093 tokens; installed in codex-set-c/walk/frames.
"""
from pathlib import Path

from PIL import Image

ANIM = Path(__file__).resolve().parent
STILLS = ANIM.parent / "fixed"
OUT = ANIM / "codex-walk4"
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\wolf_m\take-b\anim"
DESIGN = (ANIM / "common.txt").read_text(encoding="utf8").strip()
SELOUT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py"


def brief():
    out = ROOT + "\\codex-walk4"
    return f"""You are making pixel-art walk frames for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Do not touch any other folder, assets, art or tools, and do not commit.

{DESIGN}

Job: you drew the wolf's side-view trot in anim\\codex-walk2 (gait, foot path: targets.json, REPORT.txt) and
anim\\codex-walk3 (legs re-posed to match the still, clawed paws, clean joints: REPORT.txt, scripts). Preston, the
game's owner, approved it; it is now the side walk in anim\\codex-set-a\\walk\\frames\\side_f0-7.png. Make the same
trot in the two three-quarter views: se (facing down-right, {ROOT}\\..\\fixed\\se.png) and ne (facing up-right,
{ROOT}\\..\\fixed\\ne.png); 192x192, feet already placed, near paws lower on the canvas than far paws (depth). Frames
se_f0-7 and ne_f0-7, 100 ms each, looping, in step with the side view frame for frame: pair A (near fore + far hind)
on the ground f0-f3 and pair B (far fore + near hind) on the ground f4-f7, with the same lifts (2, 4, 4, 2 px on the
four air frames) and the same leg bends as the side frames at the same index.

The foot path in a three-quarter view: measure the body's forward axis on screen in each still (the direction from
the midpoint of the two hind paws to the midpoint of the two fore paws; unit vector u) and the foreshortening f = that
hind-to-fore paw spacing divided by the same spacing in the side still e.png. Each paw then moves exactly as in
targets.json, with every side-view x offset d turned into the screen offset d * f * u (and the lift straight up on
screen). So a planted paw slides back 5 * f px a frame along -u, which keeps it still on the ground while the body moves
forward along u. Write your measured u, f and per-paw targets into targets.json.

Method: the way codex-walk3 finished the side view, at native pixels, no image tool. The body, head, fins and tail are
the approved se or ne still, dipping 1 px at f1 and f5 like the side view, the tail swaying 1-2 px; the legs are the
still's own legs re-posed (a 2D rig: each segment keeps the still's shape, width, plates, colour bands and clawed paw,
turned at the still's joints). Every joint and every join with the body is redrawn by hand: no seams, no straight cut
edges, no gaps, no part ending abruptly (pasted parts that did not join caused the cutoffs Preston rejected before).
Where the body hides a leg in the still, draw the hidden part only as far as it shows in the new pose.

Pass marks (report each):
- Foot lock, two-dimensional: for each paw, its contact point (sole centre on its lowest row) on each of its 4 ground
  frames, plus frame index * 5 * f * u, stays within 2 px in x and y. Report the spread per paw per view. Also make a
  footprint picture per view like anim\\foot_lock_test.py does for the side (that tool only moves sideways; write your
  own version for the diagonal axis).
- Every paw meets its target within 1 px; lifts exact.
- Leg widths (upper leg, shank, paw) within 1 px of the still's; proportions within 2 px.
- 192x192 transparent frames, nothing below row 160, the stills' 12 colours, binary alpha, dark outline, no holes, no
  stray pixels, nothing touching the canvas edge.
- Judge the boards with the game's sel-out ({SELOUT}, function selout, OUTLINE #141418) at 4x.

Output in {out}: walk\\frames\\se_f0-7.png and ne_f0-7.png, targets.json, a preview gif per view (100 ms, loop), the
footprint pictures, board.png (per view: the approved still, set C's current row
anim\\codex-set-c\\walk\\frames, then your row; sel-out, 4x; also the side view's new row on top for timing), checks.txt
and REPORT.txt (under 30 lines): tokens if known, u and f per view, the target and foot-lock checks, the leg widths, and
by eye: does each view read as the wolf trotting forward at its three-quarter angle, in step with the side view,
legs like the still, whole and clean?
"""


def main():
    (OUT / "refs").mkdir(parents=True, exist_ok=True)
    for v in ("se", "ne", "e"):
        im = Image.open(STILLS / f"{v}.png").convert("RGBA")
        im.save(OUT / "refs" / f"{v}.png")
    (OUT / "brief.txt").write_text(brief(), encoding="utf8")
    print("codex-walk4/brief.txt written")


if __name__ == "__main__":
    main()
