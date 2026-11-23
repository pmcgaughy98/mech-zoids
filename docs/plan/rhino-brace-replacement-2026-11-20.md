# Rhino slot 3: replacing Brace (decided 2026-11-20: Aftershock)

**Decided:** Preston, 2026-11-20: "Aftershock". B and C are not being built. The wind-up is the whole-body forward drive
from the rhino 3D lane's read (see Clips), not a horn dip alone.

Kit design lane. Preston, 2026-11-20: "replace brace for rhino also talk to rhino session about it. MOBA kit it up".

## Why Brace goes
- **It's passive.** You plant for up to 3 s at a third of your speed and wait to be hit. Then a ring goes off around
  you.
- **It repeats the passive.** Front plating already blocks frontal hits for charge. Brace is the same idea with your
  feet nailed down.
- **The ring repeats ground pound.** That's already a circle around the rhino.

## Constraints from the roster (`moba-kits.md`, "Roster checks")
- **Already taken by other machines:**
  - taunt: the gorilla's chest beat;
  - a crack along the aim: the gorilla's Fault Line;
  - shields: the gorilla and the lobster;
  - silence: removed on 2026-11-05.
- **The rhino's own rules:** it owns stun. It has no dash, because Tremor charge is its only charge (Heave decision,
  2026-11-12).
- **Unclaimed:** "grounded", where an enemy can't dash, leap or roll. No machine has it. It fits a seismic machine, and
  it's how a MOBA tank "holds the line" against divers.

## Pick: Aftershock (aimed seismic wave, grounds)
The rhino drives its horn into the floor, and a seismic wave rolls forward in a cone along the aim.

