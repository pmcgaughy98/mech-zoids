extends SceneTree
## Headless check of the wolf's lunge (wolf mech session, 2026-11-05). It measures the kit itself:
## - the frames: idle_ and walk_ for all five views, each a 192-tall still, set to tilt;
## - a lunge at a dummy 4 m away, off to one side: the wolf turns to it, lands stop_short from it and bites it;
## - with nothing in range it leaps lunge_distance straight ahead and bites the air;
## - a wounded match target (hp at or under half) cuts the lunge cooldown by refund_share; a healthy one doesn't.
## Run: Godot --headless --path . --script res://tools/debug/check_wolf_kit.gd

var fails := 0
var field: Node3D
var player: Node3D
var kit: WolfKit
var last_secs := 0.0 ## game seconds the last lunge took (the player counts cooldowns down meanwhile)


func _initialize() -> void:
	_run()


func _check(ok: bool, what: String) -> void:
	print(("PASS  " if ok else "FAIL  ") + what)
	if not ok:
		fails += 1


func _clear_targets() -> void:
	for d in get_nodes_in_group("kit_target"):
		d.get_parent().remove_child(d)
		d.free()


func _lunge() -> Array:
	var got := []
	var cb := func(t, w): got.append([t, w])
	kit.bit.connect(cb)
	kit.lunge()
	var t0 := Time.get_ticks_msec()
	last_secs = 0.0
	while kit.current != "" and Time.get_ticks_msec() - t0 < 3000:
		await process_frame
		last_secs += root.get_process_delta_time()  # game time: under --fixed-fps it runs ahead of the wall clock
	kit.bit.disconnect(cb)
	return got


func _bite_done() -> void:
	var t0 := Time.get_ticks_msec()
	while kit.biting and Time.get_ticks_msec() - t0 < 2000:
		await process_frame


func _fake_unit(hp: float) -> Node3D:
	var s := GDScript.new()
	s.source_code = "extends Node3D\nvar hp := %.1f\nvar max_hp := 600.0\nvar alive := true\nvar hits := 0\nvar last_scale := 0.0\nfunc radius() -> float:\n\treturn 0.5\nfunc hit(_by = null, scale := 1.0) -> void:\n\thits += 1\n\tlast_scale = scale\n" % hp
	s.reload()
	var n := Node3D.new()
	n.set_script(s)
	n.add_to_group("kit_target")
	field.add_child(n)
	return n


