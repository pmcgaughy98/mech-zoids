extends SceneTree
## Checks the first arena blockout and draws its top-down sketch. Map design lane, 2026-11-04.
## Run: Godot --headless --fixed-fps 60 --path . -s res://tools/map/arena_check.gd
## - the lane is clear: nothing solid within 5.5 m of the lane's centre line;
## - a large machine (1 m clearance) can walk from each spawn to every spawn, core, tower, camp, pit and the plaza;
## - red's half is blue's half turned 180 degrees (every wall piece and rock has a twin);
## - each team's walk to its own side pit is the same length;
## - the named markers sit on their features, saved and built alike;
## - collision: every standing mesh has one body the shape of its mesh on the world layer, no stray bodies;
## - floors are flat and nothing solid stands on a spawn, camp, pit or the plaza; the map edge is sealed;
## - the nav mesh has no islands on rock tops and reaches every feature from both spawns;
## - dressing (Built/Dressing: trees, bushes, banners, crystals) has no bodies, and nothing in it taller than 0.5 m
##   stands where a machine walks (parts whose bottom is over OVERHEAD hang above a machine and are left out);
## - prints walk distances and times on the nav mesh, and writes the sketch SVG from the same numbers.

const Arena := preload("res://scenes/moba3d/arena_blockout.gd")
const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const SKETCH := "res://docs/plan/moba-arena-sketch-2026-11-04.svg"
const CLEAR := 1.0 ## a large machine's half-width, metres
const MOVE_SPEED := 3.5 ## the placeholder in machine_test_player.gd
const PX := 5.0 ## sketch pixels per metre
const MARGIN := 4.0 ## sketch margin, metres

var fails := 0
var passes := 0
var arena
var astar := AStarGrid2D.new()
const OVERHEAD := 2.5 ## metres; a large machine is about 2 m
var walks := [] ## [label, metres] for the sketch legend
var lane_length := 0.0
var space: PhysicsDirectSpaceState3D
var nav_map: RID


func _initialize() -> void:
	arena = load(SCENE).instantiate()
	var saved := {}
	for m in arena.get_node("Markers").get_children(): # as saved in the .tscn, before the builder moves them
		saved[String(m.name)] = m.position
	root.add_child(arena)
	await process_frame # children of root get _ready only once root is ready, after _initialize
	for i in 3:
		await physics_frame # bodies join the physics space
	nav_map = arena.get_world_3d().navigation_map
	var waited := 0
	while NavigationServer3D.map_get_closest_point(nav_map, Vector3(0, 0, 70)).is_zero_approx() and waited < 240:
		await physics_frame # the nav map syncs on its own thread, a few frames after the region joins
		waited += 1
	print("  nav map ready after %d more physics frames" % waited)
	space = arena.get_world_3d().direct_space_state
	_check_scene()
	_check_markers(saved)
	_check_lane()
	_check_symmetry()
	_check_collision()
	_check_floors()
	_check_edge()
	_check_walks()
	_check_nav()
	_check_dressing()
	_check_minimap()
	_check_vision()
	_write_sketch()
	for i in 10:
		await process_frame
	var player: Node3D = arena.get_node("Player")
	_ok(player.global_position.distance_to(Vector3(0, 0, 64)) < 0.01, "player stood still for 10 frames at blue's base")
	print("arena_check: %d passed, %d failed" % [passes, fails])
	quit(1 if fails > 0 else 0)


