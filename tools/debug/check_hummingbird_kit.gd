extends SceneTree
## Headless check of the hummingbird's link slice (hummingbird mech session, 2026-11-05). It measures the kit itself:
## - the frames: idle_ and walk_ for all five views, each a 160-tall still, size S, lifted HOVER_ROWS, not tilted;
## - a needle at an ally (300 of 600) heals it by needle_heal_share and links it;
## - the link heals link_heal_share of full health a second, measured over 3 s of physics time;
## - healing stops at full health;
## - a second ally hit moves the link ("replaced"); walking the ally out past link_range breaks it ("range");
## - an enemy on the line takes one kit hit x needle_damage_scale and makes no link;
## - the needle takes the first unit on the line, ignores one 2 m off it, and hits nothing past needle_range;
## - the beak shot (basic attack) goes to the mouse aim for 30, turns the machine, refuses an enemy out of reach, one
##   outside the aim cone and any ally; a bot's target is shot in reach and refused out of it.
## Not checked here: a wall cutting the line (the field has no wall to place on demand).
## Run: Godot --headless --path . --script res://tools/debug/check_hummingbird_kit.gd

const KIT := preload("res://scripts/moba3d/hummingbird_kit.gd")
const ALLY := preload("res://scripts/moba3d/hummingbird_ally_dummy.gd")

var fails := 0
var field: Node3D
var player: Node3D
var kit: KIT
var unlinks := []


func _initialize() -> void:
	_run()


func _check(ok: bool, what: String) -> void:
	print(("PASS  " if ok else "FAIL  ") + what)
	if not ok:
		fails += 1


func _clear() -> void:
	kit.link_target = null
	for g in ["kit_target", "kit_ally"]:
		for d in get_nodes_in_group(g):
			if d != player:
				d.get_parent().remove_child(d)
				d.free()


func _ally(at: Vector3, hp := 300.0) -> Node3D:
	var a: Node3D = ALLY.new()
	field.add_child(a)
	a.global_position = at
	a.hp = hp
	return a


func _enemy(at: Vector3) -> Node3D:
	var d := TrainingDummy.new()
	field.add_child(d)
	d.global_position = at
	return d


## Fires the needle and waits for it to land; returns [[target, ally]].
func _needle() -> Array:
	var got := []
	var cb := func(t, a): got.append([t, a])
	kit.needled.connect(cb)
	kit.needle()
	var t0 := Time.get_ticks_msec()
	while kit.current != "" and Time.get_ticks_msec() - t0 < 3000:
		await process_frame
	kit.needled.disconnect(cb)
	return got


## Calls basic_attack and waits for the shot to land; returns [fired, target it landed on or null].
func _basic(target) -> Array:
	var got := []
	var cb := func(t): got.append(t)
	kit.beak_landed.connect(cb)
	var fired: bool = kit.basic_attack(target)
	var t0 := Time.get_ticks_msec()
	while fired and got.is_empty() and Time.get_ticks_msec() - t0 < 2000:
		await process_frame
	kit.beak_landed.disconnect(cb)
	return [fired, got[0] if not got.is_empty() else null]


func _physics_secs(frames: int) -> float:
	return frames / float(Engine.physics_ticks_per_second)


