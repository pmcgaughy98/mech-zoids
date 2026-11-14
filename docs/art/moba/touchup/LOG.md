# Sprite touch-up lane: log

Toolkit and checklist: `TOOLKIT.md` in this folder.

## 1. Rhino cam35 views, pilot (2026-11-04)
**Status: approved.** Preston picked "Keep, game sel-out" (2026-11-04): the touch-up as on the board, with the game's existing sel-out; the light-following option was not picked. Ruling in `rhino_l/take-a/views_cam35_touchup/APPROVED.txt`. Installing is the game feel lane's step; this lane did not install or pack anything.

- **Input (read only):** `rhino_l/take-a/views_cam35/`, approved by Preston ("Thats it looks good"). Its SHA-256s
  were saved before the run (`cam35_touchup/input_sha256_before.txt`) and still match. `views/` was not touched.
- **Output:** `rhino_l/take-a/views_cam35_touchup/{s,se,e,ne,n}.png`. Raw, no outline: the packer adds sel-out.
- **Board:** `rhino_l/take-a/cam35_touchup/board.png`. Rows: approved, before, after, after with the light-following
  sel-out option, changed pixels, then game size at 1x and 2x.
- **Script and numbers:** `cam35_touchup/touchup.py` (run `python touchup.py 0.80 3`), `cam35_touchup/metrics.json`.
- **Aseprite working files:** `cam35_touchup/aseprite/<view>.aseprite`, each with three layers: approved (hidden),
  cam35 before (hidden), and touch-up. The 12 colours are set as the palette.

### What changed (recolour only; alpha identical, 0 px differ)
| view | px changed | specks fixed | seam ink px | bevel rim px | scratches cleaned | charcoal gap px |
|---|---|---|---|---|---|---|
| s | 760 | 52 | 45 | 569 | 7 | 94 |
| se | 671 | 65 | 19 | 478 | 12 | 114 |
| e | 695 | 26 | 21 | 508 | 4 | 137 |
| ne | 745 | 53 | 36 | 538 | 9 | 117 |
| n | 688 | 20 | 6 | 534 | 11 | 117 |

1. **Cluster cleanup:** a yellow cluster of 1-2 px with 4+ neighbours of one other yellow takes that colour.
2. **Capped ink, plate seams:** a lit-face valley, meaning a yellow pixel darker than both of the lit pixels across
   it, is inked in #141218, the darkest colour. It must form a line of 3+ px, not a blob, and must reach a plate
   edge or run 6+ px. One-pixel breaks are closed. Shorter floating marks are Codex scratches: they are cleaned
   into the plate instead (the first try inked one and made a ring on the s hump).
3. **Bevel rims:** this ends the "whole plate filled with highlight" look. Each highlight plate of 40+ px keeps
   its highlight 3 px deep along its top edges and 2 px along its left edges, and is base yellow inside. That is the
   approved views' own structure.
4. **Charcoal gaps:** a shadow-yellow pixel with a dark line above it or to its left sits in that plate's cast
   shadow, so it becomes #211e27. Capped at 0.8 x the approved dark share; the cap was never reached.

### Measured, before -> after (approved in brackets)
| view | highlight % | frame + seam % | yellow specks | 2x2 checkers | lit-face valleys left |
|---|---|---|---|---|---|
| s | 24.4 -> 12.6 (15.5) | 10.6 -> 13.6 (20.3) | 72 -> 26 (65) | 9 -> 5 (9) | 85 -> 24 |
| se | 21.9 -> 12.7 (12.7) | 15.7 -> 18.4 (24.9) | 101 -> 41 (70) | 16 -> 10 (4) | 61 -> 30 |
| e | 21.2 -> 11.0 (8.2) | 13.9 -> 17.1 (25.8) | 54 -> 39 (66) | 5 -> 3 (7) | 40 -> 9 |
| ne | 21.8 -> 11.4 (11.4) | 14.6 -> 17.6 (24.6) | 75 -> 35 (31) | 13 -> 8 (2) | 52 -> 25 |
| n | 20.1 -> 8.8 (13.3) | 15.3 -> 17.9 (28.1) | 36 -> 21 (35) | 4 -> 1 (4) | 23 -> 4 |

- Palette: 0 px off the 12 colours (Aseprite check). Lowest row 160 in all five. Alpha: 0 px differ (Python and Aseprite).
- **Eyes, untouched:** largest group s 4, se 4, e 5; no eye pixel in ne or n. The check is approved x 0.82 (s 2.5,
  se 5.7, e 4.9). **se misses: 4 px is 70%.** It was already small in the approved cam35. The free fix is the gorilla
  lane's glow-along-the-slit method, and it needs Preston's word.

### Checklist score (0-2 each, max 28): before 13, after 20
| # | Item | Before | After | Note |
|---|---|---|---|---|
| 1 | Sel-out | 1 | 1 | Game black sel-out on both. The light-following option (board row 4) would score 2 if picked. |
| 2 | Capped ink, seams | 0 | 1 | Panel lines now read; the dark share is still under the approved. |
| 3 | Manual AA | 1 | 1 | Not touched; plate edges kept hard. |
| 4 | Jaggies | 1 | 1 | Not touched (the silhouette is fixed). |
| 5 | Cluster cleanup | 1 | 2 | Specks at or under the approved in four views. |
| 6 | Banding, pillow | 0 | 1 | The plate fill is gone. PixelLab's banding flag is flat (se 94 -> 108 px). |
| 7 | Palette, ramps | 2 | 2 | |
| 8 | One light direction | 1 | 2 | Rims on top and left edges in all five. |
| 9 | Rim and specular | 0 | 2 | Highlight 8.8-12.7%, as edge bevels. |
| 10 | Feet | 2 | 2 | |
| 11 | Eyes | 1 | 1 | se small, see above. |
| 12 | Read at game size | 1 | 1 | Plates separate at 1x, but the frame is still lighter than approved. Preston judges. |
| 13 | Dithering | 1 | 2 | Checkers 1-10, near the approved 2-9. |
| 14 | Same machine | 1 | 1 | Head and hump drift is in the input; a redraw, not a touch-up. |

