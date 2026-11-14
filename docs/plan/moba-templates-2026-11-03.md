# MOBA templates and SMITE repos: what we can use (2026-11-03)

Searched with the GitHub API on 2026-11-03 (Firecrawl had no credits). Stars and licences are what the API reported that day.

## The rule that decides it

- **"No licence" does not mean free.** A repo with no licence is all rights reserved: we may read it, but not copy any of it.
- **GPL and AGPL code is off limits for copying.** If we put it in the game, the whole game has to be released under the same licence.
- **MIT, Apache-2.0 and CC0 are the usable licences.** They allow copying as long as the licence notice is kept.
- **Our own rule is stricter.** Project CLAUDE.md says references are for structure only, so permissive *games* still only teach structure. The way to really use permissive code is as an **addon**: kept whole in `addons/` with its licence file, the way we use Godot itself. It is never pasted into our scripts.

## Usable: addons we could install whole (each needs his yes)

| Need | Addon | Licence | Notes |
|---|---|---|---|
| Bot AI (if we pick bots) | LimboAI | MIT | Behaviour trees and state machines. Skill installed |
| Bot AI, lighter | Beehave | MIT | Behaviour trees only. Skill installed |
| Unit selection and commands (if commander-style) | philipbeaucamp/godot-rts-entity-controller | MIT | 70 stars, pushed 2026-02-16 |
| Camera | Phantom Camera | MIT | Skill installed |
| Online play, much later | heroiclabs/nakama | Apache-2.0 | A server, not an addon. Only if the game goes online |

## Usable for structure only (read, never copy)

| Repo | Licence | What it teaches |
|---|---|---|
| lampe-games/godot-open-rts | MIT, 1139 stars, Godot 4 | Selection, orders, navigation and match flow in a finished Godot 4 game. It is 3D; its assets are Kenney's Space Kit |
| rluders/rts-framework | MIT, 55 stars, Godot 4 | A decoupled manager layout. The README warns it is unfinished |
| godotengine/godot-demo-projects | MIT | Official 2D navigation and avoidance demos |
| spicylobstergames/shotcaller-godot | GitHub reports NOASSERTION | Already studied; see the skeleton synthesis |

## Not usable

- **No licence (read only):** DaughterOfZaun/League-of-Jinx (we took names only), metanoia83/Godot_3D_MOBA_Prototype, ColinGilbert/godot-moba and its server (Udemy course code), Alexnortung/flufwars, testman42/3D-RTS.
- **GPL or AGPL (copying would force the game open):** CosineGaming/nv-moba, ohmree/le-gam, OrriBogdan2/project-boki, ilioscio/mftr, Godostra/godostra.

## SMITE repos

- **Hi-Rez API wrappers (MIT):** luissilva1044894/hirez-api-docs, Pyrez, sergiotapia/smitego, messyfresh/hirez.js and stachu540/HiRezAPI. There is also cep21/smitego (Apache-2.0).
  - The code is free to use, but the data it fetches belongs to Hi-Rez.
  - It needs a developer key.
  - It is only worth it as a private kit reference, which the "ode to" approach already covers by hand.
  - Recommendation: add nothing to the repo.
- **No licence:** JoShMiQueL/Smite-God-Scraper, cc3397/Ra-Smite-God-Kit-UE4.
- **Stay away:** cheat and hack repos, and DeponarFawelum/SMITE-2, which pushes a suspicious download.

## Unverified

- Whether LimboAI, Beehave and Phantom Camera have builds for Godot 4.7.2.
- The licences of godot-open-rts's other assets beyond the Kenney kit.
- Shotcaller's real licence terms, beyond what the earlier synthesis recorded.
