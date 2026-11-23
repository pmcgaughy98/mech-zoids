# Pangolin basic attack (decided 2026-11-18: A, Pry chain)

**Decided:** Preston, 2026-11-18: "A, Pry chain". He also confirmed the reach in the game feel session: "The short reach
is fine, build A" (1.6 m swipes, 1.9 m pry). After the claw measurement was corrected, he confirmed the reach again:
"Keep 1.6 ／ 1.9". B, C and D are not being built. The 8 s magnetise cap stays unused unless playtests show the refresh is too
strong.

Kit design lane, asked by the pangolin 3D lane. Preston (relayed by the hub): "Study smites, especially but MOBA's in
general I know smite had a lot of unique ways each god felt and basic was one of them Whether attack chain combos,
attack speed, timing, aoe on some hits, izanami's, sylvanus's, etc."

SMITE is private reference: only patterns come from it, no names, numbers or art go into
the kit.

## Pick: A, "Pry" chain (three beats)
| Beat | Clip | Hit at | Reach (centre to edge) | Area | Damage (share) | Next beat after | Magnetise |
|---|---|---|---|---|---|---|---|
| 1, left swipe | Basic_Left as it is (0.50 s, half rear) | 0.20 s | 1.6 m | the nearest enemy within a 35 degree half angle | 23 (30%) | 0.75 s | none |
| 2, right swipe | Basic_Right as it is (0.50 s, half rear) | 0.20 s | 1.6 m | the nearest enemy within a 35 degree half angle | 23 (30%) | 0.75 s | none |
| 3, pry | Claw_Rake reworked (0.80 s, full rear, both claws drop together) | 0.375 s (matches r13) | 1.9 m, including a 0.3 m lunge on the drop (from 0.27 s) | every enemy within a 60 degree half angle | 30 (40%) | 1.1 s, then back to beat 1 | each magnetised enemy hit goes back to the full 4 s |

- **Where the numbers come from:**
  - **Beat gaps:** each clip's length plus a short window to move: 0.50 + 0.25 s for a swipe, 0.80 + 0.30 s for the
    pry. One cycle is 2.6 s.
  - **Damage:** one cycle is 76 damage, which is 29 a second on one target, between the gorilla (28) and the rhino
    (33). Per second of its own beat, a swipe deals about 31 and the pry about 27. The pry hits everyone in its arc, so
    it pays for that area with less single-target damage.
  - **Reach (measured):** the pangolin 3D lane measured the clips in Blender on 2026-11-18.
    - The claw tips reach 1.28 to 1.29 m from the centre, both at the swipe hit (0.20 s) and at the rake's impact
      (0.36 s). At idle they sit at 0.98 m.
    - The snout is the front-most point, at 1.50 m. The lane's first measurement gave that 1.50 m as the claw reach,
      then corrected it.
    - With 1.6 m swipes, hits land about 0.3 m past the claw tip.
    - **The built pry (round 13, from the exported glb):** at the 0.375 s impact the claws are 1.15 to 1.19 m forward,
      or about 1.48 m with the 0.3 m lunge. They peak at 1.29 m around 0.35 s, while still 14 cm off the floor. So a
      1.9 m pry lands about 0.4 m past the claws.
    - It's still the shortest basic in the roster (the rhino has 2.0 m, the gorilla and bison 2.2 m). That's on
      purpose: the ball is how the pangolin closes in.
    - I first proposed 2.0 and 2.2 m from the roster. The measurement replaced them.
    - **Decided:** Preston, 2026-11-18, relayed by the game feel lane: "Keep 1.6 ／ 1.9". He re-picked after the
      claw correction, knowing hits land about 0.3 m past the claw on the swipes and 0.4 m on the pry.
    - **Swipe timing:** at the 0.20 s hit, the swiping claw is still 0.25 to 0.34 m off the floor and touches down at
      about 0.24 s. A swipe hits a machine's legs and body, not the floor, so 0.20 s stays. The pry is the floor
      impact.
  - **Not taken:** the roster's 2.0 and 2.2 m, a forward step baked into the swipes, and the 1.4 / 1.6 m cut.
  - **Arcs:** half angles, the same way the kit states Salvage's 40 degrees.
- **Rhythm:** quick, quick, heavy. The pry's wind-up is 0.38 s from a full rear, almost twice a swipe's, so enemies
  can see it coming.
- **Chain rules:**
  - A beat whose hit time passes moves the chain on, whether it hit anyone or swung at the air (the game feel lane's
    call, 2026-11-18, kept). So the clips always play left, right, pry in order.
  - 1.5 s after the last beat swung, hit or miss, the chain goes back to beat 1.
  - Moving after a beat's hit time cancels the rest of the clip and keeps the chain. Moving before it cancels the
    swing, and the next basic tries the same beat again.
  - Swinging twice at the air to have the pry ready on arrival costs 1.5 s of no damage, more than the pry gives back,
    so it isn't worth guarding against.
- **Magnetise, written out:**
  - The pry refreshes magnetise but never applies it. Salvage stays the only way to magnetise.
  - The cycle is 2.6 s and the refresh is 4 s. So while every pry lands on the same enemy, its magnetise never drops,
    and the ball can curve onto it whenever the fight moves. That's the intent.
  - The pry does not refresh the plate strip. The 15% extra damage still ends 4 s after the Salvage.
  - If that's too strong, a cap: one Salvage's magnetise can't be kept going more than 8 s past that Salvage.
