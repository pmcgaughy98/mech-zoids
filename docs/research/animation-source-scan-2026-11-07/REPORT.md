# Mecha-beast MOBA animation source scan — 2026-11-07

Preston requested a GitHub scan for attack, walk, ability and other MOBA animations, prioritizing mecha beasts, their animal anatomy, and existing MOBAs. He clarified that the game-feel knowledge lives in Claude. This report combines primary source reads, local game resources, and selected saved Claude transcripts. It is a practical shortlist and coverage plan, not an exhaustive inventory of the internet.

## Recommended route

Use a small set of compatible motion families, then author each mech's power delivery as a separate animation layer. The best immediate sources are **Quaternius's animated animals**, the **Khronos Fox** benchmark, and **RobotExpressive** for a mechanical biped test. Use **GodotIK** and procedural stepping for multi-legged bodies. Use League and SMITE to study combat phases and transitions rather than assuming their animations can become our assets.

No complete, clearly reusable mechanical-beast MOBA combat library was verified. Search results containing static robot animals, unrelated boids projects, humanoid-only libraries, or research datasets are not substitutes for that missing pack. Insect, crustacean, winged and serpentine signature attacks will need authored motion.

## The strongest sources

| Source | Verified coverage | Best use here | Material limitation |
|---|---|---|---|
| [Quaternius Ultimate Animated Animals](https://quaternius.com/packs/ultimateanimatedanimals.html) | Creator advertises 12 animals with 12+ animations each, including attack, death, kicks, gallop, walk and jump; CC0 | Closest starting library for grounded animal motion | Individual files/species/bones not inspected yet; retargeting is still required |
| [Quaternius Animated Fish](https://quaternius.com/packs/animatedfish.html) | Seven animated aquatic species; CC0 | Shark/eel swim rhythm and fin coordination | Exact clips not enumerated; no verified mage-cast clip |
| [Quaternius Farm Animals](https://quaternius.com/packs/farmanimal.html) | Seven animated farm animals; CC0 | Hoofed/heavy gait and grounded-bird candidates | Exact species and clip files still need inspection |
| [Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html) and [Library 2](https://quaternius.com/packs/universalanimationlibrary2.html) | Full catalogs advertise 120+ and 130+ humanoid animations; second includes separate combo hits and recoveries | Gorilla/kangaroo upper-body experiments; attack phase reference | Humanoid topology; free Standard downloads do not necessarily contain the full advertised catalogs |
| [Khronos Fox](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/Fox) | Actual GLB inspected: Survey, Walk, Run; 24 skin joints | Small quadruped benchmark for fennec/wolf | Model CC0, but rig/animation/conversion require CC BY 4.0 attribution |
| [RobotExpressive](https://github.com/mrdoob/three.js/tree/master/examples/models/gltf/RobotExpressive) | Actual GLB inspected: 14 clips including Punch, Death, Walking, Running, Jump, WalkJump | Mechanical biped benchmark | Humanoid, not knuckle-walking gorilla or shrimp; CC0 credit is in the [upstream example](https://github.com/mrdoob/three.js/blob/master/examples/webgl_animation_skinning_morph.html) |
| [GodotIK](https://github.com/monxa/GodotIK) | MIT FABRIK solver, effectors and constraints for Godot 4.3+ | Stable feet, leg targets and landing correction | Tool, not clip library; native binary compatibility needs testing |
| [Godot Spider](https://github.com/bzdghf/godot-spider) | MIT procedural steps with raycasts, phase offsets, step height and IK | Spider/scorpion/beetle/crustacean gait design | Godot 3 scene/script syntax; requires a deliberate port |

The [full source catalog](source-catalog.csv) contains 31 entries, including usable candidates, research tools, existing MOBA references, installed tools and an excluded name collision. Verification status is recorded per entry. Listing an asset as a candidate is not a claim that it was retargeted successfully.

## What the downloaded GLBs actually contain

Only these two small, openly licensed samples were downloaded, into `D:/dev/_scratch/animation-scan/samples/`, outside the game's assets. No proprietary game model was downloaded.

**Fox:** Survey 3.4167 s; Walk 0.7083 s; Run 1.1583 s. No attack, death or spell animation in this GLB.

**RobotExpressive:** Dance, Death, Idle, Jump, No, Punch, Running, Sitting, Standing, ThumbsUp, Walking, WalkJump, Wave, Yes. Punch is 0.8333 s; Death and Walking are each 0.9583 s. These are source clip durations, not approved MOBA timings.

[verified-clip-manifest.json](verified-clip-manifest.json) records URLs, hashes, sizes, skin joint counts, clip names and durations. Metadata inspection was completed; rendering, retargeting and gameplay quality were not tested.

## Existing MOBA and mecha-beast references

**The League repository was recovered.** Saved Claude main-chat history and `docs/plan/moba-skeleton-synthesis-2026-11-03.md` identify [DaughterOfZaun/League-of-Jinx](https://github.com/DaughterOfZaun/League-of-Jinx). It is a fan-made Godot project, not Riot's official game source. Its visible engine layout separates spells, buffs, passives, events, units and stats. No root license was found. Its presence is evidence for architecture study, not a reusable animation license.

[LeagueConvert](https://github.com/jochem-waque/LeagueConvert) is an archived GPL-3.0 converter for League models and animations into glTF. This confirms a model/animation inspection route exists; it does not grant reuse rights to the underlying game content. [LeagueSandbox's README](https://github.com/LeagueSandbox/GameServer) describes a cease-and-desist history, so it is not the preferred source for this animation task.

**No separate SMITE source repository was verified in the saved relevant Claude records searched.** [UE Viewer's compatibility table](https://www.gildor.org/projects/umodel/compat) lists support for the original SMITE. The tool supports Unreal Engine 1–4 resources; that is not a verified SMITE 2 pipeline. The MIT tool license does not license a game's assets.

The official [SMITE 2 update notes](https://www.smite2.com/news/closed-alpha-1-update-notes/) provide useful primary animation lessons: chain attacks can have different swing times, attack transitions need smooth blending, and quicker entry into knockup/falling states improves response. None of those facts supplies an exportable animation file.

Proposed viewing targets, **not downloaded or measured clips**: mechanical creature skins and insect/serpent champions in League; Khepri, Arachne, Ah Muzen Cab, Fenrir, Cerberus and Jormungandr in SMITE. Judge wind-up silhouette, projectile origin, attack while moving, root/torso separation, and recovery. Do not assume their frame counts or timing fit our game.

[ZoidsLegacyDecomp](https://github.com/jmacato/ZoidsLegacyDecomp), also recovered from Claude, remains a mecha-beast game-structure reference. Its README requires the user's own ROM and does not provide a ready-made 3D animation library. [Demonstrandum/Zoids](https://github.com/Demonstrandum/Zoids) is actually a Zig boids experiment: excluded despite its name.

For mechanical locomotion, [Legged Gym](https://github.com/leggedrobotics/legged_gym) and [Webots](https://github.com/cyberbotics/webots) are engineering references for rigid links, stance and contacts. They are not MOBA combat clip packs. Legged Gym's license explicitly points to separate asset licenses and its README recommends newer Isaac Lab environments.

## Research sources that should not be mistaken for production assets

- [AI4Animation](https://github.com/sebastianstarke/AI4Animation), [AnimationAuthoring](https://github.com/paulstarke/AnimationAuthoring), and [AI4AnimationPy](https://github.com/facebookresearch/ai4animationpy) are strong quadruped/gait references, but their stated noncommercial restrictions matter. Do not label their dog mocap a free commercial game library.
- [OmniMotionGPT](https://github.com/USRC-SEA/OmniMotionGPT) describes 1,240 motions across 36 animals. Its code is MIT, but its [NOTICE](https://github.com/USRC-SEA/OmniMotionGPT/blob/main/NOTICE.txt) retains noncommercial terms for the underlying DeformingThings4D data.
- [AnimalSyn3D](https://github.com/CJcool06/AnimalSyn3D) provides sparse keypoints/skeleton sequences for 13 animals, derived from the same data family. It is not a drop-in skinned creature library; a clear root license was not found.
- [PAN](https://github.com/hlcdyy/pan-motion-retargeting) demonstrates human/dog BVH mapping, but explicitly requires respecting the input datasets' separate terms. Research retargeting is not a guarantee of correct armor, claw or wing motion.
- The [Godot quadruped demo](https://github.com/TheBogdichHD/procedural-animation-godot) credits a noncommercial/no-derivatives fox and a separately attributed dog. A useful demo can contain assets with different rights.

## What was recovered from Claude

Located and selectively reviewed these saved chats: **Run the mech MOBA game feel lane**, **Build mech walk animations**, **Build mech attack animations**, **Run the mech animation lane (fork)**, and both saved **Mech-Zoids Game** histories. Transcript IDs and selected evidence are retained locally in the JSON files here. Other chats were not treated as instructions or approval.

The durable lessons, corroborated where possible against project files:

1. **Attack phase matters more than a generic swing.** Gorilla's current kit distinguishes locked wind-up/contact from a cancelable recovery. `ape_kit.gd` still documents this behavior. Preserve contact/release events while allowing each kit to choose its cancel rules.
2. **Foot speed must match travel speed.** Historical gorilla analysis found 3.5 / 0.48 ≈ 7.3 times travel-to-foot-speed mismatch. That is a dated diagnostic, not a new balance recommendation. A longer-stride run is often better than accelerating a tiny walk cycle until it becomes unreadable.
3. **A preset called walk may be a trot.** The saved rhino MeshForge work rejected the default preset's near-diagonal pairing, then authored a lateral-sequence four-beat walk. Its reported side stride was 0.478 m/s against a 0.48 target.
4. **Rig fit and rigid parts need inspection.** Rhino's original auto-fit placed joints incorrectly; hand fitting, rigid horn/back-plate bones and weight repair were required.
5. **One model, one animation, one fixed camera.** Render all directions from the same rig at the project's 35-degree art angle. Independently generated views and independently scaled body references produced persistent drift.
6. **Armor and effects are separate.** Plates remain rigid; joints provide compression and recoil. Active flames, steam, shields, lightning and projectiles are separate VFX with timed events.
7. **Prior approval does not make a later version correct.** Read actual current resources rather than assuming older playbook status remains current.

The corpus contains much more project knowledge than this scan needed. This was a focused extraction, not a claim to have fully reviewed every Claude conversation.

## Current local animation inventory

Eight `*frames.tres` resources were inspected: six mech resources and two minion variants. This is a resource snapshot, not a complete audit of dynamically generated runtime animations.

| Resource | Named action families observed |
|---|---|
| Ape | idle, walk, chest_beat, hex_shield, bound, hex_dome, death |
| Rhino | idle, walk, horn_jab, horn_toss, brace, stampede, death, ground_pound, brace_shuffle |
| Fennec | idle, walk, sand_kick, ear_burst, sonic_boom, dig, pop_out, death, cast |
| Hippo / Kangaroo / Lobster | idle and walk |
| Blue / red minions | idle, walk, attack, hit, death |

Gorilla code references strike behavior, while the inspected SpriteFrames resource has no named strike/strike_b action. Check fallback/runtime construction before calling that set complete. Rhino's tilt metadata names idle, walk and horn_jab; Ape's tilt metadata now includes more actions than the older playbook status. [existing-animation-inventory.json](existing-animation-inventory.json) preserves the exact observed names and view suffixes.

## Animation coverage for this roster

Use [animation-requirements.csv](animation-requirements.csv) as the production checklist. These are required behavior categories and proposed IDs, **not claims that source clips already exist**.

**Core locomotion:** relaxed/combat idle, movement start/stop, walk, run where justified, turning, strafing/backpedal when combat design needs it, and hover/swim equivalents.

**Basic combat:** alternating or chained melee attacks, stationary ranged fire, moving ranged fire, empowered attack, recovery, and equipment vent/reload/reset when visible.

**Abilities:** quick cast, heavy cast, charged attack, channel start/loop/end/interruption, dash/charge phases, leap/landing, shield/guard deployment and release, heal/tether, stealth entry/reveal, transformation and terrain traversal where the kit uses them.

**Reactions:** directional light hits, heavy stagger, stun, knockback, knockup/fall/landing, knockdown/get-up. Avoid restarting a full stagger on every rapid ADC hit.

**Lifecycle:** spawn/respawn, death and held corpse pose, recall start/loop/finish/cancel if recall exists, selection and optional victory/taunt presentation.

Do not demand every optional action from every beast. A floating jellyfish needs a hover cycle, not a manufactured footstep walk. A shield tank needs a sustained guard state. An ADC needs torso/weapon firing that can coexist with locomotion if its gameplay allows movement while firing.

## Match motion families to bodies

| Family | Roster candidates | Reuse strategy and custom work |
|---|---|---|
| Small quadruped | Fennec, wolf | Fox/animal gait benchmark; author blink/lunge/spectral moves |
| Heavy quadruped | Bison, rhino, hippo | Retarget gait cautiously; custom weight shifts, charge, stomp, furnace/pressure recoil |
| Low armored quadruped | Tortoise, pangolin, chameleon | Different stance and joint limits; shell/plates rigid, custom shield/magnet/cloak actions |
| Biped/knuckle/hopper | Gorilla, kangaroo | Biped upper-body clips only as a starting point; distinct knuckle gait/hop and tail balance |
| Ground bird / flyer | Shoebill, falcon, hummingbird | Separate legs and wing controls; takeoff, hover, bank, landing, wing-fire or moon cast |
| Six/eight-legged | Beetle, mantis, spider, scorpion | Explicit limb count and step-phase rig; custom claw/blade/tail/chemical attacks |
| Crustacean | Lobster, pistol shrimp | Distinct walking legs and claw controls; heavy anchor and snap recoil |
| Insect flyer | Hornet, dragonfly | Independent wing root loops, body hover and forward-firing hardware; avoid canine/humanoid retarget |
| Serpentine / swimmer | Cobra, electric eel, shark | Chain rigs and body waves; custom wall contact, storm wind-up, bite/undertow |
| Radial floater | Jellyfish | Bell pulse and tendril chain controls; custom heal/tether motions |

**Asymmetry changes export:** the old sprite pipeline mirrors three directions. Pistol Shrimp's one giant anatomical-right claw must not swap sides under that mirror. Render eight real directions, or change the export/playback representation deliberately; do not silently reuse the five-view mirror shortcut for asymmetric bodies.

## Tools now available and limits

**Animator is installed** at `D:/dev/Animator`; dependencies and `npm run build:web` passed. The sample rig loaded in the UI with 20 bones. Open [the local studio](http://127.0.0.1:5178/) or run `D:/dev/launch-animator.ps1` to restart it. It has no native MCP server in the inspected repository. Its procedural library includes humanoid walk/run/strafe/punch/kick/dodge-style builders; these do not automatically solve beast anatomy. No native Tauri build was installed. The upstream repo is archived.

**MeshForge/Keyframe MCP** was added to Codex and the 33-tool catalog handshake passed. The existing rhino manual-clip method is a better starting point than assuming a stock preset is correct. Live browser profile access and the account's saved key were not inspected during this scan.

**Summer's curated motion route** explicitly targets Meshy-rigged humanoids; its documented five short aliases are idle/walk/run/jump/attack. Other library names must be exact. It is not a stock quadruped/insect solution, and its extra wing/tail bones require authored animation. No paid generation was called.

**Agent animation skills** were inspected as references only. The 64px sprite skill differs from this project's 192px/35-degree pipeline. The Spine cut-part workflow also differs from the unified 3D route and advertises noncommercial terms. Neither was installed or applied.

## Concrete next production order

1. Test the licensed Fox walk and RobotExpressive punch on disposable reference scenes to establish import/export/event handling, then compare one actual beast rig. This scan did not run those retarget tests.
2. Audit the Quaternius animal download for exact skeletons and clip names before choosing a heavy and small-quadruped baseline.
3. Establish separate gait rigs for multi-legged, winged and chain bodies instead of forcing all animals onto one skeleton.
4. For each mech, author one clear basic attack first: anticipation, release/contact, recoil and recovery. Then add its signature power move and required hit/death states.
5. At every handoff, verify armor rigidity, feet/hover height, projectile origin, event timing, motion cancellation, and all rendered directions in the real match.

No game code or canonical kit was changed by this research. No proprietary model/animation was installed and no paid animation job was submitted.

