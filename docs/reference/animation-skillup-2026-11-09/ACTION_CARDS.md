# Action-specific planning and review cards

Apply before another expensive polish pass. Source findings and inspection limits are in [REPORT.md](REPORT.md). The staged requirements below are project-specific proposals and review methods, not claimed measurements of real animal footage or new kit/balance decisions.

## A. Every animation starts with an action definition

Record the intended verb, target and context: e.g. chest display, fist strike into a target, heavy knuckle walk, braced horn toss. List what would make the action read as something else. Study a relevant real-animal source and the appropriate shipped-game treatment; label what each contributes. Do not substitute an unrelated donor because it has a clip called Attack.

For each selected reference, record URL/local path, species/character, observed pose sequence, support/contact events and timing. Only add timestamps after actually watching those moments. Separate observed facts, planned exaggeration and mechanical compromises. Real behavior and a fantasy combat design can differ; make that choice deliberately.

Use the existing canonical model/sheets and accepted rest proportions. Keep source donor, rig revision, curve revision, geometry revision, review cameras and export hashes identifiable.

## B. Gorilla chest beat

**Behavior anchor:** Max Planck describes a usually upright, rapid chest-beating display using cupped hands. This establishes the action's basic identity, not a fixed animation duration or mandatory universal strike sequence. [Source](https://www.mpg.de/16678047/gorillas-don-t-bluff-when-they-chest-beat-honest-signalling-indicates-body-size)

**Proposed mech phase plan:**

1. Prepare support and raise the body deliberately from the low posture. Inspect the weight shift as hands leave the ground; do not simply rotate the spine upright while the pelvis/feet remain in an impossible pose.
2. Present the chest and form a compact striking path. Check the shield geometry and available wrist/hand articulation. If the hands are rigid knuckle forms, document the adapted striking surface; do not pretend they became biological cupped palms or silently redesign the fists.
3. Show repeated, distinct approaches to the chest with readable contact and release. Choose the left/right pattern from viewed reference or label it as authored. Evaluate each striking surface relative to the moving chest, not only the world-space hand joint.
4. Let the body respond locally and settle back into a supported ready stance. Preserve a clear return to locomotion. The gameplay effect belongs to the existing kit; this card does not change its radius, stun, damage or timing values.

**Reject when:** hands wave beside the shoulders without approaching the chest; motion is merely a torso bob; an overhead slam is labelled chest beating; the hands/shields pass through the face or chest; unsupported feet slide while rising; all beats smear into one circular arm swing. Audio and rings may accompany a successful action but cannot establish the body action by themselves.

## C. Gorilla basic punch

**Intent:** a deliberate combat strike, adapted to the approved mech. A natural gorilla display is not evidence that a boxing-like attack is biologically authentic. Pick an appropriate combat reference separately.

**Proposed phase plan:** loaded preparation; coordinated body/shoulder drive; fist-led approach to the chosen target; contact; short recoil; recovery into a pose that can resume movement. Choose which supports must stay planted and when they can release. Use IK for meaningful support and FK/curves where an expressive free arc is intended.

**Measure:** path and velocity of the actual striking surface toward the target; closest approach and contact interval; elbow/shoulder configuration; body motion relative to fist; recoil direction; visible support-patch drift; armor clearances; recovery and interruption behavior. A fist that is already retreating at the nominal contact time requires diagnosis. An intentional hook can have a curved path, so a universal straight-line rule would be wrong.

**Reject when:** arm pendulums through the target with no loaded preparation or transmitted force; the torso stays inert while only the forearm swings; shield-clearance fixes turn the strike into a wide wave; effects hide a miss; every pose is clear but full-speed motion reads poorly. The rejected v15 chain is the local example of why a numerical clearance pass is insufficient.

## D. Heavy knuckle walk and rhino gait

Identify the gait and species first. Record each limb's contact/lift phase from the actual chosen reference rather than assuming any quadruped sequence will work. A narrow-beam gorilla biomechanics experiment informs support research but cannot dictate a ground-run cycle. Rhino walk and charge need their own motion identities.

**Block:** travel and primary masses; support contacts; lift/placement; body counter-motion; then controlled secondary motion. A rigid mech should carry weight through coherent joints and actuators while armor panels retain their intended shape.

**Check during actual root/controller movement:** stance-patch position relative to the support surface, touchdown/liftoff continuity, sole/knuckle penetration, limb reach, chest/pelvis/head movement, speed-to-stride relationship, loop pose AND velocity continuity, sharp turns and stop/start transitions. Distinguish an intentional rolling contact from an incorrectly frozen ankle pivot.

Test normal travel and the currently authorized speed-buff/charge previews. Report cadence, stride, travel speed and normalized cycle phase separately. Do not fix faster travel solely by accelerating every animation forever. An authored faster-gait variant may preserve weight and contact better. Do not change shared game balance to hide an animation limitation.

If a support cannot remain planted without exceeding reach, revise pose/contact timing or release it deliberately. Preserve rigid lengths and approved mass instead of stretching armor or changing the pelvis silhouette. Donor bone names, gait constants and support poses are not portable across species without adaptation.

## E. Animation-to-combat contract

Document acceptance, commitment, contact/effect and recovery events. Confirm the visible impact, damage, sound and VFX refer to the same intended moment after time-scaling. Define movement/ability cancellation boundaries and action priorities. Test misses, stun, death and return to locomotion. Keep root movement, game collision and render-only effects distinct.

Begin with native Godot AnimationTree/state transitions and existing kit hooks. Consider inertialization for position/velocity continuity where needed, while protecting contact and joint limits. No blend technique repairs unclear source motion.

## F. Required evidence before saying it works

1. Reference notes and six-or-fewer representative key poses showing the intended action. State any unobserved details or authored adaptations.
2. A plain body-only playback at full speed, then a slower diagnostic playback. Contact sheets supplement motion; they do not replace it.
3. Front/side and the real game camera at intended screen size. A close-up alone cannot prove gameplay readability.
4. Measurements against the exported GLB and actual visible contact surfaces, including scale, rigid lengths and preservation of approved anatomy/materials. Label partial checks precisely.
5. A neutral description of what the motion visibly does before repeating its intended label. If the description is arm waving while the intended action is chest beating, revise it. This is an agent self-check, not an independently validated action recognizer.
6. Separate technical and artistic verdicts. Record unresolved faults. Keep a rejected version's technical passes as evidence, never as permission to call it approved.

When an animation is rejected, identify the failed pose, path, timing, support or action read before another rebuild. Preserve the latest accepted version and keep changes isolated. Never fill the missing evidence with assumptions that Preston must later correct.
