# Creature and mech animation research, 2026-11-09

Preston requested continued GitHub, Firecrawl and web research so Codex and Claude can independently recognize, plan and evaluate the intended motions. Scope: animal behavior, professional animation craft, retarget/contact tools and responsive game playback. Public GitHub APIs, four focused Firecrawl searches, targeted Firecrawl page retrieval and web searches were used. No repository was cloned, add-on installed, asset downloaded, generation started or gameplay changed. This is a research/source-inspection pass, not validation of a new animation or installed tool.

Read this with [ACTION_CARDS.md](ACTION_CARDS.md), the [lane exchange](../../team/ANIMATION_LANE_EXCHANGE_2026-11-08.md) and [TartarusArena review](../tartarus-arena-review-2026-11-08.md). Current user corrections in the mech's own chat always take precedence over dated snapshots.

## Findings we can use now

### 1. Establish the actual action before solving bone motion

Researchers at Max Planck describe gorilla chest beating as an upright, rapid display made with cupped hands. Treat that as a specific behavior, not as a synonym for a punch, arm wave, overhead slam or continuous rocking. Our fixed mechanical hands and large shields need an intentional adaptation, documented before keyframing. The scientific source establishes posture/hand use, not one mandatory cadence or our game timing. Individual displays vary. [Max Planck research account](https://www.mpg.de/16678047/gorillas-don-t-bluff-when-they-chest-beat-honest-signalling-indicates-body-size)

The source links a published study and behavior images. The Nature paper itself did not yield usable text in this pass. No linked video was frame-analyzed, so do not invent reference timestamps, contact counts, beat rates or measured limb arcs. The next clip task must inspect relevant footage/poses and record what was actually observed.

A 2025 gorilla biomechanics paper provides force/contact diagrams and supplementary material. Its experiment used three zoo gorillas walking on a narrow elevated beam. It supports studying hand/foot support and fore/hind differences, but is not a universal ground-walk footfall prescription or a target for our mech's game speed. [Primary paper and methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC12575676/)

### 2. Use a creature animator's workflow, adapted to rigid armor

Professional creature-animation guidance starts with animal reference, scale, primary masses, support and spacing. The practical implication here is to block the hips/chest/head rhythm and contact sequence before filling the timeline with smooth curves. A generic periodic bob applied to every beast will erase the animal's movement identity. [Creature locomotion recipe](https://www.animationmentor.com/blog/5-tips-to-make-the-perfect-creature-animation-locomotion-recipe/)

A detailed quadruped tutorial demonstrates pose-by-pose blocking, foot placement, overlap between lift and landing, and graph-editor loop cleanup. It uses a dog rig: its method transfers; its anatomical poses and timings are not automatically correct for a gorilla or rhino. [Animals in motion tutorial](https://www.animationmentor.com/blog/tutorial-animate-animals-in-motion/)

For contact actions, an animator's push/pull breakdown uses FK for free approach arcs, IK at planted contact, thumbnails before posing, and deliberate breakdowns before splining. For us, this means clear weight preparation, a contact target, controlled release and recovery rather than hoping interpolation will create force. [Force and contact tutorial](https://www.animationmentor.com/blog/tutorial-animating-pushing-and-pulling-motions/)

Additional production guidance explains how anatomical rig limits constrain believable performances, including when multiple reference animals are deliberately combined. Preserve rigid plate length and approved anatomy; express compression with joints, suspension, pose and timing instead of rubber armor. This mech-specific restriction is our application of that guidance. [Creature animator tips](https://www.animationmentor.com/blog/6-animation-tips-every-creature-animator-should-know/)

### 3. Preserve action readability as speed changes

Riot's Bel'Veth animators describe distinct attacks for different attack-speed regimes, including a change from lower-speed slashes to faster stabs. The useful principle is to test the action's readable path at the requested rate and author appropriate variants when needed. It does not justify changing our kits or copying the champion's motion. [Riot animator account](https://www.leagueoflegends.com/en-us/news/dev/why-bel-veth-slaps/)

Riot's clarity guidance makes recognizable silhouette, readable facing and importance hierarchy central. Effects must communicate the action; adding more flash cannot establish that the underlying strike reads correctly. Our test therefore includes a clean body-only pass and the actual game camera. [Clarity in League](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/)

### 4. Separate desired movement, visible motion and ground contacts

Daniel Holden's controller discussion distinguishes the simulated character from the animated body and examines how their displacement is reconciled. Its contact section locks a planted point, solves the limb with IK and releases the lock when the pose becomes excessively separated. This offers a concrete alternative to either uncontrolled skating or stretching a limb indefinitely to keep a contact. [Controller displacement and foot locking](https://www.theorangeduck.com/page/code-vs-data-driven-displacement)

His inertialization explanation retains pose/velocity offsets at a transition and decays them into the next animation. Useful for abrupt starts, stops and direction changes after the base motion works. Spring-based blending can overshoot, so it must not pull a mechanical joint through armor or smooth away a necessary hit. This is a technique to evaluate, not a claim that we implemented it. [Inertialization](https://www.theorangeduck.com/page/spring-roll-call#inertialization)

Godot's own AnimationTree provides blend spaces, state machines, one-shots and filtering. Use those native facilities as the baseline. Godot's retargeting documentation also explains why identical bone names do not imply compatible rest transforms, and supports profiles beyond its humanoid preset. A rhino should not be forced into a humanoid map merely because automatic matching is convenient. [AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html), [retargeting skeletons](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html)

## Repository shortlist and actual inspection level

These are candidates or study sources. None was installed or tested against our Blender 5.2/Godot 4.7.2 rigs.

| Repository | What was inspected | Value and limits | Priority |
|---|---|---|---|
| [Mwni/blender-animation-retargeting](https://github.com/Mwni/blender-animation-retargeting) | README, extension manifest and `ik.py`; GitHub metadata | v2.4.0 manifest declares Blender >=4.4 and GPL-3.0-or-later. Explicit rest-pose alignment, hand/foot position correction and mapped-bone baking. Code has four named correction slots: left/right hands and feet. Plausible fit for gorilla support mapping; rhino assignment needs deliberate anatomical mapping. Source targets are not a measured world-contact solver. No Blender 5.2 compatibility claim from this review. | Best new retarget pilot candidate. |
| [nkeeline/Keemap-Blender-Rig-ReTargeting-Addon](https://github.com/nkeeline/Keemap-Blender-Rig-ReTargeting-Addon) | README and repository metadata | Saved per-bone mappings/offsets, parent-first evaluation and source-FK to target-IK controls. README only reports Blender 3.3.1 testing; last reported push 2023. GPL-3.0 per GitHub metadata. Broad any-rig wording is not verified rhino support. | Study mapping/control ideas; older compatibility baseline. |
| [orangeduck/Motion-Matching](https://github.com/orangeduck/Motion-Matching) | README and contact/inertialization-related source in `controller.cpp`, plus author articles | Useful inspectable controller, blending and contact methods. MIT code; README gives a different, noncommercial/no-derivatives license for the referenced training dataset. It is a raylib/C++ demo, not a Blender plugin or ready-made creature clip library. No dataset or trained asset was imported. | High-value technical reference. |
| [GuilhermeGSousa/godot-motion-matching](https://github.com/GuilhermeGSousa/godot-motion-matching) | README and repository metadata | Godot 4.4 extension, AnimationTree integration; requires animation root motion and a root bone at foot level. GitHub metadata reports MIT. Needs a pose library with useful motion coverage; current Godot 4.7.2 compatibility is untested. | Later, once enough good mech clips exist. |
| [BobbyAnguelov/Esoterica](https://github.com/BobbyAnguelov/Esoterica) | README and repository metadata | Authors present substantial animation tooling and linked presentations, but explicitly call the engine a prototype for technical teams. README says MIT; GitHub license detection returned NOASSERTION and a guessed `LICENSE` path did not resolve, so inspect the actual license files before any code reuse. No animation subsystem source was audited here. | Architecture/talk reference, not an engine migration. |
| [Rokoko/rokoko-studio-live-blender](https://github.com/Rokoko/rokoko-studio-live-blender) | Official README | Bone remapping and rest-pose setup are relevant. Live capture introduces Studio/setup requirements and human capture does not establish gorilla/rhino behavior. README's broad Blender version claim is not our local compatibility proof. | Secondary option for suitable human upper-body reference. |
| [abrykajlo/MotionMatchingGodot](https://github.com/abrykajlo/MotionMatchingGodot) | README | Course project targeting Godot 4.5 with native build setup. Less immediate leverage than the more integrated candidate above. | Background reference only. |

## Existing tools already available

Our local `atlas-animation` skill already covers blocking, timing and layers; the `animation-quality-gate` skill already requires contact sheets and failure analysis. The current failures are not evidence that we lack a principles list. We need action-specific observations and failure tests before acceptance. Generic silhouette stability in an old quality gate must be interpreted as identity/proportion stability: a moving character's outline necessarily changes.

Use existing Blender for control rigs, rigid armor ownership, IK/FK and curve editing; FFmpeg for trustworthy full-speed and slow-motion evidence; Godot for actual movement/turn/attack/recovery tests. Existing accepted originals, canonical sheets and lane revisions are the fixtures. New tools must earn adoption on isolated copies.

## Recommended order

1. Apply the action cards to one chest-beat blockout and one existing punch: establish reference posture, support, force direction and contact target before polishing curves. Do not restart an accepted clip indiscriminately.
2. Fix gait/controller reconciliation and validate actual surface contacts through travel, turns and speed buffs. Report units and limitations; do not treat joint-position zeros as visible surface proof.
3. If retargeting remains a bottleneck, test Mwni's current extension on an isolated donor/target pair. Compare it to the current method with identical source clip, scale and cameras. Installation is not part of this research pass.
4. Evaluate motion matching only when there are enough good starts, stops, turns and directional motions to search. It cannot select a convincing action from a database that lacks one.

## Coverage and unresolved points

Primary sources were preferred: researchers' behavior accounts/papers, working animators' tutorials, Riot's shipped-game developer notes, tool authors and engine documentation. Search-result snippets alone were not treated as proof of a usable tool. Generic AI motion claims, paid course listings and unrelated Firecrawl provider suggestions were excluded.

Nature text retrieval failed; Max Planck's research account was readable. The old Riot ArtEdu URL returned 404; the two actual Riot developer articles above were read instead. A source video's existence is not frame inspection, and no newly discovered add-on has passed local validation. Firecrawl usage is recorded where returned by the service; no total credit cost is asserted from missing receipts. Search feedback was submitted for the four focused searches.

This guide should reduce avoidable basic-action mistakes. It cannot certify professional visual quality without inspecting the rendered movement. Preston still directs the artistic intent and approves the feel; researching ordinary motion and checking our own output are the agents' responsibility.
