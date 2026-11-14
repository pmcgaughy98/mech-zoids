extends Node3D
## The fennec's reveal clip (Claude, 2026-11-04, game feel lane; Preston: "Do fennec reveal"). Same shape as the
## gorilla's (scripts/moba3d/ape_reveal.gd): a cold open, the name card on a landing, one card per ability with the
## ability in play, the ultimate last, an outro card. It runs the real field slice and the fennec's kit
## (scripts/moba3d/fennec_kit.gd) on training dummies (the blue ones are allies) with a scripted camera. Card words are
## the kit doc's (docs/plan/moba-kits.md, Fennec), lightly shortened; "NEW MACHINE" is a reveal label.
## The fennec walks at the kit's placeholder speed (FennecKit.walk_speed) with the trot played faster to keep its
## feet planted; the number is Preston's.
## Record: Godot --path . --resolution 1280x720 --fixed-fps 30 --position 20000,20000
##         --write-movie <dir>/f.png res://scenes/moba3d/fennec_reveal.tscn

const FIELD := preload("res://scenes/moba3d/field_test.tscn")
const ACCENT := Color("78e8e2") ## the fennec's eye cyan, which its sound effects use
const PALE := Color("eafcff")
const INK := Color("141218")
const PANEL := Color(0.129, 0.118, 0.153, 0.92)

