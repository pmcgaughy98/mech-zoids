# The creature factory: 3D models as the source for every 2D sprite (Preston and Claude, 2026-10-12)

Preston: "we can use what you learned and how we made the gorilla in 3D as a foundation to mass manufacture our
creatures. That way we can fix the side angle issues and the consistency issues, and the poses."

## Why it works
One 3D model per machine is the single source of truth. Every sprite view and every animation frame is rendered from
it, so views cannot disagree (the problem with Codex's hand-drawn set and with AI rotations), the side view is as good
as the front, and poses come from the rig instead of being drawn eight times.

## The line, as built for the gorilla
1. **Design** from Preston's sprite and real-animal research (gorilla: `docs/reference/gorilla-posture-2026-10-12.md`).
2. **Build** in Blender from code (`tools/blender/build_ape_l_v2.py`): profile solids, plates, joints, a rig with
   named bones, clips. Every part rides one bone by name.
3. **Render for sprites** (`tools/blender/render_sprite_views.py`): eight views, one framing and scale, flat albedo,
   near side-on camera (10 degrees), eyes teal, joints grey, plus a part-ID pass for plate lines.
4. **Pixelize** (`tools/art/pixelize_render.py`): Preston's ramps and shade balance, near-black outline, plate lines,
   ground shadow (rules in `docs/reference/sprite-rules-legacy-2026-10-12.md`).
5. **Measure** against Preston's references (`tools/art/compare_views.py`, `tools/blender/score_ape_vs_sprite.py`)
   and fix the model, not the pixels.
6. **Import** into the game slots (`tools/art/import_views.py`), checked by `tools/debug/view_art_check.gd`.

## What it needs to scale to every creature
- **A shared part kit.** Lift the gorilla's builders (`profile_solid`, `limb_solid`, `plate`, `shell`, `disc`,
  `segment`, joints, pelvis, fists and feet) into one library, and give each creature a short build file of
  proportions, parts and colours. Animals that share a skeleton (cats, canines, birds, reptiles) share a rig.
- **Animation frames.** Render each clip (idle, walk, attack, hit, death) at a few frames per view: eight views by
  6 to 12 frames per clip. The rig already has five clips for the gorilla.
- **One check per creature**: the view art check, the outline and colour scores against Preston's picked sprite,
  and a posture checklist from the real animal.
- **Preston's role per creature**: pick or approve one master sprite (the look), approve the 3D shape from the eight
  sprite views, then the rest is automatic.

## Not decided
Frame counts per clip, whether field sprites (small, 32 to 64 px) come from the same renders at a smaller scale, and
which creature goes second.

## First product: the pangolin (`pangolin_m`), 2026-10-12
Preston: "let's test mass manufacturing with the first product; you choose the next type and colour." Chosen: the
pangolin, in the colours already proposed in `scripts/data/machines.gd` (ochre scales, madder trim, delft snout, teal
eyes): a different body plan from the gorilla (low, long, a heavy tail), built from overlapping plates (what the
pipeline renders best), and never used for a Zoid.

- Research (Wikipedia "Pangolin", WildAid): overlapping scales over body and tail like a pine cone, small pointed
  head, short legs, big curved front claws tucked under the feet when walking, a long heavy tail.
- `tools/blender/build_pangolin_m.py` reuses the gorilla's part kit by importing `build_ape_l_v2.py` with
  `MECH_KIT_IMPORT=1`: a dark arched core, scale rows generated around an elliptical cross-section with alternate rows
  offset, a bezier tail of tapering segments with scale plates, a profile-solid head and delft snout, short limbs with
  joint discs, front claws curled under. One build, no fixes: 4.2 m long, 1.41 m tall, 15,864 triangles, 177 parts.
- What the factory needed (now general): the kit import guard; per-creature palette files
  (`tools/art/palettes/<id>.json`: colour families by hue, ramps, extra shades; `PIXEL_PALETTE`); flat material colours
  for untextured models; eyes in their own material; `SPRITE_ORTHO` with the render resolution scaled to keep 640 px
  per 4.4 m, so every machine pixelizes at the same scale (sizes true between machines).
- v1 (`docs/art/2d/pangolin_m/v1/`, `compare_v1.png`): eight views, side 143x53 px, 21 to 30 colours; light +56 to +77,
  highlights 12-18% (Legacy band); near-black edges 46-48% (Legacy 9-23). Reads as a pangolin from every angle.
- Left for v2: the eyes are too small to show at sprite size; the tail scales stand up like spikes in the side view
  (a pangolin's lie flat); the claws are too small to read; the grey legs are plain (no plates) and pale; a rig and
  clips (the stance) after the shape is approved.

### Pangolin refinement, v2 to v5 (2026-10-12)
Preston: "great foundation, it works; refine it up like the gorilla; use the synthesis to do that as well."
- What each tool contributed: Firecrawl (Wikipedia "Pangolin" and "Giant pangolin"): claws bent under the foot pad
  when walking; the giant pangolin carries "most of its weight on its columnar rear legs" and walks "on the outside of
  the wrists" with the front paws curled; head-and-body 112-180 cm. Blender (headless, the kit): every build. The
  pixelizer and `sprite_quality.py`: the Legacy-band numbers each round. The gorilla's lessons (staggered stance,
  scales lying with the slope, parts buried inside thicker limbs) carried over directly.
- v2: tail and body scales follow their slope (v1's tail sign stood them up as spikes); eyes and claws big enough to
  read; thicker limbs; diagonal-gait stagger (0.12 m); columnar hind legs; front feet rolled onto their outer edge.
- v3: leaf-shaped body scales (taper 0.55), smaller and closer rows (0.19 m); tail scales longer so no dark bands;
  palette families can set their own darkness (`"gamma"`; grey 2.0).
- v4 and v5: the leg scales were inside the thicker limbs (a limb solid reaches 0.23-0.32 m out from its axis); moved
  just outside. 19,236 triangles, 1.65 by 4.20 by 1.45 m.
- v5 (`docs/art/2d/pangolin_m/v5/`, `compare_v5.png`): 22-33 colours, light +58 to +84, highlights 6-16%, clusters
  4.8-5.9, stray 9-11%. Near-black edges 43-65% (Legacy 9-23): the dark underside, next to fix. Imported into
  `art/machines/pangolin_m/views/`. No rig or clips yet.

### Pangolin v6 to v8, and a factory-wide edge fix (2026-10-12)
- Preston: "it doesn't have to have a cockpit window at its nose; they will look like mechanical weaponised animals."
  Design rule for every machine from here: no cockpits or canopies; weapons shown on the body.
- v6: the delft snout (it read as a glass canopy) is grey metal with madder nostril vents and two scale plates down its
  top. Weapons from its moves in `scripts/data/machines.gd`: Scale Shot as a launcher rack on each shoulder with three
  madder barrels; Scale Rake as madder scales down the last third of the tail ending in a flat madder blade. v7: bigger
  launchers; palette grey gamma back to 1.4. 19,908 triangles.
- v8, pixelizer (applies to every machine): plate lines only inside the silhouette, so the outer edge follows the
  light (every scale touching the top edge had ringed it near-black); undersides three shades down instead of the
  darkest. Pangolin near-black edges 43-65% to 28-46%, light +85 to +158. Gorilla re-pixelized from the same renders
  (v32): near-black edges 27-30% to 19-21%, inside the Legacy band (9-23%) for the first time.
- Installed: `art/machines/ape_l/views/` (v32), `art/machines/pangolin_m/views/` (v8). Pair sheet:
  `docs/art/2d/factory_pair_v8.png`.

### Pangolin v9 and v10 (2026-10-12)
- v9: scale rows wrapped further round the body (to 125 degrees from the top), a dark socket ring round each eye, a
  third row of head scales. The flanks still read bare: the new low scales sat inside the core's side wall (the
  placement ellipse ran inside the core's real surface there), the third buried-part bug of this machine.
- v10: the scale ring pushed 0.07 m out to the surface and wrapped to 140 degrees. The whole body reads scaled down to
  the belly line. 25,092 triangles. Light +84 to +156, highlights 7-18%, near-black edges 28-47%, 25-31 colours.
  Installed in `art/machines/pangolin_m/views/`; `docs/art/2d/pangolin_m/compare_v10.png`.
- Lesson for the kit: generated surface parts should be placed from the core's real surface (a ray cast or the
  profile outlines), not from a separate approximation of it; three of the pangolin's passes were parts buried inside.

## Pangolin v11 (2026-10-12): edge darkness into the Legacy band

- Measured first: the near-black edges (28-47% in v10, Legacy 9-23%) were the ochre and grey edges clamping to their
  bottom shades (2e1a04, 181f1c) on the side edges, plus the red trim's second shade (4a0e08).
- Pixelizer: a palette family can now set `"edge_floor"`, the lowest ramp index its edges may be pushed to. Side edges
  always respect it; undersides only when the render was lighter, so the deepest shadow under the body still anchors the
  sprite. Flooring every edge overshot to 0-1%. Palettes without the key (the gorilla) render exactly as before.
- `pangolin_m.json`: floor 1 for ochre, grey and delft, 2 for madder. Model unchanged, re-pixelized only.
- Result: near-black edges 6-21% (n is 6%, just under the band), colours 24-30, highlights 7-19%. Installed in
  `art/machines/pangolin_m/views/`. The sw and se cells report one off-palette pixel each.
- Still out of band: light from above on the three-quarter and front views (+130 to +149 vs Legacy +49 to +107).

## Pangolin v12 (2026-10-12): light from above into the Legacy band

- v11 lit the three-quarter and front views too strongly from above (+130 to +149 vs Legacy +49 to +107). The cause is
  material, not shading: bright ochre scales on top, dark grey legs underneath, and the top edge rim pushed the ochre
  into its brightest extra shade.
- Pixelizer: per-family `"top_rim"` (shades added on top edges, default 1) and `"under_drop"` (shades taken off
  undersides, default 3). Defaults reproduce the old rule, so the gorilla is unchanged.
- Three variants measured: (a) ochre `top_rim` 0; (b) `under_drop` 2 on all families; (c) both. (b) barely moved it,
  (c) undershot (n +14). (a) adopted.
- v12a: light +46 to +102 (n just under the band), near-black edges 9-23%, highlights 7-18%, colours 24-30. All four
  Legacy bands met on every measured view except n's light (46 vs 49). Installed in `art/machines/pangolin_m/views/`.

## Kit: surface placement by ray cast (2026-10-12, pangolin v13)

- New in `tools/blender/build_ape_l_v2.py`: `surface_hit(target, origin, direction)` returns where a ray meets a built
  part (point and outward normal, world space, BVH cached per part), and `on_surface(target, center, outward,
  standoff)` moves a placement onto that real surface and `standoff` off it, falling back to `center` on a miss.
  This is the kit fix for the buried-part lesson (pangolin v4, v9, v10).
- Pangolin v13 places every body scale with `on_surface(core, ..., 0.045)` aimed along the old ellipse normal.
  Same triangle count (25,092). Scales now sit flush on the shell and wrap further down the flanks, but the back reads
  lower and less domed than v12a, because the old inflated ellipse was adding height the shell does not have.
- Metrics v13: light +44 to +135, near-black edges 8-18%, cluster 3.9-4.1. The front view's light went back over band.
- Not installed: v12a stays in the game slots. Next if v13's flush look is wanted: raise the torso shell's top
  profile so the dome comes from the core, not from floating scales.

## Pangolin v14 (2026-10-12): the dome from the core

- The torso shell now carries the dome: side profile up to the back line itself (was 0.06 under it), front profile
  the old scale ellipse less the standoff (half-width 0.585, top 1.31). The scales stay flush via `on_surface`.
- The shoulder launchers are placed with `on_surface` too (standoff 0.14), so they sit on the scales over the new dome
  instead of inside it; the barrels follow the base height. Height 1.448 to 1.559 m, the launchers now top the
  silhouette. 25,120 triangles.
- Metrics: light +77 to +126 (s over band, n +16 well under), near-black edges 8-18%, highlights 3-18%, colours 24-30.
- Read by eye against v12a: rounder, fuller back with the pine-cone rows wrapping down the flanks, the Scale Shot racks
  read as weapons from the front. Installed in `art/machines/pangolin_m/views/`.
- Open: a light-grey speckle on the near legs in the s view (appeared in v13); n's light value.

## Pangolin v15 (2026-10-12): grey despeckle

- The light-grey mottle on the near legs in the s view came from the pixelizer, not the model: the render's leg face
  is smooth, but the grey ramp's gamma and histogram matching turn tiny value noise into flips between two shades.
- Pixelizer: a family with `"despeckle": true` has each lone pixel one shade off from a shade three of its four
  same-family neighbours share take that shade (before plate lines and edges). Set for the pangolin's grey only.
  Mottle mostly gone; stray pixels unchanged at 11-14% (Legacy 11-16%). Installed.
- Tried and dropped: madder `top_rim` 2 to lift n's light. n went +16 to +30 (still under +49) while ne went to +135.
  The light value per view follows which material forms the top and bottom edges in that view (ochre over grey from
  the front, madder tail and barrels on top from the back), so per-view gaps on s and n are left as measured.

## Pangolin v16 (2026-10-12): rig, walk, idle, stance

- `build_pangolin_m.py` now rigs the machine with the gorilla's bone names (body, head, upper_arm / forearm / hand for
  the front legs, thigh / shin / foot for the hind legs) plus `tail.0-2`, so the kit's `clip()` and the sprite
  renderer work unchanged. Parts are tagged by name prefix before the join; leg joints are recorded by `legs()`.
- Clips: `walk` (36 frames, lateral-sequence gait: LH, LF, RH, RF a quarter cycle apart, 70% duty, tail sways against
  the steps) and `idle` (48 frames, breathing, head turn, tail sway).
- Stance: written to `docs/art/3d/pangolin_m.stance` (`base=1;R_arm=34;L_arm=29;R_leg=37;L_leg=9`): near fore leg
  forward, near hind leg back, far pair the other way. `pangolin_round.sh` passes it as SPRITE_STANCE.
- v16 sprites: light +53 to +125 (n now in band), near-black 11-16%, highlights 8-20%. Installed.
- Walk check (`walk_e.gif`, nine frames, e view): the gait reads, but in some frames the hind feet float about
  2-3 px. Cause found by working the chain: the hand and foot bones point forward-down, so swinging a leg back or
  bending the wrist in swing pushes the claws below the floor and the grounding lifts the whole body. Fix next:
  counter-rotate hand and foot during stance so they stay level, fold the front wrist up (negative) in swing, and
  centre the front-leg sweep on the vertical under the shoulder (about 19 degrees back).

## Pangolin v17-v18 (2026-10-12): floating feet fixed with leg IK

- Measured with `foot_heights.py` (scratchpad; lowest point of each hand / foot vertex group per walk frame): v16's
  three lowest feet were up to 14.9 cm apart.
- v17 (fixed angles, sweep centred under each joint, hand and foot counter-rotated): 6.1 cm, and the hind feet barely
  lifted in swing (toe up drops the heel). Fixed angles cannot keep four feet on one floor when the legs are nearly
  straight at rest.
- v18: `ik2()` two-bone IK in the side plane. Each wrist / ankle follows a path, flat along the floor while planted
  (stride 0.24 m, body 4 cm lower so no leg runs out of reach, front path centred 8 cm back, hind 3 cm forward), an arc
  while stepping (8 cm front, 9 cm hind). Hands and feet stay level while planted; the hand curls up 15 deg in swing.
  The hind path sits 1.3 cm lower (measured offset of its contact geometry). No body roll.
- Result: planted feet within 1.5 cm through the cycle (1.9 cm at touch-down), clear steps of 8-10 cm. `walk_e.gif`
  reads as a planted walk. v18b stance sprites installed. Kit candidate: `ik2` belongs in the shared kit for the next
  quadruped.

## Product 3: pygmy hippo (2026-10-12), the first true mass-manufacture run

- Chosen from the four starters in `scripts/data/machines.gd` because it is a quadruped: it tests reuse of the whole
  line (kit, quadruped rig, renderer, pixelizer) with only a new body, palette and weapons. The shoebill (a new bird
  skeleton) is next.
- New shared tooling, in the project:
  - `tools/blender/quad_rig.py`: the pangolin's v18 rig lifted into a module. Part-name tagging, the rig with the
    gorilla's bone names plus tail bones, the lateral-sequence walk with `ik2` leg paths, idle, and the stance file.
    A machine supplies a config dict and calls `rig_and_clips()`.
  - `tools/art/creature_round.sh <id> <version> [ortho]`: build, render in stance, pixelize, measure, sheet.
  - `tools/art/creature_sheet.py`.
- Research (firecrawl: San Diego Zoo, Louisville Zoo, SDZG fact sheet): the back slopes forward, the head is rounder
  and narrower than the river hippo's on a longer neck, eyes on the sides, longer legs, four free toes with nails,
  tusk-like incisors and canines. Colours: Preston's Desert Dusk. `tools/art/palettes/hippo_m.json` carries the
  pangolin's edge lessons (edge_floor, despeckle, plum top_rim 0) from the start.
- Rounds: v1 built and rigged first try (big plates read flat, head a grey tapir). v2 six bands of smaller plates and
  a salmon waterline stripe, plates on the legs' real surface (but tipped plates read as pangolin scales). v3 flush
  hull panels, plum head, flank vents and teal running lights (the roster says faction shows in the eyes and running
  lights). v4 inset panels, tusks outside the lips.
- v4: 12,964 triangles, 3.96 x 1.61 x 1.65 m. Light +47 to +103, near-black edges 10-25% (se 25, just over),
  highlights 8-18%, colours 22-28. Colour clusters 6.0-7.3 px and stray pixels 6-8% stay calmer than Legacy
  (3.3-4.5, 11-16%): a smooth-skinned animal on big panels. Installed in `art/machines/hippo_m/views/`, all eight
  views clean (no off-palette pixels).
- Walk, first build: planted feet within 2.0 cm, steps of about 7 cm (`walk_e.gif`). The rig needed no tuning.

## Product 4: shoebill (2026-10-12), the first bird

- New shared rig: `tools/blender/bird_rig.py`, built on `quad_rig.py`'s IK and bone names (the wings ride
  upper_arm / forearm / hand, a bird's wing being its arm; the legs ride thigh / shin / foot, the shin ending at the
  ankle and the foot being the bare tarsus with the toes). Biped walk (feet alternate, 62% duty, 40 frames, slow as
  the real bird), ankle path by IK, tarsus held at its rest angle while planted so the long toes stay flat. Idle is
  statue-like. Stance: near foot forward.
- Research (firecrawl: Wikipedia, Dallas World Aquarium): 1.1-1.4 m, head large for the body, neck shorter and thicker
  than a heron's, huge bulbous bill with a keeled upper mandible ending in a hooked nail and cutting edges, long dark
  legs, very large feet, broad wings, blue-grey with darker slate flight feathers, elongated breast feathers, rounded
  tail. Built about 1.8x life size. Colours: Preston's Blue Hour Cool. Weapons: the bill (Bill Clamp), a lens under
  the nail (Stillwater Lance), gold leading edges on the wings (Wing Buffet).
- v1 built, rigged and walking first try (8,374 triangles). v2: bill deeper and as wide as the head, primaries stacked
  tight and ending at the tail, thinner legs, deep-blue neck, blue edge_floor 1 and top_rim 0.
- v2: light +65 to +120, near-black edges 11-14%, highlights 9-27% (e and se a little over 24), colours 27-29.
  Installed in `art/machines/shoebill_m/views/` (canvas 102x90). Walk: planted foot on the floor every frame, the
  stepping foot lifts only about 3.6 cm (could be higher).

## Product 5 proposal: the fossa (Claude, 2026-10-12, for Preston to approve or change)

Preston asked for a fifth starter in the role a wolf or big cat usually fills, but less mainstream. Proposal: the
fossa (Cryptoprocta ferox), Madagascar's top predator. Verified (Wikipedia, San Diego Zoo): a slender, cat-like body
with muscular limbs, a tail nearly as long as the body (65-70 cm on 70-80 cm), semi-retractable claws, and ankles so
flexible it climbs down trees head first and leaps tree to tree; the tail is lighter than the sides. It fills the
fast striker role, is unfamiliar to most players, and its reversible ankles and balancing tail give the machine
moves no cat or wolf has.
- Draft colours (away from the four starters and the well-known Zoids schemes): burnt copper main a8552f, graphite
  trim 26262c, bone accent e6d6b8 on the tail (the real tail is lighter than the sides), teal eyes.
- Draft weapons: Hook Claws (melee, the semi-retractable claw blades); Tail Rail (beam, a rail gun along the long
  tail, fired with the tail arched over the back); Canopy Drop (melee finisher, a leap and a head-first drop, the
  swivel ankles turning the hind feet to brace the landing).
- Draft stats: hp 150, ep 55, ep_regen 11, speed 36 (fastest starter), defense 16. Untested.
- Build: quad_rig.py with a longer tail chain (four bones) and a crouched, low stance.

## Product 5: red kangaroo (2026-10-12), draft for Preston

- Preston turned down the fossa ("not canine or feline") and asked for red in the same style. Chosen: the red kangaroo
  (Australian Museum, SDZG fact sheet, WWF): about 1.5 m tall, body to 1.4 m, a thick tail to 1 m used as a prop, a
  deer-like head with a long muzzle and large ears, males orange-red with a whitish underside, a black-and-white muzzle
  patch and a white stripe from mouth to ear, over 56 km/h. The fast striker role, never a Zoid, red by nature.
- `tools/blender/build_kangaroo_m.py`: its own hop rig on `quad_rig.make_rig` and `ik2` (both feet together: a
  crouch with the feet planted, then flight with the tail lifted; the body bone pivots at the hips). The hop is its
  `walk` clip. Draft weapons: Piston Kick, Pouch Mortar, Tail Spring. Palette `kangaroo_m.json`: red b83a2c, maroon,
  cream, warm grey, teal eyes.
- New kit helper `plate_on(target, name, mat, aim, outward, w, h, t, standoff, up)`: lays a plate flat on a part's real
  surface, its face along the surface normal and its height toward `up`. v1's hand-set rotations on the leaning body
  stood the plates up as shards.
- v1 mostly grey; v2 red armour (body, thighs, tail with maroon bands), plates via plate_on; v3 deeper red ramp, slimmer
  thighs. Installed in `art/machines/kangaroo_m/views/` (canvas 150x106). Not yet in `scripts/data/machines.gd`.

## Factory pass, then individual refine pass (Preston, 2026-10-12)

The order from here: one factory pass that brings all five machines to the same standard, then one refine pass per
machine. Line-up of all five at game scale: `docs/art/2d/factory_lineup_v1.png`.

Side-view (e) numbers at the start (Legacy: cluster 3.3-4.5, stray 11-16%, light +49 to +107, highlight 3-24%,
near-black edges 9-23%):

| machine | colours | cluster | stray | light | highlight | near-black |
|---|---|---|---|---|---|---|
| gorilla | 27 | 5.3 | 9% | +96 | 13% | 21% |
| pangolin | 29 | 4.3 | 12% | +83 | 20% | 15% |
| pygmy hippo | 27 | 6.8 | 7% | +49 | 18% | 22% |
| shoebill | 28 | 5.7 | 9% | +65 | 27% | 14% |
| red kangaroo | 21 | 5.0 | 11% | +31 | 40% | 34% |

Factory pass (same treatment for every machine):
1. Detail parity: the gorilla carries baked panel texture the factory machines lack; bring an equivalent surface
   detail (panel lines, bolts, vents) through the kit so all five read at the same density.
