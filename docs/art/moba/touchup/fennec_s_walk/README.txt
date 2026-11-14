Fennec (fennec_s) trot at 35 degrees, touched up (touch-up lane, 2026-11-05). Kept by Preston ("Install both").
Source, read only: ../walk/fennec_s/final/frames/ (walk lane, s view widened). Not changed; these replace it for packing.
5 views x 8 frames, 192x192, raw (no outline, the packer adds sel-out), 100 ms a frame, same names and frame space.
Changed 2-11 px a frame: 1 px specks, spurs and dents. 1 px slits between legs left open (the walk lane's gaps).
Kept exactly: pixels equal to the standing still (1 px dip f0 and f4), the bottom 8 rows (foot lock), 15 colours,
binary alpha, one piece, eye colours. Ink share already matched the stills in every view, so no ink pass.
Files: frames/, fennec_touch.py, report.json, board_game.png, fennec_trot_<view>.gif, fennec_trot_touchup.aseprite.

Sway and bob, 2026-11-05 (Preston: "Keep, do all views", after the s test). Installed over the touch-up above.
The touch-up as it was (frames, GIFs, board_game.png, fennec_trot_touchup.aseprite) is in pre_sway/.
- Why: the trot read stiff because the body never moved (0 px sway, 1 px dip); the legs were fine.
- Method (sway.py, reads pre_sway/frames): a per-row warp, not cut-and-paste. The bottom 8 rows of each frame stay
  exactly (foot lock), the legs bend between the foot lock and a hip line, and everything above moves as one piece.
  The ear tips trail the head by one frame (full sideways, half up and down).
- Lean: over the planted front leg (walk lane: RF+LH planted f1-f3, LF+RH f5-f7). Character's right on f0-f3:
  R = +1 +2 +2 +1 -1 -2 -2 -1 px. Screen x = -R in s and se, +R in n and ne, 0 in e (the lean points at the camera).
- Bob: extra dy 0 2 1 0 0 2 1 0 on top of the 1 px dip, so the body is lowest just after each landing.
- Per view (hip line, ear base): s 142/113, se 132/105, e 140/110, ne 140/100, n 144/101.
- Pinholes: the lean sealed 1 px seams for one frame in se f3, f4 and ne f5, f6 (1-8 px); filled with the
  neighbouring dark seam colour. se f2 keeps a 17 px see-through gap between the legs, as in f1 and f3.
- Checks pass in all 40 frames (sway_report.json): one piece, binary alpha, same colours, bottom 8 rows equal,
  eye pixel counts equal. Legs lose up to 70 px on the low frames (knees bend).
- Files: frames/ (new), fennec_trot_<view>.gif (new, 3x, game sel-out), board_sway_all.png,
  fennec_trot_sway.aseprite (tags trot_<view>, old frames on a hidden layer), sway.py, install_sway.py.
