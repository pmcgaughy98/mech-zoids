# Codex: new references for the six weaponized starters (Claude for Preston, 2026-10-13)

Preston asked for "more pieces and parts" and weapons on every starter, wired up as a foundation "so codex can
generate the reference we need". The 3D builds now carry them. Your job: draw one polished reference per machine
from its render, the way the gorilla's newest reference was drawn from build v58 (Preston: "a great reference,
everything else looks great").

## Inputs: `docs/art/codex_inputs/2026-10-13/`
For each machine: `<id>_render_se.png` and `<id>_render_e.png` (full-size Blender renders) and `<id>_sprite_se.png`,
`<id>_sprite_e.png` (the in-game pixel sprites). The current references are in `docs/art/reference/starters/<id>.png`.

| id | machine | build | 
|---|---|---|
| ape_l | gorilla | v62 |
| wolf_m | black wolf | v29 |
| kangaroo_m | red kangaroo | p32 |
| shoebill_m | shoebill | p42 |
| hippo_m | pygmy hippo | p15 |
| pangolin_m | pangolin | p10 |

## Output
**Transparent background, PNG with alpha. No background colour, no glow, no vignette, no ground shadow.** (The
first gorilla and wolf from ChatGPT, 2026-10-13, came on a dark glowing backdrop and had to be cut out by script.)
Put this line first in any image prompt. Two images per machine, one creature per image:
- `docs/art/reference/starters/<id>_weapons_se.png`: the three-quarter front view, as the render_se. The gorilla's
  last reference was drawn at this angle and matched the model best (0.756 outline overlap against 0.503 for the side).
- `docs/art/reference/starters/<id>_weapons_e.png`: the side view facing right, as the render_e.
Do not overwrite the existing `<id>.png` files.

## Rules
1. **Keep the build's placement exactly.** Every weapon, plate and joint stays where the render puts it. The last
   gorilla reference moved the back pillars; that is the one thing Preston flagged. Keep proportions, leg positions
   and pose from the render.
2. **The look.** Cleaner and better finished than the Zoids sprites, never PS1-style: chunky readable plates, a
   light from above and a little left, sel-out edges (lighter on top edges, darker underneath), no uniform black ring.
3. **Colours from the build.** Same main, trim, accent and eye colours as the render. Weapon housings are the
   machine's grey frame; muzzle collars and studs are its accent colour.
4. **Weapons read as hardware.** Barrels with a muzzle collar, launcher boxes with visible tube mouths, glowing
   emitter lenses. Draft hardware, so clear shapes matter more than detail.
5. **No copying.** The Zoids Legacy sheets are for technique only. No shape, marking or colour scheme from them.

## The loadouts
Moves are the roster weapons in `scripts/data/machines.gd`. SPARE marks a DRAFT hardpoint with no move yet (Preston
names it later). Positions and muzzle points are in `docs/art/3d/<id>_weapons.json`.

**Gorilla (ape_l).** The roster's moves already had hardware: Piston Knuckles (the fists and forearm rams), Ballast
Throw (the block rack on the back), Quake Slam (the fists). New: a rotary gun on the right shoulder (SPARE) and a
2x3 launcher on the left shoulder (SPARE).

**Black wolf (wolf_m).** Fang Lunge: red teeth along the upper jaw. Howl Burst: a glowing emitter in the throat.
Shadow Dash: a swept red blade on the outside of each forearm, plus the shoulder and hip fins. SPARE: a long rail
gun on the right of the back, a 2x2 launcher on each haunch. New detail layer: jointed thin legs with a high hock,
hydraulic rams on the upper legs, a spine ridge, flank vents, two exhaust stacks, a neck collar, belly cables, tail
rings, a red brow crest, two antenna masts, a chin guard.

**Red kangaroo (kangaroo_m).** Impact Boxing Gloves, the hip jet boosters and the closed pouch hatch (the Pouch Flak
Gun stays hidden; nothing protrudes) as before. New: a 3x2 rocket pod on the right shoulder (SPARE), a rotary gun on
the left shoulder (SPARE).

**Shoebill (shoebill_m).** Stillwater Lance: the gun on top of the head, as Preston's first reference had it.
Bill Clamp: teeth along the upper bill's edge. SPARE: a gun on each side of the breast.

**Pygmy hippo (hippo_m).** Gape Crush (jaw and tusks) and Pressure Jets (the valves above the snout) as before.
Wake Charge: a water thruster on each flank, plus the bow ram. SPARE: a short twin cannon on the front of the back,
two torpedo tubes behind it.

**Pangolin (pangolin_m).** Scale Shot: the shoulder launcher racks as before. Ball Roll: Delft-blue studs along the
spine. SPARE: a rotary gun under the snout, a 2x3 launcher on the rump firing up and forward.
