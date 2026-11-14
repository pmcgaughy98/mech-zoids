extends SceneTree
## Falcon basic attack check (falcon mech session, 2026-11-05). Opens the field, makes the player the falcon, and
## measures the feather dart itself on stand-in targets that record every hit they take:
##   1 install: the kit, the approved stills as idle_ frames, size class M, the hook's numbers.
##   2 keen eye: damage 26 point blank, 39 at full range, capped there.
##   3 a bot's dart, near (2 m) and far (6.9 m): the hit lands, the far one hits harder and gives the keen cue and shake.
##   4 a bot's target past range and slack: no shot.
##   5 the player's dart along a line with two targets: only the nearer is hit.
##   6 the player's dart at nothing: a miss, still fired.
##   7 basic_attack(null) (Space): fires along the aim or facing.
## The field's own dummies leave the kit_target group first, so only the stand-ins can be hit.
## Run: godot --headless --fixed-fps 60 --path . --script res://tools/debug/falcon_basic_check.gd
const KIT := preload("res://scripts/moba3d/falcon_kit.gd")
var fails := 0
var darts: Array = [] ## [target, damage] per landed dart
var cues: Array = []
var impacts: Array = []
var foe := "" ## the stand-ins' team: the player's opponents in a match, "" outside one


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


## A stand-in enemy that records its hits. In a running match it is a red or blue minion-like match unit (the kit asks
## MatchTeams for enemies, which in a match means match units of the other team); outside one, a kit_target.
func _stub(pos: Vector3) -> Node3D:
	var gs := GDScript.new()
	gs.source_code = "extends Node3D\nvar alive := true\nvar team := \"\"\nvar kind := \"minion\"\nvar hp := 600.0\nvar max_hp := 600.0\nvar path_index := 0\nvar hits: Array = []\nfunc radius() -> float:\n\treturn 0.5\nfunc hit(by, scale := 1.0) -> void:\n\thits.append(scale)\nfunc take_damage(amount, by = null) -> void:\n\tpass\n"
	gs.reload()
	var s := Node3D.new()
	s.set_script(gs)
	current_scene.add_child(s)
	s.global_position = pos
	s.set("team", foe)
	s.add_to_group("kit_target")
	if foe != "":
		s.add_to_group("match_unit")
	return s


func _off(s: Node3D) -> void: ## a stand-in leaves every group the kit looks in
	s.remove_from_group("kit_target")
	s.remove_from_group("match_unit")


func _land(n: int) -> void: ## waits until n darts in all have landed (2 s at most)
	for i in 120:
		if darts.size() >= n:
			return
		await process_frame


func _clear(d: Vector3, player: Node3D) -> float: ## open floor from the player along d, at chest height
	var p := player.global_position
	var hit := ArenaMotion.ray(player, Vector3(p.x, 1.0, p.z), Vector3(p.x, 1.0, p.z) + d * 12.0)
	return 12.0 if hit.is_empty() else KIT.flat((hit["position"] as Vector3) - p).length()


func _run() -> void:
	await _wait(10)
	var player: Node3D = current_scene.get("player")
	if player == null:
		player = current_scene.find_child("Player", true, false)
	for d in get_nodes_in_group("kit_target"):
		d.remove_from_group("kit_target")
	var kit: Node = KIT.install(player)
	await _wait(3)
	var mine := MatchTeams.team_of(player)
	foe = "" if mine == "" else ("red" if mine == "blue" else "blue")
	print("player team '%s', stand-ins '%s'" % [mine, foe])
	kit.darted.connect(func(t: Node3D, dmg: float) -> void: darts.append([t, dmg]))
	kit.cue.connect(func(c: String) -> void: cues.append(c))
	kit.impact.connect(func(s: float) -> void: impacts.append(s))
	var spr: DirectionalSprite3D = player.get_node("Sprite")

	# 1 install
	_check(player.get_node_or_null("Kit") == kit, "the falcon kit is the player's Kit")
	_check(spr.sprite_frames.has_animation(&"idle_s") and spr.sprite_frames.has_animation(&"walk_n"), "idle and walk frames from the stills")
	_check(spr.size_class == "M", "size class M (got %s)" % spr.size_class)
	_check(kit.has_method("basic_attack") and kit.basic_range == 7.0 and kit.basic_cooldown == 0.9, "basic_attack, range 7, cooldown 0.9")

	# 2 keen eye
	_check(is_equal_approx(kit.dart_damage(0.0), 26.0) and is_equal_approx(kit.dart_damage(7.0), 39.0)
		and is_equal_approx(kit.dart_damage(20.0), 39.0), "keen eye: 26 point blank, 39 at range, capped (got %.1f, %.1f, %.1f)"
		% [kit.dart_damage(0.0), kit.dart_damage(7.0), kit.dart_damage(20.0)])

	# the most open flat direction from the player, so a wall cannot spoil the line tests
	var dirs := [Vector3.RIGHT, Vector3.LEFT, Vector3.FORWARD, Vector3.BACK]
	var dir: Vector3 = dirs[0]
	for d in dirs:
		if _clear(d, player) > _clear(dir, player):
			dir = d
	print("open floor along %s: %.1f m" % [dir, _clear(dir, player)])
	var o := player.global_position

	# 3 bot darts, near and far
	var near_t := _stub(o + dir * 2.5)
	_check(kit.basic_attack(near_t), "bot dart at 2 m fires")
	await _land(1)
	var far_t := _stub(o + dir * 7.4)
	_off(near_t)
	cues.clear()
	_check(kit.basic_attack(far_t), "bot dart at 6.9 m fires")
	await _land(2)
	var dn: float = near_t.hits[0] * MatchRules.kit_hit_damage if near_t.hits.size() == 1 else -1.0
	var df: float = far_t.hits[0] * MatchRules.kit_hit_damage if far_t.hits.size() == 1 else -1.0
	_check(absf(dn - 29.71) < 0.1, "near hit does 29.7 (measured on the target: %.2f)" % dn)
	_check(absf(df - 38.81) < 0.1, "far hit does 38.8 (measured on the target: %.2f)" % df)
	_check(dn > 0.0 and df / dn > 1.2, "far over near %.2f, keen eye shows" % (df / dn if dn > 0.0 else 0.0))
	_check("dart_keen" in cues and impacts == [0.15], "full-range hit: keen cue and one small shake (cues %s, shakes %s)" % [cues, impacts])

	# 4 past range and slack
	var away := _stub(o + dir * 9.0)
	_check(not kit.basic_attack(away), "bot target at 8.5 m: no shot")
	_off(away)
	away.queue_free()
	_off(far_t)

	# 5 the player's line: two targets, only the nearer is hit
	var a := _stub(o + dir * 3.0)
	var b := _stub(o + dir * 6.0)
	_check(kit.fire_dir(dir), "player dart along the line fires")
	await _land(3)
	await _wait(30)  # time for a wrong second hit to show
	_check(a.hits.size() == 1 and b.hits.is_empty(), "only the nearer target is hit (near %d, far %d)" % [a.hits.size(), b.hits.size()])
	_off(a)
	_off(b)

	# 6 a miss
	cues.clear()
	_check(kit.fire_dir(dir), "player dart at nothing still fires")
	await _land(4)
	_check(darts[3][0] == null and "dart_miss" in cues, "and lands as a miss")

	# 7 Space: target null
	_check(kit.basic_attack(null), "basic_attack(null) fires along aim or facing")
	await _land(5)

	print("falcon_basic_check: %d failures" % fails)
	quit(fails)
