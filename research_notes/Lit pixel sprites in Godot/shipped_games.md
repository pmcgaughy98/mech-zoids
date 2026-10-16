# How shipped games light pixel-art sprites (for a remastered GBA-style mech battle sprite in Godot)

Research pass 2026-10-14, 17 tool calls (Firecrawl search and scrape). Read in full: Vasseur's Dead Cells article, Unreal Engine's Octopath Traveler II interview, Digital Foundry's Octopath analysis, a Brigador Steam thread, Dengeki's SRW Y producer interview. Search snippets only (pages blocked or failed): Sea of Stars press kit, the Sabotage r/PixelArt post, Wireframe #43. Copy technique and structure only. Do not copy art, code or text. Facts in "Cited Findings" were read in the linked source. Items in "Inferences" are labeled [general knowledge] or [inference] and are unverified against a shipped title.

## 1. Dead Cells (Motion Twin): the 3D-model-to-pixel pipeline and how sprites were lit

### Takeaway
Dead Cells used simple 3DS Max models and rendered them at a tiny size with no antialiasing, using an in-house tool. Each animation frame was exported as a PNG with its own normal map, and the game lit the frames with "a basic toon shader" (cel shading). The article gives one hard number, a 50 px in-game character height. It says nothing about how normals were downsampled, which light types were used, how many lights there were, or rim lighting.

