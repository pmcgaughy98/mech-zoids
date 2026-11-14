# Fennec cam35: lane report (fleet redraw lane, 2026-11-04)

One Codex image, **70,848 tokens**. Fleet total: **128,162** (gorilla 57,314 + fennec 70,848).
- Board: `board_cam35.png`. Views: `../views_cam35/`. Checks: `verify.txt` and Codex's `REPORT.txt`, `heights.txt`, `shape.txt`.
- `../views/` is byte-identical (sha256, 8 of 8). No file in `../anim/`, `../remaster-pilot/` or `../views_pre_ink/` changed.

## What changed from the gorilla recipe
- **Per-view heights from the fennec's own shape guide** (`cam35_fleet/hull_guide.py`). At 35 degrees its tall ears tilt back:
  - the front view gets a little SHORTER than approved (guide s 49x65, against approved 72);
  - the rear views get taller (ne 85, n 86).
  So the prompt says that per view, not "every view grows the same".
- **A part-count line:** exactly two ears, two front legs, two hind feet and one tail. This was added because the gorilla grew an extra arm.
- **Generic scripts:** `cam35_fleet/prep_machine.py` builds the refs and palette; `cam35_fleet/fleet_board.py` builds the board and checks.

## Result
| view | W x H (approved) | H / approved | H / shape guide | eye px (expected at 35) | accent (approved) |
|---|---|---|---|---|---|
| s | 47x63 (49x72) | 0.88 | 0.97 | 28 after the eye fix (Codex 22; expected 28, floor 24) PASS | 5.0% (5.0%) |
| se | 58x68 (63x72) | 0.94 | 0.93 | 18 after the eye fix (Codex 10; expected 19, floor 16) PASS | 5.9% (5.9%) |
| e | 74x68 (74x74) | 0.92 | 0.87 | 12 (approved 18) | 5.8% (5.8%) |
| ne | 58x76 (58x75) | 1.01 | 0.89 | 0 | 5.9% (5.9%) |
| n | 42x82 (44x77) | 1.06 | 0.95 | 0 | 5.9% (5.9%) |

- Palette PASS (15 colours). Lowest row 140 in all five, no border contact, alpha on or off.
- view_check lone 0.094, so no despeckle. sheet_judge asks to redo ne, n and nw on height alone (waived for cam35).
- **Shape measure caveat:** e reads "59 degrees" by height over width. That is because Codex drew the ears shorter, and the measure cannot tell shorter ears from a steeper camera. Ignore it for e. By the same reading, s is 33 and n is 32.

## Eye checklist
- **Top shows in every view:** PASS.
  - The crown of the head is the biggest shape in s, and the back and the tail's top band show in se, e, ne and n.
  - Unlike the gorilla's s, the fennec's front view reads "from above", not "taller".
- **Far feet higher in e, se, ne:** UNCLEAR. Codex can't tell them apart either.
- **Five views agree:** the heights follow the guide's per-view pattern at 0.87 to 0.97 of it; e sits lowest against the guide.
- **Same machine, no new or extra parts:** PASS by eye (two ears, one tail). In e the far ear shows beside the near one, which is right from above.
- **Plates and seams:** PASS. Accent is at the approved share in all five, and the plates are firm.
- **Eyes:**
  - PASS after the eye fix: s 28, se 18.
  - Codex drew s at 22 and se at 10, a miss.
  - ne and n have no eye pixel: PASS.
- **Game feel's turn test (2026-11-04):** no break in the turn, but the fennec grows as it turns away.
  - Heights are s 63 to n 82, a 19 px spread; the approved spread is 5.
  - e to ne is the biggest step, +8 px, and there the tail changes from lying flat to angled.
  - The far feet in e are unclear.
  - Bar clearance and depth are fine.
  - **Preston accepted the growth (2026-11-04): "Looks fine, keep it".** The fennec cam35 views are final.
  - Board: `match/cam_angle_test/fennec35_board_2026-11-04.png`.

## Not verified
- The in-game turn.
- The mirrored views, checked only by sheet_judge.
- The widths came back a little narrow (s 47 vs 49, se 58 vs 63). The gorilla lane found that a lost width makes a front view read "taller" rather than "from above".

## Eye fix (2026-11-04, on Preston's "Yes, fix the eyes")
- **What happened:** Codex drew both eyes at about the right size, but the palette mapping turned some pale glow pixels into steel (d6d6dc, 9d9ba2) or violet highlight (e0c8ff).
- **What the fix did** (`fix_eyes.py`):
  - put those pixels back on the eye ramp, inside the dark socket Codex drew;
  - made the two front eyes mirror images;
  - turned one stray pixel at each eye's lower inner corner into socket accent.
- **Pixels changed:** s 13 (eye px 22 to 28), se 8 (10 to 18).
  - Every changed pixel was checked against its old colour first.
  - The Codex originals are kept as `s_codex_original.png` and `se_codex_original.png`.
  - Before and after: `eye_fix_before_after.png`.
- **Board and checks** are rebuilt (`board_cam35.png`, `verify.txt`). Palette and accent are unchanged.
- **Game feel at game size (2026-11-04):** both repainted views now read. In s the eyes show as two light dots, and in se the eye shows on the side of the head. Board: `match/cam_angle_test/fennec35_board_2026-11-04.png`.
  - The bar touches the fennec only at the base-wall camera spot (14 px in the worst frame). Game feel puts that down to the existing camera clamp, not the art.
- **Not fixed:** the `slices/sw.png` front three-quarter (it is not in `views_cam35`), and one grey pixel under the right front eye, which is cheek, not eye.

