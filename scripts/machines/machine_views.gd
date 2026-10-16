extends RefCounted
## Multi-view machines (Claude, 2026-10-11; Preston: "a multi-view wiring for our zoids so Codex can fill those
## in and we can do rotation camera views"). Plan and synthesis: docs/plan/multi-view-machines.md.
##
## Every machine has eight drawn views, one per 45 degrees of facing *relative to the camera*:
##   s = toward the camera, n = away, e = facing screen right, w = screen left, and the diagonals.
## The world stores where a machine faces (0 = east, 90 = north, degrees); the camera has a yaw. The view shown
## is the facing minus the camera yaw, snapped to the nearest 45. Turn the camera and every machine turns on
## screen with it.
##
## Art slots: res://art/machines/<id>/views/<dir>.png, VIEW_SIZE pixels, the machine's feet at ANCHOR.
## Missing art falls back to the mirror of the opposite side (w from e, nw from ne, sw from se), then to a
## placeholder: the machine as coloured 3D blocks seen from that angle, which is also Codex's outline guide.

const Machines := preload("res://scripts/data/machines.gd")

const DIRS := ["e", "ne", "n", "nw", "w", "sw", "s", "se"]   # index k = facing k * 45 degrees from east
const MIRROR := {"w": "e", "nw": "ne", "sw": "se", "e": "w", "ne": "nw", "se": "sw"}
const VIEW_SIZE := Vector2i(96, 72)   # room for a long machine turned diagonally toward the camera
const ANCHOR := Vector2i(48, 54)         # where the feet touch the ground (the middle of the footprint)
const ELEVATION := 30.0                  # the camera looks down this many degrees (a GBA-style raised side view)


## The view to draw for a machine facing `facing_deg` in the world, seen by a camera turned `camera_deg`.
static func dir_for(facing_deg: float, camera_deg: float = 0.0) -> String:
	var rel := fposmod(facing_deg - camera_deg, 360.0)
	return DIRS[int(round(rel / 45.0)) % 8]


static func slot_path(id: String, dir: String) -> String:
	return "res://art/machines/%s/views/%s.png" % [id, dir]


## A machine's own view canvas: size, feet point and palette, from art/machines/<id>/views/views.json (written
## by tools/art/import_views.py, which puts every view's feet on the same point). A big machine gets a bigger
## canvas. Machines with no imported art use the shared VIEW_SIZE and ANCHOR.
static func view_info(id: String) -> Dictionary:
	var path := "res://art/machines/%s/views/views.json" % id
	if FileAccess.file_exists(path):
		var d = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(d) == TYPE_DICTIONARY and d.has("size") and d.has("anchor"):
			return {"size": Vector2i(d.size[0], d.size[1]), "anchor": Vector2i(d.anchor[0], d.anchor[1]),
				"palette": d.get("palette", []), "mirrored": d.get("mirrored", [])}
	return {"size": VIEW_SIZE, "anchor": ANCHOR, "palette": [], "mirrored": []}


static func anchor(id: String) -> Vector2i:
	return view_info(id).anchor


## Which art to use for a view, given which slots exist: {"path": String, "flip": bool}; path "" = placeholder.
## `exists` is a Callable(path) -> bool so the check can test it without files on disk.
static func resolve(id: String, dir: String, exists: Callable = Callable()) -> Dictionary:
	var has := exists if exists.is_valid() else func(p: String) -> bool: return ResourceLoader.exists(p)
	if has.call(slot_path(id, dir)):
		return {"path": slot_path(id, dir), "flip": false}
	if MIRROR.has(dir) and has.call(slot_path(id, MIRROR[dir])):
		return {"path": slot_path(id, MIRROR[dir]), "flip": true}
	return {"path": "", "flip": false}


