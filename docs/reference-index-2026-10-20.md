# Reference index, 2026-10-20

What models, sprites, concepts and references the mech game holds, where they sit, and what git does with them.
Built from a full file listing of `D:/dev/new-mech-rpg` (36,335 files, 4.76 GB, not counting `.git` and `.godot`)
plus `git ls-tree`, `git status` and a scan of every reachable object. Counts, not image-by-image review.
Nothing was committed, pushed, moved or deleted.

## Short version

- 36 3D files: 8 `.glb`, 15 `.blend`, 13 `.blend1` backups. No `.fbx`, `.obj` or `.gltf` anywhere.
- Only the gorilla (`ape_l`) has a game model (`art/machines/ape_l/ape_l.glb`, 19.0 MB). The other five machines are `.blend` only.
- Six machines have installed 8-view sprites (all 8 of 8) and 6 or 7 animation clips each.
- Animation frames face east only. 8,091 of the frame files are `e`. No clip has 8 directions.
- 34,119 render-round files (4.5 GB) under `docs/art/2d/*/` are git-ignored. They exist only on this hard drive.
- That ignored set includes AI concepts the factory scripts cannot remake (Codex, Opal, Grok packs).
- No file over 50 MB anywhere: working tree, history, or `.git`. Largest is `ape_l.glb` at 19.0 MB.

## 1. 3D models

### Machines

| Machine | Game model (`art/machines`) | Source in `docs/art/3d` | Other copies and versions |
|---|---|---|---|
| ape_l (gorilla) | `ape_l.glb` 18.98 MB, modified, not committed | `ape_l_v2.blend` 1.94 MB (+ `.blend1`); `ape_l.blend` 0.14 MB (+ `.blend1`) | `ape_l_v1.glb` 0.19 MB; `backup_pre_round_joints/ape_l.glb` 18.80 MB and `ape_l_v2.blend` 1.85 MB; `gorilla-texture-2026-10-13/before/ape_l.glb` 12.85 MB and `after/ape_l.glb` 4.99 MB |
| ape2_l (retired second gorilla) | none | `ape2_l.blend1` 0.37 MB only | `docs/art/archive/ape2_l/ape2_l.blend` 0.48 MB |
| hippo_m | none | `hippo_m.blend` 1.20 MB (+ `.blend1`), `.stance`, `_weapons.json` | none |
| kangaroo_m | none | `kangaroo_m.blend` 0.47 MB (+ `.blend1`), `.stance`, `_weapons.json` | none |
| pangolin_m | none | `pangolin_m.blend` 0.65 MB (+ `.blend1`), `.stance`, `_weapons.json` | none |
| shoebill_m | none | `shoebill_m.blend` 0.73 MB (+ `.blend1`), `.stance`, `_weapons.json` | none |
| wolf_m | none | `wolf_m.blend` 0.87 MB (+ `.blend1`), `.stance`, `_weapons.json` | none |
| combiner_m | none | `combiner_m.blend` 0.48 MB (+ `.blend1`), `.stance` | none |
| combiner_v1 | none | `combiner_v1.blend` 5.31 MB (+ `.blend1`) | none |
| combiner_v2 | none | `combiner_v2.blend` 3.16 MB (+ `.blend1`) | none |

The gorilla's `.blend`, the six machine blends and the `.stance` files were all touched on 2026-10-19 or 2026-10-20.

### Rooms

| Room | Files |
|---|---|
| hangar_bay | `art/rooms/hangar_bay/hangar_bay.glb` 4.08 MB; `source/hangar_bay_form.blend` 3.99 MB, `hangar_bay_function.blend` 0.16 MB, `hangar_bay_runtime.blend` 7.18 MB (form and function have `.blend1`); `source/hero-fit-113e282db206.glb` 4.06 MB; 13 textures; `evidence/` 94 files (48 png, 21 json, logs) |
| test_box | `art/rooms/test_box/test_box.glb` 0.01 MB |

### 3D lab images (`docs/art/3d`)

168 files, 123 MB, all tracked. Model-lab turnarounds (`model_lab_*`, 13), metal and cel tests (`ape_l_lab_*`, 20),
part comparisons (`ape_l_head_*`, `ape_l_fists_v18`, `ape_l_foot_v24`, `ape_l_forearm_v23`), two mp4 clips,
`ape_l_views/` (8 views plus face and turnaround, 12), `concepts/` (7), `silhouette/` (6),
`gorilla-texture-2026-10-13/` (58 files: before and after glb, previews, pixel audit, logs).

## 2. 2D sprite sets per machine

"Plain" folders are `vNN` or `pNN` under `docs/art/2d/<machine>/`. "8/8" means the folder holds all of
`e n ne nw s se sw w .png`. All of `docs/art/2d/<machine>/` is git-ignored.

