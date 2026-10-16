extends Node2D
## One machine on screen, drawn from the right side for the camera (scripts/machines/machine_views.gd).
## Set `machine_id`, `facing_deg` (where it faces in the world) and `camera_deg`; the node's position is where
## its feet touch the ground. Shows Codex's view art when the slot is filled, its mirror when only the other
## side exists, and the block placeholder otherwise.

const Views := preload("res://scripts/machines/machine_views.gd")

@export var machine_id := "lion_m"
@export var facing_deg := 0.0
@export var camera_deg := 0.0
var show_label := false
var dir := ""          # the view on screen now: e, ne, n, nw, w, sw, s, se
var source := ""       # "art", "mirror" or "placeholder" (read by the check)
var _sprite: Sprite2D
var _polys: Array = []


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.centered = false
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	refresh()


func _process(_delta: float) -> void:
	if Views.dir_for(facing_deg, camera_deg) != dir:
		refresh()


## Pick the view for the current facing and camera, and the art or placeholder for it.
func refresh() -> void:
	dir = Views.dir_for(facing_deg, camera_deg)
	var pick := Views.resolve(machine_id, dir)
	if pick.path != "":
		_sprite.texture = load(pick.path)
		_sprite.visible = true
		_sprite.flip_h = pick.flip
		_sprite.position = -Vector2(Views.anchor(machine_id))   # this machine's own feet point (views.json)
		_polys = []
		source = "mirror" if pick.flip else "art"
	else:
		_sprite.visible = false
		# The placeholder is drawn at the exact snapped angle, so it turns in the same steps the art will.
		_polys = Views.placeholder_polys(machine_id, Views.DIRS.find(dir) * 45.0)
		source = "placeholder"
	queue_redraw()


func _draw() -> void:
	var off := -Vector2(Views.ANCHOR)
	draw_set_transform(off)
	draw_line(Vector2(Views.ANCHOR.x - 18, Views.ANCHOR.y + 1), Vector2(Views.ANCHOR.x + 18, Views.ANCHOR.y + 1), Color(0, 0, 0, 0.35), 3.0)   # a ground shadow
	for p in _polys:
		draw_colored_polygon(p[0], p[1])
	if show_label:
		draw_string(ThemeDB.fallback_font, Vector2(2, 8), "%s  %s" % [dir, source], HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1, 1, 1, 0.7))
