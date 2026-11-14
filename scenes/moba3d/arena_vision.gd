extends Node
## Fog of war: what each team can see. Map design lane, 2026-11-04. Built by arena_blockout.gd as Built/Vision while
## the game runs; reach it as arena.vision. Game feel's match asks can_see(team, pos) to show or hide enemies, and the
## minimap asks the same.
##
## The map is a grid of 1 m cells. Every TICK seconds, rays go out from each node in group "vision_sources" (meta
## "team", meta "vision_radius" in metres; game feel lane) and from each standing tower and core, and mark the cells
## they reach. Walls and rocks BLOCK_HEIGHT or taller stop them, and the cell a ray stops in counts as seen, so a wall
## face in view is lit. Pit rims (1.5 m) and the towers and cores themselves stop nothing. The cells a source sees from
## one spot are kept, so a source standing where one stood before costs a lookup. Neutral ("") and unknown teams see
## everything.
##
## The viewing team's grid also goes to the world's shaders (shaders/world/fog.gdshaderinc): ground, walls and props
## dim where that team can't see. The viewing team is that of the map_unit with meta "is_player", else blue. The
## dimming stays off while that team has no unit among the vision sources (the blockout, sandbox runs), so nobody walks
## into the dark, and off when the arena's fog_of_war export is off. can_see works either way.
## Every number here is a placeholder for Preston to set.

const CELL := 1.0 ## metres per cell
const TICK := 0.12 ## seconds between updates; the shaders ease from one grid to the next in between
const TOWER_SIGHT := 13.0 ## a tower sees a metre past its 12 m range
const CORE_SIGHT := 15.0
const BLOCK_HEIGHT := 2.0 ## walls and rocks this tall stop sight; a large machine is about 2 m
const BLOCK_PAD := 0.25 ## a cell stops sight when its centre is this close to a wall or rock
const CACHE_MAX := 6000 ## kept stamps before the cache starts over (about 2 KB each)
const CAST_BUDGET_MS := 2.0 ## new casts per update stop here; a moving source past it keeps its last view one tick

var arena: Node3D
var size := Vector2i.ZERO ## cells across x and z
var corner := Vector2.ZERO ## world x, z of the grid's corner
var block := PackedByteArray() ## 1 where sight stops
var seen := {"blue": PackedByteArray(), "red": PackedByteArray()} ## 255 where that team sees
var viewer := "blue" ## whose grid the shaders show
var fog_shown := false ## true while the world is dimmed
var last_update_ms := 0.0
var _rays := {} ## radius in cells -> [dx, dy, ends] (PackedInt32Array each)
var _stamps := {} ## Vector3i(cell x, cell z, radius in cells) -> PackedInt32Array of cell indices
var _last := {} ## source node's instance id -> the cells it saw last update
var _clock := 0.0
var _fresh := false
var _prev_tex: ImageTexture
var _next_tex: ImageTexture
var _mats: Array = []


func _ready() -> void:
	size = Vector2i(ceili(arena.HALF_X * 2.0 / CELL), ceili(arena.HALF_Z * 2.0 / CELL))
	corner = -Vector2(size) * CELL * 0.5
	_rasterize()


func _process(delta: float) -> void:
	_clock += delta
	if _clock >= TICK or not _fresh:
		refresh()
	if fog_shown:
		var t := clampf(_clock / TICK, 0.0, 1.0)
		for m in _mats:
			m.set_shader_parameter("fog_mix", t)


## True when team sees the world point pos. Neutral and unknown teams see everything.
func can_see(team: String, pos: Vector3) -> bool:
	if not seen.has(team):
		return true
	if not _fresh:
		refresh()
	var c := _open_cell(Vector2(pos.x, pos.z))
	return c >= 0 and seen[team][c] != 0


