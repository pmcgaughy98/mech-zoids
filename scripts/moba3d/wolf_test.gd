extends Node3D
## Press play: the wolf in the field slice with its first ability (wolf mech session, 2026-11-05; Preston: "Lunge in
## the match"). The field's own controls walk it; 1 lunges at the nearest dummy within 6 m and bites. One extra dummy
## stands 4 m ahead so the first press has a target. The wolf's frames are its accepted 35-degree stills (WolfKit).
## Run: Godot --path . res://scenes/moba3d/wolf_test.tscn

const FIELD := preload("res://scenes/moba3d/field_test.tscn")

var field: Node3D
var player ## machine_test_player.gd
var kit: WolfKit
var _status: Label


func _ready() -> void:
	field = FIELD.instantiate()
	add_child(field)
	player = field.get_node("Player")
	kit = WolfKit.install(player)
	var d := TrainingDummy.new()
	field.add_child(d)
	d.global_position = player.global_position + kit.ahead() * 4.0
	kit.bit.connect(_on_bit)
	_build_ui()


func _on_bit(target: Node3D, wounded: bool) -> void:
	if target == null:
		_status.text = "Last lunge: nothing in range, bit the air"
	else:
		_status.text = "Last lunge: bit %s%s" % [target.name, " (wounded: cooldown cut)" if wounded else ""]


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var box := VBoxContainer.new()
	box.position = Vector2(16, 12)
	layer.add_child(box)
	var title := Label.new()
	title.text = "Wolf: 1 = lunge (leaps at the nearest dummy within %d m and bites)" % int(kit.lunge_range)
	box.add_child(title)
	_status = Label.new()
	_status.text = "Last lunge: none yet"
	box.add_child(_status)
	for l in [title, _status]:
		l.add_theme_color_override("font_outline_color", Color.BLACK)
		l.add_theme_constant_override("outline_size", 6)
