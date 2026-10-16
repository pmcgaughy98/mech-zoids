# Synthesis tool roster (2026-10-12)

The inventory step of a synthesis pass, for the creature factory. Taken from the live connector status of this
session (73 servers) after Preston added a batch of connectors. One line each: what it is for here, or why not.
Paid tools run only on Preston's yes, with the cost named first.

## Used in the factory (proven)
- **Blender 5.2, headless** (`tools/blender/*`): the build kit, rig modules, sprite renders. The live Blender MCPs
  (two of them, 9 and 26 tools) can show the scene; the pipeline is headless so they are for looking only.
- **Our own tools** (`tools/art/*`): pixelizer, sprite_quality, factory_report, compare_views, near_duplicates,
  reference_sheet, creature_round. Free, measured, repeatable: the spine of every pass.
- **Firecrawl**: animal anatomy and reference research (gorilla, pangolin, hippo, shoebill, kangaroo, fossa).
- **PixelLab pixelart_workbench** (free for subscribers): the second scorer. Found near-duplicate colours and
  singletons; use `score` and `lint` on every installed sprite after a pass. Uploads over about 4 KB base64 get cut
  off in transit: pass sprites small or by URL. Better (2026-10-14): `get_upload_url`, then `curl -F file=@<png>`,
  and give the workbench the returned `upload:<id>`; no size limit, no base64 in the chat.
- **Retro Diffusion edit tools** (free ones): pixel_correction adds nothing over our despeckle; palette_converter
  and k_centroid_downscale need the render as base64 (about 80k tokens a call), so they stay unused unless the
  chat gains a file route. Paid generation and rd_pro styles: estimate first, Preston's yes.
- **Director's Lookbook**: the named palette cards Preston's starter colours came from (Blue Hour Cool, Desert
  Dusk, Ochre Madder Delft). `find_styles` (suit color) to name a card for a new machine; `show_card` for hexes.
- **Retro Game Gather**: sibling games and Japan-only releases for the research doc.

## New this session, worth a real use
- **Spritecook** (plugin, needs auth; repo github.com/SpriteCook/claude-plugin, read 2026-10-12): a hosted MCP that
  generates sprites, UI kits, textures, tilesets and short animations with image models (gemini-3.1-flash-image is
  its default; gpt-image-2 for UI kits), animates uploaded assets, and packages character animations for Godot.
  Every generation or animation spends SpriteCook credits: `get_credit_balance` first, Preston's yes per job.
  Where it fits this project, in order: (1) the game's menus, HUD and battle UI as one cohesive kit (a real gap
  the creature factory does not cover); (2) field and canyon tilesets; (3) animating an uploaded machine sprite as a
  comparison with the rig-based walks. Not for the machines themselves: AI-made art is never the reference, and the
  factory already owns their look. Sign-in is OAuth on the first protected call; blocked until Preston completes it
  from the app's connector settings. Ten bundled skills are installed locally (spritecook-*), workflow-essentials
  read.
- **Summer Engine** (108 tools, local engine not running): scene checks, screenshots, playtests, SFX choices. Needs
  the engine open on the project; its cloud generate tools are paid. Try once the Godot checks are due.
- **ElevenLabs** (156 tools): battle and UI sound, voices. Not art; for the audio pass. Paid: estimate first.
- **Higgsfield** (123 tools): image, video, 3D generation and upscales. Paid; AI-made art is never the reference.
- **Canva**, **Google Drive**, **Claude Docs**: sharing deliverables (line-ups, reference sheets). The Hub is
  OneDrive, so Drive only on request.
- **Three.js 3D viewer**: renders custom scenes from code; cannot load the local .glb files, so no turnaround use.
- **visualize**: diagrams for the factory pipeline doc when one is asked for.
- **grep (GitHub code search)**, **wayback-machine**: research only.
- **Qencode** (video transcoding): no sprite use; its job comes when the walk and battle animations are worth
  showing, turning the frame renders into MP4 or web clips for a trailer or share link. Paid per job: estimate first.

## Noise for this project
3DOptix (real lens and ray-trace design; no task in a 2D pixel game uses it, Preston asked 2026-10-12), Wherobots (spatial data), StatsDeck (fantasy football), Indeed,
Veltra, Audible, Spotify, Microsoft Learn, Alpix (shared pixel canvas), the bio-research and finance plugins, the
productivity and marketing plugins (all need auth anyway). Do not surface them for the game.

## Failed this session
- **godot-ai** MCP: connection timed out (30 s). The headless `--script` checks do not need it.

## Stored sources (stock-take 2026-10-13, Preston: "should also include all the github repositories we stored, learned from building hollowtide, all the models we downloaded, the zoids sprites")
All outside the project, under `D:\Program Files (x86)\Game assets\` unless noted. Technique and structure only:
nothing is copied into the game.
- **Zoids sprite sheets** (`sprite references zoids/`: Legacy GBA Helic, Zenebas, BLOX; Saga DS overworld and
  zoids): measured into `docs/reference/sprite-rules-legacy-2026-10-12.md` (sizes, 30-35 colours in long ramps,
  selective outline, light from the upper left, joint discs with a pale centre, flat violet ground line). The
  pixelizer follows it.
- **Zoids source repos** (`zoids-source/`): `ZoidsLegacyDecomp` (the GBA decompilation: battle flow, dialogue,
  regions; read for `docs/reference/zoids-legacy-structure.md` and `battle-structure.md`) and `Zoids` (a Zig game
  project with assets). Structure of the battle and the game loop only.
- **3D model rips** (`Mech references/`): Zoids (16: Command Wolf, Shadow Fox, Lightning Saix, Liger Zero, Blade
  Liger, Iron Kong x3, Gojulas x2, Cannon Tortoise, Berserk Fury, Dark Horn, Cyclops x2, Arosaurer), Transformers
  Fall of Cybertron (Dinobots, Combaticons, Megatron, Insecticons and more: the finish target, measured into the
  handoff's targets), Horizon Zero Dawn (eight machines, fan recreations: part breakdown only), Power Rangers
  (GokaiOh). Study tools: `tools/blender/study/*`, and (2026-10-13) a quadruped proportion and side-render probe in
  the session scratchpad. 2026-10-13 study of the Zoids wolf, fox and lion-types for the wolf: big round joint hubs
  at shoulder, hip and knee; light steel legs with pistons and cables between dark body armour; legs chunky and
  short against a mechanism-dense body.
- **Hollowtide** (`D:\dev\hollowtide*`, about 60 art-pass worktrees): the art-pass lessons are in
  `docs/team/CODEX_START_HERE.md` ("Lessons from Hollowtide's art passes": no AI look, measure debris, views agree,
  keep originals, paid tools on a yes). The working split (Claude scripts and wires, Codex finishes the visuals) is
  `docs/team/CODEX_TASKS_2026-10-13.md`.
- **aseprite-mcp** (`D:\dev\aseprite-mcp`, a cloned GitHub repo): an MCP server for driving Aseprite. Not connected
  in this session; a candidate for Codex's sel-out pass if Aseprite is installed (Preston's call).
- **The factory's own tools** (this project): `tools/art/column_profile.py` (2026-10-13; where an outline differs,
  per column and row; it found the wolf's and pangolin's real problems after the overlays stalled), `shadow_strip.py`,
  `extract_alpha_ref.py`, `cut_glow_bg.py`, `part_overlay.py`, `compare_views.py`; the battle poses by foot
  (`quad_rig.battle_pose_for`, `bird_rig.battle_pose_for`); the weapon module `tools/blender/weapons.py`.
