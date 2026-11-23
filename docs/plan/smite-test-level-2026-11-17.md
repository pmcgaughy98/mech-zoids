# SMITE test level: gods and mechs side by side (plan, 2026-11-17)

Preston, 2026-11-17: "Can we add a smite test enviroment I can add my mechs too with the gods etc."

Nothing is built yet. This note says what is on disk, what one test export showed, and the one choice that
decides how it gets built.

## On disk (checked 2026-11-17)
- **SMITE 1:** `D:\Program Files (x86)\SMITE\BattleGame\CookedPCConsole`, 752 packages, opened with UE Viewer
  (`D:\tools\game-extract\umodel\umodel_64.exe -game=smite`). These ode gods each have a package
  (`<NAME>_ASSETS_SF.upk`, plus LOBBY and UI ones): Agni, Cernunnos, Geb, Izanami, Kukulkan, Kuzenbo, Thor. Ymir and
  Yemoja were not checked (the listing was cut off).
- **Earlier SMITE exports:** `D:\dev\_scratch\smite-study-2026-11-08` has Hun Batz and Raijin. Their mesh,
  skeleton and animations exported fine and went into Blender, with run-cycle measurements in `clip-metrics.json`.
- **Paragon:** `D:\Unreal Projects\ParagonStudy`, 13 heroes, 31.9 GB, full quality with animations: Aurora, Crunch,
  GRIM.exe, Grux, Howitzer, Iggy & Scorch, Khaimera, Kwang, Rampage, Riktor, Sevarog, Steel, Sun Wukong.
- **SMITE 2:** installed, but its files need an AES key and FModel crashed on setup (`game-file-tools-2026-11-11.md`,
  "FModel, second try"). Not used here.

## Test export today: Geb's textures
- `GEB_ASSETS_SF`: 289 textures, 268 of them point to a texture cache named "automated" that isn't on disk.
- `GEB_LOBBY_ASSETS_SF`: 368 textures, 358 point to the same missing cache. The lobby package doesn't get around it.
- The 42 cache files on disk have other names (`CharNormals0.tfc` and so on), so UE Viewer can't find them.
- **What that means:** SMITE 1 gods come out at full shape, skeleton and animation, but with tiny textures (64 px).
  That's enough to compare scale, silhouette and timing, but not for judging looks. Paragon heroes don't have
  this problem.
- Test files: `D:\dev\_scratch\smite-testlevel\tex-test` (scratch, private).

## The choice: where it lives
- **A. The study project (`ParagonStudy`), recommended.** The gods, the Paragon heroes and copies of the mech models
  go in one sandbox level. You can look, play clips side by side, and walk a mannequin around. The SMITE files never
  touch the game project or git. The mech kits don't run there.
- **B. The game project (`D:\dev\mech-moba-unreal`), in a folder git ignores.** You drive a mech with its kit next
  to the gods. It needs editor time from the hub queue. If the folder ever got committed, Hi-Rez files would be in
  the repo.

## Build steps after the pick
1. Export the ode gods: mesh, skeleton, and an idle, a run, and the basic attacks. Path: UE Viewer, then Blender
   (the same path as Hun Batz), then FBX into Unreal.
2. Build a flat test level with a 1 m grid, a lane-width strip and height markers. Check each god's height against
   SMITE's own numbers before trusting scale.
3. Put the gods and the Paragon heroes on plinths, each playing its idle, with a sign showing its name.
4. Bring in the mechs' approved 3D models next to the god each one is an ode to (gorilla by Geb, pistol shrimp by
   Thor, and so on).
5. Write a short how-to for adding one more mech or god.

## Rules
- The SMITE files belong to Hi-Rez. They're private reference only: never committed, never shipped, and nothing is
  copied from them into a mech. Kits keep using the gods as theme only (`moba-kits.md`).
- Before opening the Unreal editor, read the hub's newest events and take a queue row.