- **Clips:**
  - Basic_Left and Basic_Right are used as they are.
  - The pry is one clip: today's Claw_Rake (0.80 s, hits at 0.20 and 0.36 s) reworked into a single both-claws impact
    at 0.38 s from a full rear, back on four feet by about 0.65 s. Same length, so it's a retime and a pose change,
    not a new clip.
  - The clip is built in place. The 0.3 m lunge is a nudge from the kit, so the feet don't slide: Godot uses KitFeel,
    and Unreal moves the actor.
  - **Built:** round 13, 2026-11-18, `out/pangolin-r13.glb`, pangolin 3D lane.
    - Both claws touch the floor together at 0.375 s, and it's back on four feet at 0.642 s. The clip is 0.80 s.
    - Its start and end poses match round 12, so it chains from Basic_Right and back to idle.
    - At the full rear, the arms hang raised in front of the chest.
    - Films are in the shared notes under `pangolin-3d/`.
  - **Lunge timing:** the nudge belongs on the drop, about 0.27 to 0.38 s, so the body moves forward as the claws come
    down and the full 0.3 m is reached at the impact. Starting it at the hit, with the claws already down, reads as a
    shove after the blow.
  - **Godot has it now** (game feel lane, 2026-11-18):
    - `MechModel3D.lunge` starts at `pry_lunge_at` 0.27 s and reads 0.30 m at the 0.375 s hit, then eases back over
      0.3 s.
    - The checks pass: pangolin_pry_probe 0 fail, match_check 68/0.
    - Arena Godot still plays the old two-hit Claw_Rake until r13 is imported. The kit times the pry itself either way.
- **Attack speed:** no kit has an attack-speed stat today. If items add one, it should shorten each beat's gap and
  clip by the same factor, so the hit stays at the same point in the swing.

## Alternatives named
- **B, plate fling:** the third beat throws one stolen plate 6 m as a projectile that magnetises the first enemy it hits
  (1.5 s). It only works while wearing plates, the 4 s after a Salvage.
  - It gives a reason for range on a short body.
  - But it makes a second way to magnetise, so the ball can curve onto a carry without Salvage. It's also a ranged
    beat on a melee diver.
- **C, plain swipes:** left and right alternate every 1.0 s, 30 damage, one target, and every hit refreshes magnetise.
  It's the simplest to build and read, but has the least identity.
- **D, add-on to A: claws wind the ball.**
  - A pry that hits an enemy machine stores one bank-shot charge for the next roll. It's the same charge a wall bounce
    gives, with the same cap of 3.
  - The brawl then feeds the roll out, which is very on-theme.
  - It needs the game feel lane to keep charges between rolls. Today they only exist during a roll.
- **Why no out-and-back or lobbed basic:** those shapes let a character fight from range. The pangolin is a melee diver
  whose range tool is the ball, and a ranged basic would compete with it. B is the closest to one, and it's limited to
  the 4 s after a Salvage.

## Who builds what, after Preston picks
- **Pangolin 3D lane:** the pry (Claw_Rake reworked, one clip). The claw reach is already measured: details are in the
  hub's shared notes, `pangolin-3d-unreal-port-review-2026-11-16.md`, section "Claw reach for the Pry proposal".
- **Game feel lane (Godot) and the Unreal pangolin port:** the chain in each kit.
  - Godot's pangolin uses the base kit's 6 m shot today. Unreal's LMB plays Claw_Rake: 30 damage, 6 m, no line check.
- **Pangolin effects lane:**
  - a claw streak on each swipe;
  - a heavier spark burst on the pry;
  - a small magnet pulse on each refreshed enemy.

<details><summary>What the study found</summary>

**SMITE (checked 2026-11-18 on the SMITE and SMITE 2 wikis):**
- **Basics are aimed, not locked on.** Melee basics hit the closest enemy in reach, and ranged basics fly in a
  straight line.
- **Many gods have a chain.** Each hit in the chain has its own damage share and its own swing time (the delay before
  the hit lands).
  - The usual shape is plain hits, then a heavier, slower last hit.
  - That last hit often catches every enemy in an area in front.
  - Some chains cleave on certain hits only.
- **Some basics are a different shape altogether:**
  - Izanami throws a piercing blade that goes out and comes back. It hits everything on the way out and again on the
    way back, with the damage split between the two.
  - Sylvanus lobs an area shot that can go over walls.
- **What gives each god a feel:** the shape of the hit (single, cleave, area, pierce, return) and the rhythm (where
  the slow, heavy beat sits).

**MOBAs in general (general knowledge, not checked live):**
- **Every basic has a wind-up and a recovery.** The hit lands at a fixed point in the swing. Moving after that point
  cancels the recovery; moving before it loses the hit. Good players weave movement in after each hit. This game
  already works that way: moving cancels a basic (Preston, 2026-11-06).
- **Basics often feed the kit:** every third hit is special, a hit refreshes a mark, or a hit charges the next
  ability. The best of these make the basic part of the character's loop, not just damage between cooldowns.

**This roster (Godot kits):**
- **Melee basics:** 2.0 to 2.2 m from the body's centre to the target's edge, at about one strike a second. The
  gorilla does 28 damage a second and the rhino 33.
- **The stand-in shot:** 30 damage, 6 m, every 0.9 s.

**What the pangolin needs:**
- **Role:** a diver that gets into the back line and survives there.
- **Its loop:** Salvage magnetises enemies (4 s) and strips their plates (they take 15% more damage for 4 s). The ball
  curves toward magnetised enemies and banks off walls for charges. Scale Flare blocks and spikes the ball.
- **The body:** its claws only read when the chest rises. The clips already half-rear for a swipe and fully rear for
  the rake. The front legs sit 1.1 m behind the snout, so the reach is short.

</details>
