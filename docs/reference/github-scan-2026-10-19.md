# GitHub scan for the synthesis (Claude, 2026-10-19)

Preston: "Github connections is huge in terms of skill-up and upgrading the synthesis. Do a scan for that and how to
skill up yourself to create professional products ... competitive with Mystery Dungeon, Zoids Legacy, and all the other
games ... Also ... all the games we got repositories for like their disassemblies."

Method: Firecrawl developer search (three queries), then each candidate checked live through the GitHub repo record
(stars, licence, last push) on 2026-10-19. Marked **verified** where the record was read; **unverified** otherwise.
Rule that still applies to everything here: study structure and technique only; never copy code, data, text, names
or art into the game (CLAUDE.md, "The reference: structure only").

## 1. What is already on hand

| Source | Where | Used for so far |
|-|-|-|
| `ZoidsLegacyDecomp` (jmacato, MIT, code only) | `D:\Program Files (x86)\Game assets\zoids-source\` | battle flow, menus, regions: `zoids-legacy-structure.md`, `battle-structure.md` |
| `Zoids` (a Zig game project) | same folder | game loop |
| `pmd-red` (PikalaxALT), SkyTemple `skytemple-dtef` | cited 4 and 3 times in Hollowtide's research docs | Hollowtide's dungeon and tile work |
| Global skills already installed (`~/.claude/skills`) | godogen-visual-proof-game-generation, agent-playtesting, playtesting-a-feature, debugging-game-feel, game-feel, pixel-art, sprite-sheet, psx-retro-rendering, scene-*, verifying-scenes, vfx-* (8), create-asset-sheet, fabricating-assets, asset-strategy | partly used (vfx-* informed the battle VFX pass) |

The project's own docs also cite the repos its installed Blender skills came from (`.claude/skills/SOURCES.md`):
MonumentalSystems/Atlas-Agent-Teams (the atlas-* skills), MAX-786/claude-3d-harness, arjun988/blender-skills,
jeremylongworth-source/AgentSkills, badowhp/skill-mania, Andrew1326/dominations, SpriteCook/claude-plugin, and
gdquest-demos/godot-4-3d-third-person-controller.

Only two game repos are actually cloned on this PC. The rest of "the games we got repositories for" lived in
Hollowtide's docs as links.

## 2. Structure references: decompilations and disassemblies (verified)

| Repo | Game | Stars | Licence | Last push | What it is good for here |
|-|-|-|-|-|-|
| `pret/pmd-sky` | PMD: Explorers of Sky (DS) | 144 | none (study only) | 2026-10-14 | dungeon turn order, menus, partner AI, mission board flow |
| `UsernameFodder/pmdsky-debug` | PMD Sky symbols | 55 | GPL-3.0 | 2026-10-10 | a named map of the game's functions and data: the fastest way to find a system in pmd-sky |
| `FireEmblemUniverse/fireemblem8u` | Fire Emblem: Sacred Stones (GBA) | 228 | none | 2026-10-12 | the best-documented GBA RPG decomp (has a docs site): battle forecast, battle animation timing, map/menu state machines |
| `dism-exe/bn6f` | Mega Man Battle Network 6 (GBA) | 44 | none | 2026-08-10 | real-time chip battle timing, custom screen, hit and flash timing |
| `Coaltergeist/goldensun-decomp` | Golden Sun (GBA) | 30 | none | 2026-10-14 | turn battle presentation (the camera swing, summon timing), psynergy field puzzles; young (May 2026), 60 open issues |

Lists to mine for more (verified to exist, contents excerpted only): `samidyfr/game-decompilations` (names Advance
Wars 2, Golden Sun, Legend of Mana, Mother 1+2, PMD Sky), `charlottecross1998/awesome-game-decompilations`,
`btelwy/awesome-romhacking`.

Not found in this scan: a Medabots decomp, a Zoids Saga decomp. An Advance Wars 2 decomp is listed on the samidyfr
list but its repo was not checked (**unverified**).

Licences: "none" means all rights reserved. Reading to learn structure is how we already use ZoidsLegacyDecomp; nothing
from these goes into the project.

## 3. Skill packs for Claude (verified)

| Repo | Stars | Licence | What it adds | Overlap with what we have |
|-|-|-|-|-|
| `jame581/GodotPrompter` | 851 | MIT | 56 Godot 4.3+ skills (state machines, UI, shaders, audio, animation, addons like Dialogue Manager, Phantom Camera, Beehave), 4.7 notes, a 16 KB budget per skill | low: we have no Godot-architecture skill pack; the strongest single install candidate |
| `htdt/godogen` | 7,162 | MIT | game-from-description pipeline with a visual QA loop (capture, compare to a visual target, fix, repeat) | high: `godogen-visual-proof-game-generation` is already installed; its visual-QA loop is the part worth adopting into our checks |
| `gamedev-skills/awesome-gamedev-agent-skills` | 1,637 | Apache-2.0 | 74 skills with a router by engine and task; "art direction, not one-off generations" asset workflow | high: create-asset-sheet, use-widget-asset and similar names already installed look like this pack |
| `thedivergentai/Game-Dev-Agentic-Skills` | 869 | LGPL-3.0 | 99 Godot 4.7 skills, 27 genre blueprints | medium; LGPL matters only if its code is copied into the game, the skills as instructions are fine |

## 4. Art pipeline references (verified)

| Repo / source | Licence | Why |
|-|-|-|
| `Broxxar/PixelArtPipeline` (360 stars, Unity, 2022) | Unlicense | the Dead Cells method: 3D models rendered as toon-lit low-res sprites. Our factory already works this way (Blender toon render, then our pixelizer); useful as a check on its normal-based lighting and outline tricks |
| David Holland, "3D Pixel Art Rendering" (davidhol.land, article) | n/a | outline and pixel-snapping problems at low resolution; matches what we hit |
| Game Developer, "Art Design Deep Dive: ... Dead Cells" (article) | n/a | the original write-up of that pipeline |

## 5. What actually closes the gap to "you can't tell it's AI"

From this week's measured work, not from the scan:
- **Repos and skills help structure and process, not the look.** The 2026-10-16 pixelizer shape rules and rounder
  gorilla joints moved the sprite by almost nothing (joints are 4 to 6 px; `sprite-detail-2026-10-16.md`).
- **What shows at sprite size is silhouette, big masses and value grouping.** Every visible win this week was one of
  those: the cloud pass's wolf saddles and hippo pillars, today's hippo height, wolf head value, far-limb tones
  (wolf claws, shoebill thigh).
- **Hand-placed pixels.** Legacy's finish is hand work; Codex's finish passes are our version of it, and the open
  Codex pass on the new art is still the biggest single lever on "looks AI".
- **The decomps answer feel questions:** how long a hit freezes, when the HP bar drains, how a menu opens. Those are
  what make a game read as made by people, and they are exact numbers in these repos.

## 6. Proposed next steps (pick; nothing installed or downloaded yet)

1. **Install GodotPrompter** (free, MIT). A persistent change to the Claude setup, so on Preston's yes.
2. **Clone three structure repos** next to ZoidsLegacyDecomp: `pret/pmd-sky` (about 320 MB),
   `FireEmblemUniverse/fireemblem8u` (about 50 MB), `dism-exe/bn6f` (about 75 MB). Downloads, so on his yes.
3. **Use them one feature at a time**, when that feature is next: battle hit timing from bn6f and fireemblem8u;
   dungeon and mission flow from pmd-sky; Golden Sun for battle camera and summon presentation.

## 7. Done (2026-10-19, Preston: "yes")
- **Cloned (depth 1, study only):** `D:\Program Files (x86)\Game assets\game-source\` holds `pmd-sky` (338 MB),
  `fireemblem8u` (70 MB) and `bn6f` (66 MB), next to `zoids-source\`. Nothing from them is built or run.
- **GodotPrompter:** cloned to `D:\dev\GodotPrompter`; 46 of its 57 skills copied into `~/.claude/skills` (plain
  SKILL.md text, MIT; licence copied as `state-machine/GODOTPROMPTER_LICENSE`). Not installed as a plugin: the
  `claude` command line is not on this PC, and the plugin's SessionStart hook would add text to every session.
  Skipped: `gdscript-patterns` (a skill of that name was already installed), and nine that do not fit this game
  (xr-development, mobile-development, dedicated-server, multiplayer-basics, multiplayer-sync, csharp-godot,
  csharp-signals, popochiu, gdextension). They load in a new session.
