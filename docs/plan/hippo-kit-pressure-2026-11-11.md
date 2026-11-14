# Hippo kit: pressure, its own ode to Bacchus (proposal, 2026-11-11)

Hippo effects lane, from Preston's calls in conversation. Names and numbers are proposals for Preston to edit. The game
feel lane owns the kit code; nothing here is built in the kit yet.

## Preston's calls
- Theme: **pressure**, the tanks as the meter, "filling up the wine flask" as the Bacchus ode (hippo-pressure-kit note).
- Vent: "Make it the purple liquid I want it to have a poisonous or toxic type effect. Or noxious."
- The combo he values in Bacchus: dive with the belly flop, the burp starts mid-air and stuns about half a second
  later, then the ult for huge damage and the Intoxicate ground: "a great initiator but all in'er".
- The ode must be its own: "Hippo obviously should be its own like how kuzenbo seems like an ode to Rasmus but the
  spike roll is kuzenbos ult". So the ingredients are kept and moved to new slots and forms.
- Lockjaw: flinging an enemy away would break the combo. He picked "Drag them into the lake".

## The kit
| Slot | Name | What it does | Bacchus ingredient it reshapes |
|---|---|---|---|
| Passive | Pressure Tanks | Fills as it deals and takes damage; the tank windows glow brighter. Full tanks overcharge the next skill, then drain. | The drunk meter |
| 1 | Vent | A toxic purple spray cone from the jaws (0.6 s window, one hit, or ticks). Leaves a puddle. Overcharged: the puddle lasts longer and slows. | The cone, with the stun moved out of it |
| 2 | Piston Drop | Leaps to a spot and lands. The landing pumps pressure into the floor; about 0.5 s later the ground under the impact erupts and stuns. | The delayed stun, moved from the cone to the dive |
| 3 | Lockjaw | Clamps one enemy. The hippo can walk for about 1 s with them held (slowed), then slams them down where it stands, or a short toss toward the aim. Used to haul a carry into the lake. | None: the animal's jaws |
| 4 (ult) | Toxic Flood | Blows all three tanks: a wave of toxic liquid rolls out, pushes enemies outward, and leaves a wide poisoned lake. Heavy damage to anyone who stays. The hippo heals standing in its own lake. Afterwards the tanks are empty: weak until they refill. | Intoxicate's burst and lingering ground; the all-in cost; the old wallow's heal |
| Basic | Bite chain | Bite, jaw swing, stomp (unchanged). | |

**Combo:** Piston Drop in, Vent while they sit in the eruption window, Lockjaw the carry and drag them into the
puddle, Toxic Flood. A great initiator; a missed dive leaves it drained.

**Dropped:** Coolant Dump (the wallow) as its own slot; its heal lives in the ult.

## Clips (hippo 3D lane, round 7) against the new kit
- Vent: Yawn (cone_start 0.35, hit 0.45, cone_end 0.95). Effect built: `scripts/moba3d/hippo_vent_fx.gd`.
- Piston Drop: Belly_Flop (push_off 0.22, hit 0.72). The eruption 0.5 s after hit needs no new clip.
- Lockjaw: Chomp (capture 0.24, release 1.12) fits the clamp and the slam-down, not the walk while holding. A held
  carry needs a "walk with jaws closed" loop or an upper-body hold over the walk: hippo 3D lane's call.
- Toxic Flood: no clip. The Wallow clip can stand in; a "blow the tanks" move (rear up, tanks vent, slam) reads better.
- Open question for game feel: can Vent be cast during the Piston Drop's air time (0.23 to 0.70 s), as Bacchus's burp
  can mid-flop? If yes, the spray aims down and the puddle lands where the hippo lands.
