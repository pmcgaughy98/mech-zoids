extends SceneTree
## A room built with Codex's Build 3D Game Rooms plugin, checked in the game (Claude, 2026-10-12). The room .glb loads
## into scenes/room_stage_3d.tscn with the machine standing in it, both get the metal finish, a mesh named floor*
## has its top at the origin, the machine fits inside, and the room is within budget. Windowed, it saves a still to
## docs/art/3d/room_<id>.png. This is the Runtime gate for a room: it must print PASS.
##   HT_ROOM=<room_id> Godot --path . --script res://tools/debug/room_check.gd
const BUDGET := 40000

var fails := 0


func _initialize() -> void:
	_run.call_deferred()


func _ok(what: String, good: bool) -> void:
	print("  %s  %s" % ["ok  " if good else "FAIL", what])
	if not good:
		fails += 1


func _run() -> void:
	var stage: Node = load("res://scenes/room_stage_3d.tscn").instantiate()
	root.add_child(stage)
	current_scene = stage
	await process_frame
	var Stage := load("res://scripts/scenes/room_stage_3d.gd")
	print("room_check: %s" % stage.room_id)
	_ok("the room loads (art/rooms/%s/%s.glb)" % [stage.room_id, stage.room_id], stage.room != null)
	if stage.room == null:
		print("room_check: 1 FAILED")
		quit(1)
		return
	var rb: AABB = Stage.bounds(stage.room)
	var mb: AABB = Stage.bounds(stage.model)
	var tris: int = Stage.triangle_count(stage.room)
	_ok("room size %.1f wide, %.1f high, %.1f deep (m)" % [rb.size.x, rb.size.y, rb.size.z], rb.size.x > 4.0 and rb.size.y > 2.5 and rb.size.z > 4.0)
	var floors: Array = stage.room.find_children("floor*", "MeshInstance3D", true, false)
	var floor_top := -99.0
	if not floors.is_empty():
		var fb: AABB = (floors[0] as MeshInstance3D).global_transform * (floors[0] as MeshInstance3D).get_aabb()
		floor_top = fb.end.y
	_ok("a mesh named floor* has its top at the origin (top %.2f)" % floor_top, not floors.is_empty() and absf(floor_top) < 0.05)
	_ok("the machine stands inside the room (machine %.1f x %.1f x %.1f at y %.2f)" % [mb.size.x, mb.size.y, mb.size.z, mb.position.y],
		rb.grow(0.05).encloses(mb) and absf(mb.position.y) < 0.1)
	_ok("the room is within budget (%d of %d triangles)" % [tris, BUDGET], tris <= BUDGET)
	var surfaces := 0
	for mi in stage.find_children("*", "MeshInstance3D", true, false):
		if (mi as MeshInstance3D).mesh:
			surfaces += (mi as MeshInstance3D).mesh.get_surface_count()
	_ok("every surface has the metal finish (%d of %d)" % [stage.finish_count, surfaces], stage.finish_count == surfaces and surfaces > 0)
	if not stage.runtime_config.is_empty():
		var atlas_ready := true
		for mi in stage.room.find_children("*", "MeshInstance3D", true, false):
			for i in (mi as MeshInstance3D).mesh.get_surface_count():
				var material := (mi as MeshInstance3D).get_active_material(i) as StandardMaterial3D
				atlas_ready = atlas_ready and material != null
				if material:
					atlas_ready = atlas_ready and material.albedo_texture != null and material.ao_enabled and material.ao_texture != null and material.emission_texture != null
					atlas_ready = atlas_ready and material.texture_filter == BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
		_ok("painted colour, baked AO and emission atlases load with nearest filtering", atlas_ready)
		var players: Array = stage.model.find_children("*", "AnimationPlayer", true, false)
		_ok("current machine's idle animation is playing", not players.is_empty() and (players[0] as AnimationPlayer).current_animation == "idle" and (players[0] as AnimationPlayer).is_playing())
		var camera := stage.get_viewport().get_camera_3d()
		var fb: AABB = (floors[0] as MeshInstance3D).global_transform * (floors[0] as MeshInstance3D).get_aabb() if not floors.is_empty() else AABB()
		_ok("production camera is inside the shell footprint", camera != null and absf(camera.global_position.x) < fb.size.x / 2 and absf(camera.global_position.z) < fb.size.z / 2 and camera.global_position.y < 8.0)
		_ok("room plus current machine below the scene budget (%d triangles)" % Stage.triangle_count(stage), Stage.triangle_count(stage) <= BUDGET)
	if DisplayServer.get_name() != "headless":
		for k in 30:
			await process_frame
		await RenderingServer.frame_post_draw
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/art/3d"))
		var capture := root.get_texture().get_image()
		capture.save_png("res://docs/art/3d/room_%s.png" % stage.room_id)
		if stage.runtime_config.has("viewport"):
			_ok("loaded game capture is 320x180", capture.get_size() == Vector2i(320, 180))
		print("  still: docs/art/3d/room_%s.png" % stage.room_id)
	if not stage.runtime_config.is_empty():
		var report_path := "res://art/rooms/%s/evidence/runtime/godot-check.json" % stage.room_id
		var report := {"passed": fails == 0, "failures": fails, "roomTriangles": tris,
			"sceneTriangles": Stage.triangle_count(stage), "materialSurfaces": surfaces,
			"roomSha256": FileAccess.get_sha256("res://art/rooms/%s/%s.glb" % [stage.room_id, stage.room_id]),
			"machineSha256": FileAccess.get_sha256("res://art/machines/ape_l/ape_l.glb"),
			"viewport": [320, 180], "camera": stage.runtime_config.get("camera", {}),
			"fixtureCount": stage.runtime_config.get("fixtures", []).size(),
			"capture": "docs/art/3d/room_%s.png" % stage.room_id,
			"runtimeApproval": "pending"}
		var file := FileAccess.open(report_path, FileAccess.WRITE)
		if file:
			file.store_string(JSON.stringify(report, "\t") + "\n")
		else:
			_ok("runtime evidence can be saved", false)
	print("room_check: %s" % ("PASS" if fails == 0 else "%d FAILED" % fails))
	quit(1 if fails else 0)
