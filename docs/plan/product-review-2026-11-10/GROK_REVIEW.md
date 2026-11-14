# Grok initial design review

Generated 2026-11-10 through the existing Grok Build subscription connection. This is a design proposal, not approved changes. Read README.md and GROK_ADDENDUM.md first: the follow-up revises the initial fennec and economy recommendations. Native web search was unavailable to Grok; its initial external-source synthesis relies on staged local studies. The follow-up also uses SOURCE_CHECKS.md supplied by Codex. No live gameplay or model changes were performed.

---

# REPORT

**Mechanical-animal MOBA — director’s recommendation**  
Date: 2026-11-10. Snapshot only: `D:/dev/_scratch/grok-game-design-2026-11-10`. Design proposals. No implementation permission. Desirability still needs human playtests.

## Answer first

Keep the compact **3v3 third-person mechanical-animal MOBA**. Original SMITE remains the control and camera reference. Paragon remains the secondary combat-feel reference. Do not grow this into 5v5 Conquest, isometric League, or a hero-shooter.

The product already has a distinctive fantasy: **living factory animals with weight, silhouette, and readable animal motion**. The gorilla is the proof. The job is to make that fantasy combat-irresistible in a short match, then give it three teammates who create different fights.

The current game is a **single-player arena prototype**. It has match structure, waves, towers, cores, camps, side pits, a plaza beacon, recall, respawn, fog, and a SMITE-fitted chase camera. It has **no store, no gold income, no items, and no networking**. Most of the 25 catalog bodies are static proxies. Fennec is a mixed experiment. Pixel/RPG documents are historical.

**Chosen path:** compact 3v3 SMITE-feel arena on the existing Foundry map. First playable roster: **gorilla, rhino, rewritten fennec, falcon**. Cut for this phase: finishing 25 kits, a shop, 5v5 scale, Janus-clone fennec, sand/tunnel leftover, and any kit that exists only as a god reskin.

**Favorite fennec:** **Rift Conductor**. One combat boom, one split-shot poke, one pocket-gate signature, one team-carry ultimate. Portals stay meaningful. They leave three of the five combat verbs.

## 1. Current product

### Player fantasy now

A third-person factory beast. You occupy a heavy mechanical animal, aim with the mouse, and fight in a short industrial lane with jungle pockets. The strongest current hook is the gorilla: knuckle-walk weight, green hex technology, grab-slam, Shield Drive, and a chest-beat cage. That is original in this snapshot. The animal bodies are original. Several planned kits still borrow SMITE role shapes too closely.

### Core combat loop (implemented)

WASD move. Mouse aim / facing. Q/E or right-drag camera. Space/LMB basic. 1–4 abilities. B recall. F8/Tab pick a body. MatchDirector runs waves, towers, cores, camps, bots, death, respawn, and win (`references/scripts/moba3d/match_director.gd`, `arena_play.gd`).

A typical minute: spawn, walk the lane, first wave at 5 s, waves meet near the plaza around 20 s, machines fight over that meeting, side pits can be taken to fatten later waves, beacon appears at 4:00 and can shut an enemy tower for 30 s, destroy the tower, then the core. All timers and damage numbers in `match_rules.gd` are placeholders.

### Implemented vs planned vs experiment vs unverified

| Layer | State | Evidence |
|---|---|---|
| Compact 3v3 Foundry arena, one lane, jungle camps, fog, recall, respawn | **Implemented** | `arena_play.gd`, `match_director.gd`, `arena_blockout.gd`, MATCH_NOTES |
| Towers, cores, minion waves on nav mesh | **Implemented**, numbers placeholder | `match_structure.gd`, `match_minion.gd`, MatchRules |
| Side capture pits (wave power) | **Implemented** | `arena_pit.gd`: 9/6/4.5 s capture, 90 s lock, `pit_wave_bonus` 0.25 |
| Plaza beacon (tower off) | **Implemented** | `arena_beacon.gd`: first up 240 s, back after 300 s, `beacon_tower_off` 30 s |
| Store / gold / items | **Not built** | CURRENT_BRIEF, ARENA_REFRESH |
| Networking / host authority | **Not built** | ARENA_REFRESH |
| Gold boss (stag beetle) and power boss (elephant) | **Art/reward proposals** | `objective-bosses-2026-11-10/REPORT.md`, jungle-objective-synthesis |
| Minion melee/ranged/siege sheets | **Concept art**, not rigged runtime | CURRENT_BRIEF, minion-set report |
| 25 catalog 3D bodies in arena | **Implemented as presentation** | `roster.json`, ARENA_MODEL_PIPELINE |
| Authored locomotion + kit clips | **Gorilla trial, rhino trial** | roster stages `authored_trial` vs `base_proxy` |
| Gorilla kit (shield, Grab Slam, Shield Drive, chest-beat cage) | **Implemented in arena**, numbers draft | `arena_gorilla_kit.gd`, `ape_kit.gd`, `arena_grab.gd`, `arena_drive.gd` |
| Rhino kit (plating, horn toss, pound, brace, stampede, horn jab) | **Implemented**, native clips only partially bridged | `rhino_kit.gd`; rhino clips: idle, walk, horn_attack, brace, charge. Ground-pound body/piston still pending |
| Fennec | **Isolated mix**: old sand/tunnel/boom + blink gate + two-faced preview on key 5 | `fennec_kit.gd` header and keys 1–5 |
| Squirrel / falcon / wolf / hummingbird / shoebill / hippo / lobster / kangaroo | **Partial**: usually basic, sometimes 1 slot | kit file headers |
| Chameleon, pangolin, and 12 extra catalog animals | **Bodies only** or plan-only | no chameleon/pangolin kit scripts in this snapshot |
| Automated checks | **Verified in refresh notes**, not re-run here | match_check 67/0; arena_roster_check 104 at 15/60/120 fps |
| “Feels irresistible” | **Unverified** | this run did not launch the game |

