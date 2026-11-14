extends SceneTree
## Ring pull-back check (camera lane, 2026-11-14; Preston picked "Ring pull-back"). For each machine's ring move it fires
## the kit's real `used(slot)` signal, waits for the camera to settle, and measures the ring on screen: its near edge
## (behind the machine) must sit above the HUD bar (82% down), its far edge and sides on screen, and the aim must stay
## on the same spot of floor. Once the hold ends the camera must be back to the normal frame (feet 71% down).
## Run: godot --headless --fixed-fps 60 --path <project> --script res://tools/debug/ring_hold_check.gd
const CASES := [["gorilla", "4"], ["gorilla", "2"], ["rhino", "2"], ["hippo", "4"], ["kangaroo", "4"], ["pangolin", "4"]]
var fails := 0


func _initialize() -> void:
	change_scene_to_file("res://scenes/moba3d/arena_play.tscn")
	_run.call_deferred()


func _wait(n: int) -> void:
	for i in n:
		await process_frame


func _frac(cam: Camera3D, w: Vector3, vs: Vector2) -> Vector2:
	return cam.unproject_position(w) / vs


func _run() -> void:
	await _wait(30)
	var scene := current_scene
	var vs: Vector2 = root.get_visible_rect().size
	for c in CASES:
		scene.set_machine(c[0])
		await _wait(20)
		var p: Node3D = scene.get("player")
		p.global_position = Vector3(0.0, 0.0, 6.0)
		var cam := root.get_camera_3d() as ChaseCamera3D
		cam.set("_force_look", true)
		cam.yaw_degrees = 30.0
		await _wait(5)
		var aim0: Vector3 = p.aim_point() - p.global_position  # relative to the machine: a minion can bump it mid-hold
		var kit: Node = p.get_node_or_null("Kit")
		var row: Array = cam.RING_MOMENTS[c[0]][c[1]]
		var r: float = row[1]
		if row[0] != "" and kit != null and kit.get(row[0]) != null:
			r = float(kit.get(row[0]))
		p.global_position = Vector3(0.0, 0.0, 6.0)  # in case a test cast moved it
		kit.emit_signal("used", c[1])
		await _wait(40)  # 0.67 s: well into the hold
		var feet := p.global_position
		var yaw := deg_to_rad(cam.yaw_degrees)
		var back := Vector3(sin(yaw), 0.0, cos(yaw))
		var right := Vector3(cos(yaw), 0.0, -sin(yaw))
		var near := _frac(cam, feet + back * r, vs)
		var far := _frac(cam, feet - back * r, vs)
		var lf := _frac(cam, feet - right * r, vs)
		var rt := _frac(cam, feet + right * r, vs)
		var aim1: Vector3 = p.aim_point() - p.global_position
		var pushed := p.global_position.distance_to(Vector3(0.0, 0.0, 6.0))
		var arm := (cam.global_position - feet).length()
		var ok := near.y <= 0.82 and far.y >= 0.0 and lf.x >= 0.0 and rt.x <= 1.0 and aim0.distance_to(aim1) < 0.3
		fails += 0 if ok else 1
		print("%s %s slot %s, ring %.1f m: camera %.1f m from the feet; ring near edge %.0f%% down, far edge %.0f%%, sides %.0f%%-%.0f%% across; feet %.0f%% down; aim moved %.2f m (machine pushed %.2f m)"
				% ["PASS" if ok else "FAIL", c[0], c[1], r, arm, near.y * 100.0, far.y * 100.0, lf.x * 100.0, rt.x * 100.0,
				_frac(cam, feet, vs).y * 100.0, aim0.distance_to(aim1), pushed])
		await _wait(int(float(row[2]) * 60.0) + 90)  # hold ends, then 1.5 s to ease out
		var back_feet := _frac(cam, p.global_position, vs).y * 100.0
		var settled: bool = absf(back_feet - 71.0) <= 2.0 and cam.get("_ring_w") == 0.0
		fails += 0 if settled else 1
		print("%s   after the hold: feet %.0f%% down, ring weight %.3f" % ["PASS" if settled else "FAIL", back_feet, cam.get("_ring_w")])
	print("ring_hold_check: %d failures" % fails)
	quit(1 if fails else 0)
