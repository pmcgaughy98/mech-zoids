extends Node3D
## The dressed field with the gorilla in place of the rhino (Claude, 2026-11-04, game feel lane). Keys 1-4 are the
## gorilla's kit (ApeKit). One dummy stands in as an ally (blue) so hex shield and bound have someone to reach.
## The field itself is the map lane's scenes/moba3d/field_test.tscn, instanced untouched.

const FIELD := preload("res://scenes/moba3d/field_test.tscn")

@export var ally_dummy := "Dummy4"


func _ready() -> void:
	var field := FIELD.instantiate()
	add_child(field)
	ApeKit.install(field.get_node("Player"))
	var d := field.get_node_or_null(ally_dummy)
	if d != null:
		ApeKit.make_ally(d)
