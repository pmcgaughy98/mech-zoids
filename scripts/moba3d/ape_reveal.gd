extends Node3D
## The gorilla's reveal clip (Claude, 2026-11-04, game feel lane; Preston: "Now run gorillas reveal"). Same shape as
## the rhino's (scripts/moba3d/rhino_reveal.gd): a cold open, the name card on a big landing, one card per ability with
## the ability in play, the ultimate last, an outro card. It runs the real field slice and the gorilla's kit
## (scripts/moba3d/ape_kit.gd) on training dummies (the blue ones are allies) with a scripted camera. Card words are
## the kit doc's (docs/plan/moba-kits.md, Gorilla), lightly shortened; "NEW MACHINE" is a reveal label.
## Record: Godot --path . --resolution 1280x720 --fixed-fps 30 --position 20000,20000
##         --write-movie <dir>/f.png res://scenes/moba3d/ape_reveal.tscn

const FIELD := preload("res://scenes/moba3d/field_test.tscn")
const BOLT := preload("res://art/fx/moba3d/bolt.png")
const ACCENT := Color("3fe07f") ## the hex shields' green (art/fx/moba3d/hex_tile.png)
const PALE := Color("eafff0")
const INK := Color("141218")
const PANEL := Color(0.129, 0.118, 0.153, 0.92)

