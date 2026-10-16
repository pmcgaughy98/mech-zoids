# Zoids Legacy's battle, read as structure (Claude, 2026-10-11)

Read for structure only, from `jmacato/ZoidsLegacyDecomp` (MIT): `src/battle/battle.h`,
`present_queued_battle_effect_results.c` and the `src/battle/deck_commands/` folder. Nothing copied: no code,
numbers, names or text. Sections marked *(read)* come from the source; the rest is labelled.

## 1. The round (read)
A battle is a fixed sequence of phases: set up, prepare the round, pick the next unit by turn order, that
unit's turn (use an item, or choose a command), carry the action out, check whether anyone has won, end the
round, then victory or defeat. Turn order is rebuilt each round from a speed-like stat. Some effects add
extra turns or remove a unit from the order.

## 2. The machines (read)
Each machine carries about ten stats: health, energy (EP) with a maximum and a regen rate, speed, mobility,
defense, armor, sensor accuracy, load capacity, and a points pool used for commands. It has a size class
(S, M, L, XL), movement flags (flying among them) and up to eight equipment slots. A machine can have several
forms, each changing its energy regen, defense and weapon power. Battle rules filter by size, by flying, and
by animal line (some fights allow only one kind of animal), so the animal kind is a real category in the
rules, not just a look.

## 3. Weapons (read)
Each weapon has a type (ballistic, missile, laser, particle, melee) plus traits: anti-air, works in water,
homing, pierces, ignores defense, damages defense, stuns the pilot, freezes, confuses. It has a range band
(0 to 3) and a target area: one machine, a column, a row, a whole side, itself. Up to six machines a side
stand in a formation, so range and area matter. "Charge energy" is its own action: you spend a turn to fill
EP for a bigger attack later.

## 4. The deck of commands (read)
Before battle the player builds a short deck by choosing from a catalog of about fifty commands. In battle a
command is played from that deck, separate from the machines' own attacks. The kinds: field hazards (mines,
storms, obstacles), shields and covering fire, buffs and recovery, tricks on the enemy (confusion, false
orders, scrambled data), swapping a machine in, and the big ones: two or more machines combining into one,
and formation attacks. Some commands need a particular pilot. A battle rule can ban commands entirely.
**The deck is built, not drawn.** There is no random hand each turn in the source.

## 5. Showing results (read)
An action's effects are queued first, then shown one at a time: camera moves to the target, then a number
pops up (damage, miss, decoy), then gauges update, then any applied or removed effect shows, then
destroyed machines are marked. Act, then show. This is what gives the battle its rhythm.

## 6. From the connectors
- **Retro Game Gather:** Zoids Legacy is the US release of *Zoids Saga II* (GBA, Tomy, 18 April 2003, RPG).
  The same family on GBA: *Zoids Saga* (2001) and *Zoids Saga Fuzors* (2004); later *Zoids Saga DS* (2005)
  and *Zoids Tactics* (PS2, 2005). Tomy also made a *Zoids Battle Card Game* (PS1, 2001): a drawn-card take
  on the same machines. That's the precedent if you want a drawn hand rather than a built deck.
- **Director's Lookbook:** two cards fit. *Candy Pop Primaries*: black, bright blue, cherry red, lemon on
  off-white, "the toy box". That's model-kit colour. *16-bit Pixel RPG*: 320x180, a small indexed palette,
  1-pixel dark outlines, no anti-aliasing. The hand it dealt first (teal and orange, oil painting) was wrong
  for this and is set aside.

## 7. The Zoids Saga family and the card game (read, 2026-10-11, Firecrawl)
Sources: GameFAQs Zoids Legacy guide by mech_gouki (`gamefaqs.gamespot.com/gba/918731-zoids-legacy/faqs/34699`),
ja.wikipedia "ZOIDS SAGAシリーズ" and "ゾイドバトルカードゲーム". The atwiki review page had no detail on these games.
- **Deck rule (Legacy):** up to 10 commands equipped before each battle; each usable once per battle; one per
  turn phase. This settles section 4: built, not drawn.