## Fog of war (scenes/moba3d/arena_vision.gd): the rays against a dense straight-line test, the two teams' views as
## mirror images, towers giving and losing sight, the dimming staying off without a unit of the viewer's team, cost.
func _check_vision() -> void:
	var v = arena.get("vision")
	if v == null:
		_ok(false, "the vision grid is built")
		return
	var w: int = v.size.x
	var n: int = v.size.x * v.size.y
	var agree := 0
	var total := 0
	var leaks := 0
	for at in [Vector2(-2.5, 9.5), Vector2(-20.3, 24.5)]: # in the plaza by the lane mouth; in blue's jungle by a rock
		v.stamp({"blue": [Vector3(at.x, at.y, 12.0)], "red": []})
		var g: PackedByteArray = v.seen["blue"]
		var from: Vector2 = v.corner + (((at - v.corner) / v.CELL).floor() + Vector2(0.5, 0.5)) * v.CELL
		for i in n:
			var c: Vector2 = v.corner + Vector2(i % w + 0.5, i / w + 0.5) * v.CELL
			if c.distance_to(from) > 11.0 or v.block[i] != 0:
				continue
			total += 1
			var clear := _line_clear(v, from, c)
			var got: bool = g[i] != 0
			if got == clear:
				agree += 1
			elif got:
				leaks += 1
	_ok(total > 0 and agree >= total * 0.97 and leaks <= total * 0.01, "vision: the rays agree with a straight-line check on %d of %d open cells within 11 m of two spots (%d seen through a wall)" % [agree, total, leaks])
	v.stamp({"blue": [Vector3(-2.5, 9.5, 12.0), Vector3(-20.3, 24.5, 12.0)], "red": [Vector3(2.5, -9.5, 12.0), Vector3(20.3, -24.5, 12.0)]})
	var gb: PackedByteArray = v.seen["blue"]
	var gr: PackedByteArray = v.seen["red"]
	var odd := 0
	for i in n:
		if gb[i] != gr[n - 1 - i]:
			odd += 1
	_ok(odd == 0, "vision: red's view from the turned spots is blue's turned, cell for cell (%d odd cells)" % odd)
	var down_lane := Vector3(0, 0, 31)
	v.refresh()
	var tower_sees: bool = v.can_see("blue", down_lane)
	var red_sees: bool = v.can_see("red", down_lane)
	var plaza: bool = v.can_see("blue", Vector3.ZERO)
	arena.set_structure_down("BlueTower", true)
	v.refresh()
	var felled: bool = v.can_see("blue", down_lane)
	arena.set_structure_down("BlueTower", false)
	v.refresh()
	_ok(tower_sees and not red_sees and not plaza and not felled and v.can_see("", Vector3.ZERO) and not v.fog_shown, "vision: blue's tower sees 9 m down the lane and red doesn't; the plaza is out of the bases' sight; a felled tower sees nothing; neutral sees all; no dimming without a unit of the viewer's team")
	var src := {"blue": [], "red": []}
	var lane: Array = Arena.LANE
	for s in lane.size() - 1:
		for q in 4:
			var p: Vector2 = lane[s].lerp(lane[s + 1], (q + 0.5) / 4.0)
			src["blue" if (s * 4 + q) % 2 == 0 else "red"].append(Vector3(p.x, p.y, 12.0 if q % 2 == 0 else 8.0))
	v._stamps.clear()
	var t0 := Time.get_ticks_usec()
	v.stamp(src)
	var cold := (Time.get_ticks_usec() - t0) / 1000.0
	t0 = Time.get_ticks_usec()
	v.stamp(src)
	var warm := (Time.get_ticks_usec() - t0) / 1000.0
	var mats: int = arena.fog_materials().size()
	_ok(warm < 8.0 and mats >= 5, "vision: %d sources along the lane take %.1f ms from new spots (spread over updates, %.0f ms each), %.1f ms from known ones (every %.2f s); %d world materials take the fog" % [src.blue.size() + src.red.size(), cold, v.CAST_BUDGET_MS, warm, v.TICK, mats])


## True when no cell that stops sight lies between cell centres a and b (dense samples, 0.1 m apart).
func _line_clear(v, a: Vector2, b: Vector2) -> bool:
	var w: int = v.size.x
	var steps := int(ceil(a.distance_to(b) / 0.1))
	var end_cell := Vector2i(((b - v.corner) / v.CELL).floor())
	for k in range(1, steps):
		var p := a.lerp(b, float(k) / steps)
		var cell := Vector2i(((p - v.corner) / v.CELL).floor())
		if cell != end_cell and v.block[cell.y * w + cell.x] != 0:
			return false
	return true


func _ok(cond: bool, what: String) -> void:
	if cond:
		passes += 1
		print("  ok   ", what)
	else:
		fails += 1
		print("  FAIL ", what)


func _check_scene() -> void:
	_ok(arena.walls.size() > 50, "built %d wall pieces, %d rocks, %d features" % [arena.walls.size(), arena.rocks.size(), arena.features.size()])
	_ok(arena.get_node_or_null("Player/Sprite") != null, "the player machine is in the arena")
	var cam: Camera3D = arena.get_node_or_null("Camera")
	_ok(cam != null and cam.current, "the chase camera is current")


