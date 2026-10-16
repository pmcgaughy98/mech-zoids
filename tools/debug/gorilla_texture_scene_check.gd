extends SceneTree
## Smoke-check the playable preview and capture it using the actual lab camera.

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var preview: Node = (load("res://scenes/gorilla_texture_preview.tscn") as PackedScene).instantiate()
	root.add_child(preview)
	current_scene = preview
	await process_frame
	var players: Array = preview.model.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		push_error("Missing animation player")
		quit(1)
		return
	var player: AnimationPlayer = players[0]
	for clip in ["idle", "walk", "gait", "punch", "slam", "throw", "hit", "death"]:
		if not player.has_animation(clip):
			push_error("Missing clip " + clip)
			quit(1)
			return
		preview.play_clip(clip)
		for frame in 20:
			await process_frame
		print("ok preview plays " + clip)
	preview.play_clip("idle")
	player.seek(0, true)
	player.pause()
	for frame in 8:
		await process_frame
	await RenderingServer.frame_post_draw
	var result := root.get_texture().get_image().save_png("res://docs/art/3d/gorilla-texture-2026-10-13/preview.png")
	print("gorilla_texture_scene_check: " + ("PASS" if result == OK else "FAIL"))
	quit(0 if result == OK else 1)
