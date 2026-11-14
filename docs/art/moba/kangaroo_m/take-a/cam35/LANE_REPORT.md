# Kangaroo (kangaroo_m/take-a) at 35 degrees: lane report (fleet redraw lane, 2026-11-05)

**Preston's go:** "Go, start the kangaroo" (2026-11-05), after the hippo was accepted.
**Result:** one Codex image, **78,028 tokens**. Fleet total now **393,303** (of 0.9M to 1.5M).
**Verdict by eye: MISS.** Codex's own report says the same ("FAILED candidate").
- The rear three-quarter view (ne) shows the face: the head is drawn in profile with the muzzle and a cyan eye (3 px).
- se, e and ne barely read from above: they look close to the low-camera stills. Their heights are under the guide
  (e 78 against 83, ne 81 against 89, n 82 against 90).
- The front view's eyes are small (2 + 1 px against 2 + 2).
- Not sent to the game feel lane yet: the turn test waits for Preston's choice below.

- Board: `board_cam35.png`. Checks: `verify.txt`, Codex's `REPORT.txt`, `heights.txt`, `shape.txt`.
- Views: `../views_cam35/` (s, se, e, ne, n). `../fixed/` was not touched.

## What was sent
- The hippo's brief with the kangaroo's parts, palette (13 colours, including steel deep 38353e from the take's own
  finish) and numbers. The four take-2 changes and the part-count line are kept, plus a guard against a third arm or
  fist (the gorilla once grew an extra forearm).
- Heights from the kangaroo's own hull guide at 35 degrees: s 55x73, se 65x80, e 69x83, ne 65x89, n 55x90. It stands
  upright with tall ears, so the front gets a little shorter and the back views grow about 11 px.
- **New: the side-view fix.** The prompt says the side view is "about one and a quarter times as long as the front
  view is wide", the tallest view is set to 55% of the cell, and Codex reports the side over front ratio.
- Canvas 160, feet row 140, kept (the approved canvas). The tallest view tops out at row 59.

## Numbers (new against approved)
| view | W x H | W ratio | H ratio | H against guide | top row | eyes |
|---|---|---|---|---|---|---|
| s | 55x74 | 1.00 | 0.93 | 74 / 73 | 67 | 2 + 1 (miss) |
| se | 64x80 | 1.00 | 1.01 | 80 / 80 | 61 | 7 |
| e | 69x78 | 1.00 | 1.00 | 78 / 83 | 63 | 4 |
| ne | 66x81 | 1.02 | 1.05 | 81 / 89 | 60 | **3 (miss)** |
| n | 49x82 | 1.00 | 1.04 | 82 / 90 | 59 | 0 |

- **The side-view fix worked:** every width is 1.00 to 1.02, and side over front is 1.25 against the approved 1.25
  (wolf and hippo were 0.86 and 0.88 of approved).
- Palette PASS (13 fixed colours). Accent matches the approved share in all five. No third arm or fist.
- Far foot higher: se 131 against 140, e 123 against 140.
- Lit tops doubled (lightest orange-red 11 to 16% against 4 to 8%).
- Heights s 74, se 80, e 78, ne 81, n 82: very smooth (steps of 6 px at most), so a turn test would likely find no pop.
- view_check front/back 0.69 (below 0.80); one despeckle pass (lone 0.103 to 0.042).

## The eye checklist
- Top shows in every view: **weakly.** s shows lit tops on the fists, shoulders and thighs; se, e and ne look close
  to the approved.
- Far feet higher in e, se, ne: **yes** in se and e.
- Five views agree: **no.** The front matches the guide; the side and rear views fall short of it.
- Same machine, no new parts: **yes**, but ne turns the head to show the face.
- Plates hard, seams at the approved share: **yes.**
- Eyes: **miss** in s (small) and ne (should be none).

## Options for Preston
1. **Second image (recommended, about 80k tokens, fleet total about 475k, inside budget).** Keep the side-view fix
   (it worked). Add: ne shows the BACK of the head and both ears with the muzzle pointing away, no face; and push the
   side and rear views to their guide heights with the top of the thigh, tail and shoulders as broad bands.
2. **Turn test, then fix.** Paint over the 3 ne eye pixels and add 1 to the small s eye. The head in ne would still be a
   profile, and se, e and ne would still look nearly level.

## Not done
- No pixel fixes. No turn test asked. No frames redrawn. Nothing installed. Not committed.