func _check_lane() -> void:
	var worst := INF
	var worst_at := Vector2.ZERO
	for i in Arena.LANE.size() - 1:
		var a: Vector2 = Arena.LANE[i]
		var b: Vector2 = Arena.LANE[i + 1]
		lane_length += a.distance_to(b)
		var steps := int(a.distance_to(b) / 0.5)
		for k in steps + 1:
			var p := a.lerp(b, float(k) / steps)
			var d := _clearance(p)
			if d < worst:
				worst = d
				worst_at = p
	_ok(worst >= 5.5, "nothing solid within %.1f m of the lane centre line (closest at %.0f, %.0f)" % [worst, worst_at.x, worst_at.y])
	print("  lane, core to core: %.1f m, %.1f s at %.1f m/s" % [lane_length, lane_length / MOVE_SPEED, MOVE_SPEED])


func _obb_dist(p: Vector2, w: Dictionary) -> float:
	var d: Vector2 = p - w.c
	var u: Vector2 = w.u
	var along: float = absf(d.dot(u)) - w.half_len
	var across: float = absf(d.dot(Vector2(-u.y, u.x))) - w.half_thick
	if along < 0.0 and across < 0.0:
		return maxf(along, across)
	return Vector2(maxf(along, 0.0), maxf(across, 0.0)).length()


func _clearance(p: Vector2) -> float:
	var best := INF
	for w in arena.walls:
		best = minf(best, _obb_dist(p, w))
	for r in arena.rocks:
		best = minf(best, p.distance_to(r.c) - r.r)
	return best


func _check_symmetry() -> void:
	var missing := 0
	for list in [arena.walls, arena.rocks]:
		for a in list:
			var twin: Vector2 = -a.c
			var found := false
			for b in list:
				if (b.c as Vector2).distance_to(twin) < 0.05:
					found = true
					break
			if not found:
				missing += 1
	_ok(missing == 0, "red's half is blue's half turned 180 degrees (%d pieces without a twin)" % missing)


func _cell(p: Vector2) -> Vector2i:
	return Vector2i(floori(p.x + Arena.HALF_X), floori(p.y + Arena.HALF_Z))


func _check_walks() -> void:
	var nx := int(Arena.HALF_X * 2)
	var nz := int(Arena.HALF_Z * 2)
	astar.region = Rect2i(0, 0, nx, nz)
	astar.cell_size = Vector2.ONE
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	astar.update()
	var solid := 0
	for iz in nz:
		for ix in nx:
			var p := Vector2(ix - Arena.HALF_X + 0.5, iz - Arena.HALF_Z + 0.5)
			var near_edge: bool = absf(p.x) > Arena.HALF_X - CLEAR or absf(p.y) > Arena.HALF_Z - CLEAR
			if near_edge or _clearance(p) < CLEAR:
				astar.set_point_solid(Vector2i(ix, iz))
				solid += 1
	print("  walk grid: %d x %d cells of 1 m, %d blocked for a large machine" % [nx, nz, solid])
	var spawns := {"blue": _feat("blue spawn").p, "red": _feat("red spawn").p}
	var unreachable := []
	for team in spawns:
		for f in arena.features:
			if _walk(spawns[team], f.p) < 0.0:
				unreachable.append("%s spawn to %s" % [team, f.name])
	_ok(unreachable.is_empty(), "every feature can be reached from both spawns %s" % str(unreachable))
	var own_blue := _walk(spawns.blue, _feat("blue side pit").p)
	var own_red := _walk(spawns.red, _feat("red side pit").p)
	_ok(absf(own_blue - own_red) < 0.5, "own side pit is the same walk for both teams (%.1f m and %.1f m)" % [own_blue, own_red])
	print("  walks from blue spawn (1 m grid, 8 directions; the real walk is up to about 8% shorter):")
	for target in ["blue tower", "blue camp", "blue side pit", "plaza", "red side pit", "red tower", "red core"]:
		var best := INF
		for f in arena.features:
			if f.name == target:
				best = minf(best, _walk(spawns.blue, f.p))
		print("    %-14s %6.1f m  %5.1f s" % [target, best, best / MOVE_SPEED])


