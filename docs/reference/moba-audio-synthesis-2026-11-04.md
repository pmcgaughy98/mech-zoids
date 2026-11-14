# MOBA audio synthesis (sound lane, 2026-11-04)

Preston: "The synthesis repos etc. should help especially the moba ones though. Maybe remake them after that."
So before remaking the sounds, this pass studies how shipped games handle the same jobs. Structure only: no audio,
code or text from any of them goes into the game.

## What was read
| Source | Read? | What it gave |
|---|---|---|
| SMITE 2 Developer Deep Dive, Audio (Hi-Rez, YouTube `5LAS6vnyZk0`, 4 min) | Transcript read in full | SMITE 1 capped sounds at 32 voices. Walking a lane solo already used 24, and minion fights hit the cap, so gameplay sounds cut out; SMITE 2 raised it to 128. A smaller attenuation radius tells you more exactly where a sound comes from. Occlusion: behind a wall, a sound gets quieter and low-passed. Three ability pillars: responsive (a sound the instant you press), informative and visceral (the sound tells you what hurts you), keep the iconic sounds that already work. |
| Doom (id Software, GPL), `linuxdoom-1.10/s_sound.c` and `sounds.h` in `Game assets/game-source/doom` | Constants and the sound table read | Every sound has a priority and a "singularity" flag (one instance at a time). When channels run out, the lowest priority loses. Full volume inside a close distance (160 units), fading to silence at a clipping distance (1200). Repeated sounds get a random pitch nudge (most ±16 of 255, saws ±8) so they don't machine-gun. |
| Riot dev blog "Unleashing the Elements" (2019) | Search excerpt only | The reworked Rift "was still so... quiet", so each elemental variant got its own ambience (shifting rock, whispering wind, crackling flame). The ambience follows map state. |
| `shotcaller-godot` (MIT Godot MOBA) in `Game assets/game-source` | Checked | No sound system to learn from (one soundtrack file). |
| League Frequencies (Riot video series), Dota 2 sound design videos | Found, not read | Next reads if the remake needs more. |

## Where our sound stands, measured against that
- **Voice cap:** `MapAudio` caps one-shots at 8 and drops any new sound once 8 are playing, whatever it is. A
  minion fight can silence a tower going down: SMITE 1's exact problem, at a quarter of its cap.
- **No priority, singularity or occlusion.** Events are full within 12 m and silent past 70 m. The beds are full
  within 14 m and silent past 45 m.
- **Ability sounds:** only the rhino's ground pound has cast and landing sounds. The gorilla and fennec abilities
  have voice callouts but no sound of the ability itself, so they fail SMITE's first pillar (a sound on the press).
- **Theme:** the five beds now fit the foundry, but the 12 map events were made before Preston picked it.

## Proposal (nothing here is canon)
1. **Sound priority (Doom and SMITE 2).** A pool of 32 one-shots shared by map events and kits. Each sound gets a
   priority: core down, tower down, and the win and lose stingers top; tower shot and hit high; camp aggro,
   recall and respawn middle; minion hits low. When the pool is full, the oldest lowest-priority sound is cut,
   never a higher one. Minion hits are one at a time per minion, with a random pitch nudge.
   *Alternative:* just raise the cap to 32. Simpler, but it still drops whatever comes last.
2. **Foundry remake of the 12 map events.** Towers become industrial turrets (heavy bolt, steam vent after the
   shot), tower down a steel frame collapsing with a long hiss, the wave spawn a shift horn and gate clank,
   minion hits small metal impacts, respawn and recall a hydraulic lift and power-up. Synthesised, free.
   *Alternative:* ElevenLabs sound effects, priced first and sent through the hub.
3. **Cast sounds for the gorilla and fennec (8 sounds).**
   - Fennec: sand kick (servo and a sand hiss), ear burst (a sonic pulse), tunnel (digging, then a pop-out),
     sonic boom (a charge whine, then the blast).
   - Gorilla: hex shield (an energy hum up), chest beat (metal drum hits), bound (a servo leap and landing),
     hex dome (a dome forming).
   - Same pattern as the rhino: a sound on `used`, and a landing sound on the hit frame where there is one.
     Synthesised first, free. *Alternative:* ElevenLabs sound effects, priced.
4. **Occlusion (SMITE 2).** A raycast from the camera to the emitter against the arena walls. Behind a wall the
   sound drops about 6 dB and is low-passed near 1.5 kHz (`attenuation_filter_cutoff_hz` on the 3D player).
   Tune it in the live game.
5. **Tighter event radius,** set by ear from the real camera height once there is a playable match.

## First slice
**1, sound priority:** free, with a headless check.
- Fill the pool with 40 minion hits, fire `tower_destroyed`, and `tower_down` must play.
- One minion's hits never stack.
- `core_down` is never cut.

After that, 2 and 3 are the remake Preston asked about. 4 and 5 need his ears in a running match.

<details><summary>Ledger</summary>

- **Firecrawl search:** 2 queries. They found the SMITE 2 audio deep dive, the League Frequencies series and the Riot blog.
- **watch skill:** SMITE 2 transcript (captions, no frames).
- **Local game-source clones:** Doom's sound engine read; shotcaller-godot checked and empty of sound.
- **Not used:** ElevenLabs (nothing to generate yet), Gemini (not needed for a 4-minute transcript), and subagents (cost rules).
</details>
