# Start here

A new Godot game, built by synthesis from Zoids Legacy (GBA), one of Preston's favourite games. Prepared
2026-10-11 by the Hollowtide session at Preston's request: "prepare new session that's going to build new
godot project based on that and we'll build it in D drive."

> **Back from the Hollowtide session (2026-10-11):** read `docs/team/HANDOFF_FROM_HOLLOWTIDE_SESSION_2026-10-11.md`
> first. The starters changed (four to pick from), and multi-view machines are wired.

## Required reading (read both in full before the first answer)
1. `CLAUDE.md`: how to work with Preston on this project.
2. `docs/reference/zoids-legacy-structure.md`: what is in the decompilation and where to look.

When Preston says "use synthesis", follow the method in `CLAUDE.md` ("Synthesis: what Preston means").

The first synthesis doc is `docs/reference/battle-structure.md` (read it before battle work). It used only
Zoids Legacy and its sibling games so far; the wider references the method asks for are still to do.

## Decided so far (Preston, 2026-10-11)
He loves the battles, the machines' colours, the many animals and the classes of animals. Machines are
animal-like beasts, close to Zoids in animals and palette (within the line in `CLAUDE.md`). A deck of
commands. No name or story yet; `new-mech-rpg` is a placeholder.

Correction (2026-10-11): an earlier draft of this file said the player "draws a hand of commands each turn."
The source shows Zoids Legacy's deck is built before battle, not drawn. Which way we go is his pick.

## Session 1 status (2026-10-11)
Done: questions answered; battle structure and the Zoids Saga family read (`docs/reference/battle-structure.md`);
the whole start wired with placeholder art: title > opening > hangar > field > first battle > back to the
hangar, with lose-and-retry, story flags, the objective line and the mechanic's debrief. Press play in Godot.
Checks (both pass): `tools/debug/start_chain_check.gd` (run with `--fixed-fps 60`) and `tools/debug/battle_check.gd`.
Art slots for Codex: `docs/team/CODEX_TASKS.md`. Git initialised, nothing committed.

Defaults used, still Preston's to change: Zoids Legacy's deck rule (equip up to 10, each once per battle, one
per round); classes = size x body; the faction palette; 320x180. Every number is a draft.
Session 1, second pass (same day): pause menu (X: Deck editor, Team, Save), Continue on the title, and the canyon
(second field area) with a flying rival. Winning the first battle gives the Air Lock command, which the canyon
needs: the battle check shows 34% wins without it, 80% with it. Third check: `tools/debug/systems_check.gd`
(deck rules, save and load). Next links: the town past the canyon (research lab and battle arena, per the
Legacy opening), and a second machine on the team.

**Build order (Preston, 2026-10-11):** foundation and wiring for the whole start first, placeholder art,
then Codex fills it in. Read `docs/plan/foundation-and-wiring.md` before building past the first slice.

**Multi-view machines (2026-10-11):** eight views per machine and a turning camera, wired and checked, not yet
in the battle. See `docs/plan/multi-view-machines.md`; try `scenes/view_lab.tscn` with F6.

**Starters (Preston, 2026-10-11):** the player picks one of four: gorilla (green, kept), shoebill, pangolin,
pygmy hippo (proposals in `docs/design/starters-2026-10-11.md`). The tiger, raptor and hawk were too mainstream.
The opening still gives the tiger; the four-way choice is the next opening task.

**3D pivot (Preston, 2026-10-11):** machines become 3D models instead of eight drawn views. Read
`docs/plan/3d-pivot-2026-10-11.md`: the installed 3D skills (`vehicle-model` covers mechs), generators, free assets.

Hollowtide continues in its own folder and sessions; nothing here changes it.