### Gorilla, as actually coded (arena)

Parent `ApeKit` still documents the older 1 shield / 2 chest beat / 3 bound / 4 hex dome slice. Arena Play installs `arena_gorilla_kit.gd`, which overrides:

- **1 Hex shield.** `hex_shield()` in `ape_kit.gd`. Nearest ally in 6 m, else self. 3D clips `Shield_Self` / `Shield_Ally`. Lands on `release`, fallback 0.25 s. Clears one slow. Green hex shell, no orbiting gems.
- **2 Grab Slam.** `fling()` → `arena_grab.gd`. Capture 0.18 s, impact 0.60 s. Real match victims. Busy/non-interruptible kits and braced rhinos are ineligible. Whiff clip if the grab fails.
- **3 Shield Drive.** `bound()` override → `arena_drive.gd`. Brace `29/120` s, travel `38/120` s at 12 m/s, front 1.30 m, half-width 0.64 m, damage 24, shove 0.70. Green hex energy ahead of both hands (`shield_drive_energy.gd`). Recovery cancel after ~0.23–0.27 s.
- **4 Chest-beat cage.** Arena override of `chest_beat_ult()`: three Ult `beat` events. Beats 1–2 taunt in `ult_radius` 5.5 m for 1.5 s. Beat 3 raises the cage (`ult_dome_radius` 5.5 m) with `ward` heal share. Parent `ape_kit.gd` comment records a later call: **no ally shields on the ult**; beat 2 re-taunts. That is the live arena kit. The November 9 plan in `moba-kits.md` (beat 2 mass hex shield) is **not** what arena currently does.
- **Passive silverback.** `covers()`: allies inside 2.5 m take reduced damage (amount unset).
- **Basic.** Chain swat / swat / slam. 28 / 28 / 42, 1.0 s, 2.2 m edge, 60° cone, assist turn. 3D clips `Swat_Right`, `Swat_Left`, `Slam`. Contact on damage event, then hitstop. Backswing is free; movement or an ability cancels it (`_strike_3d`).

Codex’s latest heavy-basic weight pass is a **review candidate**, not an approved finisher (CURRENT_BRIEF).

### Fennec, as actually coded

`fennec_kit.gd` keys: 1 `sand_kick()`, 2 `blink_gate()` / recast `gate_back()`, 3 `tunnel()`, 4 `sonic_boom()`, 5 preview `two_faced_shot()`. Passive `_listen()` pings movers in 9 m. Basic is a 6 m violet dart. Taken portal kit in `moba-kits.md` is only partly present. MECH_STATUS.md matches that inventory.

### Pixel/RPG vs present 3D MOBA

`START_HERE.md` (2026-10-11) is a Zoids-Legacy-inspired deck RPG with hangar, canyon, and command cards. `3d-pivot-2026-10-11.md` is the first 3D gorilla blockout. Those documents explain why the animals and factory look exist. They do **not** describe the current product. Current product is the 2026-11 arena MOBA in `arena_play.tscn`, with SMITE camera fit applied 2026-11-10 (`smite-camera-framing-2026-11-09.md`: pitch 13°, distance 12 m, look height 3.2 m, god ~11% of screen, aim point on the ground ~13.9 m ahead).

### Friction (local, some firsthand)

- 23 bodies slide. Flyers hover. That reads as unfinished, not as a style.
- Fennec’s live buttons still teach sand and digging after portals were chosen.
- Gorilla plan docs, parent kit comments, and arena overrides disagree on ult beat 2.
- Rhino native clips do not yet cover the full kit clock.
- All machines share 600 HP (`MatchRules.machine_hp`). Roles do not yet have bodies.
- Respawn is 8 s. A 3v3 death is cheap; a 30 s tower-off is expensive. Those two facts fight.
- MATCH_NOTES: a normal 130 s with six machines stalled at the plaza. The 59 s tower-push video held red bots at base.
- Camera clamp can hide the machine behind the base wall.
- Audio: MapAudio one-shot cap 8; gorilla/fennec often have callouts without a press sound (moba-audio-synthesis).
- Thin-center melee miss is **reported by Preston**, not proven as a hitbox bug.

### Distinctive hooks worth keeping

1. Factory-animal silhouette with authored weight (gorilla).
2. Green hex technology as a readable faction language.
3. Compact 3v3 with pits and a beacon instead of a 40-minute 5v5.
4. Portals as a team tool on a small map, if they stop eating the whole fennec kit.
5. Third-person aim with a SMITE-low camera, so the ground in front of you is the battlefield.

## 2. Reference synthesis (what actually transfers)

Local studies already extracted the useful lessons. This run did not re-open live game clients or paid page fetches.

