"""Builds the Codex jobs for the gorilla's se and ne views (Claude, animation lane, 2026-11-04; Preston: "Yes, run it").

codex-set-c: idle (from the stills, no image), walk, chest_beat, hex_shield.
codex-set-d: bound, hex_dome, death.
Same method as the rhino's make_codex_diag.py: each move's column text is kept word for word from the prompts Codex
wrote for sets A and B, so the new rows match the drawn front/side/back frames beat for beat; only the attached
views and the layout change. Run once, then launch Codex with each set's brief.txt.
"""
from pathlib import Path

from PIL import Image

ANIM = Path(__file__).resolve().parent
VIEWS = ANIM.parent / "views"
SETS = {"codex-set-c": [("walk", "codex-set-a", 8), ("chest_beat", "codex-set-a", 8), ("hex_shield", "codex-set-a", 6)],
        "codex-set-d": [("bound", "codex-set-b", 9), ("hex_dome", "codex-set-b", 8), ("death", "codex-set-b", 8)]}
TIMING = {"walk": "110 ms each, loop", "chest_beat": "350, 130, 100, 100, 100, 150, 140, 350",
          "hex_shield": "350, 130, 170, 100, 170, 350", "bound": "300, 120, 80, 90, 200, 90, 80, 150, 250",
          "hex_dome": "300, 150, 150, 300, 60, 350, 150, 300", "death": "80, 120, 120, 140, 160, 180, 250, 1000"}
LAYOUT = (
    "Layout: a grid of 2 rows and {n} columns of equal cells, one whole gorilla per cell, nothing crossing a cell edge, "
    "no labels, no text, no grid lines. Row 1 is the three-quarter front view facing down and to the right, exactly "
    "the camera angle of the first attached sprite: we see its face plate and green eyes. Row 2 is the three-quarter "
    "back view facing up and to the right, exactly the camera angle of the second attached sprite: we see its back and "
    "the back hex gem, and its head points away. Every cell in a row keeps that row's angle: never turn it to a "
    "straight front, side or back view, and never mirror it. Each column is one moment seen from two angles, so the "
    "two rows match frame for frame. The gorilla is the same size in every cell and the ground line is at the same "
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
    out = f"D:\\dev\\new-mech-rpg\\docs\\art\\moba\\ape_l\\take-a\\anim\\{set_name}"
    table = "\n".join(
        f"- {m}: {n} columns; column text from anim\\{src}\\prompts\\{m}.txt; frames se/ne; preview ms {TIMING[m]}."
        for m, src, n in moves)
    idle = ("\n- idle: NO image. Build se and ne idles (5 frames each) from the approved se.png and ne.png the way set A's "
            "idle was finished from native approved pixel parts (upper body lifts 0, 1, 2, 1, 0 px, lower contacts "
            "fixed, see anim\\codex-set-a\\finish.py and REPORT.txt); preview ms 220 each, loop.") \
        if set_name == "codex-set-c" else ""
    other = "codex-set-d" if set_name == "codex-set-c" else "codex-set-c"
    return f"""You are making pixel-art animation frames for a game. Write only inside
{out}\\. Read anything under D:\\dev\\new-mech-rpg\\docs\\art\\moba.
Another Codex job is writing the sibling folder anim\\{other} at the same time, and others may be writing under
docs\\art\\moba\\rhino_l; do not touch them.

Job: the gorilla mech (ape_l) is drawn in front, side and back (sets A and B). This job adds its two three-quarter
views for the same moves: se (three-quarter front, facing down-right) and ne (three-quarter back, facing up-right).
Method: you made the gorilla's sets A and B. Read anim\\codex-set-a and anim\\codex-set-b (brief.txt, REPORT.txt,
prompts\\, finish.py, polish.py, gems.py, final_pose.py, seam_fill.py, gem_cleanup.py, verify.py) and follow the method
that worked: one sheet per move from your image tool with the approved stills attached, slice it, finish every frame
against the stills at their native pixel scale, check, and board it. Copy and adapt those scripts; do not start over.
Generate exactly ONE image per move. Never make a second image or a redo; if one fails, report it and go on.

Approved stills, 160x160, feet on row 130, in D:\\dev\\new-mech-rpg\\docs\\art\\moba\\ape_l\\take-a\\views\\: se.png and
ne.png (copied with 6x enlargements on magenta in {set_name}\\refs\\). Attach refs\\se_6x.png then refs\\ne_6x.png, in
that order. Keep the design exactly: the mossy green armoured body and head, the grey face plate with green eyes, the
big orange forearm gauntlets each carrying a large green octagonal hex gem, the grey knuckle fists, the green hex gem
on the back, the same 15 colours, the dark outline and the chunky pixel size. Only the pose changes. Never redesign.
No effects of any kind.

Prompts: for each move write {set_name}\\prompts\\<move>.txt from that move's existing prompt: change the sentence about
the attached images to say they are the approved se (three-quarter front, facing down-right) and ne (three-quarter
back, facing up-right) views, replace the layout part with this text word for word (N = the move's column count):
"{LAYOUT}"
and keep every column description word for word, so the new rows match the drawn rows beat for beat.

Moves:
{table}{idle}

Output for each move, in {set_name}\\<move>\\ :
- frames\\se_f<i>.png and ne_f<i>.png on 192x192 transparent canvases, at the stills' pixel scale (never resize the
  design), placed like the still shifted by +16 x and +30 y, so the feet stand on row 160.
- Frame 0 of every move, and the last frame of hex_shield, chest_beat, bound and hex_dome, must be the exact approved
  se or ne still; report the IoU. The same holds for the idle's frame 0.
- Bound's frames 3, 4 and 5 are in the air, lifted exactly like the drawn rows (16, 28 and 12 px); every other frame
  stands on row 160. The walk's planted knuckles and feet keep their coordinates (no sliding), as in set A.
- Snap every pixel to the stills' colours; one-texel dark outline like the stills; no anti-aliasing, no stray pixels,
  nothing touching the canvas edge. No see-through seams or holes inside the silhouette: run the seam and hole checks
  from set B and fill what you find.
- Keep sheet_raw.png, grid.json (cut edges, row factors, every frame's placement), checks.txt, a preview gif per view
  with the listed timing, and a review.png board with the approved still at the left of each row.
Also write {set_name}\\REPORT.txt (under 30 lines): tokens used if known, each sheet's size and hash, whether each grid
was clean, the checks, and by eye per move: same gorilla in both rows? the move as asked, rows matching column for
column and matching the drawn front/side/back frames? each row at its still's three-quarter angle in every cell, not
turned straight and not mirrored? limbs keep their length? Look at your boards before finishing and fix drift from
the stills; the eyes, the hex gems and the gauntlet shapes are where drift usually shows. Do not touch anything
outside {set_name}, do not touch assets\\ or art\\, do not commit.
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
