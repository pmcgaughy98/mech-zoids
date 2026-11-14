extends Node3D
## Press play: the hummingbird in the field slice with its passive and first ability (hummingbird mech session,
## 2026-11-05; Preston: "Do the link slice"). The field's own controls move it; 1 fires the link needle at the mouse
## aim. Two wounded allies (blue, 300 of 600 health) and one enemy dummy stand in front of it; R puts the allies back
## to 300. The body is the approved standing still lifted off the ground, a stand-in until the hover redraw.
## Run: Godot --path . res://scenes/moba3d/hummingbird_test.tscn

const FIELD := preload("res://scenes/moba3d/field_test.tscn")
const KIT := preload("res://scripts/moba3d/hummingbird_kit.gd")
const ALLY := preload("res://scripts/moba3d/hummingbird_ally_dummy.gd")

var field: Node3D
var player ## machine_test_player.gd
var kit: KIT
var allies: Array[Node3D] = []
var _status: Label
var _link: Label
var _basic_cd := 0.0


func _ready() -> void:
	field = FIELD.instantiate()
	add_child(field)
	player = field.get_node("Player")
	kit = KIT.install(player)
	var f: Vector3 = kit.ahead()
	for spot in [["Ally A", f * 5.0], ["Ally B", f.rotated(Vector3.UP, deg_to_rad(-40.0)) * 6.0]]:
		var a: Node3D = ALLY.new()
		a.name = spot[0]
		field.add_child(a)
		a.global_position = player.global_position + spot[1]
		allies.append(a)
	var enemy := TrainingDummy.new()
	enemy.name = "Enemy"
	field.add_child(enemy)
	enemy.global_position = player.global_position + f.rotated(Vector3.UP, deg_to_rad(40.0)) * 5.0
	kit.needled.connect(_on_needled)
	_build_ui()


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k != null and k.pressed and not k.echo and k.physical_keycode == KEY_R:
		for a in allies:
			a.hp = 300.0


func _process(delta: float) -> void:
	# The field has no director, so this stands in for the match's basic attack input (arena_play.gd): Space or left
	# click held fires the beak shot every basic_cooldown while an enemy is in reach of the aim.
	_basic_cd = maxf(_basic_cd - delta, 0.0)
	if _basic_cd <= 0.0 and (Input.is_physical_key_pressed(KEY_SPACE) or Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)):
		if kit.basic_attack(null):
			_basic_cd = kit.basic_cooldown
	var t: Node3D = kit.link_target
	if t == null or not is_instance_valid(t):
		_link.text = "Link: none"
	else:
		var d: float = KIT.flat(t.global_position - player.global_position).length()
		_link.text = "Link: %s, %.1f m away (breaks past %d m), healing %d a second" % [
			t.name, d, int(kit.link_range), roundi(float(t.max_hp) * kit.link_heal_share)]


func _on_needled(target: Node3D, ally: bool) -> void:
	if target == null:
		_status.text = "Last needle: hit nothing"
	elif ally:
		_status.text = "Last needle: healed %s by %d and linked it" % [target.name, roundi(float(target.max_hp) * kit.needle_heal_share)]
	else:
		_status.text = "Last needle: hit %s for %d" % [target.name, roundi(MatchRules.kit_hit_damage * kit.needle_damage_scale)]


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var box := VBoxContainer.new()
	box.position = Vector2(16, 12)
	layer.add_child(box)
	var title := Label.new()
	title.text = "Hummingbird: 1 = link needle (aim with the mouse; first ally or enemy on the line within %d m)" % int(kit.needle_range)
	var hint := Label.new()
	hint.text = "Ally hit: healed and linked by the ruby beam. Enemy hit: damaged. R = allies back to 300 health"
	var basic := Label.new()
	basic.text = "Space or left click (hold) = beak shot: %d damage to the enemy nearest the aim within %d m, every %.1f s" % [
		roundi(kit.basic_damage), int(kit.basic_range), kit.basic_cooldown]
	_status = Label.new()
	_status.text = "Last needle: none yet"
	_link = Label.new()
	for l in [title, hint, basic, _status, _link]:
		l.add_theme_color_override("font_outline_color", Color.BLACK)
		l.add_theme_constant_override("outline_size", 6)
		box.add_child(l)
