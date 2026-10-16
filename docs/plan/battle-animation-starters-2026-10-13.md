# Battle animation foundations for the starters (Claude, 2026-10-13)

Preston: "Use the synthesis. Build Attack animation foundations for our starters." The gorilla had its set (punch,
slam, throw, from `reports/Gorilla mech animation foundation.md`); now all six starters have one, wired into the battle.

## Synthesis: what each source gave
- **The gorilla animation report** (`reports/Gorilla mech animation foundation.md`, deep research 2026-10-12): the
  method. Anticipation, action, reaction; heavy reads as a long held anticipation, one fast strike and a settle in
  parts; skip the contact frame (the first strike frame is past the target); machines never squash, the mass moves as a
  unit; rock the weight back before a heavy action; 40-50 % anticipation, 10-15 % strike, 35-50 % recovery; attack
  frame budget 9, timing 150-250 ms wind-up, 50 ms strike, 120-200 ms settle; idle 4 frames ping-pong at 450 ms; hit 3.
- **The battle code** (`scripts/scenes/battle.gd`, `scripts/ui/machine_anim.gd`): the contract. A weapon's "clip"
  plays on the attacker; the target is struck at the clip's strike frame; "hit" plays on the target, "death" on
  defeat, "idle" between. Flash, shake and damage numbers are engine-side.
- **The Zoids Legacy decomp and sprite study** (`docs/reference/zoids-legacy-structure.md`, the report's genre table):
  that style shipped one static pose per unit with overlays; so projectiles, beams, scale volleys and jet streams stay
  Godot overlays, not rendered frames.
- **The real animals** (the designs in `docs/design/` and the build files' notes): the wolf's lunge and bite, the
  hippo's gape and surge, the pangolin's tail sweep and ball, the kangaroo's boxing and tail-supported kick, the
  shoebill's motionless wait then strike.
- **Our rigs and battle stances**: every clip starts and ends on the stance the installed sprites show, so idle,
  attack and sprite agree.

## The clips
| Machine | Weapons (roster) and clip | What moves |
|---|---|---|
| Black wolf | Fang Lunge `lunge`, Howl Burst `howl`, Shadow Dash `dash` | rock back and spring, jaws past the bite; head thrown up then the blast snaps it level with recoil; deep crouch then a pass forward |
| Pygmy hippo | Gape Crush `gape`, Pressure Jets `jets`, Wake Charge `charge` | head rears up then slams down; braced recoil; rock back then a head-down surge |
| Pangolin | Scale Rake `rake`, Scale Shot `shot`, Ball Roll `roll` | tail winds and sweeps, each joint later than the last; back arches then snaps; head tucked, tail curled over, a tumble forward |
| Red kangaroo | Impact Boxing Gloves `jab`, Pouch Flak Gun `flak`, Tail Spring `kick` | near glove cocks with a twist then jabs; lean back and recoil; lean back onto the tail and both feet forward |
| Shoebill | Bill Clamp `clamp`, Stillwater Lance `lance`, Wing Buffet `buffet` | head rises then the bill drives down; a long still aim then recoil; wings lift then one downbeat |
Plus `idle` (breathing on the stance), `hit` (jolt back, head late) and `death` (sinks and tips, held) for each.

## Files
- `tools/blender/attacks.py`: the clip definitions (phase keys, stance solvers that keep feet planted, the five sets).
  Wired through `quad_rig.rig_and_clips` and `bird_rig.rig_and_clips` (cfg "battle_set") and the kangaroo's build.
- `tools/art/anim/<id>_plan.json`: frame picks and timings. `bash tools/art/anim_round.sh <id>` renders, pixelizes on
  one canvas and packs `art/machines/<id>/anim/`. Run it after installing any new build of the machine.
- `tools/blender/render_jobs.py`: all of a machine's frames in one Blender session (paths absolute: a relative output
  wrote to C:\docs once).
- `scripts/data/machines.gd`: each starter weapon names its clip.
- `tools/debug/battle_capture.gd`: HT_PLAYER, HT_ENEMY, HT_WEAPON pick the fight; writes
  `docs/art/2d/battle_<player>_vs_<enemy>.png`.

## Foundation, not final
- Signs and amounts were checked on renders and fixed once (the kangaroo kick's legs ran the wrong way, the jab read
  as an uppercut, the pangolin roll dove nose-first, three attacks travelled out of the camera frame). The kangaroo's
  jab still reads small at sprite size.
- The pangolin has no battle_feet stance yet, so its idle stands on the planted rest pose rather than the walk frames
  its installed views use.
- Next: the weapon overlays in Godot (howl wave, jets, scale volley, lance beam, flak), a sound cue two frames before
  each strike, a win clip, and Codex's finish pass on the frames.
