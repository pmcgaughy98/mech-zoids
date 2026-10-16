extends Node2D
## The view lab: the six starters on a round battle floor and a camera you can turn (Claude, 2026-10-11).
## Q / E turn the camera 45 degrees, O lets it orbit slowly, L shows each machine's view and source, Tab steps through
## the machines one at a time at full size (and back to all six), H hides the text, Esc goes back to the title. It
## proves the multi-view wiring and it is where Codex and Preston check view art: drop PNGs in
## res://art/machines/<id>/views/ and they appear here.
## 2026-10-16 (creature factory pass, from Codex's finish reports): all six starters are on the floor (the kangaroo and
## wolf were missing), drawn at half size like the battle's zoomed field so none is cropped at the top; the full-size
## look Codex set up a fixture for is Tab.

const Views := preload("res://scripts/machines/machine_views.gd")
const ViewSprite := preload("res://scripts/machines/view_sprite.gd")
const Stage := preload("res://scripts/battle/stage.gd")
const CENTRE := Vector2(160, 118)        # screen point of the floor's middle, all six on the floor
const SOLO_FEET := Vector2(160, 168)     # screen point of the feet, one machine at full size
const FLOOR_R := 210.0                   # floor radius in art pixels
const LAB_ZOOM := 0.5                    # the floor's size, rounded to whole screen pixels per art pixel (Stage)
# [machine, ground position (x east, y north, art pixels), facing in degrees (0 east, 90 north)], on a ring of 170
const CAST := [["ape_l", Vector2(-166, 35), 20.0], ["shoebill_m", Vector2(138, 100), 220.0],
	["pangolin_m", Vector2(138, -100), 160.0], ["hippo_m", Vector2(-53, -162), 300.0],
	["kangaroo_m", Vector2(-53, 162), 260.0], ["wolf_m", Vector2(-138, -100), 340.0]]

var camera_deg := 0.0        # where the camera is now (eases toward target_deg)
var target_deg := 0.0
var orbit := false
var focus := -1              # -1: all six; otherwise the one machine shown alone at full size
var actors: Array = []       # [ViewSprite, ground position]
var stage: Node2D            # the floor and the machines, scaled
var _hud: Label


func _ready() -> void:
	stage = Node2D.new()
	stage.name = "stage"
	add_child(stage)
	stage.draw.connect(_draw_floor)
	for c in CAST:
		var s := ViewSprite.new()
		s.machine_id = c[0]
		s.facing_deg = c[2]
		stage.add_child(s)
		actors.append([s, c[1]])
	_hud = Label.new()
	_hud.position = Vector2(4, 2)
	_hud.add_theme_font_size_override("font_size", 8)
	_hud.add_theme_color_override("font_color", Color(1, 1, 1, 0.8))
	add_child(_hud)
	_place()


## Turn the camera by whole 45-degree steps (eased); the check calls this directly.
func turn(steps: int) -> void:
	target_deg += steps * 45.0


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_Q: turn(-1)
		KEY_E: turn(1)
		KEY_O: orbit = not orbit
		KEY_TAB: focus = focus + 1 if focus + 1 < actors.size() else -1
		KEY_H: _hud.visible = not _hud.visible
		KEY_L:
			for a in actors:
				a[0].show_label = not a[0].show_label
				a[0].queue_redraw()
		KEY_ESCAPE: get_tree().change_scene_to_file("res://scenes/title.tscn")


func _process(delta: float) -> void:
	if orbit:
		target_deg += 20.0 * delta
	camera_deg = move_toward(camera_deg, target_deg, maxf(90.0 * delta, absf(target_deg - camera_deg) * 6.0 * delta))
	_place()


## The floor's scale: half size for all six (whole screen pixels per art pixel), full size for one alone.
func floor_scale() -> float:
	if focus >= 0:
		return 1.0
	var k := Stage.window_scale(get_window().size)
	return maxf(1.0, roundf(k * LAB_ZOOM)) / k


## Put every machine where its ground spot is for this camera, nearer ones in front, and tell it the camera.
func _place() -> void:
	var s := floor_scale()
	stage.scale = Vector2(s, s)
	var centre := (SOLO_FEET if focus >= 0 else CENTRE) / s
	for i in actors.size():
		var a: Array = actors[i]
		var sp: Node2D = a[0]
		sp.visible = focus < 0 or focus == i
		var ground: Vector2 = Vector2.ZERO if focus == i else a[1]
		sp.facing_deg = 0.0 if focus == i else CAST[i][2]   # alone: its side view, facing screen right at camera 0
		sp.position = Views.ground_to_screen(ground, camera_deg, centre).round()
		sp.z_index = 400 - int(Views.ground_depth(ground, camera_deg))   # nearer in front; always above the floor (z 0)
		sp.camera_deg = camera_deg
	_hud.text = "VIEW LAB  cam %d  Q/E turn  O orbit%s  Tab: %s  L labels  H hide" % [
		int(fposmod(round(camera_deg), 360.0)), " on" if orbit else "", "all six" if focus < 0 else actors[focus][0].machine_id]
	stage.queue_redraw()


## The floor: a ring and spokes on the ground, so the turn reads even with placeholder machines.
func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 180), Color("1d2024"))


func _draw_floor() -> void:
	var s := floor_scale()
	var centre := (SOLO_FEET if focus >= 0 else CENTRE) / s
	var r := FLOOR_R if focus < 0 else FLOOR_R * 0.6
	var ring := PackedVector2Array()
	for k in 48:
		ring.append(Views.ground_to_screen(Vector2.RIGHT.rotated(k * TAU / 48.0) * r, camera_deg, centre))
	stage.draw_colored_polygon(ring, Color("2c3036"))
	ring.append(ring[0])   # close the outline
	stage.draw_polyline(ring, Color("4a4f57"), 1.0 / s)
	for k in 8:
		var tip := Views.ground_to_screen(Vector2.RIGHT.rotated(k * TAU / 8.0) * r, camera_deg, centre)
		stage.draw_line(centre, tip, Color("3a3f46"), 1.0 / s)
	# North marker, so the world's directions stay readable while the camera turns.
	stage.draw_circle(Views.ground_to_screen(Vector2(0, r + 10), camera_deg, centre), 2.0 / s, Color("ffd400"))
