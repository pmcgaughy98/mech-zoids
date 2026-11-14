Hippo walk at 35 degrees, final from the walk lane (2026-11-05). Preston approved the motion: "Approve, to touch-up".
Machine: hippo_l take-b, still views_cam35_touchup_shade1 (APPROVED, "Keep 1 px version"), copied to stills/.
Frames: frames/<view>_f0.png to _f7.png for s, se, e, ne, n. 192x192, raw (no outline; the packer adds sel-out),
feet row 160 (a planted foot nearer the camera sits up to 163), the still's 14 colours, binary alpha.
Sources: e, se, ne from run1/walk/frames (Codex run 1, 224,713 tokens); s, n from run2/walk/frames (Codex run 2,
100,320 tokens). Total 325,033. Codex's leg layers and body layer are in run1/ and run2/ walk/layers and source/.
Gait: four-beat walk like the rhino (lateral4). LF swings f1-f3, LH f3-f5, RF f5-f7, RH f7-f1, with lifts 2, 3, 2 px.
The body dips 1 px on f0 and f4. 8 fps (125 ms a frame), looping. Step 3 px a frame in e (0.48 m/s at size L).
Planted frames and sole targets for every foot: targets.json (from plan_walk). Foot labels: ../feet.json.
Checks: foot lock within 0.9 px (Codex's stamp measure); walk_tools footlock passes, except se RH, where the sole merges
with the belly (a tool limit). Discs identical to the still, specks within the still's count plus 2.

For touch-up (known defects, coordinates on the 192 canvas, approximate; look at 8x):
- se: dark body fill hangs below the belly beside the near hind leg (RH), a block with a straight edge around x 58-66,
  rows 127-140 (seen on f0, f1 and f5; check all 8). Loose dark specks left of the RH knee disc, around x 44-48,
  rows 114-120 (f0, f1). The still there shows background below the belly.
- ne: dark body fill hangs to the right of the far hind foot (LH), around x 64-75, rows 148-160 (seen on f1-f3; check
  all 8). A 1 px enclosed gap on f1. (Corrected 2026-11-05: I first listed a dark vertical line in the LH foot pad
  as a defect. Touch-up found it sits between the grey pad and the lilac toe in the approved still too, so it is part
  of the design and stays.)
- s: 11 px gaps between a front foot and the jaw on f0, f1, f4 and f5 are real space. Leave them open.
Sway (agreed with touch-up, Preston judges): lean R = -1 0 +1 +1 +1 0 -1 -1 for f0-f7 (character's right +). Screen x:
-R in s and se, +R in n and ne, 0 in e. Bob 0 1 1 0 0 1 1 0 on top of the dip. Lock each planted foot by its own box
(se RH stands on row 135, ne RF on row 136, far above the bottom rows).
After Preston approves touch-up's version, the walk lane packs it with tools/art/pack_hippo_3d.py and a backup. Check
the hippo kit's full_speed_walk_rate (stride 0.48 m/s), or its feet will slide in game.
