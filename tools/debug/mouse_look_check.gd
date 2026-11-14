extends SceneTree
## Mouse look check (camera lane, 2026-11-13; Preston: "changing from aim at mouse to more like smite where camera moves
## with where you are looking"). Feeds the camera mouse travel and measures what follows: the camera's turn, the
## player's aim direction against the camera's forward, how far ahead the aim lands at the lowest and highest tilt,
## and that the feet stay about 71% down the screen at both tilts.
## Run: godot --headless --fixed-fps 60 --path <project> --script res://tools/debug/mouse_look_check.gd
var fails := 0


func _initialize() -> void:
	change_scene_to_file("res://scenes/moba3d/arena_play.tscn")
	_run.call_deferred()


func _wait(n: int) -> void:
	for i in n:
		await process_frame


func _move(cam: ChaseCamera3D, px: Vector2) -> void:
	var ev := InputEventMouseMotion.new()
	ev.screen_relative = px
	ev.relative = px
	cam._unhandled_input(ev)


func _check(ok: bool, line: String) -> void:
	fails += 0 if ok else 1
	print("%s %s" % ["PASS" if ok else "FAIL", line])


func _run() -> void:
	await _wait(30)
	var scene := current_scene
	scene.set_machine("gorilla")
	await _wait(20)
	var p: Node3D = scene.get("player")
	p.global_position = Vector3(0.0, 0.0, 6.0)
	var cam := root.get_camera_3d() as ChaseCamera3D
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		print("note: headless cannot capture the mouse; the check drives the camera with mouse look forced on")
		cam.set("_force_look", true)
	cam.yaw_degrees = 0.0
	await _wait(3)
	var vh: float = root.get_visible_rect().size.y
	# 1. Turn: 450 px of travel at 0.2 deg a pixel is a quarter turn to the right.
	_move(cam, Vector2(450.0, 0.0))
	await _wait(3)
	_check(absf(cam.yaw_degrees + 90.0) < 0.5, "450 px right turns the camera to %.1f deg (want -90)" % cam.yaw_degrees)
	var fwd := -cam.global_basis.z
	fwd.y = 0.0
	fwd = fwd.normalized()
	var aim: Vector3 = p.aim_dir()
	var err := rad_to_deg(Vector2(fwd.x, fwd.z).angle_to(Vector2(aim.x, aim.z)))
	_check(absf(err) < 2.0, "aim follows the camera: aim (%.2f, %.2f), camera forward (%.2f, %.2f), %.1f deg apart" % [aim.x, aim.z, fwd.x, fwd.z, err])
	# 2. Tilt: down to the steepest, then up to the flattest. The aim should come in, then go out; feet stay put.
	var reach := {}
	for want in [ChaseCamera3D.PITCH_MAX, ChaseCamera3D.PITCH_MIN]:
		_move(cam, Vector2(0.0, (want - cam.pitch_degrees) / (cam.look_sensitivity * 0.5)))
		await _wait(3)
		var feet := 100.0 * cam.unproject_position(p.global_position).y / vh
		var d: Vector3 = p.aim_point() - p.global_position
		d.y = 0.0
		reach[want] = d.length()
		_check(absf(cam.pitch_degrees - want) < 0.1 and absf(feet - 71.0) <= 2.0,
				"tilt %.1f deg (want %.1f): feet %.0f%% down, aim lands %.1f m ahead" % [cam.pitch_degrees, want, feet, d.length()])
	_check(reach[ChaseCamera3D.PITCH_MAX] < reach[ChaseCamera3D.PITCH_MIN], "tilting down brings the aim nearer (%.1f m) than tilting up (%.1f m)" % [reach[ChaseCamera3D.PITCH_MAX], reach[ChaseCamera3D.PITCH_MIN]])
	# 3. A check's aim_screen_override still wins over the reticle.
	var left := -cam.global_basis.x.slide(Vector3.UP).normalized()
	p.aim_screen_override = cam.unproject_position(p.global_position + left * 3.0)
	var o: Vector3 = p.aim_dir()
	p.aim_screen_override = null
	_check(o.dot(left) > 0.95, "aim_screen_override still steers the aim (left of the machine: %.2f, %.2f)" % [o.x, o.z])
	print("mouse_look_check: %d failures" % fails)
	quit(1 if fails else 0)
