extends SceneTree
## Headless check of the squirrel's basic attack and its Hearsay passive (squirrel mech session, 2026-11-05). It
## measures the kit itself, with fake enemies that record every hit's damage scale:
## - the frames: idle_ and walk_ for all five views, each a 160-tall approved still; size S, feet edge row 141, no tilt;
## - the reach and rate the bots and HUD read: basic_range 6.5, basic_cooldown 0.91;
## - 8 darts at an enemy 4 m ahead, with a minion 2.5 m beyond it and another 5 m to its side: exactly darts 4 and 8
##   jump, both to the near minion for 0.3 of a kit hit, never to the far one; the first enemy takes 8 darts at 0.5;
## - the count lights: 1, 2, 3 lit after darts 1 to 3, all 3 on the 4th, dark again after it;
## - a machine and a closer minion both in reach: the jump takes the machine;
## - nothing else in reach: the 4th dart strikes and does not jump;
## - a dart's flight in engine time: 24 m/s, so the 4 m shot (3.2 m of flight) lands in about 0.13 s.
## Run: Godot --headless --path . --script res://tools/debug/squirrel_hearsay_check.gd

const KIT := preload("res://scripts/moba3d/squirrel_kit.gd")

var fails := 0
var field: Node3D
var player: Node3D
var kit: Node
var hits_log: Array = [] ## [number, target, jumped] for every dart_hit
var jumps: Array = [] ## [number, from, to] for every hearsay


func _initialize() -> void:
	create_timer(60.0).timeout.connect(func() -> void:
		print("FAIL  timed out after 60 s")
		quit(2))
	_run()


func _check(ok: bool, what: String) -> void:
	print(("PASS  " if ok else "FAIL  ") + what)
	if not ok:
		fails += 1


func _clear_targets() -> void:
	for d in get_nodes_in_group("kit_target"):
		d.get_parent().remove_child(d)
		d.free()


func _fake(kind: String, at: Vector3) -> Node3D:
	var s := GDScript.new()
	s.source_code = ("extends Node3D\nvar kind := \"%s\"\nvar hits: Array = []\n" % kind) \
		+ "func hit(_by = null, scale := 1.0) -> void:\n\thits.append(scale)\n" \
		+ "func body_radius() -> float:\n\treturn 0.4\n"
	s.reload()
	var n := Node3D.new()
	n.set_script(s)
	n.add_to_group("kit_target")
	field.add_child(n)
	n.global_position = at
	return n


func _wait(secs: float) -> void:
	await create_timer(secs).timeout


## Fires n darts at target, waiting for each (and any jump) to land. Returns the seconds the first dart took to strike.
func _fire(n: int, target: Node3D) -> float:
	var first_secs := -1.0
	for i in n:
		var before := hits_log.size()
		var t0 := Time.get_ticks_msec()
		var ok: bool = kit.basic_attack(target)
		if not ok:
			_check(false, "basic_attack fired")
		var engine_secs := 0.0
		while hits_log.size() == before and Time.get_ticks_msec() - t0 < 1000:
			await process_frame
			engine_secs += root.get_process_delta_time()
		if first_secs < 0.0:
			first_secs = engine_secs
		await _wait(0.35)
	return first_secs


func _scales(u: Node3D) -> String:
	return str(u.hits)


