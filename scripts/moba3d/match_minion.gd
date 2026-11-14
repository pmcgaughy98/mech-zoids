class_name MatchMinion
extends TrainingDummy
## A lane minion (Claude, 2026-11-04, game feel lane). Preston: "Minions are small drone mechs, placeholders for now."
## THE LOOK IS THAT PLACEHOLDER DRONE: the sprite factory lane's design, packed by the animation lane (S, 96 canvas,
## idle, walk, attack, hit and death in five views, blue and red sheets). The training dummy underneath only lends its
## reactions (stun, slow, tosses, domes) and stays hidden. It walks its team's lane on the nav mesh, fights the nearest
## enemy it can see and pushes the towers. Ported from the 2D skeleton (scripts/moba/moba_unit.gd): a core only takes
## hits once its tower has fallen. Every number is a placeholder in MatchRules.

signal minion_hit ## the sound lane's name: this minion fired
signal unit_died(unit: Node3D, by: Node3D)

const TINTS := {"blue": Color(0.55, 0.75, 1.45), "red": Color(1.45, 0.6, 0.55), "": Color(0.85, 1.15, 0.5)}
const BOOST_TINTS := {"blue": Color(0.75, 1.0, 1.7), "red": Color(1.7, 0.85, 0.7)} ## a pit-boosted wave: half at one pit, full at two
const DRONE := {
	"blue": preload("res://art/machines/minion/minion_blue_frames.tres"),
	"red": preload("res://art/machines/minion/minion_red_frames.tres"),
}
const SHOT_FRAME_T := 0.2 ## the attack's frame 2 (200-300 ms, the animation lane's timing): the shot leaves then
const MUZZLE_H := 0.5 ## metres: about the drone's lens, under its hover body
const BAR_H := 1.3 ## metres: the HUD bar over an upright drone
## Over a drone with tilted views (DirectionalSprite3D tilt, off in the game): the 35-degree views
## stand taller on screen and reach the 1.3 m bar when the drone is low on the screen. 1.5 m clears every view by
## 2 px or more from 4 m nearer the camera to 14 m farther (cam_angle_set_test.gd, 2026-11-04). PLACEHOLDER.
const BAR_H_TILTED := 1.5

var team := "blue"
var kind := "minion"
var max_hp := 0.0
var hp := 0.0
var alive := true
var seen := true ## false while the map lane's fog hides it from the player
var path := PackedVector3Array() ## its lane, gate to enemy core, in world space (set by the director)
var path_index := 0
var target: Node3D = null
var last_hit_by: Node3D = null
var director: Node = null
var attack_range := 1.0
var attack_damage := 0.0
var power := 1.0 ## a pit-boosted wave's multiplier on hp and damage; the director sets it before the minion joins the tree
var attack_cooldown := 1.0
var walk_speed := 3.5
var sight := 7.0
var _cooldown := 0.0
var _think := 0.0
var _lunge := 0.0
var _lunge_dir := Vector3.ZERO
var _walk_t := 0.0
var _moving := false
var facing := Vector3(0, 0, -1)
const MODEL_GLB := "res://art/arena_models/minion_melee.glb" ## Preston's Meshy melee minion (rigged, no clips yet)
@export var model_height := 1.0 ## metres: the static 3D minion stands this tall (the drone read about 1.1 m)
var model: Node3D = null ## the static 3D minion over the hidden drone (Preston 2026-11-11: "Plug in static"), or null
var _model_over: StandardMaterial3D = null ## additive overlay: the team colour, and the hit flash on top
var _model_turn := 0.0
var _model_t := 0.0
var _model_lunge := 0.0
static var _model_scene: PackedScene = null
static var _model_scale := 0.0
var drone: DirectionalSprite3D = null ## the drone sprite; null for a camp monster's stand-in
var _drone_y := 0.0
var _action_left := 0.0 ## seconds until the drone's attack or hit animation hands back to idle and walk
var _shot_in := -1.0 ## seconds until the queued shot leaves
var _shot_target: Node3D = null