var field: Node3D
var player ## machine_test_player.gd
var kit: FennecKit
var cam: Camera3D
var clock := 0.0
var trauma := 0.0
var frame_shift := 0.0 ## metres the look point moves left, so the fennec sits right of the card
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
	kit = FennecKit.install(player)
	var chase: Camera3D = field.get_node("Camera")
	chase.set_process(false)
	chase.set_process_unhandled_input(false)
	cam = Camera3D.new()
	cam.fov = 50.0
	add_child(cam)
	cam.current = true
	player.input_override = Vector2.ZERO
	player.get_node("Ring").visible = false  # the team ring is for play
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
	var amp := trauma * trauma * 0.16
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
	# Cold open: the fennec trots up the lane at the camera, out of black.
	stage(Vector3(0, 0, -2.4), Vector3(0, 0, 1))
	player.move_override = Vector3(0, 0, 1)
	shot(Vector3(0.9, 0.4, 3.0), Vector3(1.2, 0.5, 3.6), Vector3(0, 0.6, 0), Vector3(0, 0.65, 0), 4.0)
	bars_in()
	fade_to(0.0, 1.2)
	await at(3.8)
	player.move_override = null
	# Name card: it digs in and comes up right at the lens; the name lands with it.
	var exit: Vector3 = player.global_position + Vector3(0.4, 0, 2.6)
	shot_at(exit, Vector3(0.6, 0.65, 4.8), Vector3(0.8, 0.7, 5.1), Vector3(0, 1.65, 0), Vector3(0, 1.68, 0), 4.8)  # low, under the name
	await at(4.0)
	kit.tunnel(exit)
	await kit.impact
	show_title()
	await at(6.6)
	kit.ear_burst(exit + Vector3(-2.6, 0, -1.2))
	await at(8.6)
	hide_title()

	# The ability shots stand on the grass west of the lane (G), where the sand and the sound rings read. Each camera
	# was placed with a projection of the shot (fennec and dummies against the card, 2026-11-04) and then checked in
	# the recording: the fennec sits right of the card or above it.
	var g := Vector3(-6.0, 0, 4.0)
	await at(9.0)
	stage(g, Vector3(-1, 0, 0))  # listening toward the enemies coming round
	frame_shift = 1.3
	shot(Vector3(2.0, 2.6, 3.6), Vector3(2.2, 2.7, 3.9), Vector3(-1.6, 0.3, -1.6), Vector3(-1.6, 0.3, -1.7), 6.5)
	show_card("P", "PASSIVE", "BIG EARS", "Enemies moving near it show up as sound pings, even in fog or camouflage.")
	var walkers := [dummy(g + Vector3(-3.6, 0, -2.4)), dummy(g + Vector3(-5.0, 0, -0.6)), dummy(g + Vector3(-1.6, 0, -4.6))]
	dummy(g + Vector3(-3.0, 0, -1.2))  # standing still: no ping
	await at(9.6)
	walkers[0].walk_to(g + Vector3(-4.8, 0, -1.4), 2.6)
	walkers[1].walk_to(g + Vector3(-3.8, 0, 0.0), 2.6)
	walkers[2].walk_to(g + Vector3(-0.6, 0, -3.8), 2.6)
	await at(12.4)
	walkers[0].walk_to(g + Vector3(-3.4, 0, -2.8), 2.4)
	walkers[1].walk_to(g + Vector3(-5.2, 0, -1.0), 2.4)
	walkers[2].walk_to(g + Vector3(-2.0, 0, -4.8), 2.4)
	await at(15.0)
	hide_card()

	await at(15.5)
	stage(g, Vector3(1, 0, 0))  # the side view, where the paw's throw reads
	frame_shift = 2.9
	var kicked := [dummy(g + Vector3(1.8, 0, -1.0)), dummy(g + Vector3(2.4, 0, -0.4)), dummy(g + Vector3(1.6, 0, 0.1))]
	shot(Vector3(1.6, 1.6, 5.0), Vector3(1.8, 1.7, 5.2), Vector3(1.6, 0.6, -0.4), Vector3(1.6, 0.6, -0.4), 6.0)
	show_card("1", "ABILITY 1", "SAND KICK", "Kicks a spray of sand in a cone: damage and a slow.")
	await at(16.0)
	kit.sand_kick()
	await at(17.8)
	for d in kicked:
		d.walk_to(d.global_position - Vector3(0.5, 0, 0), 1.0)  # slowed, they edge in again
	await at(18.9)
	kit.sand_kick()
	await at(21.5)
	hide_card()

	await at(22.0)
	stage(g, Vector3(0, 0, -1))  # from behind: the ears, then the burst out past them
	frame_shift = 1.8  # takes 2 and 3 had it on the card edge
	for p in [Vector3(-0.8, 0, -4.4), Vector3(-0.3, 0, -4.9), Vector3(-1.4, 0, -5.0), Vector3(2.4, 0, -4.2), Vector3(3.1, 0, -4.6)]:
		dummy(g + p)
	shot(Vector3(-1.8, 2.7, 3.7), Vector3(-2.0, 2.8, 4.0), Vector3(0.8, 0.2, -3.6), Vector3(0.8, 0.2, -3.6), 6.0)
	show_card("2", "ABILITY 2", "EAR BURST", "A burst of sound at a target spot. More damage at the centre.")
	await at(22.6)
	kit.ear_burst(g + Vector3(-0.8, 0, -4.7))
	await at(25.0)
	kit.ear_burst(g + Vector3(2.7, 0, -4.4))
	await at(27.8)
	hide_card()

	await at(28.3)
	var exit_t := g + Vector3(1.0, 0, -6.0)
	stage(g, exit_t - g)
	frame_shift = 1.8  # take 2 had the entrance on the card's edge
	var ally := dummy(g + Vector3(0.4, 0, -2.8), true)
	shot_at(g + Vector3(0.5, 0, -3.0), Vector3(-2.6, 3.4, 6.4), Vector3(-2.8, 3.5, 6.7), Vector3(0.6, 0, -0.6), Vector3(0.6, 0, -0.6), 6.5)
	show_card("3", "ABILITY 3", "TUNNEL", "Digs an entrance here and an exit far away. It and its allies can travel through for a few seconds.")
	await at(28.8)
	kit.tunnel(exit_t)
	await at(30.8)
	ally.walk_to(g, 1.0)  # into the entrance: it comes up by the exit
	await at(34.6)
	hide_card()

	await at(35.0)
	var dir := Vector3(0.6, 0, 1.0).normalized()  # toward the lens and right: the open mouth reads, the cone fans down
	var side := Vector3(-dir.z, 0, dir.x)
	stage(g, dir)
	frame_shift = 0.8
	for p in [dir * 2.0 + side * 0.3, dir * 3.0 - side * 0.9, dir * 3.6 + side * 1.4, dir * 4.6 - side * 0.2]:
		dummy(g + p)
	shot(Vector3(-1.4, 6.0, 7.0), Vector3(-1.6, 6.2, 7.4), Vector3(1.4, 0, 2.0), Vector3(1.4, 0, 2.0), 4.0)
	show_card("4", "ULTIMATE", "SONIC BOOM", "After a short charge, blasts a huge cone of sound: heavy damage and a knockback.")
	await at(35.6)
	kit.sonic_boom()
	await at(39.0)
	stage(g, Vector3(0, 0, -1))  # again from behind: the wave racing away
	frame_shift = 1.8  # take 3 had it under the card edge
	for p in [Vector3(1.3, 0, -3.4), Vector3(-0.6, 0, -4.0), Vector3(1.5, 0, -4.8), Vector3(0.0, 0, -5.6), Vector3(-1.8, 0, -5.4)]:
		dummy(g + p)
	shot(Vector3(-1.8, 2.9, 3.7), Vector3(-2.0, 3.0, 4.0), Vector3(0.6, 0.3, -3.6), Vector3(0.6, 0.3, -3.6), 3.6)
	await at(39.3)
	kit.sonic_boom()
	await at(42.6)
	hide_card()

	# Outro: it trots at the camera beside its card.
	await at(43.0)
	stage(Vector3.ZERO, Vector3(0, 0, 1))
	frame_shift = 0.0
	player.move_override = Vector3(0, 0, 1)
	shot(Vector3(0.3, 0.5, 3.6), Vector3(0.15, 0.55, 3.0), Vector3(-1.0, 0.65, 0), Vector3(-0.9, 0.7, 0), 6.0)
	_tw().tween_property(_outro, "modulate:a", 1.0, 0.6)
	await at(48.4)
	fade_to(1.0, 1.0)
	await at(49.6)
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


