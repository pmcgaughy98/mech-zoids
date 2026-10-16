# Zoids Legacy decompilation: what is in it and where to look

Repo: https://github.com/jmacato/ZoidsLegacyDecomp (MIT). Read online or with Firecrawl; no download needed.
Checked 2026-10-11 from the repo's README and `src/` listing (Claude, Hollowtide session). The code itself has
not been read yet.

**What it is.** A byte-matching decompilation of Zoids Legacy (USA, GBA): 1,130 code regions, mostly C. It
contains no ROM, game data, art or text; the English text files only work against your own ROM. The author
warns the C is rough ("jank", permutator and macro output, some AI-written). Read it for how the game is put
together, not as code to imitate line by line.

**Structure only.** Never copy code, text, names, data or art. Hollowtide's rule for disassemblies applies.

## Where to start (from `src/README.md`)
| Area | Folder / file | What to learn from it |
|---|---|---|
| The whole game's flow | `src/game/run_game_state_machine.c`, `src/game/modes/` | How title, field, battle, menus and scenes hand over to each other |
| Story events | `src/events/run_event_scripts.c`, `events/commands/`, `events/scenes/` | A script runner with commands: how scenes, dialogue and battles are triggered |
| Battle core | `src/battle/battle.h`, `battle_display.h`, `battle_animation.h` | Battle state, what is drawn, how actions animate |
| Battle results | `src/battle/present_queued_battle_effect_results.c` | Effects queued, then shown one by one (the "act, then show results" rhythm) |
| Win/lose and story | `src/battle/check_battle_result_and_play_story_scenes.c` | How a battle's outcome feeds the story |
| Machine growth | `src/zoids/update_pulse_effects_from_emotion_growth.c`, `add_pulse_effect.c` | A machine's bond/emotion grows and changes its effects |
| Customization | `src/ui/run_zoid_customization_menu.c` | Parts and loadout menu |
| Combining machines | `src/events/commands/event_combine_battle_zoids.c` | Two machines joined for a fight |
| Menus and text | `src/ui/window.h`, `player_selection.h`, `name_entry.h` | Window system, selection, name entry |
| Field | `src/field/field_display.h`, `src/graphics/camera.h`, `screen_effects.h` | Overworld drawing, camera, transitions |
| Save | `src/save/` | What a save holds |

Also in the repo root: the translation build rejects text that overflows its window and **Deck Command**
names wider than their menu line, which confirms the battle uses a deck of named commands.

## What Preston has said about it
- One of his favourite games (2026-10-10).
- Ideas flagged for later in Hollowtide's notes: the battle's Deck Command, parts-based customization, and how
  its battle menus and quote windows are laid out.
