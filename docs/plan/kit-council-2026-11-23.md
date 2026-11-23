# Kit council: every kit, new machines included (2026-11-23)

Preston, 2026-11-23: "/consciousness-council Think about all kits including all the mechs we recently added."
Kit design lane. Read for this: `moba-kits.md` (all 16 kits) and `roster-roles-2026-11-14.md` (the 11 pipeline
machines and the 13 proposed). Five lenses, picked to disagree: Strategist, Empiricist, Minimalist, Historian,
Contrarian.

**What the roster is today:**
- **Kits:** 16 machines in `moba-kits.md`.
- **Pipeline:** 11 more have sheets, but only the pistol shrimp has a kit.
- **Proposed:** 13 more are briefs only (owl, honey badger, beaver, bear, lyrebird, ant, octopus, albatross, axolotl,
  wood frog, firehawk, sloth, anglerfish). That makes 39 if all are made.
- **Playable in the Godot match:** roughly six machines.
  - Full or close to full: rhino, gorilla, hippo, bison, kangaroo, pangolin.
  - Part built: fennec, falcon, wolf (old lunge), lobster (basic only).
  - Not built: shrimp, chameleon, cobra, and nothing is listed as built for the shoebill.
  - Bots today: blue has gorilla, fennec and bison; red has rhino, gorilla, kangaroo and cobra (plain).

## Synthesis

**Agreed by three or more lenses:**
1. **Hard control is oversupplied on paper, and the roster check undercounted it.**
   - **Stun has six owners, not four:** the rhino, hippo, bison, pistol shrimp, kangaroo and cobra. The check missed
     the kangaroo's tail kick into a wall (1.2 s) and its guard counter (0.6 s), and the cobra's Hood Gaze. Fixed in
     `moba-kits.md`.
   - **The 16 kits carry about 20 hard-control effects:** stuns, roots, holds, a taunt, a charm, a knock-up and
     grounded. That's my count from the kit text.
   - **Nothing in the roster shortens or removes a stun.** The gorilla's hex shield clears a slow or a root only. The
     honey badger, as briefed, shortens grabs, pulls, chains and roots, not stuns.
2. **The design is far ahead of the build.** About six machines play, and none of the numbers have been tuned in
   play. Every judgement about balance is still a paper judgement.

**The core tension:** wide or proven.
- **Wide:** the roster's breadth is the game's identity and the fun part for Preston. Kit paper costs little.
- **Proven:** a small set should be made to play well before more pile on, because every new kit adds overlaps that
  can only be judged in play.
- The Contrarian's split resolves part of it: paper is cheap, 3D clips and engine time are not. So **gate the art and
  engine time, not the drafting.**

**The blind spot:** who feels the control.
- The match is one human against bots.
- A bot doesn't mind being chain-stunned; Preston does.
- So "too much control" only shows up as how often *his* machine can't act. No lens asked for that number, and
  nothing measures it today.

**Recommended path:**
- **Measure before adding.** Before the next kit draft (the shark is next in the order), have the bot match log how
  many seconds per minute the player's machine can't act, broken down by source.
- **Until that number exists:** new kits add no new stun owner. They take soft control (slows, displacement, zones)
  or answers to control.
- **One system rule worth drafting:** a short window after a stun ends in which the next stun is shortened. It covers
  all six owners at once, where a counter machine only helps the team that picks it.

**Confidence:** medium. The control count is a fact from the kit text. Whether it's too much in play is untested.

**A question to sit with:** when you lose a fight in this game, what do you want to feel you did wrong? If the
answer is "I got caught", the catch-heavy roster is the identity and it needs fair tells. If it's "I spaced badly",
the roster needs more ways out.

## The five lenses

### Strategist (team fights, counters, order of moves)
- **Position:** the roster is built for engage, and the answers to engage are thin.
- **Reasoning:**
  - 13 of 16 machines have a dash, leap or blink.
  - Three tanks now each limit mobility in their own way: the rhino grounds; the bison's chain lets a dash go only as
    far as its slack; the lobster's third ring halves a dash away from it.
  - Engage is everywhere: five catchers and six stun owners. Disengage is the gorilla's dome and shield, the fennec's
    gates, the lobster's Anchor and the hummingbird's surge line.
- **Key risk:** fights are decided by who lands the first catch. Everything after that is cleanup.
- **Surprising insight, a combo-order question on the rhino:**
  - Tremor charge's finale and Aftershock both spend Seismic charge.
  - The kit's own engage line ("Tremor charge in, then Aftershock the group") means the Aftershock after a charge
    always fires at base, with no full-charge stun.
  - That can be a real choice (a big finale or a big wave), or the finale could spend only the charge banked before
    the run. Open for Preston.
- **Disagrees with:** the Historian. Counters belong in kits, as picks with a cost, not in a global rule that flattens
  every stun.

