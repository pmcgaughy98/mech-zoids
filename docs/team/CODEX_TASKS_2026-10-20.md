# Codex tasks, 2026-10-20: finish the Codex-reference builds (Claude for Preston)

**Read this first. It replaces `CODEX_TASKS_2026-10-19.md`** (its branch, lock, checks and method still apply: battle
frames first, then the eight views, one machine at a time, with `art/machines/<id>/CODEX_IN_PROGRESS` while you work).
Since then Claude rebuilt four machines from the reference images you made (`docs/art/2d/codex_reference_pack_2026-10-19/
returned/`), so the art under the 10-19 notes changed. Grok Build now makes new images (`GROK_TASKS_2026-10-20.md`);
your part is the hand finish and the two reference sheets still owed.

## What is installed now (raw detail-pixelizer output, nothing hand-finished)

**Updated later on 2026-10-20 after the factory pass:** installed builds are now gorilla v78, wolf v95, kangaroo p74,
shoebill p96, hippo p48, pangolin p46 (each `<ID>_V/P<n>=0` steps back one build; the factory log has what each
changed). The table below is the morning's state.

| Machine | Build | What changed from your sheet | Previous build |
|-|-|-|-|
| ape_l (gorilla) | v77 | v76: five knuckles a fist, grey layered fist and shoulder wheels; v77: ballast blocks in a row along the spine with orange caps, one big grey forward cannon on the right of the back, rear 30 cm longer and lower, hind legs 1.3x thicker with a grey ankle wheel | `APE_V77=0`, `APE_V76=0` |
| wolf_m | v94 | v93: no bolt specks, bare light-grey legs, thick red elbow and knee rings, tail 1.28x, head 12% longer; v94: battle clips stalk (body 6 degrees and head 16 degrees nose down, feet planted) | `WOLF_V94=0`, `WOLF_V93=0` |
| kangaroo_m | p73 | joint faces bigger (thin dark rim), thighs and shins bare of greebles, armour slabs flush, tail root thicker | `KANGAROO_P73=0` |
| shoebill_m | p95 | taller spiky crest; two bold dark slits on the chest plate | `SHOEBILL_P95=0` |
| hippo_m | p46 | unchanged (no sheet yet) | `HIPPO_P46=0` |
| pangolin_m | p44 | unchanged (no sheet yet) | `PANGOLIN_P44=0` |

Before/after sheets: `docs/art/2d/ape_l/v77_before_after.png`, `wolf_m/v93_before_after.png`, `wolf_m/v94_stalk.png`,
`kangaroo_m/p73_before_after.png`, `shoebill_m/p95_before_after.png`. Log: `docs/plan/creature-factory-2026-10-12.md`.

## Task 1: the two reference sheets still owed
Hippo and pangolin, from `codex_reference_pack_2026-10-19/PROMPTS.md` with its blueprint sentence first (a flat side,
front and back, not angled views: the four sheets so far came back as angled pixel views). Save to `returned/` as
`<id>_codex_modelsheet.png` and `<id>_codex_sprite.png`.

## Task 2: hand-finish, one machine at a time
Order: **gorilla, wolf, kangaroo, shoebill**, then pangolin and hippo after their rebuilds. Per machine, what only a
hand can still fix (measured this week):
- **Gorilla v77:** the spine rack and the back cannon are Preston's approved layout (from your own sheet), so do not
  move them back across the back as the 2026-10-15 notes say; give the cannon's muzzle a readable dark bore, and keep
  the ankle wheel's light rings separate from the green leg. punch/3 may overhang the top 2 rows (allowed).
- **Wolf v94:** check that the paws stay planted on the ground line in the stalk (idle, lunge, dash); about 24 single
  light pixels remain per frame: keep the ones on plate edges, merge the rest.
- **Kangaroo p73:** the far shin still reads as a tall dark slab in SE; the tail segments need a lit top edge each so
  they read as overlapping plates, not stripes.
- **Shoebill p95:** the deep-blue band along the upper back in E and SE (likely the outline and seam on top of the
  body: lighten that run to the plate's own darker shade); keep the new crest and chest slits readable at 1x.
- **Pangolin p44 / hippo p46:** as in the 10-19 notes (the gold bar over the pangolin's head; a 1 px gap between the
  hippo's toes).

## Checks after each machine
`Godot --headless --path . --import`, then `view_art_check`, `views_check`, `battle_check`, `battle_fit_check`,
`foundation_check`, `systems_check`, `start_chain_check`, `vfx_check` (all in `tools/debug/`). Report per machine what
you changed and which checks passed.

## Do not
- Change shapes the model gives (silhouette, part positions): those go back to Claude as a source fix.
- Use the kangaroo reference painting's shoulder gun and hip boosters (Preston, 2026-10-15).
- Touch a machine without its `CODEX_IN_PROGRESS` lock, or Grok's staging folder (`docs/art/2d/grok_pack_2026-10-20/`).
