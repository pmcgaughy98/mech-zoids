# Bison ability effects: synthesis (2026-11-13)

Bison effects lane, on the method the rhino, gorilla, hippo, kangaroo and pangolin lanes used (their synthesis docs in
this folder). Bar (Preston, held across every lane): smooth, layered, HDR, SMITE 2 grade, never pixel art. Impact
flashes small and short, no drifting glowing motes, no point light washing the mech out, no red on the player's own
mech, and anything that travels has a shape with height.

## Where the bison stands (read first)
- **Kit code: none.** No `bison_kit.gd`. The kit is the Ares + Vulcan draft (`docs/plan/kit-design-2026-11-11.md`,
  line 677; `D:/dev/_scratch/bison-3d/kit-ares-vulcan-draft-2026-11-12.md`): basic Horn hook, passive Scorch and Slag,
  1 Coupling Chain, 2 Eruption, 3 Plow, 4 Freight (Brace, then Haul). Every name and number there is a placeholder.
- **Registered 2026-11-13** (Preston: "Yes register the bison"; done by the bison 3D lane): `art/arena_models/bison.glb`
  is the r4 export, its roster entry is `authored_trial`. Not in BOT_ROSTER yet (the game feel lane's file), so bots
  never pick it. The launcher puts this body on the player; the r4 GLB read at runtime is only its fallback.
- **Body:** the bison 3D lane's r4 export, `D:/dev/_scratch/bison-3d/game-export-r4/` (13 clips). Eruption events:
  gather 0.04, roar 0.32, erupt_fl 0.38, erupt_rr 0.48, erupt_fr 0.58, erupt_rl 0.68, recover 1.05 s. The four stack
  sockets ride the scapula bones (Bone_042 left, Bone_036 right), 0.34 m apart side to side, 0.27 m front to back, at
  1.69 to 1.70 m. Each shot drops the hump about 2 cm, so the effects carry the read.
- **Chase camera** (distance 12, pitch 13): the hump hides the head; the stacks are the top of the machine.

## What was read and measured

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, Vulcan, "How to Vulcan in SMITE 2 in under 7 minutes" (youtube eMB5h7tx3-s, 1280x720 at 60 fps) | Confirmed SMITE 2: the title and the in-game ability cards for Inferno Cannon, Magma Bomb and Earthshaker (scan 258 to 348 s at 1 fps, `ref/vul_scan.jpg`). **Measured** at 15 fps, cell by cell: Magma Bomb casts from 294.0 s and 299.5 s (`ref/vul_bomb15_a.jpg`, `vul_bomb15_b.jpg`); Earthshaker from 328.5 s and 331.4 s (`vul_quake15.jpg`, `vul_quake15_b.jpg`) | A thrown molten bomb's order and timing; how a falling shell is marked on the floor |
| SMITE 2, Ares, "SMITE 2 GOD GUIDE: ARES" (youtube WkAhTsxnMwc, 1280x720 at 60 fps) | Confirmed SMITE 2: the title; the narrator compares it with SMITE 1 throughout. **Measured** at 15 fps: two Shackles throws and refires from 42.6 s and 62.6 s (`ref/ares_chain15.jpg`, `ares_chain15_b.jpg`). No Escape sampled at 254.4 s (`ares_ult15.jpg`) but too close and off frame: **not measured** | The chain's shape and its heat pulse |
| Inferno Cannon | Ability card read only, not measured | Not taken (a turret; the kit takes no turret) |
| Our clips, profile and kit draft | Read | Event times, socket positions, slot list |

Scratch: `D:/dev/_scratch/bison-fx/ref/` (the two videos, their captions, every sheet). Nothing from either video is in
the project. Structure only, never a copy.

## Structure learned (measured unless marked)

**Magma Bomb** (cast at 299.5 s, cells at 15 fps):
1. Cells 1 to 11: an aim ring on the floor (the caster's targeting UI; not ours).
2. Cell 12, release: a **dark, lumpy ball** leaves the hand with one small curl of flame. One cell, no flash.
3. Cell 13: the ball is already high, still dark, a short flame under it.
4. Cells 14 to 17: the ball is off the top of the frame; a **thick glowing trail** hangs from the top down to the release
   point, then thins and goes out in about 4 cells (0.27 s).
5. Cells 18 to 22: it falls back **steeply**, still dark, with only a **thin, short streak** above it (0.33 s).
6. Cell 23, landing: a hot pale core with a **spiky star burst**. Cell 24: a wider star (the peak). Cells 25 to 26: a glow
   smear going out, a hot spot in the middle.
7. Cells 27 to 44 and on: a **dark scorch** on the floor with a few small hot spots, still there 1.2 s later.
8. Release to landing: **11 cells, 0.73 s.** The cast at 294.0 s shows the same order (trail 8 cells before the landing,
   burst 3 cells, glow 2).

**Earthshaker** (331.4 s): a big shell, dark with glowing bands, falls on a thick flame trail; **the floor under it
reddens one cell before it lands**; the landing is a flat burst with flame tongues (the video cuts away the next cell).
At 328.5 s the shell goes up on a thick exhaust.

**Shackles (Ares)** (42.6 s and 62.6 s):
1. The chain is a **solid dark iron chain of spiky links**, with real thickness: it reads from every angle.
2. It reaches the target **within one cell** (under 0.07 s). No visible travel.
3. Each refire sends a **heat pulse along the chain**, caster to target, over 5 to 6 cells (0.35 to 0.4 s): a flame blob
   at the caster end, a thinning streak running out.
4. The target glows while chained; the chain stays linked for the whole 2.4 s sampled.

**No Escape:** general knowledge only, not measured: chains to every enemy in a radius, then a pull.

## Synthesis proposal (nothing here is canon)

**Look: dark crust, hot seams.** Every molten thing (bombs, chunks, slag) is a dark, matte basalt crust with glowing
seams between its plates (Magma Bomb's dark ball and Earthshaker's banded shell both point here). Seam cores go above
HDR 1.05 and bloom; seam edges and crust stay under. That keeps the bison away from the forge's natural amber and
copper, which the rhino and pangolin own.

## Decided: colour (Preston, 2026-11-13)
"Magma orange". Option B below is the bison's effect colour: deep orange seams and fire with yellow-white cores on dark
basalt crust. `bison_fx.gd` and the launcher default to it; "white" stays in the code for comparison only.

**Colour options as shown** (two built side by side; blue built earlier and dropped):
- **A: white-hot.** Seams and fire white with a pale cream edge (hot 1.0 0.97 0.92; warm 0.95 0.88 0.74). The hottest
  forge read; distinct from every taken colour. Risk: on bright floors the trail can read pale.
- **B: magma orange.** Deep orange seams and fire with yellow-white cores (hot 1.0 0.93 0.70; warm 1.0 0.36 0.06): the
  volcano read. It stays apart from the rhino's amber cracks (1.0 0.62 0.22) by hue (redder) and by structure (dark crust
  plates, not cracks in the floor). Risk: next to amber at a glance, and near red if pushed further.
- **Dropped: blue flame** (hot 0.86 0.94 1.0; warm 0.18 0.45 1.0). Built and recorded; Preston, 2026-11-13: "Only thing
  need changing is the color theme blue doesnt fit it at all". The rest of the slice stays as built.
- Kept out: red (enemies), lime (gorilla), amber (rhino cracks), purple (hippo), copper with amber sparks (pangolin).

**Slag must not look like the hippo's toxic lake.** The lake is a liquid. Slag is crusted rock: matte plates, seams
that narrow and dim as it cools, a crust rim pushed up at the edge, a dark scorch halo, and three crust lumps with real
height sitting on it. No ripples, no shine, no flow.

**Falcon sky barrage overlap: retired (2026-11-13).** This section used to flag the falcon's sky barrage (small darts at
random spots in a 3.5 m area) as an overlap with Eruption. The kit-design lane reports that Preston approved the falcon
rework on 2026-11-13: sky barrage is gone, and the falcon's ult is now Seeding Run, a wing projection sweeping a long
line, with no ring and no darts. The shared 3.5 m radius and the "white-hot" clash no longer apply. See
`docs/plan/moba-kits.md` (Falcon).

