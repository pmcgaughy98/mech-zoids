"""Builds the Codex jobs for the wolf's walk and kit, front/side/back (Claude, animation lane, 2026-11-04).

Preston: "let's go to wolf kit and animations". Kit: docs/plan/moba-kits.md, Wolf (ode to Thanatos, assassin): passive
scent, 1 lunge, 2 hamstring, 3 howl, 4 run down; "Art it needs: lunge, bite, howl, sprint loop."
codex-set-a: walk, sprint, lunge, bite. codex-set-b: hamstring, howl, death. The idle is built from the stills by
anim/idle/make_idle.py, so it is not here. se and ne (sets C and D) come later from the same column text.
Lesson from the fennec (2026-11-04): pasting still parts onto generated bodies caused the cutoffs Preston rejected, so
these briefs forbid it. Game feel lane (2026-11-04) confirmed the counts and key frames, asked for all five views of
every move (sets C and D), the lunge drawn in place, and the walk and sprint planted pace after packing. Writes common.txt, codex-set-a/ and codex-set-b/ (brief.txt, refs/). Launch Codex with each brief.
Set A ran first (Preston: "Set a"; 183,675 Codex tokens). Its side walk and sprint drew the tail as a thin level rod, so
the tail-thickness rule was added after it (anim/codex-tailfix redraws those tails). A set that already has a
REPORT.txt keeps the brief it was run with.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ANIM = Path(__file__).resolve().parent
TAKE = ANIM.parent
STILLS = TAKE / "fixed"
ROOT = r"D:\dev\new-mech-rpg\docs\art\moba\wolf_m\take-b"
SELOUT = r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py"


def palette():
    cols = set()
    for v in ("s", "se", "e", "ne", "n"):
        a = np.asarray(Image.open(STILLS / f"{v}.png").convert("RGBA"))
        cols |= {tuple(int(x) for x in c) for c in a[a[..., 3] > 0][:, :3]}
    return " ".join("#%02x%02x%02x" % c for c in sorted(cols, key=lambda c: sum(c)))


def size(v):
    a = np.asarray(Image.open(STILLS / f"{v}.png").convert("RGBA"))[..., 3] > 0
    ys, xs = np.nonzero(a)
    return f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}"


COMMON = """The creature is the wolf mech (wolf_m, take B), the game's assassin. Approved stills, 192x192, already placed with
the feet on row 160, in {root}\\fixed\\: s.png (front), e.png (side facing right), n.png (back); se, ne, sw, w, nw also
exist. Use fixed\\, not views\\ (Preston approved the fixed back views; the n still carries a little detail ink added
today). The approved pose is STANDING on four long legs. Keep the design exactly: an armoured gunmetal wolf with a long
narrow muzzle, two pale sabre fangs, small cyan eyes under a heavy brow, a hood and tall swept-back ears, two red-edged
folded blade-fins along the back, red lower legs and paws, and a plated tail with a red tip; the same {n} colours
({pal}), the dark outline and the chunky pixel size. Sizes: front {s}, side {e}, back {nn} px. Only the pose changes.
Never redesign: no new parts, no fur, no gloss, no longer or thinner limbs, no bigger head. The tail stays a straight
line of plates (Preston: "no curved tails as they are hard to rotate"); it can lift, swing and angle, but it keeps the
still's thickness, plate count and red tip in every frame and every view (in the side view as thick as in e.png, never
a thin rod; set A's first side walk and sprint got this wrong). It is a robot: no
realistic animal anatomy beyond what the stills show."""

MOVES = {
    "codex-set-a": [
        ("walk", 8, "100 ms each, loop",
         "the trot, looping, all four legs, head level and steady, tail held back. Diagonal pairs: pair A = right "
         "foreleg + left hindleg, pair B the other two. f0 A planted, B lifting; f1 B swings forward; f2 B reaches; f3 B "
         "lands; f4 B planted, A lifts; f5 A swings forward; f6 A reaches; f7 A lands into the loop. A lifted paw clears "
         "the ground by 3-5 px. Planted paws keep their place on the ground (no sliding in the front and back views). "
         "f0 should be close to the standing still so idle-to-walk does not jump."),
        ("sprint", 6, "70 ms each, loop",
         "the run-down sprint, a full gallop, body long and low, ears flat back, tail streaming straight back. f0 "
         "gathered: all four paws under the body; f1 hind legs push off; f2 extended: forelegs reach far forward, hind "
         "legs stretch back, all paws off the ground (the one air frame, lowest row between 148 and 156); f3 forelegs "
         "land; f4 forelegs push, hind legs swing forward; f5 hind legs land under the body into the loop."),
        ("lunge", 7, "120, 180, 80, 120, 90, 160, 200",
         "ability 1. f0 the exact standing still; f1 crouch: haunches loaded low, head forward and low, eyes on the "
         "target; f2 launch: hind legs extend, body rising and driving forward; f3 airborne: body stretched forward, jaws "
         "wide open, forelegs reaching (the air frame, lowest row between 120 and 150); f4 the bite: lands on the "
         "forelegs, jaws snap shut, head thrust forward (the hit frame); f5 recovery: head tugs back, weight settles; f6 "
         "the exact standing still. Draw it IN PLACE: the airborne lift stays in the cell, but the body does not travel "
         "forward across the cell from frame to frame (the game moves the wolf from the start of f2 to the start of f4; "
         "game feel lane, 2026-11-04)."),
        ("bite", 5, "100, 120, 80, 140, 160",
         "the basic attack and run down's finishing bite. f0 the exact standing still; f1 head pulls back, jaws open, "
         "fangs bared; f2 snap: head thrust forward, jaws shut (the hit frame); f3 tug: head jerks back and a little "
         "sideways; f4 the exact standing still. Paws stay planted."),
    ],
    "codex-set-b": [
        ("hamstring", 6, "120, 120, 80, 100, 160, 200",
         "ability 2, a bite at the legs. f0 the exact standing still; f1 drops low, front legs bend, head down and "
         "forward; f2 darts in low, jaws open near the ground; f3 snaps the jaws shut at leg height, head low and turned "
         "(the hit frame); f4 yanks back, rising; f5 the exact standing still. Hind paws stay planted and the body stays "
         "in place in the cell: the head and shoulders reach, the wolf does not travel."),
        ("howl", 6, "160, 160, 200, 500, 250, 220",
         "ability 3, the pack howl. f0 the exact standing still; f1 settles back onto its haunches; f2 head lifts, "
         "muzzle rising; f3 the howl: muzzle pointed up, jaws open, ears swept back, chest out (the buff frame); f4 the "
         "howl ends, jaws closing, head coming down; f5 the exact standing still. No sound rings or effects."),
        ("death", 7, "300, 100, 130, 140, 160, 180, 1400",
         "f0 the exact standing still; f1 struck, head jerks, body flinches; f2 front legs buckle; f3 collapses onto its "
         "chest; f4 rolls onto its side; f5 lies flat, legs out, tail down; f6 still on the ground, the cyan eye light "
         "gone (eyes dark grey). Nothing below row 160."),
    ],
}


def refs(out):
    (out / "refs").mkdir(parents=True, exist_ok=True)
    for v in ("s", "e", "n"):
        im = Image.open(STILLS / f"{v}.png").convert("RGBA")
        im.save(out / "refs" / f"{v}.png")
        crop = im.crop(im.getbbox())
        big = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST)
        bg = Image.new("RGBA", (big.width + 96, big.height + 96), (255, 0, 255, 255))
        bg.alpha_composite(big, (48, 48))
        bg.convert("RGB").save(out / "refs" / f"{v}_6x.png")


def brief(set_name, moves, common):
    out = ROOT + "\\anim\\" + set_name
    table = "\n".join(f"- {m} ({n} frames; preview ms {ms}): {text}" for m, n, ms, text in moves)
    return f"""You are making pixel-art animation frames for a game. Write only inside {out}. Read anything under