## Progress, same day (Preston picked "Study project")
- **Exported:** all 23 ode gods' meshes and skeletons, as glTF in `D:\dev\_scratch\smite-testlevel\gods\<god>\`
  (140 MB). The list is in `manifest.json`. Heights range from 0.59 m (Cupid) to 3.64 m (Medusa); most gods are
  1.3 to 1.6 m.
  - The 17 odes: Cabrakan, Geb, Bacchus, Ares, Vulcan, Khepri, Ravana, Kuzenbo, Thor, Thanatos, Medusa, Thoth, Rama,
    Loki, Ratatoskr, Cupid, Janus.
  - The 6 planned mages: Kukulkan, Agni, Cernunnos, Izanami, Yemoja, Ymir.
- **Kukulkan fixed:** the first pass took `skl_god_aokuang` (Ao Kuang). The animation pass picks the mesh with the
  god's own name, `skl_god_kukulkan`.
- **Animations done, same day (Preston: "Yes" to the add-on):**
  - Blender's "Unreal PSK/PSA" extension (`io_scene_psk_psa`, 82 KB, from Blender's extensions site) is
    installed in Blender 5.2.
  - UE Viewer exports each god's mesh as `.psk` and its non-skin anim sets as `.psa`.
  - `convert_god.py` builds one `<god>_anim.glb` per god: the mesh, every clip as its own animation, and UE
    Viewer's textures (still 64 px).
  - `anim_pipeline.py` runs the 23 gods and records everything in `manifest.json`.
- **Results:** 23 of 23 gods, 56 (Yemoja) to 358 (Cupid) clips each, 1.3 GB in total. Loki and Cupid have duplicate
  clip names (`.001`) because their v2 anim sets overlap. Cupid has no clip named "idle" among its first 80.
- **Not checked:** how the clips look. The first look will be in the Unreal run.
- **Level script drafted, outside the project:** `D:\dev\_scratch\smite-testlevel\build_level.py`. It does the
  following:
  - Imports the gods and the mech models from `mech-moba-unreal\SourceArt\Models`.
  - Builds `/Game/SmiteRef/L_GodsAndMechs` in ParagonStudy: a grid floor and sky; each mech next to its ode god,
    7 m apart, with a name and height sign; and a row of the 13 Paragon heroes.
  - Six mechs only have older 2026-11-07 display models (pistol shrimp, wolf, shoebill, falcon, chameleon,
    squirrel) and are labelled "older model". The lobster has no model.
- **Waiting on an editor slot:** one Unreal editor at a time, across all lanes. ParagonStudy also needs the Python
  script plugin turned on in its `.uproject` first.
- **Booked, 2026-11-17:** the hub gave it row 35, last in the queue (after 27 to 34). The map lane
  (`local_6d56ace9`) hands over the slot; don't start Unreal before that, even though this is a different project.
  The rules for the run:
  - ParagonStudy only; MechMoba glbs are read only.
  - Paragon content stays inside ParagonStudy and is never copied into MechMoba.
  - When done, report to the hub (`local_b046f4d1`). The hub changed the handoff twice mid-run; the latest:
    the editor goes to the cobra session (`local_2b969540`) for row 36, the cobra re-import.
  - Screenshots: no desktop capture (gdigrab or screen grabs). In row 31 that recorded Preston's browser
    instead of the game. Unreal writes its own frames (`HighResShot` or `-dumpmovie`).

## Row 35 result (2026-11-17 evening)
- **Built and saved:** `/Game/SmiteRef/L_GodsAndMechs` in ParagonStudy. It has:
  - 23 gods, 15 mechs and 13 Paragon heroes;
  - a 1 m grid floor, sky and sun;
  - a sign on every model with its name and height.
  The build logged 0 errors. Numbers are in `D:\dev\_scratch\smite-testlevel\build_report.json`.
- **To look at it:** open ParagonStudy, then open `Content/SmiteRef/L_GodsAndMechs`. The layout:
  - mechs on the y=0 row, each ode god 5 m to its right, one pair every 7 m;
  - the Paragon row at y=-15 m.
