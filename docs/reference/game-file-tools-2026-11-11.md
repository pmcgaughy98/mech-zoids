# Game file tools: what each one gives the kit and art work (2026-11-11)

Preston listed these tools so we can study the games we care about. This file is the working knowledge: what each
tool reads, what is useful to us, and what is on his PC.

**The rule for everything extracted: study only, never ship.**
- Nothing pulled from another game goes into ours: no models, textures, animations, sounds or ability text. That is
  his standing rule (study, never copy) and it is also the legal line.
- **Terms of service:** these tools read the game's own files offline, but extracting may still break a game's
  terms. Keep everything private and on his PC.

## The table
| Game | Tool | Best for us | On his PC (checked 2026-11-11) |
|---|---|---|---|
| SMITE 1 (Epic) | UE Viewer (umodel) | god models and animations for motion reference; VFX textures | Preston says it is installed (not in the two default Epic folders checked); the tool is not downloaded |
| SMITE 2, Predecessor, Marvel Rivals | FModel | models, animations, VFX, and some data tables (UE4 and UE5 games) | games not installed |
| Paragon | Epic's free Paragon assets on Fab, opened in Unreal (or FModel) | full character models, animations and effects to study | Unreal is installing |
| Deadlock | Source 2 Viewer | **ability data with exact numbers** (the vdata scripts), plus models and animations | not installed |
| Overwatch | DataTool (command line) / TankView (browser) | **hero and ability list as text or JSON**, plus models, animations and voice lines | game installed at `D:\Program Files (x86)\Overwatch` (78.9 GB). The `C:` folder of the same name was a 0.2 GB leftover of runtime DLLs; it went to the Recycle Bin on 2026-11-12 at Preston's request. DataTool is at `D:\tools\game-extract\datatool` |

## What each one is for

### Overwatch: DataTool
Verified from the owlib README on GitHub:
- The project is overtools/OWLib, and releases come from the project's Discord.
- Commands take the form `DataTool.exe <overwatch_directory> <mode> [mode args]`.
- The kit catalog in one command:

  ```
  DataTool.exe "D:\Program Files (x86)\Overwatch" list-heroes --json --out="D:\tools\game-extract\dumps\overwatch\heroes.json"
  ```

- Also: `extract-unlocks`, `extract-maps`, `extract-hero-voice`. There is a Blender add-on for the models.

TankView is the same project's browser for the files. Not verified beyond its name.

### Deadlock: Source 2 Viewer (s2v.app)
- It reads Valve's VPK archives and decompiles them (verified from s2v.app).
- The Deadlock page says hero and ability stats live in the `scripts/heroes` vdata files. Modders work with
  `abilities.vdata` and `heroes.vdata` (from a public mod repo).
- **This is the most exact kit source of the lot:** every number for every ability, straight from the game.

### SMITE 2, Predecessor, Marvel Rivals: FModel
- It reads Unreal 4 and 5 pak files.
- Encrypted games need the game's AES key, which the community usually publishes. Not checked per game.
- Good for studying SMITE 2's ability effects (the look lane's quality bar) and animation timing.

### SMITE 1: UE Viewer (umodel)
- It reads Unreal 3 packages; SMITE 1 is an Unreal 3 game.
- Whether it needs a game-specific setting for SMITE was not checked.
- Use it for models and animations, not ability text.

### Paragon: the Fab release
- **Licence warning:** forum reports say the Paragon assets are licensed for Unreal Engine projects only. Our game is
  Godot, so they are study material, not assets. Check the licence on the Fab page before relying on that.

## Kit text vs art reference
- **For kit data:**
  - Deadlock (Source 2 Viewer) and Overwatch (DataTool) are exact and cheap: one dump each.
  - For League and SMITE, the wikis carry the ability text and numbers better than the game files.
- **For art and motion:** all of the tools. Play the extracted animations in Blender to study timing (anticipation,
  hold, recovery) and VFX layering. Then make our own.

