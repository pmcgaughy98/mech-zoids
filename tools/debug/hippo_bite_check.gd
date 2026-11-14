extends SceneTree
## The hippo's melee bite (hippo session, 2026-11-05; Preston: "Melee bite"). Opens the match, puts the hippo kit on
## the player and measures real bites on a red minion through the director's own basic_attack:
##   frames and size, the reach and cooldown the director reads, a hit's damage, the cooldown, busy released,
##   out of reach refused, a whiff, and the walk rate that keeps the feet planted.
## Run: godot --headless --fixed-fps 60 --path . --script res://tools/debug/hippo_bite_check.gd
const HK := preload("res://scripts/moba3d/hippo_kit.gd") ## by path: a new class_name waits on the class cache
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


## Watches the minion for 16 frames after a bite: true once a hit by the hippo at the bite's scale takes the bite's
## damage. Other units also hit it (blue bots near spawn: on 2026-11-05 the blue fennec's 30-damage basic, scale 0.5,
## landed in the same window in 2 runs of 4), so any other hit is printed as INFO and does not count.
func _snap(mn: Node, p: Node, kit: Node) -> bool:
	mn.last_hit_by = null
	var hp0: float = mn.hp
	var seen := false
	for f in 16:
		await process_frame
		if is_equal_approx(mn.hp, hp0):
			continue
		var drop: float = hp0 - mn.hp
		var by_hippo: bool = mn.last_hit_by == p and _near(mn.last_hit_scale, kit.bite_damage / MatchRules.kit_hit_damage, 0.001)
		if by_hippo and _near(drop, kit.bite_damage, 0.5):
			seen = true
		else:
			print("INFO frame %d: another hit, hp -%.1f by %s at %.3f" % [f + 1, drop, mn.last_hit_by.name if is_instance_valid(mn.last_hit_by) else "-", mn.last_hit_scale])
		hp0 = mn.hp
	return seen


func _run() -> void:
	await _wait(60)
	var a = current_scene
	var d = a.director
	var p = a.player
	var kit = HK.install(p)
	await _wait(2)
	for c in p.get_children():  # diagnostic: anything kit-like left from the arena's rhino
		var sc = c.get_script()
		if sc != null and str(sc.resource_path).ends_with("_kit.gd"):
			print("INFO player child %s: %s" % [c.name, sc.resource_path])
	var spr = p.get_node("Sprite")
	_check(spr.sprite_frames == HK.HIPPO_FRAMES and spr.size_class == "L", "the player wears the hippo frames at size L")
	_check(spr.sprite_frames.has_animation("walk_s") and spr.sprite_frames.has_animation("idle_n"), "idle and walk are in the frames")
	_check(_near(d.basic_range_of(p), kit.basic_range) and _near(d.basic_cooldown_of(p), kit.basic_cooldown),
		"the director reads the bite's reach %.1f and cooldown %.1f" % [d.basic_range_of(p), d.basic_cooldown_of(p)])
	_check(_near(p.full_speed_walk_rate, p.move_speed / HK.STRIDE, 0.001),
		"walk rate %.2f = move speed %.2f / %.2f, so the feet stay planted" % [p.full_speed_walk_rate, p.move_speed, HK.STRIDE])

	# a hit, bot style (target given)
	var dir: Vector3 = HK.flat(p.facing).normalized()
	var mn = d.spawn_minion("red", p.global_position + dir * 1.6)
	await _wait(2)
	mn.global_position = p.global_position + dir * 1.6
	p.attack_cd = 0.0
	var h0: float = mn.hp
	var reach: float = MatchTeams.edge_distance(p, mn)
	var ok: bool = d.basic_attack(p, mn)
	_check(ok, "a bite on a minion %.2f m away fires" % reach)
	_check(_near(p.attack_cd, kit.basic_cooldown, 0.02), "the director starts the %.1f s cooldown (%.2f)" % [kit.basic_cooldown, p.attack_cd])
	_check(p.busy, "the hippo is busy during the wind-up")
	var bit: bool = await _snap(mn, p, kit)
	_check(bit, "the bite takes %.0f, from the hippo at scale %.3f" % [kit.bite_damage, kit.bite_damage / MatchRules.kit_hit_damage])
	_check(not p.busy and not kit.biting, "busy is released after the bite")

	# the player's key (target null) bites what is in front
	var aim: Vector3 = p.aim_dir()
	if aim.length() < 0.01:
		aim = HK.flat(p.facing).normalized()
	mn.global_position = p.global_position + aim * 1.6
	p.attack_cd = 0.0
	h0 = mn.hp
	ok = d.basic_attack(p, null)
	bit = await _snap(mn, p, kit)
	_check(ok and bit, "Space bites the minion in the aim for %.0f" % kit.bite_damage)

	# out of reach
	mn.global_position = p.global_position + aim * 6.0
	p.attack_cd = 0.0
	h0 = mn.hp
	ok = d.basic_attack(p, mn)
	await _wait(20)
	_check(not ok and _near(h0, mn.hp), "a bot's bite at %.1f m is refused and does nothing" % MatchTeams.edge_distance(p, mn))

	# a whiff: nothing in reach, the key still answers
	p.attack_cd = 0.0
	ok = d.basic_attack(p, null)
	_check(ok and _near(p.attack_cd, kit.basic_cooldown, 0.02), "Space with nothing in reach snaps the air and the cooldown runs")
	await _wait(20)
	_check(_near(h0, mn.hp, 0.01) and not p.busy, "the whiff hurts nothing and frees the hippo")

	mn.queue_free()
	print("hippo_bite_check: %d failure(s)" % fails)
	quit(1 if fails > 0 else 0)
