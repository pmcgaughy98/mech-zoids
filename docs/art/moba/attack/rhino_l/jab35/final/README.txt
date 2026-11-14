Rhino horn_jab at 35 degrees, final five-view set (2026-11-06). Raw: no outline (the packer adds sel-out). NOT packed.
Frames: jab/<view>_F0..F5.png (also frames/<view>_f0..f5 for the board and video scripts). 192x192 canvas, feet row 160, still palette.
Moves: F0 standing, F1 wind-up, F2 LUNGE = the hit, F3 toss, F4 settle, F5 recover.
Timing proposal (placeholder, the kit owns it): holds 2,2,1,2,1,1 ticks of 100 ms played at 2x = 0.45 s; hit lands at 0.20 s. JAB_HIT_FRAME 2.
Sources: s from s3; se from s3 (second take: holds its facing on the toss; s1's head turned side-on); e from s1; ne and n from s2.
Checks (column 1 fit to the still, IoU): s 0.998, se 0.963, e 0.944, ne 0.955, n 0.964. Ink 0.075-0.119, matching each still.
Known: s F1-F4 reach 161-172, below the feet row: the horn comes toward the camera (deliberate). se row's lowest pixel is 159, 1 px above the feet row.
ne and n jabs are subtle by nature (the horn goes away from the camera). Codex tokens: s1 27,796 + s2 22,730 + s3 27,873 = 78,399 (worst case was 345k).
Board: board_jab_3x.png (still in column 1). Video: rhino_jab_phone.mp4 (4 loops at game speed, then 1 slow).
Packing: only after Preston approves. horn_jab joins TILT_ANIMS in tools/art/pack_rhino_3d.py, never the .tres; back up first; tell the Rhino session and the walk lane.
