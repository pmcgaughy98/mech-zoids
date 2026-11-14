# Pangolin take A at 35 degrees: lane report (Pangolin session, 2026-11-05)

**Run:** one Codex image, **55,009 tokens** (cap 80k), 20:30 to 20:37. Fleet total after it: 450,532 + 55,009 = 505,541.
**Files:** board `board_cam35.png`, checks `verify.txt`, `REPORT.txt`, `heights.txt`, `shape.txt`; new views in
`../views_cam35/`. The approved `views/` are untouched.

## Verdict: partial. Four views pass by eye, the side view misses.

| View | New W x H | Approved | Target | By eye |
|---|---|---|---|---|
| s | 45x70 | 45x56 | 45x68 | Pass: head low, back rising up the page behind it, tail tip at the top, eyes and claws clear |
| se | 64x61 | 70x54 | 70x68 | Pass, a little narrow (0.91) and short of the target |
| e | 78x42 | 82x43 | 82x54 | **Miss:** still the low camera, no band of back showing, the same height as approved |
| ne | 69x60 | 67x52 | 67x68 | Pass on angle; **2 cyan eye pixels** on the head (rows 113 to 114, column 128) |
| n | 47x69 | 45x59 | 45x75 | Pass: back receding up the page, tail low at the front |

- Turn risk: e is 18 to 19 px shorter than both neighbours (se 61, ne 60), so it dips both ways in a turn.
- Side length: e length over s width is 1.73 against the approved 1.82, about 5% short. The hippo's was 11% short, so
  the side-length line helped.
- Pass: palette (13 fixed colours, none added), accent shares match the approved within 0.02 points, borders clear,
  feet on row 160, no despeckle needed (lone 0.09).
- Eyes: s 10 + 10, se 12, e 8 (the minimum is 8), n 0. Small detached glint groups at the feet in s and se are steel
  glints that the check counts as eye colour; they are not eyes.
- Lit tops: the brightest yellow share rose in every view (for example s 10.0 to 12.6%, e 8.8 to 14.8%), but in e the rise
  comes from brighter scales, not from a top band.

## Options for Preston
1. **Second image for the side views only:** paid, inside the fleet's second-image allowance. Cap 80k, likely about
   50k to 60k, worst case about 155k. The prompt would carry one view, e (w mirrors it), with the back as a wide band of
   scale rows and about 54 px tall.
2. **Turn test first:** free, game feel lane. I expect the e dip to show.

Either way, removing the 2 ne eye pixels is a free fix that needs his word, as the wolf's ne ear-tip pixel did.

## Second image, side view only (Preston: "Second image, side only", 2026-11-05)
**Run:** 20:57 to 21:02, **63,527 tokens** (cap 80k). Pangolin total 118,536; fleet total 569,068. Folder `side2/`;
`views_cam35/` untouched.
- Result: **miss again.** e is 82x41 (full length now, but no taller); the spine is still the top outline and no band
  of back shows.
- Better than the first try: length 82 (was 78); the far front foot sits 10 rows above the near feet; the eye is 9 px;
  the brightest-yellow share is 17.1% (first try 14.8%). Palette, accent (1.79%) and borders pass.
- Prompt changes that did NOT work: the four passing 35-degree views attached as the camera to match, and four
  plain-language lines on what changes from above (back band, ridge inside the outline, far legs higher, head and
  tail tops). Codex's image tool keeps redrawing a side profile from a low camera.
- A third image needs Preston's new yes under the fleet rule, and I don't recommend it: the same tool missed twice the
  same way.

## Lesson for the next long machine
Saying "a quarter taller, two thirds as tall as long" did not make Codex raise the side view's camera; it redrew the
low side view nearly unchanged. The front and rear views moved fine. For long machines (shoebill, chameleon,
hummingbird), give the side view its own sentence about what new surface shows (the whole back as a band seen from
above) and consider a separate side-only image.

## Hand-drawn side view (Preston: "Hand-draw it (free)", then "Yes, finish it", 2026-11-06)
**Cost:** nothing paid. Folder `hand/`: `e.png` (the drawing), `board_hand.png`, `draw_band.py` (the script that drew it).
`views_cam35/e.png` is **not** replaced; that waits for Preston's word.
- Method: Codex's second side view (`side2/e.png`) is the base. Between its old top outline (the spine) and the 35-degree
  angle guide's side outline, the script draws the far half of the back as new rows of scale plates in the 13 fixed
  colours. Nothing is cut and re-placed. The band follows the arch only and eases out over the tail and the head.
- Six versions. v1 read as bricks, v2 left a ghost tail, v3 made a tent shape, v4 looked like a second shell stacked on
  top. v5 fixed those; v6 is v5 plus one closed-in see-through pixel filled.
- Numbers (v6): 82x54 (target 54; se 61, ne 60). Palette clean, borders clear, feet on row 160. Band 0 to 13 px,
  623 pixels added. Brightest yellow 15.7% (se 13.5%, ne 14.1%). Accent 1.36% (approved side 1.8%). No lone pixels
  added (the 85 lone pixels are all in Codex's base).
- Board, top row at 4x: approved side, Codex's side2, hand v6, run-1 se and ne. Bottom row at 2x: the turn s, se, e, ne, n.

| Tool | What it did |
|---|---|
| `draw_band.py` (Python, numpy, PIL, scipy) | Drew the band, measured height, palette, accent, lone pixels and holes, built the board |
| Angle guide (`refs/angle_guide.png`, from `hull_guide.py`) | The target top outline at 35 degrees |
| PixelLab `pixelart_workbench score` (free) | Independent check: v5 93.4, which flagged one hole; v6 95.9; Codex's side2 95.6 |

- Not used: PixelLab and Retro Diffusion generation (paid, and generated redraws come back light on ink), a third Codex
  image (missed twice the same way), Aseprite (the script places every pixel exactly), Blender (no 3D model of it).
- Still short: accent 1.36% against 1.8%, so the plate seams are lighter than the approved side; a steep step where the
  band meets the neck; the side is still 6 to 7 px shorter than se and ne, as the guide says it should be. The turn
  test is the real gate.