## Installed 2026-11-11 (Preston: "Approve all downloads")
Everything lives in `D:\tools\game-extract\`, one folder per tool. C: has only 14 GB free, D: has 281 GB.

| Tool | Version, source | Size, SHA-256 (first 16 hex digits) | Check |
|---|---|---|---|
| FModel | `nov-2026`, github.com/4sval/FModel releases | 21,019,605 bytes, `209bef15402dd580` | unpacked to `fmodel\FModel.exe`; not code-signed (normal for its releases). **Needs .NET 10, which is not installed** (only 6.0.36 and 8.0.21 are). *Corrected 2026-11-12:* this first said it needs .NET 8. Windows' event log shows both launches on 2026-11-12 failing with "You must install or update .NET", framework 10.0.0 |
| Source 2 Viewer (GUI) | `20.1`, github.com/ValveResourceFormat releases | 105,383,576 bytes, `b41b28c6ea3d9260` | `source2viewer\Source2Viewer.exe`, signature valid (SignPath Foundation) |
| Source 2 Viewer (CLI) | `20.1`, same | 52,773,073 bytes, `67aaf8a67a85ca60` | `source2viewer-cli\Source2Viewer-CLI.exe`, signature valid; `--help` runs |

Empty folders are ready for `umodel\`, `datatool\` and `dumps\` (where text dumps go).

**The Deadlock kit dump, once the game is installed.** This is a guess at the paths; it is untested until Deadlock is
on disk:

```
Source2Viewer-CLI.exe -i "<Steam library>\steamapps\common\Deadlock\game\citadel\pak01_dir.vpk" -f "scripts/" -e "vdata_c" -d -o "D:\tools\game-extract\dumps\deadlock"
```

## Status after the second pass (2026-11-11, Preston: "I approve you to do 3-5 with computer use")
- **UE Viewer: works on SMITE 1.**
  - Preston downloaded it to `D:\Unreal`; it is unpacked in `D:\tools\game-extract\umodel\`.
  - SMITE 1 is at `D:\Program Files (x86)\SMITE` (found in the Epic manifests): 752 packages in
    `BattleGame\CookedPCConsole`.
  - UE Viewer needs `-game=smite` (from its readme). Tested:

    ```
    umodel_64.exe -game=smite -path="D:\Program Files (x86)\SMITE\BattleGame\CookedPCConsole" -list BACCHUS_ASSETS_SF.upk
    ```

    It listed 57,491 entries, including the god's animation sequences.
- **DataTool: runs, but there is no Overwatch to read.**
  - Preston's `toolchain-release.zip` (DataTool v2.25.1, which brings its own .NET 10) is unpacked in
    `D:\tools\game-extract\datatool\`.
  - Neither `C:\Program Files (x86)\Overwatch` nor `D:\Program Files (x86)\Overwatch` has the `.build.info` file a
    full install has. DataTool stops with "Invalid archive directory".
  - The C: folder holds only a few DLLs; Battle.net's default install path is `D:\Program Files (x86)`.
  - Overwatch needs installing or repairing in Battle.net. Then `list-heroes --json` should run.
- **Steam, all into `D:\SteamLibrary`:**
  - **SMITE 2 (37.8 GB): downloading.**
  - **Predecessor (26.5 GB) and Marvel Rivals (109.9 GB):** installing. Claude accepted both games' terms of
    service on Preston's "Yes, accept both" (Marvel Rivals' terms include binding arbitration).
  - Steam's manifests at the time:
    - SMITE 2: 3.3 of 27.6 GB downloaded;
    - Predecessor: 0.2 of 22.9 GB downloaded;
    - Marvel Rivals: queued behind them.
  - **Deadlock: invite-only.** Steam reports "No licenses", and the store page offers only a wishlist button.
  - `steam://` links did nothing until Steam was open. That is likely why the Run buttons failed.
