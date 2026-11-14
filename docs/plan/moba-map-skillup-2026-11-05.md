# Map skill-up from other MOBAs (map design lane, 2026-11-05)

Status (2026-11-06): choices 4 and 5 are built and committed: the side pits (a0bc7e5) and the plaza beacon
(fbcd915), both written up below. Choices 2, 3 and 6 are "no change" recommendations still waiting on Preston's
pick. Every pick is Preston's. The map this is for is
the 3 v 3 side mode: one lane, 84 x 156 m, one tower and one core per team, 2 camps and 1 side pit per team, a
26 m plaza in the middle, waves every 30 s (`moba-arena-layout-2026-11-04.md`). The 5 v 5 main-mode map is not
started.

The earlier map work sized everything from the kits (`moba-kits.md`) and the chase camera. This pass adds what
the three closest shipped maps do: all three are 3 v 3, and two of them have one lane.

## 1. The three closest maps

**SMITE, Joust** (source: smite.fandom.com/wiki/Joust, a SMITE 1 page)
- 3 per team. One short lane, guarded by one tower and one phoenix, then the Titan.
- Jungle camps sit on both sides of the lane:
  - 2 XP camps (respawn 2 min);
  - 2 speed buff camps, the ones nearest the phoenix;
  - 2 mana buff camps;
  - 1 void buff camp, across the map from the boss;
  - 1 damage buff camp near the centre, which first spawns at 2:00.
  - The others spawn at 0:10, and the buff camps respawn every 3 min.
- Boss: the **Demon King**, on one side of the map. It spawns at 4:00 and respawns every 5 min.
  - The team that kills it gets a short buff.
  - While the buff lasts, the enemy's first standing tower or phoenix is switched off.
  - The wiki says no other SMITE map has this.
- No wiki number for the buff's length.

**Vainglory, Halcyon Fold** (source: vainglory.fandom.com/wiki/Halcyon_Fold)
- 3 per team. One lane with five turrets per team, and a jungle beside it.
- **Two minion mines**, one each side, both neutral at the start.
  - Hit the miner to take a mine, and your lane minions grow bigger and stronger.
  - Hold both, and your side spawns super-minions while the enemy's minions drop back to normal size.
  - The other team can retake a mine at any time.
- **A gold mine** that fills with gold until someone takes it, then pays it out. Holding it pays the team again
  at intervals. Something happens there at the 15-minute mark.
- A shop in the middle of the jungle, where a player buying is open to attack.

**League of Legends, Twisted Treeline** (source: wiki.leagueoflegends.com/en-us/Twisted_Treeline)
- 3 per team. Two lanes either side of a neutral middle, turrets along each lane, one turret on the nexus.
- **Two altars** on opposite sides of the map:
  - stand on one for 9 s to take it, faster with more champions on it;
  - once taken it locks for 90 s, shows the area round it, and gives 80 gold to each player on the team;
  - one altar held: 10% move speed for the team;
  - both held: heal 1% of max health on every minion or monster kill.
- Boss: Vilemaw, at 10:00.
- Minions spawn at 0:45 and meet at 1:07, so about 22 s on the lane. No wards on this map.
- A search result says it was removed in 2019. The wiki page itself didn't confirm that.

## 2. What they agree on
- **The side objectives sit off the lane.** Leaving the lane to take one costs the lane, which is the choice
  the mode is built on. Ours already do this: the side pits sit in the pocket the lane's bend leaves.
- **Side points you take and hold, which feed the whole team.** Vainglory's mines make the waves stronger, and
  Twisted Treeline's altars give speed and healing. Neither pays only one player.
- **A timed big objective that breaks a stalemate:** the Demon King at 4:00, Vilemaw at 10:00, the gold mine
  event at 15:00.
  - Joust's is the most direct: it switches off a defence. Joust is also the closest map to ours, with one
    lane and few structures.
- **Joust has more jungle than we do:** 9 camps and a boss, against our 4 camps and 2 pits.
- **Our lane timing matches.** Our waves reach the plaza about 20 s after leaving the spawn. Twisted Treeline's
  minions meet after about 22 s.

## 3. Our open choices, with what the references say
These are the open choices from the layout doc, numbered as they are there.

**2. One tower or two.**
- Joust has two defences before the Titan (tower, then phoenix). We have one tower, then the core.
- Recommendation: keep one tower for now. Let the plaza objective (choice 5) do the work of opening the core.
  Add a second defence only if a played match ends too fast. Our match length hasn't been measured yet.

**3. Bushes.**
- None of the three sources covers bushes.
- From memory, not checked: SMITE has no hiding bushes, while LoL and Vainglory do.
- Recommendation: keep no bushes. That matches SMITE and keeps camouflage the chameleon's alone.

**4. What sits in the side pits.**
- Recommendation: make each pit a point you take and hold, using Twisted Treeline's altar numbers as the start.
  - Stand in the pit for about 9 s to take it, faster with more machines inside.
  - Once taken it locks for 90 s and shows the area round the pit through the fog.
