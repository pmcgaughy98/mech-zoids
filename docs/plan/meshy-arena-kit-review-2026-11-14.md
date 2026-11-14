# 3v3 Meshy kit: review, 2026-11-14

What it is: 7 Meshy models (210 credits, balance 860 to 650) skinned over the 3v3 blockout in
`scenes/moba3d/arena_blockout.gd` (`_meshy_kit`, `meshy_kit` toggle). The pieces are a wall, a tower base, a tower head,
a core, a slag rock, a scrap rock and a refinery backdrop. Bodies, nav mesh, sight and fog of war are unchanged.
Uncommitted.

Reviewed by the game feel lane and the kit design lane, from the off/on contact sheet
(`kit_look.png`, sent to Preston) and the code. Neither has seen an ability effect against the kit yet.

## Both lanes agree

| Item | Verdict | Fix | Credits |
| --- | --- | --- | ---: |
| Skin over unchanged bodies, one-flag toggle | Good | keep | 0 |
| Machines pop against walls and lane floor; blue base walls read blue | Good | keep | 0 |
| Amber strip glow on every neutral wall, plus slag and windows: one warm band, too bright near the camera, competes with warm abilities (bison) | Refine | neutral strips to about half glow or cool grey-white; full glow only on team pieces | 0 |
| Tower and core lost their team read (dark dome, thin strip) | Refine | a big team-coloured emissive band or top light on the tower head and core | 0 |
| Walls read as separate slabs; curves (plaza and base rings) get a sawtooth top, so every joint looks like a corner | Rework | one continuous top cap along each wall, overlapped joints on curves, posts only at real ends; or regenerate a tileable wall module | 0, or 30 |
| Slag rock glows like a hazard (same orange and name as the bison's slag) | Remove the glow; maybe regenerate | emission off now; regenerate as cold dark rock if it still reads hot | 0, or 30 |
| Refinery backdrop: one lumpy model cloned, glowing windows, looms over the field | Remove or regenerate | first dim it, push it back, fog it, vary its scale; if that fails, regenerate it hard-surface or go back to the old low skyline | 0, or 30 |

## One lane only

- **Game feel:**
  - The rocks look 15% wider than their bodies, so shots look like they pass through rock. Match the body at chest height.
  - Measure each model's real bounds instead of assuming 2 x 3 x 1.2 m.
  - The scrap rock reads as explosion debris; regenerate it or drop it.
  - Yellow or amber machines would sink into the orange.
- **Kit design:**
  - The round amber floor light pools (there before the kit) now read as area telegraphs; dim them, cool them or break the circle.
  - The plaza floor pattern and yellow rings compete with ground fields; tone the plaza down.
  - In row 2, a scrap rock clips into a wall and reads as a wreck.
  - Skin faces must sit within a few cm of the colliders, with tops at 3.0 m. Kangaroo wall stun, pangolin bounce, falcon and fennec bolts, and the cobra's Wall_Over clip depend on it.
- **Kit design: room to make:**
  - Cobra Breach: one wall module that can open, with its length equal to the gap.
  - Cobra Seam: one continuous wall face.
  - Clear floor round each tower for the fennec's gates.
  - Settle which walls the cobra can cross, and mark them.

## Corrections to the reviews

- Pit rims are still bare blockout; the kit skips walls under 2 m.
- The foundry 3v3 has no stealth brush by design. The bush caps were decoration on rock and wall tops, and they're off with the kit. If Seed Flare or chameleon ambushes need brush, that's a map design call for Preston.

## Proposed order

1. **Free pass, no credits.** Covers every Refine row and the free half of every Rework, Remove and Regenerate row:
   - neutral glow down or cool;
   - rock glow off;
   - team bands on towers and cores;
   - a continuous wall cap and overlapped curves;
   - rocks fitted to their bodies;
   - bounds measured;
   - backdrop dimmed, pushed back and varied;
   - floor light pools cooled.

   Then a new sheet with one ability effect in it, sent back to both lanes.
2. **Regenerate only what still fails** after step 1: wall module, cold rock, scrap rock, backdrop. At most 4 x 30 = 120 credits.

## Outcome (2026-11-14, after the free pass and two regenerations)

- Credits: 270 spent in all (210 first batch, 60 for wall_run and rock_cold). Balance 860 to 590 (440 monthly, 150 permanent).
- Free pass: pools at 0.25 energy and a cooler colour with the kit on; skyline sprite rows and bush sprite caps off with the kit on; plinth boxes and side panels off under kit walls; rocks fitted to their bodies (top at the body top, width at 1 m matches the body radius).
- wall_run replaces wall_piece. It has no amber strips, so it is tinted (0.4, 0.44, 0.55) and every wall gets a dark steel cap.
- Base walls get team-lit caps (KitTeamCapsBlue / KitTeamCapsRed). That cap is the "do not cross" mark for the cobra rule (inner walls only).
- rock_cold replaces rock_scrap and rock_slag, tinted (0.45, 0.47, 0.53) with warm_calm 0.85. Every rock is rock_cold now: the slag model's orange read as the bison's hurting field even dark and unlit (both lanes' fallback).
- wall_piece, rock_scrap and rock_slag stay in runtime/ as fallbacks. The code picks them only if the newer model is missing.
- Checks: arena_check 24 passed / 0 failed, match_check 67 / 0. Rough windowed frame time at the five test spots: kit on 1.36 to 2.01 ms, kit off 1.19 to 2.22 ms. About 490k kit triangles.
- Still open: the plaza yellow ring markings (kit design's floor tweak). Up close, edge walls differ from inner walls only by height (3.5 m against 3 m).
- Final comparison sheet: kit_look5.png (left kit off, right kit on; spawn, hex dome on the lane, bend rocks, pit, steep 57 degree view).

## Rock swap (2026-11-14, later): Poly Haven boulder replaces rock_cold

- rock_cold still read as smooth, pale shapes at chase-camera distance. Three free CC0 rocks from Patch's asset search went beside it: Poly Haven rock_face_01, Poly Haven namaqualand_boulder_04 and Kenney rock_largeA. No credits spent.
- Verdicts: the rock face was too dark and flat and disappeared into the floor; the Kenney rock looked like a cream-coloured low-poly placeholder; the boulder had the clearest shape and real stone surface.
- Preston picked the boulder. It is runtime/rock_boulder.glb (59,066 to 2,499 triangles, 1K textures), tinted (0.6, 0.63, 0.7) with warm_calm 0.85. It reads dull tan, not orange.
- Credit: source/rock_boulder/CREDITS.md (CC0, so no credit is required; kept anyway).
- The code picks rock_boulder, then rock_cold, then rock_scrap, whichever exists. rock_cold, rock_scrap and rock_slag stay as fallbacks. The rock_face and Kenney trial files were deleted.
- Patch search (back on: Preston's newest word, relayed by the hub 2026-11-14, is "just take what we can"): `npx --yes @patchgg/cli assets search "<words>" --type model --json` (or `--type material`), run from D:\dev\_scratch\patch-gg-try, no login, no install. CC0 or CC-BY only, keep each credit, skip ai=true hits, never for the machines.

## Plaza rings and edge walls (2026-11-14, later)

- Plaza (kit design's floor tweak): with the kit on, the plaza's inlay ring and rim line use their own cool steel colour (0.55, 0.6, 0.7, glow 0.15) in place of the theme's yellow line, and the alternating sectors are softer (0.9 instead of 0.8). The lane's yellow path edges stay. New ground.gdshader uniforms: plaza_line (alpha 0 keeps line_color, so other maps are unchanged) and plaza_sector_shade (default 0.8).
- Edge walls: the 3.5 m map edge walls get a neutral lit cap ("KitEdgeCaps", cool white). Base walls already had team-lit caps, so a lit cap now always means a wall the cobra can't cross; inner walls keep the plain steel cap.
- 