extends Node2D
## The MOBA arena root: owns every unit and steps them in fixed steps, ticks once a second, and ends the match
## when a core falls. Lanes are Line2D children of Lanes, drawn from blue's core to red's; each team's buildings
## sit under the blue and red nodes. Layout studied from Shotcaller (structure only, nothing copied).

signal second_ticked(seconds: int)
signal unit_attacked(target: Node2D, attacker: Node2D, amount: int)
signal unit_died(unit: Node2D)
signal match_ended(winner: String)

## Fixed step, so a sped-up check plays exactly the match the game would.
const STEP := 1.0 / 30.0

## Off when a check drives advance() itself.
@export var run_on_its_own := true

var units: Array = []
var lanes := {}  ## lane name -> PackedVector2Array in global space, blue's core first
var elapsed := 0.0
var winner := ""
var _next_tick := 1.0
var _spare := 0.0

@onready var spawner: Node = $Spawner
@onready var unit_layer: Node2D = $Units


func _ready() -> void:
	for lane: Line2D in $Lanes.get_children():
		var points := PackedVector2Array()
		for point in lane.points:
			points.append(lane.to_global(point))
		lanes[String(lane.name)] = points
	for team in ["blue", "red"]:
		for building in get_node(team).get_children():
			register(building)


func _physics_process(delta: float) -> void:
	if run_on_its_own:
		advance(delta)


## Steps the whole match by delta seconds.
func advance(delta: float) -> void:
	_spare += delta
	while _spare >= STEP and winner == "":
		_spare -= STEP
		elapsed += STEP
		spawner.advance(STEP)
		for unit in units.duplicate():
			if unit.alive:
				unit.advance(STEP)
		if elapsed >= _next_tick:
			second_ticked.emit(int(_next_tick))
			_next_tick += 1.0


func register(unit: Node2D) -> void:
	unit.match_node = self
	units.append(unit)


func spawn(unit: Node2D, at: Vector2) -> void:
	unit_layer.add_child(unit)
	unit.global_position = at
	register(unit)


func on_unit_died(unit: Node2D) -> void:
	units.erase(unit)
	unit_died.emit(unit)
	unit.queue_free()
	if unit.kind == "core" and winner == "":
		winner = "red" if unit.team == "blue" else "blue"
		match_ended.emit(winner)


func towers_standing(team: String) -> int:
	var count := 0
	for unit in units:
		if unit.team == team and unit.kind == "tower":
			count += 1
	return count


## The closest enemy of the given unit that can be hit, within reach of its edge, or null.
func nearest_enemy(of: Node2D, reach: float) -> Node2D:
	var best: Node2D = null
	var best_distance := INF
	for other in units:
		if other.team == of.team or not other.can_be_hit():
			continue
		var distance: float = of.global_position.distance_to(other.global_position) - other.radius()
		if distance <= reach and distance < best_distance:
			best = other
			best_distance = distance
	return best
