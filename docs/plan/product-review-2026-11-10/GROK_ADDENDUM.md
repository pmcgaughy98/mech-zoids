# Grok evidence and design follow-up

2026-11-10. Follow-up to GROK_REVIEW.md. Where these recommendations differ, this later pass takes precedence as Grok's proposal. Source access limits remain explicit.

I’ll read the supplied source leads and the captured fennec sections, then write a focused addendum from that evidence.# FINAL ADDENDUM

**Date:** 2026-11-10. Critique of the captured review, using Codex-supplied source checks in `SOURCE_LEADS.md`. I did not browse those URLs. Distinctions: **supplied evidence** (Codex retrieval or excerpt) versus **my interpretation**. Kit text below is an authored proposal. It is not user approval.

## 1. What the supplied accounts do to the recommendation

**Riot Scruffy, Champion Counterplay, 2021-05-14, full text retrieved by Codex:**  
https://www.leagueoflegends.com/en-us/news/dev/quick-gameplay-thoughts-may-14/  
Strategic weakness on a spreadsheet is a different test from a decision an enemy can take *during* the fight. Interpretation: gorilla Drive, rhino stampede, and any fennec door need a visible tell and a bodily answer (side-step, body-block, interrupt). A “squishy mage” line in a table is not enough.

**Riot, Clarity in League, full text retrieved by Codex:**  
https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/  
Silhouette, facing, hitbox/effect alignment, and a hierarchy of visual importance. Interpretation: this strengthens the center-line melee contract and a ground mark on the reticle. It also argues against putting ultimate-scale VFX on every basic, which the gorilla already mostly respects.

**Riot, Champion Insights: Sett, search excerpt:**  
https://www.leagueoflegends.com/en-ph/news/dev/champion-insights-sett/  
Designer account of clarity, player frustration, and animation cost when grappling other champions. Interpretation: keep the existing Grab Slam as the roster’s one carry/slam. Do not spread tosses onto unready rigs (lobster pull waits on a GLB; fennec gets none).

**Steve Superville, Paragon creative director, Q&A, 2016-08-16, full interview retrieved by Codex:**  
https://digitalchumps.com/2016/08/16/qanda-with-paragon-creative-director-steve-superville/  
Plus a Ten Ton Hammer excerpt: https://www.tentonhammer.com/articles/paragon-an-interview-with-creative-director-steve-superville  
Third-person targeting as action *and* MOBA strategy; kit-first heroes; the camera exists so space is tactile. Historical intent, not proof Paragon succeeded. Interpretation: keep compact 3v3 third-person. A portal the team *walks into* fits that camera. A recast blink is a hotkey; a doorway in the world is a place.

**Firsthand player excerpts (qualitative, version-specific, not consensus):**  
- Janus portal firing-time change broke a practiced escape: https://www.reddit.com/r/Smite/comments/1vo0qmf/janus_abilities_firing_time_change_ob41/  
- Thread disagreement: mobility-plus-damage as the frustration; also portal-placement bugs. Full page failed. https://www.reddit.com/r/Smite/comments/189cqh7/  
- Predecessor player asking how items work; replies on auto-buy/counterbuilding: https://www.reddit.com/r/PredecessorGame/comments/148jd7o/  
- Players enjoying match length while still reaching late builds: https://www.reddit.com/r/PredecessorGame/comments/1cf12u0/  

Interpretation: personal blink windows are brittle; mobility stacked with burst is the pattern to refuse on fennec; a huge unexplained shop is a bad first economy; a *small* set of buys can still exist in a short match.

