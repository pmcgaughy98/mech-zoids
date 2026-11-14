extends SceneTree
## Checks the gorilla's kit in the 3D slice (Claude, 2026-11-04, game feel lane): the ape sheet, the feet on the
## ground, and each slot doing what docs/plan/moba-kits.md (Gorilla) says, with each effect landing on its frame
## (the throw, the first beat, the fist-slam landing, the fists-down dome).
## Run: Godot --headless --fixed-fps 60 --path . --script res://tools/debug/ape3d_check.gd

const SCENE := preload("res://scenes/moba3d/ape_field_test.tscn")

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


func _wait_kit(kit: ApeKit) -> void:
	for i in 600:
		if kit.current == "":
			return
		await process_frame


func _run() -> void:
	var top := SCENE.instantiate()
	root.add_child(top)
	await _wait(2)
	var field := top.get_child(0)
	var player = field.get_node("Player")
	var sprite: DirectionalSprite3D = player.get_node("Sprite")
	var kit := player.get_node("Kit") as ApeKit
	_check(kit != null, "the Player's kit is the gorilla's")
	_check(player.get_children().filter(func(c): return c is RhinoKit).is_empty(), "the rhino kit is gone")
	var frames := sprite.sprite_frames
	for v in ["s", "se", "e", "ne", "n"]:
		_check(frames.has_animation("walk_" + v) and frames.has_animation("idle_" + v), "walk_%s and idle_%s exist" % [v, v])
	for a in [["chest_beat", 8], ["hex_shield", 6], ["bound", 9], ["hex_dome", 8], ["death", 8]]:
		for v in ["s", "se", "e", "ne", "n"]:
			var n := "%s_%s" % [a[0], v]
			_check(frames.has_animation(n) and frames.get_frame_count(n) == a[1], "%s has %d frames" % [n, a[1]])
	for v in ["se", "ne"]:  # the diagonals play their own drawings now, not the side view
		sprite.view = v
		sprite.action = "bound"
		_check(sprite.action_anim() == StringName("bound_" + v), "facing %s, bound plays bound_%s (got %s)" % [v, v, sprite.action_anim()])
	sprite.action = ""
	sprite.view = "n"
	var feet_y := sprite.global_position.y - (sprite.feet_edge_row - sprite.canvas_height / 2.0) * sprite.pixel_size
	_check(absf(feet_y - player.global_position.y) < 0.001, "feet stand on the ground (%.4f m)" % feet_y)

	var d1 = field.get_node("Dummy1")
	var d2 = field.get_node("Dummy2")
	var ally = field.get_node("Dummy4")
	_check(ally.is_in_group("kit_ally") and not ally.is_in_group("kit_target"), "Dummy4 stands in as an ally")
	var far := Vector3(40, 0, 40)
	for d in [d1, d2, field.get_node("Dummy3")]:
		d.global_position = far
	player.global_position = Vector3.ZERO
	player.facing = Vector3(0, 0, -1)

	# Passive, silverback.
	_check(kit._aura != null and kit._aura.get_parent() == player, "the silverback ring follows the gorilla")
	ally.global_position = Vector3(2, 0, 0)
	_check(kit.covers(ally), "an ally 2 m away is inside the silverback ring")
	ally.global_position = Vector3(4, 0, 0)
	_check(not kit.covers(ally), "an ally 4 m away is outside it")

	# 1 hex shield onto an ally: turns to it, the shield lands on the release frame, the slow is cleared.
	ally.global_position = Vector3(3, 0, 0)
	ally.slowed = 2.0
	kit.hex_shield()
	var seen := -1
	for i in 120:
		await process_frame
		if ApeKit.shield_on(ally) != null:
			seen = sprite.frame
			break
	_check(seen == ApeKit.SHIELD_RELEASE_FRAME, "the shield lands on the ally on the throw frame (frame %d)" % seen)
	_check(player.facing.x > 0.9, "the gorilla turned to throw at the ally")
	_check(ally.slowed == 0.0, "the shield cleared the ally's slow")
	_check(ApeKit.shield_on(player) == null, "the gorilla did not shield itself")
	await _wait_kit(kit)
	_check(not player.busy and sprite.action == "", "the gorilla is free after the throw")

	# 1 hex shield with no ally in range: on itself, and it takes a hit from any side.
	ally.global_position = far
	player.facing = Vector3(0, 0, -1)
	kit.hex_shield()
	await _wait_kit(kit)
	_check(ApeKit.shield_on(player) != null, "with no ally in range the shield goes on the gorilla")
	_check(kit.take_hit(Vector3(0, 0, 3)), "a hit from behind lands on its shield")
	await _wait(int((kit.shield_time + 0.6) * 60.0))
	_check(ApeKit.shield_on(player) == null and not kit.take_hit(Vector3(0, 0, -3)), "once the shield runs out, hits land")

	# 2 chest beat: enemies close by are taunted on the first beat; one farther away is not.
	d1.global_position = Vector3(0, 0, -2)
	d2.global_position = Vector3(0, 0, -5)
	kit.chest_beat()
	var beat_frame := -1
	for i in 120:
		await process_frame
		if d1.taunted > 0.0:
			beat_frame = sprite.frame
			break
	_check(beat_frame == ApeKit.BEAT_FRAMES[0] and d1.taunted_by == player,
		"a dummy 2 m away is taunted on the first beat (frame %d)" % beat_frame)
	_check(d2.taunted == 0.0, "a dummy 5 m away is not")
	await _wait_kit(kit)

	# 3 bound with no ally in range: a leap straight ahead, knocking back an enemy near the landing.
	d1.global_position = Vector3(0, 0, -5.5)
	d2.global_position = far
	var land := Vector3(0, 0, -kit.bound_distance)
	kit.bound()
	var bound_anim := ""
	var land_frame := -1
	var d1_at: Vector3 = d1.global_position
	for i in 240:
		await process_frame
		if sprite.action == "bound" and bound_anim == "":
			bound_anim = String(sprite.animation)
		if land_frame < 0 and d1.global_position.distance_to(d1_at) > 0.01:
			land_frame = sprite.frame
		if kit.current == "":
			break
	_check(bound_anim.begins_with("bound_"), "bound plays its own frames (%s)" % bound_anim)
	_check(land_frame == ApeKit.BOUND_LAND_FRAME, "the landing knock comes on the fist-slam frame (frame %d)" % land_frame)
	_check(player.global_position.distance_to(land) < 0.05, "bound lands %.1f m ahead (at %s)" % [kit.bound_distance, player.global_position])
	await _wait(30)
	_check(ApeKit.flat(d1.global_position - land).length() > 1.5, "the landing knocked the dummy back (%.2f m from the landing)"
		% ApeKit.flat(d1.global_position - land).length())
	_check(is_equal_approx(sprite.position.y, (sprite.feet_edge_row - sprite.canvas_height / 2.0) * sprite.pixel_size),
		"the sprite is back on its feet after the leap")

	# 3 bound to an ally: lands just short of it.
	d1.global_position = far
	ally.global_position = player.global_position + Vector3(4, 0, 0)
	var expect: Vector3 = player.global_position + Vector3(4.0 - kit.bound_stop_short, 0, 0)
	kit.bound()
	await _wait_kit(kit)
	_check(player.global_position.distance_to(expect) < 0.05, "bound lands %.1f m short of the ally" % kit.bound_stop_short)

	# 4 hex dome: hits from outside stop at the wall, hits from inside land, allies inside are under it.
	# Enemies inside when it rises are trapped; allies walk out (Preston, 2026-11-04).
	ally.global_position = Vector3(-1, 0, 0)
	d1.global_position = Vector3(1, 0, 0.5)
	d2.global_position = Vector3(5, 0, 0)
	player.global_position = Vector3.ZERO
	kit.hex_dome()
	var dome_frame := -1
	for i in 300:
		await process_frame
		if dome_frame < 0 and kit.dome_at(Vector3.ZERO) != null:
			dome_frame = sprite.frame
		if kit.current == "":
			break
	_check(dome_frame == ApeKit.DOME_SLAM_FRAME, "the dome rises on the fists-down frame (frame %d)" % dome_frame)
	_check(kit.dome_at(Vector3.ZERO) != null, "the hex dome stands over the gorilla")
	_check(kit.take_hit(Vector3(0, 0, -6)), "a hit from outside the dome stops at its wall")
	_check(not kit.take_hit(Vector3(0, 0, -1)), "a hit from inside the dome lands")
	_check(kit.dome_at(Vector3(1.5, 0, 1.5)) != null and kit.dome_at(Vector3(5, 0, 0)) == null,
		"a spot 2.1 m out is under the dome and one 5 m out is not")
	_check(d1.cage != null and d2.cage == null, "the enemy inside the dome is trapped and the one outside is not")
	d1.knock_aside(Vector3(4, 0, 0), 0.3)
	ally.walk_to(Vector3(-5, 0, 0), 0.5)
	await _wait(45)
	var r1 := ApeKit.flat(d1.global_position).length()
	_check(r1 > kit.dome_radius - 0.5 and r1 <= kit.dome_radius,
		"a knock toward the wall stops the trapped enemy at it (%.2f m out)" % r1)
	_check(ApeKit.flat(ally.global_position).length() > kit.dome_radius + 1.0, "an ally walks out through the wall")
	await _wait(int((kit.dome_time + 2.0) * 60.0))
	d1.knock_aside(Vector3(3, 0, 0), 0.3)
	await _wait(30)
	_check(ApeKit.flat(d1.global_position).length() > kit.dome_radius, "once the dome ends, the enemy can leave")
	_check(not player.busy and sprite.action == "", "the gorilla is free at the end")
	print("ape3d_check: %d failures" % fails)
	quit(1 if fails else 0)
