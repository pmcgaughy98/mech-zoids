---
name: hollowtide-sprites
description: Make or repair a Hollowtide creature's eight-angle views (and then its walk) in the house style, with image generation drawing and tools/art/sheet_judge.py deciding which views pass, which code can fix, and which to generate again. Use for any new creature, new stage, or broken angle set.
---

# Hollowtide creature sprites

Written by Claude on 2026-10-28 for Codex, from what the project has measured since 2026-10-12. Preston approves
every creature; nothing here replaces his eye. Read `CLAUDE.md` and `docs/AI_COLLABORATION.md` first.

## The split of work

- **Image generation draws.** Code never redraws a creature. A code renderer reads as 3D ("roblox"), and Preston
  judged Nano Banana 2.1's raw output better than our heavy finishing (2026-10-13).
- **Code judges and corrects.** `tools/art/sheet_judge.py` measures the eight views, fixes what moving or flipping
  can fix, and names the views to generate again. Nothing is copied from other games or repos; references are
  structure only.
- **Ask before paying.** Every generation costs credits. Give Preston the tool, the count and the estimate first.

## House style

- **References:** the creature's own approved views, then Tallowroot (`assets/sprites/arena/tallowroot/`). Never
  Preostmar; Preston called it one of the worst. Ask him before adding other style references.
- **Colours:** fantasy colours, not Earth-animal browns and greys. Keep the line's colour family across stages.
- **A new stage evolves, it does not grow.** Keep only two or three anchors (the face and eye motif, the signature
  part, the colour family). Change the silhouette, head shape, proportions, posture and palette shade, and turn the
  signature part into something new. Keep a line's named parts, for example the Flintram line's horn.
- **Canvas:** transparent, alpha 0 or 255 only, the creature bottom-centred. Use the size of the creature's own
  existing views: Rimefin is 128 px, Sparkwick 144, and Riftfin and Scourmaw 160. Do not assume a size from the
  creature's stage. For a new line, match the line's other stages.
- **Finishing Codex image output:** shrink the whole sheet once so that its median view height matches the target,
  give all eight views one shared palette (16 or fewer, see `docs/art/sprite-canon-2026-11-02.md`), then slice. Shrinking views one at a time, or giving
  each view its own palette, makes the views drift apart.
- **One Codex image job at a time.** Concurrent jobs share `~/.codex/generated_images`, and both logs of the
  2026-10-28 pair named the same file. Neither picked the wrong image that time, but Retro Diffusion misfiled a walk
  the same way.
- **Outline:** the game draws the black outline with a shader (`scripts/arena/creature_finish.gd`). Do not paint a
  heavy outline around the silhouette. Do paint a dark line inside the body where one part overlaps another, and give
  each main material 4 tones (highlight, base, shadow, deep shadow): sheets with 2 or 3 tones read flat (2026-11-02).
- **Lighting:** from the upper left, the same in every view.

## Read the canon first

Before every sheet, read `docs/art/sprite-canon-2026-11-02.md` and copy its numbers into the brief: colours, top-5 share, lone pixels, drawing for game size, the evolution step and the back-view rules. Preston, 2026-11-02: "dont forget to use what we need everytime we make new sprites with codex".

## Why Drembit's views agreed

Preston, 2026-10-31: "drembit was almost perfect ... future creatures should account for that so we dont keep
creating creatures we have to scrap eventually." Front and back are one body seen from opposite sides, so their
outlines should nearly cover each other. `python tools/art/view_check.py <folder>` prints that as front/back, where
1.0 is the same shape.

| Set | front/back |
| --- | --- |
| Drembit, raw sheet | 0.88 |
| Kithflare, raw sheet | 0.83 |
| Kithflare after its front was replaced by a separate redraw | 0.67 |
| The same set after three repair passes | 0.77 |
| Game Sparkwick | 0.33 |
| Kithflare, one fresh sheet under the rules below, first try | 0.88 |

The sheet agreed with itself, the separate redraw broke it, and repairs never won it back. Body length is not the
cause: Drembit is a long body, and across 51 creatures length has no link to this score.

Every new creature takes these from it:

- **One image.** All eight views come from one sheet. A view drawn later is drawn by a different hand.
- **Start from Drembit's brief,** `docs/creatures/codex-new-creature-2026-10-31/prompt-sheet.txt`. Keep its cell
  layout and its "eight copies of the exact same creature" paragraph word for word, and change only the design.
