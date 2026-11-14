"""Builds the Codex jobs for the rhino's missing views (Claude, animation lane, 2026-11-04).

codex-set-c: se and ne rows for stampede, horn toss, ground pound, horn jab.
codex-set-d: se and ne rows for brace, death, idle; plus the drawn braced shuffle (front, side, back).
The braced shuffle's se and ne come later, from set D's diagonal brace.

Prompts reuse the original column text word for word, so the new rows match the drawn ones beat for beat;
only the sprite sentence and the layout paragraph change. Run once, then launch Codex with each set's brief.txt.
"""
from pathlib import Path

from PIL import Image

ANIM = Path(__file__).resolve().parent
VIEWS = ANIM.parent / "views"
OLD = {
    "stampede": ANIM / "codex-set-b/prompts/stampede.txt",
    "horn-toss": ANIM / "codex-set-a/prompts/horn-toss.txt",
    "ground-pound": ANIM / "codex-ground-pound/prompt.txt",
    "horn-jab": ANIM / "codex-set-a/prompts/horn-jab.txt",
    "brace": ANIM / "codex-set-b/prompts/brace.txt",
    "death": ANIM / "codex-set-b/prompts/death.txt",
    "idle": ANIM / "codex-set-a/prompts/idle.txt",
}
COLS = {"stampede": 7, "horn-toss": 7, "ground-pound": 6, "horn-jab": 6, "brace": 5, "death": 7, "idle": 5,
        "brace-shuffle": 6}
TIMING = {  # GIF timing in ms per frame, from the 2D reels and the engine's ticks
    "stampede": "f1-f6, 80 ms each, loop",
    "horn-toss": "f0-f6 at 200, 100, 100, 100, 200, 100, 100 ms",
    "ground-pound": "f0-f5 at 100, 200, 100, 300, 300, 300 ms",
    "horn-jab": "f0-f5 at 200, 200, 100, 200, 100, 100 ms",
    "brace": "f0-f4, 120 ms each with f3 held 600 ms",
    "death": "f0-f6, 120 ms each with f6 held 1000 ms",
    "idle": "f0-f4, 200 ms each, loop",
    "brace-shuffle": "f0-f5, 150 ms each, loop",
}
SETS = {"codex-set-c": ["stampede", "horn-toss", "ground-pound", "horn-jab"],
        "codex-set-d": ["brace", "death", "idle", "brace-shuffle"]}

OLD_REF = ("The three attached sprites are the exact design: the first is the front view, the second the side view "
           "facing right, the third the back view.")
DIAG_REF = ("The two attached sprites are the exact design: the first is the three-quarter front view, turned toward "
            "the camera and facing down and to the right; the second is the three-quarter back view, turned away from "
            "the camera and facing up and to the right.")
DIAG_LAYOUT = (
    "Layout: a grid of 2 rows and {n} columns of equal cells, one whole rhino per cell, nothing crossing a cell edge, "
    "no labels, no text, no grid lines. Row 1 is the three-quarter front view facing down and to the right, exactly "
    "the camera angle of the first sprite: we see its face and horn. Row 2 is the three-quarter back view facing up "
    "and to the right, exactly the camera angle of the second sprite: we see its rump and tail stub, and its head "
    "points away. Every cell in a row keeps that row's angle: never turn it to a straight front, side or back view, "
    "and never mirror it. Each column is one moment seen from two angles, so the two rows match frame for frame. The "
    "rhino is the same size in every cell and the ground line is at the same height in every cell. Its legs keep "
    "their length in every view: when the front end rises, the shoulders and head rise above the hips while the "
    "hind legs stay planted as they are.")
STD_LAYOUT = (
    "Layout: a grid of 3 rows and 6 columns of equal cells, one whole rhino per cell, nothing crossing a cell edge, "
    "no labels, no text, no grid lines. Row 1 is the front view: camera directly in front, centred and left-right "
    "symmetric, like the first sprite. Row 2 is the side view facing right, like the second sprite. Row 3 is the back "
    "view: camera directly behind, centred and symmetric, tail stub toward the viewer, no face, like the third "
    "sprite. Each column is one moment seen from three sides, so the three rows match frame for frame. The rhino is "
    "the same size in every cell and the ground line is at the same height in every cell. Its legs keep their length "
    "in every view.")
DESIGN = ("Keep everything from them: big flat hexagonal yellow armour plates with the dark frame showing between "
          "them, short stubby legs with big round grey disc wheel joints, flat grey feet, two-tone grey nose horn and a "
          "small second horn, red eye, grey jaw, short tail stub, the same colours, outline and chunky pixel size.")