2. One rig code path: the pangolin onto `quad_rig.py`; the hop into a shared module beside `bird_rig.py`.
3. One palette standard: edge_floor, top_rim and despeckle reviewed across all five palettes, the same rules.
4. Every machine inside the Legacy bands on all eight views, measured the same way.
5. Walk and idle GIFs for all five; the Godot view check on all five (when Preston's editor is closed).

Individual refine passes after that: gorilla (orange low from the side), pangolin (front-view light), hippo
(smoothness, tusks), shoebill (step height, wing shape, highlights), kangaroo (side-view light and highlights,
head size, arm detail, roster entry for Preston to approve).

## Hippo individual pass (2026-10-12): v5-v7

- Kit bug found: `plate(recess=...)` never inset anything. `bmesh.ops.inset_region` on an open sheet needs
  `use_boundary=True`; without it the op returned no faces, so every recessed plate since the gorilla came out flat
  (a test plate had 12 faces with and without recess). Fixed in `build_ape_l_v2.py`. The gorilla is not rebuilt yet,
  so its sprites are unchanged until its own pass; when it is, its recessed back, rump and chest plates will gain
  their framed panels.
- v5: the inset panels now show (22,164 triangles from 12,964); tusks bigger, but read as thin grey whiskers.
- v6: short thick tusks, a pair of trim rivets on each upper hull plate; the rivets stood 6 cm proud and fringed the
  top outline.
- v7: rivets nearly flush; a cream ramp in `hippo_m.json` so the tusks stop falling into the violet-grey ramp.
  e: colours 35, cluster 6.3, stray 8%, light +42, highlights 11%, near-black 19%. The tusks read from the front and
  three-quarter views. Installed. Still calmer than Legacy (cluster 5.6-7.3, stray 7-8%); front light +129, back +25.

## Factory pass, progress (2026-10-12)

- One rig code path: the pangolin now runs on `quad_rig.py` (243 lines from 364). Output identical: zero differing
  pixels on e, se, s and n against v18b, same stance file, walk spread 1.9 cm as before. The kangaroo's hop stays in
  its own build file until a second hopper exists.
- Kit inset fix applied to the gorilla as a test (v33): almost no visible change and side-view light rose to +115, so
  v32 stays installed and the gorilla's game files (glb, atlases, textures, blend) were restored from the backup.
- `tools/art/factory_report.py`: every installed view of every machine against the Legacy bands in one table.
  Report v1: out-of-band values of 48 per machine: gorilla 31, hippo 24, kangaroo 34, pangolin 8, shoebill 22. The
  shared gap: colour clusters too big and too few stray pixels (all eight views on four machines).
- Pixelizer: per-family ordered dither (`"dither": strength`; a 2x2 Bayer threshold on the block's mean shade
  position at sprite resolution). It touches only palette-driven families, so the gorilla is unchanged. Strength 0.6
  set on the hippo, shoebill and kangaroo (not the pangolin, already in band). Report v2: hippo 12, shoebill 10,
  kangaroo 30, pangolin 8, gorilla 31. Installed.
- Preston's reference sprites for the four new starters (2026-10-12, shown in chat): the matching targets for the
  individual passes, as his green gorilla sprite was for the gorilla. Waiting on the files in
  `docs/art/reference/starters/` to measure outline overlap and colours.

## Reference pass (2026-10-12): Preston's starter sprites as targets

Preston made a detailed side-view reference for each new starter (`docs/art/reference/starters/`, README there has
the measured colours). Tools added: `tools/art/reference_sheet.py` (installed / candidate / reference rows) and the
`compare_views.py` overlays. Pixelizer: `"match_style": false` per family opts out of matching the gorilla master's
shade distribution. Lesson that cost two rounds: the pixelizer stretches each family over its whole ramp, so a
frame that should stay charcoal must have a ramp that stops at charcoal; capping the grey ramps fixed the light-grey
legs on all three machines, and capping the red ramp at e6724c fixed the kangaroo's salmon.

Outline overlap with the reference (e view), installed to latest round:
- pangolin 0.698 to 0.704 (r4: higher back arch, launchers low behind the head, longer tail, bigger scales)
- hippo 0.665 to 0.681 (r3: body 10% shorter, legs 10 cm longer, muzzle 16% shorter, brighter purple, charcoal legs)
- kangaroo 0.589 to 0.622 (r4: orange-red over charcoal from the reference, torso leaning forward, crouched stance,
  bigger chest and haunches, longer feet, a quarter-bigger head, rounded armour blocks)
- shoebill 0.490 to 0.497 (r3: body higher on longer legs, upright posture pitched 35 degrees about the hips, fat egg
  body, wings held out and sweeping down; still too tall for its width, aspect 0.57 vs his 0.83)
- Installed after the reference pass: pangolin r4, hippo r3, kangaroo r4, shoebill r4 (overlap 0.517, aspect 0.72:
  pitch 28 degrees, primaries reaching back behind the legs, the shoe 15% bigger). Line-up:
  `docs/art/2d/factory_lineup_v3.png`; reference sheet `docs/art/reference/starters/installed_vs_reference.png`.
- Factory report v4 (`docs/art/2d/factory_report_v4.md`), out-of-band values of 48: see the file's last line. The
  kangaroo sits at 17 colours (Legacy 27-54) because its ramps are capped at the reference's colours; that is a
  choice for Preston: the reference's look or the Legacy colour count.
- Open after this pass: the shoebill is still narrower than his (0.72 vs 0.83); the kangaroo's armour reads as one
  red mass where his shows rounded blocks with charcoal gaps; the hippo's head is still a little long; the gorilla is
  untouched (Preston's approved v32).
- Round 5 (2026-10-12, Preston: "the neck connecting head to body has a gap and is too thin on hippo"): the hippo's
  neck is now a plum segment 0.9 x 0.84 m from inside the chest to inside the shortened head (the round-2 head
  scaling had pulled the head off the old 0.62 m neck), with three recessed bands over it; overlap 0.687. Shoebill
  r5: primaries end at mid height behind the legs (r4's dragged on the ground once pitched), wing limbs and five
  layered coverts bulked into a cloak; overlap 0.534. Kangaroo r5: five rows of smaller rounded blocks standing
  9 cm off the charcoal core so the gaps show; overlap 0.621. All three installed; lineup v4, report v5.
- Round 6 (2026-10-12): shoebill r6 installed (six light-blue recessed coverts in two columns over a deep-blue
  forearm, six primaries; overlap 0.536). Walk checks after the pose changes: hippo planted feet within 2.0 cm, the
  new neck pumps with the head; shoebill planted foot 0.0 cm spread, 3 cm steps, upright through the cycle;
  kangaroo hop fixed (flight phase now tucks the feet 32 cm up and points the toes 40 degrees; the GIF builder now
  keeps each frame's position in the camera frame so the lift shows). GIFs: `docs/art/2d/<id>/walk_e.gif`,
  `kangaroo_m/hop_e.gif`.

## Synthesis pass (2026-10-12): what each tool contributed

- PixelLab pixelart_workbench (free): scored every machine's side sprite out of 100 for pixel-art discipline:
  pangolin 93.9, gorilla 92.8, kangaroo 87.7, hippo 83.7 (shoebill: upload cut off in transit twice). The deduction
  it found everywhere, "near-duplicate colours" (hippo -10.5), is something none of our metrics measured. Its lint
  on the kangaroo: 297 one-or-two-pixel clusters, 36 px of banding, a clean single-component silhouette.
- Retro Diffusion edit tools (free ones): pixel_correction on the kangaroo changed 0 of 3,050 pixels, so our despeckle
  already does that job. k_centroid_downscale was evaluated and skipped: the 2x render it needs is about 80k tokens
  per call through this chat, too costly for one comparison image.
- Our own tools, prompted by PixelLab's finding: `tools/art/near_duplicates.py` lists colour pairs closer than a
  threshold with pixel counts. It found the shared cause: the pixelizer's fixed ground-shadow colours (2c2838,
  403a52) sit within 7-16 RGB units of every machine's dark greys, and the hippo's charcoal grey ramp lies almost
  on its purple ramp (41304b vs 433e4b, 524c5b vs 553e5e, 625c6b vs 6b4e71).
- firecrawl (earlier today): the animal anatomy for the hippo, shoebill, kangaroo and fossa proposals.
- Near-duplicate pass, result: pixelizer draws the ground shadow in the palette's third and fourth greys (the fixed
  colours were near-duplicates of every machine's dark greys; the darkest greys read as a near-black edge row);
  hippo grey ramp moved cooler (14171f to 6c7482), kangaroo grey thinned to six steps, shoebill grey darkest lifted.
  Near-duplicate pairs (< 24 RGB): hippo 15 to 9, kangaroo 8 to 4 to 3, shoebill 5 to 2, pangolin 8 to 5; gorilla
  untouched at 10. PixelLab re-score of the hippo: 83.7 to 91.2 (near_duplicates -10.5 to -3.0; singletons -4.7 is
  now its largest deduction). All four reinstalled (nd2). Factory report v7: gorilla 31, hippo 12, kangaroo 28,
  pangolin 21, shoebill 28 of 48 out of band; the pangolin's rise (12 to 21) and the shoebill's come from the
  reference pass (bigger scales, upright pose), not this one. Lineup v5: `docs/art/2d/factory_lineup_v5.png`.
- Next from the synthesis: singletons (lone pixels) are now the top PixelLab deduction on every machine; our
  despeckle only runs on the grey family. Enabling it on all families is the one-line follow-up.

## Synthesis roster and the despeckle pass (2026-10-12)

- Tool roster written: `docs/plan/synthesis-tool-roster-2026-10-12.md` (73 live servers sorted into used, worth a
  real use, noise, failed), pointed to from CLAUDE.md's synthesis section. New and relevant: Spritecook (needs
  Preston's sign-in), Summer Engine (engine not running), ElevenLabs (audio pass, paid), Director's Lookbook
  (named palette cards; used below). Three.js viewer cannot load local .glb files; Alpix is a shared pixel canvas.
- Despeckle on every colour family (not only grey) in the four palettes; reinstalled. Factory report v8: gorilla 31,
  hippo 13, kangaroo 28, pangolin 21, shoebill 25 (from 28). Near-duplicate pairs unchanged.

## Kangaroo roster entry, draft for Preston (Claude, 2026-10-12; nothing here is canon)

For `scripts/data/machines.gd`, after `hippo_m`. Colours from the reference pass (Preston's sprite). Lookbook's
nearest named card for the scheme is "Golden Hour Warmth" (espresso shadows through sienna and amber to honey
gold and cream); the reference's reds sit between that and "Hot Yellow to Red".

    "kangaroo_m": {
        "name": "Red Kangaroo type", "animal": "kangaroo", "size": "M", "body": "ground", "faction": "player",
        "hp": 150, "ep": 55, "ep_regen": 11, "speed": 36, "defense": 16, "starter": true,
        "colours": {"main": "d4553a", "trim": "2b2429", "accent": "e6724c", "light": "5fe1d0"},
        "weapons": [
            {"name": "Piston Kick", "type": "melee", "power": 26, "ep": 0, "accuracy": 90,
                "mount": "both hind legs: the shin pistons fire as it rears onto its tail"},
            {"name": "Pouch Mortar", "type": "shell", "power": 30, "ep": 14, "accuracy": 80,
                "mount": "a stubby launcher in the pouch hatch, lobbed in an arc"},
            {"name": "Tail Spring", "type": "melee", "power": 58, "ep": 36, "accuracy": 80,
                "mount": "a full-weight leap off the tail, both feet first"},
        ],
        "slot": "res://art/machines/kangaroo_m.png",
    },

Stats are drafts near the other starters (fastest of the five, lowest defence), untested in battle.
- Lookbook card for the kangaroo, from show_card: "Golden Hour Warmth" (shadow 2B1D14, dark 7A3E1D, mid D9822B, accent
  F2C46D, highlight FBE8C8; "the shadows stay deep brown so the gold glows"). Preston's reference is redder (d75d3d,
  ae301d), so the card is the named neighbour, not the source; the installed palette follows the reference.
- Shoebill r7 installed: egg 14% deeper front to back, primaries further back, the shoe 28% longer. Aspect 0.82 vs
  his 0.83 (was 0.70); overlap 0.535. Near-black 17-21%, highlights 14-24%, colours 20-25.
- Godot checks (2026-10-12, headless, no editor open): `views_check` PASS for all seven roster machines (eight
  different views, side longer than front, every view fits the 96x72 slot; the view lab turns the machines with the
  camera). `view_art_check` first FAILed 24 times on the three new machines because their PNGs had no `.import`
  sidecars (the editor had not re-scanned); `Godot --headless --path . --import` wrote them (1,328 steps), then
  PASS for ape_l, shoebill_m, pangolin_m, hippo_m. The kangaroo is not checked until its roster entry is approved
  and added to `scripts/data/machines.gd`. The import step now belongs in the factory round after every install.

## Factory gorilla test (2026-10-12): archived

ape2_l, four rounds (v1 0.509, v2 0.577, v3 0.590, v4 0.585 overlap with the master; ape_l 0.534). Preston judged
ape_l better by eye and it is: the factory path gave it a rig, palette and measures in one round, but the modelling
detail of 43 passes is what reads. Archived to `docs/art/archive/ape2_l/`. The first gorilla's factory-pass
re-pixelize (fp1, fp2) is also set aside: fp1 lost the dark outline, fp2 matched v32's numbers without improving
them. ape_l v32 stays installed.

## Weapons pass (Preston, 2026-10-12: "Weaponize gorilla 1 ... also weaponize Hippo, shoebill and kangaroo")

Visible hardware for each roster weapon, chosen from the animal's build:
- **Gorilla (v34, candidate):** Piston Knuckles as hydraulic accumulator tanks on the upper arms with a feed line to
  each fist and a row of four orange knuckle spikes; Ballast Throw as a throwing arm on the rack (grey rail along
  the spine, pivot drum, orange claw over the rear block). Quake Slam is the fists, no extra part. Built through
  `build_ape_l_v2.py` (parts named for its bone map: upper_tank, fist_line, knuckle_spike, ballast_*). The build
  rewrote the gorilla's game glb and atlases; the pre-weapons set is backed up in the scratchpad
  (`ape_backup_pre_weapons`) and goes back if Preston keeps v32.
- **Hippo (w1, w2):** Pressure Jets as a twin cannon riding above the snout (dark barrels, cream muzzles, tanks and
  valves behind the head); Wake Charge as a cream ram wedge ahead of the chest with a dark cutting edge and two
  pistons; Gape Crush is the jaw and tusks. w1's hardware in the body colour vanished at sprite scale; w2 contrasts.
- **Shoebill (w1, w2):** Stillwater Lance as a deep-blue barrel riding above the bill to a dark muzzle, with a sight
  block and lens on the crown; Bill Clamp as five serrated teeth along each cutting edge; Wing Buffet as gold
  leading-edge blades standing proud of the wing with a dark edge.
- **Kangaroo (w1, w2):** Pouch Mortar as a tube sticking out forward of the pouch hatch with a feed drum; Piston
  Kick as thick shin pistons with orange rods and dark cylinder heads; Tail Spring as a coil of four dark rings
  around the tail root.
- Lesson: a weapon reads at 1 px per 4.4 cm only if it contrasts with the body colour and breaks the silhouette.
- Installed (2026-10-12): hippo w3 (ram back on the chest), shoebill w3 (wing blade along the edge), kangaroo w2,
  gorilla v34 (weapons). ape_l v32 sprites stay in `docs/art/2d/ape_l/v32/` and its pre-weapons game files in the
  scratchpad backup for a rollback. Godot headless import and view_art_check re-run after the installs. Lineup v7:
  `docs/art/2d/factory_lineup_v7.png`. Pangolin not weaponized this pass: its Scale Shot launchers and Scale Rake
  tail blade were built in its v6 (already visible).

## Approved and next (Preston, 2026-10-12)

- Gorilla v34 (weapons) kept. Kangaroo roster entry approved and added to `scripts/data/machines.gd` after hippo_m
  (no slot PNG needed: `scripts/ui/slot.gd` falls back when the slot file is missing, as for the other starters).
- Part-by-part refine pass, one starter at a time in order of gap to the reference: kangaroo (0.621), shoebill
  (0.535), hippo (0.687), pangolin (0.704). Tool: `tools/art/part_compare.py` crops one region of ours beside the
  same region of the reference and scores the region's outline overlap. Parts per machine: head, torso and arms or
  wings, legs and feet, tail; weapons stay as installed unless a part round moves them.

## Part-by-part pass, round 1 (2026-10-12)

Region overlaps are from `part_compare.py` (crop by bounding-box fractions; the measure shifts when a part changes
the bounding box, so it is read with the crops, not alone). Whole-sprite overlap from `compare_views.py`.
- **Kangaroo** (installed w2: whole 0.621). Head p1-p4: long tapering muzzle, dark nose tip, visor eye, jaw hinge
  bolt, segmented charcoal neck from the chest front, thicker ears with lighter inner panels; a 1.45x head overshot
  (p2-p3), back to 1.25x (p4). Legs p5-p8: blocky thigh, charcoal shin column, big knee bolt, long orange foot,
  wider stagger; the crouch frame hides the shin behind the thigh and the standing frame loses the whole-sprite
  match, so p8 uses frame 3 with no thigh plate. Tail thicker, arms charcoal with orange claws. p8: whole 0.542,
  legs region 0.524. By the measure w2 still wins; by eye p8 carries the reference's head features. Preston's call.
- **Hippo** (installed w3: 0.687). Legs p1-p2: charcoal limb columns with bigger purple inset plates, bolt discs at
  hip, shoulder and knee, bigger cream nails. Head p3-p4: boxy square-fronted muzzle, ring ears, jaw hinge bolt,
  visor eye, the jet cannon moved behind the eyes onto the crown. p4: whole 0.679, head region 0.589 to 0.638.
  Installed.
- **Shoebill** (installed w3: 0.535). Legs p1-p2: thicker tarsus, gold hex joint blocks at knee and ankle, long
  spread toes raised off the ground with gold joints and tips, legs closer; region 0.238 to 0.326. Head p3-p4:
  the lance a slim grey barrel on the keel (the fat blue bar read as a crocodile), tooth row removed, a bigger
  hooked nail, the gold ramp saturated to the reference's shoe. p4: whole 0.569. Installed.
- **Pangolin** (installed: 0.704; regions head 0.71, body 0.86, legs 0.65, tail 0.70, the closest starter). p1:
  joint rings red-centred as in the reference (the "light" material a02010). Whole unchanged at 0.704.
- Part pass installs (2026-10-12): hippo p5 (p4 plus smaller joint discs; the 0.2 m discs read as black holes;
  legs region 0.549 to 0.600, whole 0.679), shoebill p4 (whole 0.569), pangolin p1 (red joint rings). Kangaroo
  left at w2 pending Preston's choice against p8 (`docs/art/2d/kangaroo_m/p8/`). Sheet:
  `docs/art/reference/starters/part_pass_sheet.png`. Godot import and checks not re-run (editor open).

## Part pass, round 2 (2026-10-12): shoebill priority, gorilla de-Cybertroned

- **Gorilla v35-v36 (installed):** Preston: "it has a lot of the Transformers Fall of Cybertron look". Tells found
  with part_compare against his master: the 16-segment glow pod on the flank, the glow ring in every joint disc,
  the teal inlay lines on the fists, the throwing-arm rail sticking out behind. v35: the pod a plain grey disc,
  `disc()` without its glow ring (a plain bolt head: grey disc, orange ring, dark hub), the hand inlays removed,
  the rail shortened inside the silhouette. v36: hip, knee and elbow bolts smaller (0.24/0.22/0.2 to
  0.18/0.16/0.16). Whole overlap 0.542 both; torso region 0.813 to 0.823. Remaining gaps: head (0.67, his is green
  rounded blocks over a grey jaw) and hind legs (0.50).
- **Shoebill p5-p7 (p7 installed):** LIFT 0.14 to 0.3 on thinner shins and tarsi (legs region 0.30 to 0.35); the
  wing rebuilt three times: p5 stacked light-blue blocks with a deep-blue fan (fan dominated), p6 bigger blocks and
  a light-blue body (one pale mass), p7 separate blocks over a dark wing base with gaps, a grey shoulder bolt, the
  crown sight removed, grey jaw bolts. Whole 0.569 to 0.585; wings region 0.658 to 0.659 (the crops, not the
  number, show the change). Head region 0.68 to 0.62 from the bolts widening the box.
- **Kangaroo p9 (installed over w2):** grey bolt discs at shoulder and hip on top of p8's head, tail, arms and
  legs. Whole 0.542 vs w2's 0.621; chosen by eye for the reference's head and visible shins. w2 stays in
  `docs/art/2d/kangaroo_m/w2/` for a rollback.
- Hippo and pangolin: no second round this pass (five and one rounds in the first).
- Part pass, round 3 (2026-10-12): shoebill p8 installed (grey mechanical neck column with dark rings, a four-slat
  chest grille; whole 0.586); hippo p6 installed (the visor eye high on the skull above the muzzle, the muzzle box
  deeper and squarer; head region 0.634, whole 0.678); pangolin p2 installed (bigger gold crown scales; head 0.715).
  Gorilla pass 37 (hind legs tucked, HIND_IN 0.8 to 0.7) made the legs one mass (region 0.497 to 0.490): dropped,
  build script back to v36. Lineup v9; report v12.
- **Gorilla v37 (installed), the visor (Preston, 2026-10-12: "Do the face visor thing here for the gorilla. Then
  make the eye one line across like Iron Kong kind of").** Pass 38 in `build_ape_l_v2.py`: the two lens eyes,
  their sockets and glow blocks are gone; one dark visor band (`socket_visor`) is sunk across the face under the
  brow shelf and one teal plate (`eye_visor`, 0.78 wide, 0.07 tall, bent 0.45 so its ends wrap the cheeks) sits
  proud of the face, flush with the brow front. The nose bridge dropped below it. Three tries: a round rod caught
  a specular band (38a); the flat plate set into the face sat in the brow's shadow, dark in the middle (38b); the
  plate moved forward out of the shadow (38c, kept). Two pipeline changes it needed: `render_sprite_views.py`
  samples teal faces along the line (a grid of 34 points) instead of at two lens centres, and
  `pixelize_render.py` has a flat-eye mode (`PIXEL_EYE_FLAT=1`, in the gorilla's round script only): a visor is
  dozens of teal pixels, and stretching them over the three-shade eye ramp painted its lit third near-white and
  dropped its shadowed middle to grey; flat mode uses the middle shade, the dark shade where the render is dim and
  the glint only on the brightest 3%. Measures unchanged against v36 (26-29 colours, cluster 5.1-6.5, light
  +123..+153, head region overlap 0.726 both; the reference has two eyes, so the visor is Preston's call, not a
  measured one). Sheets: `docs/art/2d/ape_l/compare_visor_v36_v37.png`, `compare_visor_heads.png` (8x head crops).
  Installed with the v36 map; `Godot --headless --import` then `view_art_check`: PASS for all five, the kangaroo's
  first check since its roster entry. v36 build kept in the scratchpad as `build_ape_l_v2_v36.py`.

## Round 4 part pass (2026-10-12, Preston: "Do full creature pass again part by part", then "use the synthesis and the zoid sprite references in the folder too")

Measured first: five regions of each installed side view against Preston's reference (`part_compare.py`), the
weakest region picked per machine. Weakest: pangolin front legs 0.683, hippo front 0.613, shoebill hind legs
0.520, kangaroo head 0.502, gorilla hind 0.558.

- **Pangolin p3 (installed):** front legs thicker columns (upper 0.28 to 0.34, lower 0.23 to 0.28), bigger scale
  plates and foot, claws 0.08 to 0.1. Front region 0.683 to 0.717, whole 0.705 to 0.716.
- **Shoebill p9 (installed):** shin 0.10 to 0.15, tarsus 0.085 to 0.12, joint blocks and toes thicker, primaries
  carried 0.22 higher. Hind region 0.520 to 0.568, whole 0.586 to 0.600.
- **Kangaroo p10 (installed, palette p10b):** muzzle shortened (tip -0.62 to -0.48) and angled down, nose tip
  moved back, ears 0.2x0.42 to 0.24x0.5. Head region 0.502 to 0.619, front 0.558 to 0.641, mid 0.726 to 0.823,
  whole 0.542 to 0.607, the largest gain of any round.
- **Hippo p7 (dropped):** leg plates narrowed, feet and nails bigger. Front 0.613 to 0.609, whole 0.678 to 0.670.
  Build file restored to p6.
- **Gorilla v38 (dropped):** feet and toes 20% bigger. Hind region 0.558 to 0.531 (the master's feet sit under an
  upright body; ours reach further). Build file restored to v37 (visor).

**Zoids Legacy sheets** (`D:\Program Files (x86)\Game assets\sprite references zoids`, three Legacy sheets and
three Saga DS; structure and technique only, nothing copied): ten structural comparables cropped to
`docs/art/reference/legacy/` (Iron Kong for the gorilla; Elephander, DiBison, Red Horn for the hippo; Gun Blaster,
Gordos for the pangolin; Gun Sniper, Hellrunner for the shoebill; Godos, Rev Raptor for the kangaroo), index sheets
`index_helic.png` and `index_zenebas.png`. Scored with `sprite_quality.py` beside our installed side views
(`docs/art/2d/round4_legacy_study.png`, 3x, same pixel scale):

| | colours | cluster | stray | light | highlight | near-black edges |
|---|---|---|---|---|---|---|
| Legacy comparables (7) | 27-40 | 2.6-4.5 | 11-23% | +31..+137 | 6-17% | 0-18% |
| ours, installed | 15-31 | 4.0-5.1 | 10-16% | +35..+123 | 13-30% | 9-40% |

What the comparison says: Legacy machines are built from more, smaller clusters (joint discs with pale centres,
grilles, panel bevels) where ours are blockier; their edges are rarely near-black; a large Legacy machine is 160-190
px wide where our hippo is about 115 (the game slot sets ours, left alone). Acted on:
- **Kangaroo palette (p10b):** 15 colours and 40% near-black edges against Godos/Rev Raptor at 27-33 and 1-14%.
  Red ramp 6 to 8 steps plus a lit top, grey ramp lifted off black, edge floors 2: 18 colours, edges 24%. Gamma 1.5
  (p10c) only darkened the edges again; `match_style` (p10d) did nothing, the gorilla master has no red family.
  PixelLab `pixelart_workbench score` on p10: 95.9 (singletons -3.2, banding -0.9).
- **Hippo p8 and shoebill p10 (building):** Legacy quadrupeds stand on legs clear of the body (ours merge into it):
  hippo LIFT 0.1 to 0.25. Legacy bipeds have thick leg columns: shoebill shin 0.15 to 0.18, tarsus 0.14, joints 0.25.
Not used this round: Retro Diffusion (paid tools need a yes; its free edit tools did nothing last time), Spritecook
(for UI, not machines), Firecrawl (no new anatomy question). Godot `--import` and `view_art_check`: PASS for all
five after each install.
- **Hippo p8 (dropped):** LIFT 0.25 made the body taller than the reference's (width/height 1.73 against 1.97);
  whole 0.678 to 0.625, front 0.613 to 0.556. Build file back to p6. The Legacy "legs clear of the body" reading
  does not transfer to Preston's hippo, which is squat on purpose.
- **Shoebill p10 (dropped):** shin 0.18 and tarsus 0.14 measured flat (whole 0.600 to 0.595); p9's 0.15/0.12 kept.
Installed after round 4: gorilla v37, hippo p6, pangolin p3, shoebill p9, kangaroo p10 (palette p10b).

## Kangaroo loadout pivot (2026-10-12, Preston: "Remove cannon that is in area of phallus ... pivot to having jetboosters" plus his boxing loadout text)

- **Build (p11, p12 installed):** the pouch mortar barrel, muzzle and drum are gone. The pouch is a closed hatch flat
  to the belly with a dark seam and two latch discs (the Pouch Flak Gun is concealed, per his text). Impact Boxing
  Gloves: fists 0.13 to 0.17 with an orange knuckle plate and a charcoal hydraulic piston with an orange cap along
  the back of each forearm. Jet boosters: a pod on each hip behind the plate rows, charcoal mount, grey cylinder
  housing with a trim band, flared trim nozzle and a dark throat facing back; p11's pods sat at the tail root and read
  as small drums, p12's are higher, longer and 0.17 radius and read as pods in the side and back views.
- **Structure study (synthesis):** the Zoids Vs. GameCube model rips in `Game assets\Mech references\Zoids` are
  OBJ meshes with textures. Rendered headless (Blade Liger, Iron Kong Old, Cannon Tortoise; sheet in the scratchpad):
  the Liger carries paired cylinder booster pods on the hip armour with the axis along the body and the nozzle
  facing back; the Kong a boxed back pack; the Tortoise a housing set into the shell. The kangaroo's pods follow the
  Liger's construction only (cylinder on a mount, band, flared nozzle, dark throat); nothing copied.
- **Decomp (`zoids-source\ZoidsLegacyDecomp`, notes in `docs/reference/zoids-legacy-structure.md`):** weapons carry a
  type and traits; our battle code has no knockback effect, so the gloves' knock-back is a design note for Preston,
  not wired.
- **Roster (`scripts/data/machines.gd`):** weapons renamed from his text, Impact Boxing Gloves (melee), Pouch Flak
  Gun (shell), Tail Spring (jet-boosted); the numbers carry over from the old slots and are marked DRAFT for him.
- **Measures:** p12 e 18 colours, cluster 4.0, near-black edges 22%; whole outline against his reference 0.607
  (p10) to 0.567 (p12), the reference has no boosters or gloves. Godot import and `view_art_check`: PASS.
- **Gorilla v39 (installed), highlights:** `sprite_quality` on Preston's own references: his gorilla master is 27
  colours, cluster 4.2, 7% highlights, 95% near-black edges (a full dark outline, so the Legacy "no black edges" rule
  loses to his reference and our edges stay); the other four references are smooth upscales the tool cannot read.
  Our gorilla was 14% highlights. `pixelize_render.py` now reads `PIXEL_HIGHLIGHT_RANK` (default unchanged,
  0.86,0.95); the gorilla round sets 0.93,0.975. v39 side view: highlights 14% to 9%, colours 26 to 29, cluster
  5.1 to 4.9, outline overlap 0.542 (v37 0.544). Same build as v37 (the visor). Godot import and check: PASS.

## Gorilla animation foundation (2026-10-12, deep research, Preston: "create movement and animations for gorilla")
Report: `reports/Gorilla mech animation foundation.md` (notes in `research_notes/Gorilla mech animation foundation/`).
Three researchers (gorilla biomechanics; heavy-mech animation craft and Blender scripting; how games and films
animate animal machines and what Zoids Legacy style battle screens show) plus a writer. Headline: our 36-frame walk
at 24 fps is 1.5 s, inside the measured gorilla stride range (1.13 to 1.78 s), so the measured limb-phase timeline
converts straight to frame numbers; Legacy-style battle screens use one static sprite per unit with flash, offset
and overlays, so any frames we add are already above the genre baseline. Plan proposed (marked as inference): eight
states, about 52 to 55 frames per direction. Next step named: script the walk from the measured timeline, bake,
render nine frames of two views, judge the bob and hand plants before any attack.

## Gorilla animation pass 1 (2026-10-12, Preston: "do that", the report's next step: script the walk from the measured timeline, render nine frames, judge the bob and hand plants)
- The existing 36-frame `walk` clip was already keyed from the Ito et al. 2025 contact phases (arm 0 / 0.507, leg
  0.475 / 0.986, duty 0.66). Measured per frame inside Blender (scratchpad `walk_measure.py`, `walk_lowest.py`):
  the body bobbed 0.20 m (8% of height) twice per stride because `clip()` grounded the whole mesh on its lowest
  vertex and knuckles hang 0.16 m below the hand bone, toes 0.25 m below the foot bone, so the floor jumped whenever
  the lowest limb changed. The planted hand floated 0.24 m at touchdown and the swinging hand dipped 0.19 m through
  the floor. By eye the strip read as a walk; the numbers did not.
- **Fixes in `build_ape_l_v2.py`:** `walk_pose` now lists its stance limbs and `clip()` grounds on those limbs'
  vertex groups only (bob 0.20 to 0.13 m). The rest arm leans 20.7 deg ahead of the shoulder and the leg 9.7 deg
  (`joints.py`), so the old sweep never passed vertical; a new `gait` clip re-centres the sweeps 14 deg back on the
  arms and 10 deg on the thighs with more swing lift (upper arm 20, forearm 55, hand 40). `walk` is untouched
  because the battle stance samples its frames. A contact-only grid (`walk_grid.py`, 30 settings) had picked 40
  and 30 deg, which folded the limbs under the belly: numbers without a posture rule are not enough.
- **Result (gait, v40 build):** planted hands float 3 to 8 cm, feet up to 16 cm, swing hand dips 5 to 19 cm at
  lift-off, body bob 0.18 m (7%). Strips: `docs/art/2d/ape_l/walk_frames_v39.png` (before), `walk_frames_v40.png`,
  `gait_frames_v40.png` (renders, three-quarter renders, pixelized side frames with the ground line).
- **Judgment:** a rotation-only sweep cannot plant four limbs at once; each limb's tip rides an arc and the floor
  follows the lowest one. The real animal absorbs that with compliant elbows and knees. Next step is the report's
  foot lock: two-bone IK on each limb for the gait clip only, stance targets keyed as straight lines on the floor,
  swing targets on raised arcs, baked to FK keys with visual keying so the stance clip and renderer stay as they are.
- Installed sprites unchanged (v39); the v40 blend holds the extra clip. Builds backed up in the scratchpad.

## Gorilla animation pass 2, attacks (2026-10-12, Preston: "attack animations")
Three 36-frame clips (1.5 s at 24 fps) in `build_ape_l_v2.py`, built on the report's spine: weight rocks back onto
the hind legs, held anticipation, a one-to-two-frame strike already past the target, compression on impact, settle
in parts. Each pose names its stance limbs so the grounding ignores the striking arm.
- **punch (Piston Knuckles):** wind-up 0-0.40, hold to 0.50, strike 0.50-0.58, hold to 0.72, settle with the arm
  3 frames and the head 5 frames behind the body. First render swung the fist over the head: the rest arm already
  leans 20 deg ahead, so 88 deg of swing passed horizontal; 62 deg puts the fist forward at chest height.
- **slam (Quake Slam):** rear-up 0-0.35 with both arms (the one twinned clip), hold, drop 0.45-0.53 with a 0.10 m
  compression, crouch hold, a 3 cm shudder 0.70-0.80, settle with the right arm 3 frames before the left. First
  render's rear-up was too subtle; body 38 deg, thighs 30, arms 95 and a 0.12 m rise read as rearing.
- **throw (Ballast Throw):** tear 0-0.35 (arm over the shoulder to the rack, torso turned and tilted back over the
  hind legs), load hold, hurl 0.45-0.55, plant 0.55-0.70, settle. The block is a separate sprite or effect, not
  modelled. Read right first time.
- Sheet: `docs/art/2d/ape_l/attacks_v40.png` (ten three-quarter frames per clip, renders and pixelized). Helpers
  `_seg` and `_pulse` added. The clips live in `docs/art/3d/ape_l_v2.blend`; the game still shows one static
  sprite per machine, so wiring frames into Godot (SpriteFrames with the report's durations) is the next step
  after hit, win and defeat are refined. Installed sprites unchanged.

## Battle wiring, Legacy style (2026-10-12, Preston: "Wire the battle setup real quick so I can see the test ... zoids legacy battle style as foundation")
- **Staging** (`scripts/scenes/battle.gd`): the player's machine front-left and low (feet y 121), the enemy
  back-right and higher (feet y 101), drawn behind, overlapping in the middle as the reference's diagonal
  formation does; gauges moved into the bottom panel under the message line; the default test fight is
  gorilla vs hippo. Machines draw from `art/machines/<id>/anim/` when it exists (AnimatedSprite2D built at run
  time by `scripts/ui/machine_anim.gd` from `anim.json`), else the side view in `views/`, else the old blocks.
- **Turn presentation** (act, then show, as the decomp notes): the text line, the attacker's clip (or a 14 px
  lunge for art without one), and at the clip's strike frame the target flashes, plays `hit` if it has one,
  jolts 8 px away, the screen shakes 3 px and the number pops and rises. `battle_logic.gd` tags attack steps
  with the attacker and its weapon's `clip`; the gorilla's weapons name punch, throw and slam in `machines.gd`.
- **Frames:** `tools/art/export_anim.py` packs pixelized clip frames on one fixed-camera canvas (the pixelizer's
  new `PIXEL_NO_CROP=1`) with the report's frame picks and durations: idle 4, gait 9, punch 9, slam 10, throw
  10, hit 3, death 6 (51 frames, 147x144 canvas, feet row 116) into `art/machines/ape_l/anim/`. Shading is
  ranked per frame, so a lunge frame can shift a shade; a shared ranking across a clip is the known follow-up.
- **Godot:** the headless `--import` wrote no sidecars for the new folder until `docs/.gdignore` kept the docs
  Blender files out of the scan (the Blender importer error was aborting the pass). `tools/debug/battle_capture.gd`
  runs the scene windowed, fires Piston Knuckles and saves nine shots (`docs/art/2d/battle_capture.png`,
  three-shot cut `battle_test_v1.png`): wind-up, strike, the hippo flashing with the number, the miss path too.
  `view_art_check` PASS. Open: a stray "14" drawn top-left of the battle screen, not from the background image.

## Black wolf, the sixth starter (2026-10-12, Preston: "a black wolf with blood red accents. Use the synthesis and creature factory then mass manufacture it")
- **Research:** San Diego Zoo Wildlife Alliance fact sheet and National Wildlife Federation (Firecrawl): shoulder
  66-84 cm, head and body 100-160 cm, tail 35-56 cm, narrow keel chest, long legs with elbows in and paws out, an
  elongate skull, a bushy black-tipped tail, a mane on the neck and shoulders. Legacy canids cropped for structure
  only (`docs/art/reference/legacy/command_wolf.png`, `shadow_fox.png`: width to height 1.4-1.5, 60-68 colours).
- **Build** `tools/blender/build_wolf_m.py` (kit plus quad_rig), palette `tools/art/palettes/wolf_m.json`, DRAFT
  roster entry `wolf_m` in `machines.gd` (Fang Lunge, Howl Burst, Shadow Dash; numbers in the medium starters'
  range, Preston's to set; teal eyes by the faction rule, red is one line if he wants it).
- **Rounds:** v1 read as a crocodile (tail to 2.35, muzzle 0.94) with floating paws and red specks; v2 shorter
  tail carried low, muzzle 20% shorter, mane plates and fins doubled; v3 paws centred on the joints; v4 found the
  real fault by measuring the mesh against the bones (`wolf_paws.py`): the paws were attached all along, the
  claws sat on the floor ahead of them and the grounding lifted the paw. Claws now grow from the paw front.
  v4 installed: `art/machines/wolf_m/views/`, lineup `factory_lineup_v11.png`, report v14. Side view 20 colours,
  cluster 4.5, near-black edges 48% (a black machine; Preston's gorilla master is 95%).

## Round 5 part pass (2026-10-12, Preston: "keep upgrading and refining our models. Do pass on each creatures by part", with new wolf and gorilla references; "better quality than the zoids sprites", not "ps1 creatures")
- **References:** `docs/art/reference/starters/wolf_m.png` (new) and `ape_l.png` (his second gorilla, a knuckle-walk
  three-quarter pose that matches our pose; the upright master kept as `ape_l_master_upright.png`). Against the
  new gorilla reference the installed v39 measured 0.616 whole (0.544 against the upright master).
- **Gorilla v41 (installed):** fists 1.35x to 1.5x about the base, a squarer fist block. Front region 0.569 to
  0.586, whole 0.616 to 0.622. v42 (building): knee discs 0.16 to 0.21 with a dark knee seam, for the hind region
  (0.591), where his sprite shows thigh and shin as two blocks either side of a big disc.
- **Wolf v5 to v7 (v7 installed):** against his reference v4 measured 0.503 whole, front 0.414, hind 0.602, and
  read as a low crocodile; his wolf stands on legs a third longer than the body is deep, steel-grey segmented
  columns with big joint discs, a long finned tail joined high on the rump and held level. v5: legs 0.3 longer
  and thicker, limb grey lifted from 2b2b30 to 4a4a54, discs 0.09 to 0.14 plus shoulder and hip hubs, body and
  head lifted, tail fins (whole 0.493, the long tail took the length to 2.15 to tall against his 1.82). v6: tail
  shortened and lifted (0.509). v7: hind legs reshaped into his digitigrade Z (knee forward, hock back, foot
  forward), tail root at the top of the rump running level, stance stagger halved (0.517, hind 0.602 to 0.415 is
  a region-crop artefact of the longer legs; by eye the closest yet). v8 (dropped): head raised to back height,
  front region fell 0.393 to 0.375. v9 (building): the upper arm runs down and forward from the chest with the
  forearm vertical ahead of it, as his forelegs do.
- **Pangolin p4 (installed):** hind legs the columns the front got in round 4, bigger hind claws. Hind region
  0.720 to 0.730, whole 0.716 to 0.719.
- **Hippo p9 (installed):** joint discs 0.14 to 0.17 and shoulder discs 0.13 to 0.16. Silhouette measures
  unchanged (the region tool reads outlines, not interior detail); no regression, bigger hubs for the quality aim.
- **Shoebill p11 (dropped):** egg 1.14 to 1.2 deeper with plates grown: head region 0.776 to 0.759, front flat.
  **Kangaroo p13 (dropped):** a rounded thigh muscle shell and a 0.2 knee disc: every region flat. Both files
  restored.
- **Gorilla v42 (installed):** knee discs 0.21 with a dark knee seam; silhouette measures flat (hind 0.589, whole
  0.621), the hubs read in the side view. **Wolf v9 and v10 (v10 installed):** v9's forelegs run down and forward
  from the chest with the forearm vertical ahead (front region 0.393 to 0.444, whole 0.510); v10 shows both
  forelegs (stagger 0.06 to 0.1), slims them (0.2 to 0.17) and adds wrist and ankle discs (whole 0.512, hind
  0.437, front 0.431). Against his reference the wolf went from 0.503 (v4) to 0.512 whole with the look changed
  far more than the number: steel legs, discs, a level finned tail, the head up.
- **Installed after round 5:** gorilla v42, wolf v10, pangolin p4, hippo p9, shoebill p9, kangaroo p12. Lineup
  `factory_lineup_v12.png` (six, the wolf beside its reference), report v15. Godot checks PASS for all six.
- **What the region tool cannot see:** interior detail (discs, seams, muscle shells) leaves the outline masks
  unchanged, so those rounds were judged by eye against the reference crops; a detail measure (interior edge
  density, the Legacy study's cluster size) is the missing instrument for Preston's "better than the Zoids
  sprites" aim.

## Round 6 part pass (2026-10-13, Preston: "go again. Use the synthesis", hippo tusks at the mouth corner, shoebill pose and wings with no head gun, kangaroo tail and head, plus the usual pass)
- **Hippo p10 (installed):** tusks moved from the front of the jaw to the corners of the mouth line, rising from the
  jaw hinge as his reference shows. Measures flat (whole 0.676, head 0.635); the ask was placement.
- **Kangaroo p14 (installed):** tail rebuilt as five thick plated segments with a slow taper reaching further back
  along the ground (eight thin rings and four fat root rings had read as a beehive), two root rings only; head
  rounder and shorter (muzzle tip -0.48 to -0.4, crown raised), ears wider. Whole 0.567 to 0.611.
- **Wolf v11 (installed), detail pass:** two dark rivets and a seam on each upper body plate. Cluster size 4.8 to
  4.5 (side) and 5.0 to 4.7 (three-quarter), outline unchanged (0.511): the first measured move toward the Legacy
  canids' 2.8 to 3.3 and his "better than the Zoids sprites" aim; the same pass is due on the other five.
- **Shoebill p12 (dropped):** PITCH -28 to -42, LIFT 0.3 to 0.45, bill barrel removed, primaries shortened to end
  at the tail at mid height, the under-fan tucked. Upright the egg's long axis went vertical and the side view
  thinned to 0.60 wide to tall against his 0.83; whole 0.600 to 0.529. p13 (building): egg 1.5 deep front to back
  and the wing arm light blue so the folded wing reads pale as his does. The first p13 run rebuilt p12 unchanged
  because the patch targeted a line the round-5 restore had removed; corrected.
- **Shoebill p13, p14 (dropped), p9 stays:** p13 (egg 1.5 deep, wing arm light blue) 0.538; p14 (egg also 30%
  taller and wider about its centre, LIFT back to 0.3) 0.557, still under p9's 0.600, and the bigger egg shows the
  dark core where the plate bands no longer cover it. The upright pose Preston wants (his bird is mostly a plump
  round body with folded pale wings, legs under it) needs the body, plate bands, breast blades and wing blocks
  rebuilt together around a bigger egg, not one knob at a time: a dedicated shoebill session is the next step,
  starting from p12's pose (PITCH -42, no bill barrel, short primaries) with the plates scaled to the egg. Build
  file restored to p9. Sprites of every try kept in `docs/art/2d/shoebill_m/`.
- **Installed after round 6:** gorilla v42, wolf v11, pangolin p4, hippo p10, shoebill p9, kangaroo p14. Lineup
  `factory_lineup_v13.png`, report v16. Godot checks PASS for six. The rivet-and-seam detail pass measured on the
  wolf is the next thing to run across the other five.

## Round 7, kangaroo head and tail, shoebill, pangolin (2026-10-13, Preston: "use synthesis to figure out how to make kangaroo head. You were closer with the longer version. The tail is farther from reference"; then "the kangaroo head with the long shape before was closest. keep that but keep refining it")
- **Kangaroo, measured from his sprite:** tail root 29% of body height thick, tip 5%, nine rounded segments with
  dark gaps, outer half on the ground, tip half a body length behind the hips. p15 built that tail and a domed
  head: whole 0.567 to 0.633, but the tail went dark (gap segments fatter than the barrels), and Preston judged
  the p12 long head closer. p16-p18 chased the tail: p16 barrels had their length on the sideways axis (thin
  discs), p17 fixed the axis, p18 found the real fault: the kit's `shell` takes full extents, not radii, so the
  barrels were half size inside the core. p18: red barrels with dark gaps, whole 0.649. p19: p12 head on the p18
  tail (0.623, head 0.616). p20 (installed): crown raised to the ear base, both ears at different tilts, a round
  ringed lens instead of the visor bar, deeper jaw (whole 0.636, head 0.643). p21: deeper convex muzzle, measured
  worse (head 0.613). p22: p20 muzzle with p21's taller side-by-side ears and a grey neck column: whole 0.648
  (best) but head 0.612; p20 stays installed since the head is the target. Every try in `docs/art/2d/kangaroo_m/`.
- **Shoebill p15 to p17 (p17 installed):** Preston called the upright direction closer. p15: p14's bigger egg with
  four plate bands aimed at it (0.559, the bare dark core still showed); p16: core light blue with deep-blue lower
  bands (0.556, reads as his pale plump bird); p17: primaries trailing past the rump, legs longer and slimmer
  (0.543, width 0.65 to 0.71 against his 0.83). Installed on his direction, the outline number under p9's 0.600.
- **Pangolin p5 (dropped):** rivets on the limb plates, cluster unchanged (4.7); file back to p4.

## Round 8, the look-compare round (2026-10-13, Preston: "Can you do the blender look compare thing? Are you sure you are utilizing everything when we are using the synthesis?"; then "get the head details right for kangaroo. Then do factory pass for every creature")
- **Look-compare (new, now first step of every pass):** the machine's blend opened in Preston's live Blender (MCP
  add-on 1.8, Blender 5.2.2), his reference loaded as a textured plane at the model's exact height beside it, a
  side orthographic camera rendered to `docs/art/2d/<id>/look_compare_<version>.png`. The viewport `look` tool
  reads its own camera, so the render-to-file is the repeatable form. What it showed that the sprite crops hid:
  kangaroo torso sheared 45 deg into a crouch with the head low; shoebill body two thirds of the height with no
  neck and a small head (his: head and bill the top quarter, a narrow neck, body a third and wider than tall,
  legs nearly 40%, measured row by row); hippo head long and flat with the jet barrels as a bar ahead of it and
  dark leg plates over the legs; wolf body long and thin with a small head; pangolin scales sparse over a grey
  core; gorilla body a flat crate against his rounded blocks (not acted on yet).
- **Kangaroo p23, p24 (installed), p25:** p23 lean 0.2 to 0.06 and the head raised: front 0.608 to 0.716, hind
  0.609 to 0.701, head region fell (the head floated above the neck). `tools/art/part_overlay.py` (new): the
  stacked red/blue overlay of one region, zoomed, beside both arts. p24 from the head overlay: muzzle 12% shorter
  and raised, the back ear laid further back and taller, the head seated on the neck: whole 0.670 (best), front
  0.740, hind 0.690. p25 (longer tail, ears more upright) measured worse on both and was dropped.
- **Wolf v12 (installed):** deeper body, head group 1.2x, tail angled up 20 deg: whole 0.511 to 0.548, hind
  0.437 to 0.497. **Hippo p11 (installed):** HEAD_SQ 0.84 to 0.74, jet barrels halved to stubs, leg plates
  smaller: head region 0.635 to 0.659, whole flat. **Pangolin p6 (installed):** scales 35% denser, smaller,
  rows closer: whole 0.719 to 0.724. **Shoebill p18, p19 (p19 installed):** rebuilt to the measured rows (body a
  third, centred level, PITCH 0; neck long and slim; head group 1.25x; hips inside the body bottom with legs near
  40%; wing folded down the side). Reads as his bird's structure for the first time; the outline number (0.467)
  is dragged by the bill carried level and the body a touch wide (0.95 to his 0.83); p20 (building) tilts the bill
  down and narrows the body.
- **Patch slips this round, both caught by the measures:** hippo p11 first ran on a line the round-5 restore had
  changed, then on a comment I dropped mid-expression (syntax error, old build rendered); shoebill p13 the same
  restore issue. Every patch now asserts its target text and the build log is grepped for Traceback.
- **Shoebill p20 (installed), p21 (dropped):** p20 bill carried 16 deg down and the body narrowed: 0.467 to 0.498,
  width 0.68 to tall (his 0.83, so the tilt overshot). p21 eased the tilt to 10 deg and deepened the body 15%:
  0.492, and the head did not render at all (the build log showed no traceback; the head group is missing from
  every view, cause not yet found). File restored to p20. Next for the shoebill: find why p21 lost its head, then
  the width (body depth without the bill tilt) and a look-compare of p20.

## Round 9 (2026-10-13, resumed)
- **Shoebill p20 was headless, p22 installed.** The p20 patch dropped its comment into the middle of the head
  rotation expression, commenting out the translation back, so the head rotated about the world origin and left
  the frame; p20's 0.498 and p21's 0.492 were measures of a headless bird, and p20 was installed on that number
  without a look at its sheet. The slot went back to p19 while p22 rebuilt with the line repaired: bill 12 deg
  down, body 1.1 deep. p22: 0.489 against p19's 0.467, width 0.88 to tall (his 0.83), head and bill present and
  angled as his. Rule from this: every install is looked at, not just measured; patches never put a comment inside
  an expression.
- **Skills read before the detail pass:** `pixel-art` and `sprite-sheet` on disk are Summer Engine image-generation
  recipes; the transferable rules (outline from the palette's darkest colour, not black; three-tone shading; no
  anti-aliasing) are already the pixelizer's. Nothing new to apply.
- **Headless look-compare:** `tools/art/look_compare.py` renders the same reference-plane compare from the shell
  (`blender -b <blend> -P tools/art/look_compare.py -- <id> <out.png>`), so it no longer needs the live add-on,
  which dropped its connection mid-session. Caveat found on the gorilla: the compare shows the rest pose, while
  the sprites are rendered in the battle stance, so posture read from it needs checking against the stance sprite.
- **Gorilla v43 (dropped):** the torso profile reshaped into the reference's mound produced a pixel-identical
  sprite: the torso shell is fully covered by the back plates, arms and rack in every view. Build file back to v42.
  The silhouette lives in the back plate row (`back_plate_*`), the rack and the limb armour, not the shell.
- **Shoebill p23, p24:** p23 thickened the neck into a blue-plated column (kept), lightened the legs (kept), and
  deepened the bill to a short round clam (dropped); p24 put the bill length back (0.496). The p24 head overlay
  showed the bill tip rising where his hooks down: the head rotation sign was inverted, -12 raised the tip. p25
  sets +20 and adds a five-blade crest (his spiky crest showed red at the back of the head).
- **Shoebill p25, p26 (p26 installed on the look):** p25 at +20 hooked the bill well below the head (0.450). p26
  at +8 with the crest: whole 0.460 against p22's 0.489, but the head overlay's reference-only share fell from 27%
  to 19% (we now cover his crest and bill), with the excess being our thicker neck. First version whose head reads
  as his: crest, heavy bill sloping slightly down, blue plated neck. Installed on Preston's standing preference for
  shape over the outline number on this machine; the width (0.95 to tall against his 0.83) is the next target.
- **Installed after round 9:** gorilla v42, wolf v12, pangolin p6, hippo p11, shoebill p26, kangaroo p24. Lineup
  `factory_lineup_v15.png`. Godot checks PASS for six.

## Round 10: factory pass, individual pass, part pass (2026-10-13, Preston: "Full creature factory pass, do each individually. Then do by part")
- **Factory pass:** every creature rebuilt from its build file through the full pipeline, then look-compare, whole
  and five region measures, and a pixel diff against the installed slot. All six reproduce pixel-identical, so
  sources and game agree. Script: scratchpad `factory_pass.sh` (rows: id, new version, installed version, blend).
- **Individual pass, one fix each from its own look-compare:** hippo p13 (LIFT 0.1 to 0: whole 0.676 to 0.705,
  front 0.618 to 0.659), kangaroo p27 (booster pods shorter and tucked: 0.670 to 0.674, hind 0.690 to 0.718),
  shoebill p28 (thin grey leg rods: 0.460 to 0.464), wolf v14 (tail 20% shorter: whole 0.548 to 0.540 but hind
  0.497 to 0.563 and width to tall 2.02 to 1.93 against his 1.82) all installed. Pangolin p8 (arch 7% lower)
  0.724 to 0.706 and gorilla v45 (back plates 7 cm lower) unchanged: both dropped.
- **Part pass, each creature's weakest region from the stacked overlay:** pangolin p9 (front legs 12 cm forward:
  0.727, front 0.716 to 0.721) installed. Hippo p14 (front legs 18 cm forward) 0.695, wolf v15 (forelegs angled
  forward) 0.531, shoebill p29 (legs 10 cm back) 0.436, kangaroo p28 (head 6 cm back, muzzle 7% shorter) whole
  0.678 but head overlay 0.576 to 0.561: all dropped. Finding: the side sprites render the battle stance, where the
  walk rig's IK places the feet from the gait paths, so moving rest-pose leg joints barely moves the sprite's
  legs; leg placement work belongs in the stance spec and gait paths (quad_rig CFG), not the joint list.
  Gorilla front arm left alone for the same reason (its stance is hand-set in render_sprite_views).
- **Installed after round 10:** gorilla v42, wolf v14, pangolin p9, hippo p13, shoebill p28, kangaroo p27. Lineup
  `factory_lineup_v16.png`. Godot checks PASS for six.

## Round 11, gorilla part by part (2026-10-13, Preston: "part by part, refine 1 by 1. Start with gorilla")
Five parts overlaid against his second reference (`tools/art/part_overlay.py`, regions as fractions of the bbox:
head 0.6,0,1,0.45; back and rack 0,0,0.6,0.4; torso 0.3,0.2,0.7,0.7; fists and front arms 0.5,0.45,1,1; hind
legs 0,0.4,0.45,1), worked worst first.
- **Fists and front arms (0.551):** his reference shows both front fists, near forward and far planted behind;
  ours showed one. The battle stance picks a walk frame per limb (`SPRITE_STANCE`), so this was a stance choice:
  far arm frame 27 (frames 23-28 tried; 28 lifts the fist) gave fists 0.636, whole 0.645 (v47). Near-arm changes
  all lost the reach and scored worse.
- **Hind legs (0.600):** near hind leg 16 and far hind leg 3 splay the legs as his do: hind 0.617, whole 0.655
  (v49). Far leg 7 scored higher but caught its swing and showed lifted in the w view.
- **Head (0.656):** the head group pulled 16 cm back over the shoulders (10 cm: 0.719; 16 cm: 0.760; smaller head
  instead: 0.682): whole 0.670 (v52). `render_sprite_views.py` EYES points moved with it; at first the visor
  rendered grey because they still sampled the old head position.
- **Fists again (0.605):** fists 1.5x to 1.7x: fists 0.630, whole 0.677 (v53, installed).
- Gorilla's stance now lives in `tools/art/ape_round.sh` (the round script, moved from the scratchpad):
  `base=19;R_leg=16;L_leg=3;L_arm=27`. Parts after the pass: head 0.760, back and rack 0.839, torso 0.884, fists
  0.630, hind legs 0.625. Whole 0.621 (v42) to 0.677 (v53), the gorilla's best against either reference.
- **Gorilla v54 (installed), chest armour (Preston: in S, SW and SE the orange chest plate "looks like its hanging
  off in front rather than tightly folding against its chest"):** `chest_shield` was tipped -18 deg about X, which
  swings a plate's bottom edge forward, and sat 14 cm off the chest front; now +12 deg (bottom tucked back), flush
  at y -1.28, 4 cm shorter. The two `belly_side` plates that hung low and splayed moved up 10 cm, in 6 cm, tucked
  +14 deg and turned 32 deg instead of 50. Whole outline unchanged (0.677); a front-view fix the side measure
  cannot see. Sheet `docs/art/2d/ape_l/chest_v53_v54.png`.
- **Gorilla v55 to v57 (v57 installed), the collar plates (Preston: "the top orange plate thats hanging near collar
  needs same thing"):** `chest_upper` tucked +12 deg and flush at y -1.26 like the shield; the two `chest_side` flaps,
  angled 55 deg out from the collar, folded to 30 deg in v55, which hid the orange in profile (the pass-38 ask) and
  bared the frame in front; 40 deg tucked at the bottom in v56 keeps both. v57 moves the dark chest band and its
  lights back with the collar band. The grey bar under the visor in the front view is the muzzle and jaw (his
  reference has a grey jaw there too). Whole 0.677 to 0.669: the profile carries slightly less orange.
- **Gorilla v58 (installed), the grey plate (Preston: "Add that yellow ... where grey plate is then get rid of
  grey"):** sampled down the front render's centre: visor, socket, green jaw, then the grey bar, then the orange
  shield, so the bar was not the muzzle but `chest_frame` (grey, front face at y -1.30), left standing proud when
  the shield tucked to -1.28. Frame moved 14 cm back behind the armour; the shield grew from 0.62 to 0.76 tall and
  up 8 cm to reach the collar band, the orange covering that area as before the plates moved. Whole 0.668.

## Round 12, shoebill part by part (2026-10-13, Preston: "Next creature ... refining for each creature 1 by 1. Part by part")
Parts against his reference (regions: head and bill 0,0,1,0.3; neck 0.2,0.2,0.75,0.42; body and wing 0,0.3,1,0.68;
legs and feet 0.15,0.62,0.85,1). Start (p28): whole 0.464, head 0.513, neck 0.435, body 0.579, legs 0.294.
- **Legs, stance:** `bird_rig.py` now lets a machine's CFG set its own `stance`; leg-frame trials (at the
  production SPRITE_ORTHO 5.6, where the current stance reproduces the installed 0.464 exactly) picked near 22, far
  2: legs 0.359, whole 0.483. The trials at the renderer's default width read 0.015 high; trial widths must match.
- **Legs, length (p31):** LIFT 0.3 to 0.5, his bare legs about 40% of the height with the body high: whole 0.494.
- **Head (p32):** head group 1.25x to 1.05x (the bill was as wide as the body): whole 0.513, width to tall 0.82
  against his 0.83, neck 0.435 to 0.505.
- **Body and wing (p33):** six primaries fanned back past the rump and down instead of four tucked: whole 0.554,
  head 0.640, neck 0.681, body 0.682.
- **Legs, spread (p34, installed):** STAGGER 0.06 to 0.2, the two legs stand apart with a gap as his: whole 0.637,
  body 0.720, legs 0.392. The shoebill went from the lowest machine to mid-table in one pass.
- **Shoebill pass 2 (Preston: "another part pass on shoebill"), p37 installed:** from p34 (whole 0.637; head
  0.640, neck 0.681, body 0.720, legs 0.392). Step 1 (p35), the egg 12 cm forward so his breast pushes out under
  the neck: whole 0.671, neck 0.738, body 0.769. Step 2 (p36), the primary fan reaching lower: whole 0.678, body
  0.781. Step 3 (p37), legs STAGGER 0.2 to 0.3 and longer toes: legs 0.384 to 0.485 but whole 0.656; split test
  showed the stagger alone makes both moves (p39: whole 0.660, legs 0.475) and the toes are neutral (p38). By eye
  p37's splayed legs are his stance and p36's are not; installed on shape, as Preston has preferred on this bird.
  The build file was restored to p37 and rebuilt (p40) to confirm it reproduces the installed sprite.

## Round 13, wolf part by part (2026-10-13)
Parts against his reference (head 0.6,0,1,0.45; front legs 0.5,0.4,1,1; body 0.25,0.1,0.75,0.6; hind legs
0.1,0.4,0.5,1; tail 0,0,0.3,0.55). Start (v14): whole 0.540; head 0.704, front 0.427, body 0.839, hind 0.585,
tail 0.332.
- **Tail (v18, installed):** his tail runs long from the top of the rump down to about knee height; v12 had
  angled ours up (a misread of the look-compare). Sloped down and lengthened: tail 0.374, whole 0.540.
- **Legs, four approaches, none helped:** front-leg stance frames (7 pairs: front region 0.42 to 0.46, whole up to
  0.548, not enough to keep); stride 0.34 to 0.6 (v19, 0.525); foot paths 20 cm forward and back (v21, 0.506, the
  front legs leaned back instead of reaching); body and leg tops 15 cm higher with legs 25% thinner (v22, 0.514).
  A front-to-back render squash (`SPRITE_SQUASH_Y`, now settable per run) matched the proportion (1.83 to his
  1.82) but lowered the match (0.533). Reading: his wolf's legs form an open A with gaps between near and far legs;
  ours drop near-vertical in the stance and overlap. The fix is in the leg build itself (separate thin jointed
  segments angled out from the shoulder and hip, as in his sprite), not a rig setting.
- `quad_rig.py` now lets a machine's CFG set its own stance, as `bird_rig.py` does.

## Round 14, gorilla against reference 3 (2026-10-13)
Preston sent a new gorilla reference drawn from v58 (back pillars misplaced in it, everything else approved). Installed as `docs/art/reference/starters/ape_l.png`; the previous one is kept as `ape_l_ref2_pre_v58.png`.
- The reference is drawn at our SE angle (3/4 front), not the side. v58 against it: SE 0.756 whole (E only 0.503). SE parts: head 0.899, back 0.822, fists 0.812, hind legs 0.782.
- Stance trials (ten arm/leg/base frames) on E: none past 0.505.
- Fist size: HAND_GROW 2.0 (v59) and 2.3 (v60). v60 SE whole 0.766 but fists part 0.757 (down from 0.812) and on sight the fists rise to the chest, taller than his. Dropped.
- Kept v58. v61 is the v58 rebuild to restore the working blend.

## Round 15, weapons on all six, wolf pass 2 (2026-10-13)
Preston: one more wolf part pass; "add more pieces and parts, it kind of looks like a bare prototype ... wire them and build foundation so codex can generate the reference we need"; "weaponize it up ... for all creatures".
- New shared module `tools/blender/weapons.py`: cannon, missile_pod, gatling, emitter, blade, jet, spikes; detail pieces piston, vent, antenna, cable; anchor()/on() place parts on an existing part's box or surface. Each build has a loadout; `build_loadout()` writes `docs/art/3d/<id>_weapons.json` (parts, roster move or SPARE, muzzle points). `MECH_WEAPONS=0` builds bare.
- Rig fix (quad_rig.py): parts named like `front_foot_1_cap` or `_-1_hub` rode the .R bone on both sides; the side regex now reads them.
- Wolf v26 (= v24): open-A legs (front paw ahead, hind hock back over a thin pastern), thinner leg segments, rams on the upper legs, detail layer, loadout. Scores: whole 0.540 to 0.485 (bare v25 0.491); hind 0.361 to 0.443, front 0.389 to 0.264, head 0.562 to 0.583. Seven stance trials did not recover the front (best 0.296). Installed on shape for the Codex reference; v18 is the fallback.
- Installed: ape_l v62, wolf_m v26, kangaroo_m p30, shoebill_m p42, hippo_m p15, pangolin_m p10. Godot view_art_check PASS (6). Gorilla SE has 1 off-palette pixel.
- Kangaroo p29 and shoebill p41 hid their new weapons (under the shoulder plates; behind the crest and wings); p30 and p42 moved them out.
- Codex brief: `docs/team/CODEX_WEAPONIZED_REFERENCES_2026-10-13.md`, inputs in `docs/art/codex_inputs/2026-10-13/`.
- Wolf v27, wolflike pass (Preston: "make wolf look more wolflike"): head carried above the back on a rising neck (HC z +0.22), a domed forehead with a stop and a muzzle that tapers in the top view (profile_solid top_xy), bigger ears, a bushy tail thickest mid-way. Whole 0.485 to 0.539 (w/h 1.72 against his 1.82), tail 0.189 to 0.434, hind 0.443 to 0.535, front 0.264 to 0.295, head 0.583 to 0.586, SE 0.386 to 0.419. Installed.
- Kangaroo head pass (Preston: "its way off. Ears are uneven everything"): p31 evened the ears (both -14, was -30/0), shrank the head (1.25 to 1.08), raised it on a slimmer neck; head region fell 0.532 to 0.470, one wedge. p32: a rounded skull stepping down to a long narrow snout, the eye on the skull, the far ear 12 cm behind the near one so both show from the side. Head region 0.651, whole 0.678 to 0.647. Installed on shape. Codex inputs updated to v27 and p32.
- Gorilla reference 4 (ChatGPT from v62, 2026-10-13; Preston: "looks awesome", the back pillars right). It came on a dark glowing backdrop; cut out with the new `tools/art/cut_glow_bg.py` (smooth dim gradient reachable from the border = background; scipy installed for it). Installed as `ape_l.png`; ref 3 kept as `ape_l_ref3_v58.png`, the source as `ape_l_ref4_source.png`. v62 against it: SE 0.811, S 0.654, SW 0.611, E 0.543. Brief now asks for transparency first.
- Wolf armor pass (Preston on the ChatGPT render of v26, kept as `wolf_m_chatgpt_v26_source.png`: "still looks like a naked canine, parts stripped robot with weapons"). v28: armor sleeves over each limb segment, shoulder and hip pads with red rims, armored paws, neck side plates, cheek guards, a helmet, chest armor, tail side armor (whole 0.551, tail 0.550; legs still read grey, tail a block chain). v29: sleeves 30-50% bulkier, a heavy haunch, bigger pads, slimmer tail armor, a five-plate ruff over the withers and shoulders. Whole 0.557 (best yet), head 0.620, body 0.792, front 0.305, hind 0.538, tail 0.507. Installed; Codex inputs updated to v29.

## Round 16, the ChatGPT "Mechabeast" references and the gorilla part pass (2026-10-13)
- All six references from `Downloads/Mecha Beasts- ChatGPT references/` installed as `docs/art/reference/starters/<id>.png`; old ones kept as `<id>_pre_mechabeast.png`, sources as `<id>_mechabeast_source.png`. Five were already transparent (the "glow" sat under alpha 0 and only showed when the alpha was dropped); the wolf's glow is baked into partial alpha. New `tools/art/extract_alpha_ref.py`: solid pixels only (alpha >= 200; the wolf at 250), largest pieces, holes filled. `cut_glow_bg.py` is no longer needed for these.
- Current versions against them (E / SE / SW / S): gorilla v62 0.500 / 0.752 / 0.610 / 0.639; wolf v29 0.468 / 0.387 / 0.430 / 0.248; kangaroo p32 0.635 / 0.435 / 0.227 / 0.242; shoebill p42 0.626 / 0.634 / 0.315 / 0.467; hippo p15 0.710 / 0.687 / 0.654 / 0.427; pangolin p10 0.652 / 0.508 / 0.425 / 0.345.
- Gorilla part pass in the SE view (the reference's angle). Parts: head 0.5,0,0.8,0.45; back 0.05,0,0.6,0.25; torso 0.3,0.2,0.75,0.6; near fist 0.33,0.5,0.66,1; far fist 0.66,0.35,1,1; hind 0,0.4,0.33,1.
  - v62: whole 0.752, head 0.882, back 0.653, torso 0.980, near fist 0.886, far fist 0.785, hind 0.738.
  - v63: back rack 12 cm higher (BACK_UP): back 0.794, whole 0.799.
  - v64: stance base 22, R_leg 22, L_leg 34, L_arm 21 (ape_round.sh): whole 0.816, far fist 0.871, hind 0.788. The SW view's far fist draws high from the camera's angle; the S view shows both fists planted.
  - v65: HIND_BACK 0.22 to 0.36: whole 0.833.
  - v66: HAND_GROW 1.7 to 1.9: whole 0.841, head 0.929, back 0.808, near fist 0.903, far fist 0.842, hind 0.783. E 0.499, SW 0.648, S 0.644. Installed; view_art_check PASS.
- Measure fix (2026-10-13): `tools/art/shadow_strip.py`; compare_views.py and part_overlay.py drop the pixelizer's flat ground-shadow line from our sprite (it ran wide under the wolf's spread legs and skewed the box). Gorilla v66 SE 0.841 to 0.847.
- Wolf, new reference (Preston's re-download without the glow, `wolf_m_mechabeast_source.png`; the glow one kept as `wolf_m_mechabeast1_glow.png`). Side view. v29: whole 0.496, head 0.587, body 0.649, front 0.358, hind 0.416, tail 0.412.
  - v30: elbow back (-0.84), paw forward (-1.36): front 0.325, dropped on its own.
  - v31: UP 0.3 to 0.55 with the shoulder, hip, elbow, knee and hock raised to match (his legs near half the height): whole 0.493, body 0.675, front 0.387, tail 0.506, head 0.574, hind 0.413.
  - v32: paws further apart (wr -1.58, hock 1.42): front 0.317, hind 0.372; the length is set by the head and tail tips, and it read as sliding. Dropped.
  - v33: head 28 cm higher, tail fins lower: whole 0.363, a llama neck. Dropped.
  - Installed v34 (= v31, pixel-identical). SE 0.362, SW 0.439, S 0.217.
- Shoebill part pass against its Mechabeast reference (2026-10-13), drawn at our SE angle. Parts (SE): head 0.35,0,1,0.3; neck 0.3,0.15,0.7,0.42; body 0,0.3,0.85,0.65; legs 0.15,0.6,0.85,1.
  - p42: whole 0.632 (w/h 0.72, his 0.79), head 0.677, neck 0.837, body 0.778, legs 0.333.
  - p43: LIFT 0.75: whole 0.624, w/h 0.68 (ours already too tall). Dropped.
  - p44: legs splay to the feet (knee x 0.26, ankle 0.3, foot 0.32), stance near 2 far 22: whole 0.650, legs 0.408.
  - stance trials on p44: near 6 far 24 best (whole 0.657).
  - p45: bill a pointed wedge narrowing in the top view, hooked nail; Stillwater Lance thinner and longer on a small mount: whole 0.658, head 0.698; from the side the bill read as a blade (E 0.543).
  - p46: bill deep at the base, still pointed: whole 0.662, head 0.710, neck 0.824, body 0.771, legs 0.409. E 0.550, SW 0.309, S 0.440. Installed; view_art_check PASS.
- Kangaroo part pass against its Mechabeast reference (2026-10-13; side view; Preston: the reference has no hip boosters, ours keep them). Parts (E): head 0.55,0,1,0.3; arms 0.5,0.3,0.95,0.6; body 0.3,0.25,0.75,0.75; feet 0.3,0.75,1,1; tail 0,0.5,0.45,1.
  - p32: whole 0.644 (w/h 1.05, his 1.14), head 0.580, arms 0.693, body 0.842, feet 0.706, tail 0.746. Hop frames 0-26 tried: base 3 stays best.
  - p33: chest and belly pushed forward into a rounded front (was flat at y -0.3), arms 14 cm forward with it: whole 0.675.
  - p34: lower belly further forward, knee forward and up (-0.4, 0.7): whole 0.701, feet 0.747.
  - p35: head forward and lower (HC -0.72, 2.48), ears 0.6 to 0.5: whole 0.701 (w/h 1.14, his 1.14), head 0.593, body 0.875, feet 0.712, tail 0.704. SE 0.442 to 0.499, S 0.247 to 0.264. Installed; view_art_check PASS.
- Shoebill pass 2 (2026-10-13): nothing beat p46 (SE 0.662). STAGGER 0 (p47) 0.647 and -0.3 (p48) 0.582, 0.5 (p49) 0.649; shorter wing tips with LIFT 0.62 (p50) 0.621, too narrow (w/h 0.68, his 0.79); hips wider apart (p51) 0.655; head group 1.15 (p52) 0.661. p46 kept; the build file and blend restored (p53 pixel-identical to p46).
- Kangaroo pass 2 (2026-10-13): p36 ears near upright (tilt -14 to -3) and narrower, head 7 cm back: whole 0.731, arms 0.771, body 0.890. p37 head 12 cm higher: 0.719 (taller overall), dropped. p38 = p36 + far ear 20 cm behind (a gap, his) + snout 10% shorter: whole 0.742, arms 0.805, body 0.886, feet 0.779, tail 0.731; head part 0.509 (its box now tops at the ear tips; on sight the closest head yet). SE 0.487, S 0.265. Installed on shape; view_art_check PASS.
- Kangaroo p39 (Preston: "ears positioning looks good on most except where one ear is floating or one is missing"): p38's far ear sat 20 cm behind the near one, behind the skull, floating in E and W. p39: 8 cm behind, both on the skull, splayed 14 degrees so both show front and back. Whole 0.742 unchanged. Installed.
- Pangolin part pass against its Mechabeast reference (2026-10-13; side view). Parts (E): head 0.72,0.2,1,0.75; back 0.3,0,0.8,0.5; legs 0.35,0.55,0.95,1; tail 0,0.2,0.4,1. p10: whole 0.677, head 0.584, back 0.744, legs 0.717, tail 0.626. p11: the dome peak forward over the shoulders and steep to the head (TOP), the tail a straight decline (control point 0.8 to 0.55), the head group 1.25x and 6 cm lower: whole 0.716, head 0.637, back 0.764, legs 0.747, tail 0.751; SE 0.557, S 0.351. Installed; view_art_check PASS.
- Wolf pass 3 (2026-10-13). Walk-frame stances on v34: best 0.507 (forelegs worse). Column profiles: the reference stands in a long stride, feet across the whole length, a fore paw under the nose; no walk frame puts the feet there.
  - v35: antenna raked below the ear tips (the top is the ear tip, as his; no change) and stride 0.65: whole 0.462. Dropped.
  - New: `quad_rig.battle_pose_for(cfg)` and a "battle" clip when cfg has "battle_feet" {"R_arm": (dy, dz), ...}: each foot moved from its planted target, two-bone IK for the leg. The renderer holds a clip when SPRITE_STANCE has "clip=battle;frame=1".
  - v36: feet (-0.45, 0.15, 0.35, -0.25): whole 0.407, the layout too far back.
  - v37: feet R_arm -0.8, L_arm -0.2, R_leg 0.1, L_leg -0.45: E 0.472 (v34 0.493), head 0.603, body 0.705, front 0.358, hind 0.327, tail 0.452; SE 0.362 to 0.520, SW 0.430, S 0.224. A striding wolf like his.
  - v38: hind feet further forward: E 0.457, SE 0.482. Dropped.
  - Installed v39 (= v37, pixel-identical); view_art_check PASS.
- Hippo part pass against its Mechabeast reference (2026-10-13; side view, the SE close behind). Parts: head 0.68,0.1,1,0.75; back 0.1,0,0.7,0.4; body 0.1,0.3,0.7,0.75; front 0.55,0.6,0.9,1; hind 0.05,0.6,0.45,1.
  - p15: E 0.741 (head 0.682, back 0.863, body 0.968, front 0.519, hind 0.594); SE 0.725.
  - p16: battle_feet R_arm -0.45, L_arm -0.25, R_leg 0.25, L_leg -0.3 (stance clip=battle): E 0.740, hind 0.705; SE 0.783.
  - p17: fore paws -0.7 / -0.45: E 0.737 (head 0.689, front 0.514, hind 0.701); SE 0.813 (front 0.792). Installed; view_art_check PASS.

## Round 17, Codex tasks and a factory-wide pass (2026-10-13)
- Codex task list written: `docs/team/CODEX_TASKS_2026-10-13.md` (Claude builds and wires, Codex finishes: sel-out on all eight views per machine, gorilla first; then the battle check; texture sheets and the pixel-3D world queued until Claude wires them). CODEX_START_HERE.md and CODEX_TASKS.md now point to it. The gorilla is left alone in this pass so Codex can start on it.
- Pangolin: battle pose p12 (E 0.693, w/h 2.77, too long; SE 0.618) and a shorter stride with the tail 20 cm shorter p13 (E 0.710, w/h 2.64; the snout gun sets the front). p11 kept (blend restored, p14 identical).
- Wolf: thin spiked tail v40 (his newest reference): whole 0.468, tail 0.445, no gain; the tail already sits where his does. v39 kept (blend restored, v41 identical).
- Hippo p18: head 12 cm lower and 1.12x: E 0.749 (head 0.689 to 0.750, front 0.564), SE 0.808. Installed.
- Shoebill p54: a tighter wing fan: SE 0.644, worse. p46 kept (blend restored, p55 identical).
- Kangaroo p40: gloves 12 cm further forward: E 0.750 (arms 0.810), SE 0.490. Installed. view_art_check PASS.
- Kangaroo pass 3 (2026-10-13, Preston: "Kangaroo pass, also skill up with the synthesis"). Stock-take: the mech skill-up handoff (`docs/team/CLAUDE_MECH_SKILLUP_HANDOFF_2026-10-12.md`), the reference, the outline and part measures, the headless kit. New tool `tools/art/column_profile.py`: top and bottom edges per column and left and right per row, ours against the reference, so a pass can see where the outline differs instead of only how much.
  - Profile of p40: his head and ears 8% of the width further back, his snout higher; his arms reach forward at shoulder height; his knee further forward; our feet run past his toes.
  - p41: head 15 cm back, elbow, wrist and fingers raised (1.58 / 1.76 / 1.72), knee forward (-0.5, 0.74), toe 10 cm shorter: E 0.778 (arms 0.813, body 0.861), SE 0.458.
  - p42: gloves 8 cm back and 8 cm higher (they overshot at chest height), toecaps shorter, rocket pod further back: E 0.779 (arms 0.821, body 0.875, feet 0.732, tail 0.736), SE 0.476. Installed; view_art_check PASS.
- Column-profile pass (2026-10-13, Preston: "go").
  - Kangaroo p43: snout higher and shorter, gloves back: E 0.772, the snout row overshot. p42 kept (blend restored, p44 identical).
  - Pangolin: the profile showed our head, snout and chin gun took the front 25% of the length (his 15%), and the dome already ended where his does relative to the body. p15 (dome held high to a steep front, front legs forward, tail shorter): 0.712, no gain. p16 (from p11: snout 12% shorter, chin gatling 0.5 to 0.3 m and further back): E 0.756 (head 0.757, back 0.816, legs 0.758, tail 0.751), SE 0.582, w/h 2.50 (his 2.43). p17 (front legs further forward): 0.754, no gain. p16 installed (blend restored, p18 identical); view_art_check PASS.
  - Shoebill: SE profile shows his two legs apart at shin height (0.39-0.63) and ours merged. Seven leg-frame pairs on p46: none beat it (best legs 0.427 with both legs on frame 1, whole 0.653). p46 kept.
- Shoebill battle pose (2026-10-13, Preston: "go"). New `bird_rig.battle_pose_for(cfg)` and a "battle" clip when cfg has "battle_legs" {"R": (dy, dz, splay), "L": ...}: the ankle moved by dy and dz, IK on thigh and shin, the leg swung out sideways by splay degrees about the thigh's own Z, the tarsus turned back so the toes stay flat; the head takes the walk's first-frame tilt (cfg "battle_head", default -3).
  - p56: R -0.08, L 0.08, splay 12, head at rest: SE 0.634 (head 0.627: the walk frame had tilted the head 3 degrees). The legs stand apart in SE.
  - p57: head tilt restored, R -0.16, L 0.14, splay 10: SE 0.671, legs 0.434.
  - p58: splay 16: SE 0.676 (head 0.706, neck 0.825, body 0.776, legs 0.454), E 0.541, S 0.461. Installed; view_art_check PASS.
- Wolf pass 4 (2026-10-13, column profile). Profile of v39: his back line sits higher against the ear tips (our head and tall ears stood too far above the back), his fore paw reaches under the nose (ours could not: the IK target was out of reach, so the rig lifted the paw), and all his legs sit a little forward of ours.
  - v42: head 10 cm lower, ears 0.44 to 0.34 tall, shoulder and elbow 20 cm forward, fore feet -0.7 / -0.15: E 0.566 (head 0.640, body 0.808, front 0.366, tail 0.546), SE 0.538.
  - v43: hind feet 25 cm forward (-0.15 / -0.7): E 0.587 (head 0.642, body 0.814, front 0.365, hind 0.484, tail 0.574), SE 0.517, SW 0.345, S 0.221. Installed (blend restored, v45 identical); view_art_check PASS.
  - v44: fore feet further forward (-0.95 / -0.35): front 0.266, whole 0.563. Dropped.
- Synthesis stock-take (2026-10-13, Preston: include the stored GitHub repos, the Hollowtide lessons, the downloaded models, the Zoids sprites). Written into `docs/plan/synthesis-tool-roster-2026-10-12.md` ("Stored sources"). Study of three Zoids quadruped rips (wolf, fox, lion types; structure only, side renders and proportions in the session scratchpad): big round joint hubs at shoulder, hip and knee, light steel legs between dark body armour; his reference shows the same.
- Wolf v46: lower-leg guards near-black to the palette's light steel, shoulder/hip hubs 0.12 to 0.17 and knee/elbow discs 0.14 to 0.19, set proud of the armour: E 0.589 (front 0.371, hind 0.490), SE 0.518. Installed; view_art_check PASS.
- Shoebill column-profile pass (2026-10-13). Profile of p58 (SE): our bill hung lower, our wing tips drooped lower on the left, our toes and breast guns reached past his.
  - p59: battle_head +4, primaries drop 0.09 to 0.065 per feather, toes 0.66/0.56 to 0.5/0.46: SE 0.621 (head 0.572: positive tips the bill down).
  - p60: battle_head -8: SE 0.682 (head 0.699), E 0.564.
  - p61: breast guns 0.4 to 0.22 long: SE 0.684 (head 0.699, neck 0.826, body 0.757, legs 0.442), E 0.568, S 0.459. Installed; view_art_check PASS.
- Shoebill p62 (Preston: "east view for shoebill the gun isnt attached on top of head"): `weapons.cannon` takes `post`, a pylon from a body point to the mount; the Stillwater Lance stands on one from the skull, its mount 5 cm lower (0.16 to 0.11 above the head). Attached in all eight views. SE 0.682, E 0.549 (p61 0.684 / 0.568). Installed.
- Hippo column-profile pass. Profile of p18 (E): his head top sits well below ours; his lowest feet are mid-length, ours stood far back. p19: head a further 12 cm lower (HC z 0.84 + LIFT), hind feet toward the middle (R_leg 0.0, L_leg -0.55): E 0.760 (head 0.807, back 0.855, front 0.576, hind 0.653), SE 0.784 (p18 0.808). Installed on the side view, his angle. view_art_check PASS.
- Wolf v47 (column profile of v46): his ears read as two broad triangles (ours edge-on spikes), his far fore leg stands back at two-thirds of the length (we had nothing there). Ears turned out 12 to 38 degrees, far fore foot L_arm -0.15 to +0.2: E 0.603 (head 0.647, body 0.817, front 0.371 to 0.516, hind 0.474, tail 0.563), SE 0.516, SW 0.368. Installed; view_art_check PASS. The near fore paw still stops short of his (at the leg's reach).
- Wolf v48 (column profile): his head ear-to-nose is about 16% of the length, ours 22%; the near fore paw cannot reach his nose by leg length (straight reach at the floor about 0.5 m ahead of the shoulder). Muzzle 25% shorter beyond the eyes (skull and jaw side and top outlines, fangs, nose, head plates, chin): E 0.618 (head 0.647 to 0.719, body 0.830, front 0.537, hind 0.477, tail 0.557), SE 0.508, SW 0.370. Installed; view_art_check PASS.
- Wolf claws (Preston: "for east view wolf the claws look like one line instead of 3. Needs some love"): four claws side by side at one angle stacked into one red line from the side. v49: three claws per paw, each a knuckle segment and a hook, fanned (middle longest and lowest, outer two shorter and higher). v50: chunkier (0.075/0.065 wide) and a wider fan. Three separate hooks in E, SE and W. E 0.612 (v48 0.618), SE 0.501. Installed; view_art_check PASS.
- Claw pass for the others (2026-10-13, after the wolf's claws): feet zoomed in E.
  - Pangolin p19: the three red claws curled under each foot at one depth stacked into one line and hid; now `claws()` fans three hooks forward from each foot's front (as the wolf's). E 0.760 (legs 0.767). Installed.
  - Hippo: four cream nails in one row merged into one nub. p20 set them round the pad's front curve (still one nub at sprite size); p21 bigger (0.12 x 0.13 x 0.13) and wider (angles +-80/+-22, radius 0.24): two nails show per foot in E, more in SE. E 0.756, SE 0.784. Installed.
  - Kangaroo p45: the two toe claws were dark on a dark foot; now accent orange, bigger and fanned. E 0.779. Installed.
  - Shoebill: toes read fine; unchanged. view_art_check PASS.
- Wolf foreleg (column profile of v50): our near fore paw sat higher than the hind feet; the battle pose asked more reach than the leg had (straight reach about 0.5 m ahead of the shoulder, the rest paw already there), so IK lifted it. v51: elbow back and down (-0.62, 0.95), a 1.8 m leg; near hind 0.0, far hind -0.85, near fore -0.6: E 0.603 (hind 0.580), SE 0.420; the paw planted. v52: elbow partway (-0.8, 1.0): E 0.643 (head 0.718, body 0.829, front 0.549, hind 0.618, tail 0.586), SE 0.459, SW 0.379. Installed; view_art_check PASS.
- Shoebill column-profile pass 2 (2026-10-13). Profile of p62 (SE): his legs fill half what ours did at shin height (9% against 21%) and his near leg stands further out; our body and folded wings start higher and run wider through the middle.
  - p63: thighs 0.2/0.14 to 0.15/0.1, shins 0.09/0.075 to 0.06/0.05, tarsus 0.08/0.07 to 0.055/0.05, splay 16 to 22: SE 0.677 (head 0.732, legs 0.421), E 0.556, S 0.420.
  - p64: the thin legs at splay 16: SE 0.675, S 0.455.
  - p65: body and wings 0.9x: SE 0.663, w/h 0.71 (his 0.79), too narrow. Dropped.
  - p63 installed on shape (thin grey legs as his; level with p62's 0.682 within noise; blend restored, p66 identical). view_art_check PASS.
- Shoebill p67: knee and ankle gold blocks 0.21/0.19/0.21 to 0.14/0.13/0.14 to suit the thin legs: SE 0.679, E 0.559. Installed; view_art_check PASS.
- Pangolin p20 (column profile of p19): his scale armour stays high almost to the head (top at 0.11 of the height at 84% of the length; ours had dropped to 0.40). Dome front raised (TOP front (-0.9, 1.22), (-0.65, 1.44); side front 1.05) and three overlapping neck scales bridging to the head: E 0.774 (head 0.819, back 0.840, legs 0.767, tail 0.751), SE 0.591, S 0.348. Installed; view_art_check PASS.
- Hippo p22 (column profile of p21): our fore feet sat higher than the hind (out of reach, lifted), his feet gather mid-body and his tallest point (the torpedo tubes) is mid-back. Fore feet back within reach (-0.42 / -0.22), hind feet forward (-0.2 / -0.75), torpedo pod forward (fy 0.6 to 0.44), head 8 cm lower: E 0.748 (hind 0.522), SE 0.747. Worse; p21 kept (blend restored, p23 identical).
- Hippo p24: the foreleg stood nearly straight (no forward reach), so the battle pose lifted the fore feet, as the wolf's. Elbow back and lower (-0.4 SQ, 0.42 + LIFT/2), fore feet -0.45 / -0.25, hind as p21: E 0.771 (head 0.785, back 0.846, body 0.969, front 0.607, hind 0.653), SE 0.737 (p21 0.784). Fore paws planted. Installed on the side view, his angle; view_art_check PASS.
- Gorilla battle animation now has a permanent tool: `bash tools/art/ape_anim_round.sh` (plan and jobs in `tools/art/ape_l_anim_plan.json` and `ape_l_anim_jobs.txt`). Run it after installing any new gorilla build.
- Battle check (2026-10-13): the battle draws each machine's side view (`art/machines/<id>/views/e.png`, mirrored for the enemy) through `scripts/ui/machine_anim.gd`, so the side view is the one that shows in play; the SE drops on wolf v52 and hippo p24 do not reach the battle. The gorilla alone uses an animation set (`art/machines/ape_l/anim/`), and it was stale: exported 2026-10-12 from a pre-v58 build. Re-rendered all 51 frames of the seven clips (idle, gait, punch, slam, throw, hit, death; plan in the session scratchpad's anim_plan.json) from the v66 blend, pixelized with PIXEL_NO_CROP=1 (export_anim needs one canvas; the default crop broke it on the first try), packed with `tools/art/export_anim.py`: 149x148 canvas, feet row 121. Old set backed up in the session scratchpad. Battle capture (`tools/debug/battle_capture.gd`) shows v66 punching hippo p24. view_art_check PASS.
- Wolf v53 (column profile hint: hind feet back, R_leg 0.0 to 0.2, L_leg -0.85 to -0.65): E 0.621, hind 0.618 to 0.422. Worse; v52 kept (blend restored, v54 identical).
- Battle animation foundations for all starters (2026-10-13): see docs/plan/battle-animation-starters-2026-10-13.md.

## Round 18, factory pass with the synthesis (2026-10-14, Preston: "skill up with the synthesis then do a factory pass"; "Use the synthesis too during the factory pass")
- Stock-take: the roster (`docs/plan/synthesis-tool-roster-2026-10-12.md`), the Legacy bands from the Zoids sprites (`factory_report.py`), the references and outline tools (`compare_views.py`, `column_profile.py`), PixelLab's free workbench as the second scorer, the kept Blender renders. Gemini MCP failed to connect; nothing paid was used.
- Every kept render (`docs/art/2d/<id>/renders/`) re-pixelizes to the installed build pixel for pixel (wolf v52, kangaroo p45, shoebill p67, hippo p24, pangolin p20), so palette trials need no Blender run. Trial script: `ramp_trial.py` in the session scratchpad.
- Where each stands (outline overlap with his reference): gorilla SE 0.847, pangolin E 0.774, kangaroo E 0.779, hippo E 0.771, shoebill SE 0.679, wolf E 0.643. Legacy bands: wolf, kangaroo and shoebill sit under 27 colours.
- Longer ramps (midpoints inserted): colours into the band (kangaroo 31, shoebill 34-43, wolf 27-34) but stray and near-black rose and the sprites looked the same at game size. Darker family gamma (kangaroo red 1.3-1.7, shoebill blue 1.5-1.7): highlight share barely moved (a bright coat stays bright). Both dropped.
- Wolf feet (new `feet.py`, scratchpad: the blobs in the bottom tenth, x as a share of the length): our feet already sit where his do along the length; his near fore paw is the one further back and his far one reaches under the nose, ours the reverse. v55 (swapped): E 0.637; v56 (far paw -0.4): 0.604; v57 (-0.45, -0.08): 0.600. The far paw lifts out of reach. All dropped; v52 kept (blend restored, v58 identical).
- PixelLab scores (side views): wolf 89.2, kangaroo 90.9, hippo 91.4, gorilla 92.4, shoebill 93.2, pangolin 95.2. Top deductions: singletons, holes, near-duplicate colours. Our `near_duplicates.py` found the wolf's extra highlight 82829a sat 2.8 from the ramp top 84849a (a leftover); hippo's dark purple and grey ramps run in parallel (10-21 apart) and the gorilla's outline 181f1c sits 13 from its darkest green (both left: design, and the gorilla is Codex's).
- Wolf v59: grey extra top a0a0b4 (same 21 colours): PixelLab 89.2 to 92.2. Kangaroo p46: red dither 0.25 to 0.1: side-view stray 18% to 16% (into the band), PixelLab 91.1. Same renders, so the shapes are unchanged. Both installed with their battle animation sets re-pixelized from the kept frames (`export_anim.py`, no re-render). view_art_check, battle_check and foundation_check PASS.
- Transfer route for PixelLab: `get_upload_url` then `curl -F file=@<png>`; the `upload:<id>` ref goes to the workbench. The old 4 KB base64 limit no longer matters (an indexed PNG also fits under it).

## Round 19, the Legacy look slice on the wolf (2026-10-14, Preston: "Still doesn't look like it could pass as a zoids sprite. Gorilla is closest"; then "go" on dropping the near-black and the true-black wolf)
- Gap measured against 84 Legacy battle sprites: `docs/reference/sprite-rules-legacy-2026-10-14-gap.md`; new tool `tools/art/legacy_gap.py` (fill, thin parts, brightness, near-black and lit shares against the Legacy quartiles).
- New renderer knobs (`render_sprite_views.py`, all off by default so older rounds re-render the same): `SPRITE_CAVITY=1` (ridges lit, creases dark), `SPRITE_SPECULAR=1`, `SPRITE_MATCAP=<name>` (Workbench matcap light), `SPRITE_ELEV` (degrees, default 10), `SPRITE_E_TURN` (the side view turned toward the viewer). Pixelizer palette keys: `seam_shade`, `side_drop`, `seam_share` (plate lines only where a block is mostly seam: at 0.12 any part boundary marked its block and about half the wolf was drawn as dark plate lines), `shadow` (the ground line's two colours).
- v60: camera 18 degrees up, side view turned 20 degrees toward the viewer, cavity and specular, palette lifted (grey 26262e to cacada plus e2e2ee, red one step lighter, violet ground line). v61: leg sleeves, guards and paws thicker (fill 0.40 to 0.43, thin 0.28 to 0.25). v62 to v64: matcaps toon_light, hard_surface_grey, fullmetal, plate lines at seam_share 0.35, grey gamma 0.7, edges two shades down.
- Legacy gap, side view: v59 mean 33, near-black 0.80, lit 0.00, fill 0.37, thin 0.29; v62 (toon_light) mean 71, near-black 0.34, lit 0.10, fill 0.43, thin 0.25 (Legacy medians 96, 0.08, 0.12, 0.51, 0.22; Shadow Fox, a dark machine, 94 and 0.09). v63 mean 60, v64 mean 69.
- v62 installed (renders made with `SPRITE_MATCAP=toon_light.exr SPRITE_CAVITY=1 SPRITE_ELEV=18 SPRITE_E_TURN=20`; the round script inherits them), battle animation set re-rendered with the same settings. view_art_check and battle_check PASS; battle capture `docs/art/2d/battle_wolf_m_vs_hippo_m.png`. The outline match against Preston's Mechabeast reference no longer applies to the side view (it is turned now).
- Still short of Legacy: the torso is flat box plates (one shade per face), the head is small and unclear, near-black 0.34 against 0.08. Next: rounded, layered body and head armour in the model; then the same settings on the other five; then Codex's hand finish.

## Round 20, the Legacy look and a detail pass on all six (2026-10-14, Preston: "Go also you can add parts and pieces so that the image codex generates give you an awesome reference ... you don't have to make it look too pretty. Do that for all")
- New `tools/blender/greebles.py`, called by every build just before it tags parts to bones: on each large part a raised panel (framed every other time) or a vent on each outward side face, two bolts in the part's own colour, a layer plate on top (an accent one in four), and a piston alongside long limb parts. Each piece is renamed `<host>_9NN` and kept only if the build's own bone rule puts it on the host's bone. Builds pass `skip_prefix` for parts that are already detail (pangolin scales; shoebill feet, shins and toes). `MECH_GREEBLES=0` builds without it. Kangaroo's bone rule moved into `kangaroo_bone()`; the gorilla calls it through `_greebles()`.
- Fixes found by looking: pistons on parts running left to right stuck rods out at the floor (gorilla v67); bolts on a missed ray floated (shoebill p68); dark bolts read as noise (hippo p25); panels over the pangolin's scales turned it to speckle (p21).
- The Legacy look is now the default render for every machine: `tools/art/legacy_look.json` (toon_light matcap, cavity, camera 18 degrees up, side view turned 20 degrees toward the viewer, plate lines at seam share 0.35, the ground line under every foot), exported by `tools/art/legacy_env.py` from creature_round, anim_round, ape_round and ape_anim_round. `LEGACY_LOOK=0` renders the old way. Palettes for hippo, pangolin, shoebill and kangaroo lifted as the wolf's (ramps start at brightness 36 or more, greys run to light steel, edges two shades down, violet ground line); the gorilla keeps Preston's ramps.
- Builds: gorilla v68, wolf v66, kangaroo p48, shoebill p69, hippo p26, pangolin p22. Legacy gap, side view (Legacy medians: mean 96, near-black 0.08, lit 0.12, fill 0.51): gorilla mean 80, near-black 0.25; wolf 66, 0.39; kangaroo 74, 0.18; shoebill 92, 0.00; hippo 73, 0.27; pangolin 83, 0.00.
- Four-view sheets for Codex's new reference images: `docs/art/2d/sheets/<id>_<version>.png` (new tool `tools/art/view_sheet.py`; it rewrote `ape_l_v66.png` in its own layout from the same views).
- Installed with their battle animation sets re-rendered in the same look: gorilla v68, wolf v66, kangaroo p48, shoebill p69, then pangolin p23 (camera 14 degrees: at 18 its N view stood 26% taller than its side view and view_art_check failed) and hippo p27 (plate lines one step up, purple and grey gamma 0.5: mean 73 to 88; it read too dark on the battle ground). `ape_anim_round.sh` wrote its frames under `C:\docs` (Blender takes a relative path from the drive root); its output path is absolute now and the two stray files were removed. view_art_check, battle_check, foundation_check and start_chain_check PASS. The shoebill's two tiny floating toe bits in S and SW were already in p67.

## Wolf against Mechabeast V2 (2026-10-14, Preston: "here is new wolf reference V2. Im naming these ones v2 in folder and keeping our previous references")
- Reference installed as `docs/art/reference/starters/wolf_m.png` (source `wolf_m_mechabeast2_source.png`, alpha cut 200: one piece; 250 left 725 specks); the first Mechabeast one kept as `wolf_m_mechabeast1.png`. Gorilla V2 is in `docs/plan/creature-factory-2026-10-14-gorilla-v2.md`.
- v66 side view (turned 20 degrees) 0.560. His differences: tail nearly level at back height with big silver spikes (ours drooped to knee height), hind feet further back, taller back with red plates, lighter steel (mean 79 against 66), brighter red (mean R 190 against 149).
- v67: tail level (z 1.22 to 0.9 + UP over 1.2 m), tail fins silver and bigger, red spine plates bigger, hind feet back (R_leg 0.25, L_leg -0.55): 0.611. v68: spine plates taller: 0.612; grey gamma 0.4 and grey plate lines one step up: mean 80. v69: red gamma 0.6 (mean R 170). Installed with its battle animation re-rendered; view_art_check and battle_check PASS. Sheet `docs/art/2d/sheets/wolf_m_v69.png`.
- Still short: he carries twice our red (15% of pixels against 8%) and his near fore paw reaches further forward under the head (at our leg's reach).
- Wolf V2 pass 2 (2026-10-14, Preston: "go"). v70: the top plate of each back band red, forelegs 10 cm forward (near fore paw now 0.86-0.98 of the length): 0.631; red share unchanged at 8% (the detail pass's layer plate on the torso core covered the red back). v71: the core skipped by the detail pass (`skip_prefix=("torso_core",)`): no change in red from this camera. v72: red upper flank plates on alternate bands: red 9%. His reference is drawn from higher: side view at 24 degrees 0.677 (18: 0.631; 30: 0.678), red 10%. v73 at 24 for every view failed view_art_check (front and back views a third taller); new `SPRITE_SIDE_ELEV` raises only the side views. v74: side views 24, the rest 18 (`tools/art/legacy_look.json`): side view 0.677, mean 80, near-black 0.11, lit 0.12. Installed with its battle animation; view_art_check and battle_check PASS. Sheet `docs/art/2d/sheets/wolf_m_v74.png`.

## Kangaroo against Mechabeast V2 (2026-10-14, Preston: "kangaroo v2 didnt get right shoulder gun right but still good", "nor hip boostrs")
- Reference installed as `docs/art/reference/starters/kangaroo_m.png` (source `kangaroo_m_mechabeast2_source.png`, cut 200, one piece); the first kept as `kangaroo_m_mechabeast1.png`. Our shoulder gun and hip boosters stay as they are.
- p48 side view 0.522 (front-right turns did not help: 35 degrees 0.520). His kangaroo stands tall in a split boxing stance, the near foot back and the far one forward; ours crouched feet together in the hop's frame.
- New `battle_pose()` in build_kangaroo_m.py and a "battle" clip (the stance file is now `clip=battle;frame=1`, and the battle clips stand in it): the hop's planted crouch with the feet split (BATTLE_FEET, positive is back), the body raised with the feet held on the floor (BATTLE_RISE), the tail lifted (BATTLE_TAIL). p49 split 0.35: 0.560. p50 split 0.5, rise 0.25, tail +10: 0.618. p51 split 0.7: 0.622; side views at 24 degrees 0.636, at 30 degrees 0.650 (w/h 1.10, his 1.13). p52: side views at 30 (`tools/art/legacy_look.json`): 0.650. Colour already matches (mean 73, his 70; red 51%, his 53%, same shade). Installed with its battle animation; view_art_check and battle_check PASS. Sheet `docs/art/2d/sheets/kangaroo_m_p52.png`.
- Still different: his chest and belly bulge further forward with the fists out in front.

## Shoebill, hippo and pangolin against Mechabeast V2, and dither off (2026-10-15, Preston: "go")
- References installed from Downloads ("<Name>-Mechabeast V2", cut 200, one piece each) as `docs/art/reference/starters/<id>.png`; the first Mechabeast ones kept as `<id>_mechabeast1.png`, sources as `<id>_mechabeast2_source.png`.
- Best matches before the pass: hippo front-right 0.802 (side 0.755), pangolin front-right 0.786 (side 0.698), shoebill side 0.594. These three are drawn more front-on than our 20-degree side view; turning the side view 35 degrees: hippo 0.796, pangolin 0.820, shoebill 0.604 (`tools/art/legacy_look.json`; the pangolin's side view at 18 degrees, the rest of its views at 14).
- Dither off in every palette (wolf, kangaroo, shoebill, hippo; the pangolin had none): Legacy sprites do not dither and the V2 references are clean flat plates. Most visible on the hippo's head.
- Hippo leg length: p28 (SQ 1.0, LIFT 0.2) overshot, front-right 0.763; p29 (0.9, 0.1) side 0.762, front-right 0.782.
- Installed with battle animations re-rendered (hippo, pangolin, shoebill) or re-pixelized (wolf, kangaroo): hippo p30, pangolin p24, shoebill p70, wolf v75, kangaroo p53. view_art_check, battle_check, foundation_check, start_chain_check PASS. Sheets in `docs/art/2d/sheets/`.

## Plate cleanup, blind reviews and a parallel part pass (2026-10-15, Preston: "go")
- Blind review 1 (five independent reviewers, A/B order hidden, `scratchpad/blind/`): new builds closer for wolf, hippo, pangolin (medium), shoebill a tie, kangaroo old preferred (low). Every reviewer named speckled plates first.
- Plate cleanup in `tools/art/pixelize_render.py`: `PIXEL_MIN_CLUSTER` merges one-shade patches under that many pixels into the shade most of their neighbours have (same family first; the eye is left alone); set to 4 for every machine in `tools/art/legacy_look.json`. Tiny patches on the side views fell 60 to 87%. Gorilla v71: its v70 renders and animation frames re-pixelized with it.
- Part pass, one agent per machine in parallel (own build and palette only, at most five rounds, a change kept only if the side-view outline held and it looked closer): wolf v80 (palette red ramp 6a0a10 to f85a4a, accent e01818, red tail tip; pale hooked tail spikes tried three ways and reverted, each cost 0.006 to 0.016), kangaroo p57 0.650 to 0.688 (tail lowered, BATTLE_TAIL 2; tail left bare by the detail pass; two upright ears; thigh 1.3x, hip disc 0.2, calf plate bigger, orange foot further forward; near foot 0.45 back; far shin lighter), shoebill p75 0.604 to 0.627 (four stepped navy wing blades with lighter edges, the wing 8 degrees lower; torso plate merge and gold caps reverted), hippo p35 0.796 to 0.867, front-right 0.857 (legs 1.6x thicker and upright, toes 2x, brighter pink panels 9a72a2, near-black joints, hip and shoulder wheels out on the hull; plate merge and top turret reverted), pangolin p29 0.819 (grey knee pads, orange ramp trimmed).
- Blind review 2 (new against the builds installed before): wolf, shoebill, hippo new (medium), kangaroo new (low), pangolin old (low: the grey knee pads turned its front leg grey where the reference keeps orange). The pangolin went back to its pre-pass build and palette (agent's p29 files kept in `scratchpad/blind/pangolin_p29_kept/`); p30 is that build with the plate cleanup, pixel-identical to the agent's baseline p25.
- Installed with battle animations re-rendered: gorilla v71, wolf v80, kangaroo p57, shoebill p75, hippo p35, pangolin p30. view_art_check, battle_check, foundation_check, start_chain_check PASS. Sheets in `docs/art/2d/sheets/`.
- Reviewers' next gaps: wolf claws thicker and bright red, near-white limb plating, big pale tail spikes (needs the tail lowered first); kangaroo legs split with a hip disc, fists pushed forward; shoebill torso as 4 to 6 pale plates, straighter shins; hippo panels 30 to 40% lighter, legs separated; pangolin snout 30% longer and level, legs separated with orange shins.

## Part pass 2 with a blind judge per machine (2026-10-15, Preston: "go")
- One workflow, per machine: an agent fixes the second review's gaps in its own build and palette (a change kept if it looks clearly closer and the side outline stays within 0.005 of the best), writes a blind A/B image against the installed build, then a separate reviewer judges it without knowing which is new (`scratchpad/blind3/`).
- Wolf v84 (0.677 to 0.694; judge: new, medium): tail lowered to droop lower-left (TAIL z to 1.22/1.13/1.0/0.84/0.64), three-segment claws twice as thick in a brighter 'claw' red ff3028, six near-white tail blades ('blade' d4d4da) on the first three tail segments, limb plating 'light' 6e6e7c to 9a9aa4 and grey top shades less violet. Installed.
- Kangaroo p62 (0.688 to 0.730: fists forward at chest height, hip and knee discs moved out to show, a lower crouch BATTLE_RISE 0.15; judge: old, low). Not installed; its build is kept in `scratchpad/blind3/kangaroo_p62_kept/`. The agent found a bone bug: `kangaroo_bone()` read names such as `thigh_frame_1_hip` and `knee_1_ring` as the right side, so the far leg's discs rode the near leg. Fixed (the side rule now accepts letters after the side, as quad_rig's), the installed p57 build otherwise unchanged: p63 (one 5x5 px area at the hip differs from p57; 0.687). Installed.
- Shoebill p79 (0.627 to 0.683; judge: new, medium): torso as large pale plates laid on the egg surface (plate_on) in top and flank bands, the detail pass skipping them and the core, a pale chest block forward, legs straightened and 27 cm forward, feet further apart (STAGGER 0.36), battle_legs R (-0.12, -0.02, 22) L (0.05, -0.02, 22), smaller gold joints. Installed.
- Hippo p40 (0.867 to 0.873; judge: new, medium): purple ramp about a third brighter and pinker from the reference's value bands, leg plates and joint discs bigger, the front of the back raised (taller profile). Leg spread and purple leg cores reverted. Installed.
- Pangolin: a longer tapered level snout scored 0.811 at best (against 0.820), splayed legs 0.805; nothing kept, files restored, p35 identical to p30. Nothing installed.
- The judges' next gaps: wolf_m: The tail. The reference has a long segmented spine sloping down-left about 25% of body length, with pale spikes along its top and a red block tip. In B the spikes are a white fringe bunched on the rear back, and the tail is a short horizontal red stub. Extend it down-left and run the spikes along it. | kangaroo_m: Value and hue: B is about 25-35% too dark and too brick-red. The reference is a saturated orange (around #E8501E) with bright top-edge highlights on every plate. Raise the base orange and add a 1px light rim on the top edges of the torso, thigh and tail plates. Keep the grey to joints only. | shoebill_m: Legs: the reference has bright gold rings at the knees and ankles and gold-tipped toes on dark gray legs. B's legs are plain gray with only stray gold specks. Add 2 to 3 pixel gold joint rings at the knee and ankle of both legs, gold claw tips on each foot, and lengthen the legs by about 10 percent. | hippo_m: There are no legs. The reference stands on four thick dark-grey legs with purple shin plates, raising the belly about 30-35% of body height above the toes. In A the toes sit directly under the belly. Add four visible dark leg columns, each about 4-6 px tall at sprite scale, and lift the torso to match. | pangolin_m: Legs and claws. In the reference, four splayed legs with large red three-toed claws sit clearly below the body. In the sprite they are buried under a grey mass. Lower and separate the legs about 4 to 6 sprite pixels below the belly line, and enlarge each red claw cluster to about 3 by 3 pixels at the front and rear feet.

## Part pass 3 with a blind judge per machine (2026-10-15, Preston: "go")
- Same workflow as pass 2 (`scratchpad/blind4/`).
- Kangaroo p68 (palette only; judge: new, medium): red ramp from brick to a saturated orange (8e2010 to f56a38), extra top ffa266, gamma 0.75, top_rim 1. Longer feet, a split thigh and shin and fists forward all cost outline or read worse and were reverted. Installed.
- Shoebill p84 (0.683 to 0.702; judge: new, medium): gold collar rings under each knee and over each ankle, gold claw tips, a gold and navy bill hook hanging lower, navy seams and a vent on the pale chest, pale 8aaedf. The agent renamed knee, ankle and toe joint parts so the side reads from the end of the name: bird_rig's rule had put the far leg's joint parts on the near leg (the same bug as the kangaroo's). Legs 10% longer cost 0.05 and were reverted. Installed.
- Pangolin p40 (palette only; judge: new, medium): the orange ramp without 4d2e07 and b87405, brighter gold and less brown. Raising the body, the belly or lowering the dome all cost outline. Installed.
- Wolf v89 (0.694 to 0.707: shoulder and hip hubs as clean red rings, red cut on the flanks, spikes in a line from the rump along the tail, tail lower; judge: old, low). Not installed; build kept in `scratchpad/blind4/wolf_m_r3_kept/`; the v84 build restored and rebuilt as v90, identical to v84.
- Hippo p44 (0.873 to 0.874: LIFT 0.15, legs spread 0.06, small shin pads, a cream fang, darker neck; judge: old, low). Not installed; build kept in `scratchpad/blind4/hippo_m_r3_kept/`; p40 restored and rebuilt as p45, identical.
- Installed with battle animations re-rendered: kangaroo p68, shoebill p84, pangolin p40 (gorilla v71, wolf v84, hippo p40 unchanged). view_art_check, battle_check, foundation_check, start_chain_check PASS.
- A combined install command was stopped by Claude Code's removal safety check (anim_round.sh clears its frame folder); nothing ran, and the steps were run one at a time instead.
- The judges' next gaps: wolf_m: The tail. The reference has a long segmented tail that runs about 25% of the body length back and up to the left, with a spike row along it ending in a red tip. B has a short red stub and spines bunched on the rump. Extend the tail roughly 2x and move the spines onto it. | kangaroo_m: Legs. The reference shows a round gray hip disc, a gray knee and shin, and long orange feet with black toe pads, splayed apart. The sprite has a flat diamond thigh with a vague gray blob under it. Shrink the thigh about 30%, add a clear gray hip circle and knee joint, and draw two distinct feet with dark tips. | shoebill_m: A's torso and chest are too light and uniform. Darken the base about 20-25% toward the reference's mid-blue. Add navy seam lines that split it into 3-4 distinct armour plates. Add gold joint accents at the shoulder and hip so the body stops reading as one pale mass. | hippo_m: Legs. The reference has four distinct dark-grey legs with cream toe caps and background visible between them. A merges them into one dark underbody band. Cut gaps of about 3-5 sprite pixels between the front and rear legs, and lengthen the visible leg by about 15-20% of body height. | pangolin_m: Legs and claws. The reference stands on four stout grey and gold legs splayed wide, with large red three-toed claws taking roughly 25% of its height. In A the legs are tucked under and the claws are tiny red flecks. Widen the stance and make each claw about 3x larger, in clear red.

## Codex handoff and the live-art guard (2026-10-15, Preston: "go")
- Codex had finished all six machines' views and the gorilla's 51 battle frames on 2026-10-13. Claude's installs since replaced the live copies without carrying them forward or flagging them, as `docs/team/CODEX_TASKS_2026-10-13.md` had promised. Codex's own copies are intact (`docs/art/2d/<id>/<build>_codex/`, `docs/art/2d/ape_l/anim_codex/`); the machines have changed shape since, so they are style guides now.
- New `tools/art/live_guard.py`: import_views.py and export_anim.py record a hash of every PNG they install and back up a live folder with hand edits to `docs/art/2d/<id>/live_backup_<kind>_<n>/` before replacing it; `art/machines/<id>/CODEX_IN_PROGRESS` stops the installs and all four round scripts for that machine (`LIVE_GUARD_FORCE=1` overrides). Install records seeded for the current six.
- New task file `docs/team/CODEX_TASKS_2026-10-15.md` (battle frames first, since the eight views show only in the view lab), checked by two independent reviewers: a fact-checker (78 claims, 7 wrong, all fixed) and a completeness critic reading as Codex (13 gaps, all addressed: the lock, edit-in-place instead of the sel-out install step, colour mappings per machine, the wolf's edge rule, part maps, stop after the gorilla, runnable check commands, repeatable-fix lines). The old task file and the start files point to it.

## New pixel V2 references, the gorilla ground-line fix (2026-10-15, Preston: "here is wolf, also im saving these new references as the new V2's"; "Ok all v2's from codex are done")
- The references Codex generated (pixel art) are now each machine's V2 (`docs/art/reference/starters/<id>.png`, sources `<id>_mechabeast2_source.png`); the earlier painted V2s are kept as `<id>_mechabeast2_painted*.png`. Installed views against them, side view: hippo 0.851, pangolin 0.793, kangaroo 0.675, wolf 0.671, shoebill 0.640; the gorilla's front-right view 0.784 (0.808 turned 10 degrees further). Other camera angles scored lower.
- New `tools/art/ref_palette.py` measures a family's ramp from a reference (outline pixels under brightness 34 left out). Trial palettes for wolf, kangaroo and gorilla, with shading tuned to each reference's average brightness (wolf 64 against 66, kangaroo 69 against 71, gorilla 84 against 86), were picked by three blind reviewers over the current colours. Not installed: Preston authorized Codex to continue on the current colours. Trials in the session scratchpad (`v2px/<id>_t2.json`).
- Codex finished the gorilla v71 (all 51 frames and eight views, live, awaiting Preston) and reported a detached ground line: Claude's 2026-10-14 PIXEL_SHADOW_SPAN change drew the line at the canvas bottom of animation frames whose feet sat within the span (only the gorilla's camera), and export_anim.py took the line for the feet (feet_y 146, the body's lowest row 130): the gorilla drew 26 px too high as the player, 46 as the enemy. The pixelizer now measures the line from the machine's lowest row and draws none on animation frames (as before 2026-10-14); 92 outputs checked: every view and the other five's frames unchanged. In the live gorilla frames only the line was removed (27 frames, 972 px of 2c2838 and 403a52) and feet_y set to 130, keeping Codex's finish; backup `docs/art/2d/ape_l/anim_live_backup_feetfix_2026-10-15/`. view_art_check and battle_check PASS; the gorilla stands on the ground in both slots.
- Open: the gorilla's battle camera cuts geometry in punch, slam, throw and death frames and the death clip lifts (Codex's report); a fix re-renders those frames and needs Codex's finish again, so it waits for Preston.

## Gorilla punch: the lawnmower haymaker (2026-10-15, Preston: "looks like its just flicking its wrist foward after winding it. I want it to look like a winding arching punch as its jumping towards the other mech"; then "it should lean back while bending and cocking the elbow back and up like pulling a lawnmower able then punch")
- Research (`research_notes/Gorilla haymaker punch/`): heavy punches in shipped games hold one wind-up pose as the telegraph, swing in a frame or two, hold the impact and recover long; the body leads and the arm drags.
- `punch_pose` in `tools/blender/build_ape_l_v2.py` rewritten (old one kept as `punch_pose_v1`): the body leans back 12 degrees on coiled hind legs, the upper arm cocks back and up (elbow about 30 degrees above the shoulder line) with the forearm folded to the chest; the forearm opens during a small leap (new `"air"` key in `clip()`, 0.12 m) so the fist goes up over the head, then comes over and down into contact at frame 21 and lands. Bone positions were measured per frame in the blend, not guessed: the first try hid the elbow inside the back's outline and kept the hind feet 0.85 m up through the landing. Sign facts found on the way: body +X pitches forward (lifts the hind legs); shin -X folds the knee and +X straightens it (the old "squash" stood the legs up). The clip now ends exactly on its first pose.
- Picks [4,10,14,17,19,21,24,28,36], ms [160,240,130,70,50,150,120,200,380], strike 5 (`tools/art/ape_l_anim_plan.json`, `ape_l_anim_jobs.txt`).
- The battle stands the player's feet on screen row 121, so the 148-row canvas starts 10 rows above the screen: the first install cut the reared pose's top by up to 7 rows. The lean went 22, 15, 12 degrees and the elbow 180 to 168 until every frame's top is on row 10 or lower.
- Installed with the new `tools/art/replace_clip.py`: only the punch frames are replaced; the frames are rendered 20 sprite pixels wider each side (SPRITE_ORTHO 5.61, same pixel grid; the new idle/0 matched the live one exactly at offset 20,20), the canvas grew 149 to 163 on the right for the fist, and the other 42 frames were padded with transparent pixels, every Codex pixel kept (checked). feet_y stays 130. Backups `docs/art/2d/ape_l/live_backup_anim_1/` (Codex's finish as it was) and `_2/`. `ape_anim_round.sh` now renders at ORTHO 5.61 so a future round keeps the fist. Godot import, view_art_check, battle_check PASS; capture `docs/art/2d/battle_ape_l_vs_hippo_m.png`; before/after loop `docs/art/2d/ape_l/punch_haymaker_2026-10-15.gif`.
- Open: the nine new punch frames are the pixelizer's output, without Codex's finish (see the Codex task file). Slam, throw and death camera cuts and the death lift are still open; `replace_clip.py` can now redo one clip at a time without touching the rest.

## Gorilla slam, throw and death rebuilt; rig signs measured (2026-10-15, Preston: "go" on the open items)
- Measured the rig instead of guessing (RIG_SIGNS block above `punch_pose` in `tools/blender/build_ape_l_v2.py`): body X+ pitches forward (the old slam's "rear-up" was a forward bow that drove the fists 0.9 m through the floor, the camera cut Codex reported); forearm X- flexes the elbow; shin X- folds the knee; head X+ nods down; body Y+ rolls toward the camera and stands the far side up (the death "lift"); a raised arm's Z acts the other way from a hanging arm's. And the camera: the E view turns the rig 70 degrees under an 18-degree elevation, so forward and the near side come toward the camera and draw lower, about 0.31 m per metre nearer.
- New `slam_pose`, `throw_pose`, `death_pose` (the old ones kept as `_v1`). Slam: both arms up in front, the near one in toward the centre, over and down into the floor ahead, hind feet planted throughout. Throw: the near arm swings back and up to the rack (Z -60 keeps it out on the near side; without it the raised arm crossed behind the body), over the head and forward, then plants. Death: the head snaps, the arms give way forward, the hind legs lay out behind, the body settles flat; it ends 13 px lower than idle instead of 29 px taller.
- Plan: slam frames [1,6,11,15,19,20,23,27,31,36], ms [250,250,250,300,50,50,200,80,160,250], strike 5 (a mid-swing frame, the shudder and the staggered recovery now sampled); throw frames [1,8,11,15,19,20,23,26,30,36], ms [200,200,200,260,90,50,120,120,150,150]; death frames [4,13,20,27,36,48]. `ape_l_anim_jobs.txt` regenerated from the plan.
- Judged blind (Workflow tool, A/B order shuffled per round, a judge and a defect hunter per clip, four rounds, about 3.6M subagent tokens): final vs live, slam 7-3, death 7-2, throw 7-4. The punch stays as installed (Codex finished it the same afternoon): two variants went 6-5 and 5-6 against it, no clear gain, and the build reproduces the installed punch pixel for pixel. Every round flagged the punch hit frame drawing the fist low (the camera rule above).
- Installed with `tools/art/replace_clip.py` (slam, death, throw); canvas 163 to 169 wide, feet_y 130; the 25 idle/gait/hit/punch frames are byte-identical to the live finish in their first 163 columns. Backups `docs/art/2d/ape_l/live_backup_anim_3/` (all Codex-finished, before these installs) to `_5/`. Godot import, view_art_check, battle_check PASS; throw captured in battle (`docs/art/2d/ape_l/battle_capture_weapon1.png`); the slam capture charged instead (45 EP needed, the capture starts at 35). Every frame's top is on screen (row 10 or lower) for the player slot.
- Open: the three new clips need Codex's finish. The enemy-slot gorilla stands 20 rows higher (ENEMY_FEET_Y 101), so its tall frames are cut at the top (Codex's note; battle layout, not the clips). The old `hit` clip also pitches forward on a jolt back (body +10); left alone.

## Battle staging: tall machines kept on screen (2026-10-15, Preston: "go")
- Measured every frame of every starter in both battle slots. The enemy slot (feet row 101, 20 rows above the player for the Legacy diagonal) left 100 rows of headroom; five of six starters lost rows off the top as the enemy (kangaroo 27 on its kick, pangolin 25, gorilla 20, shoebill 15 and 7 even idle, wolf 9), and damage numbers for tall machines started above the screen and never showed.
- New `scripts/battle/stage.gd` (the feet rows moved there from battle.gd): a machine stands at the highest row that keeps the clips it shows between moves (idle, hit) on screen, steps down further only while a taller clip plays (a 0.12 s ease, back up after; death stays down), and never below the player's row. Enemy home feet rows now: hippo, pangolin, wolf 101; kangaroo 105; gorilla 107; shoebill 113. Step-downs: gorilla punch +14, throw +6; kangaroo kick +16; pangolin roll +20; wolf death +9; small ones for the rest. `machine_anim.gd` records each clip's highest opaque row (and treats a frame that failed to load as empty). Damage and Miss numbers pop just under the art's visible top.
- New `tools/debug/battle_fit_check.gd` places machines through the same Stage functions, models the step-down frame by frame, and FAILS on any frame cut beyond a named allowance. Two allowances, poses too tall for the screen in either slot: kangaroo kick/5 (7 rows) and pangolin roll/6 (5 rows); fix those poses, then delete the lines. Verified it fails without them (exit 1).
- A three-lens review (Workflow tool, about 0.46M subagent tokens) found my first version of the check could never fail, the walk/gait clips held the gorilla 2 rows lower than needed, the off-screen damage numbers, a missing-frame hazard and the unmodelled ease; all fixed. battle_fit_check, view_art_check, battle_check PASS; enemy-gorilla capture `docs/art/2d/battle_kangaroo_m_vs_ape_l.png`.

## Battle zoomed out; weapon effects for every starter (2026-10-15, Preston: "Skill up with the synthesis, use zoid games repositories and source code. Fix up the battle scenes. The perspective is too close, and I want to starting adding VFX's and effects to weapons/animations etc. everything that needs it.")
- **Study (Workflow tool, 3 agents, about 0.85M subagent tokens).** Read the Zoids Legacy decomp's battle camera, staging and effect library, plus the Pokemon Emerald and Fire Emblem 8 decomps. The local `Zoids` Zig repo is a boids demo with nothing to learn. Notes, sources and numbers: `docs/reference/battle-vfx-2026-10-15.md`.
- **Framing.** Machines, effects and the ground they stand on now draw in a zoomed-out field (`scripts/battle/stage.gd`): about 0.7 of full size, rounded so art pixels stay whole screen pixels (0.75 at 1280x720, 0.667 at 1920x1080). Machines take 37 to 43% of the screen's height, against 56% before and Legacy's 52%. The background and panel stay full size. Nothing is cut at any zoomed scale, including the kangaroo kick and pangolin roll. A window resize is applied between steps.
- **Effects.** `scripts/battle/vfx.gd` draws every piece in code on whole art pixels. `scripts/battle/vfx_recipes.gd` holds one recipe per starter weapon (18) by clip frame, plus fallbacks by weapon type for lion_m, raptor_s and hawk_s. `shaders/hit_flash.gdshader` blinks the struck machine.
  - Melee attackers cross the field during the wind-up and land their frontmost point (fist, bill, feet) on the target at the strike frame. They stay above the panel and on screen, and go back during recovery.
  - Shots fly from a muzzle measured on the firing frame. Beams dim the background.
  - Impacts: burst, then blink, hit freeze, the target's own shake and knockback, with screen shake only on heavy blows.
  - Damage digits hop and the HP bar drains.
  - Charge draws light inward, and repairs sparkle.
  - Destroyed: a string of blasts, a white flash, a fireball column and a smoke column.
- **Checks.**
  - New `tools/debug/vfx_check.gd`: 288 attacks, all 18 weapons both ways as hit and miss at three window sizes, plus the older machines. PASS.
  - `battle_fit_check` now runs at every field scale.
  - battle_check, view_art_check, foundation_check, systems_check, start_chain_check and views_check PASS.
- **Look passes.** Captured with the new `tools/debug/vfx_capture.gd` and `tools/art/vfx_sheets.py`, five rounds. They fixed:
  - a full white silhouette that hid the impacts;
  - beams and jets too thin and washed white;
  - tan dust invisible on the tan path;
  - a slam wave that didn't show;
  - impacts a fifth of Legacy's size;
  - muddy after-images;
  - a weak destroyed sequence.
- **Review (Workflow tool, 6 agents, about 1.22M subagent tokens).** Fixed:
  - older drawn machines' anchors (their blasts landed on a canvas corner) and their blinks never showing;
  - the attacker drawing over its own impact;
  - an enemy lunge stepping over the panel;
  - window resize mid-attack;
  - shake gaps at the screen edge;
  - landing dust early on hits;
  - smoke drifting over the next machine;
  - the formation mark lagging a turn.
- **Open.**
  - A Legacy-style two-shot cut (attacker shot, then target shot) if the wide frame feels flat.
  - Sound effects (none exist yet).
  - Command steps (shield, repair command, mines, air lock) have no effects yet.
  - Recipe numbers are drafts for Preston's eye.

## Creature factory pass: the source fixes from Codex's finish reports (2026-10-16, Preston: "creature factory pass")
- Starting point: Codex finished all six machines and the gorilla's follow-ups (`docs/team/CODEX_FINISH_STATUS_2026-10-15.md`), so this pass took the source problems Codex logged for Claude and kept Codex's finish wherever the art did not change. The enemy-slot top clipping Codex measured was already gone (the zoomed-out battle, 2026-10-15).
- **New factory check, `tools/blender/bind_audit.py`:** it splits each saved model into its pieces and flags any piece on a left/right bone whose vertices lie on the other side, or on a tail or limb bone that sits much nearer another bone of the same chain. A folded limb (a bird's wing) skips the chain test. Reviewed false alarms are listed in `KNOWN`: the gorilla's ram fists ride a short hand bone, and the hippo's knee caps sit 12 cm above the knee. The builds can dump part name, bone and centre (`BIND_NAMES=<json>` in quad_rig, bird_rig and the gorilla's tag_parts).
- **What it found:**
  - **Shoebill, 33 pieces:** `bird_rig.bone_for` read the side only when digits followed it, so `wing_upper_1_bolt`, `wing_lead_1_edge`, `wing_fore_1_fan2` and the like rode the near wing. This is the same bug quad_rig had fixed on 2026-10-13, and it includes Codex's opposite-shoulder bolts.
  - **Pangolin, 14 tail scales:** `tail_bone` took the scale's ring index for its segment (`tailscale_<k>_<j>`: `split("_")[2]` is j). That forked the tail in Ball Roll.
  - **Wolf, kangaroo:** clean.
  - **Gorilla, hippo:** reviewed and right as built.
  - All six audit clean now.
- **New `tools/art/patch_frames.py` and `tools/art/anim_render_only.sh`:** re-render a machine's battle frames without installing them, compare each with the raw frame the live set was exported from, and replace only the frames that changed, on the same canvas. It stops if a frame would need a bigger canvas. Checked first: the kept raw frames reproduce the pre-Codex installs, 40 of 40 for both machines.
  - **Shoebill p85:** only Wing Buffet 1-7 changed. The other 33 frames and all eight views keep Codex's finish.
  - **Pangolin p41:** Scale Rake 1-8 and Ball Roll 1-8 changed; the other 24 frames are kept. The views changed too (the standing pose bends the tail): seven new, and Codex's S kept, re-placed on the 200x87 canvas (was 206x87).
- **Gorilla death:** re-rendered at `SPRITE_ORTHO=6.82` (40 sprite px of margin a side, same grid), so the far fist no longer reaches the render's edge. Installed with `replace_clip.py`; the canvas is now 173x148. All six death frames are raw: Blender's shading shifts a little with the frame size (877 of 7,690 idle pixels change a shade at 6.82 against 5.61, same palette).
- **View lab:** all six starters on the floor at half size (whole screen pixels per art pixel), so nothing is cropped. Tab shows one machine alone at full size facing right, and H hides the text. New `tools/debug/view_lab_capture.gd` writes `docs/art/2d/view_lab_capture.png`.
- **Codex handoff:** an update in `docs/team/CODEX_TASKS_2026-10-15.md`: shoebill buffet 1-7, pangolin rake and roll 1-8 plus seven views, gorilla death 0-5. Backups of the finished live folders are listed there.
- **Checks:** Godot import, view_art_check, views_check, battle_check, battle_fit_check, foundation_check, systems_check, start_chain_check and vfx_check PASS.
- **Left on purpose:**
  - Wolf dash/6's two edge pixels: a fix grows the canvas and resends the whole dash.
  - The shoebill's one-pixel barrel portions.
  - The judges' shape gaps from part pass 3 (wolf tail, kangaroo legs, hippo legs, pangolin legs and claws): each sends a machine's whole set back to Codex, so they wait for Preston.

## Detail pass: the detail pixelizer, judged blind (2026-10-16, Preston: "Skill up with the synthesis, goal better versions and more enhanced and detailed than zoids sprites")
- **Measured** (new `tools/art/detail_metrics.py`, 98 Legacy battle sprites, numbers only): ours were bigger than Legacy's but carried about a third of its separate shapes per area, clusters two to three times larger, half the panel lines and half the ramp length. Notes, sources and the full table: `docs/reference/sprite-detail-2026-10-16.md`.
- **Study** (Workflow tool, 3 agents, about 0.5M subagent tokens):
  - shipped-game technique: long hue-shifted ramps per material, own-colour panel lines with a lit lip, deliberate glints on metal, one clear light, cleanup that spares designed pixels;
  - our pipeline: `PIXEL_MIN_CLUSTER` was erasing about 65% of clusters, and the toon matcap caps the ramps;
  - Codex's finish: 31 repeatable treatments come down to five rules, blocked only by the antialiased part-ID pass.
- **Built:**
  - The piece pass (`render_sprite_views.py SPRITE_PIECES=1`: one exact colour per piece, plus `parts.json`).
  - `tools/art/pixelize_detail.py`: the factory's tone, per-part flattening and a 3x3 majority, a gradient from the normal pass, one-sided own-colour seams, lit top rims, metal glints capped at 4 per 1000 px, thin parts winning their pixel, a dark own-colour silhouette with a lit inner row, an eye recess, spur and stray-pixel cleanup.
  - `tools/art/detail_install.sh` (pixelize and install a machine) and `PIXELIZER=pixelize_detail` in `anim_render_only.sh`.
  - Shoebill blue gamma 0.85 to 1.75 (Codex's mid-blue).
  - `tools/art/detail_metrics.py`: a glint-count bug fixed and 8-connected counts added, both found by the study.
- **Judged blind** (Workflow tool, six judges a round, about 1.3M subagent tokens over two rounds):
  - The detail version beat the live Codex-finished side views on all six machines.
  - The cleaned version beat that on all six.
  - Every judge still rated all versions below the Legacy sprites.
  - Medians now: c8 174 (Legacy 173), s8 0.06 (0.06), lines 0.11 (0.10), glints 16 (18). Ramps 4.8 (7.5) and colours 29 (34) are still short.
- **Installed:** all six machines' eight views and battle frames from the detail pixelizer.
  - Builds unchanged: gorilla v71, wolf v84, kangaroo p68, shoebill p85 (views folder p84), hippo p40, pangolin p41.
  - The gorilla's frames now all render at `SPRITE_ORTHO=6.82`; canvas 170x127, feet row 122.
  - Codex's finished copies are kept: `docs/art/2d/<id>/<build>_codex/` and `live_backup_*`.
  - A bug found on the wolf's W view along the way: an eye pixel took a grey shade index, because plate rules ran per piece not per family. Fixed, and a clamp now warns instead of crashing.
- **Checks:** Godot import, view_art_check, views_check, battle_check, battle_fit_check, foundation_check, systems_check, start_chain_check and vfx_check PASS; battle captured.
- **Before and after:** `docs/art/2d/detail_pass_2026-10-16_before_after.png`.
- **Next** (the judges' notes are mostly model and design): guns and joints drawn as cylinders with a specular stripe, the wolf's red as a few defined plates with clean feet and head, the shoebill's body as hard plates, the hippo's feet and legs, pangolin scale rows and a separate snout, the kangaroo's tail and joint discs. Ramps need palette work and a less banded render.


## Model pass in a cloud session: five machines, two blind rounds (2026-10-16 to 17, Preston: "do whatever cloud session would be best for")
- **Where:** a Claude Code cloud session (Linux container) on the `cloud/model-pass-2026-10-16` branch, using cloud credits instead of the PC. New `tools/cloud/setup_cloud.sh` installs Godot 4.7.2 (Linux build of the same version) and Blender 5.2 as the `bpy` 5.2.2 module behind a `blender` shim (download.blender.org is blocked there, PyPI is not), with software EGL so Workbench renders without a GPU (about 8 s a view). The factory shell scripts now take `BLENDER` from the environment and default to the PC path, so nothing changes on the PC.
- **Reproduction first:** every builder re-rendered its live views from the unchanged model before touching it. All 40 views came out the same size; 0.6 to 2.3% of pixels differ by one shade (the software renderer). All eight Godot checks passed in the container before any change.
- **Round 1** (Workflow tool, one builder per machine, then three blind judges each with a different lens: design fidelity to Preston's painting, pixel craft, game read at 1x to 2x; about 3.5M subagent tokens). Each candidate against the live art, reference painting on top, A/B order hidden. All five won 3 of 3.
  - **Wolf v85:** three red saddles and a red square on each shoulder and hip replace about 130 small red bits (red clusters 51 to 28); paws with a dark heel and three swept red claws; a grey wedge head with a red brow, nose and fangs; four big pale hooked tail spikes (8x11 to 12x14 px, were 12 pieces of 3 to 6 px). Shadow Dash fins and Fang Lunge teeth changed with it (drafts).
  - **Hippo p41:** upright pillar legs with knee wheels; hooves with toe caps about 7x9 px (the foot was a 5 to 6 px cream strip).
  - **Pangolin p42:** bevelled scale tiles in rings, head raised clear of the front leg, feet 1.4x with thicker claws.
  - **Shoebill p86:** hull plates with navy seams; the wing as four feather blades.
  - **Kangaroo p69:** segmented tail sloping down; larger joint discs with steel faces.
- **Round 2** on the three the judges were least sure of (about 2.2M subagent tokens), judged against the installed round-1 art. All three won 3 of 3.
  - **Shoebill p87:** the faceted egg (two straight prisms) replaced by a lofted rounded hull, so seven big plates per side view instead of a facet patchwork (E clusters 280 to 256); navy feather blades with a light top strip; light blue 82a6d7 now the largest light shade. `SHOEBILL_P87=0` rebuilds p86 exactly.
  - **Pangolin p43:** overlapping shingle scales with a lit top row and a dark seam, shrinking toward the tail; the tail uses the same scales; a collar ruff covers the dark slab between head and body.
  - **Kangaroo p70:** the tail tip rests 2.5 cm off the floor in the stance (p69: 0.30 m); joint discs as a dark rim, mid-grey face and a white bead (they read inverted before); 25 rounded torso blocks replaced by 7 flat chamfered slabs. The fists are light steel now so the joint faces could drop to mid grey.
- **Installed:** all five machines' eight views and 40 battle frames, re-rendered from the new models with `anim_render_only.sh` (`PIXELIZER=pixelize_detail`) and `detail_install.sh`. The gorilla is unchanged (its joint question, the black shoulder hub, is Preston's call).
- **Checks:** Godot import, view_art_check, views_check, battle_check, battle_fit_check, foundation_check, systems_check, start_chain_check and vfx_check PASS. The kangaroo p69 kick/5 reached 8 rows above a 320x180 screen (allowed 7); p70 is back to 127 rows above the feet, as before, and passes. Battles captured under Xvfb: `docs/art/2d/battle_wolf_m+hippo_m_vs_pangolin_m+shoebill_m.png`, `docs/art/2d/battle_kangaroo_m+shoebill_m_vs_hippo_m+wolf_m.png`.
- **Before and after:** `docs/art/2d/model_pass_2026-10-17_before_after.png`.
- **Codex:** the replaced views and frames were already raw detail-pixelizer output (the detail pass); they and Codex's earlier finish stay in git history. A Codex finish pass on the new art is open.
- **Left, from the judges:**
  - Wolf: the head is lighter grey than the body (the reference's is body grey); the far-side paws' claws still merge in E.
  - Hippo: the legs stand a little tall against the reference; the toes are uniform.
  - Pangolin: SE outline overlap fell slightly (0.757 to 0.739); the far collar shows as gold bars behind the head.
  - Shoebill: the upper back reads as a deep-blue band in E and SE; the shoulder plate still splits into two or three tones.
  - Kangaroo: the tail tip still floats about a sixth of body height above the ground line in E (the 3D tip rests on the floor; the 18-degree camera lifts it); the segments read more as stripes than overlapping plates.

## Picking up the cloud pass on the PC: hippo p46, wolf v91 (2026-10-19, Preston: "go")
- **Branch:** `cloud/model-pass-2026-10-16` checked out on the PC. Godot import and all eight checks passed on Windows before any change.
- **Hippo p46** (judges: "the legs stand a little tall"; "the toes are uniform"): the body back to p40's lift (LIFT 0.25 to 0.10) on p41's pillar feet, and the five toes graded 0.72, 0.88, 1.08, 0.88, 0.72 from the outside in. E view width to height 1.37 to 1.45 (the reference is 1.56; 0.18 took only 2 px off, so it went to 0.10). Battle canvas 133x94 to 133x89, feet row 91 to 86. `HIPPO_P46=0` rebuilds p41.
- **Wolf v91** (judges: "the head is lighter grey than the body; the reference's is body grey"): the skull's "face" colour 4a4a54 to 24242b (32323a was tried first and was still 10 brighter). E view head grey mean 105 to 83 against the body's 82 (the reference: 61 and 63). `WOLF_V91=0` rebuilds v85.
- Local build folders p41 to p45 and v85 to v90 are older PC rounds, not the cloud's builds of the same names, hence the new numbers. Old detail renders are kept as `renders_detail_pre_p46`/`_pre_v91` and `anim_frames_detail_pre_*`.
- Judged by Claude alone against the reference with measurements, no blind panel (Preston's cost rule).
- **Pangolin p44** (judges: "the far collar shows as gold bars behind the head"): the collar ring skips its far-side scales from the top down to 110 degrees (80 left one of the bars). In E and SE two of the three gold bars behind the head are gone; one bar above the head remains and is not a collar scale (unidentified). `PANGOLIN_P44=0` rebuilds p43.
- **Shoebill: tried, not installed.** Judges: "the upper back reads as a deep-blue band in E and SE; the shoulder plate still splits into two or three tones." (1) Plates pressed flatter (SHOEBILL_FLAT 0.5 to 0.85): the shoulder still spans 4 light-blue shades, upper-back navy share 0.24 to 0.25 in E. (2) The upper wing bone from trim navy to the mid blue (the piece pass put 642 of 1138 dark render px in that band on it): navy share 0.24 to 0.23, no visible change at sprite size. Both reverted; p87 stays installed. The band seen in the sprite is likely the dark outline and seam along the top of the body, not a single piece; next try would be the pixelizer's top-edge silhouette rule on that machine, or a hand fix.
- **Kangaroo tail: left as is.** The cloud pass already measured it: the 3D tip rests 2.5 cm off the floor, and the raised E camera lifts whatever lies further back; curling the tail toward the camera (0, 6, 8, 10) gained 2 px in E but lifted the W tip 13 px. A fix needs a battle-only curl or a contact shadow, not a model change.
- **Wolf v92** (judges: "the far-side paws' claws still merge in E"): the far (+x) claws take a darker red, 8c1010 against the near e01818, the sprite convention for far limbs. Checked in E and SE: the far claws land a ramp step down and separate from the near paws. `WOLF_V92=0` builds v91.
- **Shoebill p89** (Preston: "what would be its left leg from its perspective ... is floating and not connected to torso", every frame): the far (+x) leg's thigh existed and was bound right (bind audit 0 of 251), but the 18-degree camera draws the far leg higher, so its knee sat at the hull's bottom edge and the hull hid all but about 5 sprite rows of thigh, the same light blue as the belly plates. The leg read as hanging from its gold knee collar. Fix: the far knee 12 cm lower (longer thigh, shorter shin, foot unchanged), and the far thigh and shin plate in the mid blue (the far-limb convention). The mid blue alone did not show; the lower knee did. `SHOEBILL_P89=0` builds p87.

## Refine pass part by part, one creature at a time (2026-10-19, Preston: "factory refine pass part by part 1 creature at time. Also codex tasks")
- **Kangaroo p71**, compared part by part with Preston's painting (head, ears, torso, pods, arms, thigh, shin, feet, tail):
  - Tail: his painting's tail also ends about a third of the way up, so the judges' "floating tail" is the camera, not a fault. Left alone.
  - Pods: the hip boosters, rocket pod and shoulder gun from charcoal "frame" to the mid-grey "light", as his. The dark mass behind the body now reads as grey hardware. **Open question for Preston:** his 2026-10-15 correction says the reference's shoulder gun and hip boosters are wrong; this changed only their colour, not their shape. `KANGAROO_P71=0` puts them back.
  - Far shin: a tall near-black slab in E and SE (the piece pass put 3564 dark render px on the far shin's charcoal column; its orange calf plate faces away from the camera). An orange plate on each shin's front, the far one turned toward the camera: E shows an orange strip now, SE is still mostly dark. Near-black share E 0.254 to 0.248, SE 0.246 to 0.255. Left for Codex's hand finish.
  - Bind audit 0 of 249.
- **Codex tasks:** `docs/team/CODEX_TASKS_2026-10-19.md` (hand-finish the model-pass art, one machine at a time, with the measured leftovers per machine).
- **Kangaroo p72** (Preston: "the middle pillar like gun thing bottom of torso looks like a phallus. So we will put a pouch there but the cannon will shoot from there but more near stomach"). The pillar was the left shin: the split stance put its foot 0.7 m forward (`BATTLE_FEET["L"] = -0.7`), standing the charcoal shin under the middle of the belly in E, SW and S. Changes:
  - Stance: the left foot back beside the right (`BATTLE_FEET["L"] = 0.15`). No shin under the belly in E, SW or S.
  - Pouch: a rounded lighter-orange shell over the lower belly with a dark lip; the two lower belly plates and the old hip hatch go.
  - Pouch Flak Gun moved up to the stomach: an orange hatch hinged on its top edge over a dark recess, and a grey barrel stowed pointing down inside the body. **Deploy bones**: `quad_rig.make_rig` now takes `cfg["extra_bones"]` (any machine can carry hatches and flip-out guns); the kangaroo adds `hatch` and `cannon`, and the flak clip (`attacks.py`) swings the hatch up 110 degrees and the barrel 90 degrees forward on the wind-up, fires, starts the barrel back on the recovery, then closes. Checked on the posed rig: at the hit the barrel points straight forward, its tip about 0.3 m out of the stomach. At sprite size it shows for three frames, a few pixels; the muzzle flash does the rest.
  - First try had the hatch at the chest (z 1.28) with a 0.3 m dark barrel: hidden behind the near arm. Now z 1.17, 0.42 m, the pods' grey.
  - **Pouch Cannon** (Preston: "A little bigger, like a pirate cannon. This attack will be pouch cannon"): the move is renamed in `scripts/data/machines.gd` (stats unchanged). The gun is now a 0.55 m iron barrel, 0.22 m across, with two raised grey bands, a flared muzzle lip, a dark bore and a knob at the breech; it is stowed pointing up inside the chest (too long to stow pointing down) and swings 90 degrees forward through a bigger hatch (0.4 by 0.36 m, at z 1.14). At the hit it sticks 0.38 m out of the stomach, tilted about 20 degrees up by the recoil lean. Battle effects (`vfx_recipes.gd`): one iron ball on a low arc (new `ball` projectile style in `vfx.gd`, puffs of powder smoke behind it), a 10 px muzzle flash, a cloud of smoke at the muzzle, a heavier hit (hitstop 0.08, knock 16) in place of the flak bursts and brass.
  - Bind audit 0 of 229. `KANGAROO_P72=0` builds p71.
  - **Legs mirrored** (Preston: "make sure legs are mirroring each other. left leg got closer than before but needs tuning"): the build staggered the hips front to back (`STAGGER` 0.16, the left hip 32 cm behind the right) and the stance pushed the feet back by different amounts (R 0.45, L 0.15). Now `STAGGER` 0 and both feet 0.3 m back, and both shin plates face straight forward (p71 turned the left one inward). Joint positions and stance angles are equal left and right; what differs in S is the upper-left light.
- **Shoebill p90/p91**, part by part against Preston's painting:
  - Wing feathers (p90): his primaries hang down and back as long navy blades ending near knee height; ours fanned out sideways at 10 to 43 degrees. Now 28 to 58 degrees, each capped at 0.95 m. Preston: "It looks great other than that." `SHOEBILL_P90=0` builds p89.
  - Legs (p91; Preston: "its leg is still not connected maybe its the right"): the near (right) thigh was a narrow block hung under the hull's dark bottom edge. Both thighs now start 14 cm higher inside the hull and flare to 0.24 m at the top, with a gold ring at each hip (his joint language). The near leg now reads as attached; the far leg is better but still shows only a short thigh in E, because the raised camera tucks it under the hull. `SHOEBILL_P91=0` builds p90.
  - Hips mirrored (p92; Preston: "Still a gap ... compare to the other hip view you can see the gap"): in S the far hip sat 0.36 m behind the near one (`STAGGER`), so its thigh hid behind the hull and its gold ring hung under it with a gap. Both hips now sit at the mean of the two staggers, the knees halfway, the feet keep the full stagger (the legs still separate in the side view); the p89 far-knee drop is off. `SHOEBILL_P92=0` builds p91.
- Kangaroo p72 final checks: Godot import and all eight checks PASS, bind audit 0 of 238.

## The combination machine, v1 (2026-10-19, Preston: "create a whole new model using mass manufacturing ... you can tell it has aspects of all creatures")
- A new factory machine, `tools/blender/build_combiner_m.py` (working id `combiner_m`): one quadruped beast in its own colours (pearl, gold, gunmetal, crimson) with one trait from each starter and six core gems in their colours. Synthesis: Zoids Legacy's combination system (the combined unit is its own model), Fuzors and Blox, the Nue and the Chimera; Earth Wars' humanoid combiners as the counter-example. Doc: `docs/reference/combiner-v2-2026-10-19.md`. Sheet: `docs/art/2d/combiner_m/combiner_m_v1_views.png`.
- First render read dark (pearl and gunmetal share the grey family and the toon light pulled the pearl flanks dark); grey gamma 0.85 to 0.5 fixed most of it. Not installed in the game. Earlier same-day experiments `build_combiner_v1.py` (humanoid, Bruticus proportions) and `build_combiner_v2.py` (the six cut apart by bone) are superseded.

## Shoebill pivot to its real bird's weapons, p93 (2026-10-19)
Preston's brief: bill-clattering that sounds like machine-gun fire, a razor-edged hooked bill that decapitates, and sentry stillness for hours then a lightning ballistic lunge; "you have permission to remove top weapon also the two bulbs sticking out of chest that look like nipples". The combiner is set aside for late game.
- Model: the Lance gun on the head, its lens under the bill hook and the two spare breast guns (the bulbs) removed; the bill's clamp teeth stay. `SHOEBILL_P93=0` builds p92.
- Moves (`scripts/data/machines.gd`, stats unchanged; working names from his notes): Bill Clamp to **Apex Decapitation** (clamp clip: the bite now wrenches sideways); Stillwater Lance to **Bill Clatter** (lance clip: the head snaps shut and open on every sampled frame of the burst; type beam to shell; effects: three bursts from the bill tip, small fire flashes); Wing Buffet to **Sentry Lunge** (buffet clip: dead still for three frames, then the body and bill shoot forward 0.5 m; effects: speed lines, a star and a slash at the bill). Clip ids kept so the battle plan and installs need no change. The rig has no lower-bill bone, so the clatter is the head snapping; a jaw bone is a later step.
- **p94, the jaw** (Preston: "do it"): the lower bill rides its own `jaw` bone, hinged at the back of the gape and parented to the head, laid along the finished lower bill. New generic hooks: `cfg["part_bones"]` in `bird_rig.bone_for` and `quad_rig.bone_for` sends named parts to extra bones (with `extra_bones` from the Pouch Cannon). Keys: Apex Decapitation gapes 36 degrees on the wind-up and slams shut on the bite; Bill Clatter claps open (30) and shut on every sampled frame; Sentry Lunge opens as it shoots forward and bites shut at contact. Checked on the posed rig (the jaw opens about 26 degrees from the head on the clatter's open frames) and in renders. The teal lens under the bill (the old Lance) also went with p93. `SHOEBILL_P94=0` builds p93.

## Gorilla v76, after Codex's reference (2026-10-19)
Codex returned a gorilla model sheet and a target sprite (`docs/art/2d/codex_reference_pack_2026-10-19/returned/`; the sheet came back as four perspective pixel views, not a flat turnaround, so `PROMPTS.md` now asks for a blueprint-style sheet). Measured against ours: Codex's is longer and lower (width/height 1.47 against 1.28), more orange (39% against 30%), brighter (mean value 0.53 against 0.47), with blocky knuckle fists, light-grey layered wheels where ours had black hubs, and one big forward cannon on the back.
- v76 (Preston: "knuckles proportions were generated correctly so make sure theres five and it looks right on the model"): each fist is the orange back-of-hand block over a row of five grey segments and five chunky orange knuckle blocks on the ground; the curled three-segment fingers, the thumb, the knuckle guard and the four knuckle spikes are gone. The black fist hub and the black shoulder-pod ring become layered light-grey wheels (grey rim, light steel ring, grey hub, light cap), which also answers the open shoulder-hub question. Checked in the S render (five knuckles a fist, the grey band between hand and knuckles) and the detail-pixelized S, SE and E. `APE_V76=0` builds v71.
- Still to do from the comparison: the back weapons as one big forward cannon, a spine rack and a missile pod; a longer, lower body with the forelimbs splayed; thicker hind legs with an ankle wheel.
- Installed: eight views and all 51 battle frames (canvas 170x127 to 173x130, feet row 125). Godot import and all checks pass. Two notes: (1) punch/2, the haymaker's fist arched over the head in the leap, now reaches 3 rows above a 320x180 window (v71 sat exactly at the top row; v76's fist is 4 cm higher in that frame, measured on the posed rig, 3.131 against 3.089 m). Turning the wrist in the leap lowered it only 2 cm, and lowering the arch would undo the haymaker Preston approved, so it is in `battle_fit_check.ALLOWED` (`ape_l/punch: 3`), the zoomed field cuts nothing. (2) The bind audit flagged the fist wheel's light cap (on the hand, nearer the forearm line); reviewed and added to KNOWN, 0 of 727.

## Wolf v93 from Codex's sheet (2026-10-19, Preston: "go")
- Codex's wolf (`codex_reference_pack_2026-10-19/returned/wolf_m_codex_*.png`) kept our design. Measured on the side views at equal height with a grid: colour shares match (red 16 to 18% against our 16 to 17%); torso within 4% (hip plate to shoulder plate 0.72 of the height against 0.69); tail 29% longer (tip to hip plate 0.54 against 0.42); shoulder plate to nose 15% longer (0.62 against 0.54). The first report to Preston said the torso was about a quarter longer: an eye estimate, wrong, corrected by the grid.
- **v93** (`WOLF_V93=0` builds v92): the detail pass's 5 cm corner bolts removed; the legs bare of the detail pass and the hydraulic rams (Codex's legs are clean light-grey blocks); elbow and knee rings out to 0.98 of the disc with a 0.5 hub (were 0.8 and 0.44) and 3 cm prouder; tail 1.28 times longer; head 12% longer along the body (not taller) and 10 cm further forward.
- The white specks were the detail pixelizer's glints, not the bolts (single light pixels in E: 38 with and without the bolts). Wolf glint cap 4 to 1.5 per 1000 px (`legacy_look.json`, `PIXEL_GLINT_CAP`). Single light pixels: E 38 to 24, battle idle 36 to 25.
- Render ortho 5.6 to 6.2 (the resolution grows with it, so the sprite scale is unchanged) so the longer wolf fits the frame. E view width to height 1.72 to 1.85 (Codex 1.90). Battle canvas 196x124, feet row 112.
- Checks: Godot import and all eight PASS, nothing cut at any battle scale. Bind audit 0 of 295.
- Not done: Codex's stalking battle pose (head below the back line, front legs reaching); offered to Preston as the next step.
- Sheet: `docs/art/2d/wolf_m/v93_before_after.png`. Old renders kept as `renders_detail_pre_v93`, `anim_frames_detail_pre_v93`.
- **Wolf v94, the stalking battle pose** (Preston: "go"): Codex's battle sprite stalks with the head below the back line. New optional stance pitch in `attacks.quad_stance`: `cfg["battle_body"]` turns the body nose-down about the body bone's head in every battle clip, each foot target turned back by the same angle so the feet stay planted and level; `cfg["battle_head"]` adds to the head. Other machines unchanged (both default to none). Wolf: body 6 degrees, head 16 degrees. The eight views keep the level stance (Codex's model sheet stands level). Battle canvas 199x129, feet row 121. All eight checks PASS, nothing cut; bind audit 0 of 295. `WOLF_V94=0` builds v93; the v93 frames are kept as `anim_frames_detail_v93`.

## Gorilla v77, the rest of Codex's list (2026-10-19 to 20, Preston: "go")
- Measured against Codex's sprite on a grid at equal height: Codex 1.47 times as wide as tall, ours 1.21 (battle idle) and 1.25 (side view); its rump sits lower than the shoulders, its weapons are one long grey cannon and an orange rack along the top, its hind legs are thick with a grey ankle wheel.
- **v77** (`APE_V77=0` builds v76):
  - Back: the three ballast blocks run in a row along the spine on a grey rail, orange caps on top (Codex's rack); the throwing arm (rail, pivot, claws) and the cross glow strip are gone. Ballast Throw's mount text still holds (a block off the rack on its back). This reverses the 2026-10-12 across-the-back layout; Preston approved Codex's.
  - The spare shoulder gatling is replaced by one big grey forward cannon along the right of the back (spare hardpoint, no move; `weapons.cannon`, 1.2 m, r 0.12). The spare missile pod on the left shoulder stays.
  - Body: `_stretch_rear()` moves everything behind the middle 0.3 m back (smoothstep over y -0.6 to 0.8) and down by up to 0.2 m in proportion to height, so the feet stay on the floor; the torso shell, rack and back plates bend vertex by vertex, every other part moves whole (discs stay round); the rig joints move the same way.
  - Hind legs 1.3 times thicker (thigh and shin armour and cores) with a layered light-grey ankle wheel as the fists' (first try sat inside the ankle disc: `HIND_IN` pulls each piece's centre in by 0.8 but not the disc's depth; now 0.32 out).
  - Haymaker (v77b): the longer rear lifted the leap 9 cm (the lean back pivots about the middle and the grounding stands the hind feet on the floor), punch/3 cut 6 rows at 320x180 against 3 allowed. The lean scaled by the lever (0.8) and the hop 0.12 to 0.10 m: the apex is now 1 to 2 rows below v76's, punch/3 cut 2 rows.
- Side view width to height 1.25 to 1.34, three-quarter 1.36 to 1.43 (Codex's sprite 1.47). Views rendered at ortho 4.9 (was 4.4; the resolution grows with it, same sprite scale) so the longer body fits; battle canvas 181x129, feet row 124.
- Checks: Godot import and all eight PASS; bind audit 0 of 737. Old frames kept as `anim_frames_detail_pre_v77`, renders as `renders_detail_pre_v77`. Sheet: `docs/art/2d/ape_l/v77_before_after.png`.
- Not done: Codex's forelimbs read wider because its far fist reaches further forward in the battle stance; ours is the ref-4 stance (L_arm 21, chosen so both fists show planted). Left as is; offered to Preston.

## Kangaroo p73 from Codex's sheet (2026-10-20, Preston: "go")
- Codex's kangaroo (`codex_reference_pack_2026-10-19/returned/kangaroo_m_codex_*.png`) kept the design and did not draw the open-hatch pose. Measured on a grid at equal height: orange share matches (52-53% against 51-54%); ours darker (near-black 30-31% against 24-25%); tail tips at the same height in all four images (0.14-0.18 of the height), so the judges' floating tail is no worse than Codex's. Piece map of the E render: the near shin (charcoal, as Codex draws it), the hip disc's near-black rim and the thigh's detail-pass vents and rams carried most of the dark.
- **p73** (`KANGAROO_P73=0` builds p72): joint faces (hip, knee, ankle) 0.68 to 0.82 of the rim, Codex's big grey face in a thin dark rim; thighs and shins bare of the detail pass; the seven armour slabs 0.07 to 0.04 m thick and 0.005 m off the core (were 0.02), so the back outline curves instead of stepping; tail root radii 0.27 to 0.32 with an even taper (0.32, 0.29, 0.26, 0.22, 0.18, 0.13).
- E view near-black 31% to 26% (Codex 25%). Battle canvas 110x132, feet row 129. Godot import and all eight checks PASS (kick/5 is the existing allowance); bind audit 0 of 225. Sheet: `docs/art/2d/kangaroo_m/p73_before_after.png`; old renders kept as `renders_detail_pre_p73`, `anim_frames_detail_pre_p73`.

## Shoebill p95 from Codex's sheet; Grok Build tested (2026-10-20, Preston: "go")
- Codex's shoebill matched ours closely (gold 9 to 10% against 9%, light blue 32 to 33% against 34%, battle sprite width 0.77 against 0.78). Its wing is already two calm plates in ours (p87) and the detail pass already skips the wing; its wider side view comes from its side drawing, not the sprite, so the feathers stay.
- **p95** (`SHOEBILL_P95=0` builds p94): the crest blades 0.26 to 0.46 m and 0.09 to 0.1 wide, a spiky tuft as Codex's; the chest vent two bold slots (was three thin ones). Found on the way: p87 to p94's vent slots were hit-tested against the body core, which lies under the chest plate, so they were buried and never showed; p95 hits the plate itself. Battle canvas 106x112, feet row 108. Godot import and all eight checks PASS; bind audit 0 of 248. Sheet: `docs/art/2d/shoebill_m/p95_before_after.png`.
- Grok Build (v1.0.62, Grok Lite login) runs headless here with the Imagine tool: one hippo reference sheet (`docs/art/2d/grok_pack_2026-10-20/hippo_m_grok_modelsheet_test.png`) came back as a true flat side, front and back at one scale, but with grey armour, one back gun and text labels. Tasks: `docs/team/GROK_TASKS_2026-10-20.md`; Codex's updated list: `docs/team/CODEX_TASKS_2026-10-20.md`.

## Hippo p47 and pangolin p45 from Codex's sheets; the Grok batch (2026-10-20, Preston: "go both", "go on the grok tasks too")
- **Hippo p47** (`HIPPO_P47=0` builds p46): Codex's hippo matched ours on colour (plum 46%, cream 8%, near-black 13% on both) but stood 1.81 to 1.88 times as wide as tall against our 1.45 to 1.49 (his painting 1.56). Preston took the middle, about 1.65. `SQ`, which scales every front-to-back position, 0.9 to 1.2 (1.04 measured only 1.53: the 35-degree side view hides length); the back's twin cannon and torpedo pod larger. Side view 1.65. Rendered at ortho 6.0 (resolution scales, same sprite scale). Battle canvas 153x103, feet row 97. Bind audit 0 of 519.
- **Pangolin p45** (`PANGOLIN_P45=0` builds p44; also set `pangolin_m` back to `SPRITE_E_TURN` 35 and `SPRITE_ELEV` 14 in `legacy_look.json`): Codex's was 2.48 to 2.57 wide to tall against our 1.79 to 2.03, mostly a long tail sloping to the floor; our hind feet also stood a fifth of the height above the front ones. Causes and changes:
  - Side-view turn 35 to 20 degrees as the other five (the 35, for the 2026-10-15 V2 references, drew the deep end of the machine high): the four feet now stand on one line.
  - Tail 1.3 times longer (controls (2.15, 0.5) and (3.25, 0.1)), the red cone from 0.78 of the tail, 0.6 m past the tip and 0.23 m wide. Side view 2.49. Ortho 7.6 (6.8 still clipped the W view).
  - The longer tail failed view_art_check (N view 89 rows against SW 64, limit 1.35x: from behind, the tail runs toward the camera along the floor and its tip draws below the feet): the non-side views' camera 14 to 12 degrees. Passes.
  - It failed battle_fit and vfx (roll/6: the body dives nose down and the tail points up, cone 13 rows over a 320x180 screen, 5 allowed). A looser curl (0.8) stood it straighter, 18 rows; a tighter one (1.4, `attacks.RC`) wraps the tail over the back into the ball and brings the tip forward: 2 rows. Battle canvas 190x129, feet row 124.
- Godot import and all eight checks PASS; bind audits 0 of 519 (hippo) and 0 of 319 (pangolin). Sheets: `docs/art/2d/hippo_m/p47_before_after.png`, `docs/art/2d/pangolin_m/p45_before_after.png`.
- **Grok batch** (`docs/art/2d/grok_pack_2026-10-20/`, `runs.jsonl`): eight runs, reported $0.06 to $0.13 each, about $0.70. Model sheets from fresh eight-view sheets of the installed builds: all four came back as true flat side, front and back views; the wolf's matches our design closely; the gorilla stands upright instead of knuckle-walking, the shoebill turned into a feathered real bird, the kangaroo is cartoonish with text labels despite the no-text rule. Screens: each reduced to 320x180 at 48 colours (`*_320_48c.png`) beside the current ones; the field keeps its layout (fences added), the title and opening keep their compositions in a flatter style, the battle background turned from a dark plain to a bright one with a lake. Nothing installed. A hippo and a pangolin sheet in the folder (10:26, 10:29) came from a Grok session Preston ran from the Preston Hub folder.
- **Screens installed** (Preston: "install the field, title and opening screens"): Grok's versions reduced to 48 colours at 320x180 replace `art/field/grassland.png`, `art/title/background.png` and `art/opening/scene.png` (each a fixed 320x180 slot; the field's left and right edges match better than before, 28.8 against 42.9 mean difference). The battle background stays. Originals: `docs/art/2d/screens_pre_grok_2026-10-20/`. Godot import and all eight checks PASS.
- **Grok sheets, hippo p47 and pangolin p45** (Preston: "run the hippo and pangolin grok sheets"): prompts now say hard mech armour, no fur or feathers, the stance, and no text twice; saved as `<id>_grok_modelsheet_p47/_p45.png` (the earlier pair from Preston's own session kept). Both flat side, front and back with no text. Pangolin: close to our design (finer scales, the tail sloping to a red cone on the floor). Hippo: our colours and parts, but an organic cartoon face and body shorter than p47's 1.65. Reported $0.11 and $0.07.
- **Pangolin p46, factory pass part by part** (Preston: "Do factory pass as well"; `PANGOLIN_P46=0` builds p45): part by part against Codex's sprite, the legs were the gap (chunky grey blocks with a gold knee plate and big red claws in Codex's; ours hidden under the flank scales and their own gold shin plates, the claws red flecks); the head lacked Codex's red nose tip; tail and body close. Changes: shin plates off (knee plates stay), flank scales to 112 degrees from the spine (were 128), claws 1.35 times bigger at the front and 1.15 at the back (were 1.0, 0.85), a red nose cap on the snout. Battle canvas 191x130, feet row 125; roll/3 overhangs 3 rows (5 allowed). Godot import and all eight checks PASS; bind audit 0 of 295. Sheet: `docs/art/2d/pangolin_m/p46_before_after.png`.
- **Grok, empty world/UI slots** (Preston: Grok for world and UI assets only): canyon field, mode-menu background and pause panel, each from an installed image as the style reference; reduced to slot size (`*_slot.png`, 48, 32 and 24 colours); preview `docs/art/2d/grok_pack_2026-10-20/slots_preview.png`. Not installed yet. Reported $0.06 to $0.11 each.
- **Grok slot images installed** (Preston: "install all three"): `art/field/canyon.png`, `art/ui/menu_mode.png`, `art/ui/pause_menu.png`. The canyon scene (`scripts/scenes/field2.gd`) drew an opaque placeholder floor band over y 40 to 156 and a "CANYON (placeholder)" label; both now draw only when the art file is missing. Godot import and all eight checks PASS.
- **Hippo p48, factory pass part by part** (Preston: "go hippo next"; `HIPPO_P48=0` builds p47): against Codex's sprite, the gaps were the tail (Codex's a grey hose curled up off the rump; ours a short stub pointing down, hidden) and the upper legs (Codex's rounded plum thighs and shoulders, dark only at the cuff and hoof; ours grey columns top to bottom). Head, wheels and back gear close. Now: the tail three grey hose segments curling up and back with dark rings and a dark tip, below the back's top; the upper columns plum under a bigger outer plate (0.6 by 0.66, mid-leg). Battle canvas 154x112, feet row 106; nothing cut. Godot import and all eight checks PASS; bind audit 0 of 527. Sheet: `docs/art/2d/hippo_m/p48_before_after.png`.
- **Wolf v95, factory pass part by part** (Preston: "go wolf next"; `WOLF_V95=0` builds v94): against Codex's sprite the body, saddles, square plates and tail spikes matched; its head was bigger with a big curved red fang hanging from the front of the upper jaw (ours a small tick), its claws bigger, its light-grey leg blocks chunkier. Head group 1.2 to 1.3, upper fangs 1.4 times longer and 1.3 thicker, claws 1.3 longer and 1.25 thicker, the light leg guards 1.15 thicker. Battle canvas 199x131, feet row 121; nothing cut. Godot import and all eight checks PASS; bind audit 0 of 295. Sheet: `docs/art/2d/wolf_m/v95_before_after.png`.
- **Gorilla v78, factory pass part by part, with the synthesis** (Preston: "go gorilla next", "don't forget to use the synthesis to skill up too"; `APE_V78=0` builds v77). Against Codex's sprite: its back cannon a light grey barrel with dark bands (ours one dark bar); its visor a thicker band; its rear plated where ours showed one big pale slab. The piece map put the slab on the near hind thigh armour (3359 render px, lit face-on; v77 made it 1.3x thicker), not the rump plate. Synthesis, Legacy's Iron Kong (structure only): its hind legs read as separate columns because they are a step darker than the body with highlights only on top edges. Changes: the barrel in light steel with two dark bands, a framed plate on each thigh's outer face, the thigh and shin armour in the darker green (trim 3e5a33), the visor 7 to 10 cm.
  - Found on the way: since v77 the SW and NE views touched the frame edge at ortho 4.9 (the diagonal sees length and arm span), clipping a fist. Views now at 5.6; all eight inside.
  - Battle canvas 181x129, feet row 124; punch/3 overhangs 2 rows (allowed). Godot import and all eight checks PASS; bind audit 0 of 745. Sheet: `docs/art/2d/ape_l/v78_before_after.png`.
- **Skill-up:** the pass written as a project skill, `.claude/skills/factory-pass/SKILL.md` (steps, frame sizes per machine, the lessons of these rounds: frame clipping after a stretch, lever effects on clips, turned cameras hiding length and lifting the deep end, buried hit-tests, glint specks, pale lit faces, scene placeholders). A pixel anchor for Grok's world and UI art in `docs/team/GROK_TASKS_2026-10-20.md` (from the pixel-art skill's anchor idea).
- **Kangaroo p74, factory pass part by part** (Preston: "go kangaroo next"; `KANGAROO_P74=0` builds p73): zoomed against Codex's sprite, the gap was posture: Codex's stands tall, the body lifted so each leg reads as a Z under the torso (orange thigh, big grey hip disc, dark shin back to a grey ankle disc, long orange foot); ours sat squat with the lower legs pressed into a dark lump at the floor. Head, guns, pod and torso plates already close. Changes: the battle stance rise 0.25 to 0.4 m (IK keeps the feet planted; the eight views use the battle stance too), the tail pitched 4.3 degrees further down (-15.9 to -20.2) so its tip stays on the floor, the ankle disc 0.11 to 0.15 m with a shine bead. E view width to height 0.88 to 0.83 (taller). Battle canvas 108x132, feet row 129; kick/3 overhangs 7 rows (the existing allowance, unchanged). Godot import and all eight checks PASS; bind audit 0 of 227. Sheet: `docs/art/2d/kangaroo_m/p74_before_after.png`.
- **Shoebill p96, factory pass part by part** (Preston: "go shoebill next"; `SHOEBILL_P96=0` builds p95): body, bill, crest, chest and wing matched Codex's sprite; its legs are about twice as thick (dark tubes, big gold collars, thick toes, big gold claws) where ours read as 1 to 2 px lines. Earlier passes thinned them on purpose to Preston's painting (r10, p63), so halfway: shins and tarsi 1.5x, collars and joint blocks 1.3x, toes 1.2x, claws 1.25x. Battle canvas 105x114, feet row 109; nothing cut. Godot import and all eight checks PASS; bind audit 0 of 248. Sheet: `docs/art/2d/shoebill_m/p96_before_after.png`.
- **Factory pass complete for all six** (pangolin p46, hippo p48, wolf v95, gorilla v78, kangaroo p74, shoebill p96). Lineup of the installed battle idles: `docs/art/2d/lineup_2026-10-20.png`.
