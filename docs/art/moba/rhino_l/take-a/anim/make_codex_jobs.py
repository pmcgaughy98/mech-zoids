"""Write the prompts and briefs for the two rhino Codex jobs (codex-set-a, codex-set-b). Claude, 2026-11-03.

Every rhino sheet is 3 rows (front, side, back) by N columns; column 1 is the reference pose so each row's
shrink factor can be measured against the approved sprite. Set B also makes one effects sheet.
"""
import shutil
from pathlib import Path

ANIM = Path(__file__).parent
ROOT = "D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim"
HEAD = """Pixel-art animation sheet of ONE mech rhino {move}, on a plain magenta background (#FF00FF). The three attached sprites are the exact design: the first is the front view, the second the side view facing right, the third the back view. Keep everything from them: big flat hexagonal yellow armour plates with the dark frame showing between them, short stubby legs with big round grey disc wheel joints, flat grey feet, two-tone grey nose horn and a small second horn, red eye, grey jaw, short tail stub, the same colours, outline and chunky pixel size. Only the pose changes. Never redesign: no gloss, no rounded armour, no long or realistic legs, no new parts.

Layout: a grid of 3 rows and {n} columns of equal cells, one whole rhino per cell, nothing crossing a cell edge, no labels, no text, no grid lines. Row 1 is the front view: camera directly in front, centred and left-right symmetric, like the first sprite. Row 2 is the side view facing right, like the second sprite. Row 3 is the back view: camera directly behind, centred and symmetric, tail stub toward the viewer, no face, like the third sprite. Each column is one moment seen from three sides, so the three rows match frame for frame. The rhino is the same size in every cell and the ground line is at the same height in every cell. Its legs keep their length in every view: in the back view, when the front end rises, the shoulders and head rise above the hips while the hind legs stay as they are.

Columns, left to right:
1. Reference: exactly the attached sprites, standing still with all four feet flat on the ground.
"""
TAIL = "\nNo motion lines, no dust, no impact effect, no shadow, no other creature.\n"
SHEETS = {
    "idle": ("breathing while it stands still", [
        "Breathe in: body and head rise very slightly, legs straighten a little.",
        "Top of the breath: head lifts a touch, horn tilted up slightly.",
        "Breathe out: body back down to the reference height.",
        "Settle: body a touch lower than the reference, head dipped slightly."],
        "All four feet stay planted in exactly the same place in every column. Every movement is small."),
    "walk": ("trotting in place, a steady heavy trot where diagonal legs move together", [
        "Contact A: right front and left back feet planted forward, left front and right back feet planted back.",
        "Down A: body at its lowest, the left front and right back feet lifting off the ground.",
        "Pass A: the left front and right back legs swing forward under the body, feet just off the ground; body rising.",
        "Contact B: left front and right back feet planted forward, right front and left back feet planted back.",
        "Down B: body at its lowest, the right front and left back feet lifting off the ground.",
        "Pass B: the right front and left back legs swing forward under the body, feet just off the ground; body rising."],
        "Columns 2 to 7 loop. It trots in place and does not move across the cell. At least two feet touch the ground in every column. The front and back views show the legs moving with the same timing as the side view."),
    "horn-jab": ("doing a quick horn jab, its basic attack", [
        "Wind-up: head pulled back and down, weight shifted onto the back legs.",
        "Lunge: body thrust forward, head low, horn pointing straight forward.",
        "Hit: head snaps up and forward, horn jabbing upward at full reach.",
        "Follow-through: head high, body forward, starting to settle back.",
        "Recover: back to the reference stance."],
        "All four feet stay on the ground; the jab comes from the neck and shoulders."),
    "horn-toss": ("doing a horn toss: it scoops low and flicks its horn up and back over its body", [
        "Crouch: front legs bent, head dropped low to the ground, horn pointing forward at ground level.",
        "Scoop: a short step forward, head still low, horn sliding forward along the ground.",
        "Flick start: head swings up hard, the front end starts to rise.",
        "Flick peak: head thrown up and back, horn pointing up and backward over the body, front feet slightly off the ground, back feet planted.",
        "Settle: front feet back on the ground, head coming down.",
        "Recover: back to the reference stance."],
        "The back feet stay planted in every column. No enemy is drawn."),
    "brace": ("bracing: it plants its feet wide and locks its armour", [
        "Sink: legs bend, body drops low, head lowers.",
        "Plant: legs spread wide with the feet planted further apart, body low, head down with the horn forward, plates held tight.",
        "Hold: the same braced pose as column 3, body one pixel lower.",
        "Release: rising back toward the reference stance, feet drawing back in."],
        "The feet never leave the ground."),
    "stampede": ("charging in a heavy gallop in place with its head held low and the horn pointing straight forward", [
        "Gathered: all four legs under the body, front feet just landing.",
        "Push: back legs push off, front legs reach far forward.",
        "Extended: front legs reaching forward, back legs stretched behind, only one front foot touching the ground.",
        "Front landing: both front feet land, body tipping forward.",
        "Front push: front legs push off while the back legs swing forward under the body.",
        "Back landing: back legs land under the body, leading back into column 2."],
        "Columns 2 to 7 loop. It gallops in place and does not move across the cell. The head stays low and the horn forward in every column. At least one foot touches the ground in every column."),
    "death": ("being destroyed and collapsing", [
        "Hit: the body jolts, head thrown back slightly.",
        "Stagger: front legs buckle, body tilting forward.",
        "Collapse: chest hits the ground, back legs still standing.",
        "Fall: back end drops, the body lies flat on its belly with the legs splayed out to the sides.",
        "Down: head drops to the ground, the eye light goes out (the eye turns dark grey instead of red).",
        "Still: the same as column 6, settled one pixel lower."],
        "In every view it falls onto its belly. No parts fly off, no fire, no smoke, no sparks."),
}
EFFECTS = """Pixel-art effects sheet for a mech-animal game, on a plain magenta background (#FF00FF). The attached sprite only shows the art style: use the same chunky pixel size, a dark outline where it helps, and its colour family (yellows, oranges, browns, greys, pale cream). Do not draw the rhino or any creature. No blue, no purple, no lightning, no fire, no text, no labels, no grid lines.

Layout: a grid of 6 rows and 6 columns of equal cells. Each row is one effect animated left to right over its six frames, each frame centred in its cell, nothing crossing a cell edge. Effects that sit on the ground share one ground line in their row and are seen from a low three-quarter camera, so flat rings look like wide ellipses.

Row 1, impact puff: a ground-level dust burst. A small pale flash in column 1, a puff of brown dust spreading out and up in columns 2 to 4, thinning in 5 and 6.
Row 2, hit spark: a bright yellow and white star-shaped burst with short sharp spikes. Grows in columns 1 and 2, biggest in 3, breaks into fragments in 4 and 5, only a few specks in 6.
Row 3, stun loop: three small yellow four-point stars circling in a flat ring seen from slightly above, each column turned one sixth further around the ring, so it loops.
Row 4, dust trail puff: one small round puff of brown dust. It appears small at ground level, grows and rises, thins out and fades away.
Row 5, brace ring: a low flat ring of grey and brown dust pushed outward along the ground, a wide ellipse. Small and dense in column 1, widening through columns 2 to 4, faint and broken in 5 and 6.
Row 6, deflect spark: a short burst of pale grey and white metal sparks glancing off to the right from one point. A small flash in column 1, sparks flying up and out in 2 and 3, falling and fading in 4 and 5, two or three specks in 6.
"""
JOBS = {"codex-set-a": ["idle", "walk", "horn-jab", "horn-toss"],
        "codex-set-b": ["brace", "stampede", "death", "effects"]}