**Original SMITE (primary).** Third-person chase, mouse aim, god low on screen, combat space in front of the character. Hi-Rez audio deep dive (SMITE 2 talk about SMITE 1): a sound on press, a sound that tells you what hurt you, keep iconic cues; SMITE 1’s 32-voice cap silenced fights. Local package study of Hun Batz / Raijin is animation-coverage craft, not a kit to copy. Joust-like 3v3 and Gold Fury / Fire Giant as economy vs power are the map lessons already used for beacon timing and boss proposals.

**SMITE 2.** Separate product (UE5, Alpha Weekend notes). Useful for audio voice count, occlusion, and HUD presets. Gold Fury numbers from Alpha Weekend 1 are historical, not current balance. Do not treat SMITE 2 Janus as the fennec spec.

**Paragon (secondary).** Over-shoulder MOBA with cinematic lighting and silhouette readability. Local look study measured Predecessor store frames as a stand-in because Paragon is shut down. Transfer: rim/silhouette, not ink-outline identity. Do not inherit a card shop or 5v5 layout.

**Predecessor.** Human-made revival on released Paragon assets. Local HUD notes: keep the ability block readable in a third-person late fight. Player UI thread cited Oct 2024 in the HUD doc; not re-read here.

**League.** Objective grammar: early gold/siege asset vs later temporary power window; contest risk while you hit the monster; death can strip a personal buff. Twisted Treeline altars informed pit capture times. Do not inherit 5v5 map scale, item complexity, or execute-on-Elder as a first boss.

**TartarusArena.** Explicitly AI-built Unreal case study. Useful engineering: delayed hit resolution, re-check targets, hitstop throttling, pose blend on death, bot spacing. Not shipped-game validation. Do not import GAS or Paragon packs.

**Player friction patterns (context, not stats).** Preston, playing this prototype: keep SMITE camera/combat; keep gorilla motion; portals yes, portal-only kit no; basics should aim at a central reticle; skinny center targets may miss; liked gorilla attack animation. MATCH_NOTES plaza stalemate. Local excerpt of a 2015 r/Smite camera-height request (SMITE 1 had little camera control). Those are specific accounts. They are not a market study.

## 3. Identity and pillars

**Working title for the fantasy:** *Foundry beasts.* You are a mechanical animal built in an industrial arena. Powers come from the body: emitters, plates, cores, vents. Nothing is held in the hand.

### Pillars

1. **Weight you can see.** Attacks plant, recover, and confirm. Cancellation is a rule, not a flourish. Tradeoff: slower than a floaty action game. Misses must be honest.
2. **Silhouette combat.** Every animal reads at SMITE god size (~11% of screen). Team color and hex/energy language carry identity. Tradeoff: busy VFX that hide the mesh are out. Preston already rejected opaque gorilla shields.
3. **Short-match geography.** One lane, two side pits, plaza beacon, two later bosses with different jobs. Fights are about *where* as much as *who*. Tradeoff: 5v5 jungle tracking and a 40-minute curve are cut.
4. **One signature per beast, from the machine.** Animal gives body and at most one trait. The rest is a power theme. Tradeoff: literal sand-fox and copy-Janus both fail this pillar.
5. **Counterplay in the body.** Grabs have a windup. Gates are visible. Cages have health. Front plating has a flank. Tradeoff: mystery stealth and unreadable teleports fight the camera.

### Format choice

| Option | Verdict |
|---|---|
| Keep compact 3v3 third-person | **Chosen.** Map, camera, bots, and gorilla proof already live here. |
| Adjust to a more skirmish/objective format on the same map | **Later tuning**, not a genre change. Beacon/pits/bosses already pull toward objectives. First, stop plaza stalemates. |
| Nearby pivot (isometric, 5v5, shooter) | **Rejected for this phase.** Throws away the camera fit, gorilla animation investment, and the 3v3 hook. |

**Cut list:** 25 finished kits; shop/items until the four-beast loop is fun; 5v5 Conquest; fennec sand/tunnel as live buttons; mass-shield-on-ult unless Preston re-asks; extra leap-and-land copies (gorilla bound is already replaced by Drive).

## 4. First playable roster

**Launch/test four:** gorilla (support brawler), rhino (engage tank), falcon (ranged damage), fennec (utility skirmish, rewritten).

Why four: 3v3 plus one extra identity to swap. Animation truth: only gorilla and rhino have authored trials. Falcon and fennec can play on base_proxy bodies with strong VFX if their kits are simple and readable.

Fifth later, if a human playtest says the four feel samey: chameleon (vision/skirmish) or hummingbird (heal), not another melee pounder.

Full table is in **ROSTER AUDIT** below.

## 5. Three fennec kits

Names and numbers are provisional. Portals stay a signature. Sand-body kits are retired. Janus’s four-teleport shape is retired.

Shared constraints: S body, 3D fennec.glb reusable, ears as silhouette only, existing SmallGate / bolt / blink-flash / arrival-shield art reused where they fit, sonic-boom charge pose redrawn as emitter energy.

### Kit A — Rift Conductor (favorite)

**Role:** utility mage who *fights* and *moves the team*.  
**Promise:** you aim cracks in space. One doorway is for people. The rest of the kit is energy that comes out of those cracks.

