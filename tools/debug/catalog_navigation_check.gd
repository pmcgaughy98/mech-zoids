extends SceneTree
## Exercise the actual title entry and return path, including viewport restoration.
func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	change_scene_to_file("res://scenes/title.tscn")
	await process_frame
	await process_frame
	var title := current_scene
	var workshop_index: int = title.choices.find("Mech Workshop")
	assert(workshop_index >= 0)
	title._pick(workshop_index)
	await process_frame
	await process_frame
	var workshop := current_scene
	assert(workshop.scene_file_path == "res://scenes/mech_catalog.tscn")
	assert(workshop.models.size() == 26)
	assert(root.content_scale_size == Vector2i(1280, 720))
	workshop._toggle_view()
	workshop._turn(45)
	workshop._select(8)
	workshop._back()
	await process_frame
	await process_frame
	assert(current_scene.scene_file_path == "res://scenes/title.tscn")
	assert(root.content_scale_size == Vector2i(320, 180))
	print("CATALOG NAVIGATION PASS: title > workshop > focus/turn/select > title, original viewport restored")
	quit()
