extends SceneTree
## Lobster basic attack check (Claude, lobster session, 2026-11-06; Preston: "Melee claw snap").
## Headless:
##   "<godot>" --headless --fixed-fps 60 --path . --script res://tools/debug/lobster_basic_check.gd
## Opens arena_play, makes the player's machine the lobster (the kit loaded by path), and snaps at the first camp
## monster through the director's hook, the way the bots and the Space key do: in reach with a target, at the air with
## no target, aimed away with the monster in reach (the assist), and out of reach. Pattern: rhino_basic_check.gd.

const KIT := "res://scripts/moba3d/lobster_kit.gd"

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
	var kit = load(KIT).install(player)  # untyped: its fields are read by name
	await frames(2)
	ok(player.get_node_or_null("Kit") == kit and kit.has_method("basic_attack"), "the player's machine is the lobster, with a basic_attack")
	ok(is_equal_approx(d.basic_range_of(player), kit.basic_range), "the director reads the lobster's reach (%.1f m)" % d.basic_range_of(player))
	ok(is_equal_approx(d.basic_cooldown_of(player), kit.basic_cooldown), "and its cooldown (%.2f s)" % d.basic_cooldown_of(player))

	var mon: MatchMonster = d.camps[0]["monster"]
	var home: Vector3 = d.camps[0]["home"]
	var r: float = mon.radius()
	var snaps := []
	kit.cue.connect(func(n): snaps.append(n))

	# A: a bot's snap, target given, 1.5 m edge to edge.
	mon.global_position = home
	player.global_position = home + Vector3(r + 1.5, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	var before: float = mon.hp
	ok(d.basic_attack(player, mon), "in reach (%.2f m edge to edge), the snap fires" % MatchTeams.edge_distance(player, mon))
	ok(is_equal_approx(player.attack_cd, kit.basic_cooldown), "the director starts the cooldown (%.2f s)" % player.attack_cd)
	ok(player.busy and kit.swinging, "the lobster is busy while it snaps")
	ok(player.facing.dot(MatchTeams.flat(mon.global_position - player.global_position).normalized()) > 0.95, "it turns to face the target")
	await secs(0.3)
	var dealt := before - mon.hp
	ok(dealt > 0.0, "the snap hits (%.1f hp off the monster; 40 damage before plating)" % dealt)
	ok(not player.busy and not kit.swinging, "busy is released right after the snap (windup 0.1 + hold 0.05)")
	ok(snaps.has("basic_snap"), "it sends the basic_snap cue for the sound lane")

	# B: Space with no target and nothing in reach: a snap at the air, no damage, the whiff cue.
	mon.global_position = home
	player.global_position = home + Vector3(r + 4.0, 0, 0)
	player.facing = Vector3(-1, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	before = mon.hp
	ok(d.basic_attack(player, null), "no target: the snap still swings (the key always answers)")
	await secs(0.3)
	ok(is_equal_approx(mon.hp, before), "nothing in reach takes damage (%.1f)" % (before - mon.hp))
	ok(snaps.has("basic_whiff"), "and it sends the basic_whiff cue")

	# D: Space with no target, aimed away, the monster in reach behind: the assist turns the snap onto it.
	mon.global_position = home
	player.global_position = home + Vector3(r + 1.5, 0, 0)
	player.facing = Vector3(1, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	before = mon.hp
	ok(d.basic_attack(player, null), "no target, aimed away, a monster in reach: the snap fires")
	await secs(0.3)
	ok(mon.hp < before, "the assist turns it onto the monster (%.1f hp off)" % (before - mon.hp))

	# C: a target given out of reach is refused, and no cooldown starts.
	mon.global_position = home
	player.global_position = home + Vector3(r + 4.0, 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	ok(not d.basic_attack(player, mon), "a target 4 m away is refused")
	ok(player.attack_cd == 0.0, "and no cooldown starts")
	_finish()


func _finish() -> void:
	print("lobster_basic_check: %d pass, %d fail" % [passed, failed])
	quit(1 if failed > 0 else 0)
