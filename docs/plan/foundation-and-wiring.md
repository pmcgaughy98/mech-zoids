# Foundation and wiring first

Preston, 2026-10-11: "I want it to build the foundation and wiring like you started doing with dungeons, town
etc. For everything for the start. Then we'll fill it in with Codex."

So Claude builds **the whole start of the game as a working chain with placeholder art**, every handoff real
and tested, and Codex later fills in art, layout and finish. This is how Hollowtide's pilot was made: the chain
ran flood talk, first dungeon, town, theft, guild, second dungeon, boss, shrine, evolution, all wired and
checked before most of the art was final.

## What "the start" is
Synthesize the order from Zoids Legacy (`src/game/run_game_state_machine.c`, `src/game/modes/`, the event
scripts) and propose it to Preston before building. A starting guess, not decided:
title, new game, opening scene, home base, first field area, first battle with the deck, its result feeding the
story, back to base, the next goal. Each link is a scene that loads, plays and hands on to the next.

## Shared pieces to build once, early
Hollowtide has a working version of each. Read them for structure, then write ours fresh for this game.

| Piece | What it does | Hollowtide example (`C:\Users\pmcga\dev\hollowtide\`) |
|---|---|---|
| Run record | Team, deck, story flags and progress carried between scenes | `scripts/town/team_state.gd` |
| Story flags and gates | What has happened; what is open next and why not yet | `story_gate()` in `scripts/town/hub_town.gd` |
| Objective | One line on screen saying what to do next and where, plus a menu page | `scripts/town/objective.gd` |
| Scene kit | Walk, face, emote, say and camera pans for cutscenes | `scripts/town/scene_kit.gd` |
| Dialogue | Lines in files, choices, portraits (Godot Dialogue Manager, MIT) | `dialogue/*.dialogue`, `scripts/creature_prologue.gd` |
| Chain check | Plays the whole start on autopilot and reports each handoff | `tools/debug/pilot_chain_check.gd` |

Lessons from Hollowtide worth keeping:
- Set the project's main scene to the title, and keep it there.
- A replayable area needs a way back in after the story moves on.
- Tell the player where to go (the objective line) from the first minute; a playtest got stuck without it.
- The chain check must walk the real scene changes, not call functions around them.

## How it fits the one-completion rule
Each session still ends with something that runs: one or two links added, and the chain check passing from the
title to the newest link. Placeholders are fine (coloured shapes, plain text, a grey box with the slot's name);
unwired stubs are not.

## For Codex later
Every placeholder loads from a named slot (a file path, with its pixel size), so Codex can drop art in without
touching code. Keep a running list in `docs/team/CODEX_TASKS.md`: slot, size, what goes there, which scene
shows it.
