extends SceneTree
## Actual Godot materials at 320x180, with matching idle pose and camera for both assets.
const Lab = preload("res://scripts/scenes/model_lab_3d.gd")
const Evidence = "res://docs/art/3d/gorilla-texture-2026-10-13"
var fails := 0

func _initialize() -> void:
	_run.call_deferred()

func check(label: String, good: bool) -> void:
	print("%s %s" % ["ok" if good else "FAIL", label])
	if not good:
		fails += 1

func _run() -> void:
	for version in ["before", "after"]:
		var viewport := SubViewport.new()
		viewport.size = Vector2i(320, 180)
		viewport.own_world_3d = true
		viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		root.add_child(viewport)
		var stage := Node3D.new()
		viewport.add_child(stage)
		var model: Node3D
		if version == "after" and OS.get_environment("HT_TEXTURE_DRAFT") != "1":
			model = (load("res://art/machines/ape_l/ape_l.glb") as PackedScene).instantiate()
		else:
			var document := GLTFDocument.new()
			var state := GLTFState.new()
			var result := document.append_from_file(ProjectSettings.globalize_path(Evidence + "/" + version + "/ape_l.glb"), state)
			check(version + " GLB opens", result == OK)
			if result != OK:
				quit(1)
				return
			model = document.generate_scene(state)
		stage.add_child(model)
		var environment := WorldEnvironment.new()
		environment.environment = Environment.new()
		stage.add_child(environment)
		var sun := DirectionalLight3D.new()
		sun.rotation_degrees = Vector3(-50, -35, 0)
		sun.shadow_enabled = true
		stage.add_child(sun)
		Lab.metal_finish(model, environment.environment, sun)
		var camera := Camera3D.new()
		camera.fov = 38
		stage.add_child(camera)
		camera.current = true
		var players := model.find_children("*", "AnimationPlayer", true, false)
		check(version + " animation player", not players.is_empty())
		if not players.is_empty():
			var player := players[0] as AnimationPlayer
			for clip in ["walk", "gait", "idle", "punch", "slam", "throw", "hit", "death"]:
				check(version + " " + clip, player.has_animation(clip))
			player.play("idle")
			player.seek(0, true)
			player.pause()
		for shot: Dictionary in [{"name": "front", "angle": 0.0}, {"name": "three-quarter", "angle": -40.0}, {"name": "side", "angle": -90.0}]:
			var angle := deg_to_rad(float(shot.angle))
			camera.position = Vector3(sin(angle) * 6.5, 3.4, cos(angle) * 6.5)
			camera.look_at(Vector3(0, 1.1, 0))
			for frame in 8:
				await process_frame
			await RenderingServer.frame_post_draw
			var image := viewport.get_texture().get_image()
			check(version + " " + shot.name + " is native 320x180", image.get_size() == Vector2i(320, 180))
			var result := image.save_png(Evidence + "/" + version + "/native-" + shot.name + ".png")
			check(version + " " + shot.name + " capture saved", result == OK)
		viewport.queue_free()
		await process_frame
	print("gorilla_texture_check: " + ("PASS" if fails == 0 else "%d FAILED" % fails))
	quit(0 if fails == 0 else 1)
