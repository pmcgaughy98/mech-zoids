extends SceneTree
## Looks at the arena from the chase camera. Map design lane, 2026-11-04. Needs a window:
## Godot --fixed-fps 60 --path . -s res://tools/map/arena_look.gd
## Stands the real rhino at eight spots, with the gorilla beside it in some (shown the way game feel's ApeKit
## shows it: the same sprite node with the ape frames). Saves one contact sheet, 2 across and 4 down, to
## docs/plan/moba-arena-look-2026-11-04.png, and prints per shot the camera spot and the screen pixels per
## world texel at the machine (1.0 means the sprite is drawn pixel for pixel at 1280 x 720).
## Sets machine_pos itself, so the wall fade shows even if the player script is not loaded.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const APE_FRAMES := "res://art/machines/ape/ape_frames.tres"
const OUT := "res://docs/plan/moba-arena-look-2026-11-04.png"
const TEXEL := 0.02 ## metres per texel for an L machine (directional_sprite_3d.gd)
const SHOTS := [ # label, machine at, looking toward, gorilla at (Vector2.INF for none)
	["1 blue spawn, toward the gate", Vector2(0, 68), Vector2(0, 40), Vector2(2.6, 65.5)],
	["2 tower bend", Vector2(0, 48), Vector2(0, 30), Vector2.INF],
	["3 the long diagonal to the plaza", Vector2(-6, 17), Vector2(0, 0), Vector2.INF],
	["4 entering the plaza, gorilla ahead", Vector2(-3, 8.5), Vector2(0, 0), Vector2(1.2, -2)],
	["5 lane wall between camera and machine", Vector2(6, 44), Vector2(0, 44), Vector2.INF],
	["6 edge cliff, camera clamped", Vector2(40.5, 28), Vector2(30, 28), Vector2.INF],
	["7 side pit, toward the stream door", Vector2(25, 16), Vector2(25, 5), Vector2(26.8, 13.5)],
	["8 rhino and gorilla side by side", Vector2(0, 62), Vector2(30, 62), Vector2(0, 59.6)],
]


func _initialize() -> void:
	var arena: Node3D = load(SCENE).instantiate()
	root.add_child(arena)
	await process_frame
	var player: Node3D = arena.get_node("Player")
	var cam = arena.get_node("Camera")
	var rhino: AnimatedSprite3D = arena.get_node("Player/Sprite")
	var ape: AnimatedSprite3D = rhino.duplicate()
	ape.sprite_frames = load(APE_FRAMES)
	var ape_holder := Node3D.new()
	arena.add_child(ape_holder)
	ape_holder.add_child(ape)
	var sheet := Image.create(1280, 1440, false, Image.FORMAT_RGB8)
	for i in SHOTS.size():
		var s: Array = SHOTS[i]
		var at: Vector2 = s[1]
		var dir: Vector2 = (s[2] - at).normalized()
		player.global_position = Vector3(at.x, 0, at.y)
		cam.yaw_degrees = rad_to_deg(atan2(-dir.x, -dir.y)) # the camera looks along -back, back = (sin, cos)
		cam.snap()
		RenderingServer.global_shader_parameter_set("machine_pos", player.global_position)
		var face := Vector3(dir.x, 0, dir.y)
		if rhino.has_method("show_facing"):
			rhino.show_facing(face, cam.global_basis, false)
		ape_holder.visible = s[3] != Vector2.INF
		if ape_holder.visible:
			ape_holder.global_position = Vector3(s[3].x, 0, s[3].y)
			if ape.has_method("show_facing"):
				ape.show_facing(-face if i != 7 else face, cam.global_basis, false) # gorilla shows its front, side in 8
		for f in 4:
			await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		var to_px: float = img.get_height() / root.get_visible_rect().size.y
		var feet: Vector2 = cam.unproject_position(player.global_position) * to_px
		var up: Vector2 = cam.unproject_position(player.global_position + Vector3.UP) * to_px
		var seen := 0
		for l in arena.get_node("Built").find_children("*", "Label3D", false, false):
			if cam.is_position_in_frustum(l.global_position):
				seen += 1
		print("  %-40s camera at %s, %.2f screen px per texel at the machine, %d labels in frame" % [s[0], cam.global_position.snapped(Vector3.ONE * 0.1), feet.distance_to(up) * TEXEL, seen])
		img.convert(Image.FORMAT_RGB8)
		img.resize(640, 360, Image.INTERPOLATE_BILINEAR)
		sheet.blit_rect(img, Rect2i(0, 0, 640, 360), Vector2i((i % 2) * 640, (i / 2) * 360))
	sheet.save_png(ProjectSettings.globalize_path(OUT))
	print("arena_look: sheet saved to ", ProjectSettings.globalize_path(OUT))
	quit(0)