**Stacks are never a gauge** (the hippo owns fill and spend). They glow as a cast winds up and go out as each one fires.
**Cooldown stacks: yes** (Preston, via the kit-design lane, 2026-11-13, "Yes, with your picks" on the bison kit, draft
2). Each stack belongs to one ability and goes dark while that ability cools down. The 3D lane checked the registered
`bison.glb`: no emissive anywhere, so the stacks are painted metal. The effects draw a lit cap at each stack socket while
its ability is ready and take it away on cooldown; "dark" is the painted metal. The stacks stand only about 9 cm above
the hump, and the socket x and z are the centre of the stack's bounding box, not its top face, so the caps are sized in
the engine.

**Kit approved** (same answer): the bison kit is draft 2 (Ares + Vulcan), in `docs/plan/moba-kits.md` (Frontline,
"Bison"). It is a catcher tank on the steam locomotive rig. War Whistle's buff stays inside Eruption. Slag stays short
and small, to keep it apart from the hippo's toxic puddle (the 4.5 s placeholder fits). Names and numbers are still
proposals. The game feel lane (`local_09448b26`) builds `bison_kit.gd` to the contracts below. Per Preston, the bison
joins BOT_ROSTER only after its kit exists and passes its checks.

**Eruption** (slot 2): see "The slice".

