extends SceneTree
## Rhino feel check (game feel lane, 2026-11-05; Preston: rhino 1 "a short dash forward then pluck back", the ground
## move "a bigger circle like cabrakan ... trembling and slowing those in the circle"). Opens the arena and runs three
## takes on the player's rhino, calling the kit directly so the mouse aim stays out of it:
##   A  a dummy 4.5 m ahead (past the old 3 m toss range): the dash should reach it, hold, and throw it behind.
##   B  nothing ahead: the dash should run its full length and flick at the air.
##   C  the tremor with dummies at 1.5, 3.5 and 5.0 m: the first two slowed while it lasts, the third untouched.
## Logs positions, frames, impacts and camera shake per take, and saves every frame for a clip.
## Run: godot --path . --resolution 1280x720 --fixed-fps 30 -s res://tools/debug/rhino_feel_check.gd -- --out=<dir>
var out := "user://rhino_feel_check"
var lines := PackedStringArray()
var n := 0
var impacts: Array = []


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
	DirAccess.make_dir_recursive_absolute(out.path_join("frames"))
	change_scene_to_file("res://scenes/moba3d/field_test.tscn")  # the dressed field, as rhino3d_check uses; no match director
	_run.call_deferred()


func _wait(k: int) -> void:
	for i in k:
		await process_frame


func _grab() -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out.path_join("frames/f%04d.png" % n))
	n += 1


func _cam_off() -> float:
	var cam := root.get_camera_3d()
	return Vector2(cam.h_offset, cam.v_offset).length()


func _setup(p, dummies: Array, offsets: Array) -> void:
	for i in dummies.size():
		var d: Node3D = dummies[i]
		d.global_position = p.global_position + (offsets[i] if i < offsets.size() else Vector3(0.0, 0.0, 40.0 + i * 3.0))
	p.facing = Vector3(1.0, 0.0, 0.0)
	p.sprite.show_facing(p.facing, root.get_camera_3d().global_transform.basis, false)
	impacts.clear()
	await _wait(20)


func _run() -> void:
	await _wait(45)
	var p = current_scene.get_node("Player")
	var kit = p.get_node("Kit")
	lines.append("kit %s, player at %s" % [kit.get_script().resource_path, p.global_position])
	kit.impact.connect(func(s: float) -> void: impacts.append([n, s]))
	var dummies: Array = current_scene.get_tree().get_nodes_in_group("kit_target")
	lines.append("%d dummies" % dummies.size())
	var home: Vector3 = p.global_position

	# A: dash, catch, throw back
	p.global_position = home
	await _setup(p, dummies, [Vector3(4.5, 0.0, 0.0)])
	var d0: Node3D = dummies[0]
	var start_x: float = p.global_position.x
	var take_from := n
	kit.horn_toss()
	var caught_at := -1
	var held := 0
	var peak := 0.0
	var dash_end_x := start_x
	for f in 45:
		await _grab()
		peak = maxf(peak, _cam_off())
		if p.sprite.action == "horn_toss" and p.sprite.frame == 3 and not p.sprite.is_playing():
			held += 1
			if caught_at < 0:
				caught_at = n - 1 - take_from
				dash_end_x = p.global_position.x
	await _wait(10)
	lines.append("A catch: rhino moved %.2f m, caught at clip frame %d (%.2f s), flick held %d frames, dummy now at %.2f m along (rhino at %.2f), behind=%s, stunned %.2f s left, max shake %.3f m, impacts %s" % [
		dash_end_x - start_x, caught_at, caught_at / 30.0, held, d0.global_position.x - start_x, p.global_position.x - start_x,
		d0.global_position.x < p.global_position.x, float(d0.get("stunned")), peak, str(impacts)])

	# B: nothing ahead
	p.global_position = home
	await _setup(p, dummies, [])
	start_x = p.global_position.x
	take_from = n
	kit.horn_toss()
	for f in 30:
		await _grab()
	lines.append("B miss: rhino moved %.2f m, action now '%s', busy %s" % [p.global_position.x - start_x, p.sprite.action, p.busy])

	# C: tremor
	p.global_position = home
	await _setup(p, dummies, [Vector3(1.5, 0.0, 0.0), Vector3(-2.0, 0.0, 2.8), Vector3(5.0, 0.0, 0.0)])
	take_from = n
	kit.ground_pound()
	var slowed := [0, 0, 0]
	var busy_frames := 0
	var stomp_frames: Array = []
	peak = 0.0
	for f in 110:
		await _grab()
		peak = maxf(peak, _cam_off())
		if p.busy:
			busy_frames += 1
		for i in 3:
			if float(dummies[i].get("slowed")) > 0.0:
				slowed[i] += 1
	for it in impacts:
		stomp_frames.append("%d:%.2f" % [it[0] - take_from, it[1]])
	lines.append("C tremor: rhino busy %.2f s, dummies at 1.5 / 3.5 / 5.0 m slowed for %.2f / %.2f / %.2f s, impacts (clip frame:strength) %s, max shake %.3f m" % [
		busy_frames / 30.0, slowed[0] / 30.0, slowed[1] / 30.0, slowed[2] / 30.0, ", ".join(stomp_frames), peak])
	var ring_tex: Texture2D = load("res://art/fx/moba3d/fx_frames.tres").get_frame_texture(&"gp_ring", 0)
	lines.append("gp_ring art %d x %d px = %.2f m wide at 0.02 m/px" % [ring_tex.get_width(), ring_tex.get_height(), ring_tex.get_width() * 0.02])
	lines.append("frames saved: %d" % n)
	var fa := FileAccess.open(out.path_join("log.txt"), FileAccess.WRITE)
	fa.store_string("\n".join(lines) + "\n")
	fa.close()
	print("\n".join(lines))
	quit()
