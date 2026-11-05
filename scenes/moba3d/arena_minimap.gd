extends Control
## The minimap, bottom right. Map design lane, 2026-11-04. Built by arena_blockout.gd (export "minimap") on a
## CanvasLayer, so it shows in the blockout and in game feel's arena_play alike.
## Pixel art at the 320 x 180 base resolution: every square drawn here is a whole base pixel (4 x 4 on screen at
## 1280 x 720). The static picture (jungle, lane, path, paving, stream, walls, pits, camps) is painted once from the
## arena's own layout data, so a layout change carries over. On top, every frame:
## - towers and cores in their team colour (grey once arena.set_structure_down has felled them);
## - every node in group "map_units" (game feel lane) by meta "team" ("blue", "red", "" neutral) and "unit_kind"
##   ("machine", "minion", "monster"); the one with meta "is_player" gets a white rim and sets the viewing team;
## - the chase camera's view on the ground, as a thin outline.
## Each team sees its own base at the bottom (red's view is the map turned 180 degrees, which is the same map).
## Once the arena has a "vision" node, enemy units show only where the viewing team can see them.

@export var px_per_metre := 0.36 ## minimap scale; the map is 84 x 156 m, so 30 x 56 px
@export var margin := 3 ## base pixels from the screen's bottom right corner

const FRAME := Color(0.08, 0.09, 0.12)
const FRAME_LIGHT := Color(0.55, 0.58, 0.66)
## The ground colours per arena theme (arena_blockout.gd THEMES), so the minimap reads like the floor it shows.
const PALETTES := {
	"nature": {"jungle": Color(0.13, 0.27, 0.15), "lane": Color(0.3, 0.48, 0.14), "path": Color(0.61, 0.48, 0.27),
		"pave": Color(0.64, 0.6, 0.54), "water": Color(0.23, 0.53, 0.78), "solid": Color(0.06, 0.07, 0.09),
		"pit": Color(0.88, 0.56, 0.22), "camp": Color(0.88, 0.76, 0.3)},
	"circuit": {"jungle": Color(0.36, 0.38, 0.44), "lane": Color(0.55, 0.58, 0.64), "path": Color(0.2, 0.2, 0.25),
		"pave": Color(0.66, 0.68, 0.74), "water": Color(0.2, 0.7, 0.85), "solid": Color(0.07, 0.07, 0.09),
		"pit": Color(0.88, 0.56, 0.22), "camp": Color(0.37, 0.85, 1.0)},
	"neon": {"jungle": Color(0.1, 0.09, 0.15), "lane": Color(0.2, 0.19, 0.26), "path": Color(0.05, 0.05, 0.08),
		"pave": Color(0.3, 0.29, 0.38), "water": Color(0.45, 0.25, 0.85), "solid": Color(0.0, 0.0, 0.02),
		"pit": Color(0.88, 0.56, 0.22), "camp": Color(0.6, 0.42, 1.0)},
	"foundry": {"jungle": Color(0.21, 0.21, 0.25), "lane": Color(0.47, 0.49, 0.54), "path": Color(0.14, 0.13, 0.16),
		"pave": Color(0.37, 0.38, 0.43), "water": Color(0.12, 0.5, 0.5), "solid": Color(0.04, 0.04, 0.06),
		"pit": Color(1.0, 0.6, 0.2), "camp": Color(0.95, 0.76, 0.15)},
}
const TEAM := {"blue": Color(0.35, 0.6, 1.0), "red": Color(1.0, 0.36, 0.3), "": Color(0.95, 0.85, 0.4)}
const DOWN := Color(0.35, 0.35, 0.38)

var arena: Node3D
var pal: Dictionary = PALETTES["nature"] ## the colours in use, from arena.theme
var flipped := false ## true while the viewer is red: the map turns 180 degrees
var _tex: ImageTexture
var _size := Vector2i.ZERO


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	pal = PALETTES.get(String(arena.get("theme")), PALETTES["nature"])
	_size = Vector2i(ceili(arena.HALF_X * 2 * px_per_metre), ceili(arena.HALF_Z * 2 * px_per_metre))
	size = Vector2(_size + Vector2i(4, 4))
	_paint()


func _process(_delta: float) -> void:
	var vp := get_viewport_rect().size
	position = (vp - size - Vector2(margin, margin)).floor()
	var red := _viewer_team() == "red"
	if red != flipped:
		flipped = red
		_paint()
	queue_redraw()


## The picture under the icons, painted from the arena's layout data, one base pixel at a time.
func image() -> Image:
	var img := Image.create(_size.x, _size.y, false, Image.FORMAT_RGBA8)
	var pad := 0.6 / px_per_metre # walls thinner than a pixel still get one
	for py in _size.y:
		for px in _size.x:
			var w := _to_world(Vector2(px + 0.5, py + 0.5))
			img.set_pixel(px, py, _ground_at(w, pad))
	return img


func _paint() -> void:
	var img := image()
	if _tex == null:
		_tex = ImageTexture.create_from_image(img)
	else:
		_tex.update(img)


