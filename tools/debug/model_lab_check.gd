extends SceneTree
## The 3D model lab (scenes/model_lab_3d.tscn): the machine loads, every surface gets the cel look and outline,
## and the camera turns. Windowed it saves stills at four camera angles to docs/art/3d/model_lab_<deg>.png.
##   Godot --headless --path . --script res://tools/debug/model_lab_check.gd
## With HT_RECORD=1 and --write-movie it plays a slow orbit for a video instead.

var fails := 0


func _initialize() -> void:
	_run.call_deferred()


func _ok(what: String, good: bool) -> void:
	print("  %s  %s" % ["ok  " if good else "FAIL", what])
	if not good:
		fails += 1


func _run() -> void:
	var lab: Node = load("res://scenes/model_lab_3d.tscn").instantiate()
	root.add_child(lab)
	current_scene = lab
	await process_frame
	var meshes: Array = lab.model.find_children("*", "MeshInstance3D", true, false)
	_ok("the gorilla model loads (%d mesh nodes)" % meshes.size(), meshes.size() > 0)
	var surfaces := 0
	var toon := 0
	var outlined := 0
	for m in meshes:
		for i in m.mesh.get_surface_count():
			surfaces += 1
			var mat: Material = m.get_surface_override_material(i)
			if mat is StandardMaterial3D and mat.diffuse_mode == BaseMaterial3D.DIFFUSE_TOON:
				toon += 1
			if mat != null and mat.next_pass is ShaderMaterial:
				outlined += 1
	_ok("every surface has the %s finish (%d of %d)" % [lab.finish, lab.finish_count, surfaces], surfaces > 0 and lab.finish_count == surfaces)
	if lab.finish == "metal":
		var mapped := 0
		for m in meshes:
			for i in m.mesh.get_surface_count():
				var sm: Material = m.get_surface_override_material(i)
				if sm is StandardMaterial3D and sm.normal_texture != null and sm.roughness_texture != null:
					mapped += 1
		_ok("the body carries its surface-detail and metal/roughness maps (%d surface)" % mapped, mapped >= 1)
	_ok("every surface has the ink outline (%d of %d)" % [outlined, surfaces], outlined == surfaces)
	var aabb := AABB()
	for m in meshes:
		aabb = aabb.merge(m.global_transform * m.get_aabb())
	_ok("2.4-3.0 m tall, standing on the floor (height %.2f, bottom %.2f)" % [aabb.size.y, aabb.position.y], aabb.size.y > 2.4 and aabb.size.y < 3.0 and absf(aabb.position.y) < 0.1)
	var player: AnimationPlayer = lab.play_walk()
	_ok("the knuckle-walk loop is playing (%s)" % ("%.2f s" % player.get_animation("walk").length if player and player.has_animation("walk") else "missing"),
		player != null and player.is_playing() and player.current_animation == "walk")
	var clips: Array = []
	for clip_name in ["walk", "idle", "punch", "hit", "death"]:
		if player and player.has_animation(clip_name):
			clips.append(clip_name)
	_ok("the animation set is there (%s)" % ", ".join(clips), clips.size() == 5)
	var skel: Skeleton3D = lab.model.find_children("*", "Skeleton3D", true, false)[0] if not lab.model.find_children("*", "Skeleton3D", true, false).is_empty() else null
	var arm_before := skel.get_bone_global_pose(skel.find_bone("upper_arm.L")).basis.get_euler() if skel else Vector3.ZERO
	for k in 20:
		await process_frame
	var arm_after := skel.get_bone_global_pose(skel.find_bone("upper_arm.L")).basis.get_euler() if skel else Vector3.ZERO
	_ok("the left arm actually swings (moved %.1f degrees)" % rad_to_deg((arm_after - arm_before).length()), (arm_after - arm_before).length() > deg_to_rad(1.0))
	var windowed := DisplayServer.get_name() != "headless"
	if OS.get_environment("HT_RECORD") == "clips":   # a video of every clip from a three-quarter view
		lab.target_deg = -35.0
		for clip_name in ["idle", "walk", "punch", "hit", "death"]:
			lab.play_clip(clip_name)
			var secs := 3.0 if clip_name in ["walk", "idle"] else player.get_animation(clip_name).length + 0.8
			for k in int(secs * 60):
				await process_frame
	elif OS.get_environment("HT_RECORD") == "1":
		for k in 30:
			await process_frame
		for step in 8:
			lab.turn(1)
			for k in 32:
				await process_frame
		lab.orbit = true
		for k in 240:
			await process_frame
	elif windowed:
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/art/3d"))
		for step in 4:
			for k in 40:
				await process_frame
			var img := root.get_texture().get_image()
			img.save_png("res://docs/art/3d/model_lab_%03d.png" % (step * 90))
			lab.turn(2)
	print("model_lab_check: %s" % ("PASS" if fails == 0 else "%d FAILED" % fails))
	quit(1 if fails else 0)
