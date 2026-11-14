extends SceneTree
## Rhino moves capture (Rhino session, 2026-11-06; slice B in docs/art/moba/rhino_l/MECH_STATUS.md). In the dressed
## field, plays key 1 (horn toss, catching a dummy), key 2 (ground pound and its stomps) and the basic jab at three
## facings: toward the camera, the diagonal and side-on. Per frame it logs the animation and view that play, the frame,
## mirroring, whether that animation is tilted to the camera, busy, and the rhino's screen position. It also logs every
## effect that spawns. Every frame is saved for a board and clip. Built on game feel's rhino_feel_check.gd, which is
## unchanged.
## Run (a window, not headless):
##   godot --path . --resolution 960x540 --fixed-fps 30 -s res://tools/debug/rhino_moves_capture.gd -- --out=<dir>
var out := "user://rhino_moves_capture"
var n := 0
var take := ""
var rows := PackedStringArray()
var fx := PackedStringArray()
var results := PackedStringArray()
var p: Node3D
var cam: Camera3D


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
	DirAccess.make_dir_recursive_absolute(out.path_join("frames"))
	change_scene_to_file("res://scenes/moba3d/field_test.tscn")
	_run.call_deferred()


func _wait(k: int) -> void:
	for i in k:
		await process_frame


func _fx_added(node: Node) -> void:
	if take == "" or not (node is Node3D) or node == p or p.is_ancestor_of(node):
		return
	_fx_log.call_deferred(node, take, n)  # the spawner sets the animation after add_child


func _fx_log(node: Node, t: String, at: int) -> void:
	if not is_instance_valid(node):
		return
	var what := String(node.name)
	if node is AnimatedSprite3D:
		what += " anim=" + String(node.animation)
	elif node is Sprite3D and node.texture != null:
		what += " tex=" + node.texture.resource_path.get_file()
	elif node is MeshInstance3D:
		what += " mesh"
	else:
		return
	fx.append("%s,%d,%s" % [t, at, what])


func _grab() -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out.path_join("frames/f%04d.png" % n))
	var s = p.sprite
	var tilt: Array = s.sprite_frames.get_meta("tilt_anims", []) if s.sprite_frames != null else []
	var sp := cam.unproject_position(p.global_position)
	var base := String(s.animation).rsplit("_", true, 1)[0]  # horn_toss_se -> horn_toss
	rows.append("%s,%d,%s,%s,%d,%s,%s,%s,%s,%d,%d" % [take, n, s.action, s.animation, s.frame, s.is_playing(), s.flip_h,
		base in tilt, p.get_node("Kit").current, roundi(sp.x), roundi(sp.y)])
	n += 1


func _face(dir: Vector3, dummies: Array, offsets: Array, home: Vector3) -> void:
	p.global_position = home
	for i in dummies.size():
		var d: Node3D = dummies[i]
		d.global_position = home + (dir * offsets[i] if i < offsets.size() else Vector3(0.0, 0.0, 40.0 + i * 3.0))
	p.facing = dir
	p.sprite.show_facing(dir, cam.global_transform.basis, false)
	await _wait(20)


func _run() -> void:
	await _wait(45)
	p = current_scene.get_node("Player")
	cam = root.get_camera_3d()
	var kit = p.get_node("Kit")
	var dummies: Array = current_scene.get_tree().get_nodes_in_group("kit_target")
	var home: Vector3 = p.global_position
	node_added.connect(_fx_added)
	var b := cam.global_transform.basis
	var toward := Vector3(b.z.x, 0.0, b.z.z).normalized()  # facing the camera: the front view
	var side := Vector3(b.x.x, 0.0, b.x.z).normalized()
	var facings := {"front": toward, "diag": (toward + side).normalized(), "side": side}
	for fname in facings:
		var dir: Vector3 = facings[fname]
		take = ""
		await _face(dir, dummies, [4.5], home)
		take = "toss_" + fname
		kit.horn_toss()
		for f in 45:
			await _grab()
		results.append("%s: dummy %.2f m along the facing (behind the rhino if negative: %.2f), stunned %.2f s" % [take,
			(dummies[0].global_position - home).dot(dir), (dummies[0].global_position - p.global_position).dot(dir),
			float(dummies[0].get("stunned"))])
		take = ""
		await _wait(15)
		await _face(dir, dummies, [1.5, 3.5], home)
		take = "pound_" + fname
		kit.ground_pound()
		var slowed := [0, 0]
		for f in 95:
			await _grab()
			for i in 2:
				if float(dummies[i].get("slowed")) > 0.0:
					slowed[i] += 1
		results.append("%s: dummies at 1.5 / 3.5 m slowed %.2f / %.2f s" % [take, slowed[0] / 30.0, slowed[1] / 30.0])
		take = ""
		await _wait(15)
		await _face(dir, dummies, [1.4], home)
		take = "jab_" + fname
		dummies[0].set("last_hit_scale", 0.0)
		kit.basic_attack(dummies[0])
		for f in 24:
			await _grab()
		results.append("%s: dummy hit scale %.2f (0.50 = 30 damage)" % [take, float(dummies[0].get("last_hit_scale"))])
		take = ""
		await _wait(10)
	var fa := FileAccess.open(out.path_join("frames.csv"), FileAccess.WRITE)
	fa.store_string("take,n,action,anim,frame,playing,flip,tilted,busy,sx,sy\n" + "\n".join(rows) + "\n")
	fa.close()
	fa = FileAccess.open(out.path_join("fx.csv"), FileAccess.WRITE)
	fa.store_string("take,n,node\n" + "\n".join(fx) + "\n")
	fa.close()
	fa = FileAccess.open(out.path_join("results.txt"), FileAccess.WRITE)
	fa.store_string("\n".join(results) + "\n")
	fa.close()
	print("\n".join(results))
	print("rhino_moves_capture: %d frames, %d effects" % [n, fx.size()])
	quit()