func _check_markers(saved: Dictionary) -> void:
	var want := {"Plaza": Vector2.ZERO}
	for t in [1.0, -1.0]:
		var team := "Blue" if t > 0 else "Red"
		want[team + "Spawn"] = Arena.SPAWN * t
		want[team + "Core"] = Arena.CORE * t
		want[team + "Tower"] = Arena.TOWER * t
		want[team + "Pit"] = Arena.PIT * t
		want[team + "Camp1"] = Arena.CAMPS[0] * t
		want[team + "Camp2"] = Arena.CAMPS[1] * t
	for i in Arena.STREAMS.size():
		want["Stream%d" % (i + 1)] = Arena.STREAMS[i]
	var bad := []
	for key in want:
		var m: Node3D = arena.get_node_or_null("Markers/" + key)
		var p: Vector2 = want[key]
		if m == null or m.global_position.distance_to(Vector3(p.x, 0, p.y)) > 0.01:
			bad.append(key + " built")
		elif not saved.has(key) or (saved[key] as Vector3).distance_to(m.position) > 0.01:
			bad.append(key + " saved")
	_ok(bad.is_empty(), "%d markers sit on their features, saved and built alike %s" % [want.size(), str(bad)])
	var blue_fwd: Vector3 = -arena.get_node("Markers/BlueSpawn").global_basis.z
	var red_fwd: Vector3 = -arena.get_node("Markers/RedSpawn").global_basis.z
	_ok(blue_fwd.dot(Vector3.FORWARD) > 0.99 and red_fwd.dot(Vector3.BACK) > 0.99, "spawn markers face up the lane (blue toward -z, red toward +z)")


func _check_collision() -> void:
	var built: Node = arena.get_node("Built")
	var standing := 0
	var bad := []
	for mi in _undressed(built):
		var aabb: AABB = mi.mesh.get_aabb()
		if aabb.size.y < 0.5:
			continue # floors: planes and discs
		standing += 1
		var bodies: Array = mi.find_children("*", "StaticBody3D", false, false)
		var shapes: Array = []
		if bodies.size() == 1:
			shapes = bodies[0].find_children("*", "CollisionShape3D", false, false)
		if shapes.size() != 1:
			bad.append("%s with %d bodies" % [mi.mesh.get_class(), bodies.size()])
			continue
		var body: StaticBody3D = bodies[0]
		var box := _shape_aabb(shapes[0].shape)
		var same := box.position.distance_to(aabb.position) < 0.02 and box.size.distance_to(aabb.size) < 0.02
		if body.collision_layer != Arena.WORLD_LAYER or not same or not body.global_transform.is_equal_approx(mi.global_transform) or not shapes[0].transform.is_equal_approx(Transform3D.IDENTITY):
			bad.append("%s at %s: mesh %s body %s" % [mi.mesh.get_class(), mi.global_position.snapped(Vector3.ONE * 0.1), aabb.size, box.size])
	_ok(standing > 50 and bad.is_empty(), "every one of %d standing meshes (walls, rims, cliffs, rocks, towers, cores) has one body the shape of its mesh, on layer bit %d %s" % [standing, Arena.WORLD_LAYER, str(bad.slice(0, 4))])
	var all_bodies: Array = built.find_children("*", "StaticBody3D", true, false)
	var ground: StaticBody3D = built.get_node_or_null("Ground")
	_ok(ground != null and all_bodies.size() == standing + 1, "no stray bodies: %d bodies = %d standing meshes + the ground" % [all_bodies.size(), standing])


## Every mesh under Built except the dressing, which has no bodies by design, and the capture points' overlays (the
## side pits' rings and the plaza beacon's ring and beam, 2026-11-05: looks only, no bodies, the ring 3.5 cm up so it
## draws over the floor marks). owned = false: Built is never saved.
func _undressed(built: Node) -> Array:
	var dress: Node = built.get_node("Dressing")
	var points: Array = built.get_tree().get_nodes_in_group("arena_pits") + built.get_tree().get_nodes_in_group("arena_beacons")
	return built.find_children("*", "MeshInstance3D", true, false).filter(func(mi): return not dress.is_ancestor_of(mi) 		and not points.any(func(p): return p.is_ancestor_of(mi)))


