# How finished games and films animate animal-shaped machines (structural reference for a 2D gorilla war machine)

Scope note: everything below is structure and technique only. Nothing here is a recommendation to copy any Zoids or Takara Tomy design, name or asset. Zoids material is cited only to describe what the battle screen does mechanically.

Research conditions: WebSearch and WebFetch hit a session limit partway through, so most pages were pulled with Firecrawl and curl, and one sprite sheet was downloaded and inspected directly. Pages that could not be opened are listed under Gaps.

## Key question 1: Zoids Legacy (GBA, 2004) and Zoids Saga battle presentation: what happens on screen during an attack turn

### Takeaway
Zoids Legacy battle Zoids are single static side-view sprites (one pose per Zoid, recoloured per palette) with no attack, hit or idle frames; the attack turn is carried by a text box, weapon and beam effects drawn over the sprite, a background animation swap for special attacks, and a roughly 3 second skippable sequence. Zoids Saga DS keeps the same shape: one 128x64 battle sprite per Zoid plus small map sprites, 16 to 48 images per sheet counting palettes and forms.

### Cited Findings
- The Spriters Resource lists 41 assets for Zoids: Legacy on GBA: 1 character sheet, 34 Zoid sheets, 4 weaponry sheets (Beam Weapons, Weaponry 1, 2, 3) and 2 miscellaneous (intro logos, text). The game is tagged "Perspective: Bird view / Isometric" and "Perspective: Side view". — [The Spriters Resource, Zoids: Legacy](https://www.spriters-resource.com/game_boy_advance/zoidslegacy/)
- The Blade Liger sheet is a 399x539 PNG; its asset page shows "Animations (0)". I downloaded and inspected the sheet: it holds 8 tiny overworld sprites (one per colour palette) and 8 large battle sprites, each a single static side-view standing pose recoloured per palette. There are no walk, attack, hit or idle frames on the sheet. — [The Spriters Resource, Blade Liger sheet](https://www.spriters-resource.com/game_boy_advance/zoidslegacy/asset/13490/)
- Weapon effects are ripped as separate sheets ("Beam Weapons", "Weaponry 1-3"), which means the firing visuals are overlays, not part of the Zoid sprite. — [The Spriters Resource, Zoids: Legacy](https://www.spriters-resource.com/game_boy_advance/zoidslegacy/)
- Giant Bomb: combat is turn-based, up to six Zoids per side (twelve on screen), the player picks battle commands for everyone, and "when all the attack commands are confirmed players are awarded with a neat animation of the actions." The page carries a screenshot captioned "An example of attack animation." — [Giant Bomb, Zoids: Legacy](https://giantbomb.com/wiki/Games/Zoids_Legacy)
- GameFAQs guide (link battle section): after a player selects a move for a Zoid "it takes about 3 seconds for the game to respond" per Zoid turn, and "The battle animation can still be 'skipped' with the 'B' button." — [GameFAQs, Zoids: Legacy guide](https://gamefaqs.gamespot.com/gba/918731-zoids-legacy/faqs/34699)
- Same guide: Deck Command attacks (Arrow Phalanx, Thor Hammer Phalanx, Cannon Phalanx) "will also have a background animation change"; a pilot's Combat Specialty skill means "A background animation will activate when using a Combat Weapon"; switching CAS armour forms in battle "uses up an action phase, but has animation"; tips section: "In combat animation, press 'B' to skip animation." — [GameFAQs, Zoids: Legacy guide](https://gamefaqs.gamespot.com/gba/918731-zoids-legacy/faqs/34699)
- A Reddit bug report describes the game getting "stuck on the 'take this' animation" after selecting a weapon and hitting decide, which confirms an attack sequence that starts with a pilot line text box before the hit resolves. — [Reddit r/Zoids, Zoids legacy attack loop](https://www.reddit.com/r/Zoids/comments/1gpm4ig/zoids_legacy_attack_loop_in_one_location/)
- Wikipedia on the Zoids Saga series: "Combat is turn-based, and occurs on two opposing two by three grids, one for the player, the other for the enemy." Zoids: Legacy is Zoids Saga II with "no changes to the gameplay." In Saga II a fused Unizon Zoid "only got one attack per turn cycle." — [Wikipedia, Zoids Saga](https://en.wikipedia.org/wiki/Zoids_Saga)
- Zoids Saga DS ripping project (VG Resource): each Zoid folder holds image, map and palette files for the main sprite plus a separate "cz" sprite that is displayed at "Width: 128 and Height: 64"; a finished sheet holds "16 to 48 total" sprites once all palettes are included. A later post notes "The only difference between the two W Victory Liger sprites is the zoid being grounded/aerial," and sheets could be auto-built by script, which only makes sense if each Zoid is a small fixed set of poses rather than animation strips. — [The VG Resource, Zoids Saga DS Ripping Project](https://archive.vg-resource.com/thread-25709.html)
- Zoids VS (GameCube) is a different genre: "free-roaming third person combat, where the player rides around in the titular Humongous Mecha, running and gunning in large open" arenas. — [TV Tropes, Zoids VS](https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/ZoidsVS); the Zoids Wiki adds that players customise Zoids and each "Zoid features a special attack." — [Zoids Wiki, Zoids VS](https://zoids.fandom.com/wiki/Zoids_VS)
- A GameFAQs Zoids: Battle Legends guide refers to firing a rifle "in the Iron Kong's faces" and using "melee attacks to stun one of them if you have it cornered," confirming melee stun and ranged attacks as separate verbs in the 3D Vs. games. — [GameFAQs, Zoids: Battle Legends guide](https://gamefaqs.gamespot.com/gamecube/924420-zoids-battle-legends/faqs/39267)

### Inferences
- The Legacy attack turn is therefore: command phase for all units, then a per-unit sequence of roughly 3 seconds: pilot text line, weapon/beam overlay drawn from the attacker toward the target, optional background swap for specials, damage number, next unit. Since the Zoid sprite has no frames, any apparent motion must come from sprite offset (slide/jolt), palette flash, or overlays. This matches how the sheets are organised (Zoids separate from Weaponry).
- Scale: a battle Zoid in Legacy is roughly the size of the large sprites on the 399 px wide sheet (two per row, so under about 190 px wide at native GBA resolution, likely closer to 96 to 128 px). Zoids Saga DS uses a 128x64 cell for its battle sprite. A gorilla mech drawn in a 128x96 or 128x128 cell would be in the same family.
- The design freedom for the new game is that even two or three extra frames per state (idle breathe, attack anticipation, hit jolt) would exceed what these games did, because they did it with zero.

### Gaps
- I could not open the Zoids Legacy manual PDF (gamegear.net) or watch the RPG Quest gameplay videos, so the exact order of the attack sequence (text, flash, overlay, damage) is inferred from the guide and the bug report rather than observed frame by frame.
- No source gave frame counts or durations for the Legacy hit flash or screen shake, or confirmed whether the attacker sprite physically slides during a melee attack.
- Zoids Saga DS: I confirmed the sprite cell size and the fact that sheets are static poses, but found no description of what the DS battle screen plays between poses.

## Key question 2: Iron Kong (Zoids) as a heavy gorilla mech: how it is staged walking, punching, firing and taking hits

### Takeaway
The published descriptions of the Iron Kong frame it as thick-armoured, slow-running but nimble, with missile fire from outside enemy range and punches whose power comes from the mass of its hands; a booster variant adds short position shifts and long leaps. In the anime it is mostly staged as armoured fodder that gets dispatched in one blow unless a named pilot is in it.

### Cited Findings
- "The Iron Kong features thick armour invulnerable to most of smaller Zoids' weaponry. Additionally, the Iron Kong's load of long-range missiles allowed it to attack from outside the range of most of its opponent's weapons." — [Zoids Wiki, Iron Kong](https://zoids.fandom.com/wiki/Iron_Kong)
- "While its running speed is relatively slow, the Iron Kong's proportions and sturdy construction make it extremely nimble for such a heavy Zoid. Additionally, the gorilla-like form and fully functional hands allow it to climb or grasp objects. The sheer mass of its hands make punching attacks particularly devastating." — [Zoids Wiki, Iron Kong](https://zoids.fandom.com/wiki/Iron_Kong)
- The MK-2 variant's back thruster "allows the Zoid to suddenly shift its position, enhancing its speed and agility, while allowing the Zoid to make long, booster-assisted leaps." — [Zoids Wiki, Iron Kong](https://zoids.fandom.com/wiki/Iron_Kong)
- Anime staging: Iron Kongs "were often rather easily disposed of"; in New Century the Backdraft elite guard's Iron Kongs "were quickly dispatched by the Fuma Team's Warsharks in a single blow"; in Fuzors "nine Iron Kongs proved unable to damage the Gairyuki Destroy." — [Zoids Wiki, Iron Kong](https://zoids.fandom.com/wiki/Iron_Kong)
- In the GameCube Battle Legends guide, enemy Iron Kongs are fought with long-range rifle fire to the face and melee attacks that "stun" them when cornered. — [GameFAQs, Zoids: Battle Legends guide](https://gamefaqs.gamespot.com/gamecube/924420-zoids-battle-legends/faqs/39267)

### Inferences
- Structurally the Iron Kong reads as a two-mode fighter: a static artillery mode (shoulder missiles fired from a planted stance) and a short-range mass mode (punch, grab, climb). An animation set for a gorilla war machine should keep those two modes visibly different: firing with the feet planted and recoil through the torso, melee with the whole body shifting weight forward.
- The "slow running but nimble" description is the classic heavy-character contract: long anticipation, short burst, long settle. The booster leap is the one allowed fast beat.

### Gaps
- I found no shot-by-shot breakdown of an Iron Kong walk, punch or hit reaction in the anime (no animator interview, no frame analysis). The staging notes above are from a fan wiki summary, not a primary animation source.
- No Zoids Vs. sprite or model-animation list (state names, frame counts) was found.

## Key question 3: Horizon Zero Dawn and Forbidden West machine animation: weight, mechanical secondary motion, readable telegraphs

### Takeaway
The primary source is Richard Oud's GDC 2018 talk "Animation Bootcamp: Bringing Life to the Machines of Horizon Zero Dawn", which covers reference, motion style, workflow, animation tech and AI behaviour; summaries confirm the goal was believable beast movement from the player's view, but I could only reach the summaries, not the talk's specific timing or telegraph rules.

### Cited Findings
- Richard Oud, lead animator at Guerrilla Games, gave the GDC 2018 talk; it "discussed their production workflow, covered the technical side of animation, the creation of believable beasts' movements from the players' view," and showed "the biggest challenges they have faced." Video: https://www.youtube.com/watch?v=50mIKB-NACU — [80.lv, Horizon Zero Dawn: Beasts Animation Production](https://80.lv/articles/horizon-zero-dawn-beasts-animation-production)
- Session description: Oud "explains the process from pre-production and prototyping, all the way to the final polish of the characters, reference, motion style, workflow, animation-tech and AI behavior." — [Game Anim, Bringing Life To The Machines Of Horizon Zero Dawn](https://www.gameanim.com/?p=46152)
- GDC Vault listing for the same session. — [GDC Vault, Animation Bootcamp: Bringing Life to the Machines of Horizon Zero Dawn](https://gdcvault.com/play/1025040/Animation-Bootcamp-Bringing-Life-to)
- A separate GDC 2018 talk by Guerrilla's Julian Berteling, "Beyond 'Killzone': Creating New AI Systems for 'Horizon Zero Dawn'", focused on the navigation and animation systems that make characters move realistically. — [GDC, Get an inside look at the AI driving Horizon Zero Dawn](https://gdconf.com/news/get-inside-look-ai-driving-horizon-zero-dawn-gdc-2018)

### Inferences
- The talk's own outline (reference, motion style, animation tech, AI behaviour) implies the Guerrilla method is: pick a real animal reference per machine, define a motion style for the machine family, then let AI behaviour drive which clips play. For a sprite game, the equivalent is choosing one real animal reference for the gorilla machine and deciding a motion style sentence (for example "slow to start, violent at contact, long to settle") before drawing frames.

### Gaps
- I could not reach the talk transcript or slides, the PlayStation Blog Fireclaw article (the URL now 404s), or any Forbidden West animation talk, so I have no cited detail on Horizon's specific weight cues, mechanical secondary motion, or attack telegraph timing. The YouTube talk above is the thing to watch.

## Key question 4: Transformers games and films, Beast Wars and Optimus Primal: what makes a beast-form robot read as heavy machinery rather than rubber

### Takeaway
Weta FX's animation supervisor on Rise of the Beasts says the robotic gorillas used the same principles as their organic apes, but rigid surfaces removed all "fleshy" give, so the shoulders (single rigid domes) had to be disconnected from arms and neck and re-posed shot by shot, and the faces were driven by a hidden human face rig under hundreds of rigid plates.

### Cited Findings
- Kevin Estey (Weta FX animation supervisor): "The principals are the same but the mechanics, quite literally, of a robotic ape are much trickier. Gorillas ... are bulky but very agile and flexible. One main challenge about robotic creatures is that flexibility is tricky, particularly due to the rigidity of their surfaces." — [TFW2005, Interview With Weta FX On VFX For Transformers: Rise Of The Beasts](https://news.tfw2005.com/2023/07/03/interview-with-weta-fx-on-vfx-for-transformers-rise-of-the-beasts-488860)
- "The most challenging aspects of these two primate characters were their shoulders and their faces. Their shoulders are the most prominent feature of their bodies and are visible in most shots ... Because the shoulders were formed from single rigid metallic domes, there was no room for faking malleability. As a result, we had to essentially disconnect them from the arms and neck to manipulate them appropriately, given each type of action." — same source
- "In many situations, this was a cheat to give the impression of them being 'fleshy' when in fact they were largely disconnected from the surrounding appendages." — same source
- Faces: Weta "used our GENMAN human face as an underlying driver for the rigid primate faces ... covered in hundreds of individual pieces that form the exterior face." — same source
- Weta came onto the film in August 2022 after principal photography, alongside MPC as main vendor. — same source
- Full interview is at Art of VFX (not fetched): https://www.artofvfx.com/transformers-rise-of-the-beasts-matt-aitken-overall-vfx-supervisor-mike-perry-vfx-supervisor-and-kevin-estey-animation-supervisor-weta-fx/

### Inferences
- The transferable rule: a machine reads as machine when its plates do not stretch. Weight has to be shown by the whole rigid mass moving (shoulders rising as a unit before a punch, torso settling after a step) and by independent sub-parts (shoulder domes, chest plate, jaw) moving on their own slightly later than the core. In pixel art that means never squashing the body outline; instead offset plates by a pixel or two on anticipation and settle frames.
- "Rubber" is what happens when the silhouette bends. "Machinery" is what happens when the silhouette stays rigid and joints rotate.

### Gaps
- Nothing concrete was found on War for Cybertron / Fall of Cybertron animation methods (the Firecrawl search for it hit a 429 rate limit), nor on Beast Wars (1996 CG series) animation technique. No source on Transformers film animation beyond the Weta interview above.

## Key question 5: Other respected gorilla and ape characters (Donkey Kong Country, Winston, Kong in film): idle, walk, charge, punch, slam, chest-beat, with timing where described

### Takeaway
Film Kong (ILM, 2017) is the richest timing source: a 100 ft biped is kept slow in wide shots because audiences expect heavy mass to take time to change direction, and fast only in close-ups; landings must show compression and a place for the mass to be absorbed before any new direction. DKC's Donkey Kong was pre-rendered in 3D and then frame-thinned (a 16-frame walk cut to every other frame) to fit the SNES. Winston was one of Overwatch's hardest characters to animate because of his many armour pieces and because his rage mode changes his movement animation.

### Cited Findings
Kong: Skull Island (ILM)
- Scott Benza (ILM animation supervisor): "With a character that's 100 feet tall, if it was actually moving in a way that was physically plausible, it would be a very slow-moving kind of uninteresting thing to look at. If Kong was really close to camera we felt like we could get away with a faster moving performance." The opening hand-plant "is probably moving at 80 or 90 miles an hour, but given the scale of it and the fact you only see the hand, we found that you could get away with that speed." — [Cartoon Brew, Why the Character Animation in 'Kong: Skull Island' Was Done Differently Than You Think](https://www.cartoonbrew.com/feature-film/character-animation-kong-skull-island-done-differently-think-149202.html)
- In wide shots speed was dialed down because audiences "are so used to seeing heavy objects in motion that take a long time to change direction. Say he was jumping down from a large altitude, for instance, we would really need to sell the compression and give a place and time for all of that mass to go and be absorbed before it could resolve itself and go a different direction." — same source
- Third Floor previs supervisor Mark Nelson: "we spent a good deal of time working out how fast he would move, how upright he would walk and how he would fight ... Too fast and he would look small, too slow and the action wouldn't be that exciting." — same source
- Kong was keyframed, not motion captured; Terry Notary's body capture and Toby Kebbell's facial studies "did inform the final animation," but a side-by-side test had the director prefer the keyframed version. — same source; fxguide adds the capture was "used for inspiration, but given the huge re-targeting from a 6 ft man to a 100ft Kong we did not use the motion capture directly." — [fxguide, ILM creatures on Kong's Skull Island](https://www.fxguide.com/fxfeatured/ilm-creatures-on-kongs-skull-island/)
- Kong "walks as a biped" and spends "little to no time on all fours," by design referencing the 1933 film. — [fxguide](https://www.fxguide.com/fxfeatured/ilm-creatures-on-kongs-skull-island/) and [Cartoon Brew](https://www.cartoonbrew.com/feature-film/character-animation-kong-skull-island-done-differently-think-149202.html)
- fxguide: "Getting scale is an issue, large things should move slowly which is very hard in an action film." The roar "was hand animated." The director's design mandate was that creatures be drawable by a ten-year-old, with silhouettes "so distinct" they are recognisable from a sketch. — [fxguide](https://www.fxguide.com/fxfeatured/ilm-creatures-on-kongs-skull-island/); [Cartoon Brew](https://www.cartoonbrew.com/feature-film/character-animation-kong-skull-island-done-differently-think-149202.html)
- Rosenbaum's favourite shot: Kong "leaping from a tall rock peak, holding a large boulder over his head, descends to whack the Skull Crawler in the head. The graphic body pose illustrates his athletic superpower." — [fxguide](https://www.fxguide.com/fxfeatured/ilm-creatures-on-kongs-skull-island/)

Donkey Kong Country (Rare, 1994)
- Steve Mayles built DK in 3D (Alias PowerAnimator on Silicon Graphics) and rendered the model down to sprites; Chris Sutherland then thinned frames to fit the SNES: "If I handed Chris Sutherland a disk with a 16-frame walk animation, he'd probably only use every other frame." — [Episodic Content, Kings of the Jungle: The Making of Donkey Kong Country, Chapter 2](https://episodiccontentmag.com/2016/02/19/dkcountry1_chapter2/)
- Genesis Aladdin's Disney-animator work was the animation benchmark the team measured against. — same source
- DK's Hand Slap / ground slap exists as a distinct move; the Donkey Kong wiki lists his weight as 800 lbs. — [Donkey Kong Wiki](https://donkeykong.fandom.com/wiki/Donkey_Kong)

Winston (Overwatch)
- "Winston was one of the hardest characters to animate due to the numerous armor pieces he wears. His rage mode also presented problems due to the changes in movement animation." — [Overwatch Wiki, Winston](https://overwatch.fandom.com/wiki/Winston)
- Timing details from the same page: after Jump Pack, a melee right before landing cancels the melee animation while damage still applies, and Winston "still is unable to use his Tesla Cannon until 0.5 seconds after he used the melee attack"; Jump Pack landing damage "increases while in the air, up to 250% more damage over 2.5 seconds." — [Overwatch Wiki, Winston](https://overwatch.fandom.com/wiki/Winston)
- Blizzard's hero page: Primal Rage grants "immense health, but you can only leap and punch enemies." — [Blizzard, Winston hero page](https://overwatch.blizzard.com/en-us/heroes/winston)

### Inferences
- A sprite-scale version of the ILM rule: the gorilla machine's walk and hit reactions should use more frames (or longer holds) than smaller units, and only the strike itself may be fast. Landings and slams need a visible compression frame followed by a held settle frame before the next action starts.
- Rare's workflow (animate at 16 frames, ship every other frame) is a cheap production trick: draw or generate the walk at a higher count, then thin to 8 while checking that the contact poses survive.
- Winston's armour problem is the same as Weta's shoulder-dome problem: rigid plates must be tracked as separate layers. In 2D that argues for a parts-based sprite (torso, shoulders, arms as separate pieces) rather than one redrawn silhouette per frame, if the tooling allows it.

### Gaps
- No frame counts or timings were found for DKC's idle, roll or hand-slap, Winston's punch cycle or chest-beat, or Rampage's George. The DKC idle-animation evolution video (https://www.youtube.com/watch?v=mRI0xAqU_eo) exists but was not watched.
- No Dan Floyd / New Frame Plus style breakdown of a gorilla character was located within the call budget.

## Key question 6: Common turn-based RPG battle animation structure for monster sprites (Pokemon, Final Fantasy, Digimon, GBA Fire Emblem): frame counts, sprite offset and screen shake instead of frames, hit flashes

### Takeaway
Classic turn-based games animate static monster sprites with effects, not frames: Gen I Pokemon ends a move animation by shaking the screen or flashing the target picture; SNES Final Fantasy enemy sprites "just flash and don't really move" while the small party sprites animate; GBA Fire Emblem is the frame-rich exception, with a full per-weapon set (attack, crit, ranged attack, ranged crit, dodge, miss) at 248x160 per frame, projectiles and screen scroll handled by the engine rather than drawn.

### Cited Findings
- Pokemon Red/Blue disassembly: the move-animation routine ends by calling a function that either shakes the screen or flashes the attacked Pokemon's picture in and out to show damage. — [pokered disassembly mirror, engine/battle/animations.asm](https://v10.next.forgejo.org/foster/pokered/src/commit/4a8c9993ad182296131ef87111e1b6d6e2af4201/engine/battle/animations.asm)
- Bulbapedia's Gen I animation index notes some special effects are applied to either or both Pokemon in battle, or to the whole screen, and often share palettes with the affected Pokemon. — [Bulbapedia, List of battle animations by index number in Generation I](https://bulbapedia.bulbagarden.net/wiki/List_of_battle_animations_by_index_number_in_Generation_I)
- Final Fantasy (SNES era): "Chibi sprites are much easier to animate. Notice how the detailed enemy sprites just flash and don't really move." — [Reddit r/FinalFantasy, why are the sprites for characters in battle chibi](https://www.reddit.com/r/FinalFantasy/comments/4zrtsp/in_older_ff_games_why_are_the_sprites_for/) (community observation, not a developer source)
- GBA Fire Emblem battle animations: a melee weapon needs "a melee attack and critical hit, a ranged attack and critical hit, a dodge, and a miss animation (usually a copy of the normal attack)" per weapon type; magic and bows need attack, crit, dodge, miss; "Each image should be 248 pixels wide by 160 pixels tall" with a 16-colour palette; "You should not draw the projectile itself flying across the screen for a thrown weapon - it gets added automatically in the game" and "the game handles the screen scrolling during ranged attacks automatically." The scripting uses command codes (for example "C03 #Start attack animation"). — [GBA FE battle animation tutorial](https://fe-battle-animations.neocities.org/)
- RPG Maker screen-shake plugins (Aries of Sheratan) attach shake to a chosen battle-animation frame, with strength and speed as separate parameters and a duration; the default RPG Maker shake is described by a competing plugin as "simple random horizontal movement." — [Yanfly wiki, Shake Screen Effects (Aries of Sheratan)](https://www.yanfly.moe/wiki/Shake_Screen_Effects_(Aries_of_Sheratan)); [LUX ScreenShake](https://luxferra.itch.io/advanced-screenshake-for-rpg-maker-mv-and-mz)
- Zoids Legacy itself belongs to the static-sprite family (see question 1): no frames, overlays and background swaps instead. — [The Spriters Resource, Blade Liger sheet](https://www.spriters-resource.com/game_boy_advance/zoidslegacy/asset/13490/)

### Inferences
- The minimum viable state set for a static-sprite RPG is: one idle pose, a palette flash (2 to 4 alternations) for hits, an x-offset jolt for the defender, a screen shake tied to the impact frame, and overlay effects for the weapon. Everything in the genre above this is optional.
- A reasonable next tier (what a gorilla machine would need to feel heavier than the genre baseline): idle with 2 to 4 frames of slow breathing or hydraulic settle; attack split into anticipation (held), strike (1 to 2 fast frames), and recovery (held); a dedicated hit frame instead of only a flash; a victory pose with one chest-beat loop. The GBA FE list (attack, crit, dodge, miss per weapon) is the upper bound for a 2D turn-based game and far more than Zoids-style games used.
- Keep projectiles and screen motion in code, as FE does, so the sprite set stays small.

### Gaps
- No source gave exact frame counts or durations for Gen I's shake or flash, SNES Final Fantasy's enemy flash, or GBA FE's typical attack length; the FE tutorial describes states and canvas size but I did not extract per-frame timing from it.
- Digimon battle sprite structure was not researched within the call budget.