- **Clips:** each god carries 16 to 33 key clips: idles, forward runs, basic attacks (`fire_*`) and abilities
  (`offhand_*`). They come from `<god>_ref.glb`, written by `trim_clips.py`. The full sets stay in
  `<god>_anim.glb`.
- **Heights:**
  - The gods imported about 100x too small. The script rescaled each one to the height measured from the SMITE
    export, so they range from 0.59 m (Cupid) to 3.64 m (Medusa); most are 1.3 to 1.6 m.
  - The Paragon heroes are 1.81 m (Aurora) to 3.55 m (Steel). SMITE gods are smaller than Paragon heroes in
    their own engines.
  - 8 of the rigged mechs are exactly 1.70 m (rhino, gorilla, bison, kangaroo, pangolin, cobra, hummingbird,
    fennec), so their export seems to have normalized height. Hippo is 1.47 m. In-game scale lives in MechMoba
    and was not checked.
- **What went wrong on the way:**
  - The first try imported inside the full editor and crashed out of video memory (5.2 GB budget) during the
    13th god, while rendering import thumbnails.
  - The fix that worked: imports and the level build run headless (`UnrealEditor-Cmd -run=pythonscript
    -nullrhi`), in 7 min 20 s.
- **Frames: not taken that night.** Both editor frames passes quit (`QUIT_EDITOR`) during the shader wait.
  - **Correction, 2026-11-18:** I first reported this as someone closing the window from outside. That was wrong.
  - Every quit came on the editor's first frame after the script returned (frame counter `[3]`). That is
    `-ExecutePythonScript` itself: it runs the script and then quits the editor.
  - The fix is a normal editor start with a temporary `Content/Python/init_unreal.py` hook in ParagonStudy, which
    does nothing unless `SMITEREF_MODE=frames` is set. Delete the hook after the run.
  - Each pass also spends about 20 to 28 minutes opening the editor and loading the level.
- **Known small fixes for a rebuild:**
  - Thoth idles on `offhand_02_idle`: the "idle" key matched before `idle_com`.
  - Rampage, Steel and Khaimera picked ability or odd idles.
  - Iggy & Scorch's idle is an additive clip, so it doesn't play.
  - Which way the models face hasn't been seen yet.