func _run() -> void:
	await process_frame
	field = load("res://scenes/moba3d/field_test.tscn").instantiate()
	root.add_child(field)
	await process_frame
	player = field.get_node("Player")
	kit = WolfKit.install(player)
	await process_frame
	var spr: DirectionalSprite3D = player.get_node("Sprite")

	# Frames
	for v in DirectionalSprite3D.VIEWS:
		for kind in ["idle_", "walk_"]:
			var a := StringName(kind + v)
			var ok := spr.sprite_frames.has_animation(a) and spr.sprite_frames.get_frame_texture(a, 0).get_height() == 192
			_check(ok, "%s is a 192-tall still" % a)
	_check(spr.tilts_any() and spr.size_class == "M" and spr.feet_edge_row == 161, "tilts, size M, feet edge row 161")

	# A dummy 4 m away but 70 degrees off the aim is not the target: the wolf leaps along the aim and bites the air
	_clear_targets()
	var start := player.global_position
	var aim0 := kit.ahead()
	var off := TrainingDummy.new()
	field.add_child(off)
	off.global_position = start + aim0.rotated(Vector3.UP, deg_to_rad(70.0)) * 4.0
	await process_frame
	var got0: Array = await _lunge()
	var moved0 := WolfKit.flat(player.global_position - start)
	_check(got0.size() == 1 and got0[0][0] == null and moved0.normalized().dot(aim0) > 0.99,
		"a dummy 70 degrees off the aim is ignored: leapt along the aim, bit the air")

	# A lunge at a dummy 4 m away, 25 degrees off the aim
	_clear_targets()
	start = player.global_position
	var to_dummy := kit.ahead().rotated(Vector3.UP, deg_to_rad(25.0))
	var dummy := TrainingDummy.new()
	field.add_child(dummy)
	dummy.global_position = start + to_dummy * 4.0
	await process_frame
	var got: Array = await _lunge()
	var end_d := WolfKit.flat(dummy.global_position - player.global_position).length()
	_check(got.size() == 1 and got[0][0] == dummy, "the bite landed on the dummy")
	_check(absf(end_d - kit.stop_short) < 0.2, "landed %.2f m from the dummy (stop_short %.2f)" % [end_d, kit.stop_short])
	_check(WolfKit.flat(player.facing).normalized().dot(to_dummy) > 0.99, "turned to face the dummy")
	_check(not player.busy and kit.current == "", "free to walk after the lunge")

	# Nothing in range: straight ahead, bites the air
	_clear_targets()
	await process_frame
	start = player.global_position
	var dir := kit.ahead()
	got = await _lunge()
	var moved := WolfKit.flat(player.global_position - start)
	_check(got.size() == 1 and got[0][0] == null, "with nothing in range it bites the air")
	_check(absf(moved.length() - kit.lunge_distance) < 0.2 and moved.normalized().dot(dir) > 0.99,
		"leapt %.2f m straight ahead (lunge_distance %.2f)" % [moved.length(), kit.lunge_distance])

	# Wounded and healthy match targets, 3 m ahead; the cooldown as the director would have set it
	for case in [[200.0, true], [500.0, false]]:
		_clear_targets()
		var u := _fake_unit(case[0])
		u.global_position = player.global_position + kit.ahead() * 3.0
		await process_frame
		player.cooldowns = {"1": 8.0}
		got = await _lunge()
		var cd := float(player.cooldowns.get("1", -1.0))
		var hit_ok: bool = got.size() == 1 and got[0][0] == u and got[0][1] == case[1] and u.hits == 1
		if case[1]:
			_check(hit_ok and cd < (8.0 - last_secs) * (1.0 - kit.refund_share) + 0.3,
				"wounded target (200/600): bitten, cooldown cut, 8.0 -> %.2f in %.2f s" % [cd, last_secs])
		else:
			_check(hit_ok and absf(cd - (8.0 - last_secs)) < 0.2,
				"healthy target (500/600): bitten, cooldown only ticked down, 8.0 -> %.2f in %.2f s" % [cd, last_secs])

	# Basic bite. The fake units have alive, radius 0.5 and record the damage scale.
	var aim: Vector3 = player.aim_dir()
	if aim == Vector3.ZERO:
		aim = kit.ahead()
	var want_scale := kit.bite_damage / MatchRules.kit_hit_damage
	# a. the player's bite (target null): a unit 1.5 m edge to edge along the aim is bitten
	_clear_targets()
	var u1 := _fake_unit(600.0)
	u1.global_position = player.global_position + aim * 2.0
	await process_frame
	var fired := kit.basic_attack(null)
	await _bite_done()
	_check(fired and u1.hits == 1 and absf(u1.last_scale - want_scale) < 0.001 and not player.busy,
		"basic bite (player, 1.5 m edge): fired, hit once at scale %.3f (%.0f damage), not left busy" % [u1.last_scale, kit.bite_damage])
	# b. nothing in reach: the player's bite still fires and whiffs
	_clear_targets()
	var u2 := _fake_unit(600.0)
	u2.global_position = player.global_position + aim * 4.0
	await process_frame
	fired = kit.basic_attack(null)
	await _bite_done()
	_check(fired and u2.hits == 0, "basic bite (player, nothing in reach): fires and whiffs, no hit")
	# c. a bot's target out of reach: does not fire
	_check(not kit.basic_attack(u2) and u2.hits == 0, "basic bite (bot, target 3.5 m edge): does not fire")
	# d. a bot's target in reach, 60 degrees off the facing: fires and hits
	_clear_targets()
	var u3 := _fake_unit(600.0)
	u3.global_position = player.global_position + kit.ahead().rotated(Vector3.UP, deg_to_rad(60.0)) * 2.0
	await process_frame
	fired = kit.basic_attack(u3)
	await _bite_done()
	_check(fired and u3.hits == 1, "basic bite (bot, target in reach): fires and hits")
	# e. mid-lunge, a bite does not fire
	_clear_targets()
	kit.lunge()
	await process_frame
	_check(not kit.basic_attack(null), "no basic bite while the lunge is under way")
	var t1 := Time.get_ticks_msec()
	while kit.current != "" and Time.get_ticks_msec() - t1 < 3000:
		await process_frame

	print("wolf kit check: %d failed" % fails)
	quit(1 if fails > 0 else 0)