- **Neutral standing pose.** Legs under the body, no lean, no crouch, no action. Kithflare's brief asked for a body
  leaning forward ready to spring.
- **The signature shows from all eight views and clears the head.** Drembit's tail stands taller than its head, on
  both sides of the centre line. Kithflare's sat at head height on the centre line, so from behind it covered the
  head and the raw north view had no head at all.
- **A tail grows from a root as wide as the hips.** Preston on a thin stem rising from a round rump: "look like a
  monkeys". Give a bird a feathered tail that flows out of the back, and cover the rear in rows of feathers or scales
  with no round cheeks and no crease.
- **The signature keeps its height as it turns.** Kithflare's tail tip stood 78 to 79 px tall on e, w, ne and nw against
  81 to 86 on the other four, and Preston saw that as wrong perspective. The tip stands tallest from the front and
  lowest from behind, and east and west show the most reach, about 1.4 times the diagonals.
- **To change one part of a sheet, redraw the whole sheet with the old sheet attached,** naming what stays and what
  changes. Kithflare's tail and rear were replaced this way and front/back held at 0.88. The parts you meant to keep
  can still drift: both peacock tail takes came back with rounder heads and bigger eyes despite "keep exactly", so
  compare the result to the old sheet and report any drift. Say so plainly, Claude can move the new part onto the
  approved body by code.
- **A tail needs volume, not only the right height.** A stripe down one long shape reads as a flat feather from the
  side and back. Draw layered feathers instead, and remember a bigger tail draws the whole creature smaller in the
  game, because game size comes from solid area.
- **Keep the identity in what shows from behind:** shape, colour and the signature. Huge eyes and cheek patches exist
  only from the front, so they can't hold eight views together, and hard numbers on eye size pull the front away from
  the rest. Drembit's face is a small eye and a bill.
- **One head.** The front and side views must be the same head. Kithflare's front is a round chick and its side a
  hooked hawk. No number sees this, so look.

## The loop

1. **Eight angles first, in one image** (Preston, 2026-10-14). Generate one 3x3 sheet before any single front view,
   with the previous stage's sheet as the pose guide. Cell layout, the creature facing the middle:

   ```
   ne  n  nw
   e   .  w
   se  s  sw
   ```

   For a creature that is the same on both sides, the west column can be left to code (step 3). The pipelines that
   hold eight views together generate five directions and mirror three.
2. **Slice:** `python tools/art/slice_grid.py <sheet.png> <out_dir> [--canvas 128] [--feet 104]`. It cuts and
   places, and never changes pixels.
3. **Score the raw sheet first:** `python tools/art/view_check.py <out_dir>`, before any repair. Under 0.80 front/back
   means generate the whole sheet again with a changed prompt. Stop after two tries and report what is failing.
4. **Judge:** `python tools/art/sheet_judge.py <out_dir>`. It prints two verdicts:
   - **FIX:** code corrects these. Run `python tools/art/sheet_judge.py <out_dir> --fix <fixed_dir>
     [--mirror-from east|west]` and judge `<fixed_dir>` again. Mirror only a creature that is the same on both
     sides. For one-sided parts (a horn or blade on one side, a lopsided body), pass `--asymmetric`; mirror faults
     then become REDO.
   - **REDO:** do not redraw one view of a new creature. If the drawing only needs moving, trimming or recolouring,
     do that in Aseprite. Otherwise generate the whole sheet again with the correction in the prompt. An installed
     creature whose other views are approved may get one view redrawn as a last resort: keep it only if front/back
     stays at or above where it was. Stop after two tries and report what is still failing. Do not loop on credits.
     Claude wrote the earlier rule here, "generate only those views again", and following it is what broke Kithflare.
5. **Look.** Things the judge cannot measure:
   - The back diagonals (ne, nw) must not show the face. A colour test for this failed in both directions on
     2026-10-28.
   - The north view must point north. The judge's `turned` check caught Sparkwick, but lopsided creatures trip it.
   - Before paying to redraw a view the judge flags, check that another file doesn't already hold it. Sparkwick's
     (2026-10-28) north file held its northeast view, its northwest file held its north view, and its northeast
     file showed the face. Putting the files back in the right slots and flipping the northeast for the northwest
     fixed the back views for free (`docs/creatures/sheet-judge-2026-10-28/sparkwick/`).
   - Before paying to redraw a view flagged `turned`, check whether it only leans. `tools/art/aseprite/fix_view.lua`
     slides pixel rows and repaints named pixels with no new colours, and it passed Gruntle's north on 2026-10-30
     (`docs/art/reference-measurements-2026-10-30.md`). A view truly drawn turned, like Sparkwick's, stays a redo.
     `tools/art/north_straighten.py` does this and gives every north frame the same lean, so the walk still matches.