SHUFFLE = "\n\n".join([
    "Pixel-art animation sheet of ONE mech rhino shuffling forward while braced: it stays locked low in its braced "
    "stance and creeps forward with small heavy steps, on a plain magenta background (#FF00FF). The three attached "
    "sprites are the exact design and the exact braced pose: the first is the front view, the second the side view "
    "facing right, the third the back view. " + DESIGN + " Only the legs change. Never redesign: no gloss, no rounded "
    "armour, no long or realistic legs, no new parts.",
    STD_LAYOUT,
    "Columns, left to right:\n"
    "1. Reference: exactly the attached braced sprites, all four feet planted wide.\n"
    "2. The rhino's own left front foot lifts just clear of the ground, two or three pixels, and reaches a short way "
    "forward; the other three feet stay planted.\n"
    "3. That foot plants again; the right hind foot lifts just clear and slides forward.\n"
    "4. The right front foot lifts just clear and reaches a short way forward; the other three stay planted.\n"
    "5. That foot plants again; the left hind foot lifts just clear and slides forward.\n"
    "6. All four feet planted, the body one pixel lower as the weight settles; the loop goes back to column 1.\n"
    "In the front view the rhino's left feet are on the viewer's right; in the back view they are on the viewer's "
    "left. The body never rises out of the brace: the head stays low, the armour stays locked, the legs stay wide. "
    "Feet lift only a little. This is a slow braced shuffle, not a walk or a trot.",
    "No motion lines, no dust, no impact effect, no shadow, no other creature.\n",
])


def diag_prompt(name):
    paras = OLD[name].read_text(encoding="utf8").split("\n\n")
    assert OLD_REF in paras[0], name
    paras[0] = paras[0].replace(OLD_REF, DIAG_REF)
    paras[1] = DIAG_LAYOUT.format(n=COLS[name])
    return "\n\n".join(paras)


def refs(out, items):
    """items: [(ref name, 192 canvas source)]. Writes the game-size ref and a 6x copy on magenta (48 px margin)."""
    sizes = {}
    for nm, src in items:
        im = Image.open(src).convert("RGBA")
        im.save(out / "refs" / f"{nm}.png")
        box = im.getbbox()
        crop = im.crop(box)
        big = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST)
        bg = Image.new("RGBA", (big.width + 96, big.height + 96), (255, 0, 255, 255))
        bg.alpha_composite(big, (48, 48))
        bg.convert("RGB").save(out / "refs" / f"{nm}_6x.png")
        sizes[nm] = (crop.width, crop.height, box[3] - 1)
    return sizes


