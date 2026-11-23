# Sound lane (living file, edit in place)

Started 2026-11-04. Goal: voice packs and ability sounds that could stand next to SMITE's and Marvel Rivals'.
SMITE voice line lists are a reference for line *categories* only (intro, ability callouts, kills, taunts,
jokes, low health). Never clone a SMITE or Marvel Rivals voice, never reuse their audio.

## Decisions (Preston)
- **Who speaks: each machine's own onboard AI** (2026-11-04). No pilot, no animal sounds in the voice lines.
- **Rhino voice:** ElevenLabs Voice Design, preview 3 of the "Veteran operator" description, saved as
  "Rhino AI (mech MOBA)" (voice id `gpouvY4qbQxBpiALUCix`). He wanted it to sound like a mecha beast, in the
  spirit of SMITE's G.E.B. 1 and Tremor Tech Cabrakan skins: the voice stays, the machine goes on top.
- **Treatment amount: light** ("light is best"). It is the default in `tools/audio/mech_voice.py`.
- **Generate lines on `eleven_v3`**, the model the voice was designed on. `eleven_v4` drifted away from the
  designed voice ("Doesnt sound close to preview 3").

## Rhino lines in the game
| File | Line | Source | Hooked to |
|---|---|---|---|
| `audio/voice/rhino/ability_2.ogg` | "Ground's coming up!" | v3 take 1, light | ground pound cast |
| `audio/voice/rhino/intro.ogg` | "Rhino unit online. Armor at full, drive at full, patience at zero. Give me a target and a straight line, and I will handle the rest." | design preview 3, light | nothing yet (no match start) |
Line text and voice description were drafts he picked; they are his now.