| Slot | Working name | What it does |
|---|---|---|
| Passive | **Rift echo** | Enemies damaged by the fennec glow through fog/camo for 3 s. Scout job without “big ears.” |
| Basic | **Rift dart** | Current 6 m violet dart. 0.9 s. 30 dmg draft. |
| 1 | **Rift boom** | 0.45 s charge, then a 7 m / 40° cone of portal energy. 60 dmg draft, 2.5 m knockback. Uses the liked sonic-boom body, emitters not ears. |
| 2 | **Pocket gate** | Gate at feet + gate 4–6 m along aim, 3 s, two-way for allies. Recast: fennec steps instantly. This is the signature. |
| 3 | **Split shot** | One bolt that forks after 3 m into two 20° legs, each slow 1.2 s. Looks both ways without a second teleport. Cover-check poke. |
| 4 | **Great ring** | 0.6 s channel. Allies in 3.5 m go with the fennec to an aimed visible point or the allied tower. Arrival: 1 s shield + 30% speed for 1.5 s. Arrival ring knocks enemies 2 m off the landing (the control piece). Enemies cannot use gates. |

**Moment-to-moment:** dart, split shot to slow a pair, boom the clustered ones, pocket gate out or onto the slowed target. Ult is a rotate or a save, maybe twice a fight.

**Limits:** boom roots the fennec during charge. Pocket gate is short. Split shot is weak on a single tank. Ult channel is interruptible. Gates last seconds, not a permanent network.

**Enemy counterplay:** interrupt the boom; stand off the fork; body-block the short gate; wait the channel and greet the landing; take the 8 s respawn if you blow the save.

**Novice:** dart + boom is a complete laner. Gate is an escape button.

**Expert:** gate a gorilla Drive path, boom the landing, ult a pit steal, split shot through a minion wave into the carry.

**Anim/VFX burden:** one charge/blast (redraw boom), one fork bolt, reuse small gate + arrival shield. Lowest new body cost of the three.

### Kit B — Corridor Mage (team taxi, current-plan descendant)

Passive **gate echo** (same as A). Basic dart. **1 Threshold pulse:** while a friendly gate exists, standing near it gives +20% move, enemies near it 20% slow. **2 Pocket gates** (same). **3 Far gates:** entrance here, exit on visible ground / ally / allied tower, 5 s. **4 Great gate:** team carry, no boom.

This is the 2026-11-05 taken kit with sand removed. Combat without a gate is a dart. Experts build corridors. Novices feel empty. Overlap with a future store/ward game. **Keep as the alternative if playtests say the map is too cramped for a boom mage.** Higher VFX: two gate sizes, pulse rings, far-anchor rules.

### Kit C — Bait Fox (skirmish trapper)

Passive **trip spark:** walking through an enemy’s last-2 s movement trail refunds 1 s of slot 1. Basic dart. **1 Snap rift:** 2.5 m disk on the ground for 2.5 s; first enemy to enter is rooted 0.8 s and tagged. **2 Pocket gate** (self recast only; allies cannot use it). **3 Backblast:** if a tagged enemy is within 6 m, fire a heavy bolt from *behind them* toward the fennec (the two-faces joke, one shot). **4 Collapse:** recast all live snaps into a 4 m implosion, 80 dmg draft + 1 s slow.

This makes portals a personal trick, not a team taxi. Preston asked for team portals. **Defer unless the 3v3 already has enough team move from gorilla Drive and rhino stampede.**

### Why A is the favorite

It keeps the liked boom, the team pocket gate, and a damage button that is not a teleport. It uses existing fennec FX. Kit B is the fallback if A’s boom + ult knockback is too much control on a small map. Kit C fights the “portals for it and team” direction.

## 6. Gorilla continuity

Preserve: model, 34-bone rig, editable sources, hex shield look, Grab Slam, Shield Drive with hand energy, chest-beat cage, swat-swat-slam character, silverback aura, non-opaque shield.

### Cohesion critique

The live kit is a **protector-brawler**, and it is close to a real identity:

- Slot 1 saves a body.
- Slot 2 removes a body from the fight.
- Slot 3 arrives with a shield-first collision.
- Slot 4 holds a patch of ground and taunts people into it.

The remaining muddle is documentation, not stats. `moba-kits.md` still promises mass ally shields on ult beat 2. Arena code taunts twice, then cages, with a ward heal. **Recommend locking the live version:** protect on 1 and in the aura; ult is the display and the prison. If Preston still wants “shield allies too,” put a **short 1.5 s hex shell on allies already inside the cage at beat 3**, not a second copy of slot 1 on beat 2. That keeps one shield verb.

Clarity issues to fix without a rework:

- Slot 3 is still named `bound()` in code and used to leap. HUD already says Shield Drive; keep that name everywhere.
- Grab Slam vs Shield Drive both “go forward and hit someone.” They differ: grab is a single pickup with a 0.18 s readable windup; Drive is a braced collision line. Teach that with VFX (grip vs hex wedge) and fail states (whiff lift vs brake).
- Cage blocks allied shots. That is a real counterplay cost. Keep it. Show a cracked-panel health read so enemies know they can break out.

### Thin-center hit-shape contract

Keep the liked attack animation. Do not widen damage or lengthen reach as the first fix.

