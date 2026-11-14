extends SceneTree
## Checks the machines in the map lane's arena (Claude, 2026-11-04, game feel lane; Preston: "Hook up the map and game
## feel"): walls stop and slide the machines; tosses, knocks, the stampede and the bound stop at walls; machine_pos
## follows the machine; Tab swaps rhino and gorilla; and the gorilla's hex dome rules from moba-kits.md (Gorilla):
## enemies cannot cross the wall either way, allies can, enemy shots stop at it from either side and wear it down, and
## at zero it breaks early; ally shots stop at it both ways too but leave its health alone (Preston, 2026-11-04).
## Run: Godot --headless --fixed-fps 60 --path . --script res://tools/debug/arena_check.gd

const SCENE := preload("res://scenes/moba3d/arena_play.tscn")

var fails := 0


func _initialize() -> void:
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	print(("PASS " if ok else "FAIL ") + what)
	if not ok:
		fails += 1


func _wait(n: int) -> void:
	for i in n:
		await process_frame


func _wait_kit(kit) -> void:
	for i in 900:
		if kit.get("current") == "":
			return
		await process_frame


func _flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _run() -> void:
	var top := SCENE.instantiate()
	top.sandbox = true  # the test field with dummies, not the match (match_check covers that)
	root.add_child(top)
	await _wait(4)
	var player = top.player
	var sprite: DirectionalSprite3D = player.get_node("Sprite")
	_check(player.global_position.distance_to(top.spawn_point("blue")) < 0.01, "the machine starts on the blue spawn %s"
		% top.spawn_point("blue"))
	_check(top.get_tree().get_nodes_in_group("kit_target").size() == top.LANE_DUMMIES.size(), "enemy dummies stand in the lane")
	for d in top.get_tree().get_nodes_in_group("kit_target"):
		d.queue_free()  # the check places its own
	await _wait(2)
	var rad: float = player.body_radius()

	# A wall to test against: from a clear spot, a chest-height ray along an axis that meets something 4-15 m away.
	var spot := Vector3.ZERO
	var dir := Vector3.ZERO
	var wall_d := 0.0
	var wall_n := Vector3.ZERO
	var tries := [[Vector3(0, 0, 70), Vector3.RIGHT], [Vector3(0, 0, 70), Vector3.LEFT], [Vector3(0, 0, 70), Vector3.BACK],
		[Vector3(0, 0, 0), Vector3.RIGHT], [Vector3(30, 0, 60), Vector3.RIGHT]]
	for c in tries:
		var a: Vector3 = c[0]
		var u: Vector3 = c[1]
		if ArenaMotion.blocked(player, a, rad):
			continue
		var h := ArenaMotion.ray(player, a + Vector3.UP, a + Vector3.UP + u * 15.0)
		if h.is_empty():
			continue
		var dist := _flat(h.position - a).dot(u)
		if dist >= 4.0:
			spot = a
			dir = u
			wall_d = dist
			wall_n = _flat(h.normal).normalized()
			break
	_check(wall_d > 0.0, "found a wall %.2f m from %s along %s" % [wall_d, spot, dir])
	if wall_d == 0.0:
		print("arena_check: %d failures" % fails)
		quit(1)
		return

	# Walking straight at it stops short; walking into it at 45 degrees slides along it.
	player.global_position = spot
	player.move_override = dir
	await _wait(int((wall_d / player.move_speed + 1.0) * 60.0))  # past the wall, a second spare
	_check(_against(player, player.global_position, dir, rad, spot), "walking at the wall stops against it, %.2f m short along the walk (radius %.2f placeholder)"
		% [wall_d - _flat(player.global_position - spot).dot(dir), rad])
	var along := wall_n.cross(Vector3.UP).normalized()
	var before: Vector3 = player.global_position
	player.move_override = (-wall_n + along).normalized()
	await _wait(60)
	var slid := _flat(player.global_position - before).dot(along)
	_check(slid > 1.0 and _against(player, player.global_position, -wall_n, rad, spot),
		"walking into it at 45 degrees slides %.2f m along it and stays against it" % slid)
	player.move_override = null
	await _wait(1)

	# machine_pos follows the machine.
	_check(ProjectSettings.has_setting("shader_globals/machine_pos"), "project.godot declares the machine_pos shader global")
	_check(player.published_pos.distance_to(player.global_position) < 0.001, "machine_pos is the machine's feet this frame")

	# A dummy tossed or knocked at the wall stops at it.
	var d := TrainingDummy.new()
	top.add_child(d)
	for how in ["toss", "knock"]:
		d.global_position = spot + dir * (wall_d - 2.0)
		if how == "toss":
			d.toss_to(spot + dir * (wall_d + 3.0), 1.5, 0.5, 0.0)
		else:
			d.knock_aside(dir * 4.0, 0.35)
		await _wait(45)
		var dg := _flat(d.global_position - spot).dot(dir)
		_check(_against(player, d.global_position, dir, TrainingDummy.BODY_R, spot), "a %s at the wall stops the dummy against it (%.2f m short)"
			% [how, wall_d - dg])
	d.queue_free()

	# The rhino's stampede and the gorilla's bound, aimed at the wall, end against it.
	var rk = player.get_node("Kit")
	_check(rk is RhinoKit, "the machine starts as the rhino")
	player.global_position = spot + dir * (wall_d - 3.0)
	player.facing = dir
	rk.stampede()
	await _wait_kit(rk)
	var sg := _flat(player.global_position - spot).dot(dir)
	_check(_against(player, player.global_position, dir, rad, spot), "a stampede at the wall ends against it (%.2f m short)" % (wall_d - sg))
	top.swap()
	await _wait(2)
	var kit: ApeKit = player.get_node("Kit") as ApeKit
	_check(kit != null and sprite.sprite_frames == ApeKit.APE_FRAMES, "Tab swaps the rhino for the gorilla")
	player.global_position = spot + dir * (wall_d - 3.0)
	player.facing = dir
	kit.bound()
	await _wait_kit(kit)
	var bg := _flat(player.global_position - spot).dot(dir)
	_check(_against(player, player.global_position, dir, rad, spot), "a bound at the wall lands against it (%.2f m short)" % (wall_d - bg))

	# The hex dome, in the open plaza.
	var c := Vector3.ZERO
	player.global_position = c
	player.facing = Vector3.FORWARD
	kit.dome_time = 30.0  # long enough for every test below; the break test ends it early
	var e_in := _dummy(top, c + Vector3(1.2, 0, 0.6))
	var e_out := _dummy(top, c + Vector3(5.0, 0, 0))
	var a_in := _dummy(top, c + Vector3(-1.0, 0, 0))
	var a_out := _dummy(top, c + Vector3(-5.5, 0, 0.5))
	ApeKit.make_ally(a_in)
	ApeKit.make_ally(a_out)
	kit.hex_dome()
	for i in 180:
		await process_frame
		if kit.dome_at(c) != null:
			break
	var dome: HexShield = kit.dome_at(c)
	_check(dome != null and dome.health == kit.dome_health, "the dome stands with its wall health (%.0f, placeholder)" % kit.dome_health)
	e_out.walk_to(c, 1.0)
	e_in.walk_to(c + Vector3(6, 0, 0.6), 1.0)
	a_out.walk_to(c + Vector3(-1.5, 0, 1.0), 1.0)
	a_in.walk_to(c + Vector3(-6.0, 0, -1.0), 1.0)
	await _wait(75)
	var r_out := _flat(e_out.global_position - c).length()
	var r_in := _flat(e_in.global_position - c).length()
	_check(r_out >= dome.radius, "an enemy outside walking in stops at the wall (%.2f m out, wall at %.1f)" % [r_out, dome.radius])
	_check(r_in <= dome.radius, "a trapped enemy walking out stops at the wall (%.2f m out)" % r_in)
	_check(_flat(a_out.global_position - c).length() < dome.radius and _flat(a_in.global_position - c).length() > dome.radius,
		"allies walk in and out through the wall")
	var h0 := dome.health
	var s1: TestShot = e_in.fire_at(c + Vector3(9, 0, 0.6))
	await _wait(30)
	_check(s1.stopped_by == "dome" and is_equal_approx(dome.health, h0 - s1.damage),
		"a trapped enemy's shot stops at the wall and takes %.0f off it (placeholder; %.0f left)" % [s1.damage, dome.health])
	var s2: TestShot = e_out.fire_at(c, player)
	await _wait(30)
	_check(s2.stopped_by == "dome" and is_equal_approx(dome.health, h0 - s1.damage - s2.damage),
		"an enemy shot from outside stops at the wall and wears it down too (%.0f left)" % dome.health)
	# Ally shots stop at the wall both ways too, and take nothing off it (Preston reversed the pass-through,
	# 2026-11-04). 30 frames at the placeholder 14 m/s is about 7 m, well past the wall either way.
	var h1 := dome.health
	var s3 := TestShot.fire(top, c + Vector3(0.5, 0, 0), c + Vector3(9, 0, 0), false)
	await _wait(30)
	var r3 := _flat(s3.global_position - c).length()
	_check(s3.stopped_by == "dome" and r3 <= dome.radius and dome.health == h1,
		"an ally's shot from inside stops at the wall, health untouched (%.2f m out, health %.0f): '%s'"
		% [r3, dome.health, s3.stopped_by])
	var s4 := TestShot.fire(top, c + Vector3(6.0, 0, -1.0), c + Vector3(-3.0, 0, -1.0), false)
	await _wait(30)
	var r4 := _flat(s4.global_position - c).length()
	_check(s4.stopped_by == "dome" and r4 > dome.radius and dome.health == h1,
		"an ally's shot from outside stops at the wall, health untouched (%.2f m out, health %.0f): '%s'"
		% [r4, dome.health, s4.stopped_by])
	dome.health = 15.0
	e_out.fire_at(c)
	await _wait(30)
	_check(is_instance_valid(dome) and dome.is_up(), "a shot that leaves health standing does not break it (%.0f left)" % dome.health)
	e_out.fire_at(c)
	await _wait(30)
	_check(not is_instance_valid(dome) or not dome.is_up(), "at zero health the dome breaks early")
	e_out.walk_to(c + Vector3(1.0, 0, 0), 0.8)
	await _wait(60)
	_check(_flat(e_out.global_position - c).length() < 3.0, "with the dome broken, the enemy walks in")
	_check(not player.busy, "the gorilla is free at the end")
	# machine_hidden (map lane's request): 0 with the machine in plain view, so walls don't thin; 1 with a wall between
	# it and the camera; eased between, not a jump. The wall here is a test sphere on the arena's wall layer.
	var cam = top.arena.get_node("Camera")
	_check(ProjectSettings.has_setting("shader_globals/machine_hidden"), "project.godot declares the machine_hidden shader global")
	player.global_position = c
	await _wait(30)
	_check(player.machine_hidden < 0.001, "in plain view machine_hidden is 0 (%.2f)" % player.machine_hidden)
	var block := StaticBody3D.new()
	block.collision_layer = ArenaMotion.wall_mask
	var ball := CollisionShape3D.new()
	ball.shape = SphereShape3D.new()
	(ball.shape as SphereShape3D).radius = 0.5
	block.add_child(ball)
	top.add_child(block)
	block.global_position = (cam.global_position as Vector3).lerp(c + Vector3.UP, 0.5)
	await _wait(4)
	var rising: float = player.machine_hidden
	_check(rising > 0.0 and rising < 1.0, "a wall coming between eases machine_hidden up, not a jump (%.2f after 4 frames)" % rising)
	await _wait(30)
	_check(player.machine_hidden > 0.999, "with a wall between camera and machine, machine_hidden is 1 (%.2f)" % player.machine_hidden)
	block.queue_free()
	await _wait(30)
	_check(player.machine_hidden < 0.001, "with the wall gone it eases back to 0 (%.2f)" % player.machine_hidden)
	# The chase camera stays inside the map edge when turned to face inward there (map lane's request).
	player.global_position = Vector3(41.0, 0, 0)
	cam.yaw_degrees = 90.0  # the camera swings to the machine's east, past the edge
	cam.snap()
	_check(cam.bounds.x > 0.0 and absf(cam.global_position.x) <= cam.bounds.x + 0.001,
		"near the east edge the camera stays inside the map (x %.2f, limit %.2f)" % [cam.global_position.x, cam.bounds.x])
	print("arena_check: %d failures" % fails)
	quit(1 if fails else 0)


## Standing against a wall: clear where it is, blocked a short step further along `into`, and no wall between it and
## where the test started (so it never went through).
func _against(n: Node3D, p: Vector3, into: Vector3, r: float, start: Vector3) -> bool:
	var clear := not ArenaMotion.blocked(n, p, r)
	var ahead := ArenaMotion.blocked(n, p + into * 0.15, r)
	var between := ArenaMotion.ray(n, start + Vector3.UP, p + Vector3.UP).is_empty()
	if not (clear and ahead and between):
		print("   at %s: clear %s, wall a step ahead %s, no wall since the start %s" % [p.snapped(Vector3.ONE * 0.01), clear, ahead, between])
	return clear and ahead and between


func _dummy(parent: Node, p: Vector3) -> Node3D:
	var d := TrainingDummy.new()
	parent.add_child(d)
	d.global_position = p
	return d
