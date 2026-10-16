# Codex tasks, 2026-10-15: finish the six machines on their current builds (Claude for Preston)

**Read this first. It replaces `CODEX_TASKS_2026-10-13.md`** (kept for history) and, for this pass, the install step,
ramps, targets and gorilla must-match list of `CODEX_SELOUT_APE_L_2026-10-12.md` (its shading technique still applies).
Since 2026-10-13 every machine has been rebuilt several times in the Zoids Legacy look.

## First: what happened to your 2026-10-13 finishes
You finished all six machines' views on 2026-10-13 and the gorilla's 51 battle frames
(`CODEX_FINISH_STATUS_2026-10-13.md`). Claude's installs since then **replaced the live copies of all of it**: the
gorilla's views (v66_codex) and battle frames (anim_codex) and the wolf's views (v52_codex) were live and were
overwritten; the other four were already waiting for a carry-forward. `CODEX_TASKS_2026-10-13.md` promised Claude
would carry finishes forward or flag them; it did neither. That was Claude's mistake.

- **Nothing of yours is lost.** Your copies are untouched: `docs/art/2d/<id>/<build>_codex/` and
  `docs/art/2d/ape_l/anim_codex/` (with `anim_v66_pre_codex/`).
- **They cannot be pasted back.** The machines changed shape, camera and palette since, so the old finishes are style
  guides for this pass, not files to restore.
- **It cannot happen silently again** (`tools/art/live_guard.py`):
  - `import_views.py` and `export_anim.py` record a hash of every PNG they install (`.installed_hashes.json` beside
    the files). Before replacing a live folder whose PNGs no longer match, they copy it to
    `docs/art/2d/<id>/live_backup_<views|anim>_<n>/` and print a warning.
  - **While you work on a machine, create the empty file `art/machines/<id>/CODEX_IN_PROGRESS`.** Every install script
    and every render round (`creature_round.sh`, `anim_round.sh`, `ape_round.sh`, `ape_anim_round.sh`) then stops for
    that machine, so your live files, its renders and its part maps stay put. Delete the file when you hand over.