| Machine | Plain version folders | 8/8 | Suffixed folders (`_detail`, `_codex`, `_pre_codex`) | Installed now (working tree) | HEAD | origin/main | Files on disk |
|---|---|---|---|---|---|---|---|
| ape_l | v2 to v79 (74) | 71 | 15, all 8/8 | v79_detail | v78_detail | v71_detail | 10,436 (1,435 MB) |
| hippo_m | p1 to p48 (48), v1 to v7 (7) | 46 + 7 | 8, all 8/8 | p48_detail | p48_detail | p40_detail | 3,581 (495 MB) |
| kangaroo_m | p1 to p74 (72), v1 to v3 (3) | 70 + 3 | 11, all 8/8 | p74_detail | p74_detail | p68_detail | 4,576 (501 MB) |
| pangolin_m | p1 to p46 (44), v1 to v19 (18) | 42 + 18 | 10, all 8/8 | p46_detail | p46_detail | p41_detail | 5,004 (661 MB) |
| shoebill_m | p1 to p96 (93), v1 to v2 (2) | 91 + 2 | 15, 14 are 8/8 | p96_detail | p96_detail | p84_detail | 4,877 (523 MB) |
| wolf_m | v1 to v95 (94) | 93 | 11, all 8/8 | v95_detail | v95_detail | v84_detail | 5,079 (733 MB) |
| combiner_m | v1, v1b, v1c | 3 | none | not installed | | | 44 (12 MB) |
| combiner_v1 / v2 | v1 / v2 | 1 / 1 | none | not installed | | | 25 + 25 (64 MB) |

Plain folders that are not 8/8 hold only `map.json`; their views sit in the matching `_detail` folder:
ape_l v77, v78, v79; hippo_m p47, p48; kangaroo_m p73, p74; pangolin_m p45, p46; shoebill_m p95, p96; wolf_m v95.

Installed sets in `art/machines/<machine>/views/`: all six have 8 of 8 views, `views.json` and a contact sheet.
None are marked mirrored. View canvas sizes: ape_l 240x112, hippo_m 190x94, kangaroo_m 112x133,
pangolin_m 230x89, shoebill_m 104x121, wolf_m 286x124.

### ape_l v62 to v68

| Version | Views | Other material |
|---|---|---|
| v62 | 8/8 + map.json | `sheets/ape_l_v62.png`; Codex concept `generated-2026-10-13/gorilla-v62-finished-v1.png` and prompt |
| v63 | 8/8 + map.json | none |
| v64 | 8/8 + map.json | none |
| v65 | 8/8 + map.json | none |
| v66 | 8/8 + map.json | `v66_codex/` (49 files), `v66_pre_codex/` (20), `anim_v66_pre_codex/` (104), `sheets/ape_l_v66.png` |
| v67 | 8/8 + map.json | `sheets/ape_l_v67.png` |
| v68 | 8/8 + map.json | `sheets/ape_l_v68.png`; Opal 8-view `generated-2026-10-14/gorilla-v68-8dir-opal-raw.jpg` with notes |

Later gorilla steps: v71_detail, v72_round_detail, v73_steel_detail, v74_crescent_detail,
v75_joint_crescent_detail, v76_detail, v77_detail, v78_detail, v79_detail. Earlier parts work: `parts/` (9),
`selout-2026-10-12/` (72), `renders*` folders (9 folders, about 33 each), `fp1`, `fp2`.

Older machine folders without `_m` (`hippo`, `pangolin`, `shoebill`, `wolf`) hold only `generated-*` concepts.

## 3. Animation frames

| Machine | Installed clips (frames) | Anim folders in `docs/art/2d` | Files |
|---|---|---|---|
| ape_l | idle 4, gait 9, punch 9, slam 10, throw 10, hit 3, death 6 | 34 | 7,602 |
| hippo_m | idle 4, charge 9, gape 9, jets 9, hit 3, death 6 | 10 | 1,886 |
| kangaroo_m | idle 4, jab 9, kick 9, flak 9, hit 3, death 6 | 12 | 2,024 |
| pangolin_m | idle 4, rake 9, roll 9, shot 9, hit 3, death 6 | 13 | 2,920 |
| shoebill_m | idle 4, lance 9, clamp 9, buffet 9, hit 3, death 6 | 13 | 2,506 |
| wolf_m | idle 4, dash 9, howl 9, lunge 9, hit 3, death 6 | 15 | 2,588 |

Installed clips live in `art/machines/<machine>/anim/<clip>/N.png` with `anim.json` (frame times, loop mode, feet line).
Work frames are per-frame folders holding `e.png`, `e_id.png`, `e_n.png`, `e_piece.png`, `e_px.png` and `parts.json`.
The gorilla keeps many backups: `live_backup_anim_1..8`, `anim_frames_detail_pre_v77/v78/v79`, `_v71`, `_v79a`,
`_v79_shifted`, plus Codex rounds (`anim_codex` 676, `anim_rebuilt_clips_codex` 1,264, `anim_punch_haymaker_codex` 405,
`anim_death_wide_codex` 528, `anim_v71_codex` 431, `anim_v77_codex` 68).

