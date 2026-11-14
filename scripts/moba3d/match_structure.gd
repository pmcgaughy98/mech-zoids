class_name MatchStructure
extends Node3D
## A tower or a core in the match (Claude, 2026-11-04, game feel lane). The map lane builds and owns the look under
## Built (arena_blockout.gd); this is only the logic, standing on their saved markers (Markers/BlueTower, RedCore ...),
## as agreed with them. When it falls it calls their arena.set_structure_down(marker, true).
## From the 2D skeleton: a core only takes hits once its team's tower has fallen.
## Tower targeting (Mech-Zoids' brief): minions first, then machines; it keeps a target until it dies or leaves range,
## and switches to an enemy machine that hits an allied machine under it. It needs a clear line at chest height, so it
## never shoots through the lane walls. Every number is a placeholder in MatchRules.

signal tower_shot ## the sound lane's names; tower_shot_hit comes from a short-lived node at the impact (HitPing)
signal tower_destroyed
signal core_destroyed
signal fell(s: MatchStructure, by: Node3D)

const BOLT_FROM := 3.6 ## where the bolt leaves the pillar: under the 4.45 m camera line, so the shot shows near it

var team := "blue"
var kind := "tower"
var marker := "BlueTower"
var max_hp := 0.0
var hp := 0.0
var alive := true
var seen := true
var body_r := 1.4
var reach := 12.0
var target: Node3D = null
var switched_to: Node3D = null ## the enemy machine it switched to for hitting an ally under it
var director: Node = null
var arena: Node = null
var _switch_left := 0.0
var _cooldown := 0.5
var _think := 0.0
var off_left := 0.0 ## seconds left switched off by the plaza beacon (no targeting, no shots, no beam); the HUD reads it
var _beam: MeshInstance3D
var _beam_mat: StandardMaterial3D
var _foot_ring: MeshInstance3D
var _alert_on := false ## what the map lane's range ring was last told (arena.set_tower_alert)


class HitPing extends Node3D:
	signal tower_shot_hit


class Bolt extends MeshInstance3D:
	var tower: MatchStructure
	var aim: Node3D

	func _process(delta: float) -> void:
		if not is_instance_valid(aim) or aim.get("alive") != true or not is_instance_valid(tower):
			queue_free()
			return
		var p := aim.global_position + Vector3.UP * 0.8
		var d := p - global_position
		var step := MatchRules.tower_bolt_speed * delta
		if d.length() <= step:
			tower.landed(aim, p)
			queue_free()
			return
		global_position += d.normalized() * step


func _ready() -> void:
	add_to_group("match_unit")
	max_hp = MatchRules.tower_hp if kind == "tower" else MatchRules.core_hp
	hp = max_hp
	if kind == "tower":
		_make_warning()


func radius() -> float:
	return body_r


func can_be_hit() -> bool:
	if not alive:
		return false
	return kind != "core" or director == null or director.towers_standing(team) == 0


func set_seen(v: bool) -> void:
	seen = v


func take_damage(amount: float, by: Node3D = null) -> void:
	if not can_be_hit():
		return
	if by != null and is_instance_valid(by) and by.has_method("rally_scale"):
		amount *= by.rally_scale(self)  # the bison's Eruption rally (2026-11-14); 1.0 unless the attacker is rallied
	hp = maxf(hp - amount, 0.0)
	Fx3D.spawn(get_parent(), "hit_spark", global_position + Vector3.UP * 1.6, 0.3)
	if hp <= 0.0:
		_fall(by)


## An enemy machine hit an allied machine under this tower: it turns on that machine for a while.
func switch_to(m: Variant) -> void:
	if not alive or kind != "tower" or off_left > 0.0 or not _can_shoot(m):
		return
	switched_to = m
	_switch_left = MatchRules.tower_switch_time
	target = m


## The plaza beacon (map lane, 2026-11-05): the team that takes it switches the other team's tower off for t seconds.
## A second capture while it is off only extends it to the longer of the two. Nothing on a core or a fallen tower.
func switch_off(t: float) -> void:
	if not alive or kind != "tower" or t <= 0.0:
		return
	var was_on := off_left <= 0.0
	off_left = maxf(off_left, t)
	target = null
	switched_to = null
	_show_warning(false)
	if was_on:
		_set_off(true)


func _set_off(on: bool) -> void: ## the map lane's visuals: head still, team light dimmed, range ring hidden
	if arena != null and arena.has_method("set_structure_off"):
		arena.set_structure_off(marker, on)


func _physics_process(delta: float) -> void:
	if not alive or kind != "tower" or MatchDirector.over:
		_show_warning(false)
		return
	if off_left > 0.0:
		off_left = maxf(off_left - delta, 0.0)
		target = null
		_show_warning(false)
		if off_left <= 0.0:
			_set_off(false)
		return
	_cooldown = maxf(_cooldown - delta, 0.0)
	_switch_left = maxf(_switch_left - delta, 0.0)
	_think -= delta
	if _think <= 0.0 or not _can_shoot(target):
		_think = 0.1
		target = _pick()
	if target != null and _cooldown <= 0.0:
		_cooldown = MatchRules.tower_cooldown
		_fire(target)
	_show_warning(target != null and director != null and target == director.get("player"))