| | Base | Per Seismic charge spent (up to 5) |
|---|---|---|
| Wind-up | 0.35 s, horn down, the drum ring flares | |
| Wave | 8 m long, about 6 m wide at the end (20 degree half angle), travels at 16 m/s | +1 m long (13 m at full) |
| Damage | 30, once per enemy | +6 |
| Slow | 30% for 1.5 s | |
| Grounded | 2.0 s: no dashes, leaps or rolls (walking and basics still work) | +0.2 s (3.0 s at full) |
| Full charge (5) | also stuns 0.75 s, the same full-charge payoff Brace had | |
| Cooldown | medium-long, 12 s (there's no 11 s tier) | |

- **Charge:** it spends the charge, like Brace did. Front plating and Tremor charge still build it.
- **Plays as:**
  - Engage: Tremor charge in, then Aftershock the group so nobody leaps out of the finale.
  - Peel: Aftershock the diver jumping onto your back line, and it can't jump.
  - Both are active, aimed plays with a counter: the wave is visible and can be walked out of at the far end.
- **Grounded stops:** the pangolin's roll, the kangaroo's hops, the hippo's Piston Drop, the gorilla's bound and any
  other dash or leap. It doesn't stop walking.
- **Kit text that changes:**
  - The passive loses "(plating or Brace)".
  - "Brace to soak the focus and let it go as a blast" becomes "Aftershock the escape or the dive".
  - Grounded is added to the Roster checks with the rhino as owner.
- **Overlap to watch:** Heave also sends a ripple forward. Keep them apart in the effects. Heave is one raised seam
  that runs to a single enemy. Aftershock is a wide fan of cracks with dust.

## Alternatives
- **B, Quick Brace (counter stance):**
  - A 1 s full block with no slow walk. It releases the moment it's first hit, or at the end, as a short wave that
    grounds and slows the attackers.
  - It's skill timing, and the cheapest option, since it reuses the brace clips (enter, hold, release).
  - But it keeps the "wait to be hit" shape.
- **C, Fissure ridge (terrain):**
  - A line of raised rock for 3 s that blocks movement. The biggest playmaker.
  - It's new tech in both engines (moving obstacles and navigation), and it reads close to the gorilla's Fault Line
    crack.

## Clips (the rhino 3D lane's read, 2026-11-20, measured on rhino.glb)
Full table: `D:\dev\_scratch\rhino-donor-2026-11-08\round27\brace_replacement_clip_read.md`.
- **A, Aftershock, needs a new clip of about 0.8 s.**
  - No existing clip gets the horn lower than 0.77 m (idle is about 1.05 m).
  - `brace_release` is too small, a 0.2 m dip.
  - `ground_pound`'s opening has the right timing, but slots 2 and 3 would then look the same.
  - Cost: about one rhino 3D session plus about 40 min of Unreal slot. A 15 min test pose comes first, to check the rig
    reaches a true horn-in-floor pose.
  - **The wind-up changes from a horn dip to a whole-body drive.** From the high MOBA camera a horn dip reads weakly and
    looks like the start of Heave. What reads instead: the body pitching forward and dropping, the shoulder pistons
    thumping, the drum ring flaring and the floor effect, with the horn dip on top.
- **Test pose result (rhino 3D lane, 2026-11-20):** the rig can't put the horn tip in the floor.
  - Head and horn are one rigid bone, and the horn curves up from the snout, so the snout touches first. Even the
    shipped `horn_gore` keeps the chin 6 cm off the floor, with the horn tip at 0.77 m.
  - What works is a **snout-first slam**: the body tips 4 degrees nose-down and the head drops 28 degrees. The chin
    meets the floor and the horn tip sits at 0.54 m.
  - Mesh stretch is a little past the shipped clips' deepest frames but not broken. Going lower tears the front
    shoulders.
  - From the game camera it reads as a head slam. The real clip steps the front feet forward and plants one toe.
  - The clip event is `aftershock_hit` at 0.35 s, matching the wind-up.
  - Notes: `D:\dev\_scratch\rhino-donor-2026-11-08\round27\aftershock_testpose.md`.
  - **Waiting on Preston:** is a snout slam with the horn tip about half a metre up close enough? The kit doesn't
    depend on the horn touching: the wave starts at the rhino's front either way. If he says yes, "drives its horn
    into the floor" and "horn down" in the pick above become "slams its head into the floor".
- **B, Quick Brace, costs no art.**
  - `brace_enter` at 1.6x reaches the low pose fast, and `brace_hold` loops for any length.
  - Then `brace_release` (0.6 s) for the wave, or `MF_brace_exit` (0.4 s) on timeout: about 1.4 to 2.0 s in all.
- **C, Fissure, needs no clip.** Its cost is engine work.
- **The five brace clips** stay in the GLB, unmapped, if A or C is picked.

## Build order (hub, 2026-11-20)
1. The game feel lane builds Aftershock in Godot first, since Godot is the behaviour reference. It also writes the list
   of moves that grounded blocks.
2. The rhino 3D lane (`local_c87babea`) owns the Unreal port as well as the clip, as hub row 80. It starts once game
   feel has Aftershock in Godot. (Correction: I first wrote row 72 here. Row 72 is the pound slow.)
   - Grounded crosses lanes, so the port touches shared code (MechHold, Trial) and needs the full Check Migration.
   - Game feel's blocked-moves list goes to the rhino 3D lane too.

## Grounded rules (kit design lane, 2026-11-20)
The game feel lane read every Godot kit for code that moves the caster itself. Full notes:
`D:\dev\_scratch\game_feel\grounded-blocked-moves-2026-11-20.md`.

**Blocked while grounded** (the caster moves itself):
- Rhino: Horn Toss (short dash), Stampede and its Tremor charge (long charge).
- Gorilla: Drive Slam, the arena bound. The grab goes with it, since it only comes off a Drive Slam hit.
- Kangaroo: Hop and Jab (leap); Boxing Ring (the leap in and the slips during the bout).
- Hippo: Piston Drop (leap); Lockjaw (the carry).
- Pangolin: Iron Ball and Scrap Comet (long rolls); Scale Flare mid-roll ends with the roll.
- Fennec: Blink Gate and its Gate Back recast (blinks); Tunnel (long move).
- Wolf: Lunge (short dash).
- Bison: Freight. **My call, Preston can change it:** it's an ultimate that relocates the bison, so it counts as
  mobility even at about 4.5 m/s.

**Not blocked:**
- Bison: the Chain haul after the hook (about 4.2 m/s). It's walking pace, and the move is about the hook, not the
  walk.
- Bison: Plow. Confirmed against the kit text: it throws enemies sideways and doesn't move the bison.
- Ground Pound, Hex Shield, Fault Line, Chest Beat, Tail Kick, Guard, Vent, Toxic Flood, Salvage, Scale Flare
  standing, Sand Kick, Ear Burst, Sonic Boom, Whistle.
- Every basic attack, including the pangolin pry's lunge (it moves the model, not the machine).
- Cobra has no Godot kit yet, so these are ruled from the kit text in `moba-kits.md` (my calls, Preston can change
  them):
  - **Blocked:** Seam (travels inside a wall, like the fennec's Tunnel; it can't be started while grounded, and since
    walls stop the wave, a cobra already inside a wall isn't hit),
    Breach (it drives itself through the wall), and the Wall Line crossing. A grounded cobra that moves into a wall
    stops at it instead of slithering over. The passive's harder first basic still works after a crossing made
    before the wave.
  - **Not blocked:** Ghost Run. It's a speed boost with pass-through, steered like walking, not a dash or leap.
    Aftershock's 30% slow still cuts it. Hood Gaze isn't blocked either.

**Edge cases (decided):**
1. **A move already running when the wave lands:**
   - Airborne and short moves finish: hops, Piston Drop, Horn Toss's dash, Drive Slam, Lunge, a blink. Nothing stops
     in mid-air.
   - Long ground moves stop at once into their normal ending, with no cooldown refund: the pangolin roll and comet,
     Stampede, Tunnel, the Lockjaw carry, the Boxing Ring slips, and Freight.
2. **Airborne machines are missed.** It's a ground wave, so a kangaroo mid-hop or a hippo mid-drop isn't hit. Jumping
   it is the counterplay. It stays a counter you have to time: the wave passes in about half a second.
3. **Held machines** (in a grab, carry or Lockjaw) still take the wave's damage and grounded.
4. **Forced movement** (knockbacks, tosses, pulls) still moves a grounded machine. Grounded blocks only its own moves.
5. **A blocked slot** reads as not ready: locked on the HUD, pressing it does nothing and costs no cooldown, and bots
   don't try it.
6. **Fennec's gate:** Gate Back is blocked. If the gate runs out during grounded, it's lost.
7. **A second wave** refreshes grounded to the longer time left. It doesn't stack.
8. **The full-charge stun** (0.75 s) runs alongside grounded. The stun ends first, and grounded carries on.

**Build:** a `grounded` timer on the machine like `stunned`; each kit lists its mobility slots and `slot_ready`
refuses them while grounded; the long moves add grounded to their per-frame stun and hold check. The same list goes
to the rhino 3D lane for the Unreal port.

## Godot build (game feel lane, 2026-11-20)
Built to the spec above, with grounded on every listed move. The probe passed 74 of 74, `match_check` 68 of 68, and
the older kit probes and `kit_api_check` had no failures. Nothing is committed. Notes:
`D:\dev\_scratch\game_feel\aftershock-build-2026-11-20.md`.
- Machines in the air when the front passes dodge it (tested with a real kangaroo leap).
- Kangaroo slips: no new ones while grounded; one already moving finishes.
- Gate Back is refused on the key press and on the bot's snap back.

**Rulings on the build's open points (kit design lane, 2026-11-20):**
1. **Cooldown 12 s** (the medium-long tier). Kept; there's no 11 s tier, and adding one isn't worth it.
2. **Reach is measured to the target's near edge**, so a target whose centre is about 8.8 m away is still hit at no
   charge. Kept: a wave that touches the body should hit it.
3. **Walls stop the wave** (changed from the build, which ignored them). It's a per-target clear-line check, like
   Freight's. Walls become cover, which adds counterplay and means the rhino can't ground what it can't see.
4. **A stun or hold during the 0.35 s wind-up cuts the cast**, with no cooldown refund (the game feel lane's rule,
   kept). The Seismic charge is spent only when the wave goes out, so a cut cast keeps its charge.
5. **A grounded Freight ends in its normal pile-up**, so its coupled cars are still stunned, just earlier and shorter
   than the bison wanted. Kept. It follows the long-move rule.
6. **The rhino bot casts it at any machine within 7 m**, with no health gate. Kept. Brace's health gate made sense for
   a defensive stance; Aftershock is engage and peel.

## Not checked
- The numbers are a starting point and haven't been played.
- Rulings 3 and 4 are built in Godot (game feel lane, 2026-11-20; probe 80 of 80, `match_check` 68 of 68):
  - Walls: each target needs a clear line from the stomp point (`MatchTeams.clear_line`, Freight's check). In the
    probe a wall blocked only the gorilla, which wasn't hit or grounded; the kangaroo beside it in the open took 30.
    Only a test wall on the arena's wall layer was tried, not the real arena walls.
  - Charge: the build already spent it when the wave goes out. A cast stunned 6 frames into its wind-up sent no wave
    and kept all 3 charges, and the cooldown still ran.
- Nothing is committed, and nobody has watched it in a game window.
- The 0.5 s figure in edge case 2 is the wave's 8 m at 16 m/s, not measured in a game.
