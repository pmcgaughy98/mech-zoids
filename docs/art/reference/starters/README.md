# Starter reference sprites (Preston, 2026-10-12)

Preston's detailed side-view reference for each new starter, the counterpart of his green gorilla sprite. Targets for
the individual refine passes: outline overlap, colours and design details are measured against these, never copied
pixel for pixel. Files: `pangolin_m.png`, `hippo_m.png`, `shoebill_m.png`, `kangaroo_m.png`; the `overlay_*.png`
files are `tools/art/compare_views.py` output against the installed e view (grey both, red his only, blue ours only).

## Main colours in each reference (median-cut, 12 colours, share of the sprite's pixels)

| machine | colours (hex:share) |
|---|---|
| pangolin | af660c 13%, 0c0b0a 11%, da8819 11%, 080706 9%, 6b5640 8%, 482b21 8%, 262222 7%, 8f2a0d 7%, eda93c 6% |
| hippo | 141118 13%, 96658a 9%, 523c58 9%, 110d14 9%, ac7ca3 9%, 6b4168 9%, 3f2e43 7%, 221f28 7%, 7c4b6a 6% |
| shoebill | 82a6d7 15%, 090d1d 13%, 223562 11%, 364d7e 8%, 070a18 8%, cfad6b 7%, 111e3c 7%, 040819 7%, 24242a 6% |
| kangaroo | 110606 11%, e6724c 11%, 231b1e 10%, ae301d 9%, 781a12 9%, 100b0d 9%, 303036 8%, 493e41 7%, d75d3d 6% |

Reading: every reference puts a quarter to a third of its pixels in near-black (outlines and the dark frame), far
more than our sprites or Legacy's edges. The kangaroo's red is orange-red (e6724c / d75d3d lit, ae301d / 781a12 in
shadow), not the maroon of our v3. The shoebill's dominant plate colour is the light blue 82a6d7, with the deep blues
as the second tone. The hippo's plum runs 96658a to 523c58 with a lighter ac7ca3 highlight.