## What changed since 2026-10-13
- **The Zoids Legacy look** (`docs/reference/sprite-rules-legacy-2026-10-14-gap.md`): lighter values, no near-black
  outline (edges take a darker shade of their own colour), a toon light with lit ridges, a violet ground line, and a
  raised camera with the side view turned toward the viewer. Camera per machine: `tools/art/legacy_look.json`
  (default 18 degrees up; the pangolin's other views are at 14).
- **A detail pass** on every build (`tools/blender/greebles.py`): panels, vents, bolts, pistons on large parts.
- **Plate cleanup in the pixelizer:** one-shade patches under 4 px merge into their neighbours (`PIXEL_MIN_CLUSTER`).
  **Dither is off for every machine as rendered** (`tools/art/palettes/ape_l.json` still says 0.45, but the gorilla's
  pipeline does not read that file).
- **New references, "Mechabeast V2"** (Preston's ChatGPT images drawn from our sheets):
  `docs/art/reference/starters/<id>.png`; the first Mechabeast set is kept as `<id>_mechabeast1.png`. Preston's
  corrections (these parts in the references are **wrong**; keep ours): the gorilla's back blocks are misaligned in the
  reference; the kangaroo's shoulder gun and hip boosters are wrong in the reference.
- **Three rounds of blind review** on wolf, kangaroo, shoebill, hippo and pangolin: a reviewer saw the V2 reference
  beside our old and new sprite without knowing which was new; only builds judged closer were installed. Log:
  `docs/plan/creature-factory-2026-10-12.md` (sections from "Plate cleanup, blind reviews and a parallel part pass").
  The gorilla was not in any round.

## The six machines now (installed; view_art_check, battle_check, foundation_check, start_chain_check PASS)
| id | Machine | Installed build | Untouched copy of the views | Battle side view |
|---|---|---|---|---|
| `ape_l` | Gorilla | v71 | `docs/art/2d/ape_l/v71/` | turned 20 degrees, camera 18 up |
| `wolf_m` | Black wolf | v84 | `docs/art/2d/wolf_m/v84/` | turned 20 degrees, camera 24 up |
| `kangaroo_m` | Red kangaroo | p68 | `docs/art/2d/kangaroo_m/p68/` | turned 20 degrees, camera 30 up |
| `shoebill_m` | Shoebill | p84 | `docs/art/2d/shoebill_m/p84/` | turned 35 degrees, camera 18 up |
| `hippo_m` | Pygmy hippo | p40 | `docs/art/2d/hippo_m/p40/` | turned 35 degrees, camera 18 up |
| `pangolin_m` | Pangolin | p40 | `docs/art/2d/pangolin_m/p40/` | turned 35 degrees, camera 18 up |

Four-view sheets (S, SE, E, SW at 3x): `docs/art/2d/sheets/<id>_<build>.png`.

**What players see:** in battle every starter plays its animation set, `art/machines/<id>/anim/<clip>/<k>.png` with
`anim.json` (gorilla 51 frames in seven clips, the others 40 frames in six clips). `scripts/ui/machine_anim.gd` loads
`anim.json` and only falls back to `views/e.png` when it is missing, which it never is now. The eight views are shown
only in the view lab (`scenes/view_lab.tscn`): the field and base scenes do not draw these machines yet. **So the
battle frames are the priority; the eight views come second.**

**Part maps** (to keep each edit inside its real part, as you did on 2026-10-13): for the views,
`docs/art/2d/<id>/renders/<view>_id.png`; for the frames, `docs/art/2d/<id>/anim_frames/<clip>/<k>/e_id.png`. On
2026-10-15 all of these belong to the installed builds (the wolf's and hippo's renders were rebuilt from the installed
files and match v84 and p40 pixel for pixel). Before using a map, check that its colour render pixelizes to the
installed crop; if it does not, flag the machine and do not guess. The CODEX_IN_PROGRESS file keeps them from changing.

## Task 1: finish the battle frames, then the eight views, one machine at a time
**Order:** gorilla, then wolf, kangaroo, shoebill, hippo, pangolin. **Stop after the gorilla until Preston approves
it;** after that, go on without waiting.

**Per machine:**
1. Create `art/machines/<id>/CODEX_IN_PROGRESS` and mark the machine in progress in
   `docs/team/CODEX_FINISH_STATUS_2026-10-15.md` (a new file; leave the 2026-10-13 one as history).
2. Check that every live PNG still matches its entry in `.installed_hashes.json` (views and anim). If any does not,
   stop and write a note.
3. Back up: copy `art/machines/<id>/anim/` to `docs/art/2d/<id>/anim_<build>_pre_codex/` and `art/machines/<id>/views/`
   to `docs/art/2d/<id>/<build>_pre_codex/`.
4. **Edit the live PNGs directly.** This replaces the sel-out doc's install step: do not run `import_views.py` or
   `export_anim.py`, and leave `views.json`, `anim.json` and `.installed_hashes.json` as they are (the guard finds your
   edits through the hash mismatch; `views.json` "source" keeps pointing at the untouched build folder).
5. Keep copies of the finished files in `docs/art/2d/<id>/anim_<build>_codex/` and `docs/art/2d/<id>/<build>_codex/`.
6. Contact sheets, before and after at 4x nearest-neighbour: `docs/art/2d/<id>/<build>_codex/before-after-4x.png` and
   `docs/art/2d/<id>/anim_<build>_codex/<clip>-before-after-4x.png`. Check each clip as a looping GIF for flicker.
7. Write `docs/team/CODEX_RESULT_2026-10-15_<ID>.md`: what you changed, and **one line per kind of fix marked
   "repeatable" or "hand only"**, so Claude can move the repeatable ones into the pixelizer and the next rebuild keeps
   them. Delete `CODEX_IN_PROGRESS` and update the status file.

**Rules:**
1. **Alpha, canvas and feet stay exact** in every view and frame.
2. **Light from above and a little left.** Top edges a shade lighter, side edges darker, undersides darkest. **No
   near-black ring** around the silhouette (Preston chose the Legacy look on 2026-10-14). Near-black only for real
   seams, vents, mouths and joint hubs. The reviewers asked for near-black plate outlines; the Legacy rule wins.
   **The wolf:** its body is already near-black (26262e, 34343e), so a dark plate's outer edge stays at its own colour
   and is not darkened further; lift top edges one step (44444f or 555562); grey flank panels take 34343e edges.
3. **Colours:** the `palette` list in the machine's `views.json` plus the teal eye ramp `1f6e66 5fe1d0 bff7ef`. This
   replaces the sel-out doc's ramps. Named colours below map to existing swatches: **hippo** "orange" trim is c98b6b
   with dca688 on its lit top edge, "near-black" is 2e2235 (never the ground line's 2e2640 on the body); **gorilla**
   back-block "yellow" is its orange ramp d4853b, eba655, f6c27c; **pangolin** c9cbd2 is already in its live art and is
   allowed. If a fix needs any other new colour, note it for Claude instead of adding it.
4. **Must-match items where they are visible.** Never paint in a part the render hides.
5. **No copying** from the Zoids sheets or the references: technique and reading only.
6. `tools/art/sprite_quality.py` and `legacy_gap.py` numbers are for the record only, with no target band; Preston
   judges by eye.

**What to fix, per machine.** For wolf, kangaroo, shoebill, hippo and pangolin these are the latest blind reviewer's
notes on the installed build, plus what Claude tried in 3D without success (do those in 2D). The gorilla's note is
Claude's own reading against its V2 reference.

- **Gorilla v71.** **Its reference is now the pixel-art Mechabeast V2** (`docs/art/reference/starters/ape_l.png`, Preston 2026-10-15:
  "best reference yet"; source `ape_l_mechabeast2_source.png`; the earlier painted V2 kept as `ape_l_mechabeast2_painted.png`). It is drawn as pixel art
  from our front-right view turned about 10 degrees further (outline 0.808 there), so it is the closest thing to
  your finish target: its crisp plate faces, lit top edges and dark seams are the look to aim for. Must match: three back blocks with orange caps in **our** arrangement, the teal visor, black knuckle
  rollers on both fists, black hubs on the shoulders and fist sides, the gatling on the right shoulder and the
  launcher on the left. Fix: from the front the arms read as one green mass; separate the upper-arm and forearm plates
  with seams and a lit top edge (the V2 reference arches the arms with a gap at the armpit).
- **Wolf v84.** Must match: four legs, red three-segment claws on every paw, six near-white tail blades, red tail tip,
  red-ringed shoulder and hip discs, cyan eye. Fix: red sits in blotches on the torso; turn it into a few clean trim
  strips along the back and shoulder edges and keep the flank panels grey. The tail reads as a short stub; give its
  segments clear joints so it reads as a spine. (Claude lowered the tail and ran the blades along it in v89, views in
  `docs/art/2d/wolf_m/v89/`; judged no better. A longer tail was not tried.)
- **Kangaroo p68.** Must match: two upright ears, **our** shoulder gun and hip boosters, a cyan eye, two feet. Fix: the
  leg reads as a flat diamond thigh with a grey blob under it; shade the outer 30% of the thigh as hip and knee grey so
  the lit orange thigh reads smaller, show a grey hip disc and knee, and two distinct feet with dark toe tips. The tail
  is speckled; band it into 3-4 px orange segments with 1-2 px dark joints. The arms and shoulder gun merge into a
  dark blob; separate them.
- **Shoebill p84.** Must match: the gold bill with its hooked tip, gold rings at the knees and ankles, gold claw tips,
  the head gun, the stepped navy wing. Fix: the pale torso is one light mass; darken it 20-25% toward mid-blue, split it
  into 3-4 plates with navy seams, add gold accents at shoulder and hip. The head gun is a faint line: **ours runs
  forward over the bill** (to the right in the side view and the battle frames), unlike the reference's; keep its
  direction and make it a clear dark line, 2 px where the silhouette allows (where it is thinner, use the gun's darkest
  shade on the pixels that are there and note the facing).
- **Hippo p40.** Must match: four legs, cream toe caps, cyan eyes, the twin-cannon turret and torpedo tubes on the
  back, the snout block. Fix: the legs merge into one dark band; between the front and rear legs, shade the already
  opaque pixels with 2e2235 so a gap reads (where there are none, note it). Most of it is purple; take the shoulder,
  hip and knee joints and the spine ridge to 2e2235 and add 4-6 short c98b6b trim strips on flank and back.
- **Pangolin p40.** Must match: red three-toed claws on all four feet, the red tail tip, blue back spikes, cyan eye.
  Fix: the claws are red flecks; make each foot's claws read as three distinct red points within the silhouette. The
  gold reads as random blotches; shade the scales in rows with a lit top row and a dark-grey seam between rows.

**Checks before handing over** (one Godot process at a time; Godot is
`C:/Users/pmcga/Games/Tools/Godot_v4.7.2/Godot_v4.7.2-stable_win64_console.exe`, called `<Godot>` below):
1. `<Godot> --headless --path . --import` after editing.
2. `<Godot> --headless --path . --script res://tools/debug/view_art_check.gd`, then `views_check.gd`, then
   `battle_check.gd`: all PASS.
3. Battle capture, before you start and after you finish. Git Bash:
   `HT_PLAYER=<id> HT_ENEMY=hippo_m <Godot> --path . --script res://tools/debug/battle_capture.gd`; PowerShell:
   `$env:HT_PLAYER='<id>'; $env:HT_ENEMY='hippo_m'; & '<Godot>' --path . --script res://tools/debug/battle_capture.gd`.
   For the hippo use `HT_ENEMY=wolf_m`. It writes `docs/art/2d/battle_<id>_vs_<enemy>*.png` and overwrites the last
   run, so copy the files into `<build>_codex/battle_before/` or `battle_after/` straight away.
4. Open `scenes/view_lab.tscn` (F6; Q / E turn the camera) and watch the machine go round.

## Coming next (Claude wires these first; do not start them yet)
- **Lit battle sprites:** the gorilla lighting slice (`docs/plan/lighting-slice-2026-10-14.md`) gives each sprite a
  normal map from the same render, lit in Godot with banded light. If it goes into battle, your finished frames get a
  matching normal map from Claude's renders; nothing for you to paint.
- **Texture sheets** for the 3D models and **the pixel 3D room**, as in the 2026-10-13 file.

## Do not
- Change any `.py`, `.gd` or `.json` under `tools/`, `scripts/` or `docs/art/3d/` (Claude's side; ask in a note).
- Edit `.installed_hashes.json`, `anim.json` or `views.json`, or run the install or round scripts.
- Move or rename files Claude's scripts read.
- Commit. Preston commits.

## Update from Claude, 2026-10-15 afternoon (after your gorilla finish)
- **All six references are now your pixel-art V2s** (`docs/art/reference/starters/<id>.png`, sources
  `<id>_mechabeast2_source.png`). The earlier painted V2s are kept as `<id>_mechabeast2_painted*.png`. The installed side
  views match them well at their current cameras (outline: hippo 0.851, pangolin 0.793, kangaroo 0.675, wolf 0.671,
  shoebill 0.640), so no build or camera changes are planned while you work.
- **Gorilla ground line fixed, your finish kept.** The detached violet line you reported came from Claude's 2026-10-14
  pixelizer change. In the live gorilla frames only the line was removed (27 frames, 972 pixels, only 2c2838 and
  403a52) and `anim.json` feet_y went 146 to 130; no body pixel changed. Backup of the live folder before the edit:
  `docs/art/2d/ape_l/anim_live_backup_feetfix_2026-10-15/`. The pixelizer no longer draws a ground line on animation
  frames (the other five never had one). Godot import, view_art_check and battle_check PASS; the gorilla stands on the
  ground in both battle slots now.
- **Still open on Claude's side, not started:** the gorilla's raw camera cuts geometry in punch, slam, throw and death
  frames, and its death clip lifts. Fixing them means re-rendering those frames, which would change their silhouettes
  and need your finish again; Claude will not do it without Preston's say-so.
- **Colour:** Claude measured trial palettes from your new references (black wolf with bright red, saturated orange
  kangaroo, brighter gorilla green and orange). Preston chose to continue your pass on the current colours, so they
  are not installed; nothing changes under you.


## Update 2026-10-15, later: the gorilla punch was redone (Claude)
- Preston asked for a new punch (a lean-back, lawnmower-pull wind-up, then an arching overhand during the leap). Claude re-rendered **only `art/machines/ape_l/anim/punch/0-8.png`** with `tools/art/replace_clip.py`. These nine frames are raw pixelizer output and **need your finish** (the same repeatable treatments as the other clips). They have new silhouettes, so don't restore the old punch frames.
- The animation canvas is now **163x148** (it was 149x148), because the punch fist reaches 14 px further right. Every other clip's frames were padded with transparent columns on the right, and all of your pixels are byte-identical in columns 0-148 (checked, 42 frames). feet_y is still 130. Your `anim_v71_codex/` copies are 149 wide, so compare on the left 149 columns.
- The punch timing changed: ms [160,240,130,70,50,150,120,200,380], strike 5. Backup of the live folder before the change: `docs/art/2d/ape_l/live_backup_anim_1/`.

## Update 2026-10-15, evening: gorilla slam, throw and death rebuilt (Claude)
- Thank you for the punch finish; it stays as you left it (the punch was not touched again).
- Preston said go on the open items from your gorilla report (the camera cuts in slam/throw/death and the death lift). Claude rebuilt those three poses and replaced **only `art/machines/ape_l/anim/{slam,throw,death}/*.png`** with `tools/art/replace_clip.py`. They are raw pixelizer output with new silhouettes and **need your finish** (your carry-forward rules). Don't restore the old frames over them.
- The canvas is now **169x148** (was 163x148): the slam's fists and the death sprawl reach further right. idle, gait, hit and punch frames were padded with transparent columns on the right only; their pixels are byte-identical in columns 0-162 (checked, 25 frames). feet_y is still 130.
- New timings: slam ms [250,250,250,300,50,50,200,80,160,250], strike 5; throw ms [200,200,200,260,90,50,120,120,150,150], strike 5; death ms [80,100,130,180,250,1000].
- Backup of the live folder with your full finish, before these installs: `docs/art/2d/ape_l/live_backup_anim_3/`.

## Update 2026-10-16: creature factory pass, the source fixes from your reports (Claude)
Thank you for the six finishes and the gorilla follow-ups. Preston asked for a creature factory pass; Claude took the
source problems your reports left on Claude's side. A new check, `tools/blender/bind_audit.py`, looks for parts riding
the wrong bone in all six models at once; it found two real bugs (both now fixed in the build rules) and nothing on the
wolf, kangaroo or hippo. Only frames whose raw render changed were replaced (new `tools/art/patch_frames.py`); every
other frame and view keeps your finish byte-for-byte (checked: shoebill 33 frames and all 8 views, pangolin 24 frames
and the S view, gorilla 45 frames in columns 0-168).

**Needs your finish (raw pixelizer output, new or changed shapes; your carry-forward rules apply):**
- **shoebill_m `anim/buffet/1-7.png`** (7 frames). The far wing's parts (bolts, stepped blades, leading edge, fan) rode
  the near wing's bones: `bird_rig.bone_for` read the side only when digits followed it, so names like
  `wing_upper_1_bolt` fell to the near side (your opposite-shoulder bolt pieces 91-93 were part of this). Only Wing
  Buffet moves the wings apart, so only it changed. The views did not change. Build p85 (rules only).
- **pangolin_m `anim/rake/1-8.png` and `anim/roll/1-8.png`** (16 frames) **and the views e, ne, n, nw, w, sw, se**
  (S kept your finish; it was re-placed 4 px left on the narrower canvas, pixels unchanged). The tail scales rode the
  wrong tail bone (the rule read the scale's place in its ring as its segment), which forked the tail in Ball Roll
  (your source-roll-tail-comparison). The scales now follow their segments in every clip that bends the tail, and in
  the standing pose. The views canvas is now **200x87, anchor [100,84]** (was 206x87, [103,84]). Build p41.
- **ape_l `anim/death/0-5.png`** (6 frames). Re-rendered with a wider frame (`SPRITE_ORTHO=6.82`, 40 sprite px of
  margin a side, same pixel grid) so the far fist no longer reaches the render's edge (your 29/68/68 edge pixels in
  death/3-5); no frame touches the edge now. The canvas is **173x148** (was 169x148), grown 4 px on the right; every
  other clip padded with transparent columns, feet_y still 130. Frames 0-2 did not change shape but Blender's shading
  shifts a little with the frame size, so all six are raw.

**Backups of the live folders with your full finish, taken before these installs:**
`docs/art/2d/shoebill_m/live_backup_anim_1/`, `docs/art/2d/pangolin_m/live_backup_anim_1/` and
`live_backup_views_1/`, `docs/art/2d/ape_l/live_backup_anim_6/`.

**Left as they are (no source change):** wolf dash/6's two pixels at the render edge (fixing them would grow the canvas
and send the whole dash back for finishing); the shoebill's one-pixel barrel portions; hidden pangolin claws (a model
change, waiting for Preston). The enemy-slot top clipping your reports measured is gone: the battle field is zoomed out
(2026-10-15) and `tools/debug/battle_fit_check.gd` and `vfx_check.gd` show nothing cut at 1280x720 or 1920x1080. The
view lab now has all six starters on the floor at half size with nothing cropped, and Tab shows one machine alone at
full size facing right (H hides the text), the fixture you built for review.

Godot import, view_art_check, views_check, battle_check, battle_fit_check, foundation_check, systems_check,
start_chain_check and vfx_check PASS.

## Update 2026-10-16, later: the detail pixelizer replaces the raw look (Claude)
Preston asked for "better versions and more enhanced and detailed than zoids sprites". Claude measured the Legacy
battle sprites against ours, studied shipped-game technique and **your finish reports**, and built
`tools/art/pixelize_detail.py` (notes and numbers: `docs/reference/sprite-detail-2026-10-16.md`).

**Five of your repeatable rules now run automatically.** A new piece pass from the renderer (`<view>_piece.png` and
`parts.json`, one exact colour per piece; the old `_id` pass was antialiased, about 40,000 colours) lets the pixelizer
do them per part:
- the lit top row of each part;
- own-colour outer edges;
- one-sided seams;
- thin parts winning their pixel;
- gentle plate cleanup.

It adds per-part form from a normal pass, metal glints, and a dark own-colour silhouette. Shoebill's blue gamma is now
1.75, your mid-blue.

**Blind judging.**
- Round 1 (six judges, one per machine): the detail version beat the live finished sprites on all six.
- Round 2: the cleaned-up version beat that on all six.
- Every judge still rated all versions below the Legacy sprites. Their remaining notes are mostly model and design
  (feet and heads, scale rows, the wolf's scattered red), listed in the reference doc.

**What this means for you.**
- All six machines' views and battle frames were re-installed from the detail pixelizer. Your finished copies are
  backed up by live_guard (`docs/art/2d/<id>/live_backup_*` and the `<build>_codex` folders).
- Please do not repaint the repeatable rules above: they are in the raw output now.
- A finish pass on top would be hand-only work: per-facing strength, heads and eyes, the judges' notes.
