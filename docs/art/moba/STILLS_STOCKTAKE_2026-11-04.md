# Approved stills: stock-take against the engine spec (sprite factory lane, 2026-11-04)

Read-only check. No pixels were changed. The script is in the session scratchpad (`audit_stills.py`); its
numbers are below.

## Answer
- **Missing 8-way stills: none.** All 13 roster machines in `docs/plan/moba-kits.md` have 8 drawn views on disk.
- **Not yet approved: the lobster only.** Take G (`lobster_l/take-g`) is still waiting on Preston's look.
- **Ruled out:** crab (`crab_m`, replaced by the lobster) and frog (`frog_m`, scratched). Neither is on the roster.

## What the check found

### 1. Size classes do not show in height on the shared grid
At 50 texels per metre every sprite pixel is 0.02 m, so pixel height is height in the world.

| Class | Machine (south-view height, px) | Height in the world |
|---|---|---|
| L | rhino 70, gorilla 72, hippo 70, lobster 66 | 1.32 to 1.44 m |
| M | kangaroo 80, shoebill 80, wolf 72, falcon 72, chameleon 65, pangolin 56 | 1.12 to 1.60 m |
| S | squirrel 72, hummingbird 72, fennec 72 | 1.44 m |

- In the 3D world the squirrel would stand as tall as the rhino, and the kangaroo and shoebill would stand taller
  than every tank.
- The large machines are longer, though. Side-view widths: rhino 103, hippo 123, lobster 124, against 74 to 92 for
  the small machines. Mass may still read. That is not checked; only a board will show it.
- **Decided: option B** (Preston, 2026-11-04, after the size board).
  - Texel size by class: L 0.020 m, which is the world's 50 per metre; M 0.018 m; S 0.016 m.
  - The stills stay as drawn, and the engine sets each sprite's pixel size from its class.
  - New machines are drawn at today's pixel sizes.
- The options he was given:
  - (A) Redraw M and S smaller. Costly, and nine machines would need approval again.
  - (B) Give each class its own texel size, for example L 0.020, M 0.018 and S 0.016 m. Cheap, but the grid is
    no longer shared.
  - (C) Keep sizes as drawn and show class through footprint and hitbox only.

### 2. Three canvas conventions
| Canvas | Foot row | Machines |
|---|---|---|
| 192x192 | 160 | rhino, hippo, lobster, pangolin, wolf |
| 160x160 | 130 | gorilla |
| 160x160 | 140 | kangaroo, shoebill, falcon, chameleon, squirrel, hummingbird, fennec |

- `tools/art/pack_rhino_3d.py` assumes 192 cells.
- The recommendation is to leave the approved stills alone and have each machine's packer read its own foot row.
  The gorilla's animation frames are already built on 160/130.

### 3. Sel-out is added at pack time, not stored in the stills
- No approved still has the #141218 outline (0% of silhouette-edge pixels). Only 3 to 13% of edge pixels are dark
  at all.
- This is by design for the rhino: `pack_rhino_3d.py` lines 58-59 run `selout()` on the stills as it packs them.
- Every new machine's packer has to do the same, or its idles will lack the outline that its walks have.

### 4. Mirrored west views drop what was drawn
- The engine draws sw, w and nw as se, e and ne mirrored. The drawn west views differ from those mirrors on 15 to
  28% of their pixels, and up to 42% for the lobster's nw. Some are also 1 px wider or narrower.
- Most of the difference is the shading, which mirroring moves to the other side.
- It matters for the asymmetric machines:
  - the lobster's big crusher claw changes sides when it turns west;
  - the squirrel's tail, cut to one side by hand, flips too.

## Proposed order (nothing is generated until Preston says yes)
1. **Lobster take G:** his look. It is the only roster gap.
2. **Size board:** all 13 at in-game scale on the 50 texels/m grid, next to option (B). It is free, scripted from
   the approved stills, and no pixels change. He picks A, B or C. A second machine should not go into the 3D world
   before that.