D:\\dev\\new-mech-rpg\\docs\\art\\moba. Other Codex jobs are writing sibling folders under anim at the same time; do
not touch them. Do not touch assets, art or tools, and do not commit.

{common}

Kit context (D:\\dev\\new-mech-rpg\\docs\\plan\\moba-kits.md, Wolf): an assassin that hunts the wounded. Passive scent; 1
lunge; 2 hamstring; 3 howl; 4 run down (a sprint, then a bite that grows with the target's missing health). Effects
(scent trails, slow marks, howl rings, blood or sparks) are made separately: draw the body only.

Method: you made the fennec's and the gorilla's sets this way. Read
D:\\dev\\new-mech-rpg\\docs\\art\\moba\\fennec_s\\take-b\\anim\\codex-set-a (brief.txt, REPORT.txt, prompts, finish.py,
polish.py, seam_fill.py, gait_finish.py, verify.py) and the fennec redo in ...\\anim\\codex-backviews (REPORT.txt,
finish.py, redraw.py, finalize.py), and follow the method: refs from the approved stills (6x copies on magenta are in
{set_name}\\refs; attach refs\\s_6x.png, refs\\e_6x.png, refs\\n_6x.png in that order), ONE sheet per move from your
built-in image tool, slice, finish every frame against the stills at their native pixel scale, check, board. Exactly ONE
image-tool call per move, no redo and no variations; if a sheet is weak, fix it in finishing and say so. Keep each
move's prompt in {set_name}\\prompts\\<move>.txt.

Rows: each sheet has three rows: front (like s.png), side facing right (like e.png), back (like n.png, no face). Each
column is one moment seen from the three sides, so the rows match frame for frame. Generous empty gutters, nothing
crossing a cell edge, no labels, no grid lines, the same design scale in every cell.

What went wrong on the fennec, so do not repeat it: Preston rejected frames with "too many cutoffs and
misproportions". The cutoffs came from pasting native parts of the stills (head, ears, haunches, tail pieces) onto the
generated bodies: straight cut edges, parts ending abruptly, leftover generated pieces beside a pasted part, gaps and
seams. Do NOT paste still parts onto generated frames. Each frame is one whole drawing: the generated cell scaled to the
stills' pixel scale, snapped to the colours and cleaned by hand pixel by pixel. Small native details (the cyan eyes,
the fangs, the fin edges) are redrawn by hand to match the still and join their neighbours. Proportions: ear size, head
and muzzle length, body length and depth, leg length and thickness, tail length and plate count stay within 2 px of
the stills in every frame; measure and report them.