- **Formation (Legacy):** front and back rows, up to 6 a side; XL machines take the middle row; an empty front
  row pulls the back row forward. Turn order by a speed-plus-reaction value.
- **Energy (Legacy):** machines start at half energy, regain some every turn, and waiting regains extra.
- **Types (Legacy):** animal types matter through pilot skills that suit a type; flyers dodge more against
  anything that is not anti-air; flyers and swimmers ignore deep-water penalties.
- **Opening (Legacy):** home town, talk to people, out to the field, two fixed fights against small machines,
  a stranger joins for one fight, then the next town with a research lab and a battle arena contest.
- **Between battles (Legacy):** item shop, weapon shop, bar, research lab, battle arena.
- **What changed across the Japan-only entries (ja.wikipedia):** Saga II let companions fight any time and
  added repainting and tuning your machines. *Fuzors* (GBA, 2004) replaced command-based combining with
  automatic combining when the right machines are on the field, and let any machine be upgraded to its cap
  for money. *Saga DS* added a touch-screen radar for enemies, traps and items. Across the series you collect
  a wild machine's data and core to build that machine yourself.
- **Card game (ja.wikipedia):** decks of 40 to 60, die rolls decide hits, win by destroying every machine or
  the enemy base; the PS1 version made you a commander for one of two factions.

## What Preston loves (2026-10-11)
The battles; the machines' colours; many different animals; classes of animals. Animal machines like
Zoids. A deck of commands. He wants them to look very close to Zoids in animals and palette.

**Where the line is:** animal war machines, faction colour schemes, exposed mechanical joints and cockpit
heads are a genre, and fine. A specific machine's silhouette and plating (a white-and-blue lion built like
Liger Zero) is someone else's design, and copying it would also sink a store page. We aim for "you can tell
what inspired this," not "that's a Zoid."

## Synthesis proposal (for Preston; nothing here is canon)
1. **Classes = size × body.** Size S, M, L, XL (bigger means more health and more slots, but slower) crossed
   with how it moves: ground, flyer, swimmer. The animal is the line inside a class (cat, canine, raptor,
   shark, bear, beetle...), and an animal line gives a small signature trait.
2. **Weapon types as the rock-paper-scissors.** The five source types cut to four for us: melee, shell,
   missile, beam. Each class resists one and is weak to one. Flyers can only be hit by anti-air or other
   flyers' melee.
3. **Energy as the second gauge.** Every machine has health and energy. Big weapons cost energy; Charge is
   a turn spent filling it. That's the choice each turn: hit now, or charge for the big one.
4. **The deck, two ways (Preston picks).**
   *A, built (Zoids Legacy):* you pick 5 commands before battle and can play one per round on top of your
   machine's attack. Each is used once.
   *B, built and drawn (Battle Card Game precedent):* you build a deck of 12, draw 3 each round, play 1.
   More variety and more luck. START_HERE assumed this one.
5. **Act, then show.** Every action fills a result queue; the screen plays it back step by step. The
   headless check reads the same queue, so the check measures the real battle.
6. **Faction palettes.** A shared gunmetal frame on every machine, with armour plates in faction colour:
   player side white and blue, rival side red and black, yellow for lights and cockpits. Starting swatches
   from the Lookbook: `#111111 #1E90FF #FF3B3F #FFD400 #FAFAF7`, plus a grey ramp for the frame.
7. **Screen size 320x180** (Lookbook's pixel RPG card; 16:9, scales 6x to 1080p exactly). The alternative is
   240x160, the GBA's own size, which is more authentic but letterboxes on every modern screen.

Later, not in the slice: formations of up to six, combining machines, forms, pilots, parts.

## The first slice (one session, verifiable)
One battle screen, 1 vs 1. Two placeholder machines built from coloured shapes in the faction palette
(player white and blue, rival red and black), each a different class. Each has two weapons and Charge. The
deck works the way Preston picks (A or B), with four placeholder commands: a shield, a repair, a field hazard
and an energy surge. Turn order by speed. Every action goes through the result queue and plays back with a
damage number and a gauge drop. Someone wins. A headless check plays 200 seeded battles with the AI on both
sides, proves every one ends, and shows that the deck and Charge actually change who wins.