func _ready() -> void:
	super()
	remove_from_group("kit_target")
	for g in ["match_unit", "map_units", "vision_sources"]:
		add_to_group(g)
	_stats()
	hp = max_hp
	set_meta("team", team)
	set_meta("unit_kind", kind)
	set_meta("vision_radius", MatchRules.vision_minion)
	tint = TINTS.get(team, Color.WHITE)
	scale = Vector3.ONE * _look_scale()
	if kind == "minion" and DRONE.has(team):
		_sprite.visible = false
		tint = Color.WHITE  # the drone's team colours are drawn in
		drone = DirectionalSprite3D.new()
		drone.sprite_frames = DRONE[team]
		drone.canvas_height = 96
		drone.feet_edge_row = 88
		drone.size_class = "S"
		add_child(drone)
		_drone_y = drone.position.y
		drone.play(&"idle_s")
		for c in get_children():  # the dummy's fixed shadow gives way to one under the drone's hull (camera lane, 2026-11-04)
			if c is MeshInstance3D:
				c.visible = false
		if not _model_up():  # the 3D model casts its own shadow; the drone's contact shadow is only for the sprite
			ContactShadow3D.attach(self, drone, {"front": 16, "rear": -20, "half_width": 24})  # hull underside and pods, texels
	if power > 1.0 and MatchRules.pit_wave_bonus > 0.0:  # the push reads: a boosted wave glows in its team colour (game feel lane, 2026-11-05)
		var k := clampf((power - 1.0) / (2.0 * MatchRules.pit_wave_bonus), 0.0, 1.0)
		tint = tint * Color.WHITE.lerp(BOOST_TINTS.get(team, Color.WHITE), k)


func _look_scale() -> float:
	return 1.0


## The static 3D minion (game feel lane, 2026-11-11). The drone keeps running hidden underneath, so its attack, hit and
## death timing still drive the minion; the model only stands in for the picture. False when the GLB is missing.
func _model_up() -> bool:
	if _model_scene == null:
		if not ResourceLoader.exists(MODEL_GLB):
			return false
		_model_scene = load(MODEL_GLB)
	model = _model_scene.instantiate()
	model.name = "Model3D"
	add_child(model)
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	if _model_scale <= 0.0:
		var h := 0.0
		for m in meshes:
			h = maxf(h, (m as MeshInstance3D).get_aabb().end.y)
		_model_scale = model_height / h if h > 0.01 else 1.0
	model.scale = Vector3.ONE * _model_scale
	_model_over = StandardMaterial3D.new()
	_model_over.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_model_over.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_model_over.albedo_color = TINTS.get(team, Color.WHITE) * 0.3
	for m in meshes:
		(m as MeshInstance3D).material_overlay = _model_over
	drone.visible = false
	_model_turn = atan2(facing.x, facing.z)
	return true


## Turns the model to its facing (it faces +Z), bobs it on the walk and hovers it standing, leans it into the walk,
## steps it forward on an attack, and carries the dummy's shakes, shoves and tosses (feel_offset) and its hit flash.
func _model_step(delta: float) -> void:
	_model_t += delta
	_model_turn = lerp_angle(_model_turn, atan2(facing.x, facing.z), minf(1.0, delta * 10.0))
	var bob := absf(sin(_model_t * 9.0)) * 0.05 if _moving else sin(_model_t * 2.2) * 0.015
	_model_lunge = _model_lunge + delta if drone.action == "attack" else 0.0
	var step := sin(clampf(_model_lunge / 0.3, 0.0, 1.0) * PI) * 0.15
	var ahead := Vector3(sin(_model_turn), 0.0, cos(_model_turn))
	model.position = Vector3(_sprite.position.x, air + bob, _sprite.position.z) + ahead * step
	model.rotation = Vector3(0.08 if _moving else 0.0, _model_turn, 0.0)
	var f := maxf(_sprite.modulate.r - 1.0, 0.0)
	_model_over.albedo_color = TINTS.get(team, Color.WHITE) * 0.3 + Color(f, f, f) * 0.6


func _stats() -> void:
	max_hp = MatchRules.minion_hp
	attack_range = MatchRules.minion_range
	attack_damage = MatchRules.minion_damage
	attack_cooldown = MatchRules.minion_cooldown
	walk_speed = MatchRules.minion_speed
	sight = MatchRules.minion_sight
	max_hp *= power
	attack_damage *= power


func radius() -> float:
	return BODY_R * scale.x


func can_be_hit() -> bool:
	return alive


## How high the HUD draws this minion's health bar.
func bar_height() -> float:
	return BAR_H_TILTED if drone != null and drone.tilts_any() else BAR_H


