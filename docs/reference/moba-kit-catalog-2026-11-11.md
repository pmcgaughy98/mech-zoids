# MOBA kit catalog: the patterns worth stealing, structure only (2026-11-11)

Preston: "catalog and think about all the moba kits we from the games we care about ... I found the ability I was
talking about its Ornn's call of god from LOL".

**What this is:**
- A catalog of kit *patterns*, with the clearest examples from:
  - League of Legends;
  - SMITE;
  - Paragon / Predecessor;
  - Deadlock;
  - Overwatch;
  - Marvel Rivals.
- **It is not every hero.** That would be about 450 kits; the exact, cheap route for most of them is the tools in
  `docs/reference/game-file-tools-2026-11-11.md`, once they are installed.
- **Sources:**
  - Ornn's ult was checked against the League wiki today.
  - Everything else is from general knowledge as of mid-2026. Kits get reworked, so check one before quoting its
    numbers.
  - **Checked 2026-11-12** against the ability text in `D:/tools/game-extract/dumps/` (SMITE 2, Predecessor and
    Marvel Rivals from their sites, Overwatch from its game files). Every row in section 2 from those four games
    was checked. Corrections are marked in place; rows added from the dumps are checked. League and Deadlock rows
    are still from memory.
- **The rule:** inspiration only. Take the structure; never a champion's or god's kit, name, look or numbers.

---

## 1. Ornn's Call of the Forge God: what Preston meant
**Checked on the League wiki, 2026-11-11:**
- **First cast:** Ornn summons a massive elemental far away, and it stampedes toward him, damaging and slowing every
  enemy it runs through.
- **Recast:** Ornn dashes. If he collides with the elemental, he headbutts it: it stampedes off in his direction and
  now knocks up and stuns (1 s, 0.5 s after the first champion).
- It can hit the same enemy twice, once on each pass.

**Why it feels giant, in structure:**
1. **It starts far away and crosses a huge stretch of the map.** The sweep is the summon's trip, not a cone at your
   feet.
2. **Everyone sees it coming.** The long run is the dodge window, which is why it can be so strong.
3. **A two-part ult:** the caster's own body move meets the summon and redirects it. That takes skill (timing and
   angle), and it is the spectacle.
4. **The summon is the caster's own theme made huge**, a forge beast for a forge god. Ours would be a hard-light copy
   of the machine itself.

**Why it doesn't fit the hippo** (Preston was right): the hippo's kit is a reservoir it fills and pours out. It
doesn't charge, and nothing in it meets a summon head-on. The structure belongs to a **horned charger**.

### Where it fits our roster (superseded)
*Superseded:* Preston, 2026-11-11: "Doesn't need the Ornn-style". On 2026-11-12 he dropped the
bison's charge and gave it an ode to Ares. Ornn was an example of a kit drawing on a god's power, not a move to
copy. Kept for the record.

**Bison (was recommended).**
- A herd animal calling a giant stampeding copy of itself reads instantly.
- It would be the bison's ult and its identity, with no built work disturbed.
- Its power theme is unread, so the look of the summon waits on that.

**Rhino (alternative).**
- The horn toss is already a headbutt, so meeting the summon needs no new move. The giant's size could spend the
  Seismic charge.
- But the rhino's built ult is the Tremor charge with the carry, which Preston asked for. This would replace it or
  push it to another slot.

**A draft in our terms**, for whichever machine he picks. Names and numbers are his.
- **Cast:** the machine plants and calls. A giant hard-light copy of itself (about 4x scale) rises out of the ground
  up to about 25 m ahead and charges back toward it. Everything the giant runs through takes damage and is slowed.
- **Recast:** the machine charges to meet it. If they collide, the giant turns and runs on in the machine's
  direction, bigger and faster, and now knocks up and stuns.
- **From the chase camera:**
  - the caster sees the giant rise on the horizon and come at them, which is the best view of it any camera could
    give;
  - enemies hear a map-wide call when it rises, and the giant is tall enough to read over walls.
- **Art:**
  - the summon is the machine's own rigged model scaled up with a hard-light shader, playing its existing run clip;
  - the recast reuses the charge or horn-toss clip;
  - new effects: the rise from the ground, the trail, the collision flash.

---

## 2. The pattern catalog
Each row: the structure, where it shows up, and where it could fit our roster.

