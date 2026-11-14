extends Node
## Sends a wave of lane units down every lane from each team's core on a timer.

const MobaUnit := preload("res://scripts/moba/moba_unit.gd")

@export var first_wave_at := 1.0
@export var wave_interval := 30.0
@export var wave_size := 3
## Gap between units of one wave as they leave the core.
@export var spacing := 14.0
## A check can leave a team out to test a lane being pushed.
@export var teams := PackedStringArray(["blue", "red"])

var waves_sent := {"blue": 0, "red": 0}
var _next_wave := 0.0

@onready var arena: Node2D = get_parent()


func _ready() -> void:
	_next_wave = first_wave_at


func advance(_delta: float) -> void:
	if arena.elapsed < _next_wave:
		return
	_next_wave += wave_interval
	for lane_name in arena.lanes:
		var points: PackedVector2Array = arena.lanes[lane_name]
		for team in teams:
			var path := points.duplicate()
			if team == "red":
				path.reverse()
			var heading := (path[1] - path[0]).normalized()
			for i in wave_size:
				var unit := MobaUnit.new()
				unit.team = team
				unit.path = path
				unit.path_index = 1
				arena.spawn(unit, path[0] - heading * spacing * i)
			waves_sent[team] += 1