func _pick() -> Node3D:
	if _switch_left > 0.0 and _can_shoot(switched_to):
		return switched_to
	switched_to = null
	if _can_shoot(target):
		return target
	var best: Node3D = null
	var best_d := INF
	for pass_kind in ["minion", "machine"]:
		for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
			if u.get("kind") != pass_kind or not _can_shoot(u):
				continue
			var d := MatchTeams.flat(u.global_position - global_position).length()
			if d < best_d:
				best = u
				best_d = d
		if best != null:
			return best
	return null


func _can_shoot(u: Variant) -> bool: ## untyped: a target can be freed between checks
	if not MatchTeams.hittable(u) or MatchTeams.team_of(u) == team or MatchTeams.team_of(u) == "":
		return false
	var to := MatchTeams.flat(u.global_position - global_position)
	if to.length() > reach:
		return false
	var from := global_position + to.normalized() * (body_r + 0.3)
	return MatchTeams.clear_line(self, from, u.global_position, 1.2)


func _fire(t: Node3D) -> void:
	var b := Bolt.new()
	b.tower = self
	b.aim = t
	var m := SphereMesh.new()
	m.radius = 0.2
	m.height = 0.4
	m.radial_segments = 8
	m.rings = 4
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = MatchTeams.COLOURS[team].lightened(0.45)
	m.material = mat
	b.mesh = m
	get_parent().add_child(b)
	var to := MatchTeams.flat(t.global_position - global_position).normalized()
	b.global_position = global_position + to * body_r + Vector3.UP * BOLT_FROM
	tower_shot.emit()


func landed(t: Node3D, at: Vector3) -> void:
	if MatchTeams.hittable(t):
		t.take_damage(MatchRules.tower_damage, self)
	Fx3D.spawn(get_parent(), "hit_spark", at, 0.4)
	var ping := HitPing.new()
	get_parent().add_child(ping)
	ping.global_position = at
	ping.tower_shot_hit.emit()
	ping.queue_free()


func _fall(by: Node3D) -> void:
	alive = false
	target = null
	remove_from_group("match_unit")
	_show_warning(false)
	if off_left > 0.0:
		off_left = 0.0
		_set_off(false)
	if arena != null and arena.has_method("set_structure_down"):
		arena.set_structure_down(marker, true)
	for i in 3:
		Fx3D.spawn(get_parent(), "impact_puff", global_position + Vector3(randf_range(-1, 1), 0.2 + i * 0.8, randf_range(-1, 1)), 0.9)
	if kind == "tower":
		tower_destroyed.emit()
	else:
		core_destroyed.emit()
	fell.emit(self, by)


# ---- the warning when it aims at the player: a red beam from the pillar and a red ring at the machine's feet ---------

func _make_warning() -> void:
	_beam_mat = StandardMaterial3D.new()
	_beam_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_beam_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_beam_mat.albedo_color = Color(1.0, 0.15, 0.1, 0.55)
	var box := BoxMesh.new()
	box.size = Vector3(0.07, 0.07, 1.0)
	box.material = _beam_mat
	_beam = MeshInstance3D.new()
	_beam.mesh = box
	_beam.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_beam.visible = false
	_beam.top_level = true
	add_child(_beam)
	var ring := TorusMesh.new()
	ring.inner_radius = 0.95
	ring.outer_radius = 1.15
	ring.rings = 24
	ring.ring_segments = 4
	ring.material = _beam_mat
	_foot_ring = MeshInstance3D.new()
	_foot_ring.mesh = ring
	_foot_ring.scale = Vector3(1, 0.05, 1)
	_foot_ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_foot_ring.visible = false
	_foot_ring.top_level = true
	add_child(_foot_ring)


func _show_warning(on: bool) -> void:
	if _beam == null:
		return
	if on != _alert_on and arena != null and arena.has_method("set_tower_alert"):
		_alert_on = on
		arena.set_tower_alert(marker, 1.0 if on else 0.0)  # the map lane's range ring turns red
	_beam.visible = on
	_foot_ring.visible = on
	if not on:
		return
	var a := global_position + Vector3.UP * BOLT_FROM
	var b := target.global_position + Vector3.UP * 0.8
	_beam.global_position = (a + b) * 0.5
	_beam.look_at_from_position(_beam.global_position, b, Vector3.UP)
	_beam.scale = Vector3(1, 1, a.distance_to(b))
	_beam_mat.albedo_color.a = 0.35 + 0.3 * absf(sin(Time.get_ticks_msec() * 0.008))
	_foot_ring.global_position = target.global_position + Vector3.UP * 0.05