### Stores what it takes, then releases it (absorb and release)
| Example (game) | Structure |
|---|---|
| Sett, Grit and Haymaker (LoL) | damage taken is stored, then spent on a big cone punch |
| Zarya, energy (Overwatch) | shields that absorb damage charge her weapon |
| Sigma, Kinetic Grasp (Overwatch) | absorbs projectiles in front of him and turns them into extra health (*corrected 2026-11-12:* said "shield") |
| Cabrakan, Refraction Shield (SMITE 2) | taking damage charges his shields (more protections); at max stacks he gets an enhanced blast, on its own cooldown, that stuns (*corrected 2026-11-12:* said the slam stuns only at full) |
| Magneto, Metal Bulwark (Marvel Rivals) | a shield on an ally; every 100 damage it absorbs charges his cannon |
| Magneto, Meteor M (Marvel Rivals, ult) | rises, pulls every enemy projectile nearby into a metal mass, then throws it |
| Mister Fantastic, Reflexive Rubber (Marvel Rivals) | immune while it soaks; after 300 damage or at the end, fires it back as a projectile |

**Ours:** the rhino's Seismic charge, already built in this family. No other machine should get it.

**Overlap check:** Meteor M is the closest outside kit to the pangolin's magnet line (scale flare, iron ball). The
pangolin's ball curves toward magnetised targets and doesn't soak projectiles. Keeping it that way keeps them apart.

### Fills a meter by fighting, with a risk at the top (fill and spend)
| Example | Structure |
|---|---|
| Rumble, Heat (LoL) | abilities build heat; a sweet spot empowers them; overheating silences him but empowers his basics |
| Gnar, Rage (LoL) | fighting fills rage; at full he transforms |
| Kled, Courage (LoL) | the mount's health is a second bar; he fights on foot until he earns it back |

**Ours:** the hippo's flask.
- One idea it suggests: a full flask held too long **overpressures** and vents by itself.
- That would add the risk Rumble's heat has. It is Preston's call; not added to the kit.