func _check_dressing() -> void:
	var dress: Node = arena.get_node("Built/Dressing")
	var bodies: Array = dress.find_children("*", "CollisionObject3D", true, false)
	var tall := 0
	var on_walk := []
	for n in dress.find_children("*", "GeometryInstance3D", true, false):
		var spots: Array = []
		var h := 0.0
		if n is MultiMeshInstance3D:
			var mm: MultiMesh = n.multimesh
			h = mm.mesh.get_aabb().size.y
			spots = Array(n.get_meta("spots", PackedVector3Array())) # the headless renderer keeps no transforms
		elif n is MeshInstance3D:
			var box: AABB = n.global_transform * n.mesh.get_aabb()
			if box.position.y > OVERHEAD:
				continue # a turret's barrels: a machine walks under them
			h = box.size.y
			spots.append(n.global_position)
		if h < 0.5:
			continue
		for p in spots:
			tall += 1
			var g := Vector3(p.x, 0, p.z)
			var c := NavigationServer3D.map_get_closest_point(nav_map, g)
			if Vector2(c.x - g.x, c.z - g.z).length() < 0.5:
				on_walk.append("%s at %s" % [n.name, Vector2(g.x, g.z).snapped(Vector2.ONE * 0.1)])
	_ok(tall > 100 and bodies.is_empty() and on_walk.is_empty(), "dressing: %d things taller than 0.5 m (trees, bushes, banners, crystals), no bodies, none standing where a machine walks %s" % [tall, str(on_walk.slice(0, 4))])


func _check_minimap() -> void:
	var map: Control = arena.get_node_or_null("Built/Minimap/Map")
	if map == null:
		_ok(false, "the minimap is built")
		return
	var img: Image = map.image()
	var w := img.get_width()
	var h := img.get_height()
	var blue_base: Color = (map.pal.pave as Color).lerp(map.TEAM["blue"], 0.3)
	var red_base: Color = (map.pal.pave as Color).lerp(map.TEAM["red"], 0.3)
	var near := func(a: Color, b: Color) -> bool: return maxf(maxf(absf(a.r - b.r), absf(a.g - b.g)), absf(a.b - b.b)) < 0.01 # 8-bit storage
	var odd := 0
	for y in h:
		for x in w:
			var a := img.get_pixel(x, y)
			var b := img.get_pixel(w - 1 - x, h - 1 - y)
			if not near.call(a, b) and not (near.call(a, blue_base) and near.call(b, red_base)) and not (near.call(a, red_base) and near.call(b, blue_base)):
				odd += 1
	var at := func(p: Vector2) -> Color: return img.get_pixelv(Vector2i((p * map.px_per_metre + Vector2(w, h) * 0.5).floor()))
	var spots_ok: bool = near.call(at.call(Vector2(0, 45)), map.pal.path) and near.call(at.call(Vector2.ZERO), map.pal.pave) 		and near.call(at.call(Vector2(-20, 18)), map.pal.solid) and near.call(at.call(Arena.CORE), blue_base)
	_ok(odd == 0 and spots_ok, "minimap: %d x %d px, painted from the layout; turned 180 degrees it is the same map (%d odd pixels); path, plaza, a rock and blue's base land where they should" % [w, h, odd])


func _shape_aabb(s: Shape3D) -> AABB:
	if s is BoxShape3D:
		var b := s as BoxShape3D
		return AABB(-b.size * 0.5, b.size)
	if s is ConvexPolygonShape3D:
		var pts: PackedVector3Array = (s as ConvexPolygonShape3D).points
		var a := AABB(pts[0], Vector3.ZERO)
		for p in pts:
			a = a.expand(p)
		return a
	return AABB()


func _check_floors() -> void:
	var built: Node = arena.get_node("Built")
	var floors := 0
	var off := 0
	for mi in _undressed(built):
		var aabb: AABB = mi.mesh.get_aabb()
		if aabb.size.y >= 0.5:
			continue
		floors += 1
		var top: float = mi.global_position.y + aabb.end.y
		if top < -0.001 or top > 0.03:
			off += 1
	var ground: StaticBody3D = built.get_node("Ground")
	var slab: BoxShape3D = ground.get_child(0).shape
	var slab_top: float = ground.get_child(0).global_position.y + slab.size.y * 0.5
	var covers: bool = slab.size.x >= Arena.HALF_X * 2 and slab.size.z >= Arena.HALF_Z * 2
	_ok(off == 0 and covers and absf(slab_top) < 0.001 and ground.collision_layer == Arena.GROUND_LAYER, "floors: %d floor meshes lie flat (tops 0 to 3 cm); one ground body on layer bit %d covers the map, top at y = %.2f" % [floors, Arena.GROUND_LAYER, slab_top])
	var probe := CylinderShape3D.new()
	probe.height = 2.0
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = probe
	q.collision_mask = Arena.WORLD_LAYER
	var blocked := []
	for f in arena.features:
		if f.kind in ["core", "tower"]:
			continue # these are the solids
		probe.radius = f.r - 0.3
		q.transform = Transform3D(Basis(), Vector3(f.p.x, 1.0, f.p.y))
		if not space.intersect_shape(q, 1).is_empty():
			blocked.append(f.name)
	_ok(blocked.is_empty(), "nothing solid stands on a spawn, camp, side pit floor or the plaza (physics query) %s" % str(blocked))


