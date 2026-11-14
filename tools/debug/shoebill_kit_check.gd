extends SceneTree
## The shoebill kit's first slice (Claude, 2026-11-05, Shoebill session): moon phases (patience), moonbeam and the lens
## flick basic attack, on the field's stand-in body. Measures the kit itself: charges over time, the beam's reach and
## damage scale, who it hits and misses, the walking rule, and the basic's reach and damage.
## Run: godot --headless --fixed-fps 60 --path . --script res://tools/debug/shoebill_kit_check.gd
var fails := 0


func _initialize() -> void:
	change_scene_to_file("res://scenes/moba3d/shoebill_field_test.tscn")
	_run.call_deferred()


func _wait(k: int) -> void:
	for i in k:
		await process_frame


func _secs(s: float) -> void:
	await _wait(int(round(s * 60.0)))


func _check(ok: bool, what: String) -> void:
	print(("PASS " if ok else "FAIL ") + what)
	if not ok:
		fails += 1


func _near(a: float, b: float, eps := 0.01) -> bool:
	return absf(a - b) <= eps


func _dmg(d: Node) -> float:
	return d.last_hit_scale * MatchRules.kit_hit_damage


func _clear(list: Array) -> void:
	for d in list:
		d.last_hit_scale = 0.0


func _run() -> void:
	await _wait(10)
	var f = current_scene
	var kit = f.kit
	var p: Node3D = f.player
	_check(kit != null and p.get_node_or_null("Kit") == kit, "the shoebill kit is on the field's player")
	var field: Node = f.get_child(0)
	var d1: Node3D = field.get_node("Dummy1")
	var d2: Node3D = field.get_node("Dummy2")
	var d4: Node3D = field.get_node("Dummy4")
	var start := p.global_position
	var down := Vector3(0.0, 0.0, -1.0)
	d4.global_position = Vector3(start.x, d4.global_position.y, start.z - 12.5)
	var dummies := [d1, d2, d4]
	p.input_override = Vector2.ZERO
	kit._spend()

	# passive, moon phases
	await _secs(1.8)
	_check(kit.charges == 0, "1.8 s still: no charge yet (%d)" % kit.charges)
	await _secs(0.7)
	_check(kit.charges == 1, "2.5 s still: crescent, 1 charge (%d)" % kit.charges)
	await _secs(1.7)
	_check(kit.charges == 3, "4.2 s still: full moon, 3 charges (%d)" % kit.charges)
	await _secs(1.0)
	_check(kit.charges == 3, "it stops at 3 (%d)" % kit.charges)
	_check(kit._disc != null and kit._disc.visible, "the moon disc shows over the body")

	# 1, moonbeam, charged
	_clear(dummies)
	_check(kit.moonbeam(down), "moonbeam starts")
	_check(kit.charges == 0, "the cast spends the charges (%d)" % kit.charges)
	await _wait(6)
	_check(_dmg(d1) == 0.0 and _dmg(d4) == 0.0, "nothing is hit during the 0.3 s warning line")
	await _secs(0.4)
	var rec: Dictionary = kit.last["moonbeam"]
	_check(rec["fired"], "the beam fired after the warning")
	_check(_near(rec["reach"], 13.0), "charged reach is 13 m (%.2f)" % rec["reach"])
	_check(_near(_dmg(d4), 87.0, 0.5), "the dummy 12.5 m away takes 87 (%.1f)" % _dmg(d4))
	_check(_near(_dmg(d1), 87.0, 0.5), "the beam passes through: the near dummy takes 87 too (%.1f)" % _dmg(d1))
	_check(_dmg(d2) == 0.0, "the dummy 1.6 m off the line is missed (%.1f)" % _dmg(d2))
	_check(not p.busy and kit.current == "", "the shoebill is free again after the beam")

	# 1, moonbeam, no charges
	_clear(dummies)
	kit.moonbeam(down)
	await _secs(0.5)
	rec = kit.last["moonbeam"]
	_check(rec["charges"] == 0 and _near(rec["reach"], 10.0), "with no charges the reach is 10 m (%.2f)" % rec["reach"])
	_check(_dmg(d4) == 0.0, "so the dummy at 12.5 m is out of reach (%.1f)" % _dmg(d4))
	_check(_near(_dmg(d1), 60.0, 0.5), "and the near dummy takes the plain 60 (%.1f)" % _dmg(d1))

	# walking keeps the charges for 3 s
	await _secs(4.2)
	_check(kit.charges == 3, "full again after 4.2 s still (%d)" % kit.charges)
	p.move_override = Vector3(1.0, 0.0, 0.0)
	await _secs(2.0)
	_check(kit.charges == 3, "2 s of walking keeps them (%d, speed %.2f)" % [kit.charges, p.speed])
	await _secs(1.5)
	_check(kit.charges == 0, "3.5 s of walking loses them (%d)" % kit.charges)
	p.move_override = null
	p.input_override = Vector2.ZERO
	await _wait(5)
	p.global_position = start

	# basic attack, lens flick
	_check(_near(kit.basic_cooldown, 1.0) and _near(kit.basic_range, 7.0), "the director will read basic_cooldown 1.0 and basic_range 7.0")
	_clear(dummies)
	d4.global_position = Vector3(start.x, d4.global_position.y, start.z - 6.5)
	var cam := root.get_camera_3d()
	p.facing = Vector3(1.0, 0.0, 0.0)  # facing sideways, so only the mouse can point it up the line
	if cam != null:
		p.aim_screen_override = cam.unproject_position(start + down * 5.0)  # the mouse, 5 m up the line
	_check(kit.basic_attack(null), "the basic fires with no target (it aims at the mouse)")
	p.aim_screen_override = null
	_check(_near(_dmg(d1), 28.0, 0.5) and _dmg(d4) == 0.0, "it hits only the first dummy in line, for 28 (%.1f and %.1f)" % [_dmg(d1), _dmg(d4)])
	_clear(dummies)
	d1.global_position += Vector3(3.0, 0.0, 0.0)
	await _wait(2)
	_check(kit.basic_attack(d4), "a bot's basic with a target fires")
	_check(_near(_dmg(d4), 28.0, 0.5), "the target 6.5 m away takes 28 (%.1f)" % _dmg(d4))
	_clear(dummies)
	d4.global_position = Vector3(start.x, d4.global_position.y, start.z - 8.5)
	await _wait(2)
	kit.basic_attack(d4)
	_check(_dmg(d4) == 0.0, "a target 8.5 m away is out of the basic's reach (%.1f)" % _dmg(d4))

	print("shoebill_kit_check: %d failures" % fails)
	quit(1 if fails > 0 else 0)