func set_seen(v: bool) -> void:
	seen = v
	visible = v


func _process(delta: float) -> void:
	super(delta)
	if has_meta("held_by"):return
	if drone != null:
		if alive:
			drone.modulate = _sprite.modulate  # the dummy's flash and slow tint
			_action_left -= delta
			if _action_left <= 0.0 and drone.action != "":
				drone.stop_action()
		# Hit shake, shoves and tosses ride on feel_offset: the drone re-plants itself (DirectionalSprite3D._plant), which
		# overwrote a plain position (2026-11-06). _drone_y is where it stood at setup, so only the toss height goes on top.
		drone.feel_offset = Vector3(_sprite.position.x, air, _sprite.position.z)
		var cam := get_viewport().get_camera_3d()
		drone.show_facing(facing, cam.global_basis if cam != null else Basis(), _moving)
		if model != null and alive:
			_model_step(delta)
		return
	_lunge = maxf(_lunge - delta, 0.0)
	var k := sin(_lunge / 0.18 * PI) if _lunge > 0.0 else 0.0  # out and back over 0.18 s
	var bob := absf(sin(_walk_t * 11.0)) * 0.06 if _moving else 0.0
	_sprite.position += _lunge_dir * k * 0.35 + Vector3.UP * bob


func _physics_process(delta: float) -> void:
	_moving = false
	if not alive or MatchDirector.over:
		return
	if _shot_in >= 0.0:
		_shot_in -= delta
		if _shot_in < 0.0 and stunned <= 0.0 and MatchTeams.hittable(_shot_target):
			_fire(_shot_target)
	_cooldown = maxf(_cooldown - delta, 0.0)
	if stunned > 0.0 or air > 0.0 or (_move_tw != null and _move_tw.is_valid() and _move_tw.is_running()):
		return
	_think -= delta
	if _think <= 0.0 or not _still_good(target):
		_think = 0.2
		target = _choose_target()
	if target != null:
		if MatchTeams.edge_distance(self, target) <= attack_range:
			if _cooldown <= 0.0:
				_attack(target)
			return
		_step_toward(target.global_position, delta)
	else:
		_idle_move(delta)


func _still_good(t: Variant) -> bool: ## untyped: a target can be freed between checks
	if not MatchTeams.hittable(t):
		return false
	if taunted > 0.0 and MatchTeams.hittable(taunted_by):
		return t == taunted_by
	return MatchTeams.edge_distance(self, t) <= sight + 2.0


## The 2D skeleton's nearest_enemy: the closest enemy it can see, with buildings only when nothing else is in sight.
## Camp monsters are left alone.
func _choose_target() -> Node3D:
	if taunted > 0.0 and MatchTeams.hittable(taunted_by):
		return taunted_by
	var best: Node3D = null
	var best_d := INF
	var building: Node3D = null
	var building_d := INF
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		if u == self or MatchTeams.team_of(u) == team or u.get("kind") == "monster" or not MatchTeams.hittable(u):
			continue
		var d := MatchTeams.edge_distance(self, u)
		if d > sight:
			continue
		if u.get("kind") == "tower" or u.get("kind") == "core":
			if d < building_d:
				building = u
				building_d = d
		elif d < best_d and MatchTeams.clear_line(self, global_position, u.global_position, 0.6):
			best = u
			best_d = d
	return best if best != null else building


## Walks toward p along the ground; walls slide it (ArenaMotion), and it keeps a little apart from its own kind.
func _step_toward(p: Vector3, delta: float) -> void:
	var to := MatchTeams.flat(p - global_position)
	if to.length() < 0.01:
		return
	var push := Vector3.ZERO
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		if u == self or u.get("kind") != kind or MatchTeams.team_of(u) != team:
			continue
		var off := MatchTeams.flat(global_position - u.global_position)
		if off.length() < 0.9 and off.length() > 0.001:
			push += off.normalized() * (0.9 - off.length())
	var pace := walk_speed * (MatchRules.slow_mult if slowed > 0.0 else 1.0)
	facing = to.normalized()
	var want := global_position + (to.normalized() + push * 1.5).limit_length(1.0) * pace * delta
	_move_to(MatchBodies.block(self, global_position, want, radius()))
	_moving = true
	_walk_t += delta


