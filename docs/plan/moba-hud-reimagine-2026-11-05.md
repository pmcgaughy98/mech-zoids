# MOBA HUD: SMITE study and a first direction (2026-11-05)

Map design lane. Preston's target is SMITE's HUD. We take the layout lessons only. The look stays ours
(pixel art at the 320 x 180 base, machine-shop style), never SMITE's art, frames or theme.

Status: research and a proposal. Nothing is built yet.

Ownership (settled 2026-11-05, Preston's pick, passed on by the game feel lane): the map lane owns the whole HUD,
`scripts/moba3d/match_hud.gd` and `scenes/moba3d/arena_minimap.gd`. The game feel lane no longer edits it.

Dependency: `scripts/moba3d/cam_angle_set_test.gd` copies the overhead bar numbers into its BARS table (line 12).
Change bar height, width or thickness there too, or the turn tests check the old bar.

## 1. What we have now

- Over every unit: a flat health bar (green you, blue allies, red enemies, amber monsters).
- Bottom centre: machine name, health bar and number, four kit slots with cooldown shade and seconds, attack (Space), recall (B).
- Top centre: clock, next-wave timer, each team's tower and core health as bars.
- Top right: kill feed (fades after 7 s).
- Middle: tower-targeting warning (red edge flash and text), respawn countdown, recall bar, victory and defeat.
- Bottom right: the minimap, pixel art, 30 x 56 base px (31% of screen height), flips for red, fog of war, camera outline.
- Look: flat bars and the default font, marked PLACEHOLDER in the code.

## 2. SMITE's HUD, element by element

Source: the official SMITE wiki's HUD page, which describes SMITE 1 on PC. SMITE 2 ships a "Legacy" preset that
emulates SMITE 1 and a "Novus" preset that pulls items toward the centre (SMITE 2 wiki, Alpha Weekend 3, mid-2024).

| Where | What |
|---|---|
| Top centre | Score display: match clock, each team's kills and gold. Pre-match countdown. |
| Under the score | Objective health: a bar for a nearby boss, structure or titan, shown only when near. Recent-death icons under each side. Accolades (streaks, objectives) in the centre. |
| Near centre | Kill messages, including deaths to minions and monsters. |
| Bottom centre | Player bar: god portrait, health (green, with regen), mana (blue, with regen), level and XP (yellow), abilities with rank, relics and consumables. |
| Above the player bar | Buff and debuff rows (up to 10 each). A per-god passive meter above or left of it. |
| Top left | Ally frames, vertical: level, health, mana. A diamond per ally lights when their ultimate is ready; wedges fill as it charges, and the last wedge means a few seconds left. |
| Top right | Enemy frames: level. Portrait greys at very low health; a respawn timer covers it when dead. |
| Upper right | Minimap: gods, structures, minions, camps. |
| Bottom left | Stats and items: KDA, gold, core stats, items with tier. Optional item panel bottom right. |
| Left side | Chat, quick voice callouts, pings, combat log. |
| Options | HUD editor: move, resize or hide most elements. SMITE 2 added a colour preset for health bars and minimap (colour-blind help, Open Beta 2). |

Console layout splits the player bar: abilities bottom right, relics bottom left, for the thumbs.

## 3. Why it reads well in third person (my reading, not sourced)

- The god stands low and centre in a chase camera, so the player bar sits right under the eye line. Health and
  cooldowns get read without looking away from the fight. Our chase camera puts the machine in the same spot.
- Distance from centre matches how often you look: every second (own health, cooldowns) at bottom centre; often
  (clock, score, objective health) at top centre; glances (team, enemies, map) in the corners; rarely (stats,
  items) bottom left.
- Context, not clutter: objective health appears only near the objective; kill messages fade.
- One glyph answers one question: the ally ultimate diamond answers "can we take this fight?"

## 4. Other MOBAs

- **Predecessor** (third person, closest to SMITE): a review credits it with staying readable in late-game
  teamfights while looking modern. Players asked for a scalable minimap and grouped sections; the studio said more
  HUD customisation is planned. Lesson: readability in the big fight is the test.
- **Deadlock** (one player's critique on Steam, an opinion): the health bar is small, grey and vertical, while
  ammo and stamina sit by the crosshair so you never look away. Lesson: the numbers you need mid-fight go where you aim.
- **Dota 2** (from memory, unverified): all ten heroes in a top bar either side of the clock, with respawn timers,
  so you see who is dead and for how long without opening a scoreboard. Minimap bottom left; hero bar bottom centre
  with items beside the abilities.
- **League of Legends** (from memory, unverified): minimap bottom right; everything about you in one bottom block.
  A red line from a tower to its target is a single aggro signal that players learn fast.
- **Pokemon Unite** (game feel lane, unverified): big shapes and one-glance team scores, timer at top centre. It
  stays legible at small sizes, which matters at our 320 x 180 base.

The game feel lane's notes (`docs/plan/hud-notes-game-feel-2026-11-05.md`) mark their SMITE and MOBA sections as
general knowledge, unverified. Where they differ from section 2, section 2 (the SMITE wiki) wins.

Common ground: every one puts the player bar bottom centre and the clock top centre. Only the minimap corner varies.

## 5. Gaps against SMITE

| SMITE has | We have | Proposal |
|---|---|---|
| Score: clock, team kills, gold | Clock, next wave, structure bars | Clock, team kills, structure pips; next wave small |
| Objective health when near | Always-on structure bars | Show the nearby structure's bar under the score only when near |
| Kill messages near centre, death icons | Kill feed top right | Move under the score, fade in 4 s |
| Player bar with portrait, level, resources | Name, health, slots | Card portrait, health, slots with cooldown sweep; resource and level only if the kits get them |
| Buff, debuff, passive meter | None | One row above the player bar; passive meter for kits that need it (fennec gate, gorilla shield) |
| Ally frames with ult diamond | None | Top left, card portrait, health, ult pip with charge wedges |
| Enemy frames with respawn timer | None | Top right, portrait greys at low health, timer when dead |
| Minimap upper right | Minimap bottom right | Open choice (section 7) |
| Stats and items bottom left | None (no items yet) | Reserve the corner; fill when items exist |
| HUD editor, colour preset | None | Later: two presets and a colour-blind team palette |

## 6. Direction, draft A

- Look: pixel art at 320 x 180 base, whole base pixels like the minimap. Dark steel plates, rivets, hazard-stripe
  trim, team blue and red, one pixel font. Portraits from the card portraits lane.
- Top centre: clock, team kills, tower and core pips per team (grey when felled). Nearby structure's bar under it.
- Under the score: kill messages and recent-death icons.
- Top left: ally frames. Top right: enemy frames.
- Bottom centre: player bar, buff row above it, passive meter at its left.
- Bottom left: reserved for stats and items.
- Centre: respawn and recall as now. The tower warning leaves the screen edges for a line from the tower and an
  icon on your own bar (feel rules below).
- Team frames: designed for 5 a side (the main mode), and they must still read cleanly at 3 on this map's 3 v 3
  side mode. At 5 a side, Dota's lesson (respawn timers on every portrait) carries more weight. The resource and level elements are optional and
  drop out cleanly while the kits run on cooldowns only.

Feel rules the HUD must serve (from the game feel lane, measured or built there):
- Cooldowns: a dark radial sweep plus whole seconds (decimals under 1 s), then a short ready flash with a sound. If a
  resource ever arrives, "can't afford" gets its own tint so it never reads as a cooldown.
- Hits: a 1 to 2 frame white flash on the struck sprite, a short hitstop on heavy hits, and a red edge vignette on
  the side the damage came from.
- Low health: under about 25 to 30%, the bar pulses and a light vignette shows, never over the middle of the screen.
- Tower aggro: a visible line from the tower to its target, plus a warning icon on your own bar.
- The HUD adds no motion of its own on top of those moments.
- Mouse aim (Preston picked "aim at the mouse", 2026-11-05; machine_test_player.gd, MATCH_NOTES.md "Aim at the
  mouse"): abilities fire at the mouse's point on the floor, shown as a ring and a line. Aiming low on the screen puts
  the ring under the player bar. Rule: the aim ring and line draw on a layer above the HUD, and the player bar stays
  as short as it can (draft A: 29 of 180 base px). Hold-to-preview ability shapes come later and use the same layer.
- Overhead bars: 64 x 6 px at 1.9 m x size scale (S 0.8, M 0.9, L 1.0); drones 30 x 4 px at 1.3 m. Tilted 35-degree
  sprites need 2.3 m x size scale. At the wall spot the bar still lands on the art (fennec -14.4 px, kangaroo
  -20.6 px); a screen-space nudge toward the camera may fix it.

## 7. Open choices for Preston

1. **Settled 2026-11-05: minimap stays bottom right** (Preston picked mock-up B). The bottom of the screen then
   carries the KDA panel, the player bar and the minimap, so the mouse-aim rule matters more: the aim ring, its line
   and later ability previews draw above the HUD.
2. **Settled 2026-11-05:** the main mode is 5 v 5 on a future map; this one-lane arena is a 3 v 3 side mode
   (Preston, via the hub). The HUD targets 5 a side and must still work at 3.
3. Resource and levels (also with the hub): nothing approved, and the kits run on cooldowns only. The draft keeps
   both droppable.

## 8. Next steps

1. **Mock-up, done 2026-11-05:** `docs/plan/moba-hud-mock-2026-11-05.png` (A over B) and `..._a.png` (A at full
   size). Built by `tools/map/hud_mock_shot.gd` (Godot: the arena frame, anchors, sprite frames) and
   `tools/map/hud_mock.py` (PIL: the HUD painted at the 320 x 180 base, a hand-drawn 3 x 5 pixel font). 5 v 5 shown.
   Portraits are sprite frames scaled down (four machines have frame sets; the rest borrow); the icons are stand-ins.
   Two look-and-fix passes changed draft A:
   - Top centre kept thin (one-row score, wave timer and structure bar without plates). In our chase camera the
     tower you are pushing sits right under SMITE's score spot, and the first pass hid it.
   - Kill messages moved from the centre to the left column under the ally frames, off the lane.
   - While an ability cools down, its seconds replace the key label in a 4 x 6 font; "2" plus "4" read as 24.
   - The health number sits beside the bar, not across the fill edge.
   - The tower-aggro line starts below the structure bar and stops above your overhead bar.
   Recommendation was A (bottom right left open for mouse aim). **Preston picked B, minimap bottom right**
   (2026-11-05); see section 7.
2. Optional check: watch a recent SMITE 2 match (watch skill) to confirm its Legacy layout still matches the wiki,
   which describes SMITE 1.
3. **Built 2026-11-05** in `scripts/moba3d/match_hud.gd` (layout B, pixel art on the 320 x 180 canvas):
   - In: score row with team kills and tower/core pips, clock, wave timer; the nearest structure's bar (your own only
     once hurt); ally frames with recharge diamonds; enemy frames (grey when low and seen, respawn seconds when down);
     kill feed under the allies; player bar with portrait, health, kit slots (seconds replace the key while cooling,
     white flash when ready), attack and recall; KDA (assists: a hit within 10 s); the tower-aggro icon and line;
     low-health pulse and edge glow; death, recall and victory screens; the mouse-aim ring and line on layer 7 when
     the aim falls under a panel (reads the game feel lane's `aim_marker_visible()`).
   - Unchanged: the overhead bars (still the 720-line sizes, so cam_angle_set_test.gd's BARS table holds);
     `feed_lines()` and `warning` for the checks.
   - Checked: match_check 67 pass, 0 fail (before two cosmetic tweaks: the larger DESTROYED text and hiding your own
     full-health structures; those two pass Godot's --check-only). Live frames: `docs/plan/moba-hud-live-2026-11-05.png`
     (top: 35 s into a match; bottom: at red's tower on low health with the aim under the bar), made by
     `tools/map/hud_shot.gd`.
   - Not in yet: the hit flash and directional damage vignette, the buff and debuff row, a ready sound, drawn ability
     icons (stand-ins now), card portraits (idle_s frames now), energy and levels (Preston hasn't decided), a
     1920 x 1080 overlap check.

Sources: smite.fandom.com/wiki/Head-up_display; wiki.smite2.com/w/SMITE_2_Alpha_Weekend_3; tacter.com SMITE 2
Open Beta 2 notes; rpggamers.com Open Beta 5 news; escapistmagazine.com Predecessor review;
r/PredecessorGame UI feedback thread (Oct 2024); steamcommunity.com Deadlock HUD discussion.
