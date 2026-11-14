extends SceneTree
## Checks the fennec's kit in the arena (Claude, 2026-11-04, game feel lane; Preston: "approve fennec kit build"):
## Tab reaches it, its frames and size class, the passive's pings, each ability's reach and its timing against the
## drawn key frames (animation lane: sand f3 0.52 s, burst f3 0.49 s, dig gone f5 0.71 s, blast f4 0.94 s), the
## tunnel carrying allies and stopping at a wall, and Tab back to the rhino. Lengths are the kit's placeholders.
## Run: Godot --headless --fixed-fps 60 --path . --script res://tools/debug/fennec3d_check.gd

const SCENE := preload("res://scenes/moba3d/arena_play.tscn")
const ANIMS := ["walk_s", "walk_se", "walk_e", "walk_ne", "walk_n", "idle_s", "idle_se", "idle_e", "idle_ne", "idle_n"]
const VIEWS := ["s", "se", "e", "ne", "n"]
const MOVES := ["sand_kick", "ear_burst", "sonic_boom", "dig", "pop_out", "death"]

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


func _wait_kit(kit) -> void:
	for i in 900:
		if kit.get("current") == "":
			return
		await process_frame


## Seconds from now until the kit records `key` in its last dictionary, or -1.
func _until(kit, key: String) -> float:
	for i in 600:
		if kit.last.has(key):
			return i / 60.0
		await process_frame
	return -1.0


func _flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _dummy(p: Vector3, ally := false) -> Node3D:
	var d := TrainingDummy.new()
	top.add_child(d)
	d.global_position = p
	if ally:
		ApeKit.make_ally(d)
	return d


func _clear() -> void:
	for g in ["kit_target", "kit_ally"]:
		for d in top.get_tree().get_nodes_in_group(g):
			d.remove_from_group(g)
			d.queue_free()