# ---------------------------------------------------------------------------------------------------------
# Placeholder bodies: boxes in the machine's own space, in pixels. x forward (the head), y to its left,
# z up; feet at z = 0. Each box: [centre, size, colour key]. A sketch of proportions only, not a design.
const BODIES := {
	"cat": [   # Tiger type: long low body, banded back plates (the stripes), jaw gun, stabilizer tail
		[Vector3(0, 0, 22), Vector3(36, 14, 12), "main"],
		# tiger stripes: thin, unevenly spaced, from the spine part way down each side, not full rings
		[Vector3(-12, 0, 25.4), Vector3(2, 14.6, 6), "trim", "decal"], [Vector3(-5, 0, 24.4), Vector3(2, 14.6, 8), "trim", "decal"],
		[Vector3(1, 0, 25.9), Vector3(2, 14.6, 5), "trim", "decal"], [Vector3(8, 0, 24.9), Vector3(2, 14.6, 7), "trim", "decal"],
		[Vector3(14, 0, 26.4), Vector3(1.5, 14.6, 4), "trim", "decal"],
		[Vector3(22, 0, 29), Vector3(12, 11, 11), "main"], [Vector3(26, 0, 22), Vector3(8, 4, 3), "frame"],
		[Vector3(13, 5, 8), Vector3(6, 4, 16), "frame"], [Vector3(13, -5, 8), Vector3(6, 4, 16), "frame"],
		[Vector3(-13, 5, 8), Vector3(7, 5, 16), "frame_dark"], [Vector3(-13, -5, 8), Vector3(7, 5, 16), "frame_dark"],
		[Vector3(-24, 0, 26), Vector3(14, 3, 3), "accent"],
	],
	"raptor": [   # Raptor type: two legs, level body, tail counterweight with the launcher pod at its tip
		[Vector3(0, 0, 26), Vector3(26, 12, 12), "main"], [Vector3(0, 0, 21), Vector3(26, 12, 3), "trim"],
		[Vector3(18, 0, 34), Vector3(13, 9, 9), "main"], [Vector3(24, 0, 31), Vector3(5, 7, 3), "trim"],
		[Vector3(-1, 5, 10), Vector3(7, 4, 20), "frame"], [Vector3(-1, -5, 10), Vector3(7, 4, 20), "frame_dark"],
		[Vector3(-20, 0, 28), Vector3(16, 4, 4), "frame"], [Vector3(-30, 0, 28), Vector3(6, 6, 6), "accent"],
	],
	"bird": [   # Hawk type: small body, louvred wings, guns in the wing roots, tucked talons
		[Vector3(0, 0, 30), Vector3(24, 10, 9), "main"], [Vector3(14, 0, 34), Vector3(9, 7, 7), "main"],
		[Vector3(19, 0, 33), Vector3(5, 3, 2), "accent"],
		[Vector3(-2, 15, 33), Vector3(14, 20, 2), "trim"], [Vector3(-2, -15, 33), Vector3(14, 20, 2), "trim"],
		[Vector3(5, 6, 31), Vector3(7, 2, 2), "frame"], [Vector3(5, -6, 31), Vector3(7, 2, 2), "frame"],
		[Vector3(0, 3, 19), Vector3(3, 3, 12), "accent"], [Vector3(0, -3, 19), Vector3(3, 3, 12), "accent"],
		[Vector3(-16, 0, 30), Vector3(10, 8, 2), "frame"],
	],
	"shoebill": [   # tall wading bird: long legs, upright body, a huge broad bill, broad folded wings
		[Vector3(-2, 0, 30), Vector3(16, 12, 16), "main"], [Vector3(-3, 0, 31), Vector3(14, 13, 10), "trim", "decal"],
		[Vector3(6, 0, 42), Vector3(8, 8, 10), "main"], [Vector3(13, 0, 44), Vector3(10, 9, 9), "main"],
		[Vector3(23, 0, 42), Vector3(12, 8, 6), "accent"], [Vector3(29, 0, 40), Vector3(2, 4, 4), "frame"],
		[Vector3(-1, 3, 11), Vector3(3, 3, 22), "frame"], [Vector3(-1, -3, 11), Vector3(3, 3, 22), "frame_dark"],
		[Vector3(1, 3, 1), Vector3(8, 4, 2), "frame"], [Vector3(1, -3, 1), Vector3(8, 4, 2), "frame_dark"],
		[Vector3(-11, 0, 28), Vector3(6, 10, 8), "trim"],
	],
	"pangolin": [   # low body under overlapping scale bands, small pointed head, long heavy tail
		[Vector3(0, 0, 14), Vector3(28, 16, 14), "main"],
		[Vector3(-10, 0, 15), Vector3(3, 16.6, 14.6), "trim", "decal"], [Vector3(-3, 0, 15), Vector3(3, 16.6, 14.6), "trim", "decal"],
		[Vector3(4, 0, 15), Vector3(3, 16.6, 14.6), "trim", "decal"],
		[Vector3(17, 0, 11), Vector3(9, 8, 8), "main"], [Vector3(23, 0, 9), Vector3(5, 4, 4), "accent"],
		[Vector3(-22, 0, 9), Vector3(18, 9, 8), "main"], [Vector3(-33, 0, 6), Vector3(8, 6, 5), "trim"],
		[Vector3(9, 6, 4), Vector3(5, 4, 8), "frame"], [Vector3(9, -6, 4), Vector3(5, 4, 8), "frame"],
		[Vector3(-8, 6, 4), Vector3(5, 4, 8), "frame_dark"], [Vector3(-8, -6, 4), Vector3(5, 4, 8), "frame_dark"],
	],
	"hippo": [   # compact barrel body, broad head with the jaw and tusks, short legs, jet valves on the snout
		[Vector3(-2, 0, 15), Vector3(26, 20, 16), "main"], [Vector3(-2, 0, 9), Vector3(26.6, 20.6, 4), "trim", "decal"],
		[Vector3(16, 0, 17), Vector3(12, 18, 12), "main"], [Vector3(20, 0, 10), Vector3(9, 16, 4), "accent"],
		[Vector3(22, 5, 23), Vector3(4, 3, 3), "frame"], [Vector3(22, -5, 23), Vector3(4, 3, 3), "frame"],
		[Vector3(11, 8, 4), Vector3(6, 5, 8), "frame"], [Vector3(11, -8, 4), Vector3(6, 5, 8), "frame"],
		[Vector3(-12, 8, 4), Vector3(6, 5, 8), "frame_dark"], [Vector3(-12, -8, 4), Vector3(6, 5, 8), "frame_dark"],
		[Vector3(-16, 0, 17), Vector3(4, 3, 3), "trim"],
	],
	"ape": [   # Gorilla type: knuckle-walker, high shoulders, bulwark chest plate, ballast rack on its back
		[Vector3(-7, 0, 22), Vector3(16, 20, 14), "main"], [Vector3(9, 0, 30), Vector3(16, 28, 18), "main"],
		[Vector3(18, 0, 28), Vector3(3, 20, 14), "accent"], [Vector3(19, 0, 41), Vector3(10, 10, 9), "trim"],
		[Vector3(15, 15, 15), Vector3(8, 8, 26), "frame"], [Vector3(15, -15, 15), Vector3(8, 8, 26), "frame"],
		[Vector3(17, 15, 3), Vector3(11, 10, 6), "accent"], [Vector3(17, -15, 3), Vector3(11, 10, 6), "accent"],
		[Vector3(-9, 7, 8), Vector3(8, 7, 16), "frame_dark"], [Vector3(-9, -7, 8), Vector3(8, 7, 16), "frame_dark"],
		[Vector3(-3, 0, 39), Vector3(12, 16, 4), "frame"],
		[Vector3(-3, 4, 43), Vector3(5, 5, 5), "trim"], [Vector3(-3, -4, 43), Vector3(5, 5, 5), "trim"],
	],
}


