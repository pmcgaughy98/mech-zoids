extends SceneTree
## The plaza beacon's hooks on the match side (game feel lane, 2026-11-05, for the map lane's ArenaBeacon). The beacon
## itself is the map lane's; this calls the director's handler directly, as beacon_taken would:
##   the director is in group "match_director"; taking the beacon switches the other team's tower off for
##   MatchRules.beacon_tower_off (no target, no shots) and leaves its own on; a second take only extends it; the tower
##   shoots again when the time runs out; a fallen tower is left alone.
## Run: godot --headless --fixed-fps 60 --path . --script res://tools/debug/beacon_hook_check.gd
var fails := 0


func _initialize() -> void:
	change_scene_to_file("res://scenes/moba3d/arena_play.tscn")
	_run.call_deferred()


func _wait(k: int) -> void:
	for i in k:
		await process_frame


func _check(ok: bool, what: String) -> void:
	print(("PASS " if ok else "FAIL ") + what)
	if not ok:
		fails += 1


func _run() -> void:
	await _wait(30)
	var d = current_scene.director
	var p = current_scene.player
	_check(d.is_in_group("match_director") and get_first_node_in_group("match_director") == d, "the director is in group match_director")
	var rt: MatchStructure = d.structures["RedTower"]
	var bt: MatchStructure = d.structures["BlueTower"]
	var shots := [0]
	rt.tower_shot.connect(func() -> void: shots[0] += 1)
	var to := MatchTeams.flat(p.global_position - rt.global_position).normalized()
	p.global_position = rt.global_position + to * (rt.body_r + 5.0)
	await _wait(150)
	_check(shots[0] > 0, "on, the red tower shoots the player standing under it (%d shots in 2.5 s)" % shots[0])
	p.hp = p.max_hp
	d._on_beacon_taken("blue")
	_check(is_equal_approx(rt.off_left, MatchRules.beacon_tower_off) and rt.target == null, "blue takes the beacon: the red tower is off for %.0f s, no target" % rt.off_left)
	_check(bt.off_left == 0.0, "the blue tower stays on")
	shots[0] = 0
	await _wait(150)
	_check(shots[0] == 0, "off, it holds fire with the player under it (%d shots in 2.5 s)" % shots[0])
	var left := rt.off_left
	d._on_beacon_taken("blue")
	_check(rt.off_left > left and rt.off_left <= MatchRules.beacon_tower_off + 0.001, "a second take extends it to the full time again (%.2f from %.2f)" % [rt.off_left, left])
	rt.off_left = 0.05
	await _wait(150)
	_check(rt.off_left == 0.0 and shots[0] > 0, "when the time runs out it shoots again (%d shots)" % shots[0])
	bt.take_damage(bt.hp + 1.0, rt)
	await _wait(2)
	d._on_beacon_taken("red")
	_check(not bt.alive and bt.off_left == 0.0, "a fallen tower is left alone")
	d._on_beacon_taken("red")
	print("beacon_hook_check: %d failures" % fails)
	quit(1 if fails > 0 else 0)
