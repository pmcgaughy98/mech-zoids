# What the synthesis offers the MOBA (Claude, 2026-11-03)

Preston: "github scan, we have a lot in the synthesis from this game and hollowtide that will help us see what'd be
useful now that were transitioning to moba. Lets start using forge to create attack moves and effects etc."

Read for this: `docs/reference/github-scan-2026-10-19.md`, `docs/plan/synthesis-tool-roster-2026-10-12.md`,
Hollowtide `docs/forges/forge-hub-2026-09-30.md` and `opal-effect-sheet-prompt-v1.md`, and the live Opal page.

## Deadline first
The Opal app page says Opal leaves Labs on **2026-11-17**: "Active workflows will no longer run after this date."
Custom workflows move to skills in Gemini, and the workflow files stay in Google Drive under My Drive > Opal.
Hollowtide already has portable versions in `docs/forges/gemini-skills/` and graph exports in `docs/forges/opal-export/`
(not opened this pass). So the forges have two weeks of life as Opal apps.

## The forges, for this game
| Forge | Use for the MOBA |
|-|-|
| Effect (MODULES: five pieces; ACTION: eight frames in a 4x2 atlas) | Yes. It draws effect pieces only, never the creature, which fits our method: the body moves its approved pixels in Aseprite, the effect is a separate sprite. Its prompt has Hollowtide wording (essences, "folklore look"); a move brief overrides most of it. |
| Attack / Title Card (six body poses, or one cut-in card) | Pose ideas only. It redraws the body, and the bodies here are approved pixels. The cut-in card could suit an ultimate. |
| World Asset (props, 16x16 tiles) | Maybe for the arena map, if its scale fits the machines. |
| Idle, Walk (32x32 chibi), Character, Creature, Evolution, Back View | No: Hollowtide scales and jobs. |

First job written and ready: Cabrakan's ground pound, `docs/art/moba/rhino_l/take-a/anim/forge/`
(`ground-pound-effect-brief.txt`, `rhino_ref_e_6x.png`, `rhino_ref_s_6x.png`). Not run: the app's inputs did not
load in Chrome on 2026-11-03 (only the notice banner showed, and the tab stopped answering).

## Other effect makers on hand
- **Aseprite by hand** (connected): the rhino ground-pound prototype proved the body half. Effects drawn this way are
  exact but small and slow.
- **PixelLab `vfx_workbench`** (free with his subscription, per its server notes): animated spells, hits, explosions
  and auras, drawn frame by frame; exports to his PixelLab effects. Not tried yet.
- **Gemini MCP** (`gemini-generate-image`, connected here): could run the Effect forge's prompt with the reference
  image, without Opal. Pricing not checked; paid use needs his yes.

## Godot skills for a MOBA (GodotPrompter, installed 2026-10-19)
Already installed and now central: `ability-system` (kits, cooldowns), `particles-vfx`, `animation-system`,
`state-machine`, `ai-navigation` (bots and minions), `camera-system`, `hud-system` (ability bar, health bars),
`input-handling` (click to move, aimed skills). Skipped in October as not fitting a turn RPG, now worth a look if the
MOBA is played online: `multiplayer-basics`, `multiplayer-sync`, `dedicated-server` (still in `D:\dev\GodotPrompter`).

## Decompilations (study only, nothing copied)
- `bn6f` (Mega Man Battle Network 6): real-time hit timing, flash and invulnerability frames. The most useful one now.
- `fireemblem8u`: battle animation timing.
- `pmd-sky`: partner AI, a model for bots.
- `ZoidsLegacyDecomp`: turn battle flow; less useful for a real-time game.

## Unverified
The Gemini skills folder and exports were not opened. Gemini MCP image pricing was not checked. Whether the MOBA is
online or against bots is not decided in anything read.