func _run() -> void:
	top = SCENE.instantiate()
	top.sandbox = true  # the test field with dummies, not the match
	root.add_child(top)
	await _wait(4)
	_clear()
	await _wait(2)
	var player = top.player
	var sprite: DirectionalSprite3D = player.get_node("Sprite")
	var rhino_speed: float = player.move_speed
	var rhino_stride: float = player.stride_speed
	var rhino_rate: float = player.full_speed_walk_rate
	top.swap()
	top.swap()
	await _wait(2)
	var kit := player.get_node("Kit") as FennecKit
	_check(kit != null and top.machine == "fennec" and sprite.sprite_frames == FennecKit.FENNEC_FRAMES,
		"Tab twice goes rhino, gorilla, fennec")
	if kit == null:
		print("fennec3d_check: %d failures" % fails)
		quit(1)
		return
	_check(sprite.size_class == "S" and sprite.canvas_height == 192 and sprite.feet_edge_row == 161
		and is_equal_approx(sprite.size_scale(), 0.8), "size S on its 192 canvas, feet on row 160: %.2f of the rhino's canvas"
		% sprite.size_scale())
	_check(is_equal_approx(sprite.position.y, (161 - 96) * 0.016), "the feet stand on the ground (sprite raised %.3f m)"
		% sprite.position.y)
	var missing := []
	for a in ANIMS:
		if not sprite.sprite_frames.has_animation(a):
			missing.append(a)
	for m in MOVES:
		for v in VIEWS:
			if not sprite.sprite_frames.has_animation(m + "_" + v):
				missing.append(m + "_" + v)
	for v in VIEWS:  # the 35-degree cast for the portal kit (animation lane, 2026-11-05: 40 -> 45 animations)
		if not sprite.sprite_frames.has_animation("cast_" + v):
			missing.append("cast_" + v)
	_check(missing.is_empty(), "every listed animation is in the sheet (%d in all), every move in all five views %s"
		% [sprite.sprite_frames.get_animation_names().size(), missing])
	# Turned to a diagonal, each move plays its own se or ne drawing (the own-view rule), not the side view.
	for v in ["se", "ne"]:
		for i in 16:
			player.facing = Vector3(sin(i * TAU / 16), 0, cos(i * TAU / 16))
			await _wait(1)
			if sprite.view == v:
				break
		var wrong := []
		for m in MOVES:
			sprite.play_action(m)
			await _wait(1)
			if sprite.view != v or sprite.animation != StringName(m + "_" + v):
				wrong.append("%s shows %s" % [m, sprite.animation])
			sprite.stop_action()
		_check(wrong.is_empty(), "facing the %s view, every move plays its own %s frames %s" % [v, v, wrong])
	await _wait(1)
	_check(player.move_speed == kit.walk_speed and player.stride_speed == FennecKit.STRIDE
		and is_equal_approx(player.full_speed_walk_rate, kit.walk_speed / FennecKit.STRIDE),
		"walks at the kit's %.2f m/s (placeholder; Preston: faster), the trot played %.2fx to match its %.2f planted pace"
		% [player.move_speed, player.full_speed_walk_rate, FennecKit.STRIDE])
	player.move_override = Vector3.RIGHT
	await _wait(10)
	var fps: float = sprite.sprite_frames.get_animation_speed(sprite.animation) * sprite.speed_scale
	_check(absf(player.foot_slide() - 1.0) < 0.02 and String(sprite.animation).begins_with("walk_"),
		"walking flat out the feet stay planted: slide %.2f, trot at %.1f fps" % [player.foot_slide(), fps])
	player.move_override = null
	await _wait(2)
	_check(is_equal_approx(player.body_radius(), player.body_radius_l * 0.8), "its body radius at walls is %.2f m (S)"
		% player.body_radius())
	var c := Vector3.ZERO
	player.global_position = c
	player.facing = Vector3.FORWARD
	await _wait(2)

	# Passive, big ears.
	var near := _dummy(c + Vector3(4, 0, 2))
	var still := _dummy(c + Vector3(-3, 0, 1))
	var far := _dummy(c + Vector3(11, 0, 0))
	near.walk_to(c + Vector3(5, 0, -2), 1.5)
	far.walk_to(c + Vector3(11, 0, -3), 1.5)
	await _wait(100)
	_check(kit.heard.get(near, 0) >= 2, "an enemy walking 4-5 m away pings: %d pings in 1.5 s (one every %.1f s)"
		% [kit.heard.get(near, 0), kit.ping_every])
	_check(kit.heard.get(still, 0) == 0, "an enemy standing still makes no ping")
	_check(kit.heard.get(far, 0) == 0, "an enemy walking 11 m away is out of hearing (%.0f m)" % kit.hear_radius)
	_clear()
	await _wait(2)

	# 1, sand kick.
	var in1 := _dummy(c + Vector3(0.6, 0, -2.5))
	var in2 := _dummy(c + Vector3(-0.8, 0, -1.5))
	var wide := _dummy(c + Vector3(2.5, 0, -1.0))
	var long := _dummy(c + Vector3(0, 0, -5.0))
	var behind := _dummy(c + Vector3(0, 0, 1.5))
	kit.last.clear()
	kit.sand_kick()
	var t: float = await _until(kit, "sand_kick")
	_check(absf(t - 0.52) < 0.05, "the sand leaves on sand_kick f3: %.2f s (drawn 0.52)" % t)
	var hit: Array = kit.last.get("sand_kick", [])
	_check(in1 in hit and in2 in hit and in1.slowed > 0.0 and in2.slowed > 0.0,
		"enemies in the cone ahead are hit and slowed (%.1f s, placeholder)" % kit.kick_slow)
	_check(not (wide in hit or long in hit or behind in hit) and wide.slowed == 0.0 and behind.slowed == 0.0,
		"one off to the side, one past the %.1f m reach and one behind are not" % kit.kick_range)
	await _wait_kit(kit)
	_check(not player.busy, "it is free once the kick ends")
	_clear()
	await _wait(2)

	# 2, ear burst.
	var spot := c + Vector3(-1.0, 0, -4.0)
	var core_d := _dummy(spot + Vector3(0.3, 0, 0.2))
	var edge_d := _dummy(spot + Vector3(1.4, 0, 0.0))
	var out_d := _dummy(spot + Vector3(2.8, 0, 0.0))
	kit.last.clear()
	kit.ear_burst(spot)
	t = await _until(kit, "ear_burst")
	_check(absf(t - 0.49) < 0.05, "the burst comes on ear_burst f3: %.2f s (drawn 0.49)" % t)
	var b: Dictionary = kit.last.get("ear_burst", {})
	_check(_flat(b.get("spot", Vector3.INF) - spot).length() < 0.01, "it bursts on the spot aimed at")
	_check(core_d in b.get("core", []) and edge_d in b.get("edge", []) and not (out_d in b.get("core", []) or out_d in b.get("edge", [])),
		"the one at the centre takes the harder hit, the one 1.4 m out the lighter, the one 2.8 m out none")
	await _wait_kit(kit)
	kit.last.clear()
	kit.ear_burst()
	await _until(kit, "ear_burst")
	b = kit.last.get("ear_burst", {})
	_check(_flat(b.get("spot", Vector3.INF) - core_d.global_position).length() < 0.01,
		"with no aim it bursts on the nearest enemy in reach")
	await _wait_kit(kit)
	_clear()
	await _wait(2)

	# 3, tunnel.
	player.global_position = c
	player.facing = Vector3.FORWARD
	var ally := _dummy(c + Vector3(1.5, 0, 0.5), true)
	var enemy := _dummy(c + Vector3(-1.5, 0, 0.5))
	kit.last.clear()
	kit.tunnel()
	var gone_at := -1.0
	for i in 600:
		if not sprite.visible and gone_at < 0.0:
			gone_at = i / 60.0
		if kit.current == "":
			break
		await process_frame
	_check(absf(gone_at - 0.71) < 0.05, "it is gone under the ground on dig f5: %.2f s (drawn 0.71)" % gone_at)
	var tn: Dictionary = kit.last.get("tunnel", {})
	var out: Vector3 = tn.get("out", Vector3.INF)
	_check(_flat(out - (c + Vector3.FORWARD * kit.tunnel_length)).length() < 0.05,
		"it comes up %.2f m ahead (placeholder %.0f)" % [_flat(out - c).length(), kit.tunnel_length])
	_check(sprite.visible and _flat(player.global_position - out).length() < 0.01 and not player.busy,
		"and stands at the exit, shown again and free")
	ally.walk_to(c, 0.5)
	enemy.walk_to(c, 0.5)
	await _wait(90)
	_check(ally in kit.carried and ally.visible and _flat(ally.global_position - out).length() < 1.5,
		"an ally stepping into the entrance comes up by the exit (%.2f m from it)" % _flat(ally.global_position - out).length())
	_check(not (enemy in kit.carried) and _flat(enemy.global_position - c).length() < 0.5, "an enemy stepping in stays put")
	await _wait(int(kit.tunnel_time * 60.0))
	var late := _dummy(c + Vector3(1.0, 0, 0), true)
	late.walk_to(c, 0.3)
	await _wait(60)
	_check(kit.tunnel_open <= 0.0 and not (late in kit.carried), "after %.0f s it closes: an ally stepping in then stays put"
		% kit.tunnel_time)
	_clear()
	await _wait(2)
	# Dug at a wall, it comes up on the near side (ArenaMotion).
	var u := Vector3.ZERO
	var wall_d := 0.0
	for dir in [Vector3.FORWARD, Vector3.BACK, Vector3.LEFT, Vector3.RIGHT, Vector3(1, 0, 1).normalized(),
			Vector3(-1, 0, 1).normalized(), Vector3(1, 0, -1).normalized(), Vector3(-1, 0, -1).normalized()]:
		var h := ArenaMotion.ray(player, c + Vector3.UP, c + Vector3.UP + dir * 16.0)
		if not h.is_empty():
			var dd := _flat(h.position - c).length()
			if dd >= 5.0:
				u = dir
				wall_d = dd
				break
	_check(wall_d > 0.0, "found a wall %.2f m from the plaza's middle along %s" % [wall_d, u])
	if wall_d > 0.0:
		var start := c + u * (wall_d - 3.0)
		player.global_position = start
		player.facing = u
		kit.last.clear()
		kit.tunnel()
		await _wait_kit(kit)
		out = kit.last.get("tunnel", {}).get("out", Vector3.INF)
		var along := _flat(out - start).dot(u)
		_check(along > 1.0 and along < 3.0 and ArenaMotion.ray(player, start + Vector3.UP, out + Vector3.UP).is_empty()
			and not ArenaMotion.blocked(player, out, player.body_radius()),
			"dug 8 m at a wall 3 m ahead, it comes up %.2f m along, on the near side of it" % along)
		await _wait(int(kit.tunnel_time * 60.0) + 30)

	# 4, sonic boom.
	player.global_position = c
	player.facing = Vector3.FORWARD
	var cone := [_dummy(c + Vector3(0.5, 0, -2.0)), _dummy(c + Vector3(-2.0, 0, -5.0)), _dummy(c + Vector3(3.0, 0, -6.0))]
	var spare := [_dummy(c + Vector3(4.0, 0, -1.0)), _dummy(c + Vector3(0, 0, 2.0)), _dummy(c + Vector3(0, 0, -8.5))]
	var before := []
	for d in cone + spare:
		before.append(d.global_position)
	kit.last.clear()
	kit.sonic_boom()
	t = await _until(kit, "sonic_boom")
	_check(absf(t - 0.94) < 0.05, "the blast comes on sonic_boom f4 after the f1-f3 charge: %.2f s (drawn 0.94)" % t)
	await _wait(60)
	var pushed := []
	for i in cone.size():
		pushed.append(_flat(cone[i].global_position - c).length() - _flat(before[i] - c).length())
	_check(pushed.all(func(p): return p > kit.boom_knock * 0.8), "the three in the cone are knocked back %.2f, %.2f and %.2f m (placeholder %.0f)"
		% [pushed[0], pushed[1], pushed[2], kit.boom_knock])
	var still_ok := true
	for i in spare.size():
		if spare[i].global_position.distance_to(before[cone.size() + i]) > 0.01:
			still_ok = false
	_check(still_ok, "one to the side, one behind and one past the %.0f m reach stay put" % kit.boom_range)
	await _wait_kit(kit)
	_check(not player.busy, "it is free once the boom ends")
	_clear()

	# Tab round to the rhino, as it was (the wolf and the squirrel sit between them since 2026-11-05).
	for i in 8:
		if top.machine == "rhino":
			break
		top.swap()
		await _wait(2)
	_check(top.machine == "rhino" and player.get_node("Kit") is RhinoKit and sprite.size_class == "L"
		and player.move_speed == rhino_speed and player.stride_speed == rhino_stride
		and player.full_speed_walk_rate == rhino_rate and sprite.visible,
		"Tab again: the rhino at size L, its own pace back (%.2f m/s) and stride (%.2f)" % [player.move_speed, player.stride_speed])
	print("fennec3d_check: %d failures" % fails)
	quit(1 if fails else 0)
