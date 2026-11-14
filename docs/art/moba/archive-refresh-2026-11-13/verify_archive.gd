extends SceneTree

const OUT := "res://docs/art/moba/archive-refresh-2026-11-13"
const IDS := ["rhino", "gorilla", "kangaroo", "hippo", "pangolin"]

func _initialize() -> void:
	_run.call_deferred()

func _shot(archive: Node, filename: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	assert(archive.get_viewport().get_texture().get_image().save_png(OUT.path_join(filename)) == OK)

func _run() -> void:
	change_scene_to_file("res://scenes/mech_catalog.tscn")
	await process_frame
	await process_frame
	var archive := current_scene
	var entry_count: int = archive.entries.size()
	assert(archive.models.size() == archive.entries.size())
	for identity in IDS:
		var index := -1
		for i in archive.entries.size():
			if archive.entries[i]["id"] == identity:
				index = i
		assert(index >= 0)
		archive._select(index)
		archive.overview = false
		archive.yaw = 22.5
		archive._update_camera()
		var model: Node = archive.models[index]
		var skeletons := model.find_children("*", "Skeleton3D", true, false)
		assert(skeletons.size() == 1)
		assert(skeletons[0].get_bone_count() == archive.entries[index]["runtime_archive_provenance"]["joint_count"])
		assert(model.find_children("*", "AnimationPlayer", true, false).size() > 0)
		await _shot(archive, identity + "-current.png")
		archive._toggle_comparison()
		assert(archive.comparing)
		await _shot(archive, identity + "-comparison.png")
		archive._clear_comparison()
	archive.overview = true
	archive.yaw = 0
	archive._update_camera()
	await _shot(archive, "lineup-current.png")
	archive._back()
	await process_frame
	await process_frame
	var expected := "res://scenes/title.tscn" if ResourceLoader.exists("res://scenes/title.tscn") else str(ProjectSettings.get_setting("application/run/main_scene"))
	assert(current_scene.scene_file_path == expected)
	assert(root.content_scale_size == Vector2i(320, 180))
	print("ARCHIVE REFRESH PASS: five current rigs, version comparisons, lineup, return navigation; ", entry_count, " entries")
	quit()
