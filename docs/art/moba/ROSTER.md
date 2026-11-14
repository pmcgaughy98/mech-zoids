# MOBA roster

Rules for "ode to": `CLAUDE.md`, section "MOBA roster". In short: "ode to X" is always the god's kit, never his look; the body is a mech animal with no god theme (but bold and lively, never plain) unless Preston names a visual himself.

| Machine | Folder | SMITE god | Ode is to | Status |
|---|---|---|---|---|
| Green gorilla | `ape_l` | Geb | Kit, plus the green hexagonal tech shields he named | Approved, take A as drawn |
| Wolf | `wolf_m` | Thanatos | Kit | Approved, take B with the back views squashed (`take-b/fixed/`) |
| Shoebill | `shoebill_m` | Thoth | Kit | Approved, take E as drawn (take C carried Thoth's look; take D was "to plain") |
| Kangaroo | `kangaroo_m` | Ravana (was Bellona until 2026-11-03) | Kit | Approved, take A with the back gloves tucked in by hand in Aseprite (`take-a/fixed/`); he confirmed the art stays for Ravana |
| Hippo | `hippo_l` | Bacchus | Kit | Approved, take B as drawn |
| Pangolin | `pangolin_m` | Kuzenbo | Kit | Approved, take A as drawn |
| Squirrel | `squirrel_s` | Ratatoskr | Kit | Approved, take B with the front tail cut to one side by hand in Aseprite (`take-b/fixed/`) |
| Falcon | `falcon_m` | Rama | Kit | Approved, take B as drawn (wings folded and resting on both sides; take A's raised V wings dropped) |
| Chameleon | `chameleon_m` | Loki (was Janus until 2026-11-03; art kept) | Kit | Approved, take B as drawn (all four feet planted; take A had a front foot lifted) |
| Hummingbird | `hummingbird_s` | Cupid | Kit | Approved, take A as drawn (heart-shaped throat plate flagged, kept) |
| Rhino | `rhino_l` | Cabrakan | Kit | Approved, take A as drawn (taller back views left unsquashed). Game-camera views approved 2026-11-04 ("Thats it looks good"; then "Swap now" via the hub): `rhino_l/take-a/views_cam35`, drawn from 35 degrees, now the in-game idle (see below) |
| Lobster | `lobster_l` | Khepri | Kit | Take C approved 2026-11-03 ("that works") except the back views; take D (a Codex edit of the back row) barely changed them and failed; take E (`lobster_l/take-e`) is C with n, ne and nw lowered by script to the front's height (77/75/75 to 66/65/65), rows taken only from the tail and fan, and the ne/nw antenna rods mirrored about their bases so they sweep back toward the tail as in the side views (his catch; he confirmed the fix). Take F (`lobster_l/take-f`) is E with the pale steel tail spikes removed by script on his ask ("get rid of those white spikes on back"): white tips refilled with tail plating, the dark spike bodies cut off the tail's top edge in the side and three-quarter views. G: F hand-touched in Aseprite on his ask (86 pixels: shadow blobs, seams, ridge spurs, notch). Waiting on his look. C has his original wolf's finish (gunmetal, red inset panels, red ring joints, pale steel legs with red feet, tail spines, antenna rods, cyan visor). Reads as machine, as lobster and as the wolf's family. Gaps: less red than the wolf, the three back views show a flat grey tail-fan slab, and Codex's own shape checks failed (profiles shorter than the front, backs taller). Board: `lobster_l/take-c/review-vs-wolf.png`. B: thin peg legs, small eyes, least detail. A: "It doesnt look like a mech though". Replaces the crab (`crab_m`, takes A-D). A scarab is left out: it is Khepri's own look |
| Fennec fox | `fennec_s` | Janus | Kit | Take B approved 2026-11-03 ("keep fennec b"): straight tail, sleepy eyes, rounded volume. Its violet sits close to the hippo's purple. A: curled tail, "looks flat and really like code". The frog (`frog_m`) was scratched before review |

Nothing is installed in the game yet; the MOBA has no sprite slot.

Moves: a first prototype, the rhino's ground pound in the side view, is in `rhino_l/take-a/anim/` (built only by moving the approved pixels in Aseprite, plus a ring, cracks and dust effect).

Approved lineup board: `LINEUP_approved.png` (south, east and north views of every approved machine at 2x). Check each new machine against it for size and colour before review.

Whole-family board: `ALL_CREATURES.png` (the six originals from `art/machines/*/views`, then every approved remake, then the machines in progress).

## Size in the 3D world (Preston, 2026-11-04: option B)
- Each size class has its own texel size:
  - L 0.020 m, the world's 50 texels per metre;
  - M 0.018 m;
  - S 0.016 m.
- The stills stay as drawn. The engine sets a sprite's pixel size from its class.
- New machines are drawn at the current pixel sizes.
- The board is `SIZE_BOARD_2026-11-04.png` and the numbers are in `STILLS_STOCKTAKE_2026-11-04.md`.
- Under B the kangaroo and shoebill still stand at tank height, and the pangolin is the smallest machine on the
  roster.

## Remaster of the stills
- **Gorilla:** sel-out only (Preston, 2026-11-04, "sel out only").
  - No detail ink: its stills already carry 8 to 11% interior ink.
  - The packer adds sel-out to the approved `ape_l/take-a/views`.
  - The record is in `ape_l/take-a/remaster-pilot/RUN.md`.
- **Hippo:** capped detail ink on ne and n (Preston, 2026-11-04, "Keep capped ink").
  - The back views are raised to the side views' level, 6.4%: +110 px on ne and +113 px on n, in the hippo's own
    darkest colour.
  - His originals are in `hippo_l/take-b/views_pre_ink/`. s, se and e are unchanged.
  - The record is in `hippo_l/take-b/remaster-pilot/RUN.md`.
- **Wolf, fennec, falcon, squirrel, hummingbird:** capped detail ink on the thin back views (Preston, 2026-11-04, "Keep all five"). Wolf n +43 and squirrel ne +38 in `take-b/fixed/`; fennec ne +50 and n +49, falcon ne +32 and hummingbird n +64 in their `views/`. Originals sit beside them in `fixed_pre_ink/` or `views_pre_ink/`. Record in each `remaster-pilot/RUN.md`.
- **Rhino:** in the game, the idles are now built from the approved stills (animation lane, 2026-11-04). The approved
  front still keeps no shoulder line.
- **Rhino, 35-degree idle (rhino camera-angle lane, 2026-11-04, Preston "Swap now"):**
  - The in-game idle in all five views is now `views_cam35_touchup` (the touch-up lane's recolour, same outline;
    Preston "Keep, game sel-out", 2026-11-04; `views_cam35` before it) with the same breath, built by
    `rhino_l/take-a/anim/cam35-idle/build_cam35_idle.py` and packed by `tools/art/pack_rhino_3d.py`.
  - The frames carry `tilt_anims = ["idle"]`, so the engine tilts the rhino toward the camera only while it idles
    (game feel lane's side).
  - The walk and the moves are still the old low angle and stand upright, so the rhino pops when it starts or
    stops walking and on every move. Accepted for now.
  - The fallback is untouched: `views/`, `views_cam30/`, `views_cam35/`, and the earlier packed files in
    `cam35-idle/backup_pre_cam35/` (old angle) and `cam35-idle/backup_pre_touchup/` (cam35 before the recolour).
  - Record: `rhino_l/take-a/cam35/LANE_REPORT.md` and `APPROVED.txt`.

## Minion drone (placeholder)
- Preston, 2026-11-04, to the hub: "Minions are small drone mechs, placeholders for now. Sprite factory makes them because they are sprites."
- He gave no name, lore or stats, and none are invented. Working id `minion_s`.
- Take A (`minion_s/take-a/`) is one Codex sheet from Claude's design, in `prompt-sheet.txt`.
  - It is a hovering drone: steel and charcoal hull, team-blue shell and glows, and a twin blaster under one lens.
  - Hovering is Claude's reading of "drone".
- Agreed with the game feel lane on 2026-11-04:
  - S class (0.016 m), 96 x 96 canvas, ground row 88, body bottom on row 78, about 46 px tall.
  - Animations idle, walk, attack, hit and death, named `<action>_<view>`, in all five views, at 10 fps. The attack is a short blaster shot (4 m reach, a placeholder) that leaves on frame 2, 200-300 ms in. The bolt and muzzle flash belong to the game feel lane.
  - Team colour by recolour (blue and red), not a tint.
  - The animation lane builds the frames and packs them once the still is approved.
- Take A built 2026-11-04 (Codex, one image, 44,868 tokens): 14 colours, all eight views 46 px tall, no lens in the back
  views, nothing touching the ground. Blue master in `views/`, red in `views_red/` (`team_recolour.py`; only the team
  plates and glows change, and the red lens glows orange). Board: `minion_s/take-a/team_board.png`.
  - Claude, by eye: it reads as a small hovering drone in every view and at game size. There are minor speckles on
    the side view's shell and uneven highlights on the steel hull, acceptable for a placeholder.
- **Approved by Preston, 2026-11-04: "Keep the drone".** Take A as drawn, both teams. The frames are handed to the animation lane.
- Frames built 2026-11-04 by the animation lane: a script working from the still, 0 Codex tokens, 25 animations for each team.
  - `res://art/machines/minion/minion_blue_frames.tres`
  - `res://art/machines/minion/minion_red_frames.tres`
  - Board: `minion_s/take-a/anim/board.png`

