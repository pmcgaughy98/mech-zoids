extends SceneTree
## Checks the side pits you take and hold (scenes/moba3d/arena_pit.gd). Map design lane, 2026-11-05. Headless, and
## needs no other Godot running:
## Godot --headless --fixed-fps 60 --path . -s res://tools/map/pit_check.gd
## Part 1 drives red's pit by hand on the bare blockout with stand-in machines, stepping it 1/60 s at a time.
## Part 2 loads arena_play and checks the pits exist, the HUD found them, and the player takes one in a live match.
## Edits nothing.

const DT := 1.0 / 60.0
var passes := 0
var fails := 0


func _initialize() -> void:
	await _bench()
	await _live()
	print("pit_check: %d pass, %d fail" % [passes, fails])
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


func _run(pit: ArenaPit, secs: float) -> void:
	for i in roundi(secs / DT):
		pit._physics_process(DT)


func _bench() -> void:
	var arena: Node3D = load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	root.add_child(arena)
	await process_frame
	var pits := get_nodes_in_group("arena_pits")
	_ok(pits.size() == 2, "the blockout builds two pits (found %d)" % pits.size())
	if pits.size() != 2:
		return
	for p in pits:
		p.set_physics_process(false)
	var pit: ArenaPit = pits[0] if pits[0].home_team == "red" else pits[1]
	var marker: Node3D = arena.find_child("RedPit", true, false)
	_ok(marker != null and Vector2(pit.global_position.x - marker.global_position.x, pit.global_position.z - marker.global_position.z).length() < 0.1,
		"red's capture sits on the RedPit marker")
	var c := pit.global_position
	var away := c + Vector3(30, 0, 0)
	var taken: Array = []
	pit.pit_taken.connect(func(t: String) -> void: taken.append(t))

	var b1 := _unit("blue", c + Vector3(1, 0, 0))
	_run(pit, 8.9)
	_ok(pit.owner_team == "" and absf(pit.progress - 8.9 / 9.0) < 0.01, "one machine: not yet at 8.9 s (fill %.3f)" % pit.progress)
	_run(pit, 0.2)
	_ok(pit.owner_team == "blue" and taken == ["blue"], "one machine: taken by 9.1 s, signal once (%s)" % [taken])
	_ok(pit.locked_left > 89.0 and pit.is_in_group("vision_sources") and pit.get_meta("team", "") == "blue",
		"taken: locked 90 s and showing blue the area")
	_ok(ArenaPit.held(self, "blue") == 1 and ArenaPit.held(self, "red") == 0, "held(): blue 1, red 0")

	var r1 := _unit("red", c + Vector3(-1, 0, 0))
	var r2 := _unit("red", c + Vector3(0, 0, 1))
	b1.global_position = away
	_run(pit, 30.0)
	_ok(pit.owner_team == "blue" and pit.progress == 0.0, "locked: two red machines make no progress")
	_run(pit, 60.2)
	_ok(pit.locked_left == 0.0 and not pit.is_in_group("vision_sources"), "the lock ends at 90 s and the vision goes")
	var p0 := pit.progress
	_run(pit, 3.0)
	_ok(absf(pit.progress - p0 - 0.5) < 0.01 and pit.capturing == "red", "two machines: 3 s fills half (6 s to take)")

	b1.global_position = c + Vector3(1, 0, 0)
	var before := pit.progress
	_run(pit, 2.0)
	_ok(pit.contested and pit.progress == before, "both teams inside: the fill pauses, it doesn't reset")
	r1.global_position = away
	r2.global_position = away + Vector3(0, 0, 2)
	_run(pit, 1.0)
	_ok(absf(pit.progress - (before - 1.0 / 9.0)) < 0.01, "the owner alone pushes the enemy fill back")
	b1.global_position = away + Vector3(0, 0, -2)
	var held_at := pit.progress
	_run(pit, 2.9)
	_ok(absf(pit.progress - held_at) < 0.001, "empty: the fill holds for 3 s")
	_run(pit, 2.0)
	_ok(pit.progress < held_at - 0.15, "then fades (%.3f to %.3f)" % [held_at, pit.progress])
	_run(pit, 20.0)
	_ok(pit.progress == 0.0 and pit.capturing == "", "and empties")

	var r3 := _unit("red", c + Vector3(0, 0, -1))
	r1.global_position = c + Vector3(-1, 0, 0)
	r2.global_position = c + Vector3(0, 0, 1)
	_run(pit, 4.4)
	_ok(pit.owner_team == "blue", "three machines: not yet at 4.4 s")
	_run(pit, 0.2)
	_ok(pit.owner_team == "red" and taken == ["blue", "red"], "three machines: taken back by 4.6 s")
	_ok(ArenaPit.held(self, "red") == 1 and ArenaPit.held(self, "blue") == 0, "held(): red 1, blue 0")
	r3.global_position = c + Vector3(5.6, 0, 0)
	_ok(pit.count_inside().red == 2, "a machine past the 5.5 m edge doesn't count")

	for u in [b1, r1, r2, r3]:
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
	var pits := get_nodes_in_group("arena_pits")
	_ok(pits.size() == 2, "arena_play has two pits (found %d)" % pits.size())
	_ok(play.hud._pits.size() == 2, "the HUD found both pits")
	if pits.size() != 2:
		return
	var p = play.player
	var theirs: ArenaPit = pits[0] if pits[0].home_team != p.team else pits[1]
	p.global_position = theirs.global_position
	for i in 600:
		await physics_frame
	_ok(theirs.owner_team == p.team, "live: the player takes the other team's pit inside 10 s (owner '%s')" % theirs.owner_team)
	_ok("took" in str(play.hud.feed_lines()).to_lower(), "live: the kill feed says so: %s" % [play.hud.feed_lines()])
	play.queue_free()
	await process_frame
