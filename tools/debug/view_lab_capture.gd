extends SceneTree
## View lab capture (Claude, 2026-10-16): opens the lab windowed at 1280x720 and saves all six on the floor at four
## camera angles, then each machine alone at full size (Tab), as one sheet.
##   Godot --path . --script res://tools/debug/view_lab_capture.gd
## Writes docs/art/2d/view_lab_capture.png.


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(320, 180)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	change_scene_to_file("res://scenes/view_lab.tscn")
	await process_frame
	while current_scene == null or not current_scene.has_method("turn"):
		await process_frame
	var lab = current_scene
	var shots: Array = []
	for step in 4:
		await create_timer(0.8).timeout
		await RenderingServer.frame_post_draw
		shots.append(root.get_texture().get_image())
		lab.turn(2)
	await create_timer(0.8).timeout
	lab.target_deg = 0.0
	lab.camera_deg = 0.0
	for i in lab.actors.size():
		lab.focus = i
		await create_timer(0.2).timeout
		await RenderingServer.frame_post_draw
		shots.append(root.get_texture().get_image())
	var w: int = shots[0].get_width() / 2
	var h: int = shots[0].get_height() / 2
	var cols := 4
	var sheet := Image.create(w * cols, h * int(ceil(shots.size() / float(cols))), false, Image.FORMAT_RGBA8)
	for i in shots.size():
		var im: Image = shots[i]
		im.resize(w, h, Image.INTERPOLATE_NEAREST)
		sheet.blit_rect(im, Rect2i(0, 0, w, h), Vector2i((i % cols) * w, (i / cols) * h))
	sheet.save_png("res://docs/art/2d/view_lab_capture.png")
	print("view_lab_capture: %d shots" % shots.size())
	quit(0)
