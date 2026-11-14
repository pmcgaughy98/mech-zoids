Gorilla walk at 35 degrees, final frames (walk lane, 2026-11-05). 5 views x 8 frames, 192x192, raw (no outline;
the packer adds sel-out), 125 ms a frame, knuckle walk in diagonal pairs (plan A, chosen by Preston).
Sources: e and se from run1 (Codex), se f0 with one loose pixel removed by hand; ne, s and n from run2 (Codex).
Fix by the walk lane (Preston: "Fix it first"): slits left where a limb slid back from the pinned body (pixels solid in the
idle still, now enclosed holes) filled with the body band on either side, or the still's own body colour there. Only the
greens are used. s and n untouched.
s: filled px per frame [0, 0, 0, 0, 0, 0, 0, 0]
se: filled px per frame [20, 17, 2, 6, 45, 34, 0, 6]
e: filled px per frame [2, 5, 4, 34, 7, 37, 0, 5]
ne: filled px per frame [22, 32, 9, 30, 36, 5, 1, 35]
n: filled px per frame [0, 0, 0, 0, 0, 0, 0, 0]
After the fill, walk_tools.py seams still flags 0-32 px a frame in e, se and ne. Looked at in e f3, se f4 and ne f4 (4x):
open space beside the far forearm and far arm strip at the silhouette edge, where the ground shows as that arm swings.
Left open on purpose; a second fill pass would push the outline back toward the idle and risk ghost limbs.
Checks on these 40 frames: footlock.json (all feet locked), one piece each, binary alpha, the still's 15 colours only.
Before/after: seam_fix_before_after.png. Preview of all five views at 8 fps with sel-out: walk_5views.gif.
