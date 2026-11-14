extends SceneTree
## Rhino basic attack check (Rhino session, 2026-11-05; Preston: "we need basic attacks. Rhino, gorilla will be melee").
## Headless:
##   "<godot>" --headless --fixed-fps 60 --path . --script res://tools/debug/rhino_basic_check.gd
## Opens arena_play (the player's machine is the rhino) and jabs the first camp monster through the director's hook,
## the way the bots and the Space key do: in reach with a target, at the air with no target, and out of reach.

var passed := 0
var failed := 0


func ok(cond: bool, what: String) -> void:
	if cond:
		passed += 1
		print("PASS ", what)
	else:
		failed += 1
		print("FAIL ", what)


func frames(n: int) -> void:
	for i in n:
		await physics_frame


func secs(t: float) -> void:
	await frames(int(t * 60.0))


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var play: Node = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	await frames(2)
	var d: MatchDirector = play.director
	var player: Node3D = play.player
	var waited := 0
	while not d.ready_to_play and waited < 300:
		await physics_frame
		waited += 1
	var kit = player.get_node_or_null("Kit")
	ok(kit is RhinoKit, "the player's machine is the rhino")
	if not (kit is RhinoKit):
		_finish()
		return
	ok(is_equal_approx(d.basic_range_of(player), kit.basic_range), "the director reads the rhino's reach (%.1f m)" % d.basic_range_of(player))
	ok(is_equal_approx(d.basic_cooldown_of(player), kit.basic_cooldown), "and its cooldown (%.2f s)" % d.basic_cooldown_of(player))

	var mon: MatchMonster = d.camps[0]["monster"]
	var home: Vector3 = d.camps[0]["home"]
	var r: float = mon.radius()

	# A: a bot's swing, target given, 1.5 m edge to edge.
	mon.global_position = home
	player.global_position = home + Vector3(r + 1.5, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	var before: float = mon.hp
	var fired := d.basic_attack(player, mon)
	ok(fired, "in reach (%.2f m edge to edge), the jab fires" % MatchTeams.edge_distance(player, mon))
	ok(is_equal_approx(player.attack_cd, kit.basic_cooldown), "the director starts the cooldown")
	ok(player.busy and kit.current == "horn_jab", "the rhino is busy with horn_jab while it swings")
	ok(player.facing.dot(MatchTeams.flat(mon.global_position - player.global_position).normalized()) > 0.95, "it turns to face the target")
	await secs(0.35)
	ok(mon.hp <= before - kit.basic_damage + 0.1, "the jab hits for %.0f (basic_damage %.0f)" % [before - mon.hp, kit.basic_damage])
	await secs(0.3)
	ok(not player.busy and kit.current == "", "busy is released after the swing (0.45 s at 2x)")

	# B: the player's Space with no target and nothing in reach: a swing at the air, no damage.
	mon.global_position = home
	player.global_position = home + Vector3(r + 4.0, 0, 0)
	player.facing = Vector3(-1, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	before = mon.hp
	ok(d.basic_attack(player, null), "no target: the jab still swings (the key always answers)")
	await secs(0.7)
	ok(is_equal_approx(mon.hp, before), "nothing in reach takes damage (%.0f)" % (before - mon.hp))

	# D: the player's Space with no target, aimed away (headless, the mouse sits at the screen corner), the monster in
	# reach behind: the assist turns the jab onto it.
	mon.global_position = home
	player.global_position = home + Vector3(r + 1.5, 0, 0)
	player.facing = Vector3(1, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	before = mon.hp
	ok(d.basic_attack(player, null), "no target, aimed away, a monster in reach: the jab fires")
	print("  D: hittable %s, edge %.2f m, facing to monster %.2f, aim_dir %s" % [MatchTeams.hittable(mon),
		MatchTeams.edge_distance(player, mon), player.facing.dot(MatchTeams.flat(mon.global_position - player.global_position).normalized()),
		player.aim_dir()])
	await secs(0.35)
	ok(mon.hp <= before - kit.basic_damage + 0.1, "the assist turns it onto the monster for %.0f" % (before - mon.hp))
	await secs(0.4)

	# C: a target given out of reach is refused, and no cooldown starts.
	mon.global_position = home
	player.global_position = home + Vector3(r + 4.0, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	ok(not d.basic_attack(player, mon), "a target 4 m away is refused")
	ok(player.attack_cd == 0.0, "and no cooldown starts")
	_finish()


func _finish() -> void:
	print("rhino_basic_check: %d pass, %d fail" % [passed, failed])
	quit(1 if failed > 0 else 0)
