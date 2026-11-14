# Bison furnace mech: proposal

Preston selected the bison, heat, flames, visible steam and a raging bull feel. This is an implementation proposal for that direction, not a final name, lore or balance specification.

## Body

A broad, low mechanical bison with its mass over the forequarters: a high shoulder hump, a huge low head, thick neck, compact hindquarters, four separate short powerful legs, split steel hoof pads and a short straight segmented tail. A bison's hump and short upward-curved horns distinguish it from a long-horned cattle bull. The hump is the furnace housing. The head and shoulder line lean into a charge without lifting a foot in the reference pose.

The upper shoulder housing carries a matched pair of squat pressure exhausts with open dark mouths. A small, clear furnace grille sits on each flank of the hump. Keep the vents and grille large enough to read at game size. Short broad horns project outward then up and slightly forward from the sides of the head, with steel tips. Recessed pale-amber lens eyes sit under a heavy mechanical brow. Hard plates, joints and pistons make it a robot at first glance. No organic fur, beard, skin, decorative mane, clothing or held weapon.

Proposed palette: saturated red-orange main armour, warm dark-red underside, charcoal chassis, cool steel horns and hooves, and yellow-orange furnace light. Do not cover the entire animal in orange glow: the dark structure must keep the shoulders, face, legs and belly readable.

## Heat and steam

Steam actually vents in the finished presentation: small paired shoulder releases at idle, stronger bursts as pressure rises, and a sharp muzzle purge before a charge. Flames appear at the built-in furnace outlets when an ability fires. These are separate effects attached to named sockets; neither steam nor flame is geometry in the model-reference image or painted permanently over the legs.

Proposed sockets: `steam_l`, `steam_r`, `muzzle_purge`, `flame_l`, `flame_r`, `core_light`. Their transforms are authored on the final rig. Both sides have the same physical hardware so rotations and mirrored sprite views agree.

## Proposed kit

Close-range pressure fighter. Descriptive labels only; no final names or numerical balance values.

| Slot | Proposed behavior | Read and counterplay |
|---|---|---|
| Basic | Short heavy horn/head sweep; alternating recovery direction | Low head wind-up, contact accent, free movement after contact; held basic repeats through the existing game input |
| Passive: heat pressure | Offensive actions build visible heat. Pressure improves an ability when deliberately spent. Venting trades stored pressure for immediate space. | Grilles brighten and steam pulses increase. Pressure drains out of combat. Avoid hidden permanent bonuses. |
| 1: furnace jet | A short aimed cone of flame from paired front furnace outlets; pressure widens its reach/coverage. | Clear wind-up and visible cone, interruptible recovery; no turret or held flamethrower. |
| 2: pressure release | A radial steam burst pushes nearby enemies outward and consumes stored pressure. | Shoulder valves open before the burst; a visible edge tells enemies its extent. Steam is brief enough to preserve team and floor readability. |
| 3: raging charge | A telegraphed head-low forward rush. First enemy contact ends the rush in a short shove and heat impact. | Paw/scrape and muzzle purge before commitment; limited steering. No rhino-style catch-and-throw. |
| 4: furnace overdrive | A short raging state with brighter vents and controlled flame exhaust. Keeps the existing kit and makes heat generation faster; its end forces a visible purge/recovery. | Strong start cue and duration read. No second full moveset, invulnerability or unlimited repeated knockups. |

The charge is the central bull behavior. Heat generation, release and overdrive carry the power theme, following the current kit rule that machines have technological/elemental abilities beyond animal motions. All listed effects and interactions are proposals until Preston picks them.

## Sources and what was actually read

- NPS, Bison, description and behavior: https://www.nps.gov/wica/learn/nature/bison-buffalo-bison-bison.htm . Shoulder hump, short upward horns, front-heavy mass, head bob/paw/snort charge warning. Anatomy/behavior only; no image copied.
- Riot, Rumble official champion page: https://www.leagueoflegends.com/en-us/champions/rumble/ . Read the heat passive description; take the structure of visible buildup and a meaningful threshold. Do not copy its exact thresholds, silence, visuals, lore or moveset.
- Riot, Ornn official champion page: https://www.leagueoflegends.com/en-us/champions/ornn/ . Read tank role, ability inventory and the described elemental ultimate. Use as a check that a heat-themed frontliner can have distinct engagement cues; do not copy its summoned ram, recast, brittle or equipment system.
- Local current kit rules: `docs/plan/moba-kits.md` and `CLAUDE.md`.

## First visual review

One model-reference sheet, then the model from those four views. Judge the front, side and back for the same horn attachment, hump, vent count, grille placement, leg proportions and palette. The body must read as a bison without any effect visible. Judge the eventual 35-degree sprites at game size before animation work.
