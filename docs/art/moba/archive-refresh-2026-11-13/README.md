# Design archive refresh, November 13

Preston flagged the archive's old Rhino. Confirmed: the viewer loaded the static reduced `art/model_catalog/display/rhino.glb`, while the deployed game and authored profile both use Rhino v57. The same stale-proxy pattern affected Gorilla, Kangaroo, Hippo and Pangolin.

Updated those five catalog entries to isolated, byte-identical snapshots of the deployed game GLBs, after verifying each against its authored profile's source file. Current snapshots: Gorilla v38, Rhino v57, Kangaroo r12, Hippo r13, Pangolin r10. Exact source paths, SHA256, joint/clip counts and previous display paths: `sync-manifest.json`. Original downloaded GLBs, Blender workspaces, reference sheets and gameplay models remain untouched. Existing Bison/Cobra and other repair entries are preserved, not replaced with a guessed newer version.

The C comparison now offers the old static proxy and current game snapshot for each refreshed entry. The viewer can automatically fit comparison assets when no authored display scale exists; existing repair comparisons keep their explicit scales. The archive's Esc return pointed to a deleted title scene, so it now falls back to the project's configured main scene when that title is absent. The main scene and gameplay scripts were not changed.

Open `scenes/mech_catalog.tscn` in Godot and press F6. The old instruction to enter through Title > Mech Workshop is historical for this checkout: the title script exists, but `scenes/title.tscn` does not. This refresh does not recreate a title screen.

## Verification

Godot parse checks passed. The native-window verification loaded the real archive, checked all 29 entries remained, confirmed the five actual skeleton counts and animation-player presence, exercised all five version comparisons, saved current/comparison captures and the lineup, and checked return navigation plus viewport restoration. `runtime.log`: `ARCHIVE REFRESH PASS`. Manually inspected all five current views, Rhino old/current comparison and the fresh lineup.

Hash checks passed for all five snapshots, five untouched original source GLBs and twenty unchanged source sheets. Captures are actual Godot renders, not texture previews. Representative files: `rhino-current.png`, `rhino-comparison.png`, `lineup-current.png`.

Environment emitted certificate-store and shader-cache-write warnings; rendering, captures, assertions and clean exit succeeded. The first verification attempt exposed the deleted title scene and was stopped before the corrected run. This refresh verifies archive display and navigation, not every animation's deformation or game readiness. The screenshots display the current geometry with the archive's lighting, without claiming the match's complete effects/rendering treatment.

## Repeat safely

`refresh_archive.py` snapshots only the five explicitly selected authored identities and refuses mismatched existing snapshots. It retains each old proxy as comparison evidence. Future authored revisions need deliberate version updates and fresh review. Do not run a generic static proxy rebuild to update these rigs. No payments, external generation or commits.
