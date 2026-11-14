Gorilla (ape_l) walk at 35 degrees, touched up (touch-up lane, 2026-11-05). Kept by Preston ("do 1 2 and 3 i agree").
Source, read only: ../walk/ape_l/final/frames/ (walk lane). That folder is not changed; these frames replace it for packing.
5 views x 8 frames, 192x192, raw (no outline, the packer adds sel-out), 125 ms a frame, same order and names as the source.
What changed (5 to 29 px a frame): 1 px specks, spurs and notches in the limbs and the filled joins; enclosed see-through
pinholes of 4 px or less filled with their neighbours' colour; se f0 corner-only slivers joined side-on.
Kept exactly: every pixel equal to the idle still (placed at 16,30, 1 px dip on f0 and f4); the bottom 8 rows (foot lock);
the still's 15 colours; binary alpha; one piece per frame. Left open on purpose: ne f3 and f4 gaps beside the far forearm.
Checks: report.json (per frame). PixelLab score, ne strip: 88.5 before, 98.4 after; lint ne f1 holes 9 -> 0, 0 errors.
Files: frames/, ape_touch.py (rebuilds frames/ here from the source), board_game.png, ape_walk_<view>.gif,
ape_walk_touchup.aseprite (touched-up layer plus the walk lane's frames on a hidden layer).
