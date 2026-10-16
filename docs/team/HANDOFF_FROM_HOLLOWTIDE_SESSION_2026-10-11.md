# Handoff: what the Hollowtide session did in this project (2026-10-11)

Preston worked on this game from the Hollowtide Claude session for part of 2026-10-11 and is now back in this
project's own session. Everything below is uncommitted, new files mostly; nothing in battle, field, opening or
run code was changed except where listed.

## Required reading (short)
1. `docs/design/starters-2026-10-11.md`: **the starters changed.** Read before any battle, opening or roster work.
2. `docs/team/how-preston-works.md`: what Hollowtide's sessions learned from Preston's corrections.

## Decisions Preston made in that session
- The **tiger, raptor and hawk are too mainstream**. The player will **pick one of four starters**.
- **Green gorilla stays.** No missiles (the Zoids gorilla has shoulder and back missiles); heavy, close-in weapons.
- **A bird stays, but not an eagle or anything from Zoids, and not red.** Proposal: shoebill.
- Use synthesis with the connectors (Retro Game Gather, Director's Lookbook, Firecrawl). Done for the starters.
- Codex (a new Codex session for this game) will **redraw everything in eight views** from Claude's designs.
- **Claude drafts real lines and names as proposals**, not bracketed placeholders (now in `CLAUDE.md`).
- He wants the foundation and wiring for the whole start first, Codex fills art later
  (`docs/plan/foundation-and-wiring.md`).

## Built (all checks pass: views, battle, systems, start chain)
- **Multi-view machines** (`docs/plan/multi-view-machines.md`): eight views per machine, chosen by facing minus
  camera yaw; mirror fallback; 3D block placeholders at the exact angles (also Codex's guides). Files:
  `scripts/machines/machine_views.gd`, `scripts/machines/view_sprite.gd`, `scenes/view_lab.tscn` (F6: Q/E turn,
  O orbit, L labels), `tools/debug/views_check.gd` (windowed it writes `docs/team/view-guides/`),
  `tools/debug/view_lab_record.gd`. Markings are "decal" boxes drawn on their body, only on its outer surfaces.
  **Not yet in the battle:** swap `Slot.machine(...)` for a `ViewSprite` and give the scene a camera yaw.
- **Machine data** (`scripts/data/machines.gd`): every machine has its own `colours` and a `mount` per weapon
  (where it sits, how it fires). The old three were renamed (Tiger type, Snap Jaw, Tail Pod...) with stats
  unchanged, so `battle_check` still passes. **New:** `ape_l` (gorilla), `shoebill_m`, `pangolin_m`, `hippo_m`,
  flagged `"starter": true`, draft stats, untested in battle. `scripts/ui/slot.gd` uses a machine's own colours.
- **Codex:** `docs/team/CODEX_START_HERE.md` (task 1: the four starters in eight views, retire the old lion and
  raptor art). `docs/team/CODEX_TASKS.md` points to it.

## Open, for this session to pick up
- **The opening still gives the Tiger type** (`run.gd` team `["lion_m"]`). Build the four-way starter choice
  (show each starter's one move on the choice screen) and wire the pick into the run.
- **Rivals:** the raptor and hawk need redesigns by the same method (still in the story chain as `raptor_s`,
  `hawk_s`).
- Run `battle_check` per new starter; the stats are guesses.
- Put the view sprites into the battle once Codex's views land.
- Preston still to pick: names; whether to keep the shoebill or try the hornbill or kingfisher alternatives;
  the defender (pangolin or armadillo); the swimmer (pygmy hippo, giant otter or giant salamander).
