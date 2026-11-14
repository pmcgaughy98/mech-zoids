extends Node3D
## The rhino's reveal clip (Claude, 2026-11-04; Preston: "show me like its a smite move reveal clip ... smite god
## reveal i mean"). The structure (a cold open, the name card, one card per ability with the ability in play, the
## ultimate last, an outro card) is the usual shape of a MOBA character reveal, from general knowledge, not from any
## one video. It runs the real field slice and kit (scripts/moba3d/rhino_kit.gd) on training dummies with a scripted
## camera. Card words are the kit doc's (docs/plan/moba-kits.md), lightly shortened; "NEW MACHINE" is a reveal label.
## Record: Godot --path . --resolution 1280x720 --fixed-fps 30 --write-movie <dir>/f.png res://scenes/moba3d/rhino_reveal.tscn

const FIELD := preload("res://scenes/moba3d/field_test.tscn")
const BOLT := preload("res://art/fx/moba3d/bolt.png")
const GOLD := Color("ffcf1f")
const PALE := Color("fff4a8")
const INK := Color("141218")
const PANEL := Color(0.129, 0.118, 0.153, 0.92)

var field: Node3D
var player ## machine_test_player.gd
var kit: RhinoKit
var cam: Camera3D
var clock := 0.0
var trauma := 0.0
var frame_shift := 0.0 ## metres the look point moves left, so the rhino sits right of the card
var _c_from := Vector3.ZERO
var _c_to := Vector3.ZERO
var _l_from := Vector3.ZERO
var _l_to := Vector3.ZERO
var _c_t := 0.0
var _c_dur := 1.0
var _c_follow := true
var _c_anchor := Vector3.ZERO
var _fade: ColorRect
var _bars: Array[ColorRect] = []
var _title: Control
var _card: Panel
var _card_slot: Label
var _card_tag: Label
var _card_name: Label
var _card_text: Label
var _outro: Control


func _ready() -> void:
	field = FIELD.instantiate()
	add_child(field)
	player = field.get_node("Player")
	kit = player.get_node("Kit")
	var chase: Camera3D = field.get_node("Camera")
	chase.set_process(false)
	chase.set_process_unhandled_input(false)
	cam = Camera3D.new()
	cam.fov = 50.0
	add_child(cam)
	cam.current = true
	player.input_override = Vector2.ZERO
	player.get_node("Ring").visible = false  # the player ring is for play, not for the reveal
	kit.impact.connect(_on_impact)
	_build_ui()
	_run()


func _on_impact(strength: float) -> void:
	trauma = minf(trauma + strength * 0.8, 1.0)


func _process(delta: float) -> void:
	clock += delta
	_c_t = minf(_c_t + delta, _c_dur)
	var k := smoothstep(0.0, 1.0, _c_t / _c_dur)
	var base: Vector3 = player.global_position if _c_follow else _c_anchor
	trauma = maxf(trauma - delta * 1.8, 0.0)
	var amp := trauma * trauma * 0.22
	var sh := Vector3(sin(clock * 71.0), sin(clock * 53.0 + 1.3), sin(clock * 61.0 + 2.1)) * amp
	var pos := base + _c_from.lerp(_c_to, k)
	var look := base + _l_from.lerp(_l_to, k)
	var right := (look - pos).cross(Vector3.UP)
	right.y = 0.0
	if right.length() > 0.01:
		look -= right.normalized() * frame_shift
	cam.global_position = pos + sh
	cam.look_at(look + sh * 0.4)