func _check_edge() -> void:
	var hx: float = Arena.HALF_X
	var hz: float = Arena.HALF_Z
	var rays := []
	var x := -hx + 0.25
	while x < hx:
		rays.append([Vector2(x, hz - 1), Vector2(x, hz + 3)])
		rays.append([Vector2(x, -hz + 1), Vector2(x, -hz - 3)])
		x += 0.5
	var z := -hz + 0.25
	while z < hz:
		rays.append([Vector2(hx - 1, z), Vector2(hx + 3, z)])
		rays.append([Vector2(-hx + 1, z), Vector2(-hx - 3, z)])
		z += 0.5
	for sx in [1.0, -1.0]:
		for sz in [1.0, -1.0]:
			rays.append([Vector2((hx - 1) * sx, (hz - 1) * sz), Vector2((hx + 3) * sx, (hz + 3) * sz)])
	var leaks := []
	for r in rays:
		for h in [0.3, 1.5, 3.0, Arena.EDGE_HEIGHT - 0.3]:
			var q := PhysicsRayQueryParameters3D.create(Vector3(r[0].x, h, r[0].y), Vector3(r[1].x, h, r[1].y), Arena.WORLD_LAYER)
			q.hit_from_inside = true
			if space.intersect_ray(q).is_empty():
				leaks.append("%s at %.1f m" % [r[0], h])
	_ok(leaks.is_empty(), "the map edge is sealed: all %d rays (0.3 to %.1f m high, every 0.5 m, corners too) hit a cliff %s" % [rays.size() * 4, Arena.EDGE_HEIGHT - 0.3, str(leaks.slice(0, 4))])


func _check_nav() -> void:
	var region: NavigationRegion3D = arena.get_node("Built/Nav")
	var nm: NavigationMesh = region.navigation_mesh
	var top := -INF
	for v in nm.get_vertices():
		top = maxf(top, v.y)
	# the mesh floats up to two 0.25 m cells over the ground; a rock top would sit at 3 m
	_ok(nm.get_polygon_count() > 0 and top < 1.0, "nav mesh: %d polygons for a %.1f m agent, baked in %.0f ms, highest point %.2f m (no islands on rock or pillar tops)" % [nm.get_polygon_count(), Arena.NAV_AGENT_RADIUS, arena.nav_bake_ms, top])
	var spawns := {"blue": _feat("blue spawn").p, "red": _feat("red spawn").p}
	var unreachable := []
	for team in spawns:
		for f in arena.features:
			var reach: float = f.r + Arena.NAV_AGENT_RADIUS + 0.5 if f.kind in ["core", "tower"] else 0.3
			var w := _nav_walk(spawns[team], f.p)
			if w.x < 0.0 or w.y > reach:
				unreachable.append("%s to %s (%.1f m short)" % [team, f.name, w.y])
	_ok(unreachable.is_empty(), "on the nav mesh every feature can be reached from both spawns %s" % str(unreachable))
	var own_blue := _nav_walk(spawns.blue, _feat("blue side pit").p).x
	var own_red := _nav_walk(spawns.red, _feat("red side pit").p).x
	_ok(own_blue > 0.0 and absf(own_blue - own_red) < 0.5, "on the nav mesh own side pit is the same walk for both teams (%.1f m and %.1f m)" % [own_blue, own_red])
	var lane := _nav_walk(Arena.CORE + Vector2(0, -4), -Arena.CORE + Vector2(0, 4)).x
	print("  lane on the nav mesh, core front to core front: %.1f m, %.1f s" % [lane, lane / MOVE_SPEED])
	print("  walks from blue spawn on the nav mesh (a %.1f m agent, corners cut as tight as it fits):" % Arena.NAV_AGENT_RADIUS)
	for target in ["blue tower", "blue camp", "blue side pit", "plaza", "red side pit", "red tower", "red core"]:
		var best := INF
		for f in arena.features:
			if f.name == target:
				var w := _nav_walk(spawns.blue, f.p).x
				if w >= 0.0:
					best = minf(best, w)
		walks.append([target, best])
		print("    %-14s %6.1f m  %5.1f s" % [target, best, best / MOVE_SPEED])


