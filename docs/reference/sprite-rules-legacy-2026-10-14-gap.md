# Why ours still don't pass as Zoids Legacy sprites (Claude, 2026-10-14)

Preston, 2026-10-14: "Still doesn't look like it could pass as a zoids sprite. Gorilla is closest but its still not
there yet either." Measured against 84 battle sprites cut from the Helic and Zenebas Legacy sheets (study only, in the
session scratchpad; nothing copied), our six installed side views. L is pixel brightness, 0 to 255.

| | width/height | fill (body share of its box) | thin parts (within 2 px of an edge) | mean L | L10 | near-black share (L<40) | lit share (L>150) |
|---|---|---|---|---|---|---|---|
| Legacy median | 1.66 | 0.51 | 0.22 | 96 | 45 | 0.08 | 0.12 |
| Legacy Shadow Fox (a dark machine) | | | | 94 | 52 | 0.09 | 0.11 |
| gorilla v66 | 1.29 | 0.55 | 0.18 | 87 | 37 | 0.22 | 0.07 |
| wolf v59 | 1.68 | 0.37 | 0.29 | 33 | 12 | 0.80 | 0.00 |
| kangaroo p46 | 1.01 | 0.36 | 0.21 | 70 | 19 | 0.36 | 0.00 |
| shoebill p67 | 0.93 | 0.35 | 0.35 | 89 | 11 | 0.31 | 0.27 |
| hippo p24 | 1.77 | 0.67 | 0.18 | 81 | 23 | 0.33 | 0.14 |
| pangolin p20 | 2.42 | 0.46 | 0.20 | 87 | 29 | 0.36 | 0.23 |

What the numbers and the side-by-side say, biggest first:
1. **Too dark.** Legacy keeps near-black to about 8% of a sprite, even on a dark machine; ours carry 22 to 80%. The
   causes in the pixelizer: plate lines drawn in each ramp's darkest shade, side and under edges dropped 3 to 4 shades,
   ramps that start near black, and grey ramps that stop at about L 125 (Legacy greys run to near white).
2. **Too spindly.** Wolf, kangaroo and shoebill fill 0.35 to 0.37 of their box against Legacy's 0.51: thin rod legs
   where Legacy legs are thick armoured pieces with big feet.
3. **Flat parts.** Legacy plates each carry a lit face, a mid face and a dark face with a bright edge; our box parts
   read as one flat shade per face. This is in the models, not the pixelizer.
4. **Angle.** Legacy battle sprites sit a little off side-on, turned toward the viewer with the camera slightly raised,
   so the far legs and the top of the back show; ours are exactly side-on at 10 degrees.
5. **Detail density.** Legacy fills the body with 1 to 3 px pistons, cables, joint discs and vents; ours have fewer.

Value trial (kept renders, palette only; `value_trial.py` in the session scratchpad; new pixelizer palette keys
`seam_shade` and `side_drop`, defaults unchanged): wolf lv1 (grey ramp 26262e to cacada, edges 3 shades) mean 67,
near-black 0.36, lit 0.08; kangaroo lv1 mean 96, near-black 0.18, lit 0.12. Easier to read, still not Legacy: points
2 to 5 remain.

## First slice: the wolf (2026-10-14, v62)
Camera raised to 18 degrees and the side view turned 20 degrees toward the viewer, Blender's toon_light matcap with cavity
shading, the lifted palette, thicker legs and paws, sparser plate lines: mean 33 to 71, near-black 0.80 to 0.34, lit
0.00 to 0.10, fill 0.37 to 0.43, thin 0.29 to 0.25. Details: `docs/plan/creature-factory-2026-10-12.md`, round 19.