func _run() -> void:
	# Cold open: the rhino walks up the lane at the camera, out of black.
	stage(Vector3(0, 0, -5), Vector3(0, 0, 1))
	player.move_override = Vector3(0, 0, 0.6)
	shot(Vector3(1.4, 0.55, 4.4), Vector3(1.9, 0.8, 5.4), Vector3(0, 0.95, 0), Vector3(0, 1.0, 0), 4.4)
	bars_in()
	fade_to(0.0, 1.2)
	await at(4.4)
	player.move_override = null
	# Name card: it rears and pounds, and the name lands with the slam.
	shot(Vector3(1.2, 0.7, 4.6), Vector3(1.6, 0.9, 5.4), Vector3(0, 1.0, 0), Vector3(0, 1.1, 0), 4.6)
	await at(4.7)
	kit.ground_pound()
	await kit.impact
	show_title()
	await at(8.6)
	hide_title()

	await at(9.0)
	stage(Vector3.ZERO, Vector3(1, 0, 0))
	frame_shift = 1.4
	shot(Vector3(-1.4, 1.8, 6.4), Vector3(1.0, 2.0, 6.6), Vector3(0, 0.8, 0), Vector3(0, 0.8, 0), 6.5)
	show_card("P", "PASSIVE", "FRONT PLATING", "Takes less damage from hits that land on its front. Flanking it is the counter.")
	for e in [[10.0, 1.0, 0.1], [10.5, 1.0, -0.2], [11.0, 1.0, 0.05], [12.3, -1.0, 0.15], [12.9, -1.0, -0.1],
			[13.8, 1.0, 0.0], [14.2, 1.0, 0.25]]:
		await at(e[0])
		bolt(Vector3(e[1], 0.0, e[2]))
	await at(15.0)
	hide_card()

	await at(15.5)
	stage(Vector3.ZERO, Vector3(1, 0, 0))
	dummy(Vector3(2.1, 0, 0.1))
	shot(Vector3(0.6, 1.6, 6.6), Vector3(-0.4, 1.8, 6.8), Vector3(0.2, 1.1, 0), Vector3(-0.4, 1.3, 0), 3.6)
	show_card("1", "ABILITY 1", "HORN TOSS", "Flicks the first enemy in front up and over its back. It lands behind the rhino and is stunned on landing.")
	await at(16.2)
	kit.horn_toss()
	await at(19.0)
	stage(Vector3.ZERO, Vector3(1, 0, 0))  # again from behind, the way it plays
	dummy(Vector3(2.1, 0, -0.1))
	shot(Vector3(-6.0, 2.8, 1.4), Vector3(-6.4, 3.0, 0.9), Vector3(0.6, 0.9, 0), Vector3(0.3, 1.0, 0), 3.0)
	await at(19.4)
	kit.horn_toss()
	await at(21.7)
	hide_card()

	await at(22.0)
	stage(Vector3.ZERO, Vector3(1, 0, 0))  # side on, so the rear-up reads; dummies ahead and beyond, none in front of the lens
	for p in [Vector3(2.3, 0, 0.2), Vector3(1.7, 0, -1.3), Vector3(0.4, 0, -1.9), Vector3(-0.9, 0, -1.5),
			Vector3(2.0, 0, 1.0), Vector3(3.4, 0, -1.9)]:
		dummy(p)
	shot(Vector3(0.4, 3.6, 6.4), Vector3(-0.6, 4.0, 6.8), Vector3(0.6, 0.3, -0.2), Vector3(0.6, 0.3, -0.2), 6.5)
	show_card("2", "ABILITY 2", "GROUND POUND", "Rears up on its hind legs and slams down. The ring deals damage and slows; the cracks linger a moment as a slow patch.")
	await at(22.8)
	kit.ground_pound()
	await at(28.2)
	hide_card()

	await at(28.6)
	stage(Vector3.ZERO, Vector3(1, 0, 0))
	shot(Vector3(-0.8, 2.6, 6.0), Vector3(0.9, 2.8, 5.8), Vector3(0, 0.6, 0), Vector3(0.4, 0.6, 0), 6.5)
	show_card("3", "ABILITY 3", "BRACE", "Plants all four feet: less damage, no knockbacks or pulls, and it moves slowly. Ground pound still works while braced.")
	await at(29.2)
	kit.brace()
	for e in [[29.9, -1.0, 0.1], [30.3, 1.0, -0.1], [30.6, -1.0, -0.2]]:
		await at(e[0])
		bolt(Vector3(e[1], 0.0, e[2]))
	await at(30.8)
	player.move_override = Vector3(1, 0, 0)
	await at(31.5)
	player.move_override = null
	kit.ground_pound()
	await at(34.6)
	hide_card()

	await at(35.0)
	stage(Vector3(0, 0, 7), Vector3(0, 0, -1))
	for p in [Vector3(-0.4, 0, 3.6), Vector3(-0.7, 0, 1.2), Vector3(-0.3, 0, -1.4), Vector3(-1.0, 0, -7.0),
			Vector3(0.6, 0, -7.2), Vector3(-0.2, 0, -8.1)]:  # lane dummies sit left of the line, so the shove sends them away from the lens
		dummy(p)
	frame_shift = 0.8
	shot(Vector3(5.2, 1.7, 2.4), Vector3(4.8, 2.0, 1.2), Vector3(0, 1.0, -1.0), Vector3(0, 1.0, -1.6), 4.0)
	show_card("4", "ULTIMATE", "STAMPEDE", "A long charge that knocks every enemy in its path aside, ending in a heavy pound that stuns everyone in the ring.")
	await at(36.3)
	kit.stampede()
	await at(39.6)
	shot(Vector3(5.0, 2.4, -1.0), Vector3(6.0, 3.2, 2.0), Vector3(0, 0.6, -1.5), Vector3(0, 0.6, -1.5), 3.5)
	await at(43.5)
	hide_card()

	# Outro: it walks at the camera beside its card.
	await at(44.0)
	stage(Vector3.ZERO, Vector3(0, 0, 1))
	frame_shift = 0.0
	player.move_override = Vector3(0, 0, 0.35)
	shot(Vector3(0.4, 0.75, 5.6), Vector3(0.2, 0.85, 4.8), Vector3(-1.5, 1.0, 0), Vector3(-1.3, 1.05, 0), 6.0)
	_tw().tween_property(_outro, "modulate:a", 1.0, 0.6)
	await at(49.4)
	fade_to(1.0, 1.0)
	await at(50.6)
	get_tree().quit()