def brief(set_name, sheets, sizes):
    out = f"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim/{set_name}"
    lines = []
    for s in sheets:
        if s == "brace-shuffle":
            lines.append(f"- brace-shuffle: 3 rows (front, side, back), {COLS[s]} columns; attach refs/brace_front_6x.png, "
                         f"brace_side_6x.png, brace_back_6x.png in that order; game-size refs brace_front.png "
                         f"{sizes['brace_front'][0]}x{sizes['brace_front'][1]}, brace_side.png "
                         f"{sizes['brace_side'][0]}x{sizes['brace_side'][1]}, brace_back.png "
                         f"{sizes['brace_back'][0]}x{sizes['brace_back'][1]}; frames front/side/back; GIF timing "
                         f"{TIMING[s]}.")
        else:
            lines.append(f"- {s}: 2 rows (se, ne), {COLS[s]} columns; attach refs/se_6x.png then ne_6x.png; game-size "
                         f"refs se.png {sizes['se'][0]}x{sizes['se'][1]} and ne.png {sizes['ne'][0]}x{sizes['ne'][1]}; "
                         f"frames se/ne; GIF timing {TIMING[s]}.")
    table = "\n".join(lines)
    return f"""Job from Claude (the animation lane of the mech RPG): rhino animation sheets for Preston's mech-animal MOBA in D:/dev/new-mech-rpg (working id rhino_l, take A). The rhino's moves are drawn in front, side and back only; this job adds the missing three-quarter views (se = three-quarter front facing down-right, ne = three-quarter back facing up-right) and, in set D, a braced shuffle. Another Codex job may be running in a sibling folder (codex-set-c or codex-set-d) and one in docs/art/moba/ape_l; do not touch either.
You run from C:\\Users\\pmcga\\dev\\hollowtide only because that folder is trusted and holds the tools. This is NOT Hollowtide work: write nothing in the Hollowtide repo. Write only inside {out} (called "out" below). The only images you may open are the files in out/refs and the images you generate in this job. Never open any other image anywhere. Text files and scripts under D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim/codex-set-b and .../codex-ground-pound may be read.
Read first: docs/art/sprite-canon-2026-11-02.md and .codex/skills/hollowtide-sprites/SKILL.md (their craft, palette and check rules apply; their lore and evolution sections do not), then codex-set-b/brief.txt, codex-set-b/refinish.py and codex-set-b/REPORT.txt. You made set B; this is the same method with different rows. Copy codex-set-b/refinish.py into out and adapt it, do not start over.
Sheets (prompt files are out/prompts/<name>.txt):
{table}
1. For each sheet, generate exactly ONE image with your built-in image tool, with out/prompts/<name>.txt word for word as the prompt and the listed 6x refs attached in the listed order. Use a wide landscape size. Save each result unchanged as out/<name>/sheet_raw.png and record every image's size and sha256 in out/generation.json. Never make a second image or a redo of any sheet; if one fails, report it and go on to the next.
2. Finish each sheet the way refinish.py does. Magenta to transparent with no magenta or plum fringe. Find the rows by N columns of cells; if a sheet is not a clean grid of separate rhinos, report it and save what you found. Shrink each ROW with its own factor so that row's column 1 matches its game-size ref: a side row by width, every other row (front, back, se, ne) by the geometric mean of the width and height ratios. Map every pixel to the union palette of all the game-size refs in out/refs, except: the two eye colours (#FF3A2A red and #FFE6D8 glint) are allowed only on pixels whose 8 neighbours are all opaque; any other pixel that would take an eye colour takes its nearest non-eye colour, so no red sits on the rim. Save out/<name>/grid.json with the cell boxes, the row factors and every frame's placement offset, so pixels can be traced from the raw sheet to the frames.
3. Frames: out/<name>/frames/<row>_f{{0..N-1}}.png on 192x192 transparent canvases (f0 is column 1). Within a row use one fixed anchor taken from column 1: place column 1 where it best overlaps its game-size ref (feet at y=160), and every other frame by the same cell offset. Then, in every frame, the lowest pixel must sit on y=160: move a frame up or down by up to 3 px to fix it, and report any frame that was off by more. No frame may touch its canvas border.
4. Checks, saved to out/<name>/checks.txt: for each frame its width, height, colour count, red eye and glint pixel counts, and eye-colour pixels touching transparency (must be 0); for each row, column 1 against its game-size ref (width, height, share of pixels with the same colour after aligning the feet) and the same share against the ref mirrored left-right (it must be lower, or the row faces the wrong way); for front and back rows the left-right mirror similarity; whether a side row faces right.
5. Previews: out/<name>/review.png (all frames at 3x, nearest, on mid grey #808080, one row per view in the listed order, columns f0 onward, with the game-size ref drawn to the left of each row) and out/<name>/preview_<row>.gif at 3x with the listed timing.
6. Do not touch anything outside out, do not touch assets/ or art/ in either repo, do not commit, do not revert other files.
7. Report in under 25 lines, also saved as out/REPORT.txt: tokens used if known; each image's size and hash; per sheet whether the grid was clean, the row factors and the check lines; and by eye, per sheet: is it the SAME rhino as the refs in every row (hex yellow plates with the dark frame, grey wheel joints, flat grey feet, two-tone horn, red eye, tail stub)? Does it show the move as asked, with the rows matching column for column? Is each se and ne row at its ref's three-quarter angle in every cell (not turned to a straight view, not mirrored)? Do the legs keep their length? For brace-shuffle: does the body stay low and braced, and does only one foot lift at a time?
"out" means {out}.
"""


def main():
    for set_name, sheets in SETS.items():
        out = ANIM / set_name
        (out / "refs").mkdir(parents=True, exist_ok=True)
        (out / "prompts").mkdir(exist_ok=True)
        items = [("se", VIEWS / "se.png"), ("ne", VIEWS / "ne.png")]
        if "brace-shuffle" in sheets:
            items += [(f"brace_{v}", ANIM / f"codex-set-b/brace/frames/{v}_f3.png") for v in ("front", "side", "back")]
        sizes = refs(out, items)
        for s in sheets:
            text = SHUFFLE if s == "brace-shuffle" else diag_prompt(s)
            (out / "prompts" / f"{s}.txt").write_text(text, encoding="utf8")
        (out / "brief.txt").write_text(brief(set_name, sheets, sizes), encoding="utf8")
        print(set_name, sheets, sizes)


if __name__ == "__main__":
    main()