func _nav_walk(a: Vector2, b: Vector2) -> Vector2: # x: path length (-1 if cut off), y: how far its end is from b
	var from := NavigationServer3D.map_get_closest_point(nav_map, Vector3(a.x, 0, a.y))
	var to := NavigationServer3D.map_get_closest_point(nav_map, Vector3(b.x, 0, b.y))
	var path := NavigationServer3D.map_get_path(nav_map, from, to, true)
	if path.is_empty() or path[path.size() - 1].distance_to(to) > 0.2:
		return Vector2(-1.0, INF)
	var length := 0.0
	for i in range(1, path.size()):
		length += path[i].distance_to(path[i - 1])
	return Vector2(length, Vector2(to.x, to.z).distance_to(b))


func _feat(name: String) -> Dictionary:
	for f in arena.features:
		if f.name == name:
			return f
	return {}


func _walk(a: Vector2, b: Vector2) -> float:
	var ia := _cell(a)
	var ib := _cell(b)
	if astar.is_point_solid(ia) or astar.is_point_solid(ib):
		return -1.0
	var path := astar.get_id_path(ia, ib)
	if path.is_empty():
		return -1.0
	var length := 0.0
	for i in range(1, path.size()):
		length += Vector2(path[i] - path[i - 1]).length()
	return length


# ---- sketch -------------------------------------------------------------------------------------------------

func _x(x: float) -> float:
	return (x + Arena.HALF_X + MARGIN) * PX


func _y(z: float) -> float: # +z (blue) at the bottom, so blue's camera looks up the page
	return (z + Arena.HALF_Z + MARGIN) * PX


func _circle(out: PackedStringArray, c: Vector2, r: float, attrs: String) -> void:
	out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" %s/>' % [_x(c.x), _y(c.y), r * PX, attrs])


func _text(out: PackedStringArray, x: float, y: float, s: String, attrs := "") -> void:
	out.append('<text x="%.1f" y="%.1f" %s>%s</text>' % [x, y, attrs, s])