func shot(from: Vector3, to: Vector3, look_a: Vector3, look_b: Vector3, dur: float, follow := true) -> void:
	_c_from = from
	_c_to = to
	_l_from = look_a
	_l_to = look_b
	_c_t = 0.0
	_c_dur = dur
	_c_follow = follow
	_c_anchor = player.global_position


func at(t: float) -> void:
	while clock < t:
		await get_tree().process_frame


func stage(pos: Vector3, facing: Vector3) -> void:
	for d in get_tree().get_nodes_in_group("kit_target"):
		d.remove_from_group("kit_target")
		d.queue_free()
	player.global_position = pos
	player.facing = facing.normalized()
	player.move_override = null


func dummy(p: Vector3) -> Node3D:
	var d := TrainingDummy.new()
	field.add_child(d)
	d.global_position = p
	return d


## A hostile bolt flying in from a direction; it hits the rhino's plating or flank.
func bolt(from_dir: Vector3) -> void:
	var dir := Vector3(from_dir.x, 0.0, from_dir.z).normalized()
	var s := Sprite3D.new()
	s.texture = BOLT
	s.pixel_size = 0.02
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	s.shaded = false
	field.add_child(s)
	var start: Vector3 = player.global_position + dir * 7.0 + Vector3.UP * 1.0
	s.global_position = start
	var tw := s.create_tween()
	tw.tween_property(s, "global_position", player.global_position + dir * 1.0 + Vector3.UP * 0.95, 0.35)
	await tw.finished
	s.queue_free()
	kit.take_hit(start)


func _tw() -> Tween:
	return create_tween().set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)


func bars_in() -> void:
	var t := _tw().set_parallel()
	t.tween_property(_bars[0], "size:y", 16.0, 0.8)
	t.tween_property(_bars[1], "size:y", 16.0, 0.8)
	t.tween_property(_bars[1], "position:y", 164.0, 0.8)


func fade_to(a: float, time: float) -> void:
	_tw().tween_property(_fade, "color:a", a, time)


func show_title() -> void:
	_title.scale = Vector2(1.25, 1.25)
	var t := _tw().set_parallel()
	t.tween_property(_title, "modulate:a", 1.0, 0.18)
	t.tween_property(_title, "scale", Vector2.ONE, 0.35)


func hide_title() -> void:
	_tw().tween_property(_title, "modulate:a", 0.0, 0.4)


func show_card(slot: String, tag: String, title: String, text: String) -> void:
	_card_slot.text = slot
	_card_tag.text = tag
	_card_name.text = title
	_card_text.text = text
	_card.position.x = -200.0
	_card.modulate.a = 1.0
	_tw().tween_property(_card, "position:x", 8.0, 0.4)


func hide_card() -> void:
	_tw().tween_property(_card, "modulate:a", 0.0, 0.3)


