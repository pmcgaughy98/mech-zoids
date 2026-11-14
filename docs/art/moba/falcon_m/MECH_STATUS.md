# Falcon (`falcon_m`): status, 2026-11-05

Falcon session, first turn: stock-take only. Nothing was built or spent. Facts below were read from the main
checkout (`D:\dev\new-mech-rpg`).

## What exists
- **Approved take: take-b.** `take-b/APPROVED.txt`, Preston 2026-11-03: "perfect". Wings folded on both sides in
  every view; take-a's raised V wings were dropped.
- **Stills (old low camera):** `take-b/views/`, eight files (s, se, e, ne, n drawn; sw, w, nw mirrored).
  - Sizes: s 50x72, se 60x71, e 71x69, ne 57x71, n 48x71.
  - Ink shares by view: s 5.8%, se 4.2%, e 4.5%, ne 4.2% (capped from 2.7%, +32 px), n 3.3%.
  - The ne capped-ink change was kept by Preston on 2026-11-04 ("Keep all five"). His originals are in
    `take-b/views_pre_ink/`.
  - Known flaws he chose to leave: the side views are 69 px tall against 72 for the front, and the back view's feet
    show forward claws where heels should be.
- **Size class:** M, 72 px tall, in a 160x160 cell with the foot row at 140. At 50 texels per metre: 72 / 50 = 1.44 m.
  Source: `docs/art/moba/STILLS_STOCKTAKE_2026-11-04.md`.
- **35-degree stills:** none. The other mechs that have them use `cam35/` and `views_cam35/` folders; the falcon has neither.
- **Animations drawn:** none. The kit lists wing dart fire, take off and land, stoop dive, and the barrage effect.
- **Basic attack (2026-11-05): built, not yet in the match.** `scripts/moba3d/falcon_kit.gd`.
  - A feather dart from the wings: 7 m range, 0.9 s cooldown.
  - Keen eye passive: 26 damage point blank, 39 at full range.
  - Check: `tools/debug/falcon_basic_check.gd`, 17 of 17 pass.
  - The game feel lane has been asked to add the falcon to the match.
  - The wing-fire frames are queued with the attack lane, blocked on the 35-degree stills. One set per drawn view,
    mirrored.
  - Sound: final, in `audio/sfx/falcon/`. Preston picked set B on 2026-11-06: dart_fire "Air cut", dart_hit
    "Spike", dart_keen "Ring out", dart_miss "Wall tick". check_kit_audio passes.
  - The kit has `class_name FalconKit` (2026-11-06), so KitAudio finds them.
- **In the game:** no. There is no `art/machines/falcon_m/` folder and no frames file.
  - The only code that names it is the camera lane's `scripts/moba3d/ult_view_test.gd`. That file tests the sky
    barrage camera at 55, 70 and 85 degrees, with plain bright boxes as placeholder darts and no falcon drawn.

## What the kit doc leaves open
`docs/plan/moba-kits.md`, Falcon section.
- **Numbers:** cooldowns are only "short, medium, long". There is no damage, range or duration anywhere.
- **Keen eye:** how fast the bonus grows with distance, and how big it gets at max range.
- **Piercing dart:** how many enemies it passes through, and whether damage drops after each one.
- **Take off:** how long it stays up, whether it can be hit or targeted while up, and the volley's area and damage.
- **Stoop:** how far it dives, how much it slows, and for how long.
- **Sky barrage:** radius, duration, number of darts, and whether the falcon can be hit while it circles.
  - Decided: the camera rises to 55 to 60 degrees and uses the 35-degree drawings ("55 to 60, no new art").
- **Art:** what each effect looks like. Nothing is drawn for any of the four moves.

## Next slices (Preston picks)

**1. 35-degree redraw of the five stills. Paid (Codex).**
- What it does: gives the falcon the drawings the game camera now needs. Nothing else can go into the game at the
  new angle without these.
- Cost: the kangaroo's run was one Codex image at 78,028 tokens. Worst case, allowing for the cap overshoot: about
  155k tokens.
- Risk: the kangaroo's first try missed (it showed the face in the rear view), so a second try may be needed. That
  doubles the worst case to about 310k.
- Can fix in the same brief: the 69 vs 72 height gap and the back-view heels.
- Who: the fleet redraw lane ran the hippo and kangaroo. The hub should say whether the falcon is in that queue or
  should run here. Only one paid job can run at a time.

**2. Sky barrage effect, drawn. Free. Pass 1 done 2026-11-05; waits on Preston's look.**
- Board, GIFs and pieces: `vfx/sky_barrage/`. References and proposal:
  `docs/reference/area-barrage-references-2026-11-05.md`. Firecrawl spent 10 credits; nothing else was paid.
- What it does: a synthesis pass on rain-of-darts ultimates in finished games. Measure what they show: the warning
  ring, dart count per second, the impact puff, and how long each lasts.
- Then draw our own feather dart, impact puff and ground ring with the free pixel tools (the PixelLab workbench and
  VFX workbench, Aseprite if it reconnects).
- Shown on a board at game size, beside the camera lane's test frames.
- It replaces the placeholder boxes only through the camera lane, never by editing its file.
- Doesn't need slice 1.

**3. Kit numbers, drafted. Free.**
- What it does: real proposed values for every open item above (cooldowns in seconds, ranges in metres, damage,
  slow, durations), each labelled as a proposal.
- Checked against the ranged carries in finished MOBAs, so you react to real numbers instead of blanks.
- Written here first. They go into the kit doc only on your yes.

Recommended order: 2 or 3 now while the paid queue is busy, then 1 when the hub says the queue is free.

## Where the files live
Written first in the falcon session's worktree because of a file guard. Copied into the main checkout on
2026-11-05 through the shell, after Preston okayed that route for every mech session ("Yes, all of them", via
the hub). The main checkout is the working copy from here on.