## Gathers the sources (the group, then the standing towers and cores) and remakes both teams' grids.
func refresh() -> void:
	var t0 := Time.get_ticks_usec()
	var src := {"blue": [], "red": []}
	var ids := {"blue": [], "red": []}
	for n in get_tree().get_nodes_in_group("vision_sources"):
		var team := String(n.get_meta("team", ""))
		if n is Node3D and src.has(team):
			var p: Vector3 = n.global_position
			src[team].append(Vector3(p.x, p.z, float(n.get_meta("vision_radius", 10.0))))
			ids[team].append(n.get_instance_id())
	var units := {"blue": src.blue.size(), "red": src.red.size()}
	for s in arena.structure_list():
		if not s.down and src.has(s.team):
			src[s.team].append(Vector3(s.p.x, s.p.y, TOWER_SIGHT if s.kind == "tower" else CORE_SIGHT))
	stamp(src, ids)
	viewer = _viewer_team()
	fog_shown = bool(arena.get("fog_of_war")) and units.get(viewer, 0) > 0
	_publish()
	last_update_ms = (Time.get_ticks_usec() - t0) / 1000.0


## Remakes the grids from {team: [Vector3(world x, world z, radius in metres), ...]}. refresh() calls it with the
## sources' instance ids alongside ({team: [id, ...]}), so a source over this update's cast budget can keep its last
## view one more tick; checks call it with made-up sources and no ids.
func stamp(src: Dictionary, ids := {}) -> void:
	if _stamps.size() > CACHE_MAX:
		_stamps.clear()
	if _last.size() > 512:
		_last.clear()
	var budget_end := Time.get_ticks_usec() + int(CAST_BUDGET_MS * 1000.0)
	for team in seen:
		var g := PackedByteArray()
		g.resize(size.x * size.y)
		var list: Array = src.get(team, [])
		var tid: Array = ids.get(team, [])
		for k in list.size():
			var s: Vector3 = list[k]
			var id: int = tid[k] if k < tid.size() else -1
			for i in _stamp_at(Vector2(s.x, s.y), s.z, id, Time.get_ticks_usec() > budget_end):
				g[i] = 255
		seen[team] = g
	_fresh = true
	_clock = 0.0


## A material the arena made after the fog started (a felled tower's stump) joins the dimming.
func track(m: Material) -> void:
	if m is ShaderMaterial and not _mats.has(m) and _next_tex:
		_mats.append(m)
		_feed(m)


func _publish() -> void:
	var img := Image.create_from_data(size.x, size.y, false, Image.FORMAT_L8, seen.get(viewer, seen.blue))
	if _next_tex == null:
		_prev_tex = ImageTexture.create_from_image(img)
		_next_tex = ImageTexture.create_from_image(img)
		_mats = arena.fog_materials() if arena.has_method("fog_materials") else []
	else:
		var old := _prev_tex
		_prev_tex = _next_tex
		_next_tex = old
		_next_tex.update(img)
	for m in _mats:
		_feed(m)


func _feed(m: ShaderMaterial) -> void:
	m.set_shader_parameter("fog_on", fog_shown)
	m.set_shader_parameter("fog_prev", _prev_tex)
	m.set_shader_parameter("fog_next", _next_tex)
	m.set_shader_parameter("fog_mix", 0.0)
	m.set_shader_parameter("fog_rect", Vector4(corner.x, corner.y, size.x * CELL, size.y * CELL))


func _viewer_team() -> String:
	for n in get_tree().get_nodes_in_group("map_units"):
		if n.get_meta("is_player", false):
			return String(n.get_meta("team", "blue"))
	return "blue"


## The cells sight stops in: walls and rocks BLOCK_HEIGHT or taller (from the arena's own layout data, so a layout
## change carries over) and the grid's border.
func _rasterize() -> void:
	var n := size.x * size.y
	block.resize(n)
	block.fill(0)
	for i in n / 2: # red's half from the layout, blue's as its turn: the map is the same map turned 180 degrees, and
		var x := i % size.x # this keeps rounding at wall edges from making one team's view differ from the other's
		var y := i / size.x
		var p := corner + Vector2(x + 0.5, y + 0.5) * CELL
		if x == 0 or y == 0 or x == size.x - 1 or y == size.y - 1 or _solid(p):
			block[i] = 1
			block[n - 1 - i] = 1


