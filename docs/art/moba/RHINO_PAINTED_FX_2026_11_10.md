# Rhino move-art integration

The gorilla handoff in `docs/team/GORILLA_TO_RHINO_ART_ANIMATION_2026_11_10.md` informed the component-atlas workflow, contact timing, native review and cleanup checks. Its current gameplay rework was not copied or edited. Cascadeur remains set aside.

## Implementation

One built-in-generated transparent eight-component atlas, with its exact prompt, is saved at `art/fx/rhino/`. The art derives from the rhino's horn, gold armor and mint seismic piston design. `rhino_painted_fx.gd` layers it on existing cast, travel, confirmed contact, stomp and planted-brace events. It listens to the current registered v47 body profile; no event timings or mechanics are changed.

The default shared Arena Play and RhinoKit scripts remain untouched. `scenes/moba3d/rhino_art_arena.tscn` inherits the real Arena Play scene and adds `rhino_art_installer.gd`. This additive art-enabled game is launched with `Launch Rhino Art Arena.cmd`. Kits retain their own class, cooldowns, targets and damage. Switching away from rhino removes the old observer; another rhino kit gets its own instance through the scene-tree node-added signal. No polling through the world is needed.

The installer explicitly selects the already registered native rhino for startup. The underlying arena's `--rhino`/test startup can otherwise remain on the legacy sprite because `set_machine` returns early for the current selection. This fix is local to the art variant and does not change shared startup behavior.

## Verification

- Thirty scripted event/lifetime checks pass at 15 fps and rendered 30 fps in the native industrial map: three basic contact arcs and confirmed hits, real target damage, one dash/catch/landing, four stomp pulses, planted brace, travel wake, one finale, expiry, stopped-windup suppression and death cleanup.
- Eight actual Arena match checks pass at 30 fps: art installation, original kit script, native pound clip, once-only slam, retained cooldown handling, expiry, cleanup on machine swap and unrelated kit type.
- Completed rendered review: `D:/dev/_scratch/rhino-painted-fx-2026-11-10/rhino-painted-art.mp4`, 634 frames / 21.133 seconds at 1280 x 720, 30 fps. Captured in Godot's native Movie Maker. `painted-pound.png` and `painted-brace.png` were inspected. Logs and `checks-15.json` / `checks-30.json` are alongside it. The first shots use the current 12 m / 13-degree gameplay camera; subsequent art-inspection shots use a closer three-quarter view.
- Shutdown still reports intermittent ObjectDB/resource warnings (final native run: four objects/two resources) and blocked shader-cache writes; the run completed all 30 assertions and wrote all 634 frames. This is not a certification of clean engine shutdown.

The generated art's haze/gutters are handled in the shader rather than editing the raw PNG. Painted textures are decorative and do not replace the true range boundary. Visual acceptance from the current 12 m / 13-degree chase camera remains distinct from event checks; a closer three-quarter shot is for inspecting the art, not a replacement gameplay camera.

No separately billed generation, model upload, purchases, credential changes, commits, Gorilla edits or shared gameplay-file edits were performed.
