extends SceneTree
## Plays the one-lane MOBA arena headless at its fixed step and checks the first slice: waves leave both cores and
## meet near the middle of the lane; with one side's waves switched off, the other side takes the tower, then the
## core, and the match ends with a winner.
## Run: Godot --headless --path . --script res://tools/debug/moba_check.gd

const ARENA := preload("res://scenes/moba/arena.tscn")

var fails := 0


func _initialize() -> void:
	# The root only joins the tree after _initialize returns, so an arena added now would never get _ready.
	_run.call_deferred()


func _run() -> void:
	print("moba_check: both sides send waves, 300 seconds")
	var arena := _arena()
	var seen := {}
	arena.unit_attacked.connect(func(target: Node2D, attacker: Node2D, amount: int) -> void:
		if not seen.has("clash") and target.kind == "lane" and attacker.kind == "lane":
			seen.clash = target.global_position
			seen.clash_at = arena.elapsed
		if target.kind != "lane":
			var key: String = target.team + " " + target.kind
			seen[key] = seen.get(key, 0) + amount)
	_play(arena, 300.0)
	var lane: PackedVector2Array = arena.lanes.mid
	var middle := (lane[0].x + lane[-1].x) / 2.0
	var length := absf(lane[-1].x - lane[0].x)
	var sent: Dictionary = arena.spawner.waves_sent
	_ok("both cores sent a wave every 30 seconds (blue %d, red %d)" % [sent.blue, sent.red],
		sent.blue == 10 and sent.red == 10)
	_ok("the first waves met near the middle of the lane (x %d at %.1fs, middle %d)"
		% [seen.get("clash", Vector2.INF).x, seen.get("clash_at", -1.0), middle],
		seen.has("clash") and absf(seen.clash.x - middle) <= length * 0.15)
	_ok("live units stay bounded (%d at the end)" % arena.units.size(), arena.units.size() < 40)
	print("  damage taken by buildings: %s; winner: %s" % [_buildings(seen), arena.winner if arena.winner else "none"])
	root.remove_child(arena)
	arena.free()

	print("\nmoba_check: only blue sends waves, up to 600 seconds")
	var push := _arena()
	push.spawner.teams = PackedStringArray(["blue"])
	var events := {}
	push.unit_attacked.connect(func(target: Node2D, _attacker: Node2D, _amount: int) -> void:
		if target.kind == "tower" and not events.has("tower_hit_at"):
			events.tower_hit_at = push.elapsed
		if target.kind == "core" and not events.has("core_hit_at"):
			events.core_hit_at = push.elapsed)
	push.unit_died.connect(func(unit: Node2D) -> void:
		if unit.kind == "tower":
			events.tower_down_at = push.elapsed)
	_play(push, 600.0)
	_ok("red's tower took damage (first hit at %.1fs)" % events.get("tower_hit_at", -1.0), events.has("tower_hit_at"))
	_ok("red's tower fell (at %.1fs)" % events.get("tower_down_at", -1.0), events.has("tower_down_at"))
	_ok("red's core took no damage while its tower stood (first hit at %.1fs)" % events.get("core_hit_at", -1.0),
		events.has("core_hit_at") and events.has("tower_down_at") and events.core_hit_at >= events.tower_down_at)
	_ok("the match ended with blue the winner (at %.1fs)" % push.elapsed, push.winner == "blue")
	print("\nmoba_check: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
	quit(1 if fails > 0 else 0)


func _arena() -> Node2D:
	var arena: Node2D = ARENA.instantiate()
	arena.run_on_its_own = false
	root.add_child(arena)
	return arena


## Advances the arena a second at a time until the time runs out or the match ends.
func _play(arena: Node2D, seconds: float) -> void:
	while arena.elapsed < seconds and arena.winner == "":
		arena.advance(1.0)


func _buildings(seen: Dictionary) -> String:
	var parts := []
	for key in ["blue tower", "blue core", "red tower", "red core"]:
		parts.append("%s %d" % [key, seen.get(key, 0)])
	return ", ".join(parts)


func _ok(label: String, passed: bool) -> void:
	print("  %s %s" % ["ok  " if passed else "FAIL", label])
	if not passed:
		fails += 1