GIF = {"idle": "f0-f4, 220 ms each, loop", "walk": "f1-f6, 110 ms each, loop",
       "horn-jab": "f0-f5, 90 ms each with f0 held 400 ms", "horn-toss": "f0-f6, 100 ms each with f0 held 400 ms",
       "brace": "f0-f4, 120 ms each with f3 held 600 ms", "stampede": "f1-f6, 80 ms each, loop",
       "death": "f0-f6, 120 ms each with f6 held 1000 ms"}
BRIEF = """Job from Claude (the mech RPG session), set {setname} of two: rhino animation sheets for Preston's mech-animal MOBA in D:/dev/new-mech-rpg (working id rhino_l, take A). The ground pound is already done and approved; this set makes: {names}. A second Codex job is making the other sheets in a sibling folder at the same time; do not touch it.
You run from C:\\Users\\pmcga\\dev\\hollowtide only because that folder is trusted and holds the tools. This is NOT Hollowtide work: write nothing in the Hollowtide repo. Write only inside {out} (called "out" below). The only images you may open are the six files in out/refs and the images you generate in this job. Never open any other image anywhere. Text files and scripts under D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim/codex-ground-pound may be read (called "gp" below).
Read first: docs/art/sprite-canon-2026-11-02.md and .codex/skills/hollowtide-sprites/SKILL.md (their craft, palette and check rules apply; their lore and evolution sections do not), then gp/brief.txt, gp/finish.py and gp/clean/refinish.py. refinish.py is the finishing Preston approved: copy it into out and adapt it, do not start over.
Refs: out/refs/front_6x.png, side_6x.png and back_6x.png are the approved sprites at 6x on magenta. out/refs/front.png, side.png and back.png are the same sprites at game size on transparent 192x192 canvases with feet at y=160 (front 72x70, side 103x67, back 66x77 px; the 6x refs add a magenta margin).
1. For each sheet, generate exactly ONE image with your built-in image tool, with out/prompts/<name>.txt word for word as the prompt, attaching out/refs/front_6x.png, side_6x.png and back_6x.png in that order (the effects sheet attaches only side_6x.png). Use a wide landscape size. Save each result unchanged as out/<name>/sheet_raw.png and record every image's size and sha256 in out/generation.json. Never make a second image or a redo of any sheet; if one fails, report it and go on to the next.
2. Rhino sheets: finish each one the way refinish.py does. Magenta to transparent with no magenta or plum fringe. Find the 3 rows by N columns of cells (N is in the prompt); if a sheet is not a clean grid of separate rhinos, report it and save what you found. Shrink each ROW with its own factor so that row's column 1 matches its game-size ref: the side row by width to 103 px, the front and back rows by the geometric mean of the width and height ratios to 72x70 and 66x77. Map every pixel to the union palette of the three game-size refs, except: the two eye colours (#FF3A2A red and #FFE6D8 glint) are allowed only on pixels whose 8 neighbours are all opaque; any other pixel that would take an eye colour takes its nearest non-eye colour, so no red sits on the rim.
3. Frames: out/<name>/frames/{{front,side,back}}_f{{0..N-1}}.png on 192x192 transparent canvases (f0 is column 1, the reference). Within a row use one fixed anchor taken from column 1 (feet at y=160, horizontal centre at x=96) and place every frame by the same cell offset. Then, in every frame, the lowest pixel must sit on y=160: move a frame up or down by up to 3 px to fix it, and report any frame that was off by more. No frame may touch its canvas border.
4. Checks, saved to out/<name>/checks.txt: for each frame its width, height, colour count, the number of red eye pixels and glint pixels, and the number of eye-colour pixels touching transparency (must be 0); for each row, column 1 against its game-size ref (width, height, share of pixels with the same colour after aligning the feet); front and back rows left-right mirror similarity; whether the side row faces right.
5. Previews: out/<name>/review.png (all frames at 3x, nearest, on mid grey #808080, rows front/side/back, columns f0 onward) and out/<name>/preview_{{front,side,back}}.gif at 3x with this timing: {gif}.
{effects}6. Do not touch anything outside out, do not touch assets/ or art/ in either repo, do not commit, do not revert other files.
7. Report in under 25 lines, also saved as out/REPORT.txt: tokens used if known; each image's size and hash; per sheet whether the grid was clean, the three row factors and the check lines; and by eye, per sheet: is it the SAME rhino as the refs in all three rows (hex yellow plates with the dark frame, grey wheel joints, flat grey feet, two-tone horn, red eye, tail stub)? Does it show the move as asked, with the three rows matching column for column? Are the front and back rows straight on, not three-quarter? In the back row, do the legs keep their length?
"out" means {out}.
"""
EFFBRIEF = """Effects sheet (out/effects): finish it into game frames. Magenta to transparent, binary alpha, no magenta fringe. Find the 6 rows by 6 columns. Shrink each ROW with its own factor so its widest frame is this wide in px: row 1 impact puff 40, row 2 hit spark 28, row 3 stun loop 26, row 4 dust trail puff 16, row 5 brace ring 110, row 6 deflect spark 28. Map every pixel to the union palette of the three game-size refs without the two eye colours, plus #75543A, #8D7157 and #EABE53 (the dust colours of the approved ground pound effect). Keep deliberate single-pixel specks in the spark rows; remove stray single pixels elsewhere. Save out/effects/<row>/f0..f5.png, rows named impact-puff, hit-spark, stun-loop, dust-trail, brace-ring, deflect-spark, each row on one canvas size (its largest frame plus a 4 px margin) with one fixed anchor per row: the centre of the ground line for impact-puff, dust-trail and brace-ring, the burst centre for the other three. Record the anchors in out/effects/anchor.json. Save out/effects/review.png (all frames at 4x on #3D4350, rows in order) and one 4x GIF per row at 90 ms per frame (stun-loop looping).
"""

for job, names in JOBS.items():
    out = ANIM / job
    (out / "prompts").mkdir(parents=True, exist_ok=True)
    shutil.copytree(ANIM / "codex-ground-pound/refs", out / "refs", dirs_exist_ok=True)
    for name in names:
        if name == "effects":
            (out / "prompts/effects.txt").write_text(EFFECTS, encoding="utf8")
            continue
        move, cols, rule = SHEETS[name]
        text = HEAD.format(move=move, n=1 + len(cols)) + "".join(f"{i + 2}. {c}\n" for i, c in enumerate(cols)) + rule + "\n" + TAIL
        (out / "prompts" / f"{name}.txt").write_text(text, encoding="utf8")
    gif = "; ".join(f"{k}: {GIF[k]}" for k in names if k in GIF)
    brief = BRIEF.format(setname=job[-1].upper(), names=", ".join(names), out=f"{ROOT}/{job}", gif=gif,
                         effects=EFFBRIEF if "effects" in names else "")
    (out / "brief.txt").write_text(brief, encoding="utf8")
    print(job, sorted(p.name for p in (out / "prompts").iterdir()), len(brief), "chars of brief")
