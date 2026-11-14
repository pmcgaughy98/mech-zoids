# Kangaroo combat and hop references (web and GitHub scan, 2026-11-10)

Asked by Preston: SMITE would not open, so scan the web and GitHub for anything that skills us up on exactly what
the kangaroo needs. Not only SMITE: Paragon, other MOBAs, and general things he may not know about.

Kangaroo-3d session. 6 searches and 4 page reads through Firecrawl. No video was watched and no game file was
opened. Nothing here has been built yet.

## 1. What was read

"Read" means the page was fetched today and its text extracted by Firecrawl's question mode. That is a summary by a
tool, not me reading every line, so check a number at the source before treating it as exact.

| # | Source | Status | What it gave |
|---|---|---|---|
| 1 | [SMITE wiki, Ravana](https://smite.fandom.com/wiki/Ravana) (SMITE 1 page, god released 2015-06-30) | read | Kit and basic attack chain, below |
| 2 | [League wiki, Sett](https://wiki.leagueoflegends.com/en-us/Sett) and [Basic attack](https://leagueoflegends.fandom.com/wiki/Basic_attack) | search excerpts only | Alternating left and right punch with unequal timing |
| 3 | [Epic: Paragon content released free](https://www.unrealengine.com/paragon) | read | 39 heroes with animations, animation blueprints, effects and sound |
| 4 | [eLife 2025, Thornton et al., kangaroo hopping](https://elifesciences.org/articles/96437) (open access) | read | Measured hopping data, below |
| 5 | [Jason de Heras, how third-person melee games communicate hit feel](https://www.jasondeheras.com/gamedesign/2021/4/23/how-do-3rd-person-melee-combat-games-communicate-game-and-hit-feel) | read | Attack readability and hit pause numbers |
| 6 | [GDKeys, Anatomy of an Attack](https://gdkeys.com/keys-to-combat-design-1-anatomy-of-an-attack/) | search excerpt only | Anticipation rules and the 0.25 s reaction rule |
| 7 | GitHub: [godot_ability_system](https://github.com/ligameacademy/godot_ability_system), [forge-godot](https://github.com/gamesmiths-guild/forge-godot), [souls-like third-person controller for Godot 4](https://github.com/catprisbrey/third-person-controller--soulslike-godot4) | README excerpts only | Ability and combo code structure. For the game feel lane, not this one |
| 8 | [GDC: Dreamscaper, Killer Combat on an Indie Budget](https://www.youtube.com/watch?v=3Omb5exWpd4) | found, not watched | Chapters on camera and framing, enemy animation, hit reactions |
| 9 | [SMITE God Reveal: Ravana](https://www.youtube.com/watch?v=X8XtEzcWJC4) | found, not watched | Every ability shown by the developer |

### 1a. Ravana (source 1)
- **Basic attack chain: three hits, at 0.75, 0.5 and 1.25 times normal damage and swing time.** The third hit
  cleaves (hits everything in front). So the rhythm is medium, quick, heavy.
- **Passive:** every hit from a basic attack or ability adds to a combo chain; the chain pays out a shield plus
  movement speed and power per stack. The extract mixed two sets of numbers (a cap of 3 stacks, and "reaches 8"),
  which looks like two versions of the page. Read the page before quoting either.
- **Abilities:** a punch that hits and slows everything in front (range 20, slow 2.5 s); a high kick that sends a
  shockwave and makes him immune for 1 s; fists that fly out and root the first god hit for 1.25 s, healing him;
  a leap to a spot that makes enemies there take more damage (immune to control during the wind-up and leap).
- Dash distances and animation times are not on the page. Those need video.

### 1b. Sett, League of Legends (source 2)
- Basic attacks alternate left punch, right punch. He always starts on the left, and resets to the left after
  2 seconds without throwing the right.
- **The right punch's wind-up is fixed at 12.5% of the left's** (eight times faster), with a little more range and
  bonus damage. So it plays as a slow setup then an instant snap: a one-two.
- League gives every champion a "windup percent": the share of the whole attack that comes before the hit.

### 1c. Paragon (source 3)
- Epic released 39 Paragon heroes for free: meshes, skins, **animation cycles, custom animation blueprints**,
  effects and dialogue. The page's own headline picture is Crunch, the boxing robot.
- The page says: "use them in your own UE4 projects, with no strings attached". It does not spell out other engines.
  From general knowledge (not confirmed on a page I read today): the store listing licenses Paragon content for use
  only in Unreal Engine based products.
- **What this means for us:** it is legal to install Unreal (free), add the Crunch pack, and study his punches
  there at any angle and speed, including the frame each hit fires on. It is not something to export into Godot or
  our project: the licence and our own rule (never copy a reference game's meshes, textures or animation data)
  both say no. Times, phase order and pose ideas are facts we can take; the data is not.

### 1d. Real kangaroo hopping (source 4)
16 kangaroos, 13.7 to 26.6 kg, hopping at 1.99 to 4.48 m/s. Our 3.5 m/s is inside that range.
- **Stride length does the work:** it grows 0.376 m for each extra 1 m/s. Stride frequency barely moves
  (0.10 Hz per 1 m/s).
- **Ground contact gets shorter with speed:** 34 ms less per extra 1 m/s.
- **The crouch comes from the ankle and the toe joint, not the hip or knee.** Faster hopping is more crouched,
  and most of the change is in the braking half of the ground contact. Peak ankle bend is at about 45% of contact.
- At slow speeds they walk on five "legs" with the tail down; in the hop the tail is off the ground.
- Not in the extract: the base stride frequency and contact time at a given speed. Those are in the paper's
  figures and would let me check our 2 hops a second and 0.18 s contact against real animals.

### 1e. Hit feel (sources 5 and 6)
- Readability of the animation is the base; sound, effects, shake and pause are layered on top of it.
- An attack is designed around two fixed things: when the hit lands and how far it reaches. Poses are pushed past
  real-life range so they read at speed. The hit pose is held for a few frames.
- Hit pause in Street Fighter V: light 8 frames, medium 12, heavy 15 (at 60 a second: 0.13, 0.20, 0.25 s).
  Devil May Cry 5 pauses only on heavy hits, so light hits stay fast.
- Camera shake and effect size scale with the strength of the attack.
- An attack an enemy must react to needs a wind-up they cannot mistake for another move, at least 0.25 s (a
  player's reaction time) plus the time their answer takes. A player's own basic attack can be near instant.
- Decide for every action whether it can be cancelled, and in which window.

### General knowledge, not read today
- Dota 2 documents every hero's basic attack as two numbers, attack point (time to the hit) and backswing
  (recovery after it). That is the same contract as our hit time plus clip length.
- MOBAs use far shorter hit pauses than fighting games, because basic attacks land several times a second.
- I did not look for tools that unpack SMITE's files, on purpose (see the earlier answer: its terms, the anti-cheat,
  and our no-copy rule).

## 2. Synthesis proposal (nothing here is canon)

**What the references agree on, and what it would change in the kangaroo:**

1. **The basic attack should be a short chain with unequal beats, not two equal jabs.** Ravana runs medium, quick,
   heavy; Sett runs slow, instant. Both make the rhythm itself readable, which suits a kit whose passive is called
   rhythm. Ours are two matching 0.5 s jabs today.
   - Proposal A (after Ravana): left jab 0.45 s, right jab 0.30 s, then a heavy third hit 0.75 s that swings wide.
     Ratio 0.75 : 0.5 : 1.25, the same as his.
   - Proposal B (after Sett): slow left 0.5 s, right snap 0.2 s, repeat. Resets to the left after 2 s idle.
   - Proposal C: keep the two equal jabs as they are.
2. **The full-stack kick needs a wind-up enemies can read.** It knocks back, so it is an attack people must react
   to: 0.3 to 0.4 s of leaning back onto the tail before the feet fire, and no other move may start the same way.
3. **Hit pause by weight:** none or a hair on the jabs, clearly more on the chain's last hit and the tail kick.
   The numbers and the code are the game feel lane's.
4. **The hop is in the right family.** Real hopping changes stride length, not rate, so if the kangaroo ever gets
   a speed boost the clip should stretch the hop, not spin faster. The ankle-and-toe finding supports giving the
   foot a toe hinge (still an open question for Preston).
5. **Crunch is the closest finished reference to this mech:** a boxing robot in a third-person MOBA, made by a
   large studio, legally viewable in Unreal. SMITE's Ravana is the kit reference; Crunch is the motion reference.

**Alternatives to studying Crunch in Unreal:** watch Paragon and SMITE footage instead (free, less exact: 30 fps
uploads, fixed angle), or Preston records SMITE himself once it opens again.

## 3. First slice (pick one)

**Slice 1: a three-beat basic chain (Proposal A), built from the jabs we have.**
- Left jab 0.45 s (hit 0.18), right jab 0.30 s (hit 0.11), third hit 0.75 s (hit 0.32) as a wide hook. All start
  and end on the idle's first frame, same events format.
- Headless check: each fist is still travelling forward at its hit time; the three lengths hold the 0.75 : 0.5 :
  1.25 ratio; toes and tail pad stay within 1 mm; gloves stay out of the body (clearance.py); a side-by-side video.

**Slice 2: measure real footage first.** Run the watch skill on the Ravana reveal (source 9) and one Crunch
gameplay video, pull the frame times for each punch and ability, and add them to this doc. Then build Slice 1 from
measured beats instead of the wiki's ratio.

**Slice 3: Crunch in Unreal (Preston's install decision).** Unreal Engine and the Crunch pack are free but large
(tens of gigabytes). I have not checked the exact size or your free disk space. If you install them, I read the
punch clips' lengths and hit frames straight out of the editor.

## 4. Not checked
- Whether Ravana is in SMITE 2, and whether his kit there matches this SMITE 1 page.
- The exact Paragon licence wording on the store listing.
- The kangaroo paper's base numbers (stride rate and contact time at 3.5 m/s).
- Any of the three GitHub projects beyond their README excerpts.