## Gorilla lines in the game (folder `ape`, matching `ape_kit.gd` and `ape_l`)
Voice: Voice Design preview 3 of the "Guardian" description (deep, warm, booming, 40s, protective), saved as
"Gorilla AI (mech MOBA)" (voice id `FvNTSYTR7foDcX42RoSh`). All lines treated light, generated on v3.
| File | Line | Hooked to |
|---|---|---|
| `audio/voice/ape/ability_1.ogg` | "I've got you." | hex shield cast |
| `audio/voice/ape/ability_2.ogg` | "Come and get it!" | chest beat cast |
| `audio/voice/ape/ability_3.ogg` | "Coming in!" | bound cast |
| `audio/voice/ape/ability_4.ogg` | "Nobody leaves." | hex dome cast |
| `audio/voice/ape/intro.ogg` | "Silverback unit online. Shields charged, arms ready. Stay behind me and nothing touches you. That is not a promise, it is a rule." | nothing yet |
Takes in the game (Preston's pick, 2026-11-04, "1b, 2a, 3b, 4b"): line 1 take B, line 2 take A, line 3 take B,
line 4 take B. The unused takes were raw mp3s in a temporary session scratchpad, so treat them as gone.
Gorilla cost: design 128 credits, callouts 106 (8 takes).

## Fennec lines in the game (folder `fennec`, matching `fennec_kit.gd`)
Voice: Voice Design preview 3 of the "Trickster" description (playful and sly, always a step ahead), saved as
"Fennec AI (mech MOBA)" (voice id `3VdTiCFebhVROauhY6lN`). Treated light at size S, generated on v3.
| File | Line | Hooked to |
|---|---|---|
| `audio/voice/fennec/intro.ogg` | "Fennec unit online. Ears up, legs light. Nothing out there I haven't already heard. Point me somewhere, I'm already there." | nothing yet |
| `audio/voice/fennec/ability_1.ogg` | "Eat dust!" | sand kick cast |
| `audio/voice/fennec/ability_2.ogg` | "Hear that?" | ear burst cast |
| `audio/voice/fennec/ability_3.ogg` | "Follow me down!" | tunnel cast |
| `audio/voice/fennec/ability_4.ogg` | "Here comes the big one!" | sonic boom cast |
Callout lines were drafts Preston picked (2026-11-04). Takes in the game (his pick, "1a, 2a, 3a, 4b"): lines 1-3
take A, line 4 take B.
Fennec cost: design about 122 credits, callouts 114 (8 takes).

## How it works
- **Treatment:** `python tools/audio/mech_voice.py <raw file> <machine> <line name>` writes
  `audio/voice/<machine>/<line name>.ogg`. Layers (voice, robot buzz, octave-down chest, ring mod), metal
  resonance, growl, then -16 LUFS. Size classes L, M, S set pitch and buzz; `--amount` sets how much machine.
- **Playback:** `scripts/audio/kit_audio.gd` (autoload `KitAudio`) listens to the kits' own `used(slot)` and
  `impact(strength)` signals. No kit script is edited. Add a line by adding it to the `KITS` table.
- **Buses:** `default_bus_layout.tres`: Music (ducks under Voice through a sidechain compressor), SFX, Voice,
  and a limiter on Master. There is no music in the game yet, so the ducking is unheard.
- **Check:** `--headless --path . --script res://tools/debug/check_kit_audio.gd`.

## Ability sounds
- `audio/sfx/rhino/pound_rear.wav` (rear up) and `pound_slam.wav` (slam frame, also the stampede finale) are
  **option D "Titan"** from recorded sounds (Preston's pick, 2026-11-05: "D, Titan"), written by
  `tools/audio/pound_recorded.py --install D`: rear 0.62 s, -18.2 LUFS; slam 1.90 s, -19.1 LUFS, 31% under 150 Hz.
  Reimported in Godot 4.7.2; `check_kit_audio.gd` PASS. The old synthesised pair is `synth_rhino_pound.py`.
- Gorilla (`audio/sfx/ape/`): recorded since 2026-11-05 (`gorilla_recorded.py`, see Next 1). The lines below
  describe the first synthesised set, which the fennec still uses.
- Gorilla (`audio/sfx/ape/`) and fennec (`audio/sfx/fennec/`), 15 synthesised stand-ins from
  `tools/audio/synth_kits.py` (2026-11-04, after the MOBA audio synthesis: SMITE 2's "a sound the instant you
  press"). Every ability has a cast sound on `used`. The throw, landing or blast has its own sound on the kit's
  impact at that frame (`land` with a per-slot `land_min`), and the chest beat sounds on every beat (`hits`).
  Cast sounds are -18 to -20 LUFS, the landings -13 to -16. `check_kit_audio.gd` covers every slot's cast, hit
  and landing (a landing must not fire on an impact just under its land_min): PASS at 18:20 on 2026-11-04.
  Preston on the preview: "They work" (2026-11-04).
- Turret and core hum (2026-11-04, Preston: "Yes, build it"; `synth_map.py hums`, free): `audio/ambience/
  turret_hum.ogg` (drive motor, a servo whine bending up once per scan pass, gear teeth, a soft sensor blip;
  -27 LUFS) and `core_hum.ogg` (a deep slowly beating drum, electric buzz, arcing, air pushed by the four posts;
  -24 LUFS). MapAudio hangs them under any node whose name ends in TowerGem or CoreGem (the map lane's turning
  heads, `Built/Dressing/BlueTowerGem` and the rest), full within 7 m, silent past 26 m, at pitch 1.0186 so the
  scan and the post passes keep time with the heads' 0.8 rad/s turn. Hiding a node does not silence a sound, so
  the hum follows its head's visibility: `set_structure_down` hides the head and the hum stops. It would also play
  under the crystal heads if that look came back. `check_map_audio.gd` covers it: PASS. Preston on the preview:
  "They work" (2026-11-04).

## Map sounds (asked for by the hub, 2026-11-04: "sel-out moba map. Hook it up so it feels legit")
All synthesised, free, from `tools/audio/synth_map.py`; stand-ins until better takes are picked.
- **Ambient beds**, 16 s seamless loops in `audio/ambience/`: lane, jungle, plaza, stream, base, on the
  Ambience bus. `scripts/audio/map_audio.gd` (autoload `MapAudio`) attaches them at runtime as 3D sounds to
  the arena markers by name: *Core = base, *Tower = lane, *Camp = jungle, Plaza = plaza; any Node3D in group
  `ambient_<zone>` works too. Each bed is full within 14 m and silent past 45 m, so zones hand over.
  Stream: the map lane is adding Stream markers under Markers/; any Marker3D with "Stream" or "River" in
  its name gets the water bed automatically. Pit: what sits in the side pits is Preston's open choice, so
  no pit sound until he picks (hub, 2026-11-04).
- **Events** in `audio/sfx/map/`, heard at the emitter when it is a Node3D. MapAudio listens for these signal
  names on any node (sent to the game feel lane as the contract; it may answer with its own names):
  tower_shot, tower_shot_hit, tower_destroyed, core_destroyed, wave_spawned, minion_hit, camp_aggro,
  respawned, recall_started, recall_finished, match_ended(won: bool) (win or lose stinger on the Music bus).
  Remade for the foundry (2026-11-04, `synth_map.py events`): turret bolts, a steel tower collapse, the plant
  failing, a shift horn and gates, small machine hits. Levels -12 (core down) to -18 LUFS; win and lose are the
  old stingers. The first set is still there as `--theme wild`. Preston on the preview: "They work" (2026-11-04).
  **Voices** (after SMITE 2 and Doom, `docs/reference/moba-audio-synthesis-2026-11-04.md`): 32 at once, each
  event ranked (core 100, tower down 90, wave 70, tower shot and hit 60, camp and respawn 50, recall 40,
  minion hit 10). When all 32 are busy, the oldest of the lowest-ranked sounds is cut, never a higher one. A
  minion's new hit replaces its last, and repeats get a small random pitch nudge.
- **pit_taken** (map lane's capturable side pits, 2026-11-05): option A "Ring" from
  `tools/audio/pit_taken_recorded.py` (lock clunk, the metal ring climbing, shimmer on top), 1.4 s, -15 LUFS,
  rank 80. Heard at the pit. The check passes on stand-ins; no real ArenaPit has played it yet.
- **Rhino rework sounds (2026-11-05, free, recorded):** `tools/audio/rhino_tremor_recorded.py` builds the tremor
  stomp (3 options at -21 LUFS: A Ground, B Steel foot, C Rumble, heard inside the full tremor) and a first pass
  of key 1 (dash_cast -18, horn_catch -15, toss_land -16). Page: `docs/listen/rhino-tremor-and-dash-2026-11-05.html`.
  The game feel lane added `cue(name)` to rhino_kit.gd at those four moments. `kit_audio.gd` connects it through
  RhinoKit's "cues" map (each with a ±3% pitch nudge), and check_kit_audio.gd passes with all four wired. The files
  Preston picked stomp A, Ground; it is installed as `audio/sfx/rhino/tremor_stomp.wav` (`--install A --no-dash`).
  The key 1 files are installed too (his OK, 2026-11-05): dash_cast, horn_catch, toss_land.wav in `audio/sfx/rhino/`.
- **Announcer: started 2026-11-05** (Preston: "announcer pack time"). He picked the foundry overseer, the plant's
  control AI on the PA. Voice Design preview 3, saved as "Foundry Overseer (mech MOBA announcer)" (voice id
  `NnhluA0QQcnSYL6ng49e`). Preston: "a good base", treat it like the machine voices. The 21 draft lines in
  `docs/plan/announcer-lines.md` came from one v3 take (450 credits), cut by Scribe word times (v3 reads them
  50 to 100 ms apart, so a silence split fails). Treated with mech_voice's new `PA` preset at 0.6: thin machine
  layers, a loudspeaker horn, the foundry hall echo. Written to `audio/voice/announcer/<name>.ogg` by
  `tools/audio/announcer_pack.py`. Listen page: `docs/listen/announcer-2026-11-05.html`. Not hooked yet. Most
  lines need signals the game doesn't emit, and team lines need the local player's team.
- **Music: Suno** (Preston, 2026-11-05), Pro plan, 3,440 credits and 14 download credits this month. Style: foundry
  orchestral (orchestra, industrial percussion, anvils, deep synth bass), instrumental. He wanted the main menu
  theme first. Takes `52cdf372-2d9c-43ac-8ec2-0e7d9d1042c8` (kept) and `49e2971e-ad83-4b00-822f-b25482f8e91c`
  (suno.com/song/<id>). Preston picked take 1 and approved one download credit, so 13 are left this month.
  The master WAV is `D:\dev\sound-library\suno\foundry_main_theme_take1_52cdf372.wav` (119.7 s, 48 kHz stereo,
  -15.6 LUFS). The game file is `audio/music/main_theme.ogg` (Vorbis q6, -16.1 LUFS, true peak -4.0 dBFS), and
  its import is set to loop. The track has a natural ending around 117 s, so the loop restarts after it rather
  than running seamlessly. Not hooked to any menu yet. Ask before every download: each costs a credit.
- **Check:** `--headless --path . --script res://tools/debug/check_map_audio.gd` (stand-in emitters, since
  no towers or waves exist yet).

## Synthesis is not good enough (Preston, 2026-11-05)
Relayed word for word by the 3D test lane: "Hmm they sound too 8 bit and like 80-90's style games. I'm looking for
legit moba sounds competitive with smite. dota and lol". Read as covering every synthesised sound here (ability
stand-ins, map events, beds, hums), not only the listen page. Tones built from scratch have hit their ceiling; the
next step is recorded source sounds, layered and processed.
- **Free route:** the Sonniss #GameAudioGDC 2026 bundle, gdc.sonniss.com: 7.47 GB, 347 WAVs from 17 vendors, 5 zip
  parts or a torrent, no sign-up. License (sonniss.com/gdc-bundle-license, v2.0): commercial games, no attribution;
  no selling or passing on the raw sounds; **no AI training**, so these files never go into ElevenLabs, Gemini or
  any other AI tool. Earlier years' bundles (sonniss.com/gameaudiogdc) are bigger (23.5 GB, 48.2 GB). Which kinds
  of sound each vendor covers isn't listed on the page. Downloading needs Preston's yes.
- **Paid route:** ElevenLabs sound effects, 40 credits per second (their docs, 2026-11-05), up to 30 s, WAV at
  48 kHz. Everything synthesised now is 29 one-shots (40 s) and 7 loops (112 s): about
  1,600 credits per take for the one-shots, 6,100 with the loops; three takes to pick from is three times
  that. Price goes to the hub first.
- The listen page's muffling pick waits for real sounds; muffled stand-ins don't tell him much.

## Cost so far
About 716 ElevenLabs credits on 2026-11-04. Rhino about 246: design 132, v4 callout takes 38 (unused), v3
takes 38, plus small estimates. Gorilla 234: design 128, callouts 106. Fennec 236: design 122, callouts 114.
Map sounds 0 (synthesised). Announcer: voice design about 125, the 21 lines 450, Scribe 0 (2026-11-05).
A short callout costs about 1 credit per character per take on v3 (about 13 to 19 for a two-to-three word line).

## Next
1. Real ground pound sounds (ElevenLabs sound effects or a library), priced first.
   **Recorded options built (2026-11-05, free):** the Sonniss GDC 2026 bundle is downloaded and unzipped to
   `D:\dev\sound-library\sonniss-gdc-2026\wav` (362 files, 347 WAVs, 8.0 GB, each checked against its zip; zips
   kept in `zips\`; outside the project, never into an AI tool). `tools/audio/pound_recorded.py` layers trailer
   booms, a metal "thud, low ring" hit, a body punch, concrete-and-pipe crunch, debris, a robot servo motor and a
   deep latch into B "Foundry" (machine first), C "Quake" (ground first), D "Titan" (both plus a sub drop), all
   matched to the stand-in levels. Listen page: `docs/listen/ground-pound-recorded-2026-11-05.html` (A is the
   stand-in). Built by measurement, not by ear; Preston's ear decides. `--install <letter>` writes his pick over
   `audio/sfx/rhino/pound_rear.wav` and `pound_slam.wav`; nothing else changes. **Picked D, installed** (see
   Ability sounds). Not yet heard in a live match; the 0.40 s rear-to-slam gap on the page was an estimate.
   **Gorilla next (Preston, 2026-11-05: "Gorilla next"):** `tools/audio/gorilla_recorded.py` builds all 7 ape
   sounds from recordings in Titan's direction (steel door bangs and body punches for the chest beat; electric
   tonal impacts, glass shards and a chord hit for the hex shield; reversed impacts swelling into the dome; booms,
   metal thud, crunch and debris for the landings), each levelled to its stand-in. Listen page:
   `docs/listen/gorilla-recorded-2026-11-05.html` (A stand-in, B recorded). **Picked "All B", installed
   2026-11-05** (`--install all`): all 7 files in `audio/sfx/ape/` are now the recorded versions at the stand-ins'
   levels; Godot 4.7.2 reimport, `check_kit_audio.gd` PASS. Not yet heard in a live match. The fennec's 8 sounds
   are the last synthesised kit sounds left, **on hold** (hub, 2026-11-05): its kit is being redrafted after
   Preston's "No sand or fox physiology abilities" (draft in `docs/plan/moba-kits.md` drops sand kick, ear burst,
   dig and pop out; ears become passive gate echo; sonic boom returns as a portal-energy rift boom). Build the
   fennec's sounds from the kit he picks, not from the current 8.
   **Preston, after the hold: "Yes, fennec next" (2026-11-05).** Built only what both versions share (1 two-faced
   shot, 2 pocket gates, 3 far gates, 4 great gate's charge, opening and arrival), plus `rift_boom` marked as
   redraft-only: `tools/audio/fennec_portal_recorded.py`, 9 new sounds with one portal motif (glassy snap, sci-fi
   liquid hit, deep electric hum). Listen page `docs/listen/fennec-portal-recorded-2026-11-05.html` (together and
   one by one). The current 8 fennec files and their hookup are untouched. `--install` copies into
   `audio/sfx/fennec/portal/`; hooking them into `kit_audio.gd` waits on the portal kit's script and its signals.
   **Preston: "All good" (2026-11-05). Installed** all 9 in `audio/sfx/fennec/portal/` (imported in Godot 4.7.2,
   `check_kit_audio.gd` still PASS). **Not hooked up:** whoever writes the portal kit's script, map in
   `kit_audio.gd` FennecKit: cast 1 `shot_cast`, a bolt's hit `shot_hit`, cast 2 `gate_open_small`, cast 3
   `gate_open_far`, any step or jump through a gate `gate_through`, cast 4 `great_charge`, the ring opening
   `great_open`, the arrival `great_arrive`; `rift_boom` only if he takes the redraft. Then drop the old 8 and
   their table rows. Gate echo (the redraft's passive) has no sound yet.
   Listen page for his pick (2026-11-05, hub: "make the picks easy, free"): `docs/listen/sound-picks-2026-11-05.html`,
   audio inside the page, made by `tools/audio/sound_picks.py` (fixed seeds). Pound: A the stand-in now, B "Steel"
   (machine first), C "Quake" (ground first), loudness matched to the stand-in (rear -18.2, slam -19.1 LUFS); my
   pick C. Wall muffling: None (today), Light (low-pass 2.5 kHz, -4 dB), Heavy (800 Hz, steeper, -9 dB); my pick
   Light. Waiting on his picks; the chosen pound option moves into `synth_rhino_pound.py` under the same file names.
2. The rest of the rhino voice pack by category, his lines.
3. Fennec: voice, intro and four callouts done 2026-11-04, hooked in `kit_audio.gd` (FennecKit).
   `check_kit_audio.gd` now covers it (files load, slots 1-4 start their callouts): PASS at 17:49.
4. Map sounds: Preston says "Fine for now" (2026-11-04). Keep the synthesised set; revisit after he hears
   them in a real match.
   Retheme (hub, 2026-11-04): Preston picked C, "Foundry" (industrial dusk). The five beds were redone to fit
   the foundry (`synth_map.py beds`, theme "foundry"; the first set stays as `--theme wild`): corrugated-wall
   wind and plant drone (lane), machine yards with a drop forge (jungle), furnace roar and a creaking frame
   (plaza), a runoff channel with a pump (stream; the map lane may still make it coolant), a generator plant
   (base). Seamless, leveled to about -25 LUFS each; check_map_audio PASS. The events are unchanged.
   Preston on the preview: "They work" (2026-11-04).

## Team routing (hub, 2026-11-05)
- One session per mech now handles touch-ups (VFX, kit upgrades). They send sound requests here, and sound stays in this lane.
  Roster with the 13 ids: `docs/team/mech-sessions-2026-11-05.md` in the hub's worktree `admiring-bell-074042`.
- Each `<mech>_kit.gd` belongs to that mech's session. Rhino: `local_0d636c38-8177-4132-8862-4c9253c141e6`. Sound hookups
  that need a new kit signal go through them. `kit_audio.gd` is shared, under game feel; tell them when it changes.
- Paid jobs (ElevenLabs, Suno) need Preston's own yes and a price first. Only one paid job runs at a time across the team.
- **Wolf (queued 2026-11-05, from the Wolf session `local_14a93cf7-9377-457e-880e-ef8113b239c0`):** `wolf_kit.gd`
  (WolfKit) has cue(name) like RhinoKit. Slot 1 lunge fires `lunge_cast` (the leap starts), `lunge_bite` (the jaws land,
  0.07 s before the target reacts) and `lunge_miss` (bites the air). **Done 2026-11-05:** `tools/audio/wolf_lunge_recorded.py`,
  two options each. Preston picked "All A" (Pounce, Steel jaws, Air snap). Installed to `audio/sfx/wolf/`, with a WolfKit
  "cues" row in kit_audio.gd (game feel told). check_kit_audio.gd plays all three. Page: `docs/listen/wolf-lunge-2026-11-05.html`.
- **Hummingbird (queued 2026-11-05, from its session `local_9c422ba3-8212-4cea-b550-3e19bb3c38a0`, "no rush, not in the match
  yet"):** cue(name) on `hummingbird_kit.gd`: `needle_cast`, `needle_heal`, `needle_hit`, `needle_miss`, `link_on`, `link_break`.
  The link is a held ruby beam, so `link_on` should start a quiet hum loop and `link_break` stop it with a snap. KitAudio has no
  loop support yet: it needs a looping player per kit, started on one cue and stopped on another (a small kit_audio.gd change, tell
  game feel). The 5 one-shots and the hum loop come free from the recorded pipeline once Preston says go.
  **Update 2026-11-06:** it's in the match now, and it gained the basic attack cues `beak_shot`, `beak_hit` and `beak_miss`.
  hummingbird_kit.gd had no class_name, so KitAudio (which keys on get_global_name) could never match it. Agreed with game
  feel: the Hummingbird session added `class_name HummingbirdKit` (done 2026-11-06; the import is clean and global_script_class_cache lists it), and the row is keyed "HummingbirdKit".
  **Built 2026-11-06 (Preston: "Yes, hummingbird"):** `tools/audio/hummingbird_recorded.py` gives two options for the 9 cues
  plus `link_hum` (a seamless 2 s loop at -30 LUFS, its loop points in a WAV smpl chunk). Every A is installed in
  audio/sfx/hummingbird/ as a placeholder. The listen page is docs/listen/hummingbird-2026-11-06.html, Kept A (2026-11-06): Preston said "Keep all A", so the installed set is final.
  KitAudio gained a "loops" key (start cue, stop cue) with one looping player per kit; game feel was told. Check: PASS.
  The hum can't hang (Hummingbird session, 2026-11-06): every link end goes through _unlink(), which emits link_break
  (replaced, range, wall, gone, including either side dying), and a tab swap frees the kit, which frees the hum player.
- **Falcon (queued 2026-11-05, from its session `local_80615129-4017-4f14-940f-e77b38138e06`, not in the match yet):** basic
  attack cues on `falcon_kit.gd`: `dart_fire` (every shot, up to once per 0.9 s: light and short, it repeats all fight),
  `dart_hit`, `dart_keen` (a hit at 90%+ of full range, the keen eye passive's top bonus: a sharper crack than dart_hit, the shot
  to reward), `dart_miss` (nothing or a wall). Free from the recorded pipeline when Preston says go, then a FalconKit "cues" row.
  **Built 2026-11-06 (Preston: "Yes, falcon"):** `tools/audio/falcon_dart_recorded.py` gives two options per cue. Every A is
  installed in audio/sfx/falcon/ with a "FalconKit" row in kit_audio.gd. The listen page is docs/listen/falcon-dart-2026-11-06.html. Kept B (2026-11-06): Preston said "All B", so B (Air cut,
  Spike, Ring out, Wall tick) replaced the A placeholders, and that set is final.
  falcon_kit.gd has no class_name (its header skipped it on purpose), so nothing plays until the Falcon session adds
  `class_name FalconKit` (added 2026-11-06, cache lists it). check_kit_audio.gd covers the 4 falcon cues: PASS.
- **Shoebill (queued 2026-11-05, from its session `local_06f5a481-ab1b-4974-bd65-c1f383c45df6`, moon kit, not in the match
  yet):** cue(name) on `shoebill_kit.gd`: `moon_phase` (a charge gained while standing still, up to 3: a soft rising chime,
  maybe one pitch step per charge), `moonbeam_warn` (the 0.3 s warning line), `moonbeam_fire` (the beam of light), `lens_flick`
  (the basic attack, up to once per 1.0 s). It also emits used("1") and impact(0.2) when the beam hits. Free from the recorded
  pipeline when Preston says go, then a ShoebillKit "cues" row.
- **Rhino basic attack (2026-11-05, from the Rhino session):** cues `jab_swing` (swing start, about every 0.9 s) and `jab_hit`
  (contact 0.25 s later, 0.05 s hitstop). `tools/audio/rhino_jab_recorded.py` gives two options each. A+A ("Heavy air", "Plate")
  is installed as a free placeholder with RhinoKit cue rows (game feel told), and the check passes. Kept A (2026-11-06):
  `docs/listen/rhino-jab-2026-11-05.html`.
- **Gorilla basic attack (2026-11-05, from the Gorilla session):** cues `strike_swing` and `strike_hit` (contact about 0.22 s
  later, hits only) on ape_kit.gd. `tools/audio/gorilla_strike_recorded.py` gives two options each, heavier and more body than
  the rhino's metal jab. A+A ("Haymaker", "Fist") is installed as a placeholder, with an ApeKit "cues" row (game feel told),
  and the check passes. Kept A (2026-11-06): `docs/listen/gorilla-strike-2026-11-05.html`.
- **Import crash:** `--headless --import` sometimes segfaults (exit 139) on the run that imports new WAVs. The files still
  import, and a rerun exits 0.
- **Wolf basic attack (2026-11-05; built under Preston's "we need basic attacks... have them message the sessions
  they need", relayed by the Fennec session):** A placeholders are in (`tools/audio/basic_attacks_recorded.py`). Preston said yes to proper bite sounds (2026-11-06, via the Wolf session), so option C ("Snap trap", "Click") was added,
  made for the basic rather than cut from the lunge. Preston picked "All C" (2026-11-06), so basic_bite.wav and basic_whiff.wav are now C. The check passes. cues `basic_bite` (a hit) and
  `basic_whiff` (snaps the air) on WolfKit.cue. Every 0.8 s: a 0.08 s wind-up, then the snap with a 0.05 s hitstop. It's a
  short jaw snap, smaller than `lunge_bite`. A cheap route: smaller, quicker versions of the lunge's Steel jaws and Air snap.
- **Plaza beacon (queued 2026-11-05, map lane via the hub; not urgent, the beacon itself waits on Preston's yes):**
  `scenes/moba3d/arena_beacon.gd` (ArenaBeacon, group `arena_beacons`) emits `beacon_up` and `beacon_taken`. Each needs a
  MapAudio EVENTS row and a PRIORITY row (PRIORITY is indexed directly, so a missing row errors). Signal details from the
  map lane (`local_6d56ace9-00ec-4cdc-ab27-206065d6030a`). The announcer could pair with them later.
- **Hippo basic attack (2026-11-05, from the Hippo session `local_e43e9d84-85da-4dfd-8f61-5936dd027007`):** cues `bite` (contact,
  0.1 s after the key, impact 0.2) and `bite_whiff` on hippo_kit.gd. `tools/audio/hippo_bite_recorded.py` gives two options each,
  with big heavy jaws. A+A ("Crusher", "Heavy clap") is installed as a placeholder with a HippoKit row. KitAudio now wires kits that
  have cue(name) but no used(slot), since HippoKit has none (game feel told). The check passes, and Kept A (2026-11-06):
  `docs/listen/hippo-bite-2026-11-05.html`.
- **Fennec basic attack (2026-11-05, Fennec session `local_53e6b8bc-5d21-41e5-90c5-b3be322226f4`):** cues `basic_cast`
  (140 ms tick, every 0.9 s) and `basic_hit` (crystal spark). Same script, portal palette. A placeholders ("Glass tick",
  "Crystal spark") are in, with a FennecKit cues row. Page with the wolf: `docs/listen/basic-attacks-fennec-wolf-2026-11-05.html`.
  Sounds under 400 ms read -70 LUFS in ebur128 (no full block), so the `lvl()` helper pads to 0.5 s to measure.
- **Lobster basic attack (2026-11-06, Lobster session `local_60f41fc4-d480-4ad9-b040-47f6a1f7de03`, Preston: "Melee claw snap"):**
  cues `basic_snap` and `basic_whiff` on lobster_kit.gd (`class_name LobsterKit`). `tools/audio/lobster_claw_recorded.py` makes a
  hydraulic claw. The hiss is the top end of the "AEROJet Blast Off Clean" jet sound, since the bundle has no pneumatic hiss.
  A+A ("Hydraulic clamp", "Hiss-clack") is installed with a LobsterKit row (game feel told), and the check passes. Kept A (2026-11-06):
  `docs/listen/lobster-claw-2026-11-06.html`.
- **Basic attack picks (Preston, 2026-11-06): "Keep all A"** for the rhino (jab), gorilla (strike), hippo (bite), fennec
  (dart) and lobster (claw). The A placeholders are now final, so nothing needs swapping. Wolf bite is All C.

- **Gorilla re-key (2026-11-09, from the Gorilla 3D lane `local_f7ccf9b5-a288-4a10-aad3-0033dcd6da3e`):** key 4 is now the chest beat
  ult (used("4"), beats at 0.3 and 0.15, then 0.8 as the dome rises), and key 2 is empty. ApeKit row: no cast on 4 (dome_rise is
  unused now), hits "4" chest_hit, land "4" dome_slam at 0.8. kit_audio's _on_impact now ends a slot's hits when its landing plays,
  so punches after the ult don't play chest_hit. hits "2" stays only while match_bot.gd still calls the old chest_beat() on 2 for
  bots; drop it when the bot row moves. check_kit_audio.gd has an ult sequence test: PASS. Game feel was told; the backup is
  D:/dev/_scratch/sound/kit_audio_before_ape_rekey_2026-11-09.gd.
  Timing (2026-11-09): the 3D gorilla's beats land at 0.42, 0.645 and 1.10 s (clip v22, ape_kit.gd `beat_times`; it was 0.45, 0.70, 1.10). No change needed: the sounds follow the
  impact signals, which fire after each beat's wait. The one limit is that the last beat must land within KitAudio's HIT_WINDOW (2.5 s) of used("4").
- **Gorilla dome heal pulse (queued 2026-11-09, from the hub; suggested by the Gorilla 3D lane):** the ult's dome heals its own side
  6% of max HP a second, in pulses every 0.5 s while it stands. A quiet heal-pulse sound would need ape_kit.gd to emit a cue (say
  `cue("dome_pulse")`) on each pulse, plus a cues entry in the ApeKit row. It pulses twice a second, so it has to stay soft and short.
  Beat 2 now re-taunts instead of shielding allies; the beat sounds are unchanged (still chest_hit). Uncommitted, and the numbers are
  proposals awaiting Preston. Build it on his go, after the shoebill or instead of it.
- **Rhino 3D clips (2026-11-10, from the Rhino 3D lane `local_c87babea-13ae-47d7-8f02-df2c7ceb2b99`, a review build, not approved):** cue times are in
  D:/dev/_scratch/rhino-donor-2026-11-08/armor-seam-polish-v43/rhino-polish-v43.events.json. Hits: horn_hook 0.20, horn_rip 0.333,
  horn_gore 0.533 (front feet crash 0.80). Toss catch 0.40. Ground pound slam 0.40, stomps 0.80/1.20/1.60/2.00. Finale slam 0.40.
  The existing sounds need no change: they follow the kit's signals, so the kit wiring must emit at those times (mapping sent to that lane).
  Queued for Preston's go: separate hook, rip and gore hit sounds (if the three clips become a basic chain), a gore feet crash, and a
  shoulder piston hiss or clank on each slam, stomp and horn hit.
- **Rhino gore_land (2026-11-10, from game feel via the hub):** the 3D rhino is in the match, and its horn chain's gore fires `cue("gore_land")` as
  the front feet crash down (about 0.27 s after the gore hit). `tools/audio/rhino_gore_recorded.py` gives A "Feet crash" (0.70 s, -16 LUFS, very
  low: 75% under 150 Hz) and B "Steel feet" (0.65 s, more metal). A is installed with a RhinoKit cues entry. The listen page is
  docs/listen/rhino-gore-land-2026-11-10.html, and Preston picked A on 2026-11-16 ("Take A", relayed by the hub), so the installed file stays. Check: PASS.
- **Kangaroo (queued 2026-11-11, from the Kangaroo 3D lane `local_e90129d2-2d3d-451f-8d70-528caf6fda29`):** event times in
  art/arena_models/kangaroo.events.json (120 fps source, damage flags). Its kit isn't ported yet, so nothing fires in a match; game feel
  will wire it. Moments that want sound: jab hits (Jab_Left 0.20, Jab_Right_Quick 0.11, Hook_Right 0.24), HopJab (hop 0.12, land 0.40,
  four hits 0.52 to 0.88), TailKick (brace 0.14, hit 0.50, land 0.74), Guard_Counter (block 0.0, hit 0.22), Ring_Cast (glove tap 0.18,
  ring 0.42), Hit_Heavy replant 0.20, Death (collapse 0.55, settle 1.20). Walk/strafe land and push-off and the idle fidget are optional
  footsteps. Times are placeholders until Preston sets them. Videos: D:/dev/_scratch/kangaroo-3d/out/. Free from the recorded pipeline
  on Preston's go, then a KangarooKit cues row once the kit emits cue(name) (and has a class_name).
  **Preston, 2026-11-11: "Wait for the kit".** Build when game feel has ported the kit with cue(name) emits and a class_name.

## Second free source: Patch asset search (Preston okayed it, 2026-11-14, via the hub)
- Run `npx --yes @patchgg/cli assets search "<words>" --type sound --json` (or `--type music`) from `D:\dev\_scratch\patch-gg-try`.
  It needs no install and no sign-in. The hub's samples: "explosion" found 186 sounds, mostly Kenney CC0; "battle music" found 3
  OpenGameArt CC0 tracks; "mech footstep" found nothing.
- Use only CC0 or CC-BY, keep each credit, and skip `ai=true` hits unless Preston says otherwise.
- Never run `pch login` or `pch agent install` (not okayed). `pch assets add` only in scratch. Copy files into the game the usual way
  and write each credit in audio/CREDITS.md (start that file with the first Patch sound used).
- Unlike the Sonniss bundle, CC0 and CC-BY files carry no "no AI" rule. Still keep Sonniss files out of any AI tool.
- **Patch gap-fill (2026-11-14, Preston: "Patch gap-fill"):** every MapAudio event and match end already has a file. The real gap is
  music during a match (only the menu theme exists). Patch found no mech or robot sounds; the Sonniss library still covers those.
  UI sounds exist (audio/sfx/battle/ui_*) but have no hook. Four music candidates are in D:/dev/_scratch/patch-gg-try/assets/music
  (credits in its CREDITS.md): Industrial Cinematic, Industrial Revolution and Crusade - Heavy Industry (Kevin MacLeod, CC BY 4.0,
  credit needed), and Epic boss battle (Juhani Junkala, CC0, loops). The listen page is docs/listen/match-music-patch-2026-11-14.html
  (`tools/audio/match_music_preview.py`). Nothing is in the game; it waits on Preston's pick, then a match-music hook (not built yet).

### 2026-11-16: match music in (Preston: "Epic boss battle")
- `audio/music/match_theme.ogg` is "Epic boss battle" (Juhani Junkala, CC0, via Patch), copied unchanged; credit in
  `audio/CREDITS.md`. Import has loop=true, and MapAudio sets loop on the stream too.
- MapAudio starts it when a match_ended emitter enters the tree (MatchDirector, its 5v5 FoundationDirector, or the
  2D scripts/moba/moba_match.gd): one loop at a time, Music bus, `MATCH_MUSIC_DB` -14 (file -6.9 LUFS, bus -8 dB, so about -29).
  It fades out over 0.6 s on match_ended, before the win/lose stinger, or when the emitter leaves the tree. It is
  outside the 32 one-shot voices, and stop_all() leaves it alone.
- check_map_audio.gd: five new checks (loops on Music, no second loop, stops before the stinger, restarts next match
  and stops when it leaves, lose.wav and a director leaving after the fade). PASS.
- Not heard in a running match yet. If it is too loud or quiet, change the one const.
- The other three Patch tracks (Kevin MacLeod, CC BY) stay in scratch, not in the game.