- **Paragon on Fab: 40 packs are in Preston's library (2026-11-11).**
  - Preston signed in to Fab himself. Claude accepted the Fab EULA on his "Yes, accept it", ticking only the
    agreement box (no marketing box).
  - Each listing showed "Saved in My Library" after its Add click.
  - There are 37 heroes, plus Minions, the Agora and Monolith environment, and the Male Announcer.
  - The count comes from Fab's search for "Paragon" from seller Epic Games, which returned 40 Paragon-named listings
    after scrolling. The earlier note of 48 did not reproduce.
  - The Grux listing shows "Standard License", but its description says "free to use as you like in your Unreal
    Engine projects".
  - Treat them as study only either way.
  - **Opening them in Unreal: approved by Preston ("I give you permission to open them in unreal").** Status on
    2026-11-12:
    - **Engine:** Unreal Engine 5.8 is installed at `D:\Unreal\UE_5.8` (Preston, then checked on disk). Claude first
      misread this, because Epic's install list (`LauncherInstalled.dat`) shows only SMITE.
    - **Space is fixed.** Preston uninstalled XCOM 2 and Warframe, and D: has 225.3 GB free.
    - **Steam:** SMITE 2 and Predecessor are installed. Marvel Rivals is at 13.3 of 105.9 GB, and Steam shows it as
      paused; Claude did not touch Steam.
    - **Study project:** `D:\Unreal Projects\ParagonStudy\ParagonStudy.uproject`. It is on D: on purpose, because
      Unreal's default project folder is inside OneDrive Documents.
    - **Unreal 5.8 starting slowly: the cause is the D: drive, not Unreal.**
      - **The stalls:** Preston's two launches (06:18 and 06:19) and Claude's first launch stalled for over 15 minutes
        after loading 292 libraries. They had no window and wrote no log. They couldn't be force-closed and cleared
        on their own around 06:39. The Overwatch DataTool run stalled in the same window, right after reading the
        game's manifests (06:28). It never recovered: no new log lines and 10.6 s of CPU in 7 hours, so Claude
        stopped it at about 13:15. No `heroes.json` was written. Rerun the same command once the Paragon downloads
        finish and D: is quiet.
      - **The drive:** D: is a spinning hard drive (Seagate ST1000DM010, 1 TB). Windows reports it healthy. At 06:41
        it was saturated: 14.6 requests queued, active about 1,457% of the time (over 100% because requests overlap),
        and only 8 MB/s throughput. That is random-access thrashing. The busiest single process wasn't
        identifiable from the counters.
      - **Likely load at the time (not confirmed):** the XCOM 2 and Warframe uninstalls (about 126 GB of deletes),
        Steam and Battle.net installs, and antivirus scanning of the new files.
      - **The verify:** Claude started it at 06:37 on Preston's "Yes, close and verify". It was cancelled at 06:39
        with reason "User", not by Claude.
      - **The relaunch:** at 06:40, Claude's relaunch of the study project got further. It wrote
        `D:\Unreal Projects\ParagonStudy\Saved\Logs\ParagonStudy.log` and was loading editor modules.
      - **Expect first opens to be slow on this drive:** 548 editor libraries, then first-time shader compiles.
      - **C: space risk:** Unreal's shared cache (Zen) lives on C: (`%LOCALAPPDATA%\UnrealEngine\Common\Zen`), and C:
        has 27 GB free. Opening 40 Paragon packs could grow that cache a lot; the size is not measured.
    - **The launcher side works.** Its Unreal Engine > Library tab lists the Fab packs with "Add To Project" buttons.
      It shows "No user projects found" until the study project has been opened once in the editor.
    - **Progress, 2026-11-12:**
      - **Project registered:** the launcher found ParagonStudy only after Claude wrote
        `%LOCALAPPDATA%\UnrealEngine\5.8\Saved\Config\WindowsEditor\EditorSettings.ini`, with `CreatedProjectPaths` and
        `RecentlyOpenedProjectFiles` pointing at it. The editor hadn't saved its own settings yet.
      - **Aurora (first pack):** added and verified, which also confirms the packs support 5.8. It has 2,194 files:
        1,669 in `Content\ParagonAurora` (2.72 GB), and 525 in the project's `Intermediate` and `Saved` folders.
        (Corrected 2026-11-12. This line first said all 2,194 were in Content. A file-by-file check against the
        cache found all 2,194 present with matching sizes.) It sits in the launcher's cache as well, so the cache on C: grew
        to 2.97 GB (24.0 GB free on C: afterwards).
      - **Cache moved:** on Preston's "Yes, move it to D:", Claude changed the launcher's vault cache
        (Download Settings > Cache Directory) to `D:\EpicVaultCache`. The launcher log shows
        `OnVaultCacheLocationSelected FolderName D:/EpicVaultCache`. The settings field still showed the C: path
        right after, so check on the next download where it caches.
      - **Disk math for the rest:**
        - Each pack costs about double on disk, once in the cache and once in the project. At Aurora's size, the
          other 39 would be about 100 GB in the project plus about 100 GB of cache.
        - D: has about 225 GB free, and Marvel Rivals still needs about 92 GB.
        - So all 40 only fit if the cache is cleared as packs finish, or if fewer packs are added.
        - Aurora's 2.2 GB copy is still in the old C: cache.
      - **The mech-relevant dozen (Preston: "Mech-relevant dozen"), queued 13:11 to 13:20:**
        - Packs: Howitzer, Riktor, Rampage, Grux, Khaimera, Steel, Crunch, Sevarog, GRIM.exe, Wukong, Iggy & Scorch,
          Kwang. Each showed "Queued" in the launcher after its add.
        - **Cache move confirmed:** the launcher log shows Howitzer's
          `InstallDirectory: D:/EpicVaultCache/VaultCache/ParagonHowitzer/data`. C: stayed at 24.0 GB free.
        - **Howitzer done:** 1.98 GB downloaded, and `Content\ParagonHowitzer` arrived. Project content is now
          4.67 GB (Aurora 2.72 + Howitzer about 1.95).
        - **All 12 landed and verified:** each logged `AlertCode=[ok]`, and every cached file was found in the project
          with a matching size (0 missing, 0 size differences). Project Content is now 29.71 GB.
        - **Caches deleted** on Preston's "Yes, after they land": the 12 D: cache folders and Aurora's old C: copy.
          Afterwards C: had 26.7 GB free and D: 194.6 GB. One folder that isn't from these packs is still in
          `D:\EpicVaultCache\VaultCache`; it was left alone. Re-adding a pack to another project means downloading it again.
        - **Overwatch dump rerun: worked.** With D: quiet it finished in 5.4 s (build 2.25.1.0.155284) and wrote
          `D:\tools\game-extract\dumps\overwatch\heroes.json` (307 KB). That points at the busy drive as the cause of
          the first run's hang.
          - **Contents:** 135 entries, 54 of them heroes (Damage 23, Support 16, Tank 15). Each hero has a name,
            class, lore description and a Loadouts list: 141 abilities, 57 ultimates, 84 weapons and 47 passives,
            plus subrole and stats entries. All 54 heroes also carry Perks, with the same fields.
          - **What it is not:** the ability text is a one-line description ("Teleport to a targeted location."),
            and only 22 of the loadout descriptions contain any digits at all. There are no damage, cooldown or
            range numbers, so for exact numbers Deadlock's vdata is still the source.
          - **Reading it:** Windows PowerShell 5.1 showed "LÃºcio" and "TorbjÃ¶rn", which is what happens when UTF-8
            is read as ANSI. Pass `-Encoding UTF8` to `Get-Content`. The file itself was not checked byte by byte.
          - **Closest to the mechs:** Winston (gorilla), Wrecking Ball (animal piloting a mech), Jetpack Cat, and
            D.Va, Orisa, Bastion and Ramattra for machine kits.
        - **Disk math:** at 2 to 3 GB per pack, the 11 left take 22 to 33 GB of cache plus the same again in the
          project, so 44 to 66 GB. D: had 218.1 GB free. 218.1 - (44 to 66) - 92 for Marvel Rivals leaves
          60 to 82 GB.
        - **Cleanup:** the D: cache copies can be deleted once a pack is in the project. Deleting them needs
          Preston's OK, and so does deleting Aurora's old copy on C:.
    - Predecessor's heroes come from the same Paragon release, so FModel on Predecessor covers much of the same
      study material.