func _solid(p: Vector2) -> bool:
	for w in arena.walls:
		if w.h < BLOCK_HEIGHT:
			continue
		var d: Vector2 = p - w.c
		var along: float = absf(d.dot(w.u)) - w.half_len
		var across: float = absf(d.dot(Vector2(-w.u.y, w.u.x))) - w.half_thick
		if Vector2(maxf(along, 0.0), maxf(across, 0.0)).length() < BLOCK_PAD:
			return true
	for r in arena.rocks:
		if r.h >= BLOCK_HEIGHT and p.distance_to(r.c) < r.r + BLOCK_PAD:
			return true
	return false


## The cell under p; when that cell stops sight (a machine hugging a wall), the nearest open cell next to it, which is
## on the machine's own side since every wall is thicker than a cell. -1 when there is none.
func _open_cell(p: Vector2) -> int:
	var f := (p - corner) / CELL
	var cx := clampi(int(floor(f.x)), 0, size.x - 1)
	var cy := clampi(int(floor(f.y)), 0, size.y - 1)
	var i := cy * size.x + cx
	if block[i] == 0:
		return i
	var best := -1
	var best_d := INF
	for oy in [-1, 0, 1]:
		for ox in [-1, 0, 1]:
			var x: int = cx + ox
			var y: int = cy + oy
			if x < 0 or y < 0 or x >= size.x or y >= size.y or block[y * size.x + x] != 0:
				continue
			var d := f.distance_squared_to(Vector2(x + 0.5, y + 0.5))
			if d < best_d:
				best_d = d
				best = y * size.x + x
	return best


func _stamp_at(p: Vector2, radius: float, id := -1, late := false) -> PackedInt32Array:
	var c := _open_cell(p)
	if c < 0:
		return PackedInt32Array()
	var r := maxi(1, ceili(radius / CELL))
	var key := Vector3i(c % size.x, c / size.x, r)
	var cells: PackedInt32Array
	if _stamps.has(key):
		cells = _stamps[key]
	elif late and _last.has(id):
		return _last[id] # over this update's budget: last update's view for one more tick
	else:
		cells = _cast(key.x, key.y, r)
		_stamps[key] = cells
	if id >= 0:
		_last[id] = cells
	return cells


## The cells seen from cell (cx, cy) out to r cells: rays from the cell centre, each stopping in the first cell that
## stops sight (that cell is seen).
func _cast(cx: int, cy: int, r: int) -> PackedInt32Array:
	var table: Array = _ray_table(r)
	var dx: PackedInt32Array = table[0]
	var dy: PackedInt32Array = table[1]
	var ends: PackedInt32Array = table[2]
	var side := 2 * r + 1
	var local := PackedByteArray()
	local.resize(side * side)
	var out := PackedInt32Array()
	local[r * side + r] = 1
	out.append(cy * size.x + cx)
	var start := 0
	for e in ends:
		for k in range(start, e):
			var x := cx + dx[k]
			var y := cy + dy[k]
			if x < 0 or y < 0 or x >= size.x or y >= size.y:
				break
			var gi := y * size.x + x
			var li := (dy[k] + r) * side + dx[k] + r
			if local[li] == 0:
				local[li] = 1
				out.append(gi)
			if block[gi] != 0:
				break
		start = e
	return out


## Rays out to r cells as cell offsets in order, one ray after another (ends: where each ray stops in dx and dy).
## Built in opposite pairs, so a team's view mirrors the other's exactly.
func _ray_table(r: int) -> Array:
	if _rays.has(r):
		return _rays[r]
	var dx := PackedInt32Array()
	var dy := PackedInt32Array()
	var ends := PackedInt32Array()
	var half := maxi(8, ceili(TAU * r * 0.8)) # rays spaced about 0.6 cells apart at the rim
	for k in half:
		var a := PI * k / half
		for sgn in [1, -1]:
			var lx := 0
			var ly := 0
			var t := 0.5
			while t <= r + 0.01:
				var x: int = sgn * int(roundf(cos(a) * t))
				var y: int = sgn * int(roundf(sin(a) * t))
				if x != lx or y != ly:
					dx.append(x)
					dy.append(y)
					lx = x
					ly = y
				t += 0.5
			ends.append(dx.size())
	_rays[r] = [dx, dy, ends]
	return _rays[r]