func _write_sketch() -> void:
	var map_w := (Arena.HALF_X * 2 + MARGIN * 2) * PX
	var map_h := (Arena.HALF_Z * 2 + MARGIN * 2) * PX
	var full_w := map_w + 250.0
	var blue := "#" + Arena.BLUE.to_html(false)
	var red := "#" + Arena.RED.to_html(false)
	var out := PackedStringArray()
	out.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Verdana, sans-serif" font-size="11">' % [int(full_w), int(map_h), int(full_w), int(map_h)])
	out.append('<rect width="%d" height="%d" fill="#22261f"/>' % [int(full_w), int(map_h)])
	out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#7da35a"/>' % [_x(-Arena.HALF_X), _y(-Arena.HALF_Z), Arena.HALF_X * 2 * PX, Arena.HALF_Z * 2 * PX])
	var sw := Arena.HALF_X - Arena.PLAZA_R - Arena.WALL_THICK
	for sx in [-1.0, 1.0]:
		var x0: float = Arena.PLAZA_R + Arena.WALL_THICK if sx > 0 else -Arena.HALF_X
		out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#5aa6d6"/>' % [_x(x0), _y(-Arena.STREAM_HALF), sw * PX, Arena.STREAM_HALF * 2 * PX])
	_circle(out, Vector2.ZERO, Arena.PLAZA_R + 0.3, 'fill="#b8b0a0"')
	for t in [1.0, -1.0]:
		_circle(out, Arena.BASE_CENTRE * t, Arena.BASE_R, 'fill="#b8b0a0"')
	var pts := PackedStringArray()
	for p in Arena.LANE:
		pts.append("%.1f,%.1f" % [_x(p.x), _y(p.y)])
	out.append('<polyline points="%s" fill="none" stroke="#c8a26a" stroke-width="%.1f" stroke-linejoin="round" stroke-linecap="round"/>' % [" ".join(pts), Arena.PATH_WIDTH * PX])
	for f in arena.features:
		var col: String = blue if f.team == "blue" else red
		match f.kind:
			"spawn":
				_circle(out, f.p, f.r, 'fill="%s" fill-opacity="0.45"' % col)
			"pit":
				_circle(out, f.p, f.r, 'fill="#d99a48"')
			"camp":
				_circle(out, f.p, f.r, 'fill="#f2d24b" stroke="%s" stroke-width="2"' % col)
	for w in arena.walls:
		var c: Vector2 = w.c
		var u: Vector2 = w.u
		var n := Vector2(-u.y, u.x)
		var corners := PackedStringArray()
		for s in [Vector2(1, 1), Vector2(1, -1), Vector2(-1, -1), Vector2(-1, 1)]:
			var q: Vector2 = c + u * w.half_len * s.x + n * w.half_thick * s.y
			corners.append("%.1f,%.1f" % [_x(q.x), _y(q.y)])
		var fill := "#8a8f99" if w.h < Arena.WALL_HEIGHT else ("#3e4148" if w.h > Arena.WALL_HEIGHT else "#5f636c")
		out.append('<polygon points="%s" fill="%s"/>' % [" ".join(corners), fill])
	for r in arena.rocks:
		_circle(out, r.c, r.r, 'fill="#5f636c"')
	for f in arena.features:
		var col: String = blue if f.team == "blue" else red
		match f.kind:
			"tower":
				_circle(out, f.p, Arena.TOWER_RANGE, 'fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5 4"' % col)
				_circle(out, f.p, f.r, 'fill="%s" stroke="#111" stroke-width="1.5"' % col)
			"core":
				_circle(out, f.p, f.r, 'fill="%s" stroke="#111" stroke-width="2"' % col)
	var halo := 'stroke="#22261f" stroke-width="3" paint-order="stroke" fill="#ffffff" text-anchor="middle"'
	for f in arena.features:
		var label: String = f.kind
		if f.kind == "pit":
			label = "side pit"
		var dy: float = -(f.r + 1.5) * PX if f.kind in ["tower", "core"] else 4.0
		_text(out, _x(f.p.x), _y(f.p.y) + dy, label, halo)
	_text(out, _x(0), _y(-Arena.HALF_Z) - 4, "red base", halo + ' font-size="13" font-weight="bold"')
	_text(out, _x(0), _y(Arena.HALF_Z) + 14, "blue base (blue's camera looks up the page)", halo + ' font-size="12"')
	# legend
	var lx := map_w + 14.0
	var ly := 24.0
	var bold := 'fill="#ffffff" font-size="14" font-weight="bold"'
	var plain := 'fill="#e8e8e8"'
	_text(out, lx, ly, "First arena, blockout", bold)
	ly += 18
	_text(out, lx, ly, "proposal, 2026-11-04, not canon", plain)
	ly += 26
	var keys := [["#c8a26a", "lane path (lane is 14 m wall to wall)"], ["#5f636c", "wall 3 m / rock"], ["#8a8f99", "pit rim 1.5 m"], ["#3e4148", "cliff edge 6 m"], ["#b8b0a0", "paved plaza and bases"], ["#5aa6d6", "stream (looks only)"], ["#d99a48", "side pit (one per team)"], ["#f2d24b", "jungle camp"]]
	for k in keys:
		out.append('<rect x="%.1f" y="%.1f" width="14" height="10" fill="%s"/>' % [lx, ly - 9, k[0]])
		_text(out, lx + 20, ly, k[1], plain)
		ly += 17
	out.append('<circle cx="%.1f" cy="%.1f" r="6" fill="none" stroke="#ffffff" stroke-dasharray="3 2"/>' % [lx + 7, ly - 4])
	_text(out, lx + 20, ly, "tower range 12 m (placeholder)", plain)
	ly += 28
	_text(out, lx, ly, "Size %d x %d m, 180-degree turn" % [int(Arena.HALF_X * 2), int(Arena.HALF_Z * 2)], plain)
	ly += 17
	_text(out, lx, ly, "symmetry: each team sees the same map", plain)
	ly += 26
	_text(out, lx, ly, "Walks from blue spawn, nav mesh, 3.5 m/s", bold)
	ly += 18
	_text(out, lx, ly, "lane core to core: %.0f m, %.0f s" % [lane_length, lane_length / MOVE_SPEED], plain)
	for w in walks:
		ly += 17
		_text(out, lx, ly, "%s: %.0f m, %.0f s" % [w[0], w[1], w[1] / MOVE_SPEED], plain)
	ly += 26
	out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#ffffff" stroke-width="3"/>' % [lx, ly, lx + 10 * PX, ly])
	_text(out, lx + 10 * PX + 8, ly + 4, "10 m", plain)
	out.append("</svg>")
	var f := FileAccess.open(SKETCH, FileAccess.WRITE)
	f.store_string("\n".join(out))
	f.close()
	print("  sketch written: ", ProjectSettings.globalize_path(SKETCH))
