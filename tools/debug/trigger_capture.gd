extends SceneTree
## Field trigger capture (Claude, 2026-10-13): opens the hangar, stands the pilot at the lab terminal, presses Z through
## its event (text, a choice, text, a choice, then the lab) and saves a screenshot at each step. Run windowed:
##   Godot --path . --script res://tools/debug/trigger_capture.gd
## Writes docs/art/2d/trigger_capture.png (a contact sheet).


func _initialize() -> void:
	call_deferred("_capture")


func _press(action: String) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event(up)


func _shot(shots: Array) -> void:
	for i in 6:
		await process_frame
	await RenderingServer.frame_post_draw
	shots.append(root.get_texture().get_image())


func _capture() -> void:
	var run = root.get_node("Run")
	run.new_game()
	run.save_path = "user://trigger_capture_unused.json"
	run.flags.erase("lab_welcomed")
	root.size = Vector2i(1280, 720)
	change_scene_to_file("res://scenes/base.tscn")
	for i in 20:
		await process_frame
	var base = current_scene
	base.pilot.position = Vector2(30, 46)
	var shots: Array = []
	await _shot(shots)                       # the terminal's label and the Z prompt
	for action in ["ui_accept", "ui_accept", "ui_accept", "ui_accept", "ui_accept", "ui_accept"]:
		_press(action)
		await _shot(shots)                   # text, choice, text, text, choice, then the lab
	var w: int = shots[0].get_width()
	var h: int = shots[0].get_height()
	var cols := 4
	var rows := int(ceil(shots.size() / float(cols)))
	var sheet := Image.create(w * cols, h * rows, false, Image.FORMAT_RGBA8)
	for i in shots.size():
		sheet.blit_rect(shots[i], Rect2i(0, 0, w, h), Vector2i((i % cols) * w, (i / cols) * h))
	sheet.save_png("res://docs/art/2d/trigger_capture.png")
	print("trigger_capture: %d shots, now in %s (mode %s)" % [shots.size(), current_scene.scene_file_path, run.mode])
	quit(0)
