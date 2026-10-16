# How to work on this project

A new 2D game in Godot, started 2026-10-11. Preston's favourite game Zoids Legacy (GBA) is the structural
reference, the way Explorers of Sky is for Hollowtide. **Read `START_HERE.md` first**, then
`docs/team/how-preston-works.md` (what Hollowtide's sessions learned from his corrections).

## Who
Preston is the designer and director, not a programmer. Explain what code does in plain language, say why
you chose an approach and what the alternative was. He has ADHD and chronic pain: keep explanations short
and structural, show a working thing rather than describe a plan.

## The hard rule: one completion per session
Every session ends with something he can press play on. Pick one small thing, build it, run it, stop.
No scaffolding the whole game, no systems for features that don't exist yet. If a request needs more than
one session, say so and propose the first slice.

## "Synthesis": what Preston means
When Preston says **"use synthesis"** (or "synthesize", "snythesis"), it means: before building or writing
something, study how **finished, shipped, human-made games** do that same thing, learn the structure, then
build our own version from what works. It is his standing method from Hollowtide, used for everything:
battle systems, menus, scenes, pacing, dialogue voice, sprite scale, music, trailers.

How to do it:
1. Find 2 to 4 finished games (or films and books, for dialogue) that do the thing well. Zoids Legacy is
   the main one here; also look wider (other GBA and DS RPGs, Explorers of Sky, Golden Sun, Advance Wars,
   Medabots, Mega Man Battle Network, modern indie games).
2. Study them: the decompilations and disassemblies Preston links, Firecrawl for wikis, design write-ups
   and developer postmortems, the `watch` skill for gameplay videos and trailers. Prefer primary sources.
3. Take the **structure**: order, timing, layout, flow, how many of something, what the player sees when.
4. Build our own version that combines what works. Say in a line or two which games informed it and how.
5. Write what you learned, with sources, in `docs/reference/` so it isn't researched twice.

**Synthesis means using everything on hand (Preston, 2026-10-11).** The model for it is the gorilla finish
pass, where he said "make sure you are using all the things we've added today and have at our disposal. Mcps,
connectors, all that" and then: "This is now what I mean when I refer to synthesis." So a synthesis pass:
- **Inventory first:** list what is on hand right now (MCPs such as the live Blender link, connectors such as
  Firecrawl, installed skills and their guides, reference files he sent, the project's own checks), and say in
  one line what each will be used for. Paid tools are named with their cost and only run on his yes.
- **The skill-ups to include in that stock-take (2026-10-11):** they are in `.claude/skills/`, with sources and
  licences in `.claude/skills/SOURCES.md`.
  - **Godot-ready pipeline:** `blender-game-asset-artist`, `game-3d-asset-design`, `blender-export-pipeline`.
  - **Modelling, texturing, rigging, animation and budgets:** the `atlas-*` skills.
  - **bpy recipes:** the `dom-blender-*` skills.
  - **Gotchas:** `claude-3d-harness`, whose modelling guide and lessons file are in its `library/` folder.
  Read the ones that fit before building, and name them in the report.
- **Measure the references, don't eyeball them:** for example triangle counts, texture sizes, colour saturation
  and light-to-dark spread across the 13 Zoids models, turned into numeric targets.
- **Build, look, score, repeat:** change the thing, look at it live from several angles, score it against
  the targets, then check it in the real game view.
- **Report:** what each tool contributed, what was deliberately not used and why, and what still falls short.
- **The roster to start from (2026-10-12):** `docs/plan/synthesis-tool-roster-2026-10-12.md`, which sorts the
  live connector list into used, worth a real use, noise and failed. Re-check it when connectors change.

What synthesis never means: copying code, data, text, names, art, music, colours or level layouts into the
game, or treating AI-made work as the reference. Reference models or files he provides are studied and measured
in the session scratchpad only, never copied into the project. When he says the result feels off ("caveman
dialogue", "looks AI"), go back to the references, not to guesses.

## The reference: structure only
`jmacato/ZoidsLegacyDecomp` (GitHub, MIT, code only; no ROM, art, data or text in it). Read it to learn how
a finished game is organised: its state machine, battle flow, menus, events. **Never copy its code, data,
text, names or art**, never use a Zoids ROM, never use Zoids or Takara Tomy names, designs or lore. What we
build is our own game. Notes on what is in the repo: `docs/reference/zoids-legacy-structure.md`.

## Synthesis: the doc it produces, and the connectors
Format, from Hollowtide's Explorers of Sky doc (`C:\Users\pmcga\dev\hollowtide\docs\research\pmd-sky-references-2026-10-09.md`):
what was read (marked read versus general knowledge), then a **synthesis proposal** labelled "nothing here is
canon" with alternatives named, then **one first slice** with a headless check. He picks; "do the slice"
means build it. Connectors for the research step: Retro Game Gather (Japanese releases, sibling games) and
Director's Lookbook (palette and look cards; `show_card` gives hex swatches).

**The look:** he wants machines close to Zoids in animals and palette (2026-10-11). Animal war machines and
faction colour schemes are a genre and fine; a specific Zoid's silhouette or plating is not.

## Technical
- Godot 4.7.2, GDScript, 2D pixel art: `C:/Users/pmcga/Games/Tools/Godot_v4.7.2/Godot_v4.7.2-stable_win64.exe`
- Checks run headless: `--headless --path . --script res://tools/debug/<name>.gd`. Measure the thing
  itself; a test that passes can still test nothing.
- One Godot process at a time. Keep the structure simple; Godot conventions over clever abstractions.
- When something breaks, explain what broke and why before fixing it.
- This folder is separate from Hollowtide (`C:\Users\pmcga\dev\hollowtide`). Don't edit Hollowtide from here.

## Authorship and money
- Names, lore, designs and stat values are Preston's. Claude **drafts real proposals** for him to edit:
  actual lines of dialogue, names and numbers, labelled as proposals. Not bracketed placeholder text;
  he can't react to "[Opening placeholder]". (Preston, 2026-10-11.)
- Paid tools (Retro Diffusion, Higgsfield, ElevenLabs, PixelLab): estimate cost first, one job at a time.
- Commit only when Preston asks. No em-dashes, no emoji, no hype in anything written for him.

## Handoff from the Hollowtide session (2026-10-12)
Read `docs/team/CLAUDE_MECH_SKILLUP_HANDOFF_2026-10-12.md` first: the synthesis method, the build toolkit, the
measured targets, the lessons and pitfalls, and the open work, all learned in passes 4 to 24.