3. **Remaster pilot on the gorilla's five stills:** detail ink matched to the rhino walk's rule, palette locked,
   shown side by side with his original.
   - Why the gorilla: the animation lane's set B and the hex-gem cutouts (`pack_ape_fx.py`) are both built from
     these stills.
   - Cost: our own scripts or Codex, so free.
   - **Done 2026-11-04. Decided: sel-out only.** The approved stills ship as drawn and the packer adds sel-out.
     Record: `ape_l/take-a/remaster-pilot/RUN.md`.
4. **The other 11:** the same pass in kit-doc order (hippo, lobster, kangaroo, pangolin, wolf, shoebill, fennec,
   falcon, squirrel, chameleon, hummingbird), each with a side-by-side board, once the pilot's look is approved.

## Size board (built 2026-11-04)
- **Board:** `SIZE_BOARD_2026-11-04.png`. All 13 machines are shown at 50 texels per metre and 2x, side (e) and back
  (n) views, feet on one ground line. The top half is as drawn; the bottom half is option B (M at 0.9x, S at 0.8x).
- **Side silhouette area, as drawn:**
  - L 1.38 to 2.17 m²;
  - M 0.84 to 1.27 m²;
  - S 0.79 to 1.22 m².
  So the tanks keep the most mass in side view.
