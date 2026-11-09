extends SceneTree
## The floor zones and borders from the chase camera. Map design lane, 2026-11-06 (Preston: "quality and looking a
## legit moba map"). Needs a window, and no other Godot running:
## Godot --fixed-fps 60 --path . -s res://tools/map/zones_look.gd -- <out.png> [--before <old jungle tile.png>]
## Six shots, 3 across and 2 down at 640 x 360 each: blue's west camp in the jungle, the jungle toward the west edge
## (the backdrop), the stream, the plaza from the lane's mouth (the stage), blue's spawn pad (the emblem), and the side
## pit's stream door. The rhino is a blue vision source, so the fog of war draws as in play.
## --before turns the border kit and the floor zones off and lays the given tile on the jungle, which is how the map
## looked before both passes. Edits nothing.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const SHOTS := [ # machine at, looking toward
	[Vector2(-23.0, 29.0), Vector2(-29, 38)],
	[Vector2(-35.0, 22.0), Vector2(-44, 22)],
	[Vector2(-27.0, 6.0), Vector2(-29, -8)],
	[Vector2(-4.0, 11.0), Vector2(0, 0)],
	[Vector2(0.0, 62.5), Vector2(0, 72)],
	[Vector2(25.0, 4.5), Vector2(25, 16)],
]


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else OS.get_user_data_dir() + "/zones_look.png"
	var old_jungle: Texture2D = null
	var b := args.find("--before")
	if b >= 0 and b + 1 < args.size():
		old_jungle = ImageTexture.create_from_image(Image.load_from_file(args[b + 1]))
	var frames: Array = []
	for shot in SHOTS:
		var arena: Node3D = load(SCENE).instantiate()
		if old_jungle:
			arena.border_kit = false
			arena.floor_zones = false
		root.add_child(arena)
		await process_frame
		if old_jungle:
			arena._ground_mat.set_shader_parameter("jungle_tex", old_jungle)
		var player: Node3D = arena.get_node("Player")
		player.global_position = Vector3(shot[0].x, 0, shot[0].y)
		for g in ["map_units", "vision_sources"]:
			player.add_to_group(g)
		player.set_meta("team", "blue")
		player.set_meta("is_player", true)
		player.set_meta("unit_kind", "machine")
		player.set_meta("vision_radius", 12.0)
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
	sheet.save_png(out)
	print("zones_look: saved ", out)
	quit(0)