- The reward feeds the lane, like Vainglory's mines:
  - one pit held: your waves come out stronger;
  - both held: stronger still.
- Why it fits:
  - The pit already has the 1.5 m rim and a home door and a stream-side door, built so the other team can
    steal it.
  - The kits that hold a spot (gorilla dome, hippo wallow, hummingbird bloom) get somewhere to matter.
- All numbers are starting points, to tune in play.

**5. Something to hold on the plaza.**
- Recommendation: a beacon, not a boss, using Joust's Demon King timing and effect.
  - It appears on the plaza at 4:00 and comes back every 5 min.
  - Take it the same way as a pit, and the enemy tower switches off for a set time.
- Why a beacon:
  - The plaza is where waves already meet every 30 s, so the fight comes to it.
  - A capture point reuses the pit code, where a boss would need its own fighting logic.
- The off-time needs a number. The wiki gives none for Joust, so start at 30 s and tune.

**6. The stream.**
- None of the three has water that slows players.
- Recommendation: leave it as looks only.

**Camps (not a numbered choice).**
- Joust's camps each give something: speed, damage, XP, mana.
- Ours could take speed (near home) and damage (near the middle) the same way.
- A mana-style camp waits on the energy decision, which is still open.

## 4. Who would build what, if Preston picks 4 and 5
- **Map lane:**
  - the capture zones in the pits and on the plaza;
  - the grate light in team colour;
  - a pit and beacon marker in the HUD's top stack and on the minimap (both files are this lane's).
- **Game feel lane:** the rewards, meaning stronger waves and the tower switch-off. Waves and towers live in
  its `match_director.gd`. The "open choice 4" placeholder label there would go.
- Both sides are small. The pits already have their rim, doors and light.

**The game feel lane's read (2026-11-05): nothing to block, and three things to add.**
- **Both rewards would be new code.**
  - Wave strength: there's no per-team value today. `MatchRules` holds `wave_size`, `minion_hp` and
    `minion_damage` for both teams, and each minion gets its own hp and damage when it spawns. A per-team
    multiplier read at spawn, or one extra minion per wave, is about 10 lines in the director.
  - Tower switch-off: towers are match units of kind "tower" with no disabled state yet.
- **Feel:**
  - A ground ring that fills at the pit, not only a HUD bar. The fill pauses, rather than resets, while an
    enemy stands in it.
  - A payoff when the point is taken: a flash, a sound, and `KitFeel.shake(node, 0.35)` from
    `scripts/moba3d/kit_feel.gd`.
  - Buffed minions get a visible tint or glow, so the push reads.
  - A switched-off tower looks off: beam gone, lights dim, a countdown over it.
- **Timing:** 9 s standing still is long in a 3 v 3 unless someone contests it. Test it before settling on it.
- The rewards are the game feel lane's if Preston picks these. Nothing in the director has changed.

## Built 2026-11-05: side pit capture (Preston: "Side pit capture")
- **Map lane:**
  - `scenes/moba3d/arena_pit.gd`, class ArenaPit: one per pit, built by arena_blockout.gd at runtime as
    Built/BluePitCapture and Built/RedPitCapture.
    - Numbers: 9 s alone, 6 s for two, 4.5 s for three. Pauses while both teams are inside. Holds 3 s when
      empty, then fades at 10% a second. A 90 s lock with 10 m of vision for the owner.
    - Signal `pit_taken(team)`, and `ArenaPit.held(tree, team)` for how many pits a team holds.
  - The ring: `shaders/world/capture_ring.gdshader`, 24 blocks at 4.2 to 4.9 m.
    - The fill climbs clockwise in the taker's colour and blinks while both teams are inside.
    - When a team takes the pit, the ring flashes white and the grate light bursts.
    - While the pit is locked, the lit blocks count the lock down in the owner's colour.
  - The grate light takes the owner's colour. The camera shakes (KitFeel 0.35) within 22 m.
  - **HUD:** a pit marker either side of the wave timer, your half's pit on the left.
    - Gold ring: nobody holds it.
    - Owner's colour: held.
    - Filled: locked.
    - Blinking with a fill line under it: being taken.
    - The feed says "Blue took the red pit" or "... took back its pit".
  - **Minimap:** a 5 x 5 marker per pit, with the rim in the owner's colour, filled while locked.
- **Game feel lane:**
  - `MatchRules.pit_wave_bonus` 0.25: each minion in a wave gets 1 + 0.25 per held pit, on hp and damage.
  - Boosted minions are tinted toward their team colour.
  - The placeholder `_pit_slot` is gone.
  - Bots don't go for pits yet. That's still open for Preston.
- **Sound lane:** `pit_taken.wav`, Preston's pick "Ring", is in MapAudio's EVENTS and PRIORITY. It hasn't
  been heard from a real capture yet.
- **Checks:**
  - `tools/map/pit_check.gd` (headless) passes 22 of 22: timings, pause, drain, fade, lock, vision, held().
    It also takes a pit live in arena_play and checks the feed line.
  - match_check passes 67 of 67. Game feel's rerun came after its tremor-stomp fix to the check, and after
    a sprite-material fix. Before that, the player's rhino drew with the fennec's sheet, because bots copied
    its material.
