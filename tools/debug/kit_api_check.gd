extends SceneTree
## Shared kit API check (game feel lane, 2026-11-05, for the squirrel kit Preston took: "Take it").
## Opens the match and checks the four pieces the squirrel needs from the shared code:
##   1 hit(by, scale): kit damage x scale on a minion and a machine (plating or shields still halve it).
##   2 a kit's own basic_attack(target): Space (player_attack) and a bot's basic go to it; the director keeps the
##     cooldown (the kit's basic_cooldown) and the gates.
##   3 move_dir(): the movement keys in world space, zero when standing.
##   4 boost(mult, t, key): timed speed changes that multiply with brace and a slow, refresh by key, expire,
##     and clear on respawn.
## Run: godot --headless --fixed-fps 60 --path . --script res://tools/debug/kit_api_check.gd
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


func _near(a: float, b: float, eps := 0.01) -> bool:
	return absf(a - b) <= eps


func _stub() -> Node:
	var gs := GDScript.new()
	gs.source_code = "extends Node\nvar basic_cooldown := 0.7\nvar basic_range := 2.0\nvar calls: Array = []\nfunc basic_attack(t) -> bool:\n\tcalls.append(t)\n\treturn true\n"
	gs.reload()
	var s := Node.new()
	s.set_script(gs)
	s.name = "Kit"
	return s


func _swap_kit(m: Node) -> Node:
	var old := m.get_node_or_null("Kit")
	if old != null:
		old.name = "OldKit"
		old.process_mode = Node.PROCESS_MODE_DISABLED
	var s := _stub()
	m.add_child(s)
	return s