func _ground_at(p: Vector2, pad: float) -> Color:
	for w in arena.walls:
		var d: Vector2 = p - w.c
		var along: float = absf(d.dot(w.u)) - w.half_len
		var across: float = absf(d.dot(Vector2(-w.u.y, w.u.x))) - w.half_thick
		if Vector2(maxf(along, 0.0), maxf(across, 0.0)).length() < pad * 0.5:
			return pal.solid
	for r in arena.rocks:
		if p.distance_to(r.c) < r.r + pad * 0.25:
			return pal.solid
	if absf(p.x) > arena.HALF_X - pad * 0.5 or absf(p.y) > arena.HALF_Z - pad * 0.5:
		return pal.solid
	for t in [1.0, -1.0]:
		if p.distance_to(arena.PIT * t) < arena.PIT_R:
			return (pal.pit as Color).darkened(0.45)
		for c in arena.CAMPS:
			if p.distance_to(c * t) < arena.CAMP_R:
				return (pal.camp as Color).darkened(0.3)
		if p.distance_to(arena.BASE_CENTRE * t) < arena.BASE_R:
			return (pal.pave as Color).lerp(TEAM["blue" if t > 0 else "red"], 0.3)
	if p.length() < arena.PLAZA_R:
		return pal.pave
	var ld: float = arena._lane_dist(p)
	if ld < arena.PATH_WIDTH * 0.5 + pad * 0.3:
		return pal.path
	if absf(p.y) < arena.STREAM_HALF + pad * 0.3 and absf(p.x) > arena.PLAZA_R + arena.WALL_THICK:
		return pal.water
	if ld < arena.LANE_WIDTH * 0.5:
		return pal.lane
	return pal.jungle


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), FRAME)
	draw_rect(Rect2(Vector2.ONE, size - Vector2(2, 2)), FRAME_LIGHT)
	var o := Vector2(2, 2)
	draw_texture(_tex, o)
	for p in get_tree().get_nodes_in_group("arena_pits"): # side pits: rim in the owner's colour, filled while locked
		var rim: Color = TEAM.get(p.owner_team, TEAM[""])
		if p.capturing != "" and p.progress > 0.0 and fmod(Time.get_ticks_msec() / 1000.0, 0.5) < 0.25:
			rim = TEAM.get(p.capturing, rim)
		_dot(o + _to_map(Vector2(p.global_position.x, p.global_position.z)), 1, rim if p.locked_left > 0.0 else FRAME, rim)
	var viewer := _viewer_team()
	for s in arena.structure_list():
		var c: Color = DOWN if s.down else TEAM[s.team]
		var big := 2 if s.kind == "core" else 1
		_dot(o + _to_map(s.p), big, c, FRAME)
	var vision = arena.get("vision")
	var player: Node3D = null
	for n in get_tree().get_nodes_in_group("map_units"):
		if not (n is Node3D) or not n.is_visible_in_tree():
			continue
		var team: String = n.get_meta("team", "")
		var p := Vector2(n.global_position.x, n.global_position.z)
		if vision and team != "" and team != viewer and not vision.can_see(viewer, n.global_position):
			continue
		if n.get_meta("is_player", false):
			player = n
			continue
		match String(n.get_meta("unit_kind", "machine")):
			"minion":
				draw_rect(Rect2((o + _to_map(p)).floor(), Vector2.ONE), TEAM.get(team, TEAM[""]))
			"monster":
				draw_rect(Rect2((o + _to_map(p)).floor(), Vector2(2, 2)), TEAM[""])
			_:
				_dot(o + _to_map(p), 1, TEAM.get(team, TEAM[""]), FRAME)
	if player == null:
		player = arena.get_node_or_null("Player")
	_draw_view(o)
	if player:
		var team: String = player.get_meta("team", "blue")
		_dot(o + _to_map(Vector2(player.global_position.x, player.global_position.z)), 1, TEAM.get(team, TEAM["blue"]), Color.WHITE)


## A square of side 2 * r + 1 base pixels with a one-pixel rim.
func _dot(at: Vector2, r: int, fill: Color, rim: Color) -> void:
	var c := at.floor()
	draw_rect(Rect2(c - Vector2(r + 1, r + 1), Vector2(r * 2 + 3, r * 2 + 3)), rim)
	draw_rect(Rect2(c - Vector2(r, r), Vector2(r * 2 + 1, r * 2 + 1)), fill)


## What the chase camera sees of the ground, cut off 28 m out (the frame's top edge is level, so it never ends).
func _draw_view(o: Vector2) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var foot := Vector3(cam.global_position.x, 0, cam.global_position.z)
	var pts := PackedVector2Array()
	for corner in [Vector2(0, 0), Vector2(vp.x, 0), vp, Vector2(0, vp.y)]:
		var from := cam.project_ray_origin(corner)
		var dir := cam.project_ray_normal(corner)
		var hit := from + Vector3(dir.x, 0, dir.z).normalized() * 28.0
		if dir.y < -0.01:
			hit = from + dir * (-from.y / dir.y)
		if Vector3(hit.x, 0, hit.z).distance_to(foot) > 28.0:
			hit = foot + (Vector3(hit.x, 0, hit.z) - foot).normalized() * 28.0
		pts.append(o + _to_map(Vector2(hit.x, hit.z)))
	pts.append(pts[0])
	draw_polyline(pts, Color(1, 1, 1, 0.55), 1.0)


func _viewer_team() -> String:
	for n in get_tree().get_nodes_in_group("map_units"):
		if n.get_meta("is_player", false):
			return n.get_meta("team", "blue")
	return "blue"


## Centred, so pixel centres sit in twins turned 180 degrees about the map's middle, like the map itself.
func _to_map(p: Vector2) -> Vector2:
	if flipped:
		p = -p
	return p * px_per_metre + Vector2(_size) * 0.5


func _to_world(m: Vector2) -> Vector2:
	var p := (m - Vector2(_size) * 0.5) / px_per_metre
	return -p if flipped else p