func _run() -> void:
	await process_frame
	field = load("res://scenes/moba3d/field_test.tscn").instantiate()
	root.add_child(field)
	await process_frame
	player = field.get_node("Player")
	kit = KIT.install(player)
	await process_frame
	kit.dart_hit.connect(func(t, num, jumped): hits_log.append([num, t, jumped]))
	kit.hearsay.connect(func(a, b, num): jumps.append([num, a, b]))
	var spr: DirectionalSprite3D = player.get_node("Sprite")

	# Frames
	for v in DirectionalSprite3D.VIEWS:
		for k in ["idle_", "walk_"]:
			var a := StringName(k + v)
			var ok := spr.sprite_frames.has_animation(a) and spr.sprite_frames.get_frame_texture(a, 0).get_height() == 160
			_check(ok, "%s is a 160-tall still" % a)
	_check(not spr.tilts_any() and spr.size_class == "S" and spr.feet_edge_row == 141,
		"no tilt (old-angle stills), size S, feet edge row 141")
	_check(is_equal_approx(kit.basic_range, 6.5) and is_equal_approx(kit.basic_cooldown, 0.91),
		"basic_range 6.5, basic_cooldown 0.91 (what the director and bots read)")

	var start: Vector3 = player.global_position
	var ahead: Vector3 = KIT.flat(player.facing).normalized()
	var side := ahead.rotated(Vector3.UP, deg_to_rad(90.0))

	# 8 darts: jumps on 4 and 8 to the near minion only
	_clear_targets()
	var a1 := _fake("minion", start + ahead * 4.0)
	var near := _fake("minion", a1.global_position + ahead * 2.5)
	var far := _fake("minion", a1.global_position + side * 5.0)
	await process_frame
	kit.count = 0
	hits_log.clear()
	jumps.clear()
	var lit_seen: Array = []
	var flights: Array = []
	for i in 8:
		var s: float = await _fire(1, a1)
		flights.append(snappedf(s, 0.001))
		lit_seen.append(kit.lit_count())
	var jump_nums: Array = jumps.map(func(j): return j[0])
	_check(jump_nums == [4, 8], "exactly darts 4 and 8 jumped (got %s)" % str(jump_nums))
	_check(a1.hits.size() == 8 and a1.hits.all(func(x): return is_equal_approx(x, 0.5)),
		"the first enemy took 8 darts at 0.5 (30 each): %s" % _scales(a1))
	_check(near.hits.size() == 2 and near.hits.all(func(x): return is_equal_approx(x, 0.3)),
		"the minion 2.5 m beyond took both jumps at 0.3 (18 each): %s" % _scales(near))
	_check(far.hits.is_empty(), "the minion 5 m to the side (out of reach) took nothing: %s" % _scales(far))
	# 4 m less the 0.25 m muzzle offset and the 0.55 m hit radius is 3.2 m of flight: 0.133 s at 24 m/s, plus a frame.
	# The median of the 8: the first dart after setup is fired inside a long frame and covers its flight in one step
	# that the timer here can't see (it still strikes: the dart tests its whole path each frame).
	var sorted := flights.duplicate()
	sorted.sort()
	var flight: float = sorted[4]
	_check(flight > 0.10 and flight < 0.20, "4 m darts landed in %.3f s of engine time, median (about 0.13 expected at 24 m/s): %s" % [flight, str(flights)])
	# lit_seen is read 0.35 s after each dart: the 4th's flash has gone dark by then
	_check(lit_seen == [1, 2, 3, 0, 1, 2, 3, 0], "count lights after each dart: %s" % str(lit_seen))

	# The lights on the 4th dart itself: all three
	kit.count = 3
	kit.basic_attack(a1)
	var on_fourth: int = kit.lit_count()
	await _wait(0.5)
	_check(on_fourth == 3, "all three lights on the 4th dart (got %d)" % on_fourth)

	# Machine first: a machine 3 m to the side and a minion 1.5 m beyond, both in reach
	_clear_targets()
	var a2 := _fake("minion", start + ahead * 4.0)
	var mach := _fake("machine", a2.global_position + side * 3.0)
	var close_minion := _fake("minion", a2.global_position + ahead * 1.5)
	await process_frame
	kit.count = 0
	jumps.clear()
	await _fire(4, a2)
	_check(jumps.size() == 1 and jumps[0][2] == mach and mach.hits.size() == 1 and close_minion.hits.is_empty(),
		"the jump took the machine, not the closer minion: machine %s, minion %s" % [_scales(mach), _scales(close_minion)])

	# Nothing else in reach: the 4th dart strikes and stops
	_clear_targets()
	var a3 := _fake("minion", start + ahead * 4.0)
	await process_frame
	kit.count = 0
	jumps.clear()
	await _fire(4, a3)
	_check(a3.hits.size() == 4 and jumps.is_empty(), "alone, the 4th dart strikes and does not jump: %s" % _scales(a3))

	print("squirrel hearsay check: %d failed" % fails)
	quit(1 if fails > 0 else 0)