var field: Node3D
var player ## machine_test_player.gd
var kit: ApeKit
var cam: Camera3D
var clock := 0.0
var trauma := 0.0
var frame_shift := 0.0 ## metres the look point moves left, so the gorilla sits right of the card
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
	kit = ApeKit.install(player)
	var chase: Camera3D = field.get_node("Camera")
	chase.set_process(false)
	chase.set_process_unhandled_input(false)
	cam = Camera3D.new()
	cam.fov = 50.0
	add_child(cam)
	cam.current = true
	player.input_override = Vector2.ZERO
	player.get_node("Ring").visible = false  # the team ring is for play; the green silverback ring stays
	kit.shake_camera = false  # this reveal shakes its own camera on impact; the kit's match shake would double it
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
	# Cold open: the gorilla knuckle-walks up the lane at the camera, out of black.
	stage(Vector3(0, 0, -5), Vector3(0, 0, 1))
	player.move_override = Vector3(0, 0, 0.6)
	shot(Vector3(1.4, 0.55, 4.4), Vector3(1.9, 0.8, 5.4), Vector3(0, 0.95, 0), Vector3(0, 1.0, 0), 4.0)
	bars_in()
	fade_to(0.0, 1.2)
	await at(3.8)
	player.move_override = null
	# Name card: it bounds at the lens, the name lands with the landing, then it beats its chest.
	var land: Vector3 = player.global_position + Vector3(0, 0, kit.bound_distance)
	shot_at(land, Vector3(0.9, 0.7, 4.4), Vector3(1.3, 0.8, 4.9), Vector3(0, 1.6, 0), Vector3(0, 1.65, 0), 4.8)  # low, so it lands under the name
	await at(4.1)
	kit.bound()
	await kit.impact
	show_title()
	await at(5.9)
	kit.chest_beat()
	await at(8.6)
	hide_title()

	await at(9.0)
	stage(Vector3.ZERO, Vector3(1, 0, 0))
	frame_shift = 2.0
	shot(Vector3(-0.6, 2.6, 6.0), Vector3(0.6, 2.8, 6.2), Vector3(0.6, 0.6, -0.4), Vector3(0.6, 0.6, -0.4), 6.5)  # high enough to see the ring
	show_card("P", "PASSIVE", "SILVERBACK", "Allies standing near the gorilla take a little less damage.")
	var ally := dummy(Vector3(1.4, 0, -0.6), true)
	for e in [[10.0, Vector3(-1, 0, -0.4)], [10.6, Vector3(0.3, 0, -1)], [11.2, Vector3(1, 0, -0.7)]]:
		await at(e[0])
		bolt(e[1], ally)
	await at(12.0)
	_tw().tween_property(ally, "global_position", Vector3(3.2, 0, -1.4), 0.6)  # it steps out of the ring
	for e in [[13.0, Vector3(0.3, 0, -1)], [13.6, Vector3(1, 0, -0.3)], [14.2, Vector3(0.6, 0, -1)]]:
		await at(e[0])
		bolt(e[1], ally)
	await at(15.0)
	hide_card()

	await at(15.5)
	stage(Vector3.ZERO, Vector3(1, 0, 0))
	frame_shift = 3.2  # the gorilla's left side cleared the card only at 2.4 (contact sheet, 2026-11-04)
	ally = dummy(Vector3(2.0, 0, -1.4), true)
	ally.slowed = 8.0  # slowed (purple) until the shield clears it
	shot(Vector3(-1.0, 1.5, 4.6), Vector3(-0.4, 1.6, 5.0), Vector3(1.4, 0.9, 0), Vector3(1.6, 0.9, 0), 6.5)
	show_card("1", "ABILITY 1", "HEX SHIELD", "Throws a green hex shield onto an ally or itself. It absorbs damage and clears one slow or root.")
	await at(16.0)
	kit.hex_shield()
	for e in [[17.4, Vector3(1, 0, -0.5)], [17.9, Vector3(0.6, 0, -1)], [18.4, Vector3(1, 0, 0.1)]]:
		await at(e[0])
		bolt(e[1], ally)
	await at(19.0)
	_clear_group("kit_ally")
	await at(19.2)
	kit.hex_shield()  # no ally in range: it shields itself
	for e in [[20.3, Vector3(1, 0, 0.2)], [20.7, Vector3(-1, 0, -0.2)], [21.1, Vector3(0.5, 0, -1)]]:
		await at(e[0])
		bolt(e[1], player)
	await at(21.8)
	hide_card()

	await at(22.2)
	stage(Vector3.ZERO, Vector3(0, 0, 1))  # facing the lens, so both fists read
	frame_shift = 2.0
	for p in [Vector3(2.2, 0, -0.3), Vector3(-2.2, 0, -0.5), Vector3(1.1, 0, -2.3), Vector3(-1.3, 0, -2.1),
			Vector3(2.4, 0, -1.6), Vector3(3.6, 0, -2.6)]:  # none in front of it; the last stands outside the reach
		dummy(p)
	shot(Vector3(0.6, 2.4, 6.6), Vector3(-0.2, 2.6, 7.0), Vector3(0, 0.9, -0.4), Vector3(0, 0.9, -0.4), 6.0)
	show_card("2", "ABILITY 2", "CHEST BEAT", "Beats its chest. Enemies close around it are taunted, forced to attack the gorilla, for a moment.")
	await at(22.9)
	kit.chest_beat()
	await at(25.3)
	kit.chest_beat()
	await at(28.0)
	hide_card()

	await at(28.4)
	stage(Vector3.ZERO, Vector3(1, 0, 0))
	frame_shift = 4.0  # the whole leap plays right of the card
	dummy(Vector3(5.0, 0, 0.2), true)
	for p in [Vector3(4.4, 0, -1.1), Vector3(5.4, 0, -0.4), Vector3(3.6, 0, 0.9)]:
		dummy(p)
	shot_at(Vector3(2.2, 0, 0), Vector3(0.0, 2.6, 10.5), Vector3(0.3, 2.8, 10.8), Vector3(0, 1.0, 0), Vector3(0.15, 1.0, 0), 3.4)
	show_card("3", "ABILITY 3", "BOUND", "Leaps to an ally or a nearby spot. The landing knocks enemies back.")
	await at(29.0)
	kit.bound()
	await at(31.6)
	stage(Vector3.ZERO, Vector3(1, 0, 0))  # again from behind, the way it plays: no ally, so a leap straight ahead
	for p in [Vector3(5.6, 0, 0.7), Vector3(5.4, 0, -0.9), Vector3(6.4, 0, 0.1)]:
		dummy(p)
	frame_shift = 0.6
	shot(Vector3(-6.0, 2.8, 1.4), Vector3(-6.4, 3.0, 0.9), Vector3(0.6, 0.9, 0), Vector3(0.3, 1.0, 0), 3.0)
	await at(32.0)
	kit.bound()
	await at(34.6)
	hide_card()

	await at(35.0)
	stage(Vector3.ZERO, Vector3(0, 0, 1))
	frame_shift = 3.4  # the dome stands right of the card
	var guarded := [player, dummy(Vector3(1.3, 0, -1.2), true), dummy(Vector3(-1.5, 0, -0.6), true)]
	var caught = dummy(Vector3(2.1, 0, 0.0))  # an enemy inside when the dome rises: trapped (Preston, 2026-11-04)
	var shooters := [Vector3(4.6, 0, -4.6), Vector3(1.0, 0, -7.2), Vector3(-2.6, 0, -6.6), Vector3(-5.6, 0, -2.4)]
	for p in shooters:
		dummy(p)
	shot(Vector3(0.4, 3.6, 8.0), Vector3(-0.4, 4.0, 8.6), Vector3(0, 1.0, -0.8), Vector3(0, 1.2, -0.8), 4.6)
	show_card("4", "ULTIMATE", "HEX DOME", "Raises a dome of green hex panels for a few seconds. Enemies inside are trapped; allies inside take less damage and can walk out. Shots from outside stop at the wall.")
	await at(35.8)
	kit.hex_dome()
	# The dome is up from about 36.8 to 40.8 (hex_dome f5, then dome_time).
	# The trap beats play behind and right of the gorilla, where this angle sees them above the card.
	await at(37.3)
	caught.walk_to(Vector3(3.4, 0, -3.6), 0.9)  # tries to run; stops at the wall
	await at(37.6)
	bolt_from(shooters[0], player)
	await at(37.9)
	guarded[2].walk_to(Vector3(-1.6, 0, -6.2), 1.4)  # an ally walks out through the back wall
	await at(38.2)
	bolt_from(shooters[1], guarded[1])
	await at(38.6)
	bolt_from(shooters[2], player)
	await at(38.9)
	caught.walk_to(Vector3(3.8, 0, -0.2), 0.7)  # tries the other side; the wall holds again
	await at(39.3)
	shot(Vector3(-7.0, 3.0, 3.0), Vector3(-6.2, 3.6, 5.0), Vector3(0, 1.0, 0), Vector3(0, 1.1, 0), 3.7)
	for v in [[39.6, 3, 1], [40.1, 0, 0]]:
		await at(v[0])
		bolt_from(shooters[v[1]], guarded[v[2]])
	await at(41.3)
	caught.walk_to(Vector3(5.5, 0, 3.5), 1.0)  # the dome is gone, so it gets away
	await at(43.0)
	hide_card()

	# Outro: it walks at the camera beside its card.
	await at(43.4)
	stage(Vector3.ZERO, Vector3(0, 0, 1))
	frame_shift = 0.0
	player.move_override = Vector3(0, 0, 0.35)
	shot(Vector3(0.4, 0.75, 5.6), Vector3(0.2, 0.85, 4.8), Vector3(-1.5, 1.0, 0), Vector3(-1.3, 1.05, 0), 6.0)
	_tw().tween_property(_outro, "modulate:a", 1.0, 0.6)
	await at(48.8)
	fade_to(1.0, 1.0)
	await at(50.0)
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