### Changes the map: walls and terrain
| Example | Structure |
|---|---|
| Taliyah, Weaver's Wall (LoL) | a very long wall of terrain across the map that she can ride along |
| Anivia, Crystallize (LoL); Mei, Ice Wall (Overwatch); Ymir, Ice Wall (SMITE 2) | a short wall that splits a fight; Ymir's also shoves enemies aside as it forms |
| Ornn, Volcanic Rupture (LoL) | makes a pillar of terrain that his other moves smash for a knock-up |
| Azir, Emperor's Divide (LoL) | a moving wall of soldiers that shoves enemies back |
| Symmetra, Photon Barrier (Overwatch) | a massive barrier that stops shots ("across the whole map" is memory; the game's text says "massive") |
| Groot's walls (Marvel Rivals) | two kinds of wall (Thornlash, up to 3 at once, and Ironwood), built on floors or walls at any angle; each wakes an extra effect while Groot is near, and he can break them from afar |
| Cabrakan, Tectonic Shift (SMITE 2) | a fissure throws up five pieces of earth as a wall; refire smashes them all at once |
| Thor, Tectonic Rift (SMITE 2) | a fissure that stops movement but lets shots through |
| Aurora, Glacial Charge (Predecessor) | a dash that leaves a wall behind which allies can walk on |
| Marvel Rivals' destructible maps | the map itself breaks |

**Ours:**
- The gorilla's hex wall in the empty slot 2 is this pattern.
- **Ornn's pillar idea fits the rhino:** a pound that raises a slab its charge can slam into, for a bigger hit.
  Proposal only. Cabrakan's Tectonic Shift (raise the pieces, refire to smash them) is the nearest checked example.

### Changes the map: arenas
| Example | Structure |
|---|---|
| Jarvan IV, Cataclysm (LoL) | leaps in and rings the area with impassable terrain |
| Mauga, Cage Fight (Overwatch) | a barrier that traps him and enemies inside ("keeps help out" is memory, not in the game's text) |
| Veigar, Event Horizon (LoL) | a cage whose edge stuns whoever crosses it |
| Dekker, Containment Fence (Predecessor, checked) | a circular energy fence enemy heroes can't pass through |
| Odin, Ring of Spears (SMITE 2) | a ring that slows enemy gods and stops their healing |
| Yemoja, Riptide (SMITE 2) | a water ring that knocks back anyone who enters; allies are thrown further and sped up |

**Ours:** the kangaroo's boxing ring, and the gorilla dome's trap. The ring keeping outsiders out (an option in the
kit design doc) is the Mauga version.

### Changes the map: routes
| Example | Structure |
|---|---|
| Kelvin, Ice Path (Deadlock) | a skating path in the air for himself and allies |
| Bard, Magical Journey (LoL) | a one-way portal through terrain that anyone can use |
| Rek'Sai, tunnels (LoL) | lasting tunnels around the map |
| Doctor Strange, Pentagram of Farallah (Marvel Rivals); Symmetra, Teleporter (Overwatch) | two linked portals; Strange's join any two spots on the map, and every player and projectile can pass |
| Gideon, Torn Space (Predecessor) | leaps through a portal that stays open; allies can follow through it |
| The Punisher, Vantage Connection (Marvel Rivals) | sets up a zipline to high ground |

**Ours:**
- The fennec, already.
- **The cobra:** an Ice Path-style wall run for allies would turn its wall-slither into a team route. Proposal.

### Zones that change the rules
| Example | Structure |
|---|---|
| Kindred, Lamb's Respite (LoL) | no one inside can die for a few seconds |
| Bard, Tempered Fate (LoL) | everything in the area is frozen in time |
| Baptiste, Immortality Field (Overwatch) | allies inside can't die |
| Kelvin, Frozen Shelter (Deadlock) | a dome that heals allies and slows enemies |

**Ours:** the tortoise (time-preservation). One rule-changing zone in the roster is enough.

### Giant summons and projections that sweep a wide area
| Example | Structure |
|---|---|
| **Ornn, Call of the Forge God (LoL, checked)** | a summon charges toward the caster; the caster redirects it |
| Hanzo, Dragonstrike (Overwatch) | a dragon spirit flies down a long line through walls, hitting everyone it passes (*corrected 2026-11-12:* the game's text says one spirit, not two) |
| Grey Talon, Guided Owl (Deadlock) | he rises and steers a giant spirit owl into a target |
| Hecarim, Onslaught of Shadows (LoL) | charges with a line of spectral riders beside him |
| Poseidon, Release the Kraken! (SMITE 2) | summons the Kraken on an area: damage and slow, plus a stun and knock-up in the centre |
| Kukulkan, Spirit of the Nine Winds (SMITE 2) | a delayed projectile that throws the enemies it hits (*corrected 2026-11-12:* said a tornado down a lane, which is SMITE 1 memory) |
| Elsa Bloodstone, Apex Predator (Marvel Rivals) | her monster pet charges through the fight, grabs the enemies it hits and carries them along |
| Squirrel Girl, Unbeatable Squirrel Tsunami (Marvel Rivals) | a stampede that hunts enemies and turns when it hits a wall; it can be shot down |
| Nautilus, Depth Charge (LoL) | a shockwave travels underground to the target, knocking up everyone on the way |

**Ours:**
- **Bison or rhino:** none. The Ornn structure is not wanted (section 1, superseded), and the bison no longer
  charges.
- **Wolf:** Hecarim's spectral line, or Hanzo's travelling spirit. The giant spectral wolf head in the kit design doc.
- **Falcon:** Grey Talon's steered owl. **A better falcon ult than the wing shadow:** it rises and steers a giant ion
  falcon. Proposal.
- **Shark:** Poseidon's rise-from-below. A giant shark breaching under enemies, then dragging them along its current.
- **Pistol shrimp:** Nautilus's travelling shockwave. The cavitation bubble that travels to a point and bursts.

### Grab, carry and slam
| Example | Structure |
|---|---|
| Sett, The Show Stopper (LoL) | carries one enemy and slams them; everyone around the landing is hit |
| Lash, Death Slam (Deadlock) | lifts every enemy in range, then slams them |
| Sigma, Gravitic Flux (Overwatch) | lifts an area, then drops it |
| Jeff the Land Shark, It's Jeff! (Marvel Rivals) | burrows, rises under a large area and swallows every ally and enemy in it, then spits them out somewhere else, together or one side at a time; allies heal inside, enemies take damage |
| Fenrir, Ragnarok (SMITE 2) | his next basic attack grabs an enemy god and carries them anywhere |
| Boris, Ursine Burst (Predecessor) | dashes, grabs the first hero he hits, leaps and slams them |
| Grux, Stampede (Predecessor) | after a delay, dashes and drags enemy heroes along the path |

**Ours:**
- The rhino's carry, built.
- **The shark:** the Jeff structure (swallow and swim) is a shark already. Move it carefully; the rhino owns the carry
  today. Jeff also heals the allies he swallows, so it is a rescue as well as a kidnap.
- **The lobster's gravity well:** the Lash structure (lift many, slam).

### Jumps across the map
| Example | Structure |
|---|---|
| Galio, Hero's Entrance (LoL); Muriel, Reversal of Fortune (Predecessor, checked) | flies to an ally far away and lands with a knock-up or shield; Muriel's has infinite range and does both |
| Pantheon, Grand Starfall (LoL); Thor, Anvil of Dawn (SMITE 2) | goes up out of view and crashes down far away; Thor picks the landing spot from the air and stuns where he lands (the camera lift is memory) |
| Shen, Stand United (LoL) | shields an ally anywhere and teleports to them |

**Ours:** the fennec's great gate does the team version. The falcon could take the personal version.

### Map-wide effects
| Example | Structure |
|---|---|
| Nocturne, Paranoia (LoL) | darkens every enemy's vision across the map, then dives |
| Twisted Fate, Destiny (LoL) | reveals every enemy, then teleports |
| Karthus, Requiem; Soraka, Wish (LoL) | hits or heals everyone on the map |

**Ours:**
- **Chameleon:** Nocturne's darkness fits a cloaking body. The enemy team's vision shrinks for a few seconds.
- **Squirrel's Broadcast:** a map-wide relay ping is the Twisted Fate version.
- Both proposals.

### Shuts down movement
| Example | Structure |
|---|---|
| Poppy, Steadfast Presence (LoL) | stops enemy dashes near her |

**Ours:** the lobster's "grounded" at full weight, the same idea placed on a target.

### Stances and forms
| Example | Structure |
|---|---|
| Hel's light and dark (SMITE 2, checked in the game files: her orb deals Decay damage in one stance and Restoration healing in the other); Ramattra's Nemesis Form (Overwatch) | one button swaps the whole kit |
| Ullr, Wield Axes / Wield Bow (SMITE 2); Wukong (Predecessor) | swaps between two stances; Ullr's abilities in one stance cut the other stance's cooldowns |
| Winston, Primal Rage (Overwatch); Hulk (Marvel Rivals) | the ult turns the hero into a bigger form; Hulk chains it twice: Bruce Banner's ult makes the Hulk, and the Hulk's ult makes Monster Hulk for 12 s with double health and a new ability |

**Ours:** the scorpion's siege stance. A machine "transforming" fits mechs better than gods: plates opening,
reconfiguring. Keep it for one ult at most.

---

## 3. What the third-person games teach about our camera
SMITE, Paragon/Predecessor and Deadlock (third person) and Overwatch (first person) already solved our camera
problem. League's top-down view did not need to.
- **Ultimates speak to the whole map.** In Overwatch an ult announces itself with a voice line both teams hear. Ours:
  a map-wide sound per ult, plus an arrow at the screen edge.
- **Big moves happen above head height**, so they read over walls and through a crowd: Hanzo's dragons, Grey Talon's
  owl, Thor's leap. A giant summon is a natural fit for a chase camera.
- **Ground markers are tall and coloured by team.** Flat decals don't read at a low angle.
- **The long telegraph is the fairness.** Ornn's ram and Hanzo's dragons are strong because you see them coming. A
  chase camera shows things coming toward you even better than top-down does.

## 4. What this changes in the kit design doc
- The hippo's giant jaws are gone (Preston: "I don't think it fits with hippo"). Vent at a full flask is a pushback
  blast for now.
- The fourth giant projection goes to the Ornn structure, on the bison or the rhino: his pick.
- New proposals here, none applied:
  - Ornn's pillar for the rhino;
  - a team wall run for the cobra;
  - a steered giant falcon;
  - a shark that breaches from below;
  - map-wide darkness for the chameleon;
  - the overpressure risk for the hippo's flask.