**Contract (proposal):**

1. Player aim defines a **center line** from the chest through the ground reticle.
2. On the damage event, hit with a **capsule** along that line: length `basic_range` (2.2 m edge) + 0.3 m slack, radius **0.45 m**, starting 0.4 m in front of the chest.
3. The visual fists may pass left/right of a skinny target. The **gameplay volume is the center line**, so a thin dummy on the reticle is a hit.
4. If the capsule hits nothing, the animation still plays (honest whiff, current KitFeel lunge).
5. Draw a small ground mark or hex spark at the intended contact point during windup (0.15 s). That is the “central attack point” rhino feedback asked for, shared across melee beasts.
6. Assist-turn (180° snap when the cone is empty) stays for novices, **off in a later competitive toggle**.

Drive already uses a swept volume (`HALF_WIDTH` 0.64, `FRONT` 1.30). Basics should feel like a thinner version of that honesty, not a nearest-enemy magnet.

### Measured refinements (no stat inflation)

- Confirm Grab Slam vs Drive so both remain useful: grab for a single peel, Drive for a line/engage.
- Ward heal inside the cage: keep modest (`dome_ward_heal` 0.06 is already a proposal).
- Interruption: already aborts on stun/hold. Add a clear “armor clack” on press (audio pillar 1).
- Third slam is a review candidate. Judge reach at the SMITE camera before replacing the clip.

## 7. Complementary kits (existing creatures)

All numbers draft. Existing models stay reusable.

### Rhino — engage tank (continuity)

Keep: front plating, horn toss, ground pound tremble, brace, stampede, horn jab.

**Proposed live table**

| Slot | Function | Draft |
|---|---|---|
| Passive | Front 100° takes `blocked_share` 0.5 | already coded `take_hit()` |
| Basic | Horn jab to center line, same capsule contract as gorilla, 2.0 m, 30 dmg, 0.9 s | aim to reticle |
| 1 Horn toss | 3.5 m dash, pluck, land 3 m behind, stun 1.6 s | keep |
| 2 Ground pound | 4 m slow circle, one damage pulse on first slam, 4 stomps | needs the v39 piston/body clip before calling it finished |
| 3 Brace | 3 s, 0.35 move, pound still allowed, anti-grab (already: grab skips braced rhinos) | keep, this is the gorilla-grab counter |
| 4 Stampede | 12 m knock-aside charge, finale stun ring 3.4 m | keep |

**How it plays with gorilla:** rhino starts, gorilla saves the body that got focused, Drive follows the toss.  
**Enemy joy:** flank the plates, wait brace, side-step stampede, body-block the toss so the victim lands short.  
**Why an enemy enjoys it:** the rhino is loud. You can see the rear-up and the head-down. Beating it is a positioning win.

### Falcon — ranged damage

Body is a hovering M proxy. Kit today: dart + keen-eye only.

| Slot | Function | Draft |
|---|---|---|
| Passive | Keen eye: +0% to +50% dmg from 0 to full 7 m | already coded |
| Basic | Wing dart, 7 m, 26–39 dmg, 0.9 s, width 0.35 m | already coded |
| 1 Pierce | Next dart goes through 2 extra targets at 70% dmg | short, 5 s |
| 2 Takeoff | 0.8 s hover, 3 darts into a 2.5 m disk, then land | medium |
| 3 Stoop | 5 m dive, first hit 40% slow 1.2 s | medium; the only body move |
| 4 Sky barrage | 3 s rain on a 3.5 m disk in vision, camera 55–60° per Preston | long, 40 s |

**Combo:** hold max range, pierce the wave, stoop when dived, barrage a pit or a caged cluster.  
**Enemy joy:** walk at it. The falcon is fragile and grounded after takeoff. Hide in fog, then the keen-eye bonus dies.  
**Overlap watch:** shoebill is the same “stand back and delete.” **Defer shoebill.** Squirrel is the hop-carry; defer it too so falcon owns range.

### Fennec — Kit A above

The fourth slot in the test roster.

### Why this four, and what is missing

3v3 example: gorilla + falcon + fennec vs rhino + falcon + fennec is playable. Missing on purpose: dedicated assassin (wolf), dedicated healer (hummingbird), stealth (chameleon), catcher (lobster). Those are second-loop identities. A 3v3 with wolf + chameleon + fennec becomes a fog stabbing game the camera is not ready to sell.

**Enemy enjoys facing each**

- Gorilla: you can bait the grab, break the cage, and kite Drive.
- Rhino: you can flank and punish the rear-up.
- Falcon: you can dive it and make keen-eye worthless.
- Fennec: you can interrupt the boom and greet the landing.

If a fight is not fun to *lose to*, the kit is wrong. These four fail in readable ways.

## 8. Match progression

Connect the existing pieces **before** inventing a shop.

| System | Job | Already? |
|---|---|---|
| Waves every 30 s from 5 s | Clock and lane pressure | Yes |
| Side pits | Strengthen *future* waves (+25% HP/dmg per pit) | Yes |
| Plaza beacon at 4:00 | 30 s enemy tower off | Yes |
| Ordinary camps | Local HP/time sink, 60 s respawn | Yes, olive stand-ins, no reward item |
| Towers | Gate the core; switch agro if you hit an ally | Yes |
| Gold boss (beetle) | Team gold payout | Proposal only; **needs a store or it is a dummy number** |
| Power boss (elephant) | Temporary combat + structure damage, lost on death | Proposal only |