func _font(weight: int) -> SystemFont:
	var f := SystemFont.new()
	f.font_names = PackedStringArray(["Bahnschrift", "Segoe UI", "Arial"])
	f.font_weight = weight
	return f


func _label(parent: Control, text: String, pos: Vector2, size: Vector2, font_size: int, color: Color, weight := 700,
		outline := 0, align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.size = size
	l.horizontal_alignment = align
	l.add_theme_font_override("font", _font(weight))
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	if outline > 0:
		l.add_theme_color_override("font_outline_color", INK)
		l.add_theme_constant_override("outline_size", outline)
	parent.add_child(l)
	return l


func _box(parent: Control, pos: Vector2, size: Vector2, bg: Color, border := Color.TRANSPARENT, left := 0, all := 0) -> Panel:
	var p := Panel.new()
	p.position = pos
	p.size = size
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(all)
	if left > 0:
		sb.border_width_left = left
	p.add_theme_stylebox_override("panel", sb)
	parent.add_child(p)
	return p


## Cards are laid out on the project's 320x180 canvas, so every edge is a whole number of screen pixels.
func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var root := Control.new()
	root.size = Vector2(320, 180)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	for y in [0.0, 180.0]:
		var b := ColorRect.new()
		b.color = INK
		b.position = Vector2(0, y)
		b.size = Vector2(320, 0)
		root.add_child(b)
		_bars.append(b)
	_title = Control.new()
	_title.size = Vector2(320, 180)
	_title.pivot_offset = Vector2(160, 84)
	_title.modulate.a = 0.0
	root.add_child(_title)
	_label(_title, "NEW MACHINE", Vector2(0, 44), Vector2(320, 12), 8, GOLD, 700, 2, HORIZONTAL_ALIGNMENT_CENTER)
	_label(_title, "RHINO", Vector2(0, 52), Vector2(320, 48), 40, PALE, 700, 4, HORIZONTAL_ALIGNMENT_CENTER)
	var bar := ColorRect.new()
	bar.color = GOLD
	bar.position = Vector2(118, 103)
	bar.size = Vector2(84, 2)
	_title.add_child(bar)
	_label(_title, "ENGAGE TANK", Vector2(0, 107), Vector2(320, 14), 11, PALE, 700, 2, HORIZONTAL_ALIGNMENT_CENTER)
	_card = _box(root, Vector2(-200, 97), Vector2(178, 67), PANEL, GOLD, 3)
	var badge := _box(_card, Vector2(9, 8), Vector2(24, 24), GOLD, INK, 0, 1)
	_card_slot = _label(badge, "", Vector2(0, 1), Vector2(24, 22), 15, INK, 800, 0, HORIZONTAL_ALIGNMENT_CENTER)
	_card_tag = _label(_card, "", Vector2(40, 4), Vector2(130, 9), 6, GOLD)
	_card_name = _label(_card, "", Vector2(40, 11), Vector2(134, 16), 13, PALE, 700, 1)
	_card_text = _label(_card, "", Vector2(9, 35), Vector2(164, 30), 7, Color(0.9, 0.9, 0.92), 400)
	_card_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_outro = Control.new()
	_outro.size = Vector2(320, 180)
	_outro.modulate.a = 0.0
	root.add_child(_outro)
	_label(_outro, "RHINO", Vector2(14, 24), Vector2(150, 40), 34, PALE, 700, 3)
	_label(_outro, "ENGAGE TANK", Vector2(16, 64), Vector2(150, 14), 10, GOLD, 700, 2)
	var rows := [["P", "FRONT PLATING"], ["1", "HORN TOSS"], ["2", "GROUND POUND"], ["3", "BRACE"], ["4", "STAMPEDE"]]
	for i in rows.size():
		var y := 84.0 + i * 14.0
		var b := _box(_outro, Vector2(16, y), Vector2(12, 12), GOLD, INK, 0, 1)
		_label(b, rows[i][0], Vector2(0, 0), Vector2(12, 12), 8, INK, 800, 0, HORIZONTAL_ALIGNMENT_CENTER)
		_label(_outro, rows[i][1], Vector2(33, y - 1), Vector2(130, 14), 9, PALE, 700, 2)
	_fade = ColorRect.new()
	_fade.color = Color.BLACK
	_fade.size = Vector2(320, 180)
	root.add_child(_fade)