func _run() -> void:
	await process_frame
	field = load("res://scenes/moba3d/field_test.tscn").instantiate()
	root.add_child(field)
	await process_frame
	player = field.get_node("Player")
	kit = KIT.install(player)
	await process_frame
	kit.unlinked.connect(func(a, why): unlinks.append([a, why]))
	var spr: DirectionalSprite3D = player.get_node("Sprite")

	# Frames
	for v in DirectionalSprite3D.VIEWS:
		for kind in ["idle_", "walk_"]:
			var an := StringName(kind + v)
			var ok := spr.sprite_frames.has_animation(an) and spr.sprite_frames.get_frame_texture(an, 0).get_height() == 160
			_check(ok, "%s is a 160-tall still" % an)
	_check(spr.size_class == "S" and spr.feet_edge_row == KIT.FEET_EDGE + KIT.HOVER_ROWS and not spr.tilts_any(),
		"size S, feet edge row %d (hovering %d texels), not tilted" % [spr.feet_edge_row, KIT.HOVER_ROWS])
	var lift: float = spr.position.y - (KIT.FEET_EDGE - KIT.CANVAS / 2.0) * spr.pixel_size
	_check(absf(lift - KIT.HOVER_ROWS * spr.pixel_size) < 0.001, "the still floats %.2f m above where its feet would stand" % lift)

	player.facing = Vector3(0, 0, -1)
	var f: Vector3 = kit.ahead()
	var p0: Vector3 = player.global_position

	# Needle at an ally 4 m ahead
	_clear()
	var a1 := _ally(p0 + f * 4.0)
	await process_frame
	var got: Array = await _needle()
	_check(got.size() == 1 and got[0][0] == a1 and got[0][1] == true, "the needle reached the ally")
	_check(absf(a1.hp - 360.0) < 1.0, "needle healed 300 -> %.1f (expected 360, 10%% of 600)" % a1.hp)
	_check(kit.link_target == a1, "the ally is linked")

	# The link over 3 s of physics time
	var hp0: float = a1.hp
	var fr0 := Engine.get_physics_frames()
	while _physics_secs(Engine.get_physics_frames() - fr0) < 3.0:
		await physics_frame
	var secs := _physics_secs(Engine.get_physics_frames() - fr0)
	var rate: float = (a1.hp - hp0) / secs
	_check(absf(rate - 6.0) < 0.6, "link heals %.2f a second over %.2f s (expected 6, 1%% of 600)" % [rate, secs])

	# Full health caps the heal
	a1.hp = 599.0
	await _needle()
	_check(a1.hp == 600.0, "healing stops at full health (599 + 60 -> %.1f)" % a1.hp)

	# A second ally takes the link
	var a2 := _ally(p0 + f.rotated(Vector3.UP, deg_to_rad(90.0)) * 3.0)
	await process_frame
	player.facing = f.rotated(Vector3.UP, deg_to_rad(90.0))
	unlinks.clear()
	got = await _needle()
	_check(got.size() == 1 and got[0][0] == a2 and kit.link_target == a2, "a needle on a second ally moves the link to it")
	_check(unlinks.size() == 1 and unlinks[0][0] == a1 and unlinks[0][1] == "replaced", "the first link ended as replaced")
	a1.hp = 400.0  # room to heal, so "no longer heals" measures something
	var a1_hp: float = a1.hp
	for i in 30:
		await physics_frame
	_check(a1.hp == a1_hp, "the old ally no longer heals")

	# Out of range breaks the link
	unlinks.clear()
	a2.global_position = p0 + kit.ahead() * (kit.link_range + 0.5)
	for i in 3:
		await physics_frame
	_check(kit.link_target == null and unlinks.size() == 1 and unlinks[0][1] == "range",
		"walking the ally to %.1f m breaks the link (range)" % (kit.link_range + 0.5))

	# An enemy on the line takes a hit and makes no link
	_clear()
	player.facing = f
	var e := _enemy(p0 + f * 5.0)
	await process_frame
	got = await _needle()
	_check(got.size() == 1 and got[0][0] == e and got[0][1] == false, "the needle reached the enemy")
	_check(absf(e.last_hit_scale - kit.needle_damage_scale) < 0.001,
		"the enemy took a kit hit x %.2f (%d damage)" % [e.last_hit_scale, roundi(MatchRules.kit_hit_damage * e.last_hit_scale)])
	_check(kit.link_target == null, "an enemy hit makes no link")

	# First on the line wins; 2 m off the line is ignored; past range hits nothing
	_clear()
	var near_e := _enemy(p0 + f * 3.0)
	var far_a := _ally(p0 + f * 6.0)
	var off_a := _ally(p0 + f * 2.0 + f.rotated(Vector3.UP, PI / 2.0) * 2.0)
	await process_frame
	got = await _needle()
	_check(got.size() == 1 and got[0][0] == near_e and far_a.hp == 300.0 and off_a.hp == 300.0,
		"the enemy in front of the ally took it; the ally behind and the one 2 m off the line were untouched")
	_clear()
	var far := _ally(p0 + f * (kit.needle_range + 1.5))
	await process_frame
	got = await _needle()
	_check(got.size() == 1 and got[0][0] == null and far.hp == 300.0,
		"an ally %.1f m away is past the %d m range: the needle hit nothing" % [kit.needle_range + 1.5, int(kit.needle_range)])

	# Basic attack, beak shot
	_clear()
	player.facing = f
	_check(kit.has_method("basic_attack") and kit.basic_range == 6.0 and kit.basic_cooldown == 0.9,
		"basic_attack is there, reach 6 m, cooldown 0.9 s (the director reads both)")
	var cam := root.get_camera_3d()
	if cam == null:
		_check(false, "a camera to aim with")
	else:
		var side := f.rotated(Vector3.UP, -PI / 2.0)
		var e_ahead := _enemy(p0 + f * 4.0)
		var e_side := _enemy(p0 + side * 4.0)
		await process_frame
		player.aim_screen_override = cam.unproject_position(e_side.global_position)
		var shot: Array = await _basic(null)
		_check(shot[0] == true and shot[1] == e_side and absf(e_side.last_hit_scale - 0.5) < 0.001 and e_ahead.last_hit_scale == 1.0,
			"the shot went to the mouse aim (the enemy to the side, not the one it faced) for %d damage" % roundi(MatchRules.kit_hit_damage * e_side.last_hit_scale))
		_check(KIT.flat(player.facing).normalized().dot(side) > 0.99, "it turned to face its target")
		_clear()
		var e_far := _enemy(p0 + f * 8.0)
		await process_frame
		player.aim_screen_override = cam.unproject_position(e_far.global_position)
		shot = await _basic(null)
		_check(shot[0] == false and e_far.last_hit_scale == 1.0, "an enemy 8 m away is out of reach: no shot")
		_clear()
		var e_off := _enemy(p0 + side * 4.0)
		await process_frame
		player.aim_screen_override = cam.unproject_position(p0 - side * 4.0)
		shot = await _basic(null)
		_check(shot[0] == false and e_off.last_hit_scale == 1.0, "an enemy opposite the aim is outside the cone: no shot")
		_clear()
		var a_near := _ally(p0 + f * 3.0)
		await process_frame
		player.aim_screen_override = cam.unproject_position(a_near.global_position)
		shot = await _basic(null)
		_check(shot[0] == false and a_near.hp == 300.0, "an ally under the aim is never shot")
		player.aim_screen_override = null
	_clear()
	var e_bot := _enemy(p0 + f * 5.0)
	var e_bot_far := _enemy(p0 + f.rotated(Vector3.UP, PI / 2.0) * 8.0)
	await process_frame
	var bot_shot: Array = await _basic(e_bot)
	_check(bot_shot[0] == true and bot_shot[1] == e_bot and absf(e_bot.last_hit_scale - 0.5) < 0.001, "a bot's target 5 m away is shot")
	bot_shot = await _basic(e_bot_far)
	_check(bot_shot[0] == false and e_bot_far.last_hit_scale == 1.0, "a bot's target 8 m away is refused")

	print("hummingbird kit check: %d failed" % fails)
	quit(1 if fails > 0 else 0)