## A shot held on a fixed spot (the camera does not follow the gorilla), for leaps across the frame.
func shot_at(anchor: Vector3, from: Vector3, to: Vector3, look_a: Vector3, look_b: Vector3, dur: float) -> void:
	shot(from, to, look_a, look_b, dur, false)
	_c_anchor = anchor


func at(t: float) -> void:
	while clock < t:
		await get_tree().process_frame


func stage(pos: Vector3, facing: Vector3) -> void:
	_clear_group("kit_target")
	_clear_group("kit_ally")
	var s := ApeKit.shield_on(player)
	if s != null:
		s.queue_free()
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


## A hostile bolt flying in at a machine from a direction.
func bolt(from_dir: Vector3, target: Node3D) -> void:
	var dir := Vector3(from_dir.x, 0.0, from_dir.z).normalized()
	bolt_from(target.global_position + dir * 7.0, target)


## A hostile bolt from a spot at a machine. A dome around the target stops it at the wall; a hex shield takes it; an
## ally inside the silverback ring takes it lighter (a deflect spark and a green pulse); anything else takes the hit.
func bolt_from(from: Vector3, target: Node3D) -> void:
	if not is_instance_valid(target):
		return
	var dir := ApeKit.flat(from - target.global_position).normalized()
	var start := Vector3(from.x, 1.0, from.z)
	var wall := kit.dome_at(target.global_position)
	if wall != null and kit.dome_at(start) == wall:
		wall = null
	var end: Vector3 = target.global_position + dir * (1.0 if target == player else 0.5) + Vector3.UP * 0.95
	if wall != null:
		var r := sqrt(maxf(wall.radius * wall.radius - 0.81, 0.0))
		end = wall.global_position + dir * r + Vector3.UP * 0.9
	var s := Sprite3D.new()
	s.texture = BOLT
	s.pixel_size = 0.02
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	s.shaded = false
	field.add_child(s)
	s.global_position = start
	var tw := s.create_tween()
	tw.tween_property(s, "global_position", end, maxf(start.distance_to(end) / 18.0, 0.2))
	await tw.finished
	s.queue_free()
	if not is_instance_valid(target):
		return
	if target == player:
		kit.take_hit(start)
		return
	if wall != null:
		wall.hit()
		Fx3D.spawn(field, "deflect_spark", end, 0.3)
		trauma = minf(trauma + 0.1, 1.0)
	elif ApeKit.shield_on(target) != null:
		ApeKit.shield_on(target).hit()
		Fx3D.spawn(field, "deflect_spark", end, 0.3)
	elif target.is_in_group("kit_ally") and kit.covers(target):
		target.hit()
		Fx3D.spawn(field, "deflect_spark", end, 0.3)
		kit._pulse(target.global_position, 0.8, 0.25)
	else:
		target.hit()
		Fx3D.spawn(field, "hit_spark", end, 0.3)


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
	# Set higher than the rhino's: the gorilla lands low and wide, so the name sits above it instead of over it.
	_label(_title, "NEW MACHINE", Vector2(0, 19), Vector2(320, 12), 8, ACCENT, 700, 2, HORIZONTAL_ALIGNMENT_CENTER)
	_label(_title, "GORILLA", Vector2(0, 27), Vector2(320, 48), 40, PALE, 700, 4, HORIZONTAL_ALIGNMENT_CENTER)
	var bar := ColorRect.new()
	bar.color = ACCENT
	bar.position = Vector2(110, 78)
	bar.size = Vector2(100, 2)
	_title.add_child(bar)
	_label(_title, "PROTECTOR TANK", Vector2(0, 82), Vector2(320, 14), 11, PALE, 700, 2, HORIZONTAL_ALIGNMENT_CENTER)
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
	_label(_outro, "GORILLA", Vector2(14, 24), Vector2(200, 40), 34, PALE, 700, 3)
	_label(_outro, "PROTECTOR TANK", Vector2(16, 64), Vector2(170, 14), 10, ACCENT, 700, 2)
	var rows := [["P", "SILVERBACK"], ["1", "HEX SHIELD"], ["2", "CHEST BEAT"], ["3", "BOUND"], ["4", "HEX DOME"]]
	for i in rows.size():
		var y := 84.0 + i * 14.0
		var b := _box(_outro, Vector2(16, y), Vector2(12, 12), ACCENT, INK, 0, 1)
		_label(b, rows[i][0], Vector2(0, 0), Vector2(12, 12), 8, INK, 800, 0, HORIZONTAL_ALIGNMENT_CENTER)
		_label(_outro, rows[i][1], Vector2(33, y - 1), Vector2(130, 14), 9, PALE, 700, 2)
	_fade = ColorRect.new()
	_fade.color = Color.BLACK
	_fade.size = Vector2(320, 180)
	root.add_child(_fade)
