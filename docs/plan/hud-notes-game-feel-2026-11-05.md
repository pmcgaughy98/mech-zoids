# HUD notes from the game feel lane (2026-11-05)

Written for the map lane's HUD rethink. Preston named SMITE's HUD as his favourite and the target. These are layout
lessons only, with no copied art or look.

**Honesty line:** this lane has not studied SMITE's or any other MOBA's HUD in this project. Sections 1 and 3 come
from general knowledge and are **unverified**. Check them against real footage before laying anything out (for
example the `watch` skill on a SMITE 2 match video). Section 2 marks what was measured here.

## 1. SMITE (unverified)
- **Bottom centre, one block about yourself:** the god's portrait and level, health and mana bars directly above the
  ability row, the four abilities with cooldown sweeps and numbers, then the relic/active slots and consumables. The
  items sit next to the block. Unverified: whether the items sit left or right of it, and SMITE 2's exact arrangement.
- **Top centre:** team kill score and match timer. Team portraits (level, health, respawn timer) run out to either
  side. Unverified whether tower/phoenix status sits here or only on the minimap.
- **Minimap:** a screen corner, placement unverified (SMITE 1 and 2 may differ). The kill feed sits near it on the
  right. Unverified.
- **Why it reads well in third person:** the middle of the screen stays empty for the reticle and the fight. Targeting
  shapes are drawn on the ground in the world, not on the HUD. Everything about you sits in one place at the bottom,
  so the eye makes one short trip down and back.

## 2. Feel rules the HUD has to serve
Measured here:
- **Overhead bars:** match_hud.gd puts a 64 x 6 px bar at 1.9 m x size scale (S 0.8, M 0.9, L 1.0) and the
  drone's at 1.3 m, 30 x 4. Tilted 35-degree sprites need 2.3 m x size scale to clear the art from the player's spot
  outward. At the wall spot the bar still lands on the art (fennec -14.4 px, kangaroo -20.6 px), so pull it toward
  the camera or offset it in screen space. Source: `cam_angle_set_test.gd` logs and `docs/art/moba/match/MATCH_NOTES.md`.
- **Pops already measured:** the fennec's switch between its 35-degree idle and its old actions; walk turns
  swapping feet (fixed today). The HUD shouldn't add motion of its own on top of these moments.

Not built yet; standard practice, worth building:
- **Cooldowns:** a dark radial sweep plus whole seconds (decimals under 1 s), a short ready flash with a sound, and a
  separate tint for "not enough mana" so it never looks like a cooldown.
- **Hit feedback:** a 1 to 2 frame white flash on the struck sprite, a short hitstop on heavy hits, and a red edge
  vignette on the side the damage came from.
- **Low health:** below about 25 to 30%, the bar pulses and a light vignette shows. It never covers the middle of the
  screen.
- **Tower aggro:** the tower draws a visible beam or line to its target, plus a warning icon on your own block when
  you are the target.

## 3. Other MOBAs, one lesson each (unverified)
- **Predecessor** (third person, like SMITE): keep the ability block bottom centre with health right above it.
  Third-person MOBAs seem to settle on this.
- **Deadlock** (third person): time-critical numbers (ammo, cooldowns) go close to the crosshair, not in a corner.
- **League of Legends:** everything about you in one bottom block, and a red line from the tower when it targets you.
  Players learn that one tower-aggro signal fast.
- **Dota 2:** a top bar of portraits with respawn timers, so you can see who is dead and for how long without
  opening the scoreboard.
- **Pokemon Unite:** big shapes and one-glance team scores with the timer at top centre. It stays legible at small sizes.

## 4. Ownership
- This lane wrote `scripts/moba3d/match_hud.gd` (2026-11-04). Its look is a plain placeholder. The bottom-right
  corner was kept free for the map lane's minimap.
- Proposal: the map lane owns the minimap. For the rest of the HUD, Preston picks one writer. Either the map lane
  takes match_hud.gd over, or it writes the layout and this lane builds it. Only one lane edits the file at a time.
