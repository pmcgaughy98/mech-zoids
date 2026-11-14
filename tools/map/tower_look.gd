extends SceneTree
## Towers and cores from the chase camera. Map design lane, 2026-11-04 (tower quality pass). Needs a window:
## Godot --fixed-fps 60 --path . -s res://tools/map/tower_look.gd -- <out.png>
## Six shots, 3 across and 2 down at 640 x 360 each: blue's tower ahead, passing it close, red's tower as an attacker
## sees it (inside the 12 m sight), red's tower felled, blue's core ahead, and red's core from its gate. The rhino is
## a blue vision source, so the fog of war draws as in play. Edits nothing.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const SHOTS := [ # machine at, looking toward, structure to fell ("" for none)
	[Vector2(3.5, 49.5), Vector2(0, 38), ""],
	[Vector2(4.6, 42.5), Vector2(-1, 33), ""],
	[Vector2(3.6, -31.0), Vector2(0, -41), ""],
	[Vector2(3.6, -31.0), Vector2(0, -41), "RedTower"],
	[Vector2(3.5, 66.0), Vector2(0, 56), ""],
	[Vector2(-3.0, -44.0), Vector2(0, -56), ""],
]


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else "res://docs/plan/moba-tower-look.png"
	var frames: Array = []
	for shot in SHOTS:
		var arena: Node3D = load(SCENE).instantiate()
		root.add_child(arena)
		await process_frame
		var player: Node3D = arena.get_node("Player")
		player.global_position = Vector3(shot[0].x, 0, shot[0].y)
		for g in ["map_units", "vision_sources"]:
			player.add_to_group(g)
		player.set_meta("team", "blue")
		player.set_meta("is_player", true)
		player.set_meta("unit_kind", "machine")
		player.set_meta("vision_radius", 12.0)
		if shot[2] != "":
			arena.set_structure_down(shot[2], true)
		var cam = arena.get_node("Camera")
		var d: Vector2 = (shot[1] - shot[0]).normalized()
		cam.yaw_degrees = rad_to_deg(atan2(-d.x, -d.y))
		cam.snap()
		for i in 30:
			await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		img.resize(640, 360, Image.INTERPOLATE_NEAREST)
		frames.append(img)
		arena.queue_free()
		await process_frame
		await process_frame
	var sheet := Image.create(640 * 3, 360 * 2, false, Image.FORMAT_RGB8)
	for i in frames.size():
		sheet.blit_rect(frames[i], Rect2i(0, 0, 640, 360), Vector2i(i % 3 * 640, i / 3 * 360))
	sheet.save_png(ProjectSettings.globalize_path(out) if out.begins_with("res://") else out)
	print("tower_look: saved ", out)
	quit(0)
