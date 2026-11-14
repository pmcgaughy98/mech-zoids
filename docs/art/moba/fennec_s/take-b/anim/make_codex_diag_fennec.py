"""Builds the Codex jobs for the fennec's se and ne views (Claude, animation lane, 2026-11-04; Preston: "Finish up
fennec animation and do fennec kit so mech-zoids game can make reveal").

codex-set-c: idle (from the stills, no image), walk, sand_kick, ear_burst, sonic_boom.
codex-set-d: dig, pop_out, death.
Same method as the gorilla's make_codex_diag_ape.py: each move's column text is kept word for word from the prompts
Codex wrote for sets A and B, so the new rows match the drawn front/side/back frames beat for beat; only the attached
views and the layout change. Run once, then launch Codex with each set's brief.txt.
"""
from pathlib import Path

from PIL import Image

ANIM = Path(__file__).resolve().parent
VIEWS = ANIM.parent / "views"
SETS = {"codex-set-c": [("walk", "codex-set-a", 8), ("sand_kick", "codex-set-a", 6), ("ear_burst", "codex-set-a", 6),
                        ("sonic_boom", "codex-set-a", 8)],
        "codex-set-d": [("dig", "codex-set-b", 6), ("pop_out", "codex-set-b", 5), ("death", "codex-set-b", 7)]}
TIMING = {"walk": "100 ms each, loop", "sand_kick": "260, 130, 130, 90, 160, 280",
          "ear_burst": "260, 130, 100, 100, 160, 280", "sonic_boom": "300, 150, 230, 260, 100, 140, 180, 350",
          "dig": "300, 120, 90, 100, 100, 180", "pop_out": "120, 90, 130, 110, 350",
          "death": "300, 100, 130, 140, 160, 180, 1400"}
DESIGN = (ANIM / "common.txt").read_text(encoding="utf8").split("\n\n")[0]
LAYOUT = (
    "Layout: a grid of 2 rows and {n} columns of equal cells, one whole fennec per cell, nothing crossing a cell edge, "
    "no labels, no text, no grid lines. Row 1 is the three-quarter front view facing down and to the right, exactly "
    "the camera angle of the first attached sprite: we see its face, muzzle and teal eyes. Row 2 is the three-quarter "
    "back view facing up and to the right, exactly the camera angle of the second attached sprite: we see its back and "
    "the backs of its ears, and its head points away. Every cell in a row keeps that row's angle: never turn it to a "
    "straight front, side or back view, and never mirror it. Each column is one moment seen from two angles, so the "
    "two rows match frame for frame. The fennec is the same size in every cell and the ground line is at the same "
    "height in every cell.")


def refs(out):
    for v in ("se", "ne"):
        im = Image.open(VIEWS / f"{v}.png").convert("RGBA")
        im.save(out / "refs" / f"{v}.png")
        crop = im.crop(im.getbbox())
        big = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST)
        bg = Image.new("RGBA", (big.width + 96, big.height + 96), (255, 0, 255, 255))
        bg.alpha_composite(big, (48, 48))
        bg.convert("RGB").save(out / "refs" / f"{v}_6x.png")


