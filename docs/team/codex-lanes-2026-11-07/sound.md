# Sound lane status, 2026-11-07

Initialized and holding for Preston. Scope: sound effects, onboard AI voice, announcer and music; propose audio trigger work with Game Feel and the owning mech lane. No production work is assigned in this setup turn.

## Current inventory

- Read `CLAUDE.md`, `START_HERE.md`, `docs/team/how-preston-works.md`, `docs/team/mech-sessions-2026-11-05.md`, `docs/plan/HUB_HANDOFF_2026-11-04.md`, the current lane index, `docs/plan/sound-lane.md`, `docs/plan/announcer-lines.md`, and the local audio synthesis and Zoids structure notes. No applicable `AGENTS.md` was found in the project or ancestor paths checked. Dated hub instructions do not authorize contacting peers or starting chats today.
- `KitAudio` and `MapAudio` are active autoloads. KitAudio has rows for rhino, gorilla, fennec, wolf, hippo, lobster, falcon and hummingbird, including hummingbird link-loop support. Game Feel owns this shared integration code; mech lanes own their kit emitters.
- Existing media: 7 ambience loops, 13 map effects, 37 battle effects plus a separate 37-file `battle_432` set, 59 effects across the eight mech folders (including 9 fennec portal files), 12 mech voice clips, 21 announcer clips and one menu-theme track. Presence was checked; sound quality and live timing were not auditioned.
- The living notes record approved recorded sets: rhino Titan pound and Ground stomp, gorilla abilities, wolf lunge and C basic bite, falcon B darts, hummingbird A, and A basics for rhino, gorilla, hippo, fennec and lobster. These supersede older placeholder and waiting-for-picks entries. Historical PASS claims have not been rerun today.
- Current code still maps fennec abilities to the old sand/burst/dig sounds and callouts. The nine approved portal files exist, but the kit currently emits only `basic_cast` and `basic_hit` named cues. Precise portal event hooks remain needed.
- Announcer files and `audio/music/main_theme.ogg` exist; no references to them were found in gameplay scripts/scenes. Existing intro voice clips also lack a match-start mapping. MapAudio has no beacon event rows; shoebill has cue emitters but no KitAudio row.

## Free/local tools on hand

- Python 3.12 with NumPy and SciPy verified available. `soundfile` is absent; existing builders use SciPy WAV I/O and FFmpeg instead.
- FFmpeg and ffprobe resolve on PATH: local decoding, filtering, loudness measurement and Ogg export. Audacity was not found on PATH; installation elsewhere was not checked.
- Godot 4.7.2 executable exists at the documented path. Existing checks: `tools/debug/check_kit_audio.gd` and `check_map_audio.gd`. No Godot process was launched during initialization.
- `tools/audio/` contains 20 scripts for recorded layering, voice/PA treatment, local synthesis and embedded listening pages. Recorded builders use existing sources; `mech_voice.py` processes supplied voice recordings locally rather than generating speech.
- The local Sonniss library at `D:/dev/sound-library/sonniss-gdc-2026/wav` contains 347 WAVs. Project notes document its license and prohibit sending raw library files into AI tools. No source was uploaded or downloaded. ElevenLabs/Suno history is context only; no current balance or paid service was accessed. Do not assume 432 Hz for this game from the legacy battle folder.

## Remaining needs and next useful slice

**Proposed first slice: fennec portal audio trigger contract.** Review the current portal kit with Game Feel and its mech owner, then agree the exact cast, bolt-hit, gate-open, traversal, charge and arrival moments. Map the existing approved files to those moments, review whether old voice lines still fit, and keep `rift_boom` conditional on Preston's kit choice. Once assigned, implement only that slice, check changed scripts before the audio check, and hear it in a real match for timing and duplicate playback. No new generation is needed.

Other queued needs: announcer event/team context and playback policy; menu-theme start/stop; intro trigger; shoebill effects; beacon effects; wall muffling; broader roster coverage; live mix and range checks. These are proposals, not work started.

Only this initialization file was written. No game, audio, art, peer files, commits, paid operations, saved credentials, new chats or peer messages were touched.