## No enemy in sight: on down its lane.
func _idle_move(delta: float) -> void:
	while path_index < path.size() and MatchTeams.flat(path[path_index] - global_position).length() < 1.2:
		path_index += 1
	if path_index < path.size():
		_step_toward(path[path_index], delta)


func _attack(t: Node3D) -> void:
	_cooldown = attack_cooldown
	var dir := MatchTeams.flat(t.global_position - global_position).normalized()
	if dir.length() > 0.01:
		facing = dir
	_strike(t, dir)
	if director != null and director.has_method("note_clash"):
		director.note_clash(self, t)


## The drone's twin blaster (sprite factory lane, 2026-11-04): the attack plays, and the shot leaves on its frame 2.
func _strike(t: Node3D, _dir: Vector3) -> void:
	if drone != null:
		drone.play_action("attack")
		_action_left = 0.5
	_shot_in = SHOT_FRAME_T
	_shot_target = t


func _fire(t: Node3D) -> void:
	var from := global_position + Vector3.UP * (MUZZLE_H - TestShot.CHEST)  # the shot flies at the lens's height
	var s := TestShot.fire(get_parent(), from, t.global_position, team == "red", t)
	s.team = team
	s.hp_damage = attack_damage
	s.source = self
	s.reach = attack_range + 2.0
	Fx3D.spawn(get_parent(), "hit_spark", global_position + facing * 0.4 + Vector3.UP * MUZZLE_H, 0.15)  # muzzle flash
	minion_hit.emit()


func take_damage(amount: float, by: Node3D = null) -> void:
	if not alive:
		return
	if by != null and is_instance_valid(by) and by.has_method("rally_scale"):
		amount *= by.rally_scale(self)  # the bison's Eruption rally (2026-11-14); 1.0 unless the attacker is rallied
	_flash = 0.16
	hp = maxf(hp - amount, 0.0)
	if by != null and is_instance_valid(by):
		last_hit_by = by
	_hurt(by)
	if hp <= 0.0:
		_die(by)
	elif drone != null and drone.action == "":
		drone.play_action("hit")  # never over an attack, so the shot still shows
		_action_left = 0.2


func _hurt(_by: Node3D) -> void:
	pass


## A kit hit (the kits call hit(player), or hit(player, scale) for a lighter or heavier one): the flash, and the kit's
## placeholder damage times the scale.
func hit(by: Node3D = null, scale := 1.0) -> void:
	super(by, scale)
	if by != null and by != self:
		take_damage(MatchRules.kit_hit_damage * scale, by)


func toss_to(land: Vector3, height: float, time: float, stun_t: float, deal := true) -> void:  # deal false: the lift only
	if deal:
		take_damage(MatchRules.kit_hit_damage, MatchTeams.caster)
	if alive:
		super(land, height, time, stun_t, deal)  # as before when dealing; the lift only when not


func knock_aside(offset: Vector3, time: float, deal := true) -> void:  # deal false: the push only (rhino release)
	if deal:
		take_damage(MatchRules.kit_hit_damage, MatchTeams.caster)
	if alive:
		super(offset, time, deal)


func _die(by: Node3D) -> void:
	alive = false
	for g in ["match_unit", "map_units", "vision_sources"]:
		remove_from_group(g)
	halt()
	unit_died.emit(self, by)
	Fx3D.spawn(get_parent(), "impact_puff", global_position, 0.3)
	var tw := create_tween()
	if drone != null:  # it drops to the ground, the wreck rests a moment, then fades
		drone.play_action("death")
		drone.modulate = Color.WHITE
		tw.tween_interval(1.6)
		tw.tween_property(drone, "modulate:a", 0.0, 0.5)
		if model != null:  # the static model tips and settles, rests, then shrinks away on the drone's timing
			var mt := create_tween()
			mt.tween_property(model, "rotation:z", 0.5, 0.35)
			mt.parallel().tween_property(model, "position:y", -0.12, 0.35)
			mt.tween_interval(1.25)
			mt.tween_property(model, "scale", model.scale * 0.05, 0.5)
	else:
		tw.tween_property(self, "scale", Vector3.ONE * 0.05, 0.3)
	tw.tween_callback(queue_free)


## A hex dome holds it only when the dome is the other team's (ApeKit tags each dome with its team).
func _blocked_by(dome: HexShield) -> bool:
	return dome.cage_all or str(dome.get_meta("team", "")) != team