**Prerequisite honesty:** gold payout does nothing until there is something to buy. First playable can ship **without** a store if the gold boss waits. Power boss can ship as a buff with no shop.

**Suggested job split (same as the jungle synthesis, endorsed):**

- Pits = minion quality.
- Beacon = a short hole in a tower.
- Gold boss (later) = buy a spike.
- Power boss (later) = win the next fight/push.
- Do not let pits + beacon + power boss all mean “the tower dies for free.”

**Snowball watch:** 8 s respawn is forgiving. 90 s pit lock + 30 s tower off is not. If the leading team also gets a power buff, the match ends from a single 4:00 take. **First test rule:** beacon and pits live; bosses off. Measure how often a tower falls from beacon alone.

### First 60 seconds

0:00 spawn, camera down the lane. 0:05 first three drones. Players can leash a camp or walk with the wave. 0:20 plaza clash. First fight is the wave meeting plus one skill trade. Taking a pit this early costs the clash. That is the first real choice.

### First fight

A 3v3 around the plaza with minions as cover. Gorilla Drive/grab, rhino pound, falcon darts, fennec boom. If nobody dies, the game currently stalls (MATCH_NOTES 130 s). **Fix with objectives, not damage inflation:** make the nearest pit’s ring visible from the plaza, so the losing clash has a place to go.

### First objective

The **side pit**, not the beacon. It is always available. Reward is the next wave, ~30 s later, so the take is a delayed punch. Beacon at 4:00 is the first *map event* that can end a tower.

### Midgame comeback

Losing team takes the remaining pit, waits beacon, or catches a greedy camp. 8 s respawns mean a wipe is not a lost match unless a tower is already open. When bosses exist: gold boss is the comeback purchase; power boss is the “we can actually siege now” window. Death strips power, so a catch on the way out is the defense.

### Ending the match

Tower down (maybe during beacon). Core is hittable. Power boss, if live, is the honest siege window: escort a fat wave (pits) through a dark tower (beacon) with a personal buff (boss). Without a boss, ending still works: fat wave + beacon hole. **That should be the first playable end condition.**

## 9. Implementation sequence

Proposals only.

### Slice 1 (small, demonstrable, this week of work)

**Gorilla vs skinny dummy + rhino, center-line melee contract.**

- Assets: none new. Reuse gorilla/rhino trials.
- Code: shared aim capsule + ground mark on gorilla and rhino basics.
- Preserve: current clips, damage, timings.
- Timing contract: hit on existing damage/jab events only.
- Playtest (human): 10 minutes. Can a thin pole on the reticle be hit by the liked slam? Does the animation still look like the animation he liked?
- Pass: Preston says yes to both.

This validates the latest user feedback on the only professional-feeling combat.

### Slice 2 — Fennec Kit A in the real arena

- Move boom to 1 (portal energy VFX on existing cone).
- Upgrade blink gate to two-way pocket gate (allies).
- Put split shot on 3 (reuse bolt).
- Great ring on 4 (reuse arrival shield).
- Disable sand/tunnel as live keys.
- Body: base_proxy fennec is enough if cast/boom poses exist; redraw boom emitters later.
- Playtest: can a novice escape with 2, and can an ally walk the gate without a tutorial?

### Slice 3 — Four-beast bot match, bosses off

Gorilla, rhino, falcon (pierce + stoop only; barrage later), fennec A. Same Foundry map. Record whether plaza still stalemates and whether beacon + pits already end towers too fast.

### Slice 4 — Audio press cues for the four

SMITE pillar 1. Eight sounds beat a shop.

### Later

Falcon barrage camera 55–60°. Rhino v39 pound. Power boss as a buff with no gold. Store only after gold has a sink. Wolf/chameleon/hummingbird after four beasts are fun.

### Work vs animation readiness

| Beast | Model | Motion | Kit code | Next cost |
|---|---|---|---|---|
| Gorilla | authored trial | high | high | hit-shape, naming, audio |
| Rhino | authored trial | medium (bridged) | high | pound clip, reticle |
| Fennec | static proxy | sprite leftover + slide | mixed old/new | kit rewrite, boom redraw |
| Falcon | static hover proxy | none | basic only | 3 simple spells, VFX |

Finishing falcon’s three spells is cheaper than animating a fifth animal. That is why falcon is in the four.

### What humans must validate

Feel of weight, whether portals are fun for *allies*, whether cage-shot-block is miserable, whether 8 s respawn plus beacon is snowbally, whether the slam still looks good with a center capsule, whether the product is desirable. Checks passing is not that.

### Decisions Preston needs

1. Lock gorilla ult as taunt + cage + modest ward, with optional in-cage shells, or restore beat-2 mass shields.
2. Take Fennec Kit A, B, or a mix.
3. First four: gorilla / rhino / fennec / falcon, or swap falcon for squirrel.
4. Boss animals: beetle/elephant, or different.
5. Gold meaning: payout vs income, and whether a store is in scope before those bosses.
6. Assist-aim on melee: keep, or competitive off-toggle.
7. Approve or reject the Codex heavy-basic review candidate on art, independent of damage.

