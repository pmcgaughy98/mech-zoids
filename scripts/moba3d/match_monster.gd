class_name MatchMonster
extends MatchMinion
## A jungle camp monster (Claude, 2026-11-04, game feel lane). THE LOOK IS A PLAIN STAND-IN (the training dummy, larger,
## in an olive tint): what lives in the camps is Preston's to design. It stands at its camp until something hurts it,
## then fights back. Pulled past its leash it walks home, takes no damage on the way, and heals to full there. The
## director respawns the camp after MatchRules.monster_respawn. Every number is a placeholder in MatchRules.

signal camp_aggro ## the sound lane's name: something pulled this camp

var home := Vector3.ZERO
var resetting := false
var aggro: Node3D = null
var camp := "" ## the camp marker's name


func _ready() -> void:
	team = ""
	kind = "monster"
	super()


func _look_scale() -> float:
	return 1.1


func _stats() -> void:
	max_hp = MatchRules.monster_hp
	attack_range = MatchRules.monster_range
	attack_damage = MatchRules.monster_damage
	attack_cooldown = MatchRules.monster_cooldown
	walk_speed = MatchRules.monster_speed
	sight = 0.0


func _physics_process(delta: float) -> void:
	if alive and not resetting and aggro != null and MatchTeams.flat(global_position - home).length() > MatchRules.monster_leash:
		_start_reset()
	super(delta)


func _still_good(t: Variant) -> bool: ## untyped: a target can be freed between checks
	if resetting or not MatchTeams.hittable(t):
		return false
	if taunted > 0.0 and MatchTeams.hittable(taunted_by):
		return t == taunted_by
	return t == aggro


## Only what pulled it (or a taunt). It drops a target that has run past the leash and goes home.
func _choose_target() -> Node3D:
	if resetting:
		return null
	if taunted > 0.0 and MatchTeams.hittable(taunted_by):
		return taunted_by
	if MatchTeams.hittable(aggro) and MatchTeams.flat(aggro.global_position - home).length() <= MatchRules.monster_leash + 3.0:
		return aggro
	if aggro != null:
		_start_reset()
	return null


## No target: walk home, and heal to full once there.
func _idle_move(delta: float) -> void:
	if MatchTeams.flat(home - global_position).length() > 0.4:
		_step_toward(home, delta)
	elif resetting:
		resetting = false
		hp = max_hp


## Monsters hit up close: a lunge and the damage at once.
func _strike(t: Node3D, dir: Vector3) -> void:
	_lunge = 0.18
	_lunge_dir = dir / scale.x
	t.take_damage(attack_damage, self)
	var r: float = t.radius() if t.has_method("radius") else 0.3
	Fx3D.spawn(get_parent(), "hit_spark", t.global_position - dir * r + Vector3.UP * 0.6, 0.25)


func _start_reset() -> void:
	resetting = true
	aggro = null
	target = null


func _hurt(by: Node3D) -> void:
	if by == null or not is_instance_valid(by) or by == self:
		return
	if not MatchTeams.hittable(aggro):
		var fresh := aggro == null
		aggro = by
		if fresh:
			camp_aggro.emit()


func take_damage(amount: float, by: Node3D = null) -> void:
	if resetting:
		_flash = 0.16  # it shrugs it off on the way home
		return
	super(amount, by)
