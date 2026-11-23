# How to work on this project

## Engine migration approved, Preston, 2026-11-15

Preston decided to move the MOBA to Unreal: "Yep were doing it."
The destination is `D:/dev/mech-moba-unreal/MechMoba.uproject`; read that project's
`AGENTS.md` and `Migration/DECISION.md`. This Godot project is retained as the
playable behavior reference. Continue portable Blender/art work in preserved
workbenches; new engine gameplay, map and HUD work targets Unreal. Do not delete
or mass-rewrite this reference. Hollowtide remains separate and unchanged.
Older instructions describing Godot as the destination are historical.

## Current shared model workspace (Preston, 2026-11-07)

For downloaded MeshForge models, read `docs/art/moba/MODEL_WORKBENCH.md`.
`art/model_catalog/catalog.json` locks each download to its four exact generation sheets.
Editable Blender workspaces with those sheets visible are in `art/model_catalog/workspaces/`.
Use these full-detail sources for geometry corrections such as extra limbs and incorrect eyes or sockets.
The in-game Mech Workshop uses reduced viewing copies; it is not the geometry editing environment.
Preserve the source archive and other lanes' refinements. Workspace setup does not mean the meshes are repaired.

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
- **Sprite tools in the stock-take (Preston, 2026-11-04):**
  - **Free:** the Aseprite MCP (local; palettes, outlines, frame edits, Lua).
  - **Free daily generations, then paid:** the PixelLab MCP (pose-guided animation, normal maps, and
    `pixelart_workbench`, which is free).
  - **Paid:** the Retro Diffusion MCP (animation styles, `fix_pixel_art`, palette tools; per run) and
    SpriteCook (credits).
  - **Codex:** sel-out and finish passes. It never sees old or other art.
  - Name each tool with its cost. List: `docs/plan/moba-perspective-remaster-synthesis-2026-11-04.md`.
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

## MOBA roster: what "ode to" a SMITE god means (Preston, 2026-11-03)
Each machine honours a SMITE god. The roster, with each one's ode type, is in `docs/art/moba/ROSTER.md`.
- **"Ode to X" always means the god's KIT**: abilities and role. Never the god's look, model or design.
- **The kit is inspiration, not a copy** (Preston, 2026-11-03): take only what makes sense for the animal and
  drop the rest; the machine need not play like the god or share his role. Lobster/Khepri keeps the pull, not
  the revive. Rhino/Cabrakan keeps the tremble slow, stun and heavy burst, not the hand-shield walls or the long
  rhythmic tremble. Chameleon/Loki goes invisible but need not be an assassin. Kits: `docs/plan/moba-kits.md`.
  The body is a plain mech animal with no god theme: no god colours, regalia or symbols.
  ("its mainly for kit, not really design. Its a mech moba game." / "it should be ode to his kit not model
  or design.")
- **The one exception is a visual he names himself**, which goes in as he said it
  (Geb: "a hexagonal tech shield thats green for sure"). Nothing else from the god.
- **Always:** nothing held, no melee weapons in hand, and every machine reads as a robot first.
  No crest, headdress or banded "hair" shapes (he cut one from the shoebill).
- **No god theme is not the same as plain.** Every machine is bold and lively like the gorilla, wolf and
  kangaroo: one saturated colour on big parts, a glowing accent, and a silhouette with energy (swept fins,
  a leaning guard). A grey-on-grey shoebill was "to plain".
- Lesson: I misread "redo shoebill ode to thoth because it was ode to his design not kit" as a request for
  Thoth's look. It meant the shoebill *had been* built on his design and should be redone on his kit only.
  When a line could mean either, ask before launching a Codex take.

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

## Animations
Arena fleet onboarding now uses `docs/art/moba/ARENA_MODEL_PIPELINE.md` (2026-11-10). It documents the 25 base bodies, current gorilla/rhino copies, F8 test selector, builder/registration command and explicit base-versus-authored limits. Read it before replacing arena model hookups; completed local trials now run in Arena Play.

Before making or fixing any machine animation, read `docs/art/moba/ANIMATION_PLAYBOOK.md` (what worked and failed on the rhino walk, the checks, the finishing order). Add new lessons to it.