### Empiricist (what has been measured)
- **Position:** nothing in these kits has been judged in play, so most worries are guesses.
- **Reasoning:**
  - The numbers are proposals. Only a handful of machines run in the match.
  - Only Aftershock, the bison's slag and the pangolin's curve have probe numbers.
  - Telegraphed stuns (Thunderclap's flash, Piston Drop's delay, Aftershock's visible wave) may feel fair in play
    even where the count looks high.
- **Key risk:** tuning on paper. Fixing a problem the match doesn't have, and missing one it does.
- **Surprising insight:** the cheapest real test already exists. The 4 v 4 bot match plus a log of how long the
  player can't act gives a number for any kit change.
- **Disagrees with:** the Historian. Other games' lessons are hypotheses, not evidence for this one. Also the
  Minimalist: you can't know what to cut without measuring.

### Minimalist (what to remove)
- **Position:** stop widening. Make the 16 play before drafting the 23 behind them.
- **Reasoning:**
  - 39 machines is a team's output, not a solo project's.
  - Each new kit adds overlap checks: three fires, three healers, four roots, two control mages.
  - The roster-roles flags show the piles are already growing.
  - The six playable machines are the game.
- **Key risk:** drafting becomes the work. The roster grows on paper while the match stays at six machines.
- **Surprising insight:**
  - Some new briefs exist only to fix problems the bigger roster creates. The honey badger answers five catchers; the
    scorpion's anti-heal answers three healers.
  - Fewer machines means fewer patches.
- **Disagrees with:** the Contrarian, on whether paper is free. Every approved kit also creates art and engine debt
  someone is expected to pay.

### Historian (precedent; from general knowledge, not checked)
- **Position:** MOBAs that piled on stuns ended up with a global rule, not a counter character.
- **Reasoning:**
  - League has tenacity and Dota has status resistance (general knowledge, not verified here). Both are system-wide
    answers that came after control spread across the roster.
  - "Grounded" itself is a known MOBA status, used on a few champions as a light anti-dash tool, not on many.
- **Key risk:** with six stun owners and no rule, the strongest teams are just the ones that chain the most stuns.
- **Surprising insight:**
  - The honey badger is a tenacity item turned into a machine.
  - That only helps the team that picks it. A short post-stun window helps everyone and costs one rule in the
    shared code.
- **Disagrees with:** the Strategist, on kit-level counters, and the Empiricist, on waiting. Some lessons are cheap
  to borrow.

### Contrarian (challenging the most popular view, "freeze the roster")
- **Position:** don't freeze the drafting. Gate the expensive parts instead.
- **Reasoning:**
  - A kit draft is a page of text. The real bottlenecks are 3D clips, effects and one Unreal editor at a time.
  - The roster's breadth (gate tech, pass-through, cavitation, the four-layer rule) is what makes this game this game.
  - Freezing design to "prove" six machines against bots risks tuning a game nobody else has played.
- **Key risk:** a minimal roster gets balanced and boring before its identity is set.
- **Surprising insight:**
  - The control count is partly a symptom of the rule that every machine gets one animal trait and a power theme.
  - Stuns are the default verb when a theme has no better one. Wolf, falcon, squirrel and fennec found other verbs
    (hunt, range, relay, gates), and none of them stuns.
  - So the fix is better verbs in new kits, not fewer kits.
- **Disagrees with:** the Minimalist, on freezing, and the Historian, on a global rule that would blunt the rhino's
  identity as the stun owner.

## Findings from the read
- **Roster check undercount:** fixed in `moba-kits.md` ("Roster checks"). Stun has six owners: rhino, hippo, bison,
  pistol shrimp, kangaroo and cobra.
- **No answer to stuns anywhere in the roster:**
  - The hex shield clears a slow or root.
  - The honey badger brief covers grabs, pulls, chains and roots.
  - Lobster Anchor stops displacement, not stuns.
- **The rhino's Seismic charge spend order** (Strategist above). Not decided. It's for Preston.
- **Three anti-mobility tanks** (rhino grounded, bison chain slack, lobster rings) against 13 mobile machines. Not a
  problem yet, but a fourth would be.

## The measurement (asked 2026-11-23)
Preston: "Yes, ask game feel". Sent to the game feel lane the same day. The request:
- In the Godot bot match, on the player's machine only: seconds per minute it can't act.
- Split by kind and by source (machine and slot), with overlaps counted once and the longest unbroken lock recorded.
- Grounded and slows on separate lines.
- A few runs on two or three player machines.

Measurement only, no kit changes. Until the number exists, new kits add no new stun owner.

## Not checked
- The control and mobility counts are mine, from the kit text. They aren't from the code.
- The Historian's precedents (League tenacity, Dota status resistance, grounded in League) are from general
  knowledge and weren't verified.
- Nothing here was played.