### What each tool contributed
- **Python (numpy, Pillow):** all four passes, the metrics and the board.
- **Factory scripts:** `selout_rhino.selout()` renders every board row as the packer would. The capped-ink rule
  (darkest colour, capped at the approved share) set the seam colour and the cap.
- **Aseprite MCP:** the layered working files with the palette set, and an independent check that matched Python
  exactly (changed s 760 / se 671 / e 695 / ne 745 / n 688 on the final run, 0 off-palette, 0 alpha difference).
- **PixelLab workbench (free):** a lint and score that are not my code, run on se. Score 99.2 -> 99.1. Orphan
  clusters 217 -> 177. Banding info 94 -> 108 px, so the rims were made asymmetric (no change in the count; the
  equal-width runs are elsewhere).
- **Hollowtide sel-out README:** the rules this lane copies: change only what the pass names, keep pre-pass
  hashes, make the pass repeatable.
- **Not used:** Retro Diffusion (no off-grid or off-palette pixels to recover; paid), Codex, SpriteCook, PixelLab AI
  edits (they redraw). Gemini failed to connect.

### Still short of the approved views
- The charcoal frame between body and legs is still thinner (dark share 13.6-18.4% against 20-28%). From 35 degrees
  less underside shows, so some of that is right; the rest would need hand redraw of the frame.
- Plate corners are still rounded: that is the silhouette, which a touch-up does not move.
- Some thin highlight slivers sit beside seams in se and e; worth a hand pass in Aseprite if he likes the direction.

## Queue (2026-11-04)
- **Fennec: parked** for Preston's rhino walk request. The hub and fleet lane both confirmed the fennec and gorilla cam35 views are final (fennec: "Looks fine, keep it", LANE_REPORT line 45). `touchup/touchup_machine.py` is the rhino script generalised to read each machine's palette.json; it is not yet proven pixel-identical on the rhino, so rerun that check first. No fennec pixels written.
- Next: the first machine the "Redraw the mech fleet at 35 degrees" session reports done. Asked it to report here. None reported yet: gorilla and fennec have views_cam35 but no APPROVED.txt; the wolf is still being drawn.
- Wolf animation fixes #28, #33 (thin tails), #36, #40 (stiff death rolls): only when Preston asks.

## 2. Rhino walk35, e view (2026-11-04)
**Status: first slice, waiting for Preston's look.** Preston: "Touch up rhino walk, lots of missing art because of
movement and cutoffs." Nothing installed or packed. `walk35/` (the animation lane's folder) not touched; s and n
left alone while run 2 runs.

- **Output:** `rhino_l/take-a/anim/walk35_touchup/frames/e_f0-7.png`, `board_e.png`, `metrics.json`, `walk_rebuild.py`.
- **Board:** rows 1-2 run 1 then touch-up (f0-3, 3x, with game sel-out), rows 3-4 the same for f4-7, then run 1 and
  touch-up at 1x.
- **Cause found:** run 1 pinned the thigh plates with the body while the disc, cuff and foot moved, so each plate was
  cut where moved parts overlapped it (socket bars, half discs, steel hooks).
- **Method (free, no generator):** the body is the still's pinned pixels, dipped 1 px on f0 and f4 like run 1, drawn
  last so nothing can cut a plate. Each near leg is the still's own leg pixels: foot placed exactly on run 1's rig
  target (gait and foot lock unchanged), disc moved half as far, cuff rows sheared between them. Far legs are copies
  of the near leg at the far targets, one shade darker, and pieces under 12 px are left hidden. No rotation, no
  resampling, so every pixel is one the still already had.
- **Checks:** 0 px off the 12 colours; lowest row 160 on all frames except f7 (158, both feet lifted, same as run 1);
  body matches the still on 99.9-100% of its pixels.
- **Still short (seen at 3x):** small flecks at the front knee disc's edge on f0, f3 and f4, and a dark spike beside
  the hind disc on f6. Not fixed yet.
- **se and ne: not done.** The same leg finder picks up jaw and head pixels as the front leg in se (and splits ne's
  legs wrong), so the front foot under the head came out broken. Those frames were removed from the folder.

## Queue update (2026-11-04)
- Wolf: `wolf_m/take-b/views_cam35/` is final (wolf lane and hub). Queued after fennec and gorilla, free only, into
  `wolf_m/take-b/views_cam35_touchup/`. Palette `wolf_m/take-b/cam35/palette.json`, canvas 192, feet row 160. The ne
  ear-tip pixel (119, 71) was set to 6e6e7e by the wolf lane; keep it.

## 3. Rhino walk35, e + se + ne, second pass (2026-11-05)
**Status: waiting for Preston's look.** Preston: "Keep going, free."

- **Found first:** at 2026-11-04 22:18 another session moved the walk frames to `walk35/walk/frames_pre_touchup/` and
  wrote new ones to `walk35/walk/frames/`, recoloured to the touched-up stills (`claude-touchup-legs.png`). The body in
  every current e/se/ne frame matches `views_cam35_touchup/` exactly (1.0), so the game's idle is the touched-up
  still. This lane's rebuild now uses that still too, or idle to walk would pop. The leg cutoffs were still there.
- **Output:** `anim/walk35_touchup/frames/{e,se,ne}_f0-7.png`, `board_walk.png` (per view: current frames, then
  touch-up, f0-3 then f4-7, 3x, game sel-out), `metrics.json`, `walk_rebuild.py`. The old `board_e.png` was removed
  (built on the old still).
- **Changes since the first slice:** leg rows now come from the rig's own knee and ankle (disc to knee+4, cuff to
  ankle+3), so se and ne split right. The knee moves by the hip-pendulum share of the foot's move instead of half.
  Pinned pixels in 1-2 px thin pieces at leg height go back to the leg (that was the f6 spike). Far legs show only
  where a 5x5 block of them is visible (that was the flecks).
