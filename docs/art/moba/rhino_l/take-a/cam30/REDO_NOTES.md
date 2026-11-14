# Rhino cam30 redo: notes for the brief (sprite factory lane, 2026-11-04)

Not run. Priced at 65k to 100k Codex tokens for one image; it waits on Preston's yes, relayed by Mech-Zoids.

## Angle each cam30 view was actually drawn at (3D lane, `../../3d_test/rhino_cam30.json`, NOTES.md)
Measured from the height a solid rhino needs to match each view. The carve-at-each-pitch scan gave no usable answer on the rhino.
- se, ne, n: about 38 degrees, close to the 34 target.
- s: about 48 degrees, too steep. The redo must bring it down.
- e: far lower than target. This confirms the failed camera check in REPORT.txt.

## Fixes planned for the redo
- **Angle guide.** A second attachment: a plain box with the rhino's length, width and height (2.08 x 1.44 x 1.36 m, 104 x 72 x 68 texels), drawn at 35 degrees in each of the five views. This should hold s down, lift e, and keep the views agreeing.
- **The e view.** Don't call it a "profile". Write "side view from 35 degrees above, the top of the back showing as a wide band, the far feet higher on the page".
- **Height check.** Each view's height against the box guide's prediction; more than about 8% off is a miss.
- **Plates and seams.** Straight cut plate edges and bevelled corners, with the approved accent share (6 to 9%) as the target. If the seams still come back thin, run the free capped-ink pass afterwards.
- **Widths.** Per-view targets from the approved views. The se should be about 89 px; the cam30 se came back 78.
- **Order.** Run it after the drone's five-view job shows the guide works.