## Frames retake: row 39 (booked 2026-11-17, Preston: "Yes, book a row")
- It comes after row 37 (look lane) and row 38 (gorilla effects, `local_6fd7e1a5`). Gorilla effects hands the
  slot over directly. When done, hand the editor to gorilla 3D (`local_f7ccf9b5`) for row 40, the Chest Beat dome
  (the hub's latest change), and report to the hub.
- It runs `run_row.ps1`: a headless rebuild with no re-import that fixes the idle picks, then the frames pass.
- The two closes turned out to be `-ExecutePythonScript` quitting by design (see the correction above). No lane and
  not Preston. The rebuild in row 39 worked: 0 errors, idle picks fixed. The frames pass then quit the same way
  once more, and was rerun with the `init_unreal.py` hook.

## Row 39 frames: what they showed (2026-11-18)
- All 28 frames were written by Unreal (HighResShot). They're in `D:\dev\_scratch\smite-testlevel\frames`, with
  one contact sheet at `frames_contact_sheet.jpg`.
- **The gods are about 100x too big.** My earlier height fix was wrong:
  - The god meshes report bounds about 100x too small, but they render at the right size. The x100 rescale made
    them about 150 m tall.
  - So each pair frame shows one giant god, and the mech is a speck at its feet.
  - The heights on the signs and in the report were computed from those same bounds, so they matched the export
    numbers by construction. They were not a check.
- **Fixed in `build_level.py`:** gods keep scale 1, and the signs use the height measured from the SMITE export.
  The fix needs a level rebuild plus frames: about 1 hour of editor time, which means a new queue row.
- **The gods render untextured (white).** The 64 px SMITE textures didn't come through the PSK/glTF path. Not
  fixed.
- **Paragon frames are correct:** textured heroes on the grid with signs. Iggy & Scorch still has the additive idle.
- **Correction (2026-11-18, after row 46):** row 39's rebuild also failed to save. Its `rebuild_run.log` has the
  same NewLevel and SaveCurrentLevel errors. So row 39 filmed the row 35 level, and the idle-pick fix (no
  offhand, ability or attack clips) has never been on camera either. Row 39's frames are now in `frames_row39`.

## Reshoot: row 46 (booked 2026-11-18, Preston: "Yes, book it")
- Bison effects (`local_a357c88a`) hands over the slot after row 45. That's several hours away; rows 40 to 45 come
  first.
- It runs `run_row.ps1`: a headless rebuild with the scale fix, the `init_unreal.py` hook, the frames pass, then
  the hook is deleted.
- When done, hand the editor to the map lane (`local_6d56ace9`) for row 47a, the floor-shadow fix. This is the
  hub's latest word, which replaces its earlier changes. Report the frames path, shot count and errors to the hub.

## Row 46 result (2026-11-18, 12:39 to 13:09): failed, my bug
- 28 frames, 0 frame errors, but they show the old level with the giant gods again. The scale fix never reached
  the level.
- Cause: the headless rebuild couldn't replace the saved level. `delete_asset` fails quietly on a saved map,
  `new_level` then refused the path ("an asset already exists"), and `SaveCurrentLevel` had no filename. The
  rebuild exited with code 1, and `L_GodsAndMechs.umap` kept its 2026-11-17 19:18 timestamp. `run_row.ps1` ran
  the frames pass anyway.
- Fixed in `build_level.py` (not yet run):
  - If the level exists, the build loads it, clears every actor except WorldSettings and the brush, and rebuilds.
  - A failed save is logged as an error.
  - The frames pass logs grouped actors that are missing from the loaded level.
- Fixed in `run_row.ps1`:
  - The old `.umap` is moved out of Content to `level_backup` before the rebuild, so the build takes the
    `new_level` path that worked in row 35. Load-and-clear is only the fallback.
  - The frames pass is skipped unless the `.umap` was written after the rebuild started (`$t0`). If it wasn't,
    the old level is restored from the backup.
- Checked in `build_report.json` from the 12:41 rebuild (in memory, never saved): all 23 gods carry
  `bounds_off_by` (about 100) at scale 1, and no mech does. So the scale fix itself works; only the save failed.
- Row 39's frames are in `frames_row39`. Row 46's 28 frames are still in `frames` (they duplicate row 39's
  level), and the next frames pass deletes them.
- The editor went to the map lane for row 47a. The hub was told and asked for one more row (about 35 minutes).

## Retry: row 51 (booked by the hub 2026-11-18)
- Pangolin effects (`local_6b58b313`) hands over the editor after its row 50. When done, hand the editor to the
  look lane (`local_90045777`) for row 52, not back to the hub. This is the hub's later change. Still report to
  the hub.
  Ahead: 47a map, 47b look lane, 48 gorilla dome, 49 bison fixes, 50 pangolin burst ring.
- The hub asked for an offline test of the save guard first. It's `D:\dev\_scratch\smite-testlevel\tests\test_run_row.ps1`:
  - The rebuild and frames steps are `.cmd` stubs, and every path is a temp folder, so ParagonStudy is never
    touched. `run_row.ps1` takes parameters for this; a real row uses the defaults.
  - Three cases: a failed save over an old level, a good save, and a failed save with no old level.
  - The 2026-11-18 run passed all 12 checks. A failed save exits with code 2, skips the frames pass, restores the
    old level and leaves no hook folder. A good save exits 0 and runs the frames pass.
  - Not tested offline: whether Unreal itself saves now. Only row 51 can show that, and if it doesn't, the guard
    stops the row safely.

## Row 51 result (2026-11-18, 15:00 to 15:23): level saved, 28 frames
- **Rebuild:** 15:00 to 15:05, exit 0.
  - The level saved at 15:05:26, so moving the old .umap out first worked.
  - Build report: 23 gods, 15 mechs, 13 Paragon heroes, 0 errors.
  - The old level is kept in `D:\dev\_scratch\smite-testlevel\level_backup`.
- **Frames:** 15:07 to 15:23, exit 0. 28 frames, 0 frame errors, no grouped actor missing, and the hook is removed.
  The frames are in `frames\`, with the contact sheet at `frames_contact_sheet.jpg`. The sheet was sent to Preston.
  The editor went to the look lane for row 52, and the hub has the report.
- **What the frames show:**
  - The gods are now the right size next to the mechs: the scale fix is confirmed on camera.
  - **Gorilla and pangolin are wrong (my bug).** The build took the first mesh in each machine folder, which was a
    part mesh:
    - gorilla got `Shield_R_Cells` (0.41 m) instead of `Gorilla_Body`;
    - pangolin got `scrap_shell` (0.24 m, 100x rescale) instead of `output_unwrapped`. Its idle also came out as
      `Pangolin_Ball_Roll1`, because only `scrap_shell`'s clips were searched.
  - The pangolin pair was framed from far away. The likely cause is the same wrong mesh; not confirmed.
  - **Geb shows as three or four overlapping figures.** The cause isn't known yet. `geb_ref` is the only mesh in
    its folder, so it isn't a pick problem.
  - The gods are still untextured white (open since row 35).
  - Seven gods stand alone because their machines have no model in `MECHS`: Khepri (lobster), Kukulkan
    (albatross), Agni (firehawk), Cernunnos (sloth), Izanami (anglerfish), Yemoja (axolotl), Ymir (wood frog).
  - The older display models are tall next to the gods: shoebill 3.2 m, squirrel 2.95 m, falcon 2.2 m.
    Their scale is not calibrated.
- **Fix, done offline after the row:** `pick_mesh()` in `build_level.py` now picks, in order:
  - the mesh most clips share a skeleton with;
  - then a mesh whose name contains the machine;
  - then the biggest one.
  It records the other meshes as `skipped_meshes` in the report. py_compile passes, but it can't be checked without
  Unreal, so it's unverified until a reshoot. No row is booked for that; it waits on Preston.

## How to add one more god or mech
1. **God:**
   - Add a `(machine, GOD)` line to `ODES` in `export_gods.py` (scratchpad copy), then run it.
   - Then run `anim_pipeline.py` with `ONLY=<god>`, then `trim_clips.py`.
   - The god's `machine` must match the mech key below for the two to stand together.
2. **Mech:** add `"machine": "file.glb"` to `MECHS` in `build_level.py`. The file is read from
   `mech-moba-unreal\SourceArt\Models`, read only. Add the key to `OLD` if it is a 2026-11-07 display model.
3. **Book a hub queue row**, then run the headless build:
   - `SMITEREF_MODE=build UnrealEditor-Cmd.exe "D:\Unreal Projects\ParagonStudy\ParagonStudy.uproject"
     -run=pythonscript -script=D:/dev/_scratch/smite-testlevel/build_level.py -nullrhi -unattended`
   - Add `SMITEREF_SKIP_IMPORT=1` to only rebuild the level.
4. **Frames:** put the `init_unreal.py` hook back in `ParagonStudy\Content\Python\` (copy it from
   `D:\dev\_scratch\smite-testlevel\`). Then `run_frames.ps1` opens the editor normally with
   `SMITEREF_MODE=frames`, and Unreal writes one frame per pair to `frames\`. It needs about 35 minutes of editor
   time. Don't use `-ExecutePythonScript`: it quits the editor as soon as the script returns.

## Not checked yet
- Any way around the "automated" texture cache problem.
- How the clips look in motion: the row 51 frames are stills only. Facing looks right at contact-sheet size, but I haven't checked frame by frame.
- Why Geb renders as several overlapping figures.
- Whether Ymir and Yemoja have packages (they exported fine, so yes in practice).
