# Pixel-art 3D world test (Claude, 2026-10-13)

Preston: "should we keep building in 3D but keep the pixel look?" (for the world, not the machines). The answer given:
yes, a 3D world drawn as pixel art with the machines as sprites (the HD-2D route). This is the first test.

## What exists
- `scenes/room_stage_3d.tscn` (`scripts/scenes/room_stage_3d.gd`): loads a room GLB from `art/rooms/<room>/`, lights it,
  stands the gorilla's 3D model at the origin. A room's `runtime.json` "viewport" sets the window's content scale mode to
  VIEWPORT at that size; the hangar bay's is 320x180, so the whole 3D scene renders at the game's pixel resolution
  and scales up whole.
- New: `tools/debug/pixel_world_capture.gd` (run windowed): the hangar bay with the gorilla's 3D model, the wolf's and
  hippo's factory side sprites standing in the room as Sprite3D billboards (nearest filter, feet on the floor from
  views.json "anchor", 36 px per metre), five camera positions panned sideways. Writes
  `docs/art/2d/pixel_world_capture.png`.

## Findings
1. The room reads as pixel art at 320x180 with real light and cast shadows.
2. The factory's pixel sprites read crisper in the room than the 3D model drawn at the same resolution (the model goes
   soft and noisy at that size). Machines as sprites, world as 3D.
3. Billboards must face the camera fully (BILLBOARD_ENABLED). Upright ones (FIXED_Y) were foreshortened flat by the
   camera's 38 degree tilt; the sprites are already drawn from a raised camera.
4. Still to do for the route: a blob shadow under each sprite (billboards cast none and ignore the room light), the
   view picked from the camera's angle among the eight (as `scenes/view_lab.tscn` does), and a moving-camera check for
   edge shimmer (stills cannot show it; the fix if it shows is snapping the camera to the pixel grid).
