extends SceneTree
## Checks the fennec's blink gate, slot 2 (Claude, 2026-11-04, game feel lane; Preston: "Build blink gate", the hub's
## first slice in docs/plan/fennec-janus-kit-2026-11-04.md): the blink moves blink_range toward the aim, a gate stays at
## the start, a recast inside the window snaps back within 0.1 m, after the window the gate is gone and a recast does
## nothing, a blink at a wall stops on the near side, and the 2 key does both. Lengths are the kit's placeholders.
## Run: Godot --headless --fixed-fps 60 --path . --script res://tools/debug/blink_gate_check.gd

const SCENE := preload("res://scenes/moba3d/arena_play.tscn")
var DIRS := [Vector3.FORWARD, Vector3.BACK, Vector3.LEFT, Vector3.RIGHT, Vector3(1, 0, 1).normalized(),
	Vector3(-1, 0, 1).normalized(), Vector3(1, 0, -1).normalized(), Vector3(-1, 0, -1).normalized()]

var fails := 0
var top: Node3D


func _initialize() -> void:
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	print(("PASS " if ok else "FAIL ") + what)
	if not ok:
		fails += 1


func _wait(n: int) -> void:
	for i in n:
		await process_frame


func _flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


## Gates standing in the scene (not already on their way out). Since 2026-11-05 the marker is a SmallGate, which plays
## its close before it frees itself, so a closing gate counts as gone.
func _gates() -> int:
	var n := 0
	for g in top.find_children("BlinkGate*", "", true, false):
		if not g.is_queued_for_deletion() and g.get("phase") != "close":
			n += 1
	return n


## How far a wall is from p along dir (40 m looked at), or INF.
func _wall(player: Node3D, p: Vector3, dir: Vector3) -> float:
	var h := ArenaMotion.ray(player, p + Vector3.UP, p + Vector3.UP + dir * 40.0)
	return INF if h.is_empty() else _flat(h.position - p).length()


func _key(code: Key, down: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = code
	ev.keycode = code
	ev.pressed = down
	root.push_input(ev)


func _run() -> void:
	top = SCENE.instantiate()
	top.sandbox = true  # the test field, not the match
	root.add_child(top)
	await _wait(4)
	for g in ["kit_target", "kit_ally"]:  # nothing standing in the way
		for d in top.get_tree().get_nodes_in_group(g):
			d.remove_from_group(g)
			d.queue_free()
	top.swap()
	top.swap()
	await _wait(2)
	var player = top.player
	var kit = player.get_node("Kit")
	_check(kit is FennecKit, "Tab twice reaches the fennec")
	var c := Vector3.ZERO
	player.global_position = c
	await _wait(2)
	var open := Vector3.ZERO
	for dir in DIRS:
		if _wall(player, c, dir) > kit.blink_range + 2.0:
			open = dir
			break
	_check(open != Vector3.ZERO, "open floor from the plaza's middle along %s" % open)

	# Blink, then snap back inside the window.
	_check(kit.blink_gate(c + open * 10.0), "blink gate starts")
	var moved := _flat(player.global_position - c).length()
	_check(absf(moved - kit.blink_range) < 0.05,
		"it blinks %.2f m toward the aim (blink_range %.1f m, placeholder)" % [moved, kit.blink_range])
	_check(kit.gate_open and _gates() == 1 and is_instance_valid(kit._gate) and _flat(kit._gate.global_position - c).length() < 0.05,
		"a gate stands where it started")
	await _wait(60)
	_check(kit.gate_open and kit.gate_back(), "1 s into the %.1f s window, the recast snaps back" % kit.gate_window)
	var off := _flat(player.global_position - c).length()
	_check(off <= 0.1, "it is back at the start, %.3f m off (allowed 0.1)" % off)
	await _wait(2)
	_check(not kit.gate_open and _gates() == 0, "the gate is gone after the snap back")

	# Let the window run out.
	player.global_position = c
	kit.blink_gate(c + open * 10.0)
	var landed: Vector3 = player.global_position
	await _wait(int(kit.gate_window * 60.0) + 10)
	_check(not kit.gate_open and _gates() == 0, "after the %.1f s window the gate is gone" % kit.gate_window)
	_check(not kit.gate_back() and _flat(player.global_position - landed).length() < 0.01,
		"a recast after the window does nothing")

	# At a wall it stops on the near side.
	player.global_position = c
	var u := Vector3.ZERO
	var wall_d := 0.0
	for dir in DIRS:
		var w := _wall(player, c, dir)
		if w >= 5.0 and w < 40.0:
			u = dir
			wall_d = w
			break
	_check(wall_d > 0.0, "found a wall %.2f m from the plaza's middle along %s" % [wall_d, u])
	if wall_d > 0.0:
		var start := c + u * (wall_d - 2.0)
		player.global_position = start
		kit.blink_gate(start + u * 10.0)
		var to: Vector3 = player.global_position
		var along := _flat(to - start).dot(u)
		_check(along > 0.5 and along < 2.0 and ArenaMotion.ray(player, start + Vector3.UP, to + Vector3.UP).is_empty()
			and not ArenaMotion.blocked(player, to, player.body_radius()),
			"blinked at a wall 2 m ahead, it stops %.2f m along, on the near side" % along)
		kit.gate_back()
		await _wait(2)

	# The 2 key: once to blink, again to snap back.
	player.global_position = c
	player.facing = open
	await _wait(2)
	_key(KEY_2, true)
	_key(KEY_2, false)
	await _wait(2)
	var keyed := _flat(player.global_position - c).length()
	_check(kit.gate_open and absf(keyed - kit.blink_range) < 0.05, "pressing 2 blinks %.2f m ahead" % keyed)
	await _wait(30)
	_key(KEY_2, true)
	_key(KEY_2, false)
	await _wait(2)
	_check(not kit.gate_open and _flat(player.global_position - c).length() <= 0.1, "pressing 2 again snaps back")

	print("blink_gate_check: %d fail" % fails)
	quit()