---

# ROSTER AUDIT

Readiness: **authored** = native clips in arena; **kit-partial** = some slots in GDScript; **proxy** = static 3D body; **legacy sprite** = lobster. Roles from `moba-kits.md` unless noted.

| Animal | Size | Readiness / current role | Keep / change / defer | Unique promise | Overlap risk |
|---|---|---|---|---|---|
| Gorilla | L | Authored trial. Protector-brawler. Full arena kit | **Keep** as foundation | Hex tech, grab, Drive, cage | Leap-and-land already removed |
| Rhino | L | Authored trial, kit full on sprite clock. Engage tank | **Keep**, finish pound clip | Front plates, tremble, stampede | Hippo also “owns a patch” |
| Fennec | S | Proxy body. Mixed old/new kit. Planned utility mage | **Change** to Kit A | Team pocket gate + rift energy | Janus clone if every slot teleports |
| Falcon | M | Proxy hover. Basic + keen eye. Ranged carry | **Keep** as first ranged | Distance-scaled darts, sky rain | Shoebill long-range; squirrel poke |
| Wolf | M | Proxy. Basic + lunge only. Assassin | **Defer** | Hunt wounded | Needs fog/readability first |
| Squirrel | S | Proxy. Dart + Hearsay only. Mobile carry | **Defer** | Tail relay, hop-shoot | Falcon + fennec mobility |
| Hummingbird | S | Proxy hover. Needle + link + beak. Healer | **Defer** (fifth candidate) | Bond beam | Only healer; 3v3 may not need it yet |
| Shoebill | M | Proxy. Patience + moonbeam + flick. Artillery | **Defer** | Charged long line | Falcon owns “far damage” |
| Hippo | L | Proxy. Bite only. Sustain tank | **Defer** | Territory meter, chomp | Rhino/gorilla frontline |
| Lobster | L | **Legacy sprite**, no catalog GLB. Catcher | **Defer body**; keep pull as a *future* kit | Claw cable pull | Gorilla grab already peels |
| Kangaroo | M | Proxy. Basic only. Brawler | **Defer** | Punch rhythm, ring | Gorilla melee |
| Pangolin | M | Proxy. Plan only (iron ball). Diver | **Defer** | Momentum roll | Needs animation; overlaps wolf dive |
| Chameleon | M | Proxy. No kit script. Scout | **Defer** (fifth candidate) | Camo, vision | Fog/stealth on this camera is hard |
| Bison | L | Proxy, no kit | **Defer** | Future siege brute | Rhino charge |
| Bombardier beetle | M | Proxy, no kit | **Future proposal** | Directed chemical cone, area deny | Shoebill/fennec zones |
| Cobra | M | Proxy, no kit | **Future** | Commit-strike from hood coil | Wolf |
| Dragonfly | S | Proxy hover, no kit | **Future** | Vertical scout, intercept darts | Falcon stoop |
| Electric eel | M | Proxy hover, no kit | **Future** | Chain shock through clustered units | Squirrel Hearsay |
| Hornet | S | Proxy hover, no kit | **Future** | Mark-and-sting repeat dive | Wolf |
| Jellyfish | M | Proxy hover, no kit | **Future** | Soft zone, slow field | Hippo wallow / rhino pound |
| Mantis | M | Proxy, no kit | **Future** | Predatory reach, hold | Lobster grab, gorilla grab |
| Pistol shrimp | S | Proxy, no kit. Kept as own design | **Future** | Aimed shock-cavitation poke | Falcon dart |
| Scorpion | M | Proxy, no kit | **Future** | Hook + venom DoT | Lobster pull |
| Shark | M | Proxy hover, no kit | **Future** | Commit dash through a line | Rhino stampede |
| Spider | M | Proxy, no kit | **Future** | Web terrain | Fennec gates as terrain |
| Tortoise | L | Proxy, no kit | **Future** | Shell fortress, walk-up siege | Gorilla cage, rhino brace |
| Legacy lobster | L | Sprite only | **Keep art path parked** | Pull support | No GLB; pistol shrimp is a different animal |

**Realistic first playable:** gorilla, rhino, fennec (A), falcon.  
**Do not finish 25 kits.** Extra catalog bodies stay as F8 dress extras with `arena_base_kit.gd` test shots.

**New-creature bar:** a future animal needs a job the four lack. Strongest unfilled jobs after the four: **vision/stealth (chameleon)**, **catcher pull (lobster when a GLB exists)**, **healer (hummingbird)**. Bombardier beetle is the only extra I would sketch early, and only if zone-deny is missing after fennec boom. It can wait.

---

# SOURCES

Native web search was **not available** in this environment (read/grep/list only; no MCP, no paid fetch). Dates below are from the staged files or from the local study that originally retrieved the page.