Moves:
{table}

Output for each move, in {set_name}\\<move>:
- frames\\front_f<i>.png, side_f<i>.png, back_f<i>.png on 192x192 transparent canvases at the stills' pixel scale,
  placed like the stills (feet on row 160). Nothing below row 160 ever; nothing touching the canvas edge.
- Frames the move calls "the exact standing still" must be byte-identical to the approved still (IoU 1.0); those are the
  only frames where the still itself is used. Report their IoU.
- Every frame stands on row 160 except the named air frames, whose lowest row must fall in the stated range.
- Snap every pixel to the stills' colours; binary alpha; a dark outline like the stills; no anti-aliasing, no stray
  pixels, no enclosed holes, no see-through seams, no straight cut edges, no part ending abruptly.
- The game adds a one-texel sel-out outline at pack time ({SELOUT}, function selout, with OUTLINE set to the stills'
  darkest colour). Judge every board with it applied, at 4x or more, next to the stills, and play the gifs.
- Keep sheet_raw.png, grid.json (cut edges, scale, each frame's placement and preview ms), checks.txt, a preview gif per
  view with the listed timing, and review.png: per view the approved still leftmost, then the frames, sel-out on.
Also write {set_name}\\REPORT.txt (under 40 lines): tokens used if known, each sheet's size and hash, the checks and
their results, the proportion numbers against the stills, and by eye per move: same wolf in all rows? the move as asked,
with the key frame readable? rows matching column for column? whole parts, no cutoffs? Look at your boards before
finishing and fix anything cut off or out of proportion.
"""


def main():
    pal = palette()
    common = COMMON.format(root=ROOT, n=len(pal.split()), pal=pal, s=size("s"), e=size("e"), nn=size("n"))
    (ANIM / "common.txt").write_text(common + "\n", encoding="utf8")
    for set_name, moves in MOVES.items():
        out = ANIM / set_name
        if (out / "REPORT.txt").exists():
            print(set_name, "already run; brief kept")
            continue
        refs(out)
        (out / "prompts").mkdir(exist_ok=True)
        (out / "brief.txt").write_text(brief(set_name, moves, common), encoding="utf8")
        print(set_name, [m for m, *_ in moves])
    print("palette", pal)


if __name__ == "__main__":
    main()