- **From the back** (the chase camera's main view), as drawn, everything is 1.18 to 1.64 m tall. The fennec (1.54 m)
  matches the rhino (1.54 m).
- **Option B:**
  - The small machines drop to 1.15 to 1.23 m from the back.
  - The kangaroo (1.42 m) and shoebill (1.48 m) still stand as tall as the tanks.
  - The pangolin becomes the smallest machine on the roster (1.06 m from the back).
- **Script:** `size_board.py`, in the session scratchpad. It reads the approved stills and writes only the PNG.

## Not verified
- Mass on screen (point 1): the size board above now covers it as area. It is not checked in the 3D world.
- `rhino_l/take-a/forge/RUNS.md`, named in the lane brief, is not in `take-a/` itself. It may be under `anim/`,
  which this check did not search.
- Whether the drawn west views were ever meant to ship. The lane brief says they are mirrors.

## Ink measure (2026-11-04, read-only)
- Preston: "Measure them". Script: `measure_ink.py`, in this folder. It uses the ink rule in
  `rhino_l/take-a/anim/detail_ink.py`, and it writes no pixels.
- **Share** is the part of a view's interior drawn in the machine's own darkest colour. **Target** is the lower of
  se and e, the gate the gorilla pilot used.
- Kangaroo, wolf and squirrel are read from `fixed/`; the others are read from `views/`.

| Machine | s | se | e | ne | n | Target | Clear gaps (under 0.75 x target) |
|---|---|---|---|---|---|---|---|
| rhino | 6.8 | 8.4 | 10.0 | 8.1 | 10.1 | 8.4 | none |
| gorilla | 10.9 | 9.1 | 9.5 | 8.3 | 9.0 | 9.1 | none (sel-out only, decided) |
| hippo | 6.6 | 6.5 | 6.4 | 4.3 | 3.6 | 6.4 | ne, n |
| lobster (take G) | 6.4 | 8.6 | 11.8 | 9.0 | 6.1 | 8.6 | s, n |
| kangaroo | 9.0 | 9.0 | 8.8 | 6.9 | 6.8 | 8.8 | none |
| pangolin | 3.5 | 1.8 | 2.1 | 2.1 | 2.5 | 1.8 | none |
| wolf | 8.9 | 7.9 | 5.6 | 6.3 | 2.6 | 5.6 | n |
| shoebill | 8.0 | 6.5 | 5.3 | 4.3 | 5.9 | 5.3 | none |
| fennec | 5.6 | 6.7 | 6.7 | 4.0 | 3.9 | 6.7 | ne, n |
| falcon | 5.8 | 4.2 | 4.5 | 2.7 | 3.3 | 4.2 | ne |
| squirrel | 7.1 | 5.7 | 5.5 | 4.1 | 6.0 | 5.5 | ne |
| chameleon | 8.2 | 6.7 | 9.2 | 6.8 | 8.0 | 6.7 | none |
| hummingbird | 10.8 | 7.9 | 8.7 | 7.0 | 4.7 | 7.9 | n |

All shares are percentages.

### What it shows
1. **The backs are the thinnest views, and they are the ones the chase camera mostly sees.**
   - Among the 11, n is under its own target on 7 machines and ne is under it on 7.
   - The biggest gap is the wolf's n: 2.6% against 5.6%. Its front is 8.9%.
2. **Clear gaps: 10 views on 7 machines** (the last column).
3. **The contour rule overshoots on every machine, not just the gorilla.**
   - Wherever it fires, the view lands at 1.5 to 2.8 times its target. For example, the fennec's s goes from 5.6%
     to 18.3% against a target of 6.7%, and the falcon's ne from 2.7% to 11.9% against 4.2%.
   - So the look Preston turned down on the gorilla is what this rule does in general.
4. **The pangolin and chameleon have no gaps.** The pangolin is the least inked machine (1.8 to 3.5%), but it is
   even across its views.
5. **The gorilla's numbers match the pilot exactly**, so this measure agrees with the trial he saw.

### Next, only on Preston's yes
- Try a capped rule on one machine: it adds ink, strongest contrast first, only until a view reaches its target.
  Show it on a board next to his original.
- The other choice is sel-out only everywhere, like the gorilla.
- **Hippo done (2026-11-04):** Preston kept the capped ink on ne and n. Record:
  `hippo_l/take-b/remaster-pilot/RUN.md`.

## Capped ink, five more (2026-11-04, trial only)
- Preston: "Build all five". This is the same rule he kept for the hippo. Script: `capped_ink_trial.py`.
- No approved still was changed.
- Overview: `CAPPED_INK_BOARD_2026-11-04.png`. Each machine's full board, numbers and `RUN.md` are in
  `<machine>/<take>/remaster-pilot/`.

| Machine | View | Before | Capped | Pixels added | The full rule would add |
|---|---|---|---|---|---|
| Wolf (from `fixed/`) | n | 2.6% | 5.6% | 43 | 161 |
| Fennec | ne | 4.0% | 6.7% | 50 | 302 |
| Fennec | n | 3.9% | 6.7% | 49 | 243 |
| Falcon | ne | 2.7% | 4.2% | 32 | 223 |
| Squirrel (from `fixed/`) | ne | 4.1% | 5.6% | 38 | 230 |
| Hummingbird | n | 4.7% | 7.9% | 64 | 182 |

### By eye (Claude, on the overview at 4x)
- **Wolf n:** a seam across the hips, where the body meets the back legs.
- **Fennec ne:** the leg, haunch and tail-segment seams, and the back of the neck.
- **Fennec n:** the collar under the head, and the hip joints.
- **Falcon ne:** the line under the helmet, the shoulder joint and the feet.
- **Squirrel ne:** around the head, ear and arm. It has the only lone pixel of the five.
- **Hummingbird n:** the edges where the two wings cross, plus the neck. This is the most visible change of the five.
- **Overall:** as on the hippo, each change is small (32 to 64 px) and sits on joints and seams. Nothing overshoots,
  and no view looks worse to me. At game size the difference is slight.
- **Not checked:** the game-size rows on the per-machine boards.

### Five installed (2026-11-04)
- Preston: "Keep all five". The capped views above are now the approved stills: wolf n and squirrel ne in `fixed/`, fennec ne and n, falcon ne and hummingbird n in `views/`.
- Originals backed up beside each folder (`fixed_pre_ink/`, `views_pre_ink/`). sha1 before and after in each machine's `remaster-pilot/RUN.md`.
- With the hippo, six machines carry capped ink. Lobster (take G) and the mirror question are still open.