## A machine's colours: its own scheme (machines.gd "colours"), on the shared gunmetal frame.
static func colours(id: String) -> Dictionary:
	var d: Dictionary = Machines.MACHINES[id]
	var p: Dictionary = Machines.PALETTE
	var c: Dictionary = d.get("colours", {})
	var player: bool = d.faction == "player"
	return {"main": Color(c.get("main", p.player_main if player else p.rival_main)),
		"trim": Color(c.get("trim", p.player_trim if player else p.rival_trim)),
		"accent": Color(c.get("accent", p.light)), "light": Color(c.get("light", p.light)),
		"frame": p.frame, "frame_dark": p.frame_dark}


## The placeholder as filled polygons in view-canvas pixels, back to front: [[PackedVector2Array, Color], ...].
## `rel_deg` is the facing relative to the camera (0 = screen right, 270 = toward the camera).
static func placeholder_polys(id: String, rel_deg: float) -> Array:
	var animal: String = Machines.MACHINES[id].animal
	var boxes: Array = BODIES.get(animal, BODIES["cat"])
	var cols := colours(id)
	var a := deg_to_rad(rel_deg)
	var e := deg_to_rad(ELEVATION)
	var to_viewer := Vector3(0, -cos(e), sin(e))   # from the scene toward the camera (south and up)
	# Boxes are drawn whole, far to near. A box marked "decal" (stripes, markings) belongs to the box before
	# it and is drawn straight after it, so it always sits on that box's surface. Sorting single faces instead
	# let the body paint over its own stripes in the diagonal views (Preston, 2026-10-11).
	var groups: Array = []   # [depth, [box, decal, ...]]
	for b in boxes:
		if b.size() > 3 and b[3] == "decal" and not groups.is_empty():
			groups[-1][1].append(b)
		else:
			groups.append([_turn(b[0], a).y, [b]])
	groups.sort_custom(func(p: Array, q: Array) -> bool: return p[0] > q[0])   # far (north) first
	var out: Array = []
	for g in groups:
		for b in g[1]:
			out.append_array(_box_faces(b, cols[b[2]], a, e, to_viewer, g[1][0]))
	return out


