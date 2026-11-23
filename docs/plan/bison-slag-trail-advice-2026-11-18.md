# Bison Freight haul slag: how MOBAs draw moving ground damage (kit design lane, 2026-11-18)

Asked by the bison effects lane. Preston said the slag "makes it look like poop is dropping, especially during
towing", the lava doesn't have to come from the pipes, and the other effects stay.

## What real MOBAs do (checked 2026-11-18)
- **LoL, Singed's Poison Trail:** touching the trail applies poison that deals magic damage every 0.25 s for 2 s
  (LoL wiki data page). The damage carries on after the enemy leaves the trail.
- **Dota 2, Batrider's Firefly:** a flame trail for 15 s, and "the entire flame trail disappears at once" when the
  duration ends (Dota 2 wiki). The fire is one continuous path, not pools.
- **SMITE 2, Agni's Path of Flames:** a fire trail on the floor that lasts 3 s (a SMITE 2 guide site, not an
  official page). A SMITE 1 player noted the trail started a bit behind Agni.
- **The common rule:** a moving damage trail is drawn as one continuous track, and the drawn edge is the edge that
  hurts. None of the three drops separate blobs.
- **Paragon, coming soon:** Grux has `P_Stampede_Trail` and `P_Grux_Magma_StampedTrail`. Row 58's breakdown covers
  all 13 heroes, so their layer-by-layer construction will be in `sheets\Grux.md` after that row.

## Why the current slag reads as poop
- **Spaced blobs behind the body:** one patch per drop, spaced 230 to 295 cm, born behind and under the body.
- **The patch doesn't match the hitbox:**
  - The hitbox is a circle 120 cm across (60 cm radius, plus the enemy's body radius).
  - The Godot patch is an oval, 0.8 x 1.76 m.
  - If the 1.76 m runs along the path, the drawing is longer than the hitbox in that direction and narrower than
    it from side to side. Players learn spacing from the drawing, so it should match the hitbox exactly.

## Recommendation
1. **Make the damage continuous (a kit change, Preston's call).**
   - Each 0.6 s drop becomes a capsule from the previous drop point to this one, radius 60 cm, living 4.5 s, with
     the same 12 damage per second.
   - The visual is then one burning track that matches the hitbox exactly.
   - Crossing the track costs about 5 to 6 damage: 120 cm plus body width at about 350 cm/s is roughly 0.45 s. That's
     the same as crossing one of today's circles.
   - The real change is for chasers. Anyone following the bison takes 12 per second for as long as they follow,
     instead of weaving through the gaps.
   - **Correction (same day):** I first wrote that the track would be 17 to 22 m long. That was wrong: I multiplied
     the 4.5 s burn time by haul speed, but Freight only hauls for 2 s (`moba-kits.md`). The track is about 8.4 m
     long, and each part burns for 4.5 s after it is laid. Agni's floor trail lasts 3 s.
   - **Decided:** Preston, 2026-11-18: "Yes, continuous track". The 4.5 s burn time is unchanged.
2. **If the damage stays as circles,** draw each circle exactly 120 cm across, flat, with a bright rim. It's honest,
   but circles 2.3 to 3 m apart will still read as droppings. The spacing is the root cause, not the art.

## How to draw the track (effects lane, numbers to start from)
- **Born at ground contact, never from height:**
  - Start it where something touches the floor at the rear: the dragged load's contact point if the haul tows one,
    otherwise the rear hooves or treads.
  - Add a short bright scrape with sparks, living 0.2 to 0.3 s, at the contact point to show where it comes from.
  - Nothing falls from the body.
- **Spawn by distance, not by time:** one strip segment every 25 to 40 cm of travel, so the track is even at any
  speed. Cascade's spawn-per-unit module does exactly this. It will show up in the Paragon sheets.
- **Flat:** a decal or a mesh that hugs the ground, under 10 cm tall. Embers are sparse (1 to 3 per second per metre),
  small and short-lived, rising from the crust.
- **Edge:**
  - A rim 10 to 15 cm wide, about twice as bright as the inside, sitting exactly on the hitbox edge.
  - The inside is dark crust with glowing cracks that pan slowly backward (0.2 to 0.4 m/s) so it reads as molten, not
    wet.
  - The inside's alpha is about 0.6 to 0.8, so the floor shows through faintly.
- **End:** in the last 0.5 to 0.75 s of each segment's life, the rim dims and the crust cools to black. Enemies can
  read "safe soon", and the drawing ends when the damage ends.

## When an enemy stands in it
- **On the enemy:**
  - Burning embers at the feet while in the track.
  - A brief orange flash on each damage tick.
  - A damage number per tick.
  - A sizzle sound per tick.
- **Feedback every 0.5 s:** the flash, number and sizzle show about 6 damage each time. The kit itself burns per
  frame, the same as Godot and every bison burn. Settled with bison Unreal, 2026-11-18.
- **Optional linger:** Singed's poison keeps ticking after the enemy leaves. A 0.5 to 1 s linger would be a kit
  change, Preston's call.
- **Enemy-only colour:** LoL and Dota draw these the same for both teams and rely on the colour reading as harmful.
  An enemy-red rim is a game-wide rule for Preston to set, not a bison choice.

## Who does what
- **Effects lane (row 62, BisonFx files only):** the drawing, the contact scrape, distance spawning, the rim, the
  fade, and the on-enemy burn.
- **Bison Unreal lane (`local_f94df86f`):** the capsule hitbox and any change to the duration or linger. Only with
  Preston's yes and a hub row.
