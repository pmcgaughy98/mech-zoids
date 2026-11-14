# Shared arena model pipeline

Preston requested a mass-manufacture base on 2026-11-10. This is the shared Codex/Claude route for moving the existing models into `arena_play.tscn` and replacing rough bodies with authored upgrades. No paid generator is involved.

## Play now

Run `scenes/moba3d/arena_play.tscn`, the project's main scene, or `Launch Arena Play.cmd` in the project root.

- WASD: movement; Q/E or right drag: camera.
- F8: choose a test mech directly. Tab cycles the roster.
- Space/LMB: existing basic attack, or the clearly provisional test shot when a kit has no authored basic.
- Gorilla 1: authored self/ally shield, released at 0.25 seconds.
- Gorilla 2: grab/lift/ground slam, capture 0.18 seconds and impact 0.60 seconds.
- Gorilla 3: Shield Drive, brace then collision or brake.
- Gorilla 4: corrected chest-beat finish and cage.
- B: recall. Enter restarts after a match ends.

25 unique catalog designs have 3D arena bodies. The alternate rigged gorilla export and the shoebill back-plate reference are not separate playable animals. The previously installed lobster remains a legacy sprite choice because no matching lobster GLB is in the catalog; the pistol shrimp is kept as its own design.

## Two current levels

**Base proxy:** original catalog's reduced display mesh, automatically centered, grounded, fitted to provisional S/M/L bounds, with hover for appropriate flying/swimming bodies. It receives the shared look, team handling, body collision, health, movement, recall, respawn and existing basic/kit behavior. Root sway/hover is presentation only. These static meshes have no authored leg gait, so grounded ones still slide. Their four original generation sheets and Blender workspace stay linked in the registry. Models with no implemented kit have disabled ability slots and the test basic; they do not borrow a different animal's powers.

**Authored trial:** gorilla's completed grab-slam/Drive/shield/chest-beat review export and rhino's completed v38 export, copied to runtime paths with hashes. Original scratch exports and artist sources remain intact. The gorilla has measured action events and interruption handling. Rhino's idle, walk, horn, brace and charge are bridged to its existing kit. Its horn presentation still follows the old sprite clock, and the ground-pound body/piston upgrade remains pending in Claude's v39 work. These are playable trials, not final art approval or a finished fleet.

## Build or inspect

From `D:/dev/new-mech-rpg`:

```powershell
python tools/art/build_arena_roster.py
python tools/art/build_arena_roster.py --check
python tools/art/build_arena_roster.py --inspect art/arena_models/rhino.glb
```

The builder reads `art/model_catalog/catalog.json`, excludes reference/duplicate entries, verifies the source files, copies the two completed authored exports when needed, and writes `art/arena_models/roster.json`. It does not edit original geometry or references. The registry carries identity, four sheet links, source hash, workspace, body stage, fit bounds and native clip inventory. Keep it under the same identity when refining a model.

## Upgrade another mech

**Meshy Smart Rig starting points:** preserve the rigged GLB and edit a native Blender copy rather than restarting a template rig. The kangaroo check in `docs/reference/kangaroo-smart-rig-import-2026-11-10.md` retained all 29 bones through MeshForge import, but its generic names left almost all roles unrecognized. Existing-bound weight editing and draft-joint editing are different paths. Its preserved Blender touch-up workspace includes the four original sheets; this is a rig starting point, not a finished animation set.

1. Work in its catalog Blender workspace with the four exact sheets. Repair anatomy before final rigging. Preserve the archived download, approved proportions/materials and another lane's refinements.
2. Inspect the actual rig. Use native quadruped/insect/avian anatomy, rest axes and measured segment lengths. Gorilla's 34-bone map and rhino's 34-bone map are examples, not universal templates. Do not blindly copy humanoid donors or assume a fixed Meshy joint count.
3. Export a separate GLB with Idle and Walk (or an appropriate hover loop), **Godot +Z forward, +Y up, meters**, grounded root and in-place movement. Measure the gait's travel speed. Keep movement in gameplay, avoiding double root motion. Add action clips and identify real contact/release times in seconds, with explicit frame rate.
4. Create a body profile JSON following `art/arena_models/rhino-profile.example.json`. `clips` maps stable gameplay roles to exact exported animation names; `events` holds `[name, seconds, damage]` entries. These are native-rig role mappings, not automatic anatomical retargeting.
5. Validate without writing, then register the reviewed export:

```powershell
python tools/art/build_arena_roster.py --register bison --source D:/path/to/bison.glb --profile D:/path/to/bison-profile.json --dry-run
python tools/art/build_arena_roster.py --register bison --source D:/path/to/bison.glb --profile D:/path/to/bison-profile.json
```

Registration requires a known catalog design, a skinned file, existing idle/walk clips, valid alias names and event times within their clips. It records the source in `authored_profiles.json`, copies a runtime GLB, and upgrades the same arena entry. It does not author missing animations, decide a kit, retarget bones or certify mesh clearance. The runtime reads registered profiles without adding another hard-coded model class.

6. Test in the real arena with effects off/on, normal speed and slow playback, front/side/game camera, idle/move/action/recovery, body contacts, walls/cage, interruption before/after impact, death/respawn, and multiple units. Preserve source geometry/weights/rest rig and unrelated actions. Add measured event and cancellation checks for the new kit. Promote only what was actually reviewed.

## Existing reusable pieces

- `MechModel3D`: clip lookup, events, locomotion rates, reactions, hitstop, shader flash, manual movement-owned clock.
- `arena_base_body.gd`: automatic static base; does not claim a foot-locking gait.
- `arena_rhino_body.gd`: transitional bridge from the existing kit's sprite clock to native rhino clips.
- `arena_gorilla_kit.gd`, `arena_grab.gd`, `arena_drive.gd`: current gorilla phase and real target-state examples.
- `arena_contact_fx.gd`: contact-only small hex accents, separate from the skeletal motion.
- `arena_roster_check.gd`: every body/identity/scale, current gorilla clips, real targets/minions, interruptions, once-only damage and independent material flashes.
- `arena_native_review.gd`: rendered roster and action screenshots in the current industrial arena.

Read `ANIMATION_PLAYBOOK.md`, sourced action cards and the corrected Gemini `REVIEW.md` before making animations. The Meshy donor trial was rejected and is not part of this registry.