func _run() -> void:
	await _wait(60)
	var a = current_scene
	var d = a.director
	var p = a.player
	var k := MatchRules.kit_hit_damage
	var rm: Node3D = null
	for m in d.machines:
		if m.team == "red":
			rm = m
			break
	_check(rm != null, "a red machine is in the match")

	# 1 hit scale
	var mn = d.spawn_minion("red", p.global_position + Vector3(3.0, 0.0, 0.0))
	await _wait(2)
	_check(mn != null and mn is MatchMinion, "spawn_minion hands back the minion")
	var h0: float = mn.hp
	mn.hit(p, 18.0 / k)
	_check(_near(h0 - mn.hp, 18.0) and _near(mn.last_hit_scale, 18.0 / k), "a minion hit at 18 / kit damage takes 18 (took %.2f)" % (h0 - mn.hp))
	h0 = mn.hp
	mn.hit(p)
	_check(_near(h0 - mn.hp, k) and _near(mn.last_hit_scale, 1.0), "a plain minion hit still takes the full %.0f (took %.2f)" % [k, h0 - mn.hp])
	h0 = p.hp
	p.hit(rm, 0.5)
	var took: float = h0 - p.hp
	_check(_near(took, k * 0.5) or _near(took, k * 0.5 * MatchRules.blocked_share), "a machine hit at 0.5 takes %.0f, or %.0f through the plating (took %.2f)" % [k * 0.5, k * 0.5 * MatchRules.blocked_share, took])
	h0 = p.hp
	p.hit(rm)
	took = h0 - p.hp
	_check(_near(took, k) or _near(took, k * MatchRules.blocked_share), "a plain machine hit is unchanged (took %.2f)" % took)
	p.hp = p.max_hp
	mn.queue_free()

	# 3 move direction
	var cam := root.get_camera_3d()
	var right := Vector3(cam.global_basis.x.x, 0.0, cam.global_basis.x.z).normalized()
	var fwd := Vector3(-cam.global_basis.z.x, 0.0, -cam.global_basis.z.z).normalized()
	p.input_override = Vector2(1.0, 0.0)
	_check(p.move_dir().dot(right) > 0.99, "move_dir follows the keys: D is screen right (%s)" % p.move_dir())
	p.input_override = Vector2(0.0, -1.0)
	_check(p.move_dir().dot(fwd) > 0.99, "W is screen up (%s)" % p.move_dir())
	p.input_override = Vector2.ZERO
	_check(p.move_dir().length() < 0.001, "standing still gives zero")
	p.input_override = null
	p.move_override = Vector3(0.0, 0.0, 1.0)
	_check(p.move_dir().is_equal_approx(Vector3(0.0, 0.0, 1.0)), "a scripted move wins")
	p.move_override = null

	# 4 speed boosts
	p.slowed = 0.0
	p.boosts.clear()
	p.boost(1.3, 0.5, &"tail_ping")
	_check(_near(p.speed_factor(), 1.3), "a 1.3 boost alone gives 1.3 (%.3f)" % p.speed_factor())
	p.slowed = 1.0
	_check(_near(p.speed_factor(), 0.78), "with a slow 1.3 x 0.6 = 0.78 (%.3f)" % p.speed_factor())
	p.speed_mult = 0.5
	_check(_near(p.speed_factor(), 0.39), "and with a 0.5 brace 0.39 (%.3f)" % p.speed_factor())
	p.speed_mult = 1.0
	p.boost(1.3, 0.5, &"tail_ping")
	_check(_near(p.speed_factor(), 0.78), "the same key refreshes, never stacks with itself (%.3f)" % p.speed_factor())
	p.boost(1.2, 0.2, &"other")
	_check(_near(p.speed_factor(), 0.936), "a second key multiplies (%.3f)" % p.speed_factor())
	await _wait(18)
	_check(not p.boosts.has(&"other") and p.boosts.has(&"tail_ping"), "the 0.2 s boost has run out, the 0.5 s one is left")
	await _wait(24)
	_check(p.boosts.is_empty(), "both boosts have run out")
	p.slowed = 0.0
	p.boost(1.3, 5.0, &"tail_ping")
	p.input_override = Vector2(0.0, -1.0)
	await _wait(6)
	_check(_near(p.speed, p.move_speed * 1.3, 0.05), "walking with it: %.2f m/s against %.2f plain" % [p.speed, p.move_speed])
	p.input_override = null
	await _wait(2)
	d._respawn(p)
	_check(p.boosts.is_empty(), "a respawn clears the boosts")

	# heal (for the hummingbird)
	var heals: Array = []
	p.healed.connect(func(amt: float, _by: Node3D) -> void: heals.append(amt))
	p.hp = p.max_hp - 100.0
	var got: float = p.heal(50.0, rm)
	_check(_near(got, 50.0) and _near(p.hp, p.max_hp - 50.0), "heal(50) on a hurt machine heals 50 (%.1f)" % got)
	got = p.heal(200.0)
	_check(_near(got, 50.0) and _near(p.hp, p.max_hp), "heal past full stops at max_hp and returns what it healed (%.1f)" % got)
	_check(_near(p.heal(10.0), 0.0), "a full machine heals 0")
	_check(heals.size() == 2, "healed fires only when something was healed (%d)" % heals.size())
	p.alive = false
	_check(_near(p.heal(10.0), 0.0), "a dead machine heals 0")
	p.alive = true

	# 2 kit basic attack
	await _wait(2)
	var s := _swap_kit(p)
	await _wait(1)
	p.attack_cd = 0.0
	a.player_attack()
	_check(s.calls.size() == 1 and s.calls[0] == null, "Space goes to the kit's basic_attack, with no target (it aims at the mouse)")
	_check(_near(p.attack_cd, 0.7, 0.02), "the director keeps the kit's 0.7 s basic_cooldown (%.2f)" % p.attack_cd)
	a.player_attack()
	_check(s.calls.size() == 1, "a second press inside the cooldown does nothing")
	await _wait(45)
	a.player_attack()
	_check(s.calls.size() == 2, "after the cooldown it fires again")
	var rs := _swap_kit(rm)
	await _wait(1)
	rm.attack_cd = 0.0
	var free: bool = rm.alive and not rm.busy and rm.stunned <= 0.0
	var ok: bool = d.basic_attack(rm, p)
	_check(not free or (ok and rs.calls.size() >= 1 and rs.calls.back() == p), "a bot's basic goes to its kit with the target (free %s, fired %s)" % [free, ok])

	_check(_near(d.basic_range_of(rm), 2.0) and _near(d.basic_cooldown_of(rm), 0.7), "a kit's basic_range and basic_cooldown are what the bots and the HUD read")
	var plain: Node3D = null
	for m in d.machines:
		var mk: Node = m.get_node_or_null("Kit")
		if m != p and m != rm and not (mk != null and mk.has_method("basic_attack")):  # most kits have their own basic now
			plain = m
			break
	_check(plain == null or (_near(d.basic_range_of(plain), MatchRules.basic_range) and _near(d.basic_cooldown_of(plain), MatchRules.basic_cooldown)), "a machine without one keeps the stand-in's reach and cooldown")
	print("kit_api_check: %d failures" % fails)
	quit(1 if fails > 0 else 0)
