# Gorilla remaster pilot (sprite factory lane, 2026-11-04)

Preston: "Start the gorilla test". Still-only work: the approved `../views` were never written.
Script: `remaster_pilot.py`. Board: `board.png`. Numbers: `metrics.json`.

## What ran
1. **Detail ink.** The rhino walk's `contour` rule (`rhino_l/take-a/anim/detail_ink.py`, imported), with the same
   gate: a view gets ink only when its interior ink share is under the lower of se and e.
   - The gorilla's ink colour is its own darkest, #141a16, so the palette doesn't change.
   - First run: the gate counted only #141218, so every view read 0% and none was inked. Fixed, then rerun.
2. **Palette lock.** Every pixel is snapped to the 15 approved colours plus the roster outline #141218. The
   untouched views needed 0 snaps.
3. **Sel-out** (`selout_rhino.py`), for review only. The packer adds it in the game.

## Result
| View | Ink share before | After | Ink pixels added |
|---|---|---|---|
| s | 10.9% | not inked | 0 |
| se | 9.1% (target) | not inked | 0 |
| e | 9.5% | not inked | 0 |
| ne | 8.3% | 19.8% | 518 |
| n | 9.0% | 21.2% | 561 |

- For comparison, the rhino's liked walks sit at 5.8%. The gorilla is already the more inked machine.

## Decided: sel-out only (Preston, 2026-11-04)
- He first clicked "Keep the ink", then corrected it: "sel out only / i meant".
- The approved `../views` ship as drawn, and the packer adds sel-out. The ink trial below is kept as a record only.
- On the first click, Claude copied the inked ne and n into `../views`. Once this correction was seen, his
  originals were copied back (sha1 5283138 for ne, e0a5bc5 for n). The animation lane confirmed that nothing was packed
  in that window (the last ape pack was at 10:38) and that the ape pack check passes, so nothing needs a rerun.

## Verdict (Claude): ink rejected for the gorilla, sel-out only
- **The gate fired on noise.** ne and n were within one point of the target, and the rule then more than doubled
  their ink. Their backs now carry hard contour rings that the front and side don't have. That is the mismatch
  between views the rule exists to remove.
- **ne picks up speckle.** Broken single pixels show along the left forearm and the right hand.
- **Sel-out alone (board row 2) reads clean in every view.** That is what the packer already does.
- **So the gorilla's approved stills are remaster-ready as they are.**

## For the rest of the roster
- **Tolerance gate.** Ink a view only when its share is clearly below the liked views', for example under 0.75 times
  the target. The rhino's front (1.6% against 5.8%) still qualifies; a view a hair under does not.
- **Ink colour.** Count and draw ink with each machine's own darkest colour, not #141218.
- **Not checked.** The rhino's back walk went from 5.7% to 10.0% under the same marginal gate. This is the same
  pattern, flagged for the animation lane and not looked at.

## Files
- `views_ink_trial/`: the trial stills. s, se and e equal the approved views; ne and n are inked.
- `views_ink_trial_selout/`: the same with sel-out.
- Neither folder is packer-ready. Use `../views`: Preston ruled sel-out only.