`docs/art/2d/battle_vfx/`: 19 effect sheets, one impacts sheet, one reel mp4 (2026-10-15).

## 4. Generated concepts (Codex, Opal, Grok)

| Where | Made by | What | Images | In git |
|---|---|---|---|---|
| `docs/art/2d/<m>/generated-2026-10-12/` | Codex image_gen (named in prompt.txt) | "finished" look, one per machine: gorilla, hippo, kangaroo, pangolin, shoebill, wolf | 6 | no |
| `docs/art/2d/<m>/generated-2026-10-13/` | Codex image_gen | gorilla v58 and v62, hippo p15, kangaroo p32, pangolin p10, shoebill p42, wolf v27 and three v29 takes | 10 | no |
| `docs/art/2d/ape_l/generated-2026-10-14/` | Opal | gorilla v68 eight views, plus a new-reference eight views, raw jpg, with notes | 2 | no |
| `docs/art/2d/<m>/generated-2026-10-15/` | Codex built-in imagegen | "Legacy sprite concept" for ape_l v71, hippo_m p40, kangaroo_m p68, pangolin_m p40, shoebill_m p84, wolf_m v84 | 6 | no |
| `docs/art/reference/generated-2026-10-19-*` and `-2026-10-20-shoebill` | Codex "Built-in image_gen.imagegen" (generation-record.json) | 7 folders: gorilla+wolf, hippo, kangaroo, kangaroo corrected, pangolin, wolf updated, shoebill. Model sheet and battle sprite each | 16 | yes |
| `docs/art/2d/codex_reference_pack_2026-10-19/` | our sheets sent to Codex, and its returns | 6 input sheets, PROMPTS.md; `returned/`: 6 model sheets, 6 sprites, 6 ours-vs-Codex, one JSON | 24 | no |
| `docs/art/2d/grok_pack_2026-10-20/` | Grok | 6 machine model sheets plus 2 alternates and 2 group sheets; our sheets for comparison; battle bg, two fields, opening, title, two menus, slot previews; runs.jsonl | 33 | no |
| `docs/art/2d/screens_pre_grok_2026-10-20/` | our screens before Grok art | field, opening, title | 3 | no |
| `docs/art/codex_inputs/2026-10-13/` | inputs prepared for Codex | 24 images | 24 | yes |

Grok's world and UI art is installed in `art/` (title, field, battle, opening, ui, people). Those game files are tracked.

## 5. Reference material

| Where | What | Count | In git |
|---|---|---|---|
| `docs/reference/` | written studies: battle structure, Legacy structure, sprite rules (two), sprite detail, gorilla posture, hangar synthesis, battle VFX, combiner v1 and v2, deploy-and-combine scan, GitHub scan | 12 md | yes |
| `docs/art/reference/legacy/` | Zoids Legacy sheets: Command Wolf, Dibison, Elephander, Godos, Gordos, Gun Blaster, Gun Sniper, Hellrunner, Iron Kong, Red Horn, Rev Raptor, Shadow Fox, plus Blox, Helic and Zenebas index sheets with txt | 15 images, 3 txt | no, ignored on purpose ("structure only") |
| `docs/art/reference/starters/` | per-machine refs (ape 11, ape2 1, hippo 7, kangaroo 7, pangolin 7, shoebill 7, wolf 9), 56 overlays, round 1 to 7 sheets, near-dup and installed-vs-reference sheets, README | 117 images, 66 MB | yes |
| `docs/art/dreamina-gorilla-2026-10-11/` | `guide_ape_l_4x.png`, the guide sent to Dreamina | 1 image | yes |
| `docs/art/ape-rd-2026-10-11/` | Retro Diffusion gorilla tests and fixes, `slots_before_v29/` | 36 images | yes |
| `docs/art/starter-sources-2026-10-11/guides/` | starter guides | 32 images | yes |
| `docs/art/archive/ape2_l/` | retired second gorilla, with its .blend | 56 images | yes |
| `docs/art/retired-2026-10-11/` | lion_m, raptor_s, manifest | 2 images | yes |
| `docs/art/2d/video_reference_pack/` | 8 shot frames, all-frames sheet, SHOTS.md | 9 images | no |
| `docs/art/2d/gba_canine/`, `gba_canine_voxel/` | GBA-size canine and voxel test | 5 images | no |
| `docs/art/2d/sheets/` | contact sheets per version (ape_l v62 to v71, hippo, kangaroo, and so on) | 75 | no |
| `docs/art/2d/` top level | battle captures (188), factory (35), round and pixel tests, lineup | 262 | yes |
| `research_notes/` | gorilla animation, haymaker punch, lit pixel sprites in Godot | 10 | yes |
| `art/` (game) | machines 684 files, rooms 136, ui 3, title 2, people 2, field 2, battle 1, opening 1 | | yes |

