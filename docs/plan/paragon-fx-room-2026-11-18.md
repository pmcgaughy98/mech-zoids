# Paragon effects room (plan, 2026-11-18)

Preston, 2026-11-18: "I was hoping we'd be able to study in a smite enviroment with the effects etc. So we could make
a game quality based off smites construction." Then he picked "Paragon effects room".

## Why Paragon and not SMITE
- **SMITE 1:** the extractor gets meshes and animations, but not particle systems or materials, and textures come
  out at 64 px.
- **SMITE 2:** its files need an AES key, and its effects wouldn't come out as working assets anyway.
- **Paragon:** its effects are already in `D:\Unreal Projects\ParagonStudy` and they work. Paragon was Epic's own
  big-budget MOBA. The 13 hero packs hold about 5,100 FX assets, about 1,250 of them particle systems (`P_*`,
  counted 2026-11-18).

## Checked offline (2026-11-18)
- **Unreal 5.8 still runs these effects.** They are Cascade, the older particle system. Cascade is an engine plugin
  that is on by default (`Engine\Plugins\FX\Cascade`), and its runtime classes are in the engine.
- **The effects don't fire from the clips.** No ability clip in any of the 13 heroes references an effect. Only the
  level-start montages mention particles. Paragon fired its effects from gameplay code that isn't in the packs. So the
  room fires each effect on its own, and any pairing with a clip would be ours, not Paragon's timing.
- **What each effect is made of can be read by script.** The `CascadeToNiagaraConverter` plugin's
  `FXConverterUtilitiesLibrary` gives Python each emitter, its modules, material, sub-UV grid, spawn rate, bursts,
  lifetime and duration. The plugin is now turned on in `ParagonStudy.uproject` (study project only).

## What the row does
Everything is in `D:\dev\_scratch\paragon-fx-room\` (private, never committed). `run_row.ps1` runs these steps in
order:
1. **Breakdown, headless.** Every particle system of all 13 heroes goes into `fx_breakdown.json`.
   `python fx_sheets.py` then writes `sheets\<Hero>.md` (one table per effect, one row per emitter) and
   `sheets\00_summary.md`. The summary covers emitters per effect, renderer mix, blend modes, flipbook grids,
   texture sizes, spawn style, lifetimes and the most used modules. Those numbers are the quality bar the effects
   lanes can build to.
2. **Build, headless.** `/Game/FxStudy/L_ParagonFx` is a dark floor with a black sky, two lights and manual exposure
   (no eye adaptation), so additive effects read.
   - Each hero gets a row: the hero playing an idle, then up to 8 of its effects on pads 10 m apart.
   - Each pad has a 2 m pole for scale and a name sign.
   - The effects are picked from the breakdown. Camera, lobby and emote effects are skipped, and so is anything that
     needs a bone, a trail source or a beam target. Ultimates, casts and impacts come first.
3. **Frames, editor.**
   - A 240 s warm-up fires every effect every 5 s so the shaders compile.
   - Then each effect fires on its own and is shot at 0.2, 0.6 and 1.5 s. The real delay is written to the report.
   - Each hero row also gets one shot with all of its effects firing.
   - **The gate comes first:** one effect is shot twice, about 2 s apart. If the two frames match, the effects
     aren't ticking in the editor, so the run stops instead of filming frozen effects.

**Exit codes:**
- 0: frames ran.
- 2: the level didn't save (old level restored).
- 3: the gate says frozen.
- 4: the breakdown didn't finish.
- 5: someone else's `init_unreal.py` is in the hook folder (nothing run).

## First row: two heroes
- **The heroes are my pick, easy to change:**
  - **Rampage:** a big brawler beast, the closest to the gorilla.
  - **Howitzer:** a mech suit.
- The breakdown always covers all 13 heroes.
- The advice taken: don't go 13 wide on a frames path that has never run.
- **Expected editor time:** about 35 to 45 minutes (breakdown 10 to 20, build about 5, frames about 15).

## Booked: row 58 (hub, 2026-11-18)
- The look lane (`local_90045777`) hands over the editor after its row 57b proof measure.
- Ahead: 56 kangaroo effects, 57 map arena colour default, 57b look lane.
- The hub approved the plan as written.
- When done, hand the editor to hippo effects (`local_be3160ac`) for row 59, not back to the hub (the hub's later
  change). Still report the frames path, counts and errors to the hub.
- After the run: run `python fx_sheets.py`, then send Preston the summary page and a few frames.

## Row 58 result (2026-11-18, 19:22 to 20:11)
- **Breakdown (22 min):** 13 heroes, 683 particle systems, none failed to load.
  - Correction: I wrote "about 1,250 particle systems" above. That count was by file name (`P_*`). The breakdown reads
    by asset class and finds 683.
- **Build (4 min):** `L_ParagonFx` saved, with 16 effects: 8 Rampage and 8 Howitzer.
  - Two errors: the hero idle failed to start for both heroes. Those errors are why the editor exited with code 1.
  - The effects themselves all placed.
- **Frames (17 min):** 52 frames, 0 frame errors, in `D:\dev\_scratch\paragon-fx-room\frames\`.
  - The gate said "unclear": only 0.5% of the pixels changed between its two shots.
  - The 0.2, 0.6 and 1.5 s shots of each effect clearly differ, though: they bloom, then fade to smoke. So the effects
    do tick in the editor.
- **Sheets:** `sheets\00_summary.md`, plus one sheet per hero.
- **What the frames show:**
  - Howitzer's eight are varied: ultimate blasts, water hits, a grenade and a charge.
  - Rampage's eight are all variants of one lunge impact. The picker favoured "impact" in names.
  - **Fixed offline (2026-11-18, Preston: "fix rapamage picker"):** `pick_effects` now takes one effect per family
    before any repeat. The family is the ability word, after the hero prefix, skin words (Ice, Hyper) and variant
    words (Enraged, Blue, New, V2, ...).
    - On the real breakdown, Rampage's eight are lunge, rock, rip-n-toss, enrage, enraged impact, melee, smash arc
      and roar. Howitzer keeps eight different abilities.
    - Two leaks remain:
      - IggyScorch: four of its eight are the ultimate under different spellings (ultimate, ultloop, ult, ulti).
      - GRIMexe: four of its eight are the BFG.
    - The offline tests pass, with three new checks. The fix is not re-shot; that would need a hub row.
  - The all-effects shot is too far away to read.
  - The floor reads mid-grey, not dark.
- **Closed cleanly:** no Unreal running, and the hook is deleted. The editor went to hippo effects for row 59.

## Tests (offline, 2026-11-18)
- `tests\test_offline.py`: 16 of 16 pass.
  - The effect picker and effect length run against a stand-in `unreal` module, with all paths in a temp folder.
  - The sheet writer runs on a made-up breakdown.
  - The gate check runs on frozen and moving image pairs.
- `tests\test_run_row.ps1`: 30 of 30 pass. The Unreal steps are stubs, and every path is a temp folder. It covers a
  foreign hook, a failed breakdown, a failed build, a good run, and a frozen gate (the stub editor gets stopped).
- **Not testable offline:**
  - whether the converter calls return what the header says;
  - whether the Emitter, exposure and realtime calls work as written;
  - whether the exposure looks right.
  The first row shows all of that, and the gate stops it early if nothing moves.

## Rules
- Paragon content stays in ParagonStudy and is never copied into MechMoba (hub rule). Only text sheets and frames come
  out, and they stay private.
- Before opening Unreal, take a hub queue row. Close only processes this row started, and delete the hook after.