**Coupling Chain** (slot 1, built: see "The slice: Coupling Chain"). Ares' structure, ours: a real chain mesh (links with height) from `muzzle_purge` that
is there within a frame; a heat pulse runs out along it when it couples and on each refire; the coupled enemy gets a
small hot collar. Watch the chase camera: the chain leaves from under the hump, so from behind it can read end-on (the
pangolin's rail streak did). The links' height and the running pulse are what carry it.

**Plow** (slot 3, built: see "The slice: Plow"): the stacks flare on the `flare` event (0.40); scorch on the floor along the sweep; rhino dust, used as
is, thrown sideways.

**Freight** (ult, built: see "The slice: Freight"): Brace: chains out to every enemy (the Coupling Chain look, several at once), stamp dust on
`stamp_l` and `stamp_r`. Haul: the stacks pour a low fire and drop slag on `slag` (0.15, 0.75 of each loop), patches
that merge into a burning track behind it. Built from shapes with height (crust lumps, chain), never a flat travelling
strip.

## The slice: Eruption (built 2026-11-13, launcher only)

Files, all new: `scripts/moba3d/bison_fx.gd` (the observer), `shaders/bison_bomb.gdshader`, `bison_trail.gdshader`,
`bison_burst.gdshader`, `bison_glow.gdshader`, `bison_slag.gdshader`; dust is `shaders/rhino_dust.gdshader` used as is.
Launcher: `scenes/moba3d/bison_fx_arena.tscn` (the main match plus one node, `scripts/moba3d/bison_fx_standin.gd`, which
takes the player's machine, freezes its kit, puts the registered bison body on it and adds a stub kit; keys: 2 Eruption,
P switch palette). `arena_play.tscn` is unchanged.

**Order, per cast, on the body's clip events:**

| Event (s into the clip) | What shows |
| --- | --- |
| gather 0.04 | The four stack mouths heat up: a small soft glow on each, building over 0.3 s |
| roar 0.32 | Two short pale steam jets from the steam vents behind the stacks |
| erupt_fl 0.38, erupt_rr 0.48, erupt_fr 0.58, erupt_rl 0.68 | At that stack: its glow goes out, a 0.16 s muzzle burst (stretched up), a soot puff; a bomb leaves |
| erupt + 0 to 0.72 | The bomb (dark crust, hot seams, spinning) climbs on a thick hot tube trail and falls on a thin one; the trail is a tube rebuilt each frame, so it has height from every camera |
| erupt + 0.42 to 0.72 | The floor under the landing point heats |
| erupt + 0.72 (1.10, 1.20, 1.30, 1.40 s) | Landing: a 0.27 s spiky burst, a floor glow that cools in 0.45 s, 7 molten chunks that fly and fall and cool, two basalt dust puffs, and a slag patch |
| landing + 4.5 s | The slag has cooled to dark crust and fades out |

**Placeholder numbers, for the kit to match later:** bombs land 3.5 m from the bison (`RING_R`, or the kit's
`eruption_radius`), one at each diagonal corner, in the order the stacks fire; flight 0.72 s; arc 3.2 m above the line;
slag 4.5 s (`SLAG_TIME`, or the kit's `slag_time`); scorch 1.9 m across, crusted slag about 1.15 m.

**Contract proposed to the game feel lane** (copied from the pangolin's pattern; the effects never call the kit):
- `signal cue(name)`: "eruption" at the cast (optional; the clip events carry the timing).
- Fields read if present: `eruption_radius: float`, `slag_time: float`, `eruption_points: Array` (four Vector3, if the
  kit aims the bombs itself, in erupt order fl, rr, fr, rl).
- Body events from `MechModel3D.event` on clip "Eruption", as above.

**Recorded:** `D:/dev/_scratch/bison-fx/rec/bison-eruption-white-vs-magma.mp4` (also in the shared notes folder): two
casts at full speed, one at quarter speed, at the game camera, A and B side by side, then the slow cast zoomed.
Recorder: `rec/record.sh <white|magma> [--shots]` with `eruption_rec.gd`; compose: `rec/compose.sh`.

## The slice: Coupling Chain (built 2026-11-13, launcher only)

Files: `shaders/bison_chain.gdshader` (new); the chain section of `scripts/moba3d/bison_fx.gd`; launcher key 1 and the stub's
chain rules in `bison_fx_standin.gd`. No kit, body or shared script edited.

**What it is:**
- **Links:** real iron links, a MultiMesh of tori (0.115 m outer, 0.06 m inner, stretched 1.35 along the chain, so 0.31 m
  long), alternating 90 degrees and 0.22 m apart so they interlock. They are drawn from the `muzzle_purge` socket (Bone_026)
  to the target. Each link carries its own heat in INSTANCE_CUSTOM.r.
- **Look:** dark lit iron, metallic 0.55. Heat glows magma from the rim inward. Only the pulse core goes above HDR 1.05.
- **Collar:** a ring of 14 links snapped round the target at 0.75 m up, 0.55 m across (placeholders for the target's
  waist).

**Order:**

| When | What shows |
| --- | --- |
| Chain_Throw windup 0.04 | A small glow at `muzzle_purge`, 0.3 s |
| fire 0.283, cue `chain_fire` | A muzzle burst; the chain reaches out in 0.09 s, straight and hot (heat 0.6) |
| cue `chain_couple` (the stub sends it 0.09 s after fire) | A burst at the target; the collar snaps in from 1.6x to 1x its size in 0.1 s; the chain drops into a 0.3 m sag with a short decaying wobble and cools to a dim red-hot rest (0.32) over 0.5 s; one heat pulse runs muzzle to target in 0.38 s and flashes the collar when it arrives |
| a refire while coupled (another `chain_fire` at the same target) | A new heat pulse runs out along the held chain, 0.38 s, and flashes the collar again |
| cue `chain_miss` | The chain reaches `chain_end` and pulls back to the muzzle in 0.18 s |
| cue `chain_break` | The chain drops (the sag grows by 1.4 m), and the chain and collar shrink away in 0.3 s |

**End-on read from behind:** the coupled chain's sag and the links' thickness give it height from the chase camera. A miss
straight ahead does read end-on: a short vertical line from the bison toward the horizon, which is right for a miss.
At the game camera the first take's links (0.085 m) read like a necklace; the take shown uses the thicker links above.

**Contract proposed to the game feel lane** (sent to them directly; the effects never call the kit):
- `signal cue(name)`:
  - `"chain_fire"` at the Chain_Throw `fire` event. A fire at a target already coupled is a refire.
  - `"chain_couple"` when the chain catches `chain_target`; `"chain_miss"` when it catches nothing.
  - `"chain_break"` when `chain_target`'s chain ends (null `chain_target`: every chain ends).
- Fields read when a cue fires: `chain_target: Node3D` (null on a miss), `chain_end: Vector3` (where a miss reaches).
- Several chains at once are supported (one per target), for Freight's Brace.
- Taut at its length (2026-11-14, from the game feel lane's slice 2: the chain is 9 m and tows past that): the coupled
  chain's sag goes to nothing over the last 1.5 m, and it runs warmer under the strain. It reads `chain_length` from the
  kit if present (else 9.0). Not recorded yet: no launcher take moves a coupled target that far.
- Body events from `MechModel3D.event` on clip "Chain_Throw": only `windup` is used.
- The stub's guesses, for the kit to replace: couple 0.09 s after fire, range 9 m, 35 degree cone, break 3.0 s after the
  last couple or refire.

**Recorded:** `D:/dev/_scratch/bison-fx/rec/bison-coupling-chain.mp4` (also in the shared notes folder), at the game
camera, magma. A red minion stands 6 m ahead and 2 m right. The take shows a throw and couple, a refire 1.2 s later, the
hold until the break, a miss, then a couple and refire at quarter speed. Recorder: `rec/chain_record.sh [--shots]` with
`chain_rec.gd`. Logged order per cast: fire, couple 0.10 s later (one 60 fps frame of rounding), pulse, break 3.0 s after
the refire.

## The slice: Plow (built 2026-11-13, launcher only)

Files: `shaders/bison_plow.gdshader` and `shaders/bison_scorch.gdshader` (new); the Plow section of
`scripts/moba3d/bison_fx.gd`; launcher key 3 in `bison_fx_standin.gd`. No kit, body or shared script edited.

**No god reference for the sweep itself.** The kit takes Plow from the animal: the hump-powered head sweep bison use to
plow snow. Its pieces reuse structure already measured:
- the stack flare: Vulcan's Earthshaker exhaust;
- the floor heating: Earthshaker's reddening floor;
- the short dark scorch with hot spots: Magma Bomb.

The swing itself was measured on the registered body:

**The head's sweep, measured** (`muzzle_purge` sampled every 0.04 s through `Bison_Plow` on `art/arena_models/bison.glb`,
model space, angle 0 = straight ahead, + = the bison's left):

| Clip time | Head angle | Head height | What it is |
| --- | --- | --- | --- |
| 0.00 to 0.28 s | 0 to 32 degrees right | 0.46 to 0.26 m | wind-up to the right, dropping |
| 0.32 to 0.48 s | 30 right to 10 left, fastest about 310 degrees a second | 0.18 to 0.19 m (lowest) | the scoop through the ground; `flare` 0.40 and `hit` 0.467 fall here |
| 0.52 to 0.64 s | 22 to 41 left | 0.22 to 0.56 m | follow-through, rising; `throw` 0.62 is the end of the swing |
| 0.68 to 1.16 s | back to 0 | up to 0.75 m, then down | recovery |

So the sweep runs right to left, and Plow throws enemies to the bison's left. The kit should throw that way too.

**What it is:**
- The wave follows the real head, not a canned curve. Each frame, the head's angle is read off the socket and scaled by
  1.6 onto an arc 2.4 m from the bison. While the head moves left faster than 120 degrees a second, the arc grows
  (logged: 42 to 45 degrees right, then 64 degrees left).
- **The wave:** a standing wall of burning earth, built as a strip with height. Each column rises in 0.03 s where the
  head passes and sinks and darkens over 0.45 s; both ends are faded. It is a hot base, a deep magma body and sooty
  tongue tips, mixed rather than added: added orange over the blue arena floor washed out to peach in the first take.
- Molten clods (the bomb crust) and basalt dust are thrown along the sweep as the head passes.
- **The scorch:** a band of charred, furrowed ground under the arc (1.5 to 3.0 m out), with embers that cool in about
  1 s; gone by 2.4 s. It is shorter and flatter than slag, so slag stays the only lasting mark, and nothing liquid
  (the hippo).
- **The stacks:** they heat on `windup` (all four, about 0.45 s) and flare on `flare`: a short burst stretched up and a
  soot puff each.
- **Throw:** two dust puffs thrown sideways off the far end of the arc. A hit target gets a burst and four molten clods
  thrown to the bison's left.
- **Launcher only:** the stand-in shoves each hit target 2.5 m to the bison's left over 0.32 s, with a hop, so the throw
  reads in the take. That is the kit's job, not the effects'.

**Contract proposed to the game feel lane** (the effects never call the kit):
- `signal cue(name)`: `"plow"` at the cast (optional, logged only); `"plow_hit"` at the Plow `hit` event (0.467), with
  the field `plow_targets: Array` (Node3D) set first.
- Field read if present: `plow_radius` (m, placeholder 2.4).
- The kit's hit area (game feel lane, `bison_kit.gd` slice 2, 2026-11-14): `plow_reach` 3.0 m from the bison's centre to
  the target's edge (MatchTeams.edge_distance), so a hit target's edge is inside the scorch band's outer edge; a
  140 degree arc, not skewed. It also exposes `chain_length` 9.0, which the taut chain reads.
- Body events from `MechModel3D.event` on clip "Plow": `windup`, `flare` and `throw` are used; `step` is left for
  footfall dust.
- The throw direction, measured: the bison's left. A coupled target hit by Plow is thrown to the far end of its chain
  (kit). The chain effect follows its target wherever the kit moves it, up to 21 m of links.

**Recorded:** `D:/dev/_scratch/bison-fx/rec/bison-plow.mp4` (also in the shared notes folder), at the game camera, magma.
A red minion stands 2.3 m ahead, inside the arc, and is put back before each cast. The take is two casts at full speed,
then one at quarter speed. Recorder: `rec/plow_record.sh [--shots]` with `plow_rec.gd`; the head sampler is
`rec/plow_measure.gd`.

## The slice: Freight (built 2026-11-14, launcher only)

Files: the Freight section of `scripts/moba3d/bison_fx.gd`; launcher key 4 in `bison_fx_standin.gd` (again while hauling:
a snap). No new shader: it reuses the chain, the bomb crust, slag, bursts and basalt dust. No kit, body or shared script
edited.

**References:** nothing new was measured. The chains are the Coupling Chain (Ares' Shackles, measured for that slice),
several at once. The stack fire is Earthshaker's exhaust, and the track is Magma Bomb's crust and slag, made smaller.

**What it is, on the clip events** (`Freight_Brace` gather 0.04, chains_out 0.26, stamp_l 0.46, stamp_r 0.56, braced
0.75; logged on time in the take):
- **gather:** all four stacks and the rear coupler heat.
- **chains_out:** a Coupling Chain from the rear coupler to every target in `freight_targets`. Each couples 0.09 s later
  on its own (logged 0.10 s), with no further cue.
- **stamp_l, stamp_r:** basalt dust thrown low and outward off each front foot.
- **braced:** the whistle. Steam comes from both vents (the Eruption roar) and every stack flares.
- **The haul** (`Freight_Haul`, a 1.20 s held loop):
  - All four stacks burn, with a short burst every 0.11 s, and the rear stacks smoke.
  - On the slag beats, 0.15 and 0.75 s into each loop, a molten glob pours off a rear stack, alternating sides. A held
    loop fires its events on the first pass only, so the beats are read off the clip position.
  - The glob arcs back and lands as a burst, a puff, two clods and a 1.2 m slag patch (Eruption's are 1.9 m), which
    lasts the same 4.5 s. The take logs a landing every 0.60 s.
  - At the launcher's 0.52 m/s the patches land about 0.3 m apart, so they overlap into a short burning track, about
    2.3 m long behind the bison. Short and small, as asked.
- **End:** `chain_break` with a null target drops every chain at once. `freight_snap` (the hauler stunned or knocked up)
  bursts each coupled chain at its middle and drops it.
- **The coupler:** the bison has no socket at its rear yet. One is taken from the model's bounds at bind time: centred,
  40% up, 8 cm inside the rear face, bound to the nearest bone. It resolves at (0, 0.68, -1.35) on Bone_002. A
  `coupler_rear` socket was proposed to the 3D lane. If it gives one (a bone and a model-space point, like the stacks),
  it replaces the bounds guess in one line of `_bind_sockets`.

**Contract proposed to the game feel lane** (the effects never call the kit):
- `signal cue(name)`:
  - `"freight"` at the cast (optional, logged only);
  - `"freight_chains"` at the Freight_Brace `chains_out` event (0.26), with the field `freight_targets: Array` (Node3D)
    set first;
  - `"chain_break"` with `chain_target = null` when the haul ends (drops every chain);
  - `"freight_snap"` when the haul is broken (a stun or knock-up on the bison).
- Body: the haul is read off the body, `action == "Freight_Haul"` (started with `play_hold`), and its clip position.
  Stopping the action (`stop_action`) ends the haul's fire and smoke.
- The towing, the haul speed and any damage are the kit's. The launcher's numbers are stand-ins: 0.518 m/s for 4 s,
  targets 2.6 m behind and 1.7 m apart.
- The track is look only and lands near the glob's arc, not at set points. The game feel lane (2026-11-14): it stays
  look only for now. If the kit gives it damage, the kit will set `slag_spots: Array` (Vector3) before a `"slag"` cue,
  and the effects will land the globs there (not built; that lane says before it lands).

**Recorded:** `D:/dev/_scratch/bison-fx/rec/bison-freight.mp4` (also in the shared notes folder), at the game camera,
magma, with the bison turned to face screen-left so the haul runs across the frame. Three red minions stand behind and
beside it. Cast 1: the brace, a 4 s haul, the chains drop. Cast 2: the brace at quarter speed, then a snap 2 s into the
haul. Recorder: `rec/freight_record.sh [--shots]` with `freight_rec.gd`.

## The slice: footfall dust (built 2026-11-14, launcher only)

Files: the footfall section of `scripts/moba3d/bison_fx.gd`; launcher key H (a heavy hit) in `bison_fx_standin.gd`.
No new shader: it uses the rhino dust, as is. No kit, body or shared script edited.

**How the steps are read.** The bison's clips carry their footfalls as `step` events: Walk has four; Trot, Walk_Back,
Strafe_Left and Strafe_Right have two each. The times match the r5 export's `bison.events.json`. But neither body
signal fires for them:
- the body fires `event` for actions only, not for locomotion loops;
- its `step` signal reads a `steps` row the bison does not have.

So the effect follows the playing locomotion loop by its clip position and fires on each step time it passes, wrap
included. If the body's `step` signal ever fires with a hoof name (fl, fr, rl, rr), the effect uses that instead.

**Which hoof lands, measured** (`rec/feet_measure.gd`). The hoof bones are the lowest rest bone in each quadrant:
fl Bone_037, fr Bone_031, rl Bone_015, rr Bone_010. The table is their landing times on the registered r5 body:

| Clip | Step events | Hooves landing |
| --- | --- | --- |
| Walk (0.80 s) | 0.0, 0.176, 0.40, 0.576 | rear-left, front-left, rear-right, front-right (a four-beat walk) |
| Trot (0.43 s) | 0.0, 0.22 | front-left with rear-right, then front-right with rear-left |
| Walk_Back (0.47 s) | 0.0, 0.23 | the same diagonal pairs |
| Strafe_Left, Strafe_Right (0.43 s) | 0.0, 0.22 | the same diagonal pairs |
| Hit_Heavy `replant` (0.34) | | front-left lands at 0.32, front-right at 0.36 |

If the 3D lane re-times a clip, this table needs measuring again.

**What it is:**
- A low puff of the arena dust (the rhino's and gorilla's colour) under each landing hoof, pushed out from the body.
  It is sized to the gorilla's foot puff: 0.85 m at strength 0.65; the trot's is a quarter larger.
- Puffs stay where they rise, so a moving bison leaves them behind. Nothing drifts or lingers past 0.45 s.
- **Hit_Heavy `replant`:** Freight's stamp dust under both front hooves.
- **Changed with it:** Freight's stamps now sit on the measured hooves rather than a bounds guess, in the same lighter
  dust, a little larger. The bison's darker basalt was nearly invisible on the blue floor in the first footfall
  take. Freight's video was recorded before this change.

**Proposal for the 3D lane.** A `steps` row with hoof names would let the body's own `step` signal carry this, for sound
too. The table above gives the names.

**Recorded:** `D:/dev/_scratch/bison-fx/rec/bison-footfalls.mp4` (also in the shared notes folder), at the game camera,
magma. The bison walks screen-left, trots back, then, held facing left, strafes away from and toward the camera and
backs up. Two heavy hits follow, the second at quarter speed. The movement goes through the player's `move_override`, so
the body picks its own clips. Recorder: `rec/feet_record.sh [--shots]` with `feet_rec.gd`.

## The slice: cooldown stacks (built 2026-11-14, launcher only)

Files: the cooldown section of `scripts/moba3d/bison_fx.gd`; the launcher's casts now set `player.cooldowns` in
`bison_fx_standin.gd`. No new shader: the caps use the glow shader. No kit, body or shared script edited.

**What it is:** each stack wears a lit cap while its ability is ready and goes dark while that ability cools down.
- The cap is a small billboard glow, 0.26 m, over the stack's mouth: 5 cm above the socket, since the socket is the box
  centre of a 9 cm stack. It is lit at a steady 0.75 in the palette's hot colour.
- On cooldown it fades out in about 0.1 s. Coming back ready, it pulses bright for a quarter second, then settles.
- On or off only, never a gauge (the hippo owns fill-and-spend). Dead or hidden, the caps are off.
- At the game camera the caps read as small hot points on the stack tops; side-on, the two far stacks sit behind the
  near two. If Preston wants them louder, the size and glow are two constants (`CAP_SIZE`, `CAP_GLOW`).

**Source, no cue needed** (game feel lane, 2026-11-13; `bison_kit.gd` slice 1 has it, 2026-11-14): a stack is lit
while `float(machine.cooldowns.get(slot, 0.0)) <= 0.0`, with the slot from the kit's `stack_slot` (`{"fl": "1", "fr":
"2", "rl": "3", "rr": "4"}`, placeholder order). With no kit field, the effect uses the same placeholder. With no
director, the dict stays empty and every stack reads ready.

**Launcher only:** each cast sets its slot to `MatchRules.cooldown("bison", slot)` in `player.cooldowns`, as the
director would, and the player counts it down itself. Casting again still works, and it restarts the timer.

**Recorded:** `D:/dev/_scratch/bison-fx/rec/bison-cooldown-stacks.mp4` (also in the shared notes folder), at the game
camera, magma, side-on. The take, as logged:
- all four caps lit;
- all four slots on staggered cooldowns (1.0 to 3.4 s), so they relight one by one (logged 2.40, 3.22, 4.02, 4.82);
- a real Eruption (slot 2, fr dark) and a real Plow (slot 3, rl dark);
- every cooldown cleared, and both relight.

Recorder: `rec/caps_record.sh [--shots]` with `caps_rec.gd`.

## In the match: the installer (2026-11-14)

`scripts/moba3d/bison_fx_installer.gd` (new) attaches `bison_fx.gd` under every `BisonKit` in the scene, named
`BisonFx`, as `gorilla_fx_installer.gd` does for the gorilla.
- **Why not the kit's own hook:** the kit's `fx_on` stays false. The kit would only hang the effects at its first cast,
  so the footfall dust and the cooldown stacks would wait for one. The installer attaches them as soon as the body is
  on.
- The effects sit under the kit, so a swap to another machine frees them with it.
- It sets the kit's `_fx_hung`, so the kit never hangs a second copy if `fx_on` is turned on later.
- It stays out of the bison fx launcher, which runs its own stand-in.

**The kit's haul slag** (`bison_kit.gd`, game feel lane): the kit drops a burning patch behind the hauler every 0.6 s.
It sets `slag_spots` before each `"slag"` cue. With such a kit, the effect pours each molten glob onto that spot, 0.3 s
from a rear stack, and drops none on the clip's beats. With the launcher's stub, the beats still drive the globs.

**Status: on in the real match (2026-11-14).** On Preston's direct "Yes, turn on", the game feel lane added the
`BisonFxInstaller` node (ext_resource `5_bisonfx`) to `scenes/moba3d/arena_play.tscn`, after `RhinoFxInstaller`. Its
checks: installer check-only clean, the scene loads 600 frames with no errors, match_check 67 pass, 0 fail, and its
bison probe passes, including a check that `BisonFx` hangs under the kit after `set_machine("bison")`. To turn the
effects off, remove that node and its ext_resource.

How it got there: Preston's "also turn on" (2026-11-14) first came relayed through the bison 3D lane. The edit that puts the
installer node into `scenes/moba3d/arena_play.tscn` was refused by this session's permission check, because the
go-ahead was relayed rather than typed here. That edit is two lines, an `ext_resource` and a `BisonFxInstaller` node,
and waits on Preston's direct yes. `arena_play.tscn` is the game feel lane's file: it is asking him, and on his yes it
adds the two lines itself.

**Proved in the real match without it:** `rec/match_rec.gd` loads `arena_play.tscn`, adds the installer at runtime,
switches to the bison and runs the kit's own `eruption()`, `chain()`, `plow()` and `freight()`. The installer hung the
effects under the kit. Every kit cue drove them: eruption, the four bomb landings, chain fire and couple, plow and its
hit, freight chains to three minions, and seven slag spots, each glob landing 0.30 s after its cue. The chains then
dropped at the haul's end. Video: `D:/dev/_scratch/bison-fx/rec/bison-in-match.mp4` (also in the shared notes folder).

**A chain carried into Freight, by design.** In that take, the slot-1 chain coupled at 5.80 s stayed up until the
haul's end at 13.18 s, past its 3.0 s hold. A rerun at a fixed 60 fps logged the kit's targets on every cue. The
chained minion was first in `freight_targets` at `freight_chains`, 2.88 s after the couple and 0.12 s before the chain's
own break. Freight takes in any enemy already on a chain and holds every car to the haul's end (game feel lane), so
this is the kit working as designed.

**Checks:** check-only clean on `bison_fx.gd`, `bison_fx_installer.gd` and `match_rec.gd`. match_check's first run was
63 pass, 4 fail, all on the flaky tower checks; the rerun was 67 pass, 0 fail.

## The Whistle Stop refine (2026-11-14): what changes here
Preston approved a refined bison kit ("Whistle Stop"; `docs/plan/moba-kits.md`, Bison, and `kit-design-2026-11-11.md`,
"Bison refine draft"). For this lane:
- **Eruption's bombs and slag ring retire.** They stay in `bison_fx.gd` only until the kit stops sending `bomb_land`;
  nothing new wires them into a match. Eruption's vent fire is kept as the fire at the base of the steam columns.
- **Kept as built:** Coupling Chain (chain from `muzzle_purge`, heat pulse, hot collar, taut chain), Plow, footfall dust,
  the cooldown stacks, Freight's slag track (small, short, beside the hippo's puddles), magma orange.
- **New:** Whistle Stop's steam columns and scald; the Haul (slot 1 recast) with its chuff and buffer slam; Freight as a
  line chain that couples a train nose to tail, then the pile-up when it brakes; all four stack caps blasting together
  on Whistle Stop.
- **The kit is rebuilt (game feel lane, 2026-11-14, Preston: "Yes, rebuild it"),** with the names proposed here. New cues:
  `whistle` (time the columns off the Whistle clip's inhale, blast and plume_end), `scald` at the blast
  (`scald_targets`; `whistle_radius` 9, `scald_radius` 3), `haul` and `buffer_slam` (then `chain_break`), `pile_up`
  (then one null `chain_break`). Fields `hauling`, `haul_kind` ("haul" or "freight") and `steam` (0 to 1 over 2 s). Both
  hauls play the r6 `Haul` clip. `freight_targets` is nose to tail, and `chain_end` is the line's far end (12 m, cut
  short at walls). Gone: `eruption`, `rally`, `bomb_land` and their fields, so the bombs no longer show.
- **Checked with the rebuilt kit in the real match** (`rec/match_rec.gd`, 2026-11-14): no script errors. Every new cue
  arrives, and the effects ignore the ones not yet built. The slot-1 Haul and Freight's haul both read as hauls
  (6.18 to 7.70 s, and 11.27 to 15.28 s), with `steam` 0.375 midway through the first. The chain, Plow, the slag globs
  and the chain breaks all fire as before. Still built for the old kit: Freight chains each car to the bison, not nose
  to tail, until item 5.
- **The rule bent on purpose:** the effects rule is small, short flashes. Whistle Stop's columns must be "seen across
  the map", so they are the one tall effect: about 1.5 s up, then gone, no lingering cloud.

## The slice: Whistle Stop (built 2026-11-17, Preston: "Yes, read and start")
Files: the WHISTLE STOP section of `scripts/moba3d/bison_fx.gd`; new `shaders/bison_ring.gdshader` (a thin floor ring,
additive, render_priority 3); launcher key 2 is now Whistle Stop (`bison_fx_standin.gd`, which sends "scald" on the
clip's blast). No kit, body or shared file edited.

Timed off the Whistle clip (1.3 s), with the structure of the Gemini sheet (ripple, base flare, columns, ground steam
ring, call ring, fade):
- **inhale (0.05):** the four stack mouths heat, the steam vents shriek, and a short orange ripple runs out under the bison.
- **blast (0.32):** every stack flashes and all four caps blast together, the cooling ones included. Each stack then
  shoots a column of steam straight up until plume_end (0.95), with flame bursting at its base. The columns lean
  slightly out from the hump's centre, so four read at height rather than one pillar. They widen as they climb to
  about 7 m, which runs off the top of the play camera. They are gone by about 1.7 s.
- **scald (the kit's cue at the blast):** a low ring of steam rolls out to `scald_radius` (3 m) over a hot floor ring,
  and each scalded enemy gets a flash and a hiss.
- **The ally call:** one faint, thin ring runs out to `whistle_radius` (9 m).
- The columns are the kit's one tall effect, on purpose ("seen across the map"). The rest stays small and short.

**Recorded:** `D:/dev/_scratch/bison-fx/rec/bison-whistle-stop.mp4` (also in the shared notes folder). It is the main
match with the real kit at the game camera: a standing cast, then a walking one, with three minions inside the scald
radius and one outside. The log shows "scald 3" on both casts. Recorder: `rec/whistle_record.sh [--shots]` with
`whistle_rec.gd`. A first take came out black, because the display had slept; the re-take was clean.
**Known:** the columns are built of stacked puffs and look slightly beaded up close. That reads as a locomotive's
chuff, and is cheap to smooth (a shorter COLUMN_TICK) if Preston wants one smooth plume.

## The slag fix: no more "poop" (2026-11-17)
Preston, relayed by the bison 3D lane: "the lava balls look like poop when towing". Round globs falling from behind
the rump read as dung. Now no ball falls. Each slag spot is a flat streak of cracked, glowing slag that appears on
the floor at once, laid along the haul (0.8 m by 1.76 m), with a low flash and a short hiss of steam. It cools from
orange to black over the slag time. A rear stack still spits a small flash, alternating sides, to tie the spill to the
engine. The streaks line up into a short dashed track. Checked in the launcher's Freight take: a flat dark crack with
orange veins behind the bison, nothing round.

## The slice: Haul chuff and buffer slam (built 2026-11-18, Preston: "yep get in queue")
Files: the HAUL CHUFF AND BUFFER SLAM section of `scripts/moba3d/bison_fx.gd`. No kit, body or shared file edited.
- **Chuff:** the r6 Haul clip's chuff beats (0.092 and 0.312 of its 0.433 s loop) are read off the clip position. On
  each beat a diagonal pair of stacks (fl and rr, then fr and rl) coughs a short flame and a puff of steam that rises
  and trails off behind. The kit's steam sharpens it: bigger, slower, greyer puffs at the start, smaller, faster, whiter
  ones at full steam. The clip speeds up with the haul (rate 1.08 to 1.44 measured), so the chuffs quicken. The "haul"
  cue opens with one chuff from all four stacks.
- **Full steam:** the vents shriek once when steam reaches 1. Slot 1's haul (1.5 s) tops out at 0.75 steam, so it never
  fires there. In the take, Freight's haul ran 2.0 s and full steam landed on the same frame as the pile-up, so in
  practice it reads as the brakes at the pile-up. Cheap to drop if the kit keeps these timings.
- **Buffer slam:** a hot flash where the two backs meet and one on the slammed enemy, a short floor ring, low dust, and
  the brakes venting steam out of both rear stacks. The stun shows with the match's own gold stars (seen on the slammed
  minion), so nothing is added for it.
- **Freight** plays the same clip, so it chuffs the same way. The old Freight_Haul trudge keeps its steady burn.

**Recorded:** `D:/dev/_scratch/bison-fx/rec/haul_take.mp4` (in the shared notes folder as
`bison-haul-chuff-buffer-slam.mp4`): the main match with the real kit at the game camera. Slot 1 chains a minion,
hauls it and slams it, then Freight runs. Log: 9 chuffs on the 1.5 s haul; cues haul, buffer_slam, chain_break in
order; the slam names the minion; Freight 12 chuffs over 2.0 s, 4 slag spills, full steam with the pile-up. Recorder:
`rec/haul_record.sh [--shots]` with `haul_rec.gd`.
**Fixed after the first take:** the chuff puffs read faint at the game camera (about 25% bigger now), and the slam
flash sat at the coupler behind both bodies (moved to where the backs meet, plus one on the enemy).
**Not covered:** the launcher stand-in sends no haul or buffer_slam cues, so this slice shows only in the main match.
The chuff times are written into HAUL_CHUFFS; if the 3D lane's stronger Haul pass moves the chuff events, update them.

## What is next (ordered)
1. Done: magma orange, Coupling Chain, Plow, Freight (old kit), footfall dust and the replant, cooldown stacks.
2. Done: `bison_fx_installer.gd`, on in the real match since 2026-11-14.
3. Done, 2026-11-17: Whistle Stop (see "The slice: Whistle Stop"), and the slag spill fix.
4. Done, 2026-11-18: the Haul chuff and buffer slam (see its slice).
5. **Freight as a line.** One chain fired in a line; each car coupled to the one ahead, nose to tail; the chuff and slag
   track as now; the pile-up when it brakes (a flash where each pair of cars meets, a stun tell on each). Needs:
   `freight_targets` ordered nose to tail, and a `pile_up` cue.
6. Retire the bomb and slag-ring code once the kit's Eruption is gone.
7. A `steps` row with hoof names in the bison's body row (3D lane, proposed), so the body's `step` signal carries the
   footfalls for sound too.
8. **The Unreal port** (hub row 45, after pangolin effects at 44; approved 2026-11-18): new files only,
   `Source/MechMoba/BisonFx.h/.cpp` (a client tickable world subsystem, the HippoFx pattern), `Tools/make_bison_fx.py`,
   `/Game/Bison/Fx`, a launch flag inside BisonFx for the film runs (as pangolin's `-PangolinCometFxFilm`), a full Check
   Migration. Slice 1 is Whistle Stop and the slag streaks. Drafts go in `D:/dev/_scratch/bison-fx/ue-drafts/` until
   pangolin hands over the editor.
   Done 2026-11-18: Whistle Stop and the slag streaks filmed in Unreal and the full check passed. The look is not at
   Godot parity yet: the flash and rings wash toward white, and the slag shows as separate ovals. Frames, DLL hash, the
   three look fixes and what is still open are in `D:/dev/_scratch/bison-fx/ue-drafts/ROW45_PLAN.md` (Result). The
   lesson that carries over to every Unreal effect: the arena's auto exposure brightens unlit emissive about 9x, so
   cancel it with EyeAdaptationInverse, connected by first input and checked.
