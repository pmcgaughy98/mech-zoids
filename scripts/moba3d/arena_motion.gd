class_name ArenaMotion
## Moving machines, dummies and shots through the arena without passing through its walls (Claude, 2026-11-04, game
## feel lane; agreed with the map lane in docs/plan/moba-arena-layout-2026-11-04.md). Nothing here is a physics body,
## so the Player and the dummies stay Node3D. A sphere is swept along the move against the arena's StaticBody3D walls;
## where it stops, the rest of the move turns to run along the wall, so a move into a wall at an angle slides.
## Structure studied, not copied: Doom's P_XYMovement and P_SlideMove (linuxdoom-1.10 p_mobj.c, p_map.c). A blocked
## player slides along the wall line it hit; a blocked missile stops. Doom also halves big moves so fast things can't
## skip a thin wall; a swept cast (cast_motion) covers the whole move instead. A first version slid one axis at a time
## (Doom's "stairstep" fallback); it snagged on the curved base walls, so the slide follows the wall's normal.

## The collision layers the arena's solid things sit on: the blockout's WORLD_LAYER, layer 1 (map lane, 2026-11-04).
## The ground body is on layer 2, for the nav bake, so the cast never meets it.
static var wall_mask := 1
## The sphere's lowest point above the feet: anything lower than this never stops a move.
const LIFT := 0.25
const SLIDES := 2 ## after the first stop, how many times the rest of the move may turn along a wall

static var _queries := {}


## Where something with this radius ends up moving `motion` from `from`. The height is not tested: machines and
## dummies stay on the ground, and their sprites carry any hop.
static func slide(node: Node3D, from: Vector3, motion: Vector3, radius: float) -> Vector3:
	var space := _space(node)
	if space == null:
		return from + motion
	var q := _query(radius)
	var p := _push_out(space, q, from, radius)
	var m := Vector3(motion.x, 0.0, motion.z)
	for i in SLIDES + 1:
		if m.length_squared() < 1e-10:
			break
		q.transform = Transform3D(Basis(), _centre(p, radius))
		q.motion = m
		var r := space.cast_motion(q)
		q.motion = Vector3.ZERO
		var part: float = 1.0 if r.size() < 2 else r[0]
		p += m * part
		if part >= 1.0:
			break
		q.transform = Transform3D(Basis(), _centre(p + m * (r[1] - r[0]), radius))  # where it would touch
		var n := _normal(space, q, p + m * (r[1] - r[0]), radius)
		var rest := m * (1.0 - part)
		m = rest - n * rest.dot(n) if n != Vector3.ZERO else Vector3.ZERO
	p = _push_out(space, q, p, radius)
	p.y = from.y + motion.y
	return p


## Out of any wall it overlaps (a rounding overlap after a stop, or placed inside one): stepped out along the wall's
## normal by the least of a few distances that clears it. It never moves anything further in.
static func _push_out(space: PhysicsDirectSpaceState3D, q: PhysicsShapeQueryParameters3D, p: Vector3,
		radius: float) -> Vector3:
	q.motion = Vector3.ZERO
	for k in 3:
		q.transform = Transform3D(Basis(), _centre(p, radius))
		var n := _normal(space, q, p, radius)
		if n == Vector3.ZERO:
			return p
		var moved := false
		for d in [0.005, 0.02, 0.06, 0.15, 0.4]:
			q.transform = Transform3D(Basis(), _centre(p + n * d, radius))
			if space.intersect_shape(q, 1).is_empty():
				p += n * d
				moved = true
				break
		if not moved:
			return p
	return p


## True when a sphere of this radius at p touches a wall.
static func blocked(node: Node3D, p: Vector3, radius: float) -> bool:
	var space := _space(node)
	if space == null:
		return false
	var q := _query(radius)
	q.transform = Transform3D(Basis(), _centre(p, radius))
	q.motion = Vector3.ZERO
	return not space.intersect_shape(q, 1).is_empty()


## The first wall point on the segment a-b (both already at the height that matters), or {} if it is clear.
static func ray(node: Node3D, a: Vector3, b: Vector3) -> Dictionary:
	var space := _space(node)
	if space == null:
		return {}
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(a, b, wall_mask))


## The flat direction from the wall's contact point to the sphere's centre, or zero when nothing touches.
## Taken from the contact point, not the reported normal, so its sign can't be wrong.
static func _normal(space: PhysicsDirectSpaceState3D, q: PhysicsShapeQueryParameters3D, p: Vector3,
		radius: float) -> Vector3:
	var info := space.get_rest_info(q)
	if info.is_empty():
		return Vector3.ZERO
	var c := _centre(p, radius)
	var pt: Vector3 = info.get("point", c)
	var n := Vector3(c.x - pt.x, 0.0, c.z - pt.z)
	if n.length() < 0.0001:
		var rn: Vector3 = info.get("normal", Vector3.ZERO)
		n = Vector3(rn.x, 0.0, rn.z)
	return n.normalized()


static func _centre(p: Vector3, radius: float) -> Vector3:
	return p + Vector3.UP * (LIFT + radius)


static func _space(node: Node3D) -> PhysicsDirectSpaceState3D:
	if node == null or not node.is_inside_tree():
		return null
	return node.get_world_3d().direct_space_state


static func _query(radius: float) -> PhysicsShapeQueryParameters3D:
	var key := snappedf(radius, 0.001)
	var q: PhysicsShapeQueryParameters3D = _queries.get(key)
	if q == null:
		var s := SphereShape3D.new()
		s.radius = radius
		q = PhysicsShapeQueryParameters3D.new()
		q.shape = s
		q.collide_with_areas = false
		q.collide_with_bodies = true
		_queries[key] = q
	q.collision_mask = wall_mask
	return q
