Fennec trot at 35 degrees, final frames (walk lane, 2026-11-05). 5 views x 8 frames, 192x192, raw (no outline; the packer
adds sel-out), 100 ms a frame (10 fps), looping, trot in diagonal pairs (RF+LH swing f5-f7, LF+RH swing f1-f3, both pairs
planted f0 and f4), body dips 1 px on f0 and f4, the tail one frame later. 3.5 px a step = 0.56 m/s, the kit's STRIDE.
Built from the standing 35 still (../views_stand35, step A), NOT the seated idle: idle to walk changes pose, as before.
Sources: se from run1 (Codex); e, ne, s, n from run2 (Codex: ne tail repaired, e chest repaired, s and n new).
Checks on these 40 frames: one piece each, binary alpha, the still's 15 colours only; above the legs equal to the standing
still after the dip. Foot lock by Codex's stamp measure (run1/checks.txt, run2/checks.txt): spreads 0.5-0.95 px, target
errors 0.5 px or less. walk_tools' silhouette footlock (footlock_silhouette.json) passes s and n; in e, se and ne it
merges neighbouring soles (the fennec's feet stand close), a tool limit. ne tail light px 68-77 (still 70); e gold 4
solid pieces every frame. Seams flags left are gaps between legs or between tail and leg, open on purpose.
Lowest rows: up to 164 in s and n (near feet stepping toward the camera), 163 in se and ne. Preview with a plain 1 px
dark outline: walk_5views.gif. Not touched up, packed or tested in the game yet.

2026-11-05, after the above: s widened (Preston: "Widen front view front legs a bit as it looks like its still walking in
the sitting position"). widen_s/widen_s.py 2 pulls the s legs apart 2 px each side below row 140 (1 px on rows 141-144),
leaving the gold chest plate exactly in place. The gap between the front legs goes from 4 px to 8 px. Feet still locked
(spreads 0.5 px or less), seams 0, 15 colours, one piece. The standing still views_stand35/s.png got the same change;
final/stills holds the 192-canvas stills these frames match. Originals: widen_s/before/. Compare: widen_s/s_before_after.gif.
Preston: "looks great" (2 px each side kept).