### Cited Findings
- The article is dated January 25, 2018 on Game Developer, not 2017. The original Gamasutra URL was gamasutra.com/view/news/313026. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-); [mirror citing the original URL](https://sudonull.com/post/14066-Dead-Cells-Using-3D-Pipeline-for-2D-Animation/)
- Vasseur was the only artist on Dead Cells for one year, covering art direction, characters, monsters, animation, FX and most backgrounds. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Pipeline order: draw a basic 2D pixel-art model sheet, build the character and skeleton in 3D in 3DS Max, then export in "filmbox format" (FBX). [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- The 3D models were kept very basic because "the ingame height of the character will only be 50 pixels". [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- "A little homebrew program" renders the mesh "in a very small size and without antialiasing, giving us that pixelated look." [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Key quote: "We export each frame of the animation we made with the 3D skeleton to a .png, along with its normal map, allowing us to render the volume using a basic toon shader." [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Exporting frames as a sequence also let them "slip in a blend mode or two" for extra effect. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Animation was keyed like 2D work. The key frames come first, with as few frames as possible. Interpolation frames are added "before or after the key frames. Never in-between." Attacks are pose-to-pose, and VFX supply the sense of movement, impact and strength. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- On the predecessor prototype ScarKrow, shadows were hand-drawn on every frame. Dead Cells avoided that cost "by designing a lightning [sic] system with that in mind." [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Stated result: "cell shading on our models rendered in low resolution, without any anti-aliasing". Stated unsolved problem: "flickering pixels", which they chose not to clean by hand. The low level of detail was accepted as a trade for animation quality. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Reuse benefits: a piece of armor can be attached to an old model, and old model parts can be reused to build new monsters. Vasseur calls the second "the single most useful little trick" in the workflow. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- The 3D approach let the ScarKrow prototype reach 30 fps animation. The team cites King of Fighters, BlazBlue and Guilty Gear as influences. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)

### Inferences
- [inference] The structure to copy is one albedo PNG plus one normal PNG per frame, both rendered from the same pose at the same tiny size with no AA, then lit at runtime by a stepped (toon) light response. Our mech, at 100-200 px wide, has roughly 2-4x Dead Cells' 50 px character height, so per-pixel detail loss is smaller. Frame-to-frame flicker will be the same class of problem.
- [general knowledge] There are two ways to get normals at pixel size. (a) Render the normal pass directly at the target resolution with no AA. Each pixel then takes the normal of the surface at its center, so it matches the albedo silhouette exactly. This is the approach consistent with Vasseur's "no antialiasing". (b) Render the pass larger, average it down, then renormalize. This is smoother, but it blends normals across cluster edges, and that reads as soft shading. For a crisp look, (a) plus nearest filtering is the safer default.
- [general knowledge] Ways to reduce flicker that the article does not cover: fix the ortho camera and model scale across all frames, snap the root position to whole pixels, and clean up the worst key poses by hand. This last fix matches how Dead Cells accepted flicker in in-betweens.

### Gaps
- The article gives no details on normal-map encoding, the downsampling method, in-game light types, light count, rim light or ramp band count. Third-party breakdowns turned up in search (for example a "Shaders Case Study - Dead Cells' Character Art Pipeline" thread), but they are not primary sources and were not read.

## 2. Octopath Traveler / Octopath Traveler II / Triangle Strategy (HD-2D, Square Enix and Acquire)

### Takeaway
In HD-2D the sprites stay flat pixel cards. The modern look comes from the 3D Unreal scene around them: sprites cast perspective-correct shadows, bokeh depth of field is exaggerated into a tilt-shift "miniature" look, torches and spells light up the scene, the environment's hue shifts during battle, and Octopath II adds dynamic day/night lighting. Acquire says Octopath I "had to play tricks with the lighting" to make the flat characters match the 3D backgrounds. No source I read confirms normal maps on the character sprites.

### Cited Findings
- Characters are sprites. Towns are modeled in 3D and wrapped in pixelated, tile-like textures. [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- High-quality bokeh depth of field, deliberately exaggerated, "sharpening the frame at the screen's centre". Side effect: a tilt-shift photographic look that makes everything look like a miniature model. [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- Ice and stone have specular shaders. Water uses an animated shader that reflects nearby light. Flags use full cloth simulation disguised as a low-res texture. [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- Carried torches light nearby objects, and light shafts give a "specular fizz" across the ground. [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- "Despite our heroes being purely sprite-based, they're assigned a physical value in this 3D space to let them cast shade." These are perspective-correct shadows: a low sun throws long silhouettes, and cloud shadows roll across the ground and change shadow intensity. [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- In battle, casting spells and building boost points "changes the environment's hue". Fire and smoke use high-resolution alpha rather than pixel art, and they "brighten up the entire room, flashing the area with light". [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- Cost on Switch: 720p docked, 1024x576 handheld, 30 fps cap. [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- Acquire: the characters "resemble flat sheets of paper" while the backgrounds are almost entirely 3D, and the team "struggled to figure out how to make them look natural alongside the characters". [Unreal Engine interview](https://www.unrealengine.com/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style)
- Acquire: "In the original Octopath Traveler, we sometimes had to play tricks with the lighting to make the characters and the background look well together; this required us to consider a variety of approaches using both 2D and 3D graphics." [Unreal Engine interview](https://www.unrealengine.com/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style)
- Octopath II's art goal was "high-resolution artwork that just barely looked like it could belong in a pixel-art game". The characters have a smaller head-to-body ratio, map resolution was raised, and dynamic day/night lighting was added on top. [Unreal Engine interview](https://www.unrealengine.com/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style)
- Day/night was built with Unreal's Sequencer. Sequencer was also used for battle abilities, encounters and event cameras, which let artists preview parameters in real time. [Unreal Engine interview](https://www.unrealengine.com/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style)
- The team rotated the camera "nearly 90 degrees in some battle effects and 180 degrees in some events". The open question was how far it could turn before the flat sprites compromised graphical fidelity. [Unreal Engine interview](https://www.unrealengine.com/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style)
- Players report removing bloom and depth of field by editing Engine.ini, which suggests both are standard post effects in the series. This is a community report, not a developer statement, and was seen only as a snippet. [Steam community](https://steamcommunity.com/app/1971650/discussions/0/3777994452130450169/?ctp=2)

### Inferences
- [inference] In HD-2D, most of the "released today" feel comes from what surrounds the sprite rather than from the sprite itself. Applied to a mech battle screen, that means: (1) a lit, layered backdrop, (2) a real ground shadow under the mech, (3) attack and explosion flashes that light the whole scene briefly, (4) a hue or grade shift during special attacks, and (5) mild bloom on bright effects. All five are available in Godot 2D without changing the sprite art.
- [inference] Keep the battle camera mostly frontal. Acquire treats camera rotation as the thing that breaks flat sprites.
- [inference] Effects do not have to be pixel art. Octopath mixes high-res alpha fire and smoke with pixel sprites. Still, a crisp GBA look is easier to protect if effects are rendered at the same art resolution as the sprites (see section 6).

### Gaps
- None of the sources I read say whether Octopath or Triangle Strategy character sprites take per-pixel point-light shading or use normal maps. Unity and Unreal "Octopath-style" tutorials turned up in search, but they are recreations, not developer statements. No CEDEC or Unreal Fest HD-2D talk was retrieved in budget. A 2018 Unreal Fest East HD-2D talk is a recollection only and unverified.
- No Triangle Strategy source was read.

## 3. Sea of Stars (Sabotage Studio)

### Takeaway
Sabotage markets "full-on dynamic lighting" through a "custom-made render pipeline" and posted a dev clip of dynamic lighting on its pixel art. I could not open a primary source that describes the technique, so whether it uses normal maps is unconfirmed.

### Cited Findings
- Press kit (search snippet, page not opened): "Full-on dynamic lighting. Our custom-made render pipeline allows the creation of a breathtaking world coming to life by pushing the limits of 2D pixel-art games". [Sabotage press kit](https://sabotagestudio.com/presskits/sea-of-stars/)
- A Sea of Stars team post on r/PixelArt is titled "Dynamic lighting on pixel art in our upcoming turn-based RPG". The search snippet includes a fragment about a "sprite that 'looks at' the light source", with unknown context. Reddit is blocked for the scraper. [Reddit r/PixelArt](https://www.reddit.com/r/PixelArt/comments/odn30d/dynamic_lighting_on_pixel_art_in_our_upcoming/)
- Wireframe issue 43 (October 2020) carries a Sea of Stars feature. Snippet: "The dynamic lighting in Sea of Stars feeds into the gameplay itself". The PDF failed to load. [Wireframe 43 PDF](https://www.mclibre.org/descargar/docs/revistas/wireframe/wireframe-43-en-202010.pdf)
- A Sabotage Facebook post describes "sun and moon combine with full-on pixel art, dynamic lighting" (snippet). [Sabotage Facebook](https://www.facebook.com/SabotageQC/videos/sea-of-stars-on-steam/919304685573614/)

### Inferences
- [general knowledge, unverified] Sea of Stars is built in Unity, and its time-of-day (sun/moon) control is a player mechanic, which fits the Wireframe snippet about lighting feeding gameplay.
- [inference, speculative] The "looks at the light source" fragment could mean a per-sprite directional cue rather than full per-pixel normal maps. Do not rely on this.

### Gaps
- The actual technique is unknown: normal maps, hand-painted lit variants, or a shader rim. Next step: open the Reddit thread in real Chrome, where the user is logged in, or get the Wireframe #43 pages another way.

## 4. Other shipped pixel games with dynamically lit sprites (Brigador, Children of Morta, Eastward, Blasphemous 2)

### Takeaway
Brigador is the closest structural match to our case. Its mechs are prerendered from 3D models into sprite sheets that carry depth and normal-type data for a real-time lighting engine. The only evidence is a Steam thread where posters write as "we" but are not verified as developers. I retrieved no sources for Children of Morta, Eastward or Blasphemous 2.

### Cited Findings
- Brigador, poster writing as the team: "All of the game content is sprite based. We have sprite sheets laid out just like many other 'traditional' sprite games." The sprites are put on billboards placed in 3D space and sized in 3D render space, so they are "inherently DPI aware". [Steam thread](https://steamcommunity.com/app/274500/discussions/0/133261370000956352/?l=brazilian)
- Brigador, a second poster writing as "we": "We use depth mapping and various tricks with information rendered out for the sprites from the original 3D models, so the lighting engine has '3D model' information for each sprite." [Steam thread](https://steamcommunity.com/app/274500/discussions/0/133261370000956352/?l=brazilian)
- Brigador, a player: the debug lighting settings show vehicles casting fully dynamic shadows on the ground. [Steam thread](https://steamcommunity.com/app/274500/discussions/0/133261370000956352/?l=brazilian)
- Normal-map authoring tools for 2D art exist. Sprite Lamp (Snake Hill Games) "combine[s] dynamic lighting with 2D art" ([Steam thread embed](https://steamcommunity.com/app/274500/discussions/0/133261370000956352/?l=brazilian)). SpriteIlluminator supports "algorithmic and hand-painted normal maps" ([CodeAndWeb](https://www.codeandweb.com/spriteilluminator)).

### Inferences
- [inference] Brigador and Dead Cells together give the pattern for a 3D-rendered mech. Render albedo and normal per frame (and per angle, if there are several) from the same model, optionally with a depth pass, then light it in the engine. Depth makes ground-contact shadows and light-height falloff possible. We render from Blender, so the normal and depth passes cost almost nothing extra: they come from the same render.
- [general knowledge, unverified] Children of Morta (Dead Mage, 2019) was promoted as pixel art with dynamic lighting. Eastward (Pixpil, 2021) uses a custom engine with real-time light and shadow on pixel art. Blasphemous 2 (The Game Kitchen, 2023) was not checked. None of these specifics were verified this session.

### Gaps
- No primary developer write-ups were found within budget for Children of Morta, Eastward or Blasphemous 2.
- The Brigador posters' developer status (Stellar Jockeys) is not verified. Treat those quotes as low-to-medium confidence.

## 5. Modern Super Robot Wars battle animations (2D mech battle sprites today)

### Takeaway
I found no published sprite resolution or frame counts. What is published: through SRW 30 the series ran on an in-house engine dating back to the Alpha series. SRW Y (2025) moved to Unity. Battle animations are still made by long-time staff, and SRW Y's battle animations were remade, with fewer screen blackouts and a wider display area. Players report the 2D sprites look pixelated above 1080p.

### Cited Findings
- Producer Toma (Dengeki, Aug 2025): up to "30", the series kept improving the engine built in the Alpha era. They switched to Unity because work was concentrated on a few engineers, which risked a fatal bug. [Dengeki Online](https://dengekionline.com/article/202508/47898)
- Toma: battle animations are still handled by "熟練のスタッフ" (veteran staff) and have not changed greatly. For Y they cut screen blackouts so attack and defense switch smoothly, and changed the UI to widen the animation display area. [Dengeki Online](https://dengekionline.com/article/202508/47898)
- Famitsu, Sept 2025: the headline says a dedicated SRW department was created and that in SRW Y "戦闘アニメを作り直す" (the battle animations were remade). A targeted extraction of the body found no discussion of sprite resolution, frame counts or effect layering. [Famitsu](https://www.famitsu.com/article/202509/50907)
- Player report (title and snippet only): "I did NOT expect the latest SRW to be limited to 1080p". The poster says the 2D sprites look pixelated at 1440p. [Reddit r/Super_Robot_Wars](https://www.reddit.com/r/Super_Robot_Wars/comments/1t285c1/i_did_not_expect_the_latest_srw_to_be_limited_to/)
- Player opinion on SRW 30: "HD sprite doesn't make the animation good". Camera, dynamics and sound effects are cited as what makes some units' animations better. [Steam community](https://steamcommunity.com/app/898750/discussions/0/3189115819978629901/?l=hungarian&ctp=2)

### Inferences
- [general knowledge] The GBA screen is 240x160. A 100-200 px wide mech fills 42-83% of GBA width (100/240 = 0.42, 200/240 = 0.83).
- [inference] For a 16:9 remaster, a 320x180 base scales 6x to exactly 1920x1080 (320x6 = 1920, 180x6 = 1080) and 12x to 3840x2160. A 480x270 base scales 4x to 1920x1080 and 8x to 4K. A 200 px mech is 62% of 320 width or 42% of 480 width. The 480x270 base keeps GBA-like screen proportions for a 100-200 px mech with room for an enemy opposite.
- [inference] SRW's "modern" look is high-res hand-drawn 2D plus camera moves and effects, not lit pixel art. Players credit camera work, motion and sound for animation quality, not sprite resolution. Our pixel-lighting route goes beyond what SRW does, so the camera and effects layer still matters as much as the lighting.

### Gaps
- No developer-published sprite sizes or frame counts for SRW 30, SRW Y or GBA-era OG. Getting them would mean measuring frame captures (not done).
- No source describes how SRW layers flashes, glow or lighting on its mech sprites.

## 6. Rules developers state for keeping lit pixel art crisp

### Takeaway
In this pass, Dead Cells is the only shipped-game primary source that states rules outright: render at low resolution, use no antialiasing, cel/toon shade, and accept some flicker. Octopath II adds a design target: art that "just barely" still reads as pixel art. Everything else below (light bands, pixel-snapped lights, light-count limits, emissive masks) is common craft knowledge, not a quote from a shipped title.

### Cited Findings
- Dead Cells: "cell shading on our models rendered in low resolution, without any anti-aliasing". Per-frame normal maps feed "a basic toon shader". Flicker is a known unsolved cost. [Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Octopath II target: "high-resolution artwork that just barely looked like it could belong in a pixel-art game". [Unreal Engine interview](https://www.unrealengine.com/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style)
- Octopath: effects lighting the whole room and battle hue shifts carry the modern feel while the sprites stay pixel art. [Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)
- Phaser 4 lighting docs (engine docs, not a game), snippet: light height (z) sets how high the light floats above the scene, and without a normal map a light only lights the sprite's overall shape. [Phaser](https://phaser.io/news/2026/05/phaser-4-dynamic-lighting)

### Inferences
All of these are [general knowledge]. Treat them as structure to test in Godot, not as quotes.
- **Band the light.** Replace smooth N·L with 2-4 hard bands (a ramp or step). Dead Cells' "toon shader" is the shipped precedent. 3 bands (shadow, mid, lit) plus one highlight band is a common starting point.
- **Light at art resolution.** Render the battle scene into a SubViewport at the base resolution (for example 480x270), light it there, then integer-scale the whole viewport with nearest filtering. Lighting then quantizes per art pixel and never produces sub-pixel gradients.
- **Nearest everything.** Use nearest filtering and no mipmaps on both albedo and normal textures. Bilinear filtering on a normal map produces smeared highlights across cluster edges.
- **Snap and step.** Snap sprite and light positions to whole art pixels. Animate light energy in a few discrete steps rather than smoothly, which avoids banding shimmer on hits.
- **Few lights.** One key light, an ambient/fill, and at most one or two transient effect lights per hit (muzzle flash, explosion). More lights tend to fill the bands back into gradients.
- **Rim light as one band.** Treat the rim as a hard 1-2 px band where the normal faces away from the viewer toward a back light. Bake it from the Blender normal pass or compute it in the sprite shader, but clamp it to one color step.
- **Emissive mask.** Give visors, sensor eyes, thrusters and weapon muzzles a separate mask that ignores lighting and drives glow/bloom. Godot 4's CanvasTexture holds diffuse, normal and specular textures, but not emission, so emission needs a custom canvas_item shader or an additive unshaded overlay sprite. Bloom in 2D uses WorldEnvironment glow with HDR 2D enabled (added in Godot 4.2). Check against the installed Godot version.
- **Palette clamp.** Optionally run the lit result through a palette LUT so the mech keeps a fixed color count after lighting, which keeps the GBA read.
- **Godot hooks to check.** Light2D/PointLight2D `height` (light elevation for normal maps), the canvas_item shader `light()` function (where banding goes), texture filter Nearest, and the project setting that snaps 2D transforms to pixels. These are documented Godot features. Confirm the exact property names in the installed version.

### Gaps
- No shipped-game primary source was found that states specific band counts, light-count limits, or emissive-mask workflows for pixel sprites. These stay craft knowledge until a dev talk or postmortem confirms them.
- Not read: the Makin' Stuff Look Good Dead Cells case study, Sprite Lamp's own docs, and any GDC Vault talk on 2D lighting.
