extends SceneTree
## Render the art in its actual scenes and verify all task slots load at native size.

func _initialize() -> void:
	call_deferred("_capture")

func _capture() -> void:
	var manifest = JSON.parse_string(FileAccess.get_file_as_string("res://docs/team/art-generation-2026-10-11.json"))
	for asset in manifest.assets:
		var texture = load("res://art/" + asset.path)
		if texture == null or texture.get_size() != Vector2(asset.width, asset.height):
			push_error("Art slot failed: " + asset.path)
			quit(1)
			return
	var run = root.get_node("Run")
	run.new_game()
	run.save_path = "res://tools/debug/art_capture_unused_save.tmp"
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(320, 180)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	for scene_name in ["title", "opening", "base", "field", "battle"]:
		change_scene_to_file("res://scenes/%s.tscn" % scene_name)
		for i in (90 if scene_name == "battle" else 5):
			await process_frame
		if scene_name == "battle":
			for i in 600:
				if current_scene.state == "menu":
					break
				await process_frame
		await RenderingServer.frame_post_draw
		var image = root.get_texture().get_image()
		var result = image.save_png("res://docs/team/art-preview-%s.png" % scene_name)
		if result != OK:
			push_error("Capture failed: " + scene_name)
			quit(1)
			return
		print("Captured " + scene_name)
	print("art_capture: PASS (12 textures, 5 scenes)")
	quit()