## 6. Gaps

1. Five machines have no game model. Only `ape_l.glb` exists. The others are `.blend` only.
2. No exchange formats. No `.fbx`, `.obj` or `.gltf` for any machine.
3. Animations face one way. Views are 8 of 8, but every clip is east-facing. 8,091 frame files are `e`.
4. Version numbers missing on disk: kangaroo_m p69, p70; pangolin_m p42, p43 (and v12); shoebill_m p86, p87; wolf_m v94.
   Commit messages show kangaroo p69 and p70, pangolin p42 and p43, and shoebill p86 and p87 were made in the
   cloud session. Their render folders are git-ignored, so they never came back. Shoebill p85 exists only as
   `p85_buffet_codex`, which has no views. Wolf v94 has no trace.
5. Gorilla v72 to v75 exist only as named detail folders (round, steel, crescent, joint crescent), not plain folders.
6. Single copy on one hard drive. All 34,119 files under `docs/art/2d/*/` (4.5 GB) are ignored. The factory
   scripts can remake render rounds, but not the AI concepts: 24 ignored `generated-*` images, the Codex reference pack,
   the Grok pack, battle VFX sheets, the video reference pack and the contact sheets. D: is a spinning disk (Seagate ST1000DM010).
7. Zoids Legacy reference sheets are ignored on purpose and also have one copy only.
8. No Dreamina output is kept. Only the guide image that was sent.
9. Three gorilla `.glb` files of 12.8 to 19.0 MB are tracked (game, pre-round-joints backup, texture "before").
   Every new export of the game model adds about 19 MB to history.
10. Tracked clutter: 13 `.blend1` backups (17.7 MB), 8 `.pyc` (plus one untracked), 13 logs, `project.godot.bak`.

## 7. Git and GitHub readiness

| Fact | Value |
|---|---|
| Current branch | `cloud/model-pass-2026-10-16` |
| Upstream | `origin/cloud/model-pass-2026-10-16`, ahead 1 (commit 6480ef3, "Codex reference round...", not pushed) |
| Other branches | local `master` = `origin/main` = 94e3ae5, 6 commits behind HEAD |
| Remote | `origin` = https://github.com/pmcgaughy98/C-drive.git (fetch and push) |
| mech-zoids repo | https://github.com/pmcgaughy98/mech-zoids.git answers `git ls-remote` with no branches: it exists and is empty. It is not a remote of this folder |
| Uncommitted | 116 entries: 115 modified tracked files (about 60 MB: 73 under `art/machines/ape_l` incl. `ape_l.glb`, 22 in `docs/art/3d`, 3 each for hippo, pangolin, wolf, 7 `.pyc`, 2 Blender scripts, the factory plan and the factory-pass skill) and 1 untracked `.pyc` |
| Ignored, not in git | `docs/art/2d/*/` 34,119 files 4.5 GB; `docs/art/reference/legacy/`; `.godot/`; caches |
| Files over 50 MB | none (tracked, untracked, history or inside `.git`) |
| Files over 100 MB | none |
| Largest tracked | `art/machines/ape_l/ape_l.glb` 19.0 MB; `backup_pre_round_joints/ape_l.glb` 18.8 MB; texture `before/ape_l.glb` 12.8 MB |
| Tracked at HEAD | 2,424 files, 389.6 MB |
| Reachable history | 3,117 blobs, 432.7 MB uncompressed |
| `.git` on disk | 1,943 MB: 21,086 loose objects (1.87 GiB) and one 22 MB pack. Far more than reachable history, so most loose objects are likely leftovers. Only reachable objects are pushed |
| `.gitattributes` | none |
| Git LFS | git-lfs 3.7.1 installed, filters set in the system gitconfig, `.git/lfs/objects` empty, `git lfs ls-files` empty. Not set up for this repo |

What this means:

- A push today is within GitHub's per-file limits (100 MB blocked, 50 MB warning). No LFS is needed for the current tracked set.
- The ignored render tree (4.5 GB, 34k files) is far past GitHub's size guidance. Keep it out of plain git.
  If it needs an off-disk copy, a separate backup or LFS for the irreplaceable concept folders only is the safer route.
- If `.glb` and `.blend` keep growing, a `.gitattributes` with LFS for `*.glb`, `*.blend` would stop history from swelling.
- The two repo URLs given (`hollowtide.git`, `mech-zoids.git`) do not match this folder's remote (`C-drive.git`).
  Which one the mech game should push to is Preston's call.
- `git gc` would likely shrink `.git` a lot. Not run: this pass was read-only.
