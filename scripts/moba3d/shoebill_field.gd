extends Node3D
## The dressed field with the shoebill's kit on the field's Player (Claude, 2026-11-05, Shoebill session). The body is
## a stand-in until the shoebill's 35-degree frames exist. Stand still to fill the moon disc (three phases), 1 is
## moonbeam, Space or a left click is the basic attack (lens flick). The field itself is the map lane's
## scenes/moba3d/field_test.tscn, instanced untouched.

const FIELD := preload("res://scenes/moba3d/field_test.tscn")
const KIT := preload("res://scripts/moba3d/shoebill_kit.gd")

var kit: Node ## shoebill_kit.gd
var player: Node3D
var _basic_cd := 0.0


func _ready() -> void:
	var field := FIELD.instantiate()
	add_child(field)
	player = field.get_node("Player")
	kit = KIT.install(player)


func _process(delta: float) -> void:
	_basic_cd = maxf(0.0, _basic_cd - delta)


## Outside a match there is no director, so the field keeps the basic attack's cooldown itself.
func _unhandled_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	var b := event as InputEventMouseButton
	var key_hit := k != null and k.pressed and not k.echo and k.physical_keycode == KEY_SPACE
	var click := b != null and b.pressed and b.button_index == MOUSE_BUTTON_LEFT
	if (key_hit or click) and _basic_cd <= 0.0 and not player.busy and kit.basic_attack(null):
		_basic_cd = kit.basic_cooldown
