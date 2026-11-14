extends SceneTree
## Fog of war look. Map design lane, 2026-11-04. Needs a window:
## Godot --fixed-fps 60 --path . -s res://tools/map/fog_look.gd
## Two chase-camera shots with the fog drawn: the rhino made a blue vision source with game feel's machine sight
## (12 m), first in the plaza looking down red's lane, then in blue's jungle beside a rock looking across the lane
## wall. Saves docs/plan/moba-fog-look-2026-11-04.png, the two side by side. Hiding enemy units is game feel's
## (arena.vision.can_see), so none are placed here. Edits nothing.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const OUT := "res://docs/plan/moba-fog-look-2026-11-04.png"
const SIGHT := 12.0
const SHOTS := [
	[Vector3(3, 0, -8), Vector2(1, -40), "plaza, looking down red's lane"],
	[Vector3(-20, 0, 24.5), Vector2(-4, 30), "blue's jungle, looking across the lane wall"],
]


func _initialize() -> void:
	var frames: Array = []
	for shot in SHOTS:
		var arena: Node3D = load(SCENE).instantiate()
		root.add_child(arena)
		await process_frame
		var player: Node3D = arena.get_node("Player")
		player.global_position = shot[0]
		for g in ["map_units", "vision_sources"]:
			player.add_to_group(g)
		player.set_meta("team", "blue")
		player.set_meta("is_player", true)
		player.set_meta("unit_kind", "machine")
		player.set_meta("vision_radius", SIGHT)
		var cam = arena.get_node("Camera")
		var at := Vector2(shot[0].x, shot[0].z)
		var d: Vector2 = (shot[1] - at).normalized()
		cam.yaw_degrees = rad_to_deg(atan2(-d.x, -d.y))
		cam.snap()
		for i in 20:
			await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		print("  %s: fog drawn %s, last update %.2f ms" % [shot[2], arena.vision.fog_shown, arena.vision.last_update_ms])
		frames.append(img)
		arena.queue_free()
		await process_frame
		await process_frame
	var w := 640
	var h := 360
	var sheet := Image.create(w * frames.size(), h, false, Image.FORMAT_RGB8)
	for i in frames.size():
		var f: Image = frames[i]
		f.resize(w, h, Image.INTERPOLATE_NEAREST)
		sheet.blit_rect(f, Rect2i(0, 0, w, h), Vector2i(i * w, 0))
	sheet.save_png(ProjectSettings.globalize_path(OUT))
	print("fog_look: saved ", OUT)
	quit(0)