## Status 2026-11-12 (Preston: "all games and tools should be downloaded")
Checked on disk (Steam install records, Epic's install list, the game folders):

| Game | Where | Size | Files | Kit dump |
|---|---|---|---|---|
| Overwatch | `D:\Program Files (x86)\Overwatch` | 78.9 GB | CASC | **done:** `dumps\overwatch\heroes.json`, 54 heroes |
| SMITE 2 | `D:\SteamLibrary\steamapps\common\SMITE 2` | 27.8 GB | IoStore: 3 .ucas (26.1 GB) | **done from the web:** `dumps\smite2\abilities.md`, 48 gods, 240 abilities (game files: text pak needs a key) |
| Predecessor | `D:\SteamLibrary\steamapps\common\Predecessor` | 25.5 GB | .pak (23.0 GB) | **done from the web:** `dumps\predecessor\abilities.md`, 56 heroes, 336 abilities (game files need a key) |
| Marvel Rivals | `D:\SteamLibrary\steamapps\common\MarvelRivals` | 109.9 GB | IoStore: 43 .ucas (93.1 GB) plus .pak | **done from the web:** `dumps\marvel-rivals\abilities.md`, 51 hero pages (game files need a key) |
| SMITE 1 | `D:\Program Files (x86)\SMITE` | 20.7 GB of .upk | Unreal 3 packages | art only (UE Viewer) |
| Deadlock | **not installed:** no Steam record and no folder in either library | | | blocked |

- **Tools all present:** FModel, Source 2 Viewer (GUI and CLI), DataTool and TankView, and UE Viewer (`umodel\umodel_64.exe`).
- **The cheap route to kit text in the Unreal games:** each game's English localisation file (`.locres`) holds
  every ability name and description. FModel can open it and export it as JSON, one file per game. Checked
  2026-11-12: all three games keep that file behind an AES key (see "FModel, third try" below).
- **FModel has never been set up** (no settings file in `%APPDATA%\FModel`). Its first run asks for the game
  folder and the Unreal version. Claude launched it on 2026-11-12, and Preston declined computer-use access to
  it, so it was not driven. It was left open.
- **FModel, second try (2026-11-12, Preston: "Let Claude drive it"):**
  - .NET 10.0.15 Desktop Runtime installed on his yes: 57.3 MB from builds.dotnet.microsoft.com, SHA-512 matched
    Microsoft's release list, valid Microsoft signature, installer exit code 0. FModel 4.4.4 now starts.
  - It only detects Fortnite and Valorant. Typing SMITE 2's pak folder
    (`...\SMITE 2\Windows\Hemingway\Content\Paks`, version GAME_UE5_4) into the Directory Selector and pressing OK
    restarts FModel without saving anything, and the restart crashes with a NullReferenceException in
    `AvoidEmptyGameDirectory`. This happened twice, the second time with only one copy running. The settings
    folder `%APPDATA%\FModel` stays empty.
  - The selector says to drag and drop the game folder onto it. Claude's computer use can't drag from Explorer,
    so that step needs Preston (one drag), or a long click-through of the folder picker.
  - **Engine versions read from the files:** SMITE 2's IoStore table of contents is version 8, which points to
    Unreal 5.4 or later (Gildor's forum says 5.5 since March 2026). Marvel Rivals' is version 5 (an earlier UE5).
    Predecessor uses classic pak version 11.
    *Corrected 2026-11-12:* this first said Predecessor's pak index is unencrypted. Its footer flag says
    encrypted; see the next bullet.
- **FModel, third try (2026-11-12): SMITE 2 loads, but every text file is behind a key.**
  - Preston's drag did not register (FModel loaded Fortnite). Claude closed FModel cleanly, backed up
    `%APPDATA%\FModel\AppSettings.json` to `AppSettings.backup-2026-11-12.json`, and added SMITE 2 as a manual
    game in the file (PerDirectory and ManualGames, GAME_UE5_4, no endpoints, empty key). The script is
    `add_game.py` in the session scratchpad; it takes name, pak folder and version number.
  - **SMITE 2 now opens:** 380,979 files mounted from the two IoStore containers, which are not encrypted.
  - **Encryption, read from each archive's footer or header on 2026-11-12:**

    | Game | Locked | Open |
    |---|---|---|
    | SMITE 2 | `pakchunk0-Windows.pak` (121.6 MB), index encrypted. This is where the non-asset files live, the `.locres` text included. | both `.utoc`/`.ucas` containers, so the ability assets themselves |
    | Predecessor | its one archive, `pakchunk0-WindowsClient.pak` (24.6 GB), index encrypted | nothing |
    | Marvel Rivals | 41 of 43 `.utoc` containers and every `.pak`, including `pakchunkLocres-Windows.pak` (49.8 MB) | 2 containers |

  - **Where keys are posted:** none of the three is in FModel's public key list (github.com/FModel/Unreal-Game-Keys,
    checked 2026-11-12). Gildor's SMITE 2 topic points to a cs.rin.ru thread, a piracy forum. Claude did not go
    there and won't. The other way to get a key is a dumper run on the game's own .exe (for example AESDumpster
    from GitHub), which is a download Preston has not approved.
  - **Key-free routes:** (a) SMITE 2 only: ability names and descriptions are also stored as English source text
    inside the ability assets, which sit in the open containers. FModel can export those assets raw, and the text
    can be pulled out of the bytes without the key. (b) All three: the public wikis carry every ability's name and
    description.
  - FModel was left open with SMITE 2 loaded and its update notice showing.
- **Kit text from the web instead (2026-11-12, Preston: "Wikis, all three").** All in `D:\tools\game-extract\dumps\`,
  study only. Scripts are in the session scratchpad (`pull_wikis.py`, `smite2_pull2.py`).

  | Game | Source | Got | Files | Gaps |
  |---|---|---|---|---|
  | SMITE 2 | the official site's own data feed, `webcms.hirezstudios.com/smite2/api/gods/?populate=*` (the site reads it; no key or sign-in) | 48 gods, 240 abilities (4 plus a passive each), with role and pantheon | `smite2\abilities.md`, `gods-raw.json` | The feed lists 48 gods. Whether the live roster is larger was not checked. Descriptions have no numbers. |
  | Predecessor | omeda.city's public `heroes.json`, which carries the in-game ability text | 56 heroes, 336 abilities, with class and role | `predecessor\abilities.md`, `heroes.json` | Numbers sit in `{placeholders}` in `game_description`. `menu_description` in the JSON has the per-level values. |
  | Marvel Rivals | marvelrivals.wiki.gg's API (the "Abilities" section of each hero page) | 51 hero pages | `marvel-rivals\abilities.md`, `abilities-wikitext.json` | The four Deadpool pages and White Fox (a stub) had no ability headings the script could read. |

  - SMITE 2's official wiki (wiki.smite2.com) answers scripts with a bot check. Claude did not try to get past it.
  - **Done 2026-11-12:** `docs/reference/moba-kit-catalog-2026-11-11.md` was checked against these three dumps
    and Overwatch's. Corrections are marked in the catalog.
- **Key dumper (2026-11-12, Preston: "Download dumper 1.2.5").** AESDumpster 1.2.5 from github.com/GHFear/AESDumpster:
  49,152 bytes, SHA-256 `2C0C0DE4853EB4988C4739C9714F6960A928B61527B9C98A7BADCA7291C917BB`, unsigned, and Windows
  Defender found no threats. It is in `D:\tools\game-extract\aesdumpster-1.2.5\`. Version 1.3 is online-only and was
  not used, because it would upload the game exe. Each run took a few seconds, on the exe on disk with the games closed.

  | Game | Key | Text pulled |
  |---|---|---|
  | SMITE 2 | its own exe's key opens `pakchunk0-Windows.pak` | `smite2\locres\...HemingwayGame.json`, 23,846 strings. `smite2\abilities-game.md` lists 104 gods with ability names. |
  | Predecessor | its own exe's key opens `pakchunk0-WindowsClient.pak` | `predecessor\locres\...Game.json`, 11,050 strings |
  | Marvel Rivals | none of the 3 candidates opens `pakchunkLocres-Windows.pak` | nothing; the web pull stands |

  - **SMITE 2's site feed is far behind the game.** The game files name 137 gods, against the feed's 48. Some may be
    unreleased. Hel is among them.
  - `abilities-game.md` is rough: some entries are talents or stat labels, and some abilities have no description
    matched.
  - The keys are in `D:\tools\game-extract\aes-keys.json`, outside the repo. Oodle decompression used FModel's own
    `oodle-data-shared.dll`. The script is `keytest.py` in the session scratchpad.
- **What the dumps are for:** `docs/reference/moba-kit-catalog-2026-11-11.md` quotes kits from these games from
  memory. Full rosters would check it and widen the four-layer study (how heroes mix body, power, weapon and nod).

## Manual steps, ready for Preston
1. **UE Viewer.** Done (Preston's download).
2. **DataTool.** Done (Preston's download). Overwatch itself still needs installing in Battle.net.
3. **The games, through Steam, into a library on D:.** C: is too full. App IDs were confirmed with the Steam store
   API:
   - Deadlock 1422450 (access may still need a playtest invite; not checked);
   - SMITE 2 2437170;
   - Predecessor 961200;
   - Marvel Rivals 2767030.

   Install sizes were not checked; expect tens of GB each.
4. **Paragon.** All 40 packs are added to the library (done 2026-11-11). What's left is opening them in Unreal from
   the Epic launcher. They are Unreal-only, so study only.
5. **SMITE 1.** It is not in the default Epic folders. Tell Claude the install folder.