| # | Source | Date | Kind | What was actually read this run | Lesson | Limit |
|---|---|---|---|---|---|---|
| 1 | `CURRENT_BRIEF.md` | 2026-11-10 | Local product direction | Full | Current product is 3D mechanical-animal MOBA; gorilla foundations; no store/net | Snapshot, not live checkout |
| 2 | `docs/team/ARENA_REFRESH_2026-11-10.md` | 2026-11-10 | Local implementation | Full (~53 lines + table) | What moved into arena; 23 sliding bodies; checks claimed | Tests not re-executed here |
| 3 | `docs/art/moba/ARENA_MODEL_PIPELINE.md` | 2026-11-10 | Local pipeline | Full | Base proxy vs authored trial; gorilla/rhino clips | Builder lives in live project |
| 4 | `art/arena_models/roster.json` | snapshot | Local registry | All 25 `id`/`stage`; gorilla & rhino clip lists | 2 authored, 23 proxy; no lobster GLB | Hashes not verified this run |
| 5 | `docs/plan/moba-kits.md` | 2026-11-03…11-09 | Local kit plan | Role map + gorilla/rhino/fennec + checks | Ode-to rule; fennec portal takes; gorilla ult plan | Plan ≠ arena code |
| 6 | `arena_gorilla_kit.gd`, `ape_kit.gd`, `arena_grab.gd`, `arena_drive.gd` | 2026-11-09/10 | Local code | Headers + key functions (`hex_shield`, `fling`, `bound`/`drive`, `chest_beat_ult`, `_strike_3d`, `_strike_pick`) | Live gorilla kit and hit rules | Feel unverified in-engine |
| 7 | `fennec_kit.gd`, `fennec_s/MECH_STATUS.md` | 2026-11-04/05 | Local code + status | Header, keys, status table | Sand/tunnel/boom still live; portals partial | Sprite-era frames |
| 8 | `match_director.gd`, `match_rules.gd`, `arena_pit.gd`, `arena_beacon.gd` | 2026-11-04/05 | Local code | Full rules file; director waves/bots; pit/beacon contracts | Match loop and placeholder economy | Numbers are picks |
| 9 | `docs/reference/jungle-objective-synthesis-2026-11-10.md` | 2026-11-10 | Local study of first-party pages | Full | Gold vs power; pits/beacon/boss split | Several pages were excerpts / chrome-only |
| 10 | Riot Patch 26.1 notes | cited 2026-11-10 in #9 | First-party designer/patch | **Not re-fetched**; local study says full page then | Herald as siege conversion; contest risk | Current live values unknown here |
| 11 | Hi-Rez SMITE 2 Alpha Weekend 1 | smite2.com, cited in #9 | First-party | **Not re-fetched**; local study search excerpts | Historical Gold Fury rewards | Not classic SMITE, not current |
| 12 | Hi-Rez SMITE 2 audio deep dive, YouTube `5LAS6vnyZk0` | 2026-11-04 local read | First-party talk | Local synthesis doc, transcript-was-full | Press / information / visceral sounds; SMITE 1 32-voice cap | Video not watched this run |
| 13 | `docs/reference/smite-study-2026-11-08.md` | 2026-11-08 | Local inspection of owned SMITE install | Full | Animation-set coverage; Hun Batz/Raijin are not gorilla donors | Private extracts; no kit copy |
| 14 | `docs/reference/smite-camera-framing-2026-11-09.md` | 2026-11-09/10 | Local measurement + player excerpt | Full | SMITE 1 god ~11% screen, aim ground ahead; r/Smite 2015 wanted camera height | FOV of SMITE 1 still unknown |
| 15 | `docs/plan/moba-camera-combat-reference-direction-2026-11-08.md` | 2026-11-08 | Direct user direction | Full | SMITE primary, Paragon secondary | Not a shipped-game spec |
| 16 | `docs/reference/moba-look-study-2026-11-09.md` | 2026-11-09 | Local look study | Opening + tables | SMITE 2 vs Predecessor frame stats; silhouette over ink | Paragon lighting talk 429, not read |
| 17 | `docs/reference/tartarus-arena-review-2026-11-08.md` | 2026-11-08 | Community/AI prototype | Full | Hit-resolve / hitstop / QA labs | **Not** official Paragon; AI-built |
| 18 | MATCH_NOTES plaza stalemate / push demo | 2026-11-04 | Local play observation | First 150 lines | Six-machine 130 s stall; tower push needed held bots | One session, not a playtest panel |
| 19 | Preston directions in brief + kits + camera docs | 2026-11-04…10 | Firsthand player of *this* game | Quoted in those files | Portals yes, portal-only no; keep gorilla; reticle aim; skinny miss | One player, the director |

**Not used:** leaked/proprietary repos, live `D:/dev/new-mech-rpg` checkout, raw chat stores, paid generators, MCP, whole GitHub repos (Tartarus was already excerpted locally).

**Training-knowledge gap:** official Janus/Geb/Cabrakan ability pages, Predecessor patch notes, League current jungle timers, and additional player posts were **not retrieved**. Treat any memory of those kits as unverified. The fennec proposals were written to avoid duplicating Janus’s public shape (portal / vortex / threshold / big teleport) rather than by quoting those pages.

---

# Coverage limitations

- Write tools were unavailable; this text is the deliverable.
- Game was not launched. Feel claims are hypotheses.
- Automated checks were not re-run; cited from ARENA_REFRESH.
- 23 proxy meshes were not visually inspected here.
- External web was unavailable; first-party pages rely on staged studies.
- Desire / “irresistible” is unproven until Preston and others play the four-beast slice.

**Concrete next step for Preston:** play gorilla vs a skinny pole and a rhino for ten minutes, then pick Fennec A or B. That is the only decision that unblocks the rest.