- **Looked at 3x:** e clean on all 8 frames. ne legs whole (the current f2 has a black block cut under the left leg;
  gone), a few single dark specks left near the belly on f3 and f6. **se front foot under the head is still a jumble
  of jaw and foot pieces, in both the current frames and the touch-up**: only the foot is outside the pinned head, so
  this method cannot rebuild that leg. se's other two legs are whole.

## 4. Rhino walk35, se front foot hand-drawn + one-piece frames (2026-11-05)
**Status: waiting for Preston's look.** Preston: "Hand-draw it, free."

- **What the se front leg is in the still:** a steel sole block under the jaw (rows 148-155, x 108-133) and a dark
  ankle at the jaw's left (rows 145-147, x 108-115). Rows 138-147 above it are the steel jaw (body). The mess came
  from the jaw's bottom rows staying while the foot moved, plus 4 toe pixels (row 148-149, x 130-133) that the
  pinned mask gave to the jaw, which floated as light flecks.
- **Hand-drawn part (pixel rules in `walk_rebuild.py`, HAND):** foot = the still's own sole block including those toe
  pixels; ankle = the still's own dark ankle, extended up to row 134 as one 3d3a44 column on the lit left and
  141218 behind, so the leg always reaches the body and the jaw covers the rest; both move to the rig's foot
  target; the 1-3 px gap that opens under the jaw on the down-step frames is 211e27 shadow. The hidden far front
  leg is not drawn in se (the animation lane's run 2 report calls it occluded).
- **One piece per frame:** a 1-3 px slot that opens between a moved leg and the body (a hip pulling off the plate
  edge; ne f2 had its left hind leg cut off by one) is filled 211e27 as the hollow behind the joint. All 24 frames
  are now one connected piece (the current game frames are too).
- **Checks:** 0 px off the 12 colours; lowest rows identical to the current game frames in all 24 (se and ne go to
  162 by the animation lane's foot path); everything above row 110 matches the touched-up still exactly.
- **Boards:** `walk35_touchup/board_walk.png` (all three views, current then touch-up, 3x) and `board_se_foot.png`
  (the se head and foot, current then touch-up, 5x).
- **Still short:** single dark specks on e f3 (front knee) and ne f3 and f6 (near the belly); not fixed. Not played
  as a moving loop. s and n not touched (animation lane's run 2).

## 5. Fennec cam35 views (2026-11-05)
**Status: waiting for Preston's look.** Queued by the hub ("get every session going"); free tools only. Nothing
installed.

- **First, the general script proved:** `touchup/touchup_machine.py rhino_l/take-a --cap 0.80 --rim 3` into scratch
  folders gives 0 px difference from the approved rhino touch-up in all five views. Board title now names the
  machine; new option `--rim-min` (smallest highlight plate that gets a bevel rim, default 40 as on the rhino).
- **Input (read only):** `fennec_s/take-b/views_cam35/`, approved reference `views/`, palette `cam35/palette.json`
  (15 colours). SHA-256s saved in `cam35_touchup/input_sha256_before.txt`; all still match after the run.
- **Output:** `fennec_s/take-b/views_cam35_touchup/{s,se,e,ne,n}.png` (raw; alpha identical), board
  `cam35_touchup/board.png`, numbers `cam35_touchup/metrics.json`. Run: `--cap 0.80 --rim 3` (defaults).
- **What it found:** very little. Changed s 25, se 50, e 83, ne 32, n 26 px: specks merged (19-37 per view), a few
  plate seams inked (0-7), a few charcoal gaps (0-51, e most), 0-3 scratches. The bevel-rim pass found no highlight
  plate of 40+ px because the fennec's highlights are already thin edge rims; trying 12 and 20 px plates changed
  0-12 px more, so the default was kept. Deepest-shade share is already at the approved level (14-23%).
- **Still short of the approved views:** highlight share 9.3-11.5% against 5.4-9.1% (the rims are 1-3 px wide
  already; trimming them is a per-plate hand call, not a rule); frame + seam share 11.4-15.3% against 11.9-19.1%.
- **Not done:** Aseprite working files and the PixelLab lint (the rhino pilot had both); the se eye fix by the fleet
  lane is in the input and untouched.
- **Measured, before -> after (approved):** yellow-ramp specks s 66->45 (36), se 70->40 (30), e 64->42 (22), ne 45->23
  (14), n 42->27 (13); checkers 1-3 -> 1-3 (0-3); 0 px off palette; lowest row 140 in all five. Eyes untouched:
  s 14 (needs 14.8: 95%), se 18 (17.2: ok), **e 12 (needs 14.8: 81%, a miss already in the input)**; none in ne, n.
- **Checklist (max 28): before 20, after 20.** Sel-out 1/1, capped ink 1/1, AA 1/1, jaggies 1/1, clusters 1/1
  (down 31-49% but still above approved), banding 1/1, palette 2/2, light 2/2, rim 1/1, feet 2/2, eyes 1/1 (e),
  game-size read 2/2, dithering 2/2, same machine 2/2. The pass is a real but small cleanup; it does not move a score.

## 6. Gorilla cam35 views, take 2 (2026-11-05)
**Status: waiting for Preston's look.** He said "Keep do gorilla btw" (fennec kept, `fennec_s/take-b/views_cam35_touchup/APPROVED.txt`). Nothing installed.

- **Script change:** the gorilla palette has no charcoal or eye role. Glow roles ("shield and visor glow") are now never recoloured, like eyes; with no charcoal role the darkest steel (4a4950) is the frame colour. Rhino regression after the change: 0 px in all five views.
- **Input (read only):** `ape_l/take-a/views_cam35/` (take 2, with the fleet lane's ne arm and se visor fixes), reference `views/`, palette `cam35/palette.json` (15 colours). Hashes saved and unchanged.
- **Output:** `ape_l/take-a/views_cam35_touchup/`, board `cam35_touchup/board.png`, `metrics.json`, and `rim3_vs_rim2.png` (s and e: approved, before, rim 3, rim 2). Run: defaults (`--cap 0.80 --rim 3`), same as the rhino.
- **What it did:** the shoulder, back and arm plates were filled with highlight like the rhino's; they now keep it as a 3 px bevel on top and left edges. Specks merged, 6-31 seam pixels inked. Charcoal gaps: 0 (the frame share is already at or above the target). Glow untouched.
- **Measured:**
  - s: changed 496, highlight 22.8->15.5 (rim 2: 10.2; approved 9.7), frame+seam 19.7->20.3 (22.4), specks 110->64 (127), checkers 2->3 (6), off-palette 0, lowest 130
  - se: changed 340, highlight 18.8->14.1 (rim 2: 10.3; approved 10.6), frame+seam 17.1->17.6 (16.0), specks 93->63 (136), checkers 7->6 (11), off-palette 0, lowest 130
  - e: changed 308, highlight 18.1->13.9 (rim 2: 10.4; approved 8.3), frame+seam 13.3->13.7 (14.8), specks 97->55 (100), checkers 7->4 (16), off-palette 0, lowest 130
  - ne: changed 163, highlight 11.5->9.6 (rim 2: 7.9; approved 6.9), frame+seam 14.7->14.9 (14.6), specks 106->57 (144), checkers 4->5 (11), off-palette 0, lowest 130
  - n: changed 186, highlight 10.4->7.7 (rim 2: 6.0; approved 5.3), frame+seam 11.8->11.9 (12.9), specks 70->42 (96), checkers 5->2 (13), off-palette 0, lowest 130
  - clusters score 2 -> 2 | dithering score 2 -> 2
  - TOTAL before 18 after 21
- **Checklist judgement items:** banding/pillow 0->1, light direction 1->2, rim 0->1 (still above approved in s, se, e); the rest unchanged.
- **Option:** a 2 px rim brings highlight closer to the approved numbers (see above) but flattens the e back hump; shown in `rim3_vs_rim2.png`.

- **Preston picked the 2 px rim (2026-11-05, "Use the 2 px rim").** Re-run `--rim 2 --title Gorilla` into `views_cam35_touchup/` and `cam35_touchup/` (board and metrics now show the 2 px rim). `APPROVED.txt` written.

## 7. Wolf cam35 views, take-b (2026-11-05)
**Status: kept by Preston, 2026-11-05 ("Keep it").** APPROVED.txt written in the output folder. Not packed.

- **Script changes (rhino regression still 0 px in all five):** with no charcoal or steel role (wolf: gunmetal, red,
  fang, eye, accent) the frame colour is the darkest armour shade, 22222b. New opt-in `--seam-cap`: no seam ink when a
  view's dark share is already at or above the approved views (capped ink); off by default so the rhino and gorilla
  results stay exact.
- **Input (read only):** `wolf_m/take-b/views_cam35/`, reference `fixed/` (the script's default when present),
  palette `cam35/palette.json` (12 colours). Hashes saved and unchanged. The wolf lane's ne ear-tip pixel (119, 71)
  stays 6e6e7e.
- **Run:** `touchup_machine.py wolf_m/take-b --rim 2 --seam-cap --title Wolf`. 2 px rim because Preston picked it for
  the gorilla and it measures closer here too (mean highlight gap to approved 4.4 points against 7.0 for 3 px).
  Seam ink skipped in all five views: every view's dark share already starts above approved (12.4-16.8% against
  11.8-14.8%).
- **Output:** `wolf_m/take-b/views_cam35_touchup/`, board `cam35_touchup/board.png`, `metrics.json`.
- **What it did:** the pale gunmetal plates on the back, head and tail (filled with bcbcc8) keep it as a 2 px bevel on
  top and left edges; changed s 247, se 290, e 136, ne 339, n 249 px. Specks merged (36-69 per view).
- **Measured after (approved):** highlight s 15.2 (15.2), se 16.0 (9.7), e 18.1 (9.4), ne 12.7 (9.0), n 9.0 (12.3);
  frame + seam 12.4-17.2 (11.8-14.8); specks 40-81 (105-182); 0 px off palette; lowest row 160; eyes s 3, se 6, e 4
  (approved 2, 4, 4).
- **Checklist (max 28): before 18, after 21.** Banding/pillow 0->1, light direction 1->2, rim 0->1; the rest unchanged
  (clusters 2, palette 2, feet 2, eyes 2, dithering 2, same machine 2, the others 1).
- **Still short:** highlight still above approved in se, e and ne (the red armour and fangs are not plates the rim
  pass touches); 2x2 checkers rose in s (15 -> 24, approved 10) where the new bevel edge meets existing texture.

## 8. Hippo cam35 views, take-b (2026-11-05)
**Status: kept by Preston, 2026-11-05 ("Keep it").** APPROVED.txt written in the output folder. Not packed.

- **Input (read only):** `hippo_l/take-b/views_cam35/`, reference `views/` (no `fixed/` here), palette 14 colours.
  13 input hashes saved in `cam35_touchup/input_sha256_before.txt` and checked unchanged after the run.
- **Run:** `touchup_machine.py hippo_l/take-b --rim 2 --seam-cap --title Hippo`. Same script and flags as the wolf.
  The PC restart came after the run finished; nothing was cut off.
- **Output:** `hippo_l/take-b/views_cam35_touchup/`, board `cam35_touchup/board.png`, `metrics.json`, and the
  light-following sel-out option in `cam35_touchup/views_selout_light/`.
- **What it did:** the lilac back, head and snout plates were filled with highlight (s 30.7%); they keep it as a 2 px
  bevel on top and left edges. Seam ink s 83, se 63, e 6, ne 30 px; n skipped (dark share already above approved).
  Charcoal gaps 0. Specks merged 46-114 per view. Changed s 1182, se 1145, e 699, ne 744, n 672 px. Alpha identical.
- **Measured, before -> after (approved):**
  - s: highlight 30.7->13.4 (12.8), frame+seam 13.4->14.8 (17.2), specks 160->118 (66), checkers 7->10 (6), eye 18 (20)
  - se: highlight 25.9->10.5 (10.1), frame+seam 14.0->15.0 (17.0), specks 213->134 (118), checkers 23->20 (7), eye 21 (18)
  - e: highlight 19.7->8.6 (6.6), frame+seam 13.5->13.6 (15.7), specks 140->84 (78), checkers 18->14 (7), eye 16 (21)
  - ne: highlight 18.3->8.3 (4.6), frame+seam 12.7->13.2 (13.3), specks 213->156 (88), checkers 25->18 (15)
  - n: highlight 18.6->7.5 (14.2), frame+seam 12.3->12.3 (8.8), specks 150->112 (43), checkers 22->25 (18)
  - all five: 0 px off palette, lowest row 160, no eye pixel in ne or n
- **Checklist (max 28, judged from the board): before 16, after 19.** Banding/pillow 0->1, light direction 1->2,
  rim 0->1; the rest unchanged (palette, feet, eyes, same machine 2; the others 1).
- **Still short:**
  - Deepest shade is 6-11% of each view against 14.5-17.5% in the approved views: the cam35 hippo's undersides and
    right faces are lighter than the approved ones. The touch-up only recolours lit plates, so this gap is untouched
    and is the biggest one left.
  - n now sits below the approved highlight (7.5 against 14.2); the back reads darker than the approved n.
  - Highlight still above approved in e and ne. Specks above approved in all five; checkers rose in s and n.

## 9. Hippo shade option, take-b (2026-11-05)
**Status: 1 px version kept by Preston, 2026-11-05 ("Keep 1 px version").** Final hippo set:
`views_cam35_touchup_shade1/` (9b), APPROVED.txt written there. It supersedes section 8's `views_cam35_touchup/`; a
superseded line was added to that APPROVED.txt. The 2 px option (`views_cam35_touchup_shade/`) is not used. Not packed.

Script `touchup/shade_pass.py`: written in the session worktree (the session guard blocks the file-writing tool in
the main checkout) and copied here after Preston's pick.

- **Why:** section 8 left the hippo's darkest shade at 6-11% of each view against 14.5-17.5% approved, with mid purple
  at 40-45% against 19-32%. Preston chose "Hippo undersides".
- **Script:** `shade_pass.py` (new). Light is top-left-front, so it sinks the side of each plate away from the light:
  1. Shadow plates (20+ px) keep a band d1 deep on their top and left edges; the rest becomes the deepest purple.
  2. Base plates (40+ px) get a band d2 deep on their bottom edges (d2 - 1 on right edges) in the shadow purple.
  d1 is picked per view so the darkest share lands closest to approved without passing it; d2 so the shadow share
  lands closest to approved. Highlight, steel, frame, accent and eye colours untouched; eyes guarded 2 px.
- **Input (read only):** `hippo_l/take-b/views_cam35_touchup/` (the kept views). Hashes saved in
  `cam35_touchup/shade1/hippo_kept_sha256.txt` and checked unchanged after the run.
- **Output:** `hippo_l/take-b/views_cam35_touchup_shade/`, board `cam35_touchup/shade/board.png`, `metrics.json`.
- **Run:** `python shade_pass.py hippo_l/take-b --title Hippo`.
- **Measured, kept -> shade (approved):**
  - s (d1 1, d2 0): changed 368, deep 6.2->12.5 (14.8), shadow 14.9->8.6 (10.6), base 40.0->40.0 (18.9)
  - se (d1 1, d2 1): changed 666, deep 8.2->15.0 (14.5), shadow 13.3->10.4 (13.0), base 40.8->36.9 (23.1)
  - e (d1 2, d2 1): changed 472, deep 10.9->16.3 (16.3), shadow 15.3->13.0 (12.6), base 41.8->38.6 (31.9)
  - ne (d1 3, d2 2): changed 1004, deep 10.5->17.2 (17.5), shadow 22.6->25.8 (23.8), base 40.0->30.1 (27.8)
  - n (d1 2, d2 2): changed 944, deep 9.5->16.2 (16.4), shadow 18.0->21.4 (21.1), base 44.5->34.4 (28.3)
  - all five: 0 px off palette, alpha identical, eye pixels unchanged, highlight unchanged
  - 1-2 px body specks (this script's own count): s 219->256, se 293->350, e 183->208, ne 296->307, n 221->241
- **By eye:** bellies, chin and rump read darker and more grounded at 1x and 2x; s, se and e sit closest to the
  approved. In ne and n (d2 2) the dark bottom and right bands plus the lit top and left bevel start to ring each
  plate (checklist item 6, no pillow shading). s stays short of approved (12.5 against 14.8) because the front view
  has few shadow plates to sink.
- **Next options (then):** use it as is; a softer variant with the dark bevel capped at 1 px; or keep section 8.

### 9b. 1 px bevel variant (Preston: "Try 1 px bevel", 2026-11-05)
- **Script change:** `--d2-max` (widest dark bevel), `--tag` (output names) and `--also` (extra board row). At
  d2 1 the bevel is 1 px on bottom edges only (right edges get d2 - 1 = 0).
- **Run:** `python shade_pass.py hippo_l/take-b --title Hippo --d2-max 1 --tag shade1 --also views_cam35_touchup_shade`.
- **Output:** `hippo_l/take-b/views_cam35_touchup_shade1/`, board `cam35_touchup/shade1/board.png` (rows: approved,
  kept, 2 px option, 1 px option, changed pixels, 1x, 2x), `metrics.json`. The kept views and the 2 px option were
  hashed before and checked unchanged after (`cam35_touchup/shade1/hippo_before_bevel1_sha256.txt`).
- **s, se, e are byte-identical to the 2 px option** (their d2 was already 0 or 1). Only ne and n change:
  - ne (d1 3, d2 1): changed 578, deep 10.5->17.2 (17.5), shadow 22.6->18.7 (23.8), base 40.0->37.1 (27.8),
    specks 296->345
  - n (d1 2, d2 1): changed 570, deep 9.5->16.2 (16.4), shadow 18.0->14.8 (21.1), base 44.5->41.1 (28.3),
    specks 221->251
  - 0 px off palette, alpha identical, eyes unchanged.
- **By eye:** the plate rings in ne and n are gone; each plate keeps a thin dark line on its bottom edge that reads as
  a panel line, and the rump and underside stay dark. Trade: the shadow share sits below approved in ne and n, and
  ne gained more 1-2 px specks (345 against 307 for the 2 px option).

## 2026-11-05 Gorilla walk touch-up (kept)
- **Preston:** "the 2 fold fixed a lot of it just needs touched up", then kept it ("do 1 2 and 3 i agree").
- **Output:** `touchup/ape_l_walk/frames/` (40 frames), README.txt, report.json, board, GIFs, Aseprite file.
  Walk lane's `walk/ape_l/final/` untouched.
- 5-29 px a frame; body, feet rows, colours, one piece kept; pinholes closed; ne score 88.5 -> 98.4.

## 2026-11-05 Fennec trot touch-up and death front redraw (installed)
- **Trot:** `touchup/fennec_s_walk/frames/` (40), 2-11 px a frame, slits between legs kept open; walk lane's final untouched.
- **Death front:** PixelLab skeleton redraw (real collapse, 3 free generations), then finishing. Preston: "Looks good just
  needs sell out cap ink etc", "Needs more ink", "looks flat towards end", "Fix last 2 ... still flat. Eyes are grey."
  Lesson: generated frames come back one shade light on ink (0.1-0.3% #141218 against the still's 5.0%) and with no
  violet highlight caps (0.0-0.9% against 2.3%), and the snap greys the eyes. Finish to the still's measured shares
  (ink 1.5x), add per-plate relief on lying poses, repaint eyes. Installed to `fennec_s/take-b/anim/death35/frames/`,
  method in `death35/skeleton_front/`, backup `frames_pre_skeleton_front/`. Do not rerun build_death.py.

## 2026-11-05 fennec trot, Retro Diffusion test (not installed)
Preston: "our walk animation is good the art just isnt fluid. So have retro do the same motion as ours just more fluid".
- One paid job, $0.14 (balance $25.51 after): rd_advanced_animation__walking, 8 frames, 160x160, start frame = our
  touched-up s_f0 cut from 192 at (16,16). Retro takes only a start frame and a prompt; it cannot follow our frames.
- Work: D:/dev/_scratch/touchup-lane/rd-walk/ (rd_walk.py, raw/, frames/ snapped to our 15 colours in 192 space,
  report.json, board_rd_walk.png, trot_ours_vs_retro.gif).
- Measured against ours: head sways 4 px side to side (ours 0) and bobs 4 px (ours 1). That is the fluid look.
- Costs: it redrew the design (rounder muzzle plate, head lower), the eyes go white in 6 of 8 frames (teal only f2, f7),
  some feet turn to dark violet blobs, and the surface re-draws every frame (1.2 to 2x our recolour per frame).
- Lesson: our trot reads stiff because the body never moves (0 px sway, 1 px dip); the legs are fine.
- Price check tip: base64 copied by hand corrupts; save as a 4-bit 16-colour PNG (1460 chars) and check it with the
  free estimate before the paid call.

## 2026-11-05 fennec trot, sway and bob test, s view (not installed)
Preston picked "Add sway to ours" after the Retro test. Free, scripts only.
- Work: D:/dev/_scratch/touchup-lane/fennec-sway/ (sway.py, frames/s_f0-7.png, report.json, board_sway.png,
  trot_sway_compare.gif, trot_sway_2x.gif, fennec_trot_sway_s.aseprite with the old frames on a hidden layer).
- Method: a per-row warp, not cut-and-paste. The bottom 8 rows of each frame stay exactly (foot lock), the legs bend
  between the foot lock and the hip line (row 142), and everything above moves as one piece. The ear tips trail the
  head by a frame (full sideways, half up and down).
- Motion: sway dx -1 -2 -2 -1 +1 +2 +2 +1 (leans over the landing front leg), extra bob dy 0 2 1 0 0 2 1 0.
  Head x moves 93.6 to 97.6 (was fixed at 95.6).
- Checks pass in all 8 frames: one piece, no holes, foot rows equal, 15 colours, eye pixels 15/7/7. The legs lose up to
  36 px on the low frames (knees bend).
- The other 4 views wait on Preston's verdict. Each needs its own hip line, ear base and sway sign.

## 2026-11-05 fennec trot sway, all views (installed)
Preston: "Keep, do all views". Installed over touchup/fennec_s_walk/frames; the old set is in pre_sway/. See its README.
Lean over the planted front leg, 2 px each side (s, se, n, ne), side view bob only; bob 1-2 px a step; ears trail a frame.
Rows-based hip lines fit the diagonal 3/4 bodies less well (ne tail and front feet sit in the bend zone); by eye fine.

## 2026-11-05 fennec death front, Retro Diffusion test (not installed, not usable)
Preston: "Retro death test". One paid job, $0.25 (balance $25.26 after): rd_advanced_animation__custom_action, 6 frames,
160x160, start frame = the approved s still. Work: D:/dev/_scratch/touchup-lane/rd-death/ (rd_death.py, raw/, frames/,
report.json, board_rd_death.png, close_7x.png, death_ours_vs_retro.gif).
- f0 matches the still (281 px off), but the eyes go white from f0 (8 eye px vs 28).
- f2 flips the fennec sideways in mid-air. From f3 on it lies as a long flat tube with no readable head or ears.
- A grey dust cloud is baked into the sprite; in f5 a separate puff makes it 2 pieces.
- Surface: it flattens over the frames (edge density 72 still -> 50 at f5, mean cluster 6.4 -> 10.2). At 7x the forms
  melt and the ink lines are lost. Same flat-fill problem as PixelLab, plus the design loss seen in the Retro walk test.
- Verdict: worse than the installed front death. Neither generator's animation tool gives the originals' surface on
  new poses. Left: the originals' own pipeline (fleet lane), using the installed frames as the pose guide.

## 2026-11-05 fennec death front, relight to the still's lighting (tried, not used)
Preston: "Lets keep ours but just make the art consistent ... to our original models art lighting etc."
Work: D:/dev/_scratch/touchup-lane/death-relight/ (relight.py, normals_fit.py, still_vs_f3_f5_6x.png).
- Measured, installed f1-f5 vs the still: ink 7.5% vs 5.0%; violet light from 125/176/-168/56/95 deg vs 115; gold
  clusters 18-50 px vs 44.
- Rule from the still, distance to a plate's lit and shadow edge along 116 deg: it reproduces the still only 63%,
  and the relit frames still disagree on light (f4 violet 49 deg).
- Rounded-plate normals with Lambert light, grid of angle, depth and height shape: best 52% on the still.
- Why: the still's shading follows 3D parts (ear, dome, leg segments) that colour families don't separate, so it
  can't be recovered from the flat sprite.
- Route that matches: the fennec's other animations (codex-set-a, codex-set-c, codex-backviews) are Codex redraws
  with the approved still as the art reference plus a finishing script. Retro was rejected there too ("Nvm retry
  with codex"). The death poses should go the same way, using the installed frames as the pose guide.

## 2026-11-05 hippo walk: defect cleanup and sway (candidate, waiting for Preston)
From the walk lane's hand-off (walk/hippo_l/final, motion approved: "Approve, to touch-up"). Free, no paid tools.
- Cleanup (hippo_clean.py): Codex cut the shadow side of the near leg into the body layer with a straight edge, so it
  hung below the belly when the leg moved (se beside RH, ne right of LH). Cleared body-layer pixels below the belly
  line that no leg layer covers (se 6-32 px a frame, ne 0-24). se specks left of the RH knee: loose pieces of 4 px or
  less (2-4 px on f0, f1, f3, f4). The ne LH pad's dark line between the grey pad and the lilac toe is in the
  approved still too, so it stays. s jaw gaps left open.
- Sway (hippo_sway.py): lean R -1 0 +1 +1 +1 0 -1 -1 (screen -R in s, se; +R in ne, n; 0 in e), bob 0 1 1 0 0 1 1 0
  down on top of the dip. Every visible foot pinned by its own box from targets.json and feet.json (6 rows locked,
  fade over the leg, 4 px side feather; 8-row fade for the high feet se RH and ne RF). Revised after the walk lane's
  footlock flagged ne LH and RF: each foot's whole pad (its leg layer's lowest 10 rows) is now rigid, and every
  planted foot's pixels are identical to the walk lane's final in all five views. walk_tools seams then flagged
  new 1-5 px slits; at 8x (seams_8x.png, ne_belly_8x.png) ne f1/f2 row 146 was the belly edge held back by the
  LH pad's feather while the body bobbed down 1 px, leaving dents: straightened with the still's own belly row
  (seal.py, 10 and 9 px; the still is solid there, x 72-73 is the still's own notch and stays). s f1/f5
  (jaw-gap edge), se f3 and n f2 sit on real gaps and stay open. All 40 frames pass: one
  piece, no new holes, binary alpha, only the source colours, pinned pixels identical, bottom row unchanged.
- Files: touchup/hippo_l_walk/ (frames/, hippo_walk_compare.gif before|after, per-view GIFs, board, zooms, scripts).
  When Preston approves, the walk lane packs frames/ with pack_hippo_3d.py.

## 2026-11-05 fennec death front: Codex redraw (candidate, waiting for Preston)
Preston: "Lets keep ours but just make the art consistent ... to our original models art lighting etc.", then "Yes, run
Codex here". One Codex job (gpt-6.1-sol, medium), capped at 200k: 86,707 tokens used, exactly one image call.
- Brief and refs: fennec_s/take-b/anim/death35/codex-death/ (brief.txt, refs/: the still and live f0-f5 at 6x on
  magenta, measure.json); set up by D:/dev/_scratch/touchup-lane/codex-death/prep_codex_death.py.
- Result: frames/front_f0-6.png. Codex kept the live poses' alpha exactly (IoU 1.0) and repainted 690-1160 px a frame.
- My check (check_codex_death.py, relight.py's light angle): all death35 rules pass, f0 is the still, f6 is f5 with the
  eyes out. Ink 5.6-5.9% (still 5.0, live 7.5). Violet light 72-152 deg (still 115; live swung through 57 to -174).
  f5 lilac caps 2.35% (live 7.2%). Eye px 25, 25, 12, 17, 16 (still 28; half closed).
- By eye at 7x (compare_7x.png): the grey dome highlight, stepped plates and clean ears are back on f1-f3; f5 no longer
  washed out. f4-f5 legs and back still busier than the still (Codex's report says the same).
- INSTALLED (Preston: "Install it"): death35/frames/front_f0-6.png and preview_front.gif replaced; the old ones are
  in death35/frames_pre_codex_front/. PACKED by the animation lane into art/machines/fennec/fennec_kit_sheet.png
  (the death lives in the kit sheet, not fennec_sheet.png); pack check OK, 45 anims, fennec3d_check 0 failures;
  the pack before is in fennec_s/take-b/anim/backup_pre_codex_front/.

## 2026-11-05 fennec death se and back: Codex pose redraw (candidate, waiting for Preston)
Measured first: the se and back surfaces already match their stills (built from the stills' own pixels; ink se
4.1-6.5% vs 6.1, back 2.6-6.1% vs 6.2; light se 52-69 vs 54 deg, back 65-96 vs 96), so the front's keep-the-pose
repaint would change little. Their flaw is cut-up middle frames (se f2-f4 ear fragments; back f3-f5 ears like wings,
head gone, lying slab of ear chunks). Preston: "Yes, redraw poses". One Codex job, cap 200k: 109,543 tokens, two
image calls (one per view). Setup: D:/dev/_scratch/touchup-lane/codex-death/prep_codex_death_se_back.py.
- Result: death35/codex-death-se-back/frames/{se,back}_f0-6.png. All death35 rules pass (check_se_back.py): one
  piece, no holes, lowest row 140, f0 = still, f6 = f5 with eyes out (back shows no eyes, f6 = f5).
- By eye (board_se_back.png, compare_se_back_6x.png): back clearly better, whole fox every frame, head kept, lies
  long on its right side. se f1-f4 whole and cleaner than live. se f5/f6 weak: a thin flat shape (1222 px against the
  still's 2173) that reads less like a lying fox than the live f5. Light drifts more than the front's (se 37-103,
  back 73-122 deg).
- BACK INSTALLED (Preston: "Back only"): death35/frames/back_f0-6.png and preview_back.gif replaced; the old ones are in
  death35/frames_pre_codex_back/. se kept as it was (candidate stays in codex-death-se-back/). PACKED by the animation
  lane into fennec_kit_sheet.png (pack check OK, 45 anims, fennec3d_check 0 failures; pack before in
  fennec_s/take-b/anim/backup_pre_codex_back/). Fits the cell (reaches x 156 of 192). Open look for Preston: the shadow
  ellipse stays under the stance (about x 73-87), so the lying body's far end (x 88-140) has no shadow; making the
  shadow follow the body is game code (camera lane), not frames.

## Hippo walk: approved and packed (2026-11-05)

Preston, in the Hippo session: "Approve, pack it". The walk lane packed touchup/hippo_l_walk/frames unchanged into art/machines/hippo (walk_<view> x5), with copies in hippo_l/take-b/anim/walk35/frames; the sel-out was added at pack time. Approval recorded in touchup/hippo_l_walk/APPROVED.txt.

## Rhino walk s and n: knee discs rebuilt (2026-11-05, candidate)

Asked by the Rhino session with Preston's answer "Yes, rebuild them" (to "Have the touch-up lane rebuild the s and n legs?"). The defect: in the front and back walk rows (built by walk35/build_run2.py) each leg moved as one rigid block under a body drawn on top, so a rising foot slid the round grey knee disc under the body and cut it to a flat bar or hid it (s f0 f1 f2 f4 f5 f6, n f0 f3 f4 f5 f6).

Script: rhino_l/take-a/anim/walk35_touchup/walk_rebuild_sn.py (the se/e/ne method of walk_rebuild.py, adapted to views with no rig joints):
- run 2's own traced leg borders; disc, cuff and foot split by rows (s 137-145 / 146-152 / 153-160, n 134-144 / 145-153 / 154-160)
- each foot placed where the packed frame has it (measured per frame, 98-100% pixel match), so footlock is identical: ALL FEET LOCKED, same spreads (0.88 px) and target errors as the packed s and n
- disc moves half the foot's vertical move; the cuff leans between them one whole row at a time
- drawn: cuffs and feet, body, then discs, so no disc is ever cut (a rising knee sits in front of the body's lower edge); a lowered disc leaves a 211e27 joint hollow, as on se/e/ne
- every frame one piece, no holes, still palette; lowest rows unchanged (160-163)

Output: walk35_touchup/frames/s_f0-7.png and n_f0-7.png (raw, from views_cam35_touchup), metrics_sn.json. Board: rhino_l/review/walk_sn_rebuild_2026-11-05.png (still, packed, rebuild, sel-out, 4x) and walk_s/n_rebuild_2026-11-05.gif. Not packed; se/e/ne and art/machines untouched. To pack: sel-out s and n into frames_selout as front and back (selout_rebuild.py lists only se/e/ne today).

## Fennec death se: Codex poses plus a hand-fixed lying pose, INSTALLED (2026-11-05)

Preston, after the se/back pose redraw ("Back only"), on the se lying pose: "Yes, hand-fix it", then on the result: "Install it".
- f0-f4 = Codex se f0-f4 from death35/codex-death-se-back (whole redrawn poses; f0 is the still).
- f5 = the old live se f5 (it reads as the fox lying down: tail, flat gold ear, head with eye, muzzle) with 70 pixels hand-fixed, outline unchanged: the scattered lilac stroke and steel bits under the belly became one folded hind leg (violet thigh, lilac cap, ink rim) and one steel boot shaded like the still's boots; three specks inside the far ear's gold became gold; three ground-row specks under the jaw became shadow. Script: D:/dev/_scratch/touchup-lane/se-lying/fix_se_f5.py.
- f6 = f5 with the 18 eye pixels set to #2E1A6E.
- Checks (check_se_new.py, own measure): all 7 frames pass the death35 rules (binary alpha, the still's 15 colours, one piece, no holes, no edge, lowest row 140), f0 = still, f6 = f5 eyes out. f5 ink 5.56% (was 4.69, still 6.12), cap 1.72% (still 2.35).
- Open: the lying fox is about 10% narrower than f4 and the still (51 px against 57-60); the old set shrank the same way. Full size would need a real redraw.
Installed in death35/frames/se_f0-6.png with preview_se.gif (3x, sel-out, the timings, plays once). Live se before this: death35/frames_pre_codex_se/. Repack of fennec_kit_sheet.png asked of the animation lane.
PACKED (2026-11-05) by the animation lane into art/machines/fennec/fennec_kit_sheet.png: only the six se death cells f1-f6 changed (checked against the backup here too), pack checks and fennec3d_check 0 failures, the packer's 1 px jolt allowance for se f1 removed since it now stands on the ground. Pack before: fennec_s/take-b/anim/backup_pre_codex_se/.

## 2026-11-09 Sprite touch-ups stopped: 2D sprites scrapped

Preston (relayed by the hub): "2D sprites are scrapped btw". Machines are now 3D models, rigged and animated (gorilla-3d and rhino-3d sessions lead). The lobster walk touch-up asked for on 2026-11-06 (se R3, ne R1, ne far left legs) was stopped at inspection: nothing written, touchup/lobster_l_walk never created. Still open and now moot: the rhino s/n leg rebuild in rhino_l/take-a/anim/walk35_touchup/frames (s_f*, n_f*), never packed. No paid run was in flight.
