extends Node2D
## One unit on the MOBA arena: a core, a tower or a lane unit (a machine later). The match steps it through
## advance(); placeholder shapes until the arena gets art.

signal was_attacked(attacker: Node2D, amount: int)
signal died(unit: Node2D)

const TEAM_COLOURS := {"blue": Color(0.3, 0.55, 1.0), "red": Color(1.0, 0.3, 0.25)}
const RADII := {"core": 26.0, "tower": 14.0, "lane": 5.0}

@export_enum("blue", "red") var team: String = "blue"
@export_enum("core", "tower", "lane") var kind: String = "lane"
@export var max_hp := 300
@export var damage := 20
## Reach of an attack, measured from this unit's centre to the target's edge.
@export var attack_range := 24.0
@export var attack_cooldown := 1.0
@export var speed := 60.0
## How far a moving unit looks for something to fight.
@export var sight := 110.0

var hp := 0
var alive := true
var path := PackedVector2Array()  ## lane points in global space, walked in order
var path_index := 0
var target: Node2D = null
var match_node: Node2D = null  ## the arena (moba_match.gd) that owns this unit
var _cooldown := 0.0


func _ready() -> void:
	hp = max_hp


func radius() -> float:
	return RADII[kind]


## A core can only be hit once every tower of its team has fallen.
func can_be_hit() -> bool:
	return alive and (kind != "core" or match_node.towers_standing(team) == 0)


## Steps this unit by delta seconds: fight what is in reach, else walk the lane.
func advance(delta: float) -> void:
	_cooldown = maxf(_cooldown - delta, 0.0)
	if damage <= 0:
		return
	var reach := sight if speed > 0.0 else attack_range
	if not _can_target(target) or _edge_distance(target) > reach:
		target = match_node.nearest_enemy(self, reach)
	if target != null:
		if _edge_distance(target) <= attack_range:
			if _cooldown == 0.0:
				_cooldown = attack_cooldown
				target.take_damage(damage, self)
		elif speed > 0.0:
			global_position = global_position.move_toward(target.global_position, speed * delta)
	elif speed > 0.0 and path_index < path.size():
		global_position = global_position.move_toward(path[path_index], speed * delta)
		if global_position.distance_to(path[path_index]) < 1.0:
			path_index += 1


func take_damage(amount: int, attacker: Node2D) -> void:
	if not can_be_hit():
		return
	hp = maxi(hp - amount, 0)
	was_attacked.emit(attacker, amount)
	match_node.unit_attacked.emit(self, attacker, amount)
	queue_redraw()
	if hp == 0:
		alive = false
		died.emit(self)
		match_node.on_unit_died(self)


func _can_target(other: Node2D) -> bool:
	return is_instance_valid(other) and other.team != team and other.can_be_hit()


func _edge_distance(other: Node2D) -> float:
	return global_position.distance_to(other.global_position) - other.radius()


func _draw() -> void:
	var colour: Color = TEAM_COLOURS[team]
	var r := radius()
	if kind == "lane":
		draw_circle(Vector2.ZERO, r, colour)
	else:
		draw_rect(Rect2(-r, -r, r * 2.0, r * 2.0), colour)
	var bar := Rect2(-r, -r - 6.0, r * 2.0, 3.0)
	draw_rect(bar, Color(0.0, 0.0, 0.0, 0.6))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * hp / float(max_hp), bar.size.y)), Color(0.4, 1.0, 0.4))
