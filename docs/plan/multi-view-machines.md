# Multi-view machines and a turning camera

Preston, 2026-10-11: "a multi-view wiring for our zoids so Codex can fill those in and we can do rotation
camera views." Built by the Hollowtide session as new files only (nothing in the battle or field was changed).

## What it does
- Every machine has **eight views**, one per 45 degrees of facing *relative to the camera*:
  `e` (facing screen right), `ne`, `n` (away), `nw`, `w`, `sw`, `s` (toward the camera), `se`.
- The world stores where each machine faces (0 = east, 90 = north). The camera has a yaw. The view shown is
  facing minus camera yaw, snapped to the nearest 45. Turn the camera and every machine turns on screen with
  it, and machines swap places across the screen as the ground turns.
- Missing art falls back to the **mirror** of the opposite side (`w` from `e`, `nw` from `ne`, `sw` from `se`),
  then to a **placeholder**: the machine as coloured 3D blocks seen from that exact angle. So the camera can be
  built and tested before any art exists, and the placeholders are Codex's outline guides.

## Files
| File | What it is |
|---|---|
| `scripts/machines/machine_views.gd` | The rules: which view, art slots, mirror fallback, block bodies per animal (cat, raptor, bird), ground projection |
| `scripts/machines/view_sprite.gd` | One machine on screen; set `machine_id`, `facing_deg`, `camera_deg`; its position is its feet |
| `scenes/view_lab.tscn` | A test floor with three machines. Q / E turn the camera 45, O orbits, L labels each view and its source, Esc to title. Run it with F6. |
| `tools/debug/views_check.gd` | 20 checks (view choice, fallbacks, eight distinct views that fit the slot, the lab turning). Windowed, it writes the guide sheets. |
| `tools/debug/view_lab_record.gd` | Records the lab orbiting (`docs/team/view-guides/view_lab.mp4`) |
| `docs/team/view-guides/<machine>.png` | Codex's guides: the eight placeholder views in slot order, a yellow dot at the feet point |

## Wiring it into the game (next, for the battle or field session)
Swap `Slot.machine(...)` for a `ViewSprite` and give the scene a camera yaw. The battle would keep the two
machines' world facings (each toward the other) and let the camera yaw change for a swing or orbit on big moves.
The old single side-view slot `res://art/machines/<id>.png` keeps working where the view system isn't used.

## Synthesis (from general knowledge; not yet researched with sources, do that before locking the look)
- Sprite games with a turning camera draw a fixed set of facings and choose one by facing minus camera angle:
  Final Fantasy Tactics and Tactics Ogre (camera in steps, units turn on screen), Ragnarok Online (eight
  facings), Doom-era sprite enemies (eight rotations).
- Mirroring one side to make the other halves the drawing work and is common in the GBA era; markings that
  must not flip (a number, an emblem on one side) need both sides drawn.
- Snapping the camera in 45-degree steps with a short ease reads cleanly in pixel art; a slow free orbit is
  fine for showcase moments because the views change at fixed angles anyway.
- Proposal, not decided: eight views now; sixteen only if close-ups need smoother turns.

## Numbers to agree with Preston
View canvas 96x72 at the game's 320x180, feet at (48, 54), camera looking down 30 degrees. These came from
fitting the block placeholders; the machines' real sizes are his call.
