# Fennec kit rework: ode to Janus (draft, 2026-11-04)

**Status, 2026-11-04:** Preston took this kit ("Take it"). It is written into `docs/plan/moba-kits.md` (the fennec section, the kit rule, the role map and the roster checks). Copied from the hub's worktree; the rest below is the draft as the hub wrote it.

**Nothing here is canon.** Names, numbers and the final kit are Preston's. The labels are plain descriptions, and
cooldowns are tiers, as in `docs/plan/moba-kits.md`.

This draft sits in the hub's copy of the project. The hub can't edit the main folder. Once Preston picks, a lane
working in `D:\dev\new-mech-rpg` writes it into `moba-kits.md` in place of the current fennec section.

## Why (Preston, 2026-11-04)
"were making the kit and their abilities too much like a bare parts animal like mecha beast would. For example it
digs and has sand attacks. which are fine but in my mind with it being an ode to janus I wanted it to have blinking
teleport abilites or portals. Same for the others it seems like all their attacks are more physical and dependent
on their animal."

## Proposed update to the kit rule (his to accept or edit)
The rule from 2026-11-03 says to take what makes sense for the animal. Proposed addition:
- **The animal gives the body, the silhouette and at most one trait.** That trait is usually the passive or one
  slot.
- **The rest of the kit comes from a power theme:** the god's domain, an element (heat, lightning, light), or a
  machine system (shields, portals, holograms).
- **Still true:** nothing is held in hand. Every power comes from the machine's own body: emitters, vents, cores.
- **The model already in the roster:** the gorilla's green hex shields are tech, not ape. The other machines
  should feel like that.

## What was used (general knowledge, nothing read this session)
- **Zoids (the main reference):** animal frames that carry mounted tech: cannons, blades, shields, energy weapons.
  The animal is the chassis; the powers are the machine's.
- **Blink-then-return skills in MOBAs** (a dash with a short window to recast and snap back to the start). The
  structure taken: a short window, a visible marker at the start point, and the return as the skill's real power.
- **Rewind skills** (return to where you stood a moment ago). The structure taken: escape that punishes divers.
- **Placed teleport pairs** (an entrance and an exit that a team can walk through). The structure taken: the
  current fennec tunnel already works like this, so only its look changes.
- **Janus himself:** the god of doorways, beginnings and endings, with two faces looking forward and back. In Rome,
  the doors of his temple stood open in war and shut in peace.

No names, numbers or art from any of these.

## Proposed kit

| Slot | What it does | Cooldown | Replaces |
|---|---|---|---|
| Passive, big ears (the one animal trait) | Unchanged: enemies moving near it show up as sound pings, even in fog or camouflage. Kept because the roster needs it as a camouflage counter. | none | stays |
| 1, two-faced shot | Fires a bolt forward and, from a small gate that opens behind it, a second bolt backward. Damage and a slow on both. Looks both ways, like Janus. | short | sand kick |
| 2, blink gate | Blinks a short distance and leaves a glowing gate where it started. Recast within a short window to snap back through the gate. The headline ask. | short-medium | ear burst |
| 3, twin gates | An entrance gate here and an exit gate far away. It and its allies can step through for a few seconds. Same job as the tunnel, gates instead of digging. | long | tunnel |
| 4, doors of war | After a short charge, a ring of doors rises around an area. While open, allies inside move faster. When it slams shut, enemies inside are knocked back out and silenced briefly. | long | sonic boom |

**How it plays:** pings show the enemy coming. Two-faced shot pokes and covers its back. Blink gate goes in for a
hit and snaps back out. Twin gates bring the team in for a flank or out of trouble. Doors of war opens a fight and
then shuts it in the enemy's face.

**Roster checks:**
- The pull still belongs to the lobster. Nothing here drags an enemy anywhere.
- The big knockback the roster counts on stays, now on the doors closing.
- **New control: silence.** Nobody else has it, so it's free to take.
- The two-diggers overlap with the pangolin goes away.

## Alternatives (pick any instead)
- **Passive, two faces:** a rear sensor gives the fennec vision behind it. This costs the roster its sound-ping
  camouflage counter, unless the squirrel and wolf are judged enough.
- **Slot 2 as a rewind instead of blink gate:** it returns to where it stood a moment ago and heals a little.
  Simpler, but it can't be used to go in.
- **Ult as a swap gate:** it trades places with an ally (a rescue). Less control, more support.
- **Keep sand kick as slot 1** if he wants one desert touch left.

## What changes for the art
- The old list was sand kick, ear burst, dig and pop out, and sonic boom. Most of those are body animations.
- The new kit leans on **effects:** gates, bolts, a ring of doors and a blink flash. On the body it needs one cast
  pose (ears up, emitters lit), with a short charge for the ult.
- Effects can be made with the free PixelLab pixel tools. Fewer Codex body frames should make it cheaper. That's a
  guess until the animation lane prices it.
- Some fennec moves were already animated at the old angle (Codex was spent on fennec frames). Those may be
  dropped. Not checked which.
- No attack moves at 35 degrees get drawn for any machine until the kits are redone (the hub told the animation
  lane, 2026-11-04).

## Ideas for other machines (proposals, one line each)
- **Rhino / Cabrakan (earthquakes and mountains):** molten core. Ground pound leaves lava cracks that burn; the
  stampede leaves a trail of fire. This is the heat-and-lava machine Preston mentioned.
- **Hippo:** boiler body that vents steam (a second heat option if the rhino stays earth).
- **Shoebill / Thoth (the moon, knowledge):** moonlight beam, line strike as a light lance.
- **Chameleon / Loki (tricks):** hologram decoys from its colour plates (the decoys the old kit left out).
- **Wolf / Thanatos (death):** phase step through enemies, a dark mark on the hunted target.

## First slice, if he picks this kit
**Blink gate only**, in the game feel lane's kit code, using the fennec's existing sprites (no new art):
- Blink moves the fennec its range toward the aim point and never into a wall.
- A gate marker stays at the start point for the window.
- Recast inside the window returns the fennec to the start, within 0.1 m.
- After the window, the gate is gone and recast does nothing.

**Headless check:** a `tools/debug/` script that blinks, measures the distance moved, recasts, measures the return,
then waits out the window and checks the gate is gone.