**Limits of this pass:** Codex marked some pages full text and some search excerpts. I did not independently retrieve them. Reddit is anecdote. Sett and Superville are designer intent, not our playtests. Riot 2026 season preview (excerpt, https://www.leagueoflegends.com/en-us/news/dev/dev-2026-season-one-gameplay-preview/) only supports making camps/objectives visibly worth walking to.

**What stays:** 3v3 Foundry, SMITE-feel camera, gorilla foundations, four-beast first roster, readable hit contact.  
**What changes:** fennec favorite (section 3); “no shop” becomes a tiny Foundry board so the gold boss spends (section 2).

## 2. Gold boss and a small economy

Preston already assigned a gold objective and a power objective. Deleting the gold boss to avoid a shop fights that direction. A full item mall still does not belong in the first playable: there is no store code, and the Predecessor excerpt shows players asking how items work.

**Proposal (authored, numbers draft):** a **Foundry board** of four always-visible team upgrades, one purchase at a time per player, shared UI at base and after recall.

| Buy | Job | Draft cost |
|---|---|---|
| Wave mill | Next two allied waves +15% HP/damage | cheap |
| Plate charge | Personal 120 HP shell, 45 s or until broken | medium |
| Crane repair | Allied tower regenerates a chunk over 8 s | medium |
| Overclock | +12% damage and 10% move for 25 s, lost on death | expensive |

Camps drop a little gold. The **amber stag beetle** (still an unapproved animal identity) pays **all three teammates** a lump equal to about one medium buy, including dead or elsewhere. That is a payout, not an income multiplier. The crimson elephant stays a later personal power window, lost on death, with no gold.

Pits still fatten waves. Beacon still opens a tower. The mill is a smaller, bought cousin of a pit, so taking both is greed you can see. Optional “recommended” highlight on the cheapest missing buy covers the Predecessor onboarding complaint without auto-playing the match.

**First playable:** board with two buys (mill and plate) plus camp gold plus the beetle. Power boss off until beacon-plus-pits is measured. This is a proposal for Preston, not an implemented system.

## 3. Fennec: Kit A failed its own rule

Captured Kit A still stacked **pocket recast teleport**, **team-carry ult teleport**, a **7 m knockback boom**, and an **arrival knockback**. That is two body-warps and two shoves. Preston liked **portals for it and the team**. He did not approve sonic boom as a 3D kit pillar; the old cone is leftover sprite combat. Calling boom “the liked move” over-weighted an older slice.

The supplied Janus excerpts point at the same failure mode: escape-input windows, and frustration when mobility arrives with damage. Scruffy’s in-combat test: the enemy needs a thing to *do*. A recast blink plus a team ult drop plus knockback leaves “don’t get hit by the untargetable fox.”

**Replacement favorite (authored proposal): Seamwright.**  
Chassis is the existing fennec model. Power theme is factory rift hardware: hoops, latches, seams. Ears stay silhouette. One team-portal slot. No recast blink. No second teleport. No knockback. Combat verbs stay useful while the doors are down.

| Slot | Working name | What it does (draft) |
|---|---|---|
| Passive | **Cooling seam** | For 2 s after doors close, a faint hoop remains. Darts that pass through it deal a small extra tick and apply rift echo (reveal 2 s). |
| Basic | **Emitter dart** | Current 6 m violet dart, 0.9 s, 30 dmg. Aims at the reticle. |
| 1 | **Split latch** | Slow bolt; sticks to first enemy or terrain; 0.7 s later a 1.8 m disk, 50 dmg, 30% slow 1.2 s. If fired into a live mouth, it exits the other mouth. Short cooldown. |
| 2 | **Twin doors** | **The portal.** Entrance at feet, exit up to 8 m in vision (ally or allied tower legal). Both live 4 s. Allies and the fennec **walk** through (about 0.25 s move). No recast hop. Cooldown starts on place, medium-long (~14 s). Enemies cannot traverse; they can occupy a mouth and body-block. |
| 3 | **Seam shear** | 5 m × 0.8 m energy line, 40 dmg. If it crosses a live door, a second line fires from the far mouth along that mouth’s facing. Without doors it is ordinary poke. |
| 4 | **Mouth slam** | 0.4 s interruptible plant. If twin doors are up, both mouths erupt: 70 dmg and 0.8 s root. If doors are down, a 1.5 s hoop appears at the fennec’s feet and erupts once. Long cooldown. |

**Moment-to-moment, doors up:** plant a corridor, latch through the far mouth, shear the exit facing, slam both mouths if they stand in them.  
**Doors down (the important part):** dart, latch, shear, selfish slam-hoop. A complete small mage. The signature is missing, so the player is hunting the 14 s window rather than chaining warps.

**Limits:** walk-through is commit; a wall or body-block eats the corridor; latch can be walked out of; ult channel dies to stun/Drive/grab; no displacement.

**Enemy responses (Scruffy test):** stand in a mouth; attack the fennec during the place; sidestep the delayed disk; interrupt slam; dive when 2 is dark and ignore the hoop leftover. Portal-placement bugs in the Janus thread become a test: mouths snap to nav, stay visible, and never fire from an unseen origin.

**Novice:** doors backward as a hallway home. Latch is a bomb with a warning.  
**Expert:** exit facing behind a target so shear is a reverse shot; slam only when someone camps a mouth; cooling-seam darts after the doors die.

**Anim/VFX:** reuse SmallGate hoops, bolt, arrival-shield language as a latch blob. New: line shear, mouth erupt, 2 s leftover seam. No sonic-boom redraw in the first slice. Cast pose only.

Kit B (corridor mage with far gates plus great gate) remains the alternative if Preston insists the portal must be an ult taxi. That still needs the recast blink removed.

## 4. Gorilla, models, decisions, first slice

Preserve: gorilla model/rig/sources, hex shield, Grab Slam, Shield Drive with hand energy, chest-beat cage, swat-swat-slam character, silverback aura, every catalog GLB. Sett’s excerpt is extra reason to leave Grab Slam as the one throw.

**Decision sequence for Preston (one at a time):**  
1. Gorilla ult: lock live taunt-plus-cage-plus-modest ward, or restore beat-2 mass shields.  
2. Fennec: take Seamwright, or demand an ult-only team taxi (Kit B stripped of recast).  
3. Tiny board: mill + plate as the gold sink, or delay the beetle until that UI exists.  
4. Assist-aim: keep for the first playtest, competitive off-toggle later.  
5. Codex heavy-basic: art yes/no, independent of damage.

**First playable slice (unchanged in spirit, tighter in order):**  
Human ten minutes of gorilla versus a thin pole and a rhino, center-line capsule and reticle mark, existing clips and timings. Pass is Preston’s eye on the liked animation plus a center hit.  
Then one fennec beat: Twin doors walk-through (allies included) plus Split latch, sand/tunnel keys dark. Prove the portal is fun for a teammate and that latch plays while doors are down.  
Then four-beast bots, bosses off, two-buy board optional. Gold beetle after a buy exists.

## 5. Source classes

This run inspected a **scoped snapshot**: kit scripts, `roster.json`, match rules, staged docs. It did not audit official SMITE or Paragon codebases.

| Class | Example | What it is |
|---|---|---|
| First-party public writing | Riot counterplay/clarity/Sett pages; Superville interviews; Hi-Rez API PDF https://webcdn.hirezstudios.com/hirez-studios/legal/smite-api-developer-guide.pdf | Designer intent and legal API docs. The SMITE API needs credentials we must not open. |
| Official public data feeds | Riot Data Dragon https://developer.riotgames.com/docs/lol | Versioned descriptions, often lagging live. Not gameplay source. |
| Community convenience | CommunityDragon https://communitydragon.org/docs/assets | Derived from Riot files, not identical to first-party source. No assets imported. |
| Owned-client craft study | Local SMITE package inspection already in the snapshot | Animation coverage for our gorilla. Not a kit or asset dump. |
| AI / community prototype | TartarusArena https://github.com/BartekZawadzki/TartarusArena | Engineering case study. Not Epic Paragon, not a shipped-human authority. Epic’s Paragon bot PDFs (GameAIPro3 ch. 24 and 32) are architecture leads; Codex read excerpts only. |
| Firsthand play | Preston on this prototype; Reddit excerpts above | Specific friction. Not balance consensus. |

Authored proposals in this addendum: Seamwright, Foundry board, center-line capsule, ult lock recommendation. User-approved so far: gorilla foundations, existing models, portals as a fennec signature, gold and power *roles*, compact 3v3 as the current map. Take/leave is still his.
