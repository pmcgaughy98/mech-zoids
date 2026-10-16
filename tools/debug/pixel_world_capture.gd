extends SceneTree
## Pixel 3D world test (Claude, 2026-10-13; Preston: "keep building in 3D but keep the pixel look?" for the world).
## Opens the hangar room (scenes/room_stage_3d.tscn with HT_ROOM=hangar_bay, which renders at its runtime.json
## viewport, 320x180, scaled up whole), keeps the gorilla's 3D model at the origin and stands two factory pixel
## sprites in the room as upright billboards (Sprite3D, nearest filter, feet on the floor from views.json), then pans
## the camera sideways through five positions. Shows both routes side by side: a 3D model drawn at pixel resolution,
## and a flat pixel sprite in a 3D room; and how edges hold up as the camera moves. Run windowed:
##   Godot --path . --script res://tools/debug/pixel_world_capture.gd
## Writes docs/art/2d/pixel_world_capture.png (a contact sheet) and pixel_world_capture_<n>.png.

const SPRITES := [["wolf_m", Vector3(-3.2, 0, 0.6)], ["hippo_m", Vector3(3.0, 0, 0.4)]]
const PX_PER_M := 36.0   # the gorilla's side sprite is about 88 px for its 2.4 m
const PANS := [-1.6, -0.8, 0.0, 0.8, 1.6]


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	OS.set_environment("HT_ROOM", "hangar_bay")
	root.size = Vector2i(1280, 720)
	change_scene_to_file("res://scenes/room_stage_3d.tscn")
	for i in 30:
		await process_frame
	var stage: Node3D = current_scene
	for entry in SPRITES:
		var id: String = entry[0]
		var tex: Texture2D = load("res://art/machines/%s/views/e.png" % id)
		var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/machines/%s/views/views.json" % id))
		var feet: Array = meta.get("anchor", [tex.get_width() / 2, tex.get_height()])   # views.json: the feet point
		var s := Sprite3D.new()
		s.texture = tex
		s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		s.billboard = BaseMaterial3D.BILLBOARD_ENABLED   # facing the camera fully: the sprites are already drawn from a raised camera (FIXED_Y foreshortened them flat)
		s.shaded = false
		s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		s.pixel_size = 1.0 / PX_PER_M
		var base: Vector3 = entry[1]
		s.position = base + Vector3((tex.get_width() / 2.0 - float(feet[0])) * s.pixel_size, (float(feet[1]) - tex.get_height() / 2.0) * s.pixel_size, 0)
		stage.add_child(s)
	var cam: Camera3D = stage.get_viewport().get_camera_3d()
	var start := cam.position
	var basis_x := cam.global_transform.basis.x
	var shots: Array = []
	for dx in PANS:
		cam.position = start + basis_x * dx
		for i in 4:
			await process_frame
		await RenderingServer.frame_post_draw
		shots.append(root.get_texture().get_image())
	var w: int = shots[0].get_width()
	var h: int = shots[0].get_height()
	var cols := 3
	var rows := int(ceil(shots.size() / float(cols)))
	var sheet := Image.create(w * cols, h * rows, false, Image.FORMAT_RGBA8)
	for i in shots.size():
		shots[i].save_png("res://docs/art/2d/pixel_world_capture_%d.png" % i)
		sheet.blit_rect(shots[i], Rect2i(0, 0, w, h), Vector2i((i % cols) * w, (i / cols) * h))
	sheet.save_png("res://docs/art/2d/pixel_world_capture.png")
	print("pixel_world_capture: %d shots %dx%d" % [shots.size(), w, h])
	quit(0)