6. **Show Preston** the sheet before anything goes into `assets/`. When he approves, install it into
   `assets/sprites/arena/<name>/`, then rebuild with `tools/arena/build_small.py` and
   `tools/arena/build_dungeon_set.py`, then run `tools/art/walk_lock.py <name>` for the walk.
   Then run `python tools/art/pose_fix.py plan <name>`: west walks are flips of east walks, so a west still drawn on
   its own sits a turn off them (45 creatures on 2026-10-31). `apply` flips the still that disagrees.

## What the judge checks

- **files:** all eight views, on one canvas size.
- **alpha:** no partial alpha.
- **ground:** every view on the same foot row.
- **centre:** every view on the middle column.
- **height:** no view more than 10% off the set's median height.
- **palette:** at least 85% of each view's pixels near the south view's colours.
- **specks:** few lone pixels.
- **mirror:** each pair's silhouettes overlap at 0.85 or more when flipped.
- **face:** the north view is not the south view again.
- **turned:** the north view is about as even left to right as the south view, and is not shaped like a diagonal.

The thresholds are in `LIMITS` at the top of the script. On 2026-10-28 it ran over all 50 in-game sets: 22 need
views generated again, and 29 need no new generation. Run `python tools/art/sheet_judge.py --all` for the current
list.

## Before showing Preston anything

`sheet_judge.py` checks one set of views. `python tools/art/sprite_director.py <creature> --look` then reviews the whole
creature: whether the body carries its walk, whether it stands on its shadow, whether the eight views agree in size and
colour, the attack beats, hurt and sleep. Read its worklist and look at the strips in `docs/creatures/sprite-director/look`.
Standards are in `docs/art/pro-sprite-standards-2026-10-31.md`. Every line of its regression list must print `found`.

## Don'ts

- Do not invent creature names, lore or stats. Label new ideas as proposals.
- Do not edit Route 1.
- Do not restore the Cinderpelt evolution link.
- Do not overwrite game sprites without Preston's yes. Originals for walk work live in
  `docs/creatures/walk-lock-2026-10-28/before/`.
- Do not run two Retro Diffusion creature jobs at once.

After finishing, list the palette and count how much of each colour sits on the sprite's edge. A plum colour mostly on the rim is the magenta background bled into edge pixels, and it can also show through gaps between legs. `defringe.py` can repaint 0 pixels and still leave it. Clear it, and report near-black outlines, which the brief rules out. Red creatures hide this; green ones show it (Tallowroot, 2026-10-31).

## Making the next stage of a line

Design it from the measured numbers before drawing. Real evolution lines match the last stage's outline only 0.28 to 0.55 at equal height, and area grows 1.3 to 2.7 times a stage. Run `python tools/art/stage_step.py <last stage folder> <new folder>` and report the line; over 0.55 is the old body made bigger. Game size comes from solid area, so a big tail or fan shrinks the body: Stormwick's closed train gave it 17 percent more scale than the open burst. Change the tail's shape, not only its size. When two takes share a body brief, the bodies still drift, so compare them.
A fan or big tail on a rear diagonal is not the side view's. From behind at an angle it sits on the rump, nearer than the body, so it crosses the back: centre it halfway between the side and back spreads, and shorten the blades toward the edges. If every blade leans one way, Preston reads that side as having more feathers (Stormwick, 2026-10-31). Generators miscount repeated parts, so count them by eye in every view; code can then copy one clean blade to fix the count without a new image.

Feet and tails change from behind too. On the straight back view the feet are never the front's toes pointing at the camera, and nothing from the chest or face sits on the rump. A trunk leg stands on its roots, with one or two short claws or roots toward the camera, in the same bark as the leg; no smooth rounded heel. On the rear diagonals a tail slopes down toward the camera at about the front diagonal's length. Say this in the prompt, and check it by eye: Huskward's sheet passed every number with front feet on its back (Preston, 2026-10-31), and hand-drawn rounded heels were rejected as looking edited (2026-11-01).

