extends SceneTree
## Weight in the turn check (camera lane, 2026-11-14). Stands each machine still, flips its facing 180 degrees and
## measures: the facing (what gameplay and the aim read) changes at once; the body swings round at no more than its size
## class's cap, so it takes about 180/cap seconds (L ~0.7 s, M ~0.45 s); the body still ends facing the right way.
## Run: godot --headless --fixed-fps 60 --path <project> --script res://tools/debug/turn_weight_check.gd
const KINDS := ["gorilla", "hippo", "kangaroo", "pangolin", "cobra", "rhino"]  # rhino last: it is the starting machine, so set_machine("rhino") first does nothing
var fails := 0


func _initialize() -> void:
	change_scene_to_file("res://scenes/moba3d/arena_play.tscn")
	_run.call_deferred()


func _wait(n: int) -> void:
	for i in n:
		await process_frame


func _run() -> void:
	await _wait(30)
	var scene := current_scene
	for k in KINDS:
		scene.set_machine(k)
		await _wait(20)
		var p: Node3D = scene.get("player")
		var body = p.get("body")
		if body == null:
			print("FAIL %s: no 3D body" % k)
			fails += 1
			continue
		p.facing = Vector3(0.0, 0.0, -1.0)
		await _wait(60)
		var start: float = body.model_root().rotation.y
		p.facing = Vector3(0.0, 0.0, 1.0)  # a 180 degree flip
		var want := atan2(0.0, 1.0)
		var facing_now: Vector3 = p.facing
		var frames := 0
		var fastest := 0.0
		var last := start
		while frames < 180:
			await process_frame
			frames += 1
			var y: float = body.model_root().rotation.y
			fastest = maxf(fastest, absf(rad_to_deg(wrapf(y - last, -PI, PI))) * 60.0)
			last = y
			if absf(wrapf(y - want, -PI, PI)) < deg_to_rad(5.0):
				break
		var cls := str(body.TURN_ROSTER.profile(k).get("size_class", ""))
		var cap: float = body.TURN_CAP.get(cls, 0.0)
		var secs := frames / 60.0
		var ok := facing_now.z > 0.99 and frames < 180 and fastest <= cap * 1.02 and secs >= 170.0 / cap * 0.9
		fails += 0 if ok else 1
		print("%s %s (%s, cap %.0f deg/s): facing flipped at once; body turned 180 deg in %.2f s, fastest %.0f deg/s"
				% ["PASS" if ok else "FAIL", k, cls, cap, secs, fastest])
	print("turn_weight_check: %d failures" % fails)
	quit(1 if fails else 0)
