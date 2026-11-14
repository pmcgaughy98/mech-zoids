# One session per mech (hub, 2026-11-05)

Preston, 2026-11-05: "those sessions will be for just overall touch ups upgrades and refinement for those mechs. Like VFX's, kit upgrades and touch ups."

Each mech has one session that owns its overall refinement: VFX, kit upgrades and art touch-ups. The session also works out with Preston what that mech needs next. The function lanes below still own the shared systems and do the specialised work (walks, attacks, sound, camera fit), so mech sessions ask them.

The main copy is `D:\dev\new-mech-rpg\docs\team\mech-sessions-2026-11-05.md`. Sessions in the hub's worktree are blocked by a guard from writing to the main checkout. On 2026-11-05 Preston okayed the command-line route ("Yes, all of them") for the hub and every mech session, so they copy files into the main checkout through the shell.

## Mech sessions

| Mech | Code | Session | Id |
|---|---|---|---|
| Rhino | `rhino_l` | Redraw the rhino from the camera angle | `local_0d636c38-8177-4132-8862-4c9253c141e6` |
| Gorilla | `ape_l` | Redraw the gorilla from the camera angle | `local_a78f516e-924c-4b93-8ae4-a6c4882a60a1` |
| Wolf | `wolf_m` | Redraw the wolf at 35 degrees | `local_14a93cf7-9377-457e-880e-ef8113b239c0` |
| Fennec | `fennec_s` | Fennec small gate effect, press-play in Godot | `local_53e6b8bc-5d21-41e5-90c5-b3be322226f4` |
| Hippo | `hippo_l` | Hippo mech | `local_e43e9d84-85da-4dfd-8f61-5936dd027007` |
| Lobster | `lobster_l` | Lobster mech | `local_60f41fc4-d480-4ad9-b040-47f6a1f7de03` |
| Kangaroo | `kangaroo_m` | Kangaroo mech (taking it over from the wolf session) | `local_aa5436e4-b0c0-4969-bbef-ca4ef053e3d3` |
| Pangolin | `pangolin_m` | Pangolin mech | `local_a065a335-5439-4844-9123-bc87eba6090e` |
| Shoebill | `shoebill_m` | Shoebill mech | `local_06f5a481-ab1b-4974-bd65-c1f383c45df6` |
| Falcon | `falcon_m` | Falcon mech | `local_80615129-4017-4f14-940f-e77b38138e06` |
| Squirrel | `squirrel_s` | Squirrel mech | `local_1ea519ec-39bf-4551-b0a5-aef6b2bdcc7b` |
| Chameleon | `chameleon_m` | Chameleon mech | `local_03f2a850-9f9b-45c1-9f79-e49e8c5b473f` |
| Hummingbird | `hummingbird_s` | Hummingbird mech | `local_9c422ba3-8212-4cea-b550-3e19bb3c38a0` |

`docs/art/moba/` also has `crab_m` and `frog_m` folders. Neither has a session. The roster is frozen until testing (2026-11-05): the crab was dropped for the lobster, and the frog is on hold.

Each mech session keeps a `MECH_STATUS.md` in its art folder (`D:\dev\new-mech-rpg\docs\art\moba\<code>\`).

## Function lanes (shared systems)

| Lane | Owns | Id |
|---|---|---|
| Game feel | shared match code: `machine_test_player.gd`, `directional_sprite_3d.gd`, `match_director.gd`, `kit_feel.gd`, `kit_audio.gd` | `local_09448b26-98ff-4f64-b0d4-a82acf4bb630` |
| Walk lane | walk cycles, and packing walks | `local_db7902f1-a8c3-4f3e-bdb1-769e34ff276c` |
| Attack lane | attack animations, and packing them | `local_ccc86d90-e0af-4644-8a06-67217fc4baf4` |
| Touch-up lane | sprite touch-up tools and passes (always a synthesis pass) | `local_7240508f-0c77-4ec6-9235-429d5d55d4c3` |
| Sound lane | all sound, voice and music | `local_2680af04-16fa-4e6e-aa4e-99801630d1bd` |
| Camera lane | feet, shadows and camera fit | `local_215ed72b-ef43-4822-9a9a-f24963f99f98` |
| Map lane | arena, HUD, minimap and pits | `local_6d56ace9-00ec-4cdc-ab27-206065d6030a` |
| Animation lane (fork) | packing that isn't walks or attacks | `local_3f293a5d-1800-40d0-a2bd-2d3c50ca54e8` |

Hits, deaths and other non-attack moves have no owner yet. Preston is being asked.

## Rules between them

- A mech's kit script (`scripts/moba3d/<name>_kit.gd`) belongs to its mech session. Game feel finishes anything it already has in flight in one first (the rhino's stomp and toss sound triggers), then says it's done.
- A mech session may touch up its own mech's art. It tells the touch-up lane first, so the two never edit the same frames.
- Never edit a file another lane is mid-work on. When in doubt, ask that lane.
- Only one paid job runs at a time across the whole team. Each needs a price first and Preston's own yes. Codex caps can overshoot by about 75k tokens, so quote the worst case.
  - Exception (Preston, 2026-11-06, "Yes, alongside"): a MeshForge 3D model (10 to 30 cents on his fal.ai key) may run while a Codex job is going. It still needs its own price and his yes.
- Only one Godot process runs at a time. Run `--check-only` on changed scripts before headless runs, and give long runs a timeout.
- Scratch goes in `D:\dev\_scratch\<lane or mech>\`.
- Commit only when Preston asks, and each lane commits only its own files.

## Decision, 2026-11-09

Preston: "2D sprites are scrapped btw". Machines are 3D models, rigged and animated, led by the gorilla-3d (local_f7ccf9b5) and rhino-3d (local_c87babea) sessions. The walk, attack, touch-up, camera and animation lanes stop sprite work. Nothing sprite-side is deleted without his yes.


## Decision, 2026-11-11

Preston: "lobster is scrapped btw for pistol shrimp". Lobster is out of the roster; pistol_shrimp takes its place. Nothing lobster-side is deleted without his yes.