## The visible faces of one box as [[points, colour], ...]. A box is convex, so its faces never overlap.
static func _box_faces(b: Array, col: Color, a: float, e: float, to_viewer: Vector3, parent: Array = []) -> Array:
	var c: Vector3 = b[0]
	var h: Vector3 = b[1] * 0.5
	# Five faces (the underside never shows) as (outward normal, four corners), in the machine's space.
	var quads := [
		[Vector3(0, 0, 1), [Vector3(-1, -1, 1), Vector3(1, -1, 1), Vector3(1, 1, 1), Vector3(-1, 1, 1)]],
		[Vector3(1, 0, 0), [Vector3(1, -1, -1), Vector3(1, 1, -1), Vector3(1, 1, 1), Vector3(1, -1, 1)]],
		[Vector3(-1, 0, 0), [Vector3(-1, 1, -1), Vector3(-1, -1, -1), Vector3(-1, -1, 1), Vector3(-1, 1, 1)]],
		[Vector3(0, 1, 0), [Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, 1, 1), Vector3(1, 1, 1)]],
		[Vector3(0, -1, 0), [Vector3(-1, -1, -1), Vector3(1, -1, -1), Vector3(1, -1, 1), Vector3(-1, -1, 1)]],
	]
	var out: Array = []
	var decal: bool = b.size() > 3 and b[3] == "decal" and not parent.is_empty()
	for q in quads:
		if decal and not _on_surface(b, parent, q[0]):
			continue   # a marking's face inside the body it sits on never shows (stripe ends, a belly band's top)
		var lit := _turn(q[0], a).dot(to_viewer)
		if lit <= 0.001:
			continue   # facing away from the camera
		var pts := PackedVector2Array()
		for corner in q[1]:
			pts.append(_project(_turn(c + corner * h, a), e))
		# Upper-left light: tops brightest, sides shaded by how squarely they face the camera.
		var shade := 1.0 if q[0].z > 0.5 else 0.62 + 0.3 * clampf(lit, 0.0, 1.0)
		out.append([pts, Color(col.r * shade, col.g * shade, col.b * shade, 1.0)])
	return out


## Turn a point of the machine's space to face `a` radians (0 = east) in a view where y points north.
static func _turn(p: Vector3, a: float) -> Vector3:
	return Vector3(p.x * cos(a) - p.y * sin(a), p.x * sin(a) + p.y * cos(a), p.z)


## World point (x east, y north, z up) to view-canvas pixels, seen from the south and above.
static func _project(w: Vector3, e: float) -> Vector2:
	return Vector2(ANCHOR.x + w.x, ANCHOR.y - w.z * cos(e) - w.y * sin(e))


## Where a ground point (world x east, y north) lands on screen for a camera turned `camera_deg`, relative
## to the screen point `centre`. Used to place machines and draw the ground as the camera turns.
static func ground_to_screen(p: Vector2, camera_deg: float, centre: Vector2) -> Vector2:
	var r := p.rotated(deg_to_rad(-camera_deg))
	return centre + Vector2(r.x, -r.y * sin(deg_to_rad(ELEVATION)))


## How far back a ground point is for this camera (bigger = farther = drawn first).
static func ground_depth(p: Vector2, camera_deg: float) -> float:
	return p.rotated(deg_to_rad(-camera_deg)).y


## Whether a marking's face (outward normal n) lies on or outside the matching face of the box it sits on.
static func _on_surface(decal: Array, parent: Array, n: Vector3) -> bool:
	var reach: float = (decal[0] + decal[1] * 0.5 * n).dot(n)
	var body: float = (parent[0] + parent[1] * 0.5 * n).dot(n)
	return reach >= body - 0.01