- **Picture:** `moba-pit-capture-2026-11-05.png`, from `tools/map/pit_shot.gd`. On top, the fill held at 60%;
  below, just after the take.
- **Not done:**
  - Numbers not tuned in play. Game feel's note: 9 s alone is long unless someone contests it.
  - The plaza beacon (choice 5) is built next, below.

## Built 2026-11-05: the plaza beacon (Preston: "continue", after picking the pits first)
- **Map lane:**
  - `scenes/moba3d/arena_beacon.gd`, class ArenaBeacon, extends ArenaPit. arena_blockout.gd builds it at
    runtime as Built/PlazaBeacon, at the plaza centre, counting machines within 4.5 m.
    - It comes up at 4:00 of match time, and 5:00 after each take: Joust's Demon King timings.
    - Taking it works like a pit (9 s, 6 s, 4.5 s; pauses when contested). Nobody keeps it: a take sends it
      down.
    - It reads the clock from the director (group "match_director") and keeps its own without one.
    - Signals: `beacon_up()` and `beacon_taken(team)`.
  - Looks:
    - a 3.8 m light beam with a pulsing light, under the camera's 4.45 m frame top;
    - the capture ring, gold until a team takes the beacon;
    - on a take, the beam bursts in the taker's colour and goes out, and the camera shakes within 22 m.
  - `arena_blockout.set_structure_off(structure, off)`: the tower's head stops turning, its team light drops
    to 15%, and its range ring hides.
  - HUD:
    - Under the wave timer, a "BEACON 0:30" countdown for its last 30 s, then "BEACON UP" with a blinking
      mark and a fill line in the taker's colour. The near-structure bar moves down a row while that shows.
    - A switched-off tower: its icon in the score plate blinks dark, "OFF 24" sits over it, and the
      near-structure label reads "red tower off 24".
    - Feed: "The beacon is up", "Blue took the beacon".
  - Minimap: a gold plus while it's up, blinking in the taker's colour.
  - `ArenaPit` now takes its ring size from its counting radius, and its group from `group`. The pits are
    unchanged.
- **Game feel lane:**
  - The director joins "match_director" and connects to the beacon.
  - A take switches the other team's tower off for `MatchRules.beacon_tower_off` through
    `MatchStructure.off_left`: no targeting, no shots, no beam.
  - If that tower is already down, nothing happens, because cores don't shoot.
- **Checks:** `tools/map/beacon_check.gd` (headless).
  - On the bench: timings, nothing taken before 4:00, the take, the 5:00 return, the two-machine time, and
    set_structure_off on and off.
  - Live in arena_play: it comes up, the player takes it, and the feed lines show.
- **Picture:** `moba-beacon-2026-11-05.png`, from `tools/map/beacon_shot.gd`.
- **Not done:** sounds for beacon_up and beacon_taken (the sound lane's). Numbers not tuned in play. Whether a
  bot match even reaches 4:00 hasn't been measured.

## Measured 2026-11-06: an all-bot match doesn't end
`tools/map/match_length_sim.gd` (headless) plays arena_play with all six machines on MatchBot. The player's
machine plays itself, as in the push demo. Six runs, 15 minutes each, about 3 minutes of real time per run:

| | Runs 1 to 3 | Runs 4 to 6 (tower health logged) |
|---|---|---|
| Winner by 15:00 | none | none |
| A tower down | never | never |
| Lowest tower health | not logged | blue 98% once; 100% in every other case |
| Beacon up at 4:00 | every run | every run |
| Beacon takes | 2 per run | 2 per run |
| Pit takes | 0 | 0 |
| Deaths per match | 20 to 27 | 22 to 25 |

The same seeds gave different matches, so a run isn't repeatable.

- **What it means:**
  - Waves and bots cancel out at the plaza. Nothing pushes far enough to touch a tower, so the beacon's
    30 s switch-off has nothing to act on.
  - The beacon does get taken without anyone aiming for it, because the lane runs through the plaza and
    bots walk over it. It comes up 41 s to 2.5 min after 4:00.
  - Bots never step into a pit, so the stronger-wave reward, the one piece built to break a stalemate,
    never fires in a bot match.
- **For the open choices:**
  - Choice 2: bots don't even scratch the one tower, so a second defence would only make it longer. Keep one.
    The real length still needs a human playtest; a human pushes and bots don't.
  - **Bots going for the pits and the beacon (Preston's call)** is what decides whether a bot match ever ends.
    The bot is `scripts/moba3d/match_bot.gd`, game feel's file.
- **Not measured:** a match with Preston playing, and what bots do once they do go for objectives.

## 5. Not checked
- SMITE 2's Joust may differ from the SMITE 1 wiki page.
- None of the pages gives map sizes in metres, so the comparison uses times instead.
- The bush claims above are from memory.
- Our own match length with a human playing. Bots alone don't finish one (measured above).
- For the 5 v 5 map, when Preston says go: read SMITE Conquest and Predecessor first, then give him the lane
  count, a cost and a first slice.