def brief(set_name, moves):
    out = f"D:\\dev\\new-mech-rpg\\docs\\art\\moba\\fennec_s\\take-b\\anim\\{set_name}"
    table = "\n".join(
        f"- {m}: {n} columns; column text from anim\\{src}\\prompts\\{m}.txt; frames se/ne; preview ms {TIMING[m]}."
        for m, src, n in moves)
    idle = ("\n- idle: NO image. Build se and ne idles (5 frames each) from the approved se.png and ne.png exactly the way "
            "set A's idle was built from the s, e and n stills (see anim\\codex-set-a\\idle and REPORT.txt: native "
            "approved pixels, body above the haunches lifted 0, 1, 1, 1, 0 px, ground contacts fixed); preview ms 220 "
            "each, loop.") if set_name == "codex-set-c" else ""
    other = "codex-set-d" if set_name == "codex-set-c" else "codex-set-c"
    if set_name == "codex-set-c":
        rules = ("- Frame 0 of sand_kick, ear_burst, sonic_boom and the idle must be the exact approved se or ne still; so "
                 "must their last frames. The walk is the standing trot like the drawn rows (it does not start on the "
                 "seated still); its planted feet keep their coordinates (no sliding), as in set A's gait_finish.py.\n"
                 "- Every frame stands on row 160.")
    else:
        rules = ("- Frame 0 of dig and death must be the exact approved se or ne still; so must pop_out's last frame. "
                 "pop_out starts with only the ear tips above the ground, like the drawn rows.\n"
                 "- Like the drawn rows: dig's frames 3, 4 and 5 and pop_out's frame 0 are partly underground, cut off "
                 "at row 160 (nothing below row 160 ever); pop_out's frame 2 is in the air with its lowest row between "
                 "140 and 150; every other frame stands on row 160.")
    return f"""You are making pixel-art animation frames for a game. Write only inside
{out}\\. Read anything under D:\\dev\\new-mech-rpg\\docs\\art\\moba.
Another Codex job is writing the sibling folder anim\\{other} at the same time; do not touch it.

Job: the fennec fox mech (fennec_s, take B) is drawn in front, side and back (sets A and B). This job adds its two
three-quarter views for the same moves: se (three-quarter front, facing down-right) and ne (three-quarter back, facing
up-right).
Method: you made the fennec's sets A and B. Read anim\\common.txt, anim\\codex-set-a and anim\\codex-set-b (brief.txt,
REPORT.txt, prompts\\, finish.py, polish.py, seam_fill.py, details.py, gait_finish.py, finalize.py, final_pass.py,
verify.py) and follow the method that worked: one sheet per move from your image tool with the approved stills attached,
slice it, finish every frame against the stills at their native pixel scale, check, and board it. Copy and adapt those
scripts; do not start over. Generate exactly ONE image per move. Never make a second image or a redo; if one fails,
report it and go on.

{DESIGN}

Approved stills for this job: se.png and ne.png in D:\\dev\\new-mech-rpg\\docs\\art\\moba\\fennec_s\\take-b\\views\\
(copied with 6x enlargements on magenta in {set_name}\\refs\\). Attach refs\\se_6x.png then refs\\ne_6x.png, in that
order. Effects (sand spray, sound rings, tunnel holes, pings) are made separately: draw the body only.

Prompts: for each move write {set_name}\\prompts\\<move>.txt from that move's existing prompt: change the sentence about
the attached images to say they are the approved se (three-quarter front, facing down-right) and ne (three-quarter
back, facing up-right) views, replace the layout part with this text word for word (N = the move's column count):
"{LAYOUT}"
and keep every column description word for word, so the new rows match the drawn rows beat for beat.

Moves:
{table}{idle}

Output for each move, in {set_name}\\<move>\\ :
- frames\\se_f<i>.png and ne_f<i>.png on 192x192 transparent canvases, at the stills' pixel scale (never resize the
  design), placed like the still shifted by +16 x and +20 y, so the feet stand on row 160.
{rules}
- Report the IoU of every frame that must equal a still (it must be 1.0).
- Snap every pixel to the 15 colours; binary alpha; one-texel dark outline like the stills; no anti-aliasing, no stray
  pixels, nothing touching the canvas edge. No see-through seams or holes inside the silhouette: run the seam and hole
  checks from sets A and B and fill what you find. The tail stays straight in every frame.
- Keep sheet_raw.png, grid.json (cut edges, row factors, every frame's placement and preview ms), checks.txt, a
  preview gif per view with the listed timing, and a review.png board with the approved still at the left of each row.
Also write {set_name}\\REPORT.txt (under 30 lines): tokens used if known, each sheet's size and hash, whether each grid
was clean, the checks, and by eye per move: same fennec in both rows? the move as asked, rows matching column for
column and matching the drawn front/side/back frames? each row at its still's three-quarter angle in every cell, not
turned straight and not mirrored? limbs keep their length? Look at your boards before finishing and fix drift from
the stills; the eyes, the ears and the tail segments are where drift usually shows. Do not touch anything outside
{set_name}, do not touch assets\\ or art\\, do not commit.
"""


def main():
    for set_name, moves in SETS.items():
        out = ANIM / set_name
        (out / "refs").mkdir(parents=True, exist_ok=True)
        (out / "prompts").mkdir(exist_ok=True)
        refs(out)
        (out / "brief.txt").write_text(brief(set_name, moves), encoding="utf8")
        print(set_name, [m for m, _, _ in moves])


if __name__ == "__main__":
    main()
