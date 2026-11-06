extends SceneTree
## Checks the plaza beacon (scenes/moba3d/arena_beacon.gd) and the switched-off tower look. Map design lane,
## 2026-11-05. Headless, and needs no other Godot running:
## Godot --headless --fixed-fps 60 --path . -s res://tools/map/beacon_check.gd
## Part 1 drives the beacon by hand on the bare blockout (no director, so it keeps its own clock) with stand-in
## machines, 1/60 s at a time, and switches red's tower off and on. Part 2 loads arena_play, brings the beacon up
## early and has the player take it. Edits nothing.

const DT := 1.0 / 60.0
var passes := 0
var fails := 0


func _initialize() -> void:
	await _bench()
	await _live()
	print("beacon_check: %d pass, %d fail" % [passes, fails])
	quit(1 if fails > 0 else 0)


func _ok(cond: bool, what: String) -> void:
	if cond:
		passes += 1
		print("  pass  ", what)
	else:
		fails += 1
		print("  FAIL  ", what)


func _unit(team: String, at: Vector3) -> Node3D:
	var u := Node3D.new()
	u.add_to_group("map_units")
	u.set_meta("unit_kind", "machine")
	u.set_meta("team", team)
	root.add_child(u)
	u.global_position = at
	return u


func _run(b: Node, secs: float) -> void:
	for i in roundi(secs / DT):
		b._physics_process(DT)


func _bench() -> void:
	var arena = load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	root.add_child(arena)
	await process_frame
	var bs := get_nodes_in_group("arena_beacons")
	_ok(bs.size() == 1, "the blockout builds one beacon (found %d)" % bs.size())
	if bs.size() != 1:
		return
	var b = bs[0]
	b.set_physics_process(false)
	_ok(Vector2(b.global_position.x, b.global_position.z).length() < 0.1, "it sits at the plaza centre")
	_ok(get_nodes_in_group("arena_pits").size() == 2 and not b.is_in_group("arena_pits"), "it isn't counted as a pit")
	var ups: Array = []
	var takes: Array = []
	b.beacon_up.connect(func() -> void: ups.append(b.now()))
	b.beacon_taken.connect(func(t: String) -> void: takes.append(t))
	var c: Vector3 = b.global_position

	var blue := _unit("blue", c + Vector3(1, 0, 0))
	_run(b, 239.9)
	_ok(not b.active and ups.is_empty() and not b.get_node("Ring").visible and not b.get_node("Beam").visible,
		"down until 4:00, nothing showing (up in %.1f s)" % b.up_in())
	_ok(b.progress == 0.0, "a machine standing there before 4:00 takes nothing")
	_run(b, 0.2)
	_ok(b.active and ups.size() == 1 and b.get_node("Ring").visible and b.get_node("Beam").visible,
		"up at 4:00, beacon_up once, ring and beam showing")
	b.progress = 0.0 # the machine was already inside as it came up; start the timing from now
	b.capturing = ""
	_run(b, 8.9)
	_ok(b.active and takes.is_empty(), "one machine: not yet at 8.9 s (fill %.3f)" % b.progress)
	_run(b, 0.2)
	_ok(not b.active and takes == ["blue"] and b.owner_team == "", "taken by 9.1 s: beacon_taken(blue) once, nobody keeps it")
	_ok(absf(b.up_in() - 300.0) < 0.25, "back in 5:00 (%.1f s)" % b.up_in())
	_run(b, 1.0)
	_ok(not b.get_node("Ring").visible and not b.get_node("Beam").visible, "a second after the take, nothing shows")
	blue.global_position = c + Vector3(30, 0, 0)
	_run(b, b.up_in() - 0.5)
	_ok(not b.active, "still down half a second before 5:00 is up")
	_run(b, 0.6)
	_ok(b.active and ups.size() == 2, "up again 5:00 after the take")
	var r1 := _unit("red", c + Vector3(-1, 0, 0))
	var r2 := _unit("red", c + Vector3(0, 0, 1))
	_run(b, 5.9)
	_ok(b.active, "two machines: not yet at 5.9 s")
	_run(b, 0.2)
	_ok(not b.active and takes == ["blue", "red"], "two machines: taken by 6.1 s")

	_ok(arena.has_method("set_structure_off"), "the arena has set_structure_off")
	var s: Dictionary = arena._structures.get("RedTower", {})
	var e0: float = s.light.light_energy
	arena.set_structure_off("RedTower", true)
	_ok(s.get("off", false) and absf(s.light.light_energy - e0 * 0.15) < 0.001 and not s.ring.visible,
		"switched off: light at 15%, range ring hidden")
	var yaw: float = s.gem.rotation.y
	arena._process(0.5)
	_ok(is_equal_approx(s.gem.rotation.y, yaw), "switched off: the head stops turning")
	arena.set_structure_off("RedTower", false)
	_ok(not s.off and is_equal_approx(s.light.light_energy, e0) and s.ring.visible, "switched back on: all restored")

	for u in [blue, r1, r2]:
		u.queue_free()
	arena.queue_free()
	await process_frame
	await process_frame


func _live() -> void:
	var play: Node = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	for i in 2:
		await process_frame
	var d = play.director
	for i in 600:
		if d.ready_to_play:
			break
		await physics_frame
	for i in 3:
		await process_frame
	var bs := get_nodes_in_group("arena_beacons")
	_ok(bs.size() == 1, "arena_play has the beacon")
	_ok(play.hud._beacon != null, "the HUD found it")
	if bs.size() != 1:
		return
	var b = bs[0]
	print("  note  director in group match_director: ", d.is_in_group("match_director"), "; beacon clock ", snappedf(b.now(), 0.1), " vs elapsed ", snappedf(d.elapsed, 0.1))
	b.up_at = b.now() + 0.5
	for i in 60:
		await physics_frame
	_ok(b.active, "live: it comes up")
	_ok("beacon is up" in str(play.hud.feed_lines()).to_lower(), "live: the feed says so")
	var p = play.player
	p.global_position = b.global_position + Vector3(0, 0, 1.0)
	for i in 600:
		await physics_frame
	_ok(not b.active and b.last_taker == p.team, "live: the player takes it inside 10 s (taker '%s')" % b.last_taker)
	_ok("took the beacon" in str(play.hud.feed_lines()).to_lower(), "live: the feed says so: %s" % [play.hud.feed_lines()])
	var other: String = "red" if p.team == "blue" else "blue"
	var tw = d.structures.get(other.capitalize() + "Tower")
	if tw != null and tw.get("off_left") != null:
		_ok(float(tw.off_left) > 0.0, "live: the %s tower is switched off (%.1f s left)" % [other, float(tw.off_left)])
	else:
		print("  note  MatchStructure.off_left isn't there yet (game feel's part), so the switch-off isn't checked")
	play.queue_free()
	await process_frame