## A shot held on a fixed spot (the camera does not follow the fennec), for moves across the frame.
func shot_at(anchor: Vector3, from: Vector3, to: Vector3, look_a: Vector3, look_b: Vector3, dur: float) -> void:
	shot(from, to, look_a, look_b, dur, false)
	_c_anchor = anchor


func at(t: float) -> void:
	while clock < t:
		await get_tree().process_frame


func stage(pos: Vector3, facing: Vector3) -> void:
	_clear_group("kit_target")
	_clear_group("kit_ally")
	kit._close_tunnel()
	player.global_position = pos
	player.facing = facing.normalized()
	player.move_override = null


func _clear_group(g: String) -> void:
	for d in get_tree().get_nodes_in_group(g):
		d.remove_from_group(g)
		d.queue_free()


func dummy(p: Vector3, ally := false) -> Node3D:
	var d := TrainingDummy.new()
	field.add_child(d)
	d.global_position = p
	if ally:
		ApeKit.make_ally(d)
	return d


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
	_title.pivot_offset = Vector2(160, 58)
	_title.modulate.a = 0.0
	root.add_child(_title)
	_label(_title, "NEW MACHINE", Vector2(0, 19), Vector2(320, 12), 8, ACCENT, 700, 2, HORIZONTAL_ALIGNMENT_CENTER)
	_label(_title, "FENNEC", Vector2(0, 27), Vector2(320, 48), 40, PALE, 700, 4, HORIZONTAL_ALIGNMENT_CENTER)
	var bar := ColorRect.new()
	bar.color = ACCENT
	bar.position = Vector2(110, 78)
	bar.size = Vector2(100, 2)
	_title.add_child(bar)
	_label(_title, "CONTROL MAGE", Vector2(0, 82), Vector2(320, 14), 11, PALE, 700, 2, HORIZONTAL_ALIGNMENT_CENTER)
	_card = _box(root, Vector2(-200, 97), Vector2(178, 67), PANEL, ACCENT, 3)
	var badge := _box(_card, Vector2(9, 8), Vector2(24, 24), ACCENT, INK, 0, 1)
	_card_slot = _label(badge, "", Vector2(0, 1), Vector2(24, 22), 15, INK, 800, 0, HORIZONTAL_ALIGNMENT_CENTER)
	_card_tag = _label(_card, "", Vector2(40, 4), Vector2(130, 9), 6, ACCENT)
	_card_name = _label(_card, "", Vector2(40, 11), Vector2(134, 16), 13, PALE, 700, 1)
	_card_text = _label(_card, "", Vector2(9, 35), Vector2(164, 30), 7, Color(0.9, 0.9, 0.92), 400)
	_card_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_outro = Control.new()
	_outro.size = Vector2(320, 180)
	_outro.modulate.a = 0.0
	root.add_child(_outro)
	_label(_outro, "FENNEC", Vector2(14, 24), Vector2(200, 40), 34, PALE, 700, 3)
	_label(_outro, "CONTROL MAGE", Vector2(16, 64), Vector2(170, 14), 10, ACCENT, 700, 2)
	var rows := [["P", "BIG EARS"], ["1", "SAND KICK"], ["2", "EAR BURST"], ["3", "TUNNEL"], ["4", "SONIC BOOM"]]
	for i in rows.size():
		var y := 84.0 + i * 14.0
		var b := _box(_outro, Vector2(16, y), Vector2(12, 12), ACCENT, INK, 0, 1)
		_label(b, rows[i][0], Vector2(0, 0), Vector2(12, 12), 8, INK, 800, 0, HORIZONTAL_ALIGNMENT_CENTER)
		_label(_outro, rows[i][1], Vector2(33, y - 1), Vector2(130, 14), 9, PALE, 700, 2)
	_fade = ColorRect.new()
	_fade.color = Color.BLACK
	_fade.size = Vector2(320, 180)
	root.add_child(_fade)
