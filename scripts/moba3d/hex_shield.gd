class_name HexShield
extends Node3D
## The gorilla's hex shield and hex dome (Claude, 2026-11-04).
## Shield, Preston's look: the machine that gets it is ringed by a green hexagon circle shield.
## The three orbiting gem shields were removed on his note (2026-11-04, "Remove the three shield things that rotate").
## Dome: the same hex shell, larger and cut at the ground.
## Sizes and lengths are presentation placeholders; the numbers are Preston's to set.

const HEX := preload("res://art/fx/moba3d/hex_tile.png")
const SHELL := preload("res://shaders/hex_shell.gdshader")
const BUBBLE := preload("res://shaders/hex_bubble.gdshader") ## the shield on a 3D machine: a cartoon ship shield following its shape (2026-11-09)
const MAX_SEG := 40
const PX := 0.02 ## the shared 50 texels a metre

@export var dome := false
@export var radius := 1.1
@export var centre_height := 0.85 ## the shield's shell centre above the feet; the dome sits on the ground
@export var life := 3.0

var _t := 0.0
var _ending := false
var ward := false ## the ult dome's ward (proposal, 2026-11-09): the owner's side inside heals and cannot drop below 1 hp
var ward_owner: Node3D
var ward_heal_share := 0.06 ## of max hp a second
var _ward_tick := 0.0
var cage_all := false ## the ult cage (Preston, 2026-11-09): its wall holds everyone, allies included
var panel_hp: Array[float] = [] ## the ult wall's panels, each 0..1 of its health; a broken one (0) is a gap
var _panel_max := 60.0
var health := -1.0 ## a dome wall's health; below zero it cannot be worn down. The kit sets it (a placeholder)
static var _live := [] ## the domes standing now
var _mat: ShaderMaterial
var _shell: MeshInstance3D
var _skel: Skeleton3D ## the bubble follows this skeleton
var _segs: Array = [] ## [bone, child bone or -1, radius in skeleton space]
static var _radius_cache := {} ## per mesh set: the measured bone radii, so a recast costs nothing


## Puts a hex shield on a machine (it follows the machine, as a child).
static func shield(target: Node3D, life_s := 3.0) -> HexShield:
	var s := HexShield.new()
	s.life = life_s
	var spr := target.get_node_or_null("Sprite") as DirectionalSprite3D
	if spr != null:  # the shell was sized for an L machine; M and S machines get a smaller one (size classes, 2026-11-04)
		s.radius *= spr.size_scale()
		s.centre_height *= spr.size_scale()
	target.add_child(s)
	return s


## Raises a hex dome on the ground at pos.
static func raise_dome(parent: Node, pos: Vector3, radius_m := 3.2, life_s := 4.0) -> HexShield:
	var s := HexShield.new()
	s.dome = true
	s.radius = radius_m
	s.life = life_s
	parent.add_child(s)
	s.global_position = pos
	return s


## True while m stands inside a warding dome raised by its own side.
static func wards(m: Node3D) -> bool:
	for d in live_domes():
		if d.ward and is_instance_valid(d.ward_owner) and d._warded().has(m):
			var v: Vector3 = m.global_position - d.global_position
			if Vector2(v.x, v.z).length() <= d.radius:
				return true
	return false


## The hex domes standing now (not fading out).
static func live_domes() -> Array:
	return _live.filter(func(d): return is_instance_valid(d) and d.is_up())


func _ready() -> void:
	if dome:
		_live.append(self)
	elif _wear_bubble():
		return
	_mat = ShaderMaterial.new()
	_mat.shader = SHELL
	_mat.set_shader_parameter("hex_tex", HEX)
	# Repeats chosen so one hex texel is about one world texel at the equator (tile is 24x14 texels).
	_mat.set_shader_parameter("tiles", Vector2(roundf(TAU * radius / 0.5), roundf(PI * radius / 0.5 / 0.866)) * (1.0 if dome else 1.6))  # about one plate cell per half metre
	var sm := SphereMesh.new()
	sm.radius = radius
	sm.radial_segments = 48
	sm.rings = 24
	if dome:
		sm.is_hemisphere = true
		sm.height = radius
	else:
		sm.height = radius * 2.0 * 0.9
	sm.material = _mat
	_shell = MeshInstance3D.new()
	_shell.mesh = sm
	_shell.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_shell.position.y = 0.0 if dome else centre_height
	add_child(_shell)
	_mat.set_shader_parameter("density", clamp(2.2 / radius, 0.3, 1.0) if dome else 1.0)
	_mat.set_shader_parameter("y_min", 0.0 if dome else -sm.height * 0.5)
	_mat.set_shader_parameter("y_max", radius if dome else sm.height * 0.5)
	# Builds up from the ground like plates locking in (look pass 2026-11-09), with a short pop and a flash.
	_shell.scale = Vector3.ONE * 0.85
	_mat.set_shader_parameter("flash", 1.0)
	_mat.set_shader_parameter("rise", 0.0)
	var tw := create_tween()
	tw.tween_method(func(v: float): _mat.set_shader_parameter("rise", v), 0.0, 1.0, 0.32 if dome else 0.2)
	tw.parallel().tween_callback(func(): _shell.scale = Vector3.ONE).set_delay(0.12)
	tw.tween_method(func(v: float): _mat.set_shader_parameter("flash", v), 1.0, 0.0, 0.25)
	tw.tween_method(func(v: float): _mat.set_shader_parameter("calm", v), 0.0, 1.0, 0.2)  # then rim-only, as the bubble (2026-11-09)


func _process(delta: float) -> void:
	_t += delta
	if _skel != null:
		_follow()
	else:
		_mat.set_shader_parameter("drift", _t * 0.12)
	if ward and not _ending:
		_mat.set_shader_parameter("ward", 1.0)
		_ward_tick += delta
		if _ward_tick >= 0.5:
			_ward_tick -= 0.5
			_ward_pulse()
	if not _ending:  # game feel: three flickers in the last half second say "about to drop"
		var left := life - _t
		_mat.set_shader_parameter("fade", 0.35 if left < 0.5 and fmod(left, 1.0 / 6.0) < 1.0 / 12.0 else 1.0)
	if not _ending and _t >= life:
		end()


## The owner and its side (outside a match the side is the kit_ally group, which leaves the owner out).
func _warded() -> Array:
	var side := MatchTeams.allies_of(ward_owner)
	if not side.has(ward_owner):
		side.append(ward_owner)
	return side


## Every half second: heal the owner's side inside, and a pulse runs up the shell.
func _ward_pulse() -> void:
	if not is_instance_valid(ward_owner):
		return
	for a in _warded():
		var v: Vector3 = a.global_position - global_position
		if Vector2(v.x, v.z).length() <= radius and a.has_method("heal") and "max_hp" in a:
			a.heal(a.max_hp * ward_heal_share * 0.5, ward_owner)
	var tw := create_tween()
	tw.tween_method(func(v: float): _mat.set_shader_parameter("pulse", v), 0.0, 1.0, 0.45)


## A hit landing on the shield: a short flash.
func hit(at := Vector3.INF) -> void:
	if _ending:
		return
	if _skel != null or at != Vector3.INF:  # game feel: an absorbed hit lights the cells round the impact for 0.12 s, not the whole shell
		_mat.set_shader_parameter("hit_pos", at if at != Vector3.INF else get_parent().global_position + Vector3.UP)
		var rt := create_tween()
		rt.tween_method(func(v: float): _mat.set_shader_parameter("hit_k", v), 1.0, 0.0, 0.12)
		return
	var tw := create_tween()
	tw.tween_method(func(v: float): _mat.set_shader_parameter("flash", v), 0.7, 0.0, 0.15)


## An enemy shot hits the dome's wall: the flash, and the health goes down; at zero the dome breaks early
## (Preston, 2026-11-04: "Wall can be damaged of course").
func damage(amount: float, at := Vector3.INF) -> void:
	if _ending:
		return
	hit(at)
	if not panel_hp.is_empty() and at != Vector3.INF:  # a panelled wall: only the struck panel takes it
		var i := panel_at(at)
		if panel_hp[i] <= 0.0:
			return
		panel_hp[i] = maxf(panel_hp[i] - amount / _panel_max, 0.0)
		_mat.set_shader_parameter("panel_hp", panel_hp)
		if panel_hp[i] <= 0.0:
			Fx3D.spawn(get_parent(), "deflect_spark", at, 0.3)
		return
	if health < 0.0:
		return
	health -= amount
	if health <= 0.0:
		end()


func is_up() -> bool:
	return not _ending


func _exit_tree() -> void:
	_live.erase(self)


## Preston (2026-11-09): "a layer around the model like how ship shields are in cartoons, with the hex pattern on it".
## On a 3D machine the shield is a smooth bubble that follows its shape at a distance: a rounded capsule per bone,
## sized from the mesh around that bone, melted into one shape by the shader. 2D sprite machines keep the round shell.
func _wear_bubble() -> bool:
	var found := get_parent().find_children("*", "Skeleton3D", true, false)
	if found.is_empty():
		return false
	_skel = found[0]
	_segs = _measure(_skel)
	if _segs.is_empty():
		return false
	_mat = ShaderMaterial.new()
	_mat.shader = BUBBLE
	var bm := BoxMesh.new()
	bm.material = _mat
	_shell = MeshInstance3D.new()
	_shell.mesh = bm
	_shell.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_shell.top_level = true
	add_child(_shell)
	_follow()
	# Locks on from the feet up with a flash, like a ship's shield coming online.
	_mat.set_shader_parameter("flash", 1.0)
	_mat.set_shader_parameter("rise", 0.0)
	var tw := create_tween()
	tw.tween_method(func(v: float): _mat.set_shader_parameter("rise", v), 0.0, 1.0, 0.22)
	tw.tween_method(func(v: float): _mat.set_shader_parameter("flash", v), 1.0, 0.0, 0.25)
	# game feel (2026-11-09): the lock-on shows every cell, then it calms to rim-only so the machine reads
	tw.tween_method(func(v: float): _mat.set_shader_parameter("calm", v), 0.0, 1.0, 0.2)
	return true


## One capsule per bone that has mesh on it: from the bone to its first child, as thick as the farthest vertex
## the bone carries (rest pose). The biggest MAX_SEG are kept.
func _measure(sk: Skeleton3D) -> Array:
	var meshes: Array = []
	for n in sk.find_children("*", "MeshInstance3D", true, false):
		var m := n as MeshInstance3D
		if m.mesh != null and m.skin != null and not _is_fx(m):
			meshes.append(m)
	var key := ",".join(meshes.map(func(m): return str(m.mesh.get_instance_id())))
	if _radius_cache.has(key):
		return _radius_cache[key]
	var child := {}
	for b in sk.get_bone_count():
		var par := sk.get_bone_parent(b)
		if par >= 0 and not child.has(par):
			child[par] = b
	var radius := {}
	for m in meshes:
		var skin: Skin = m.skin
		var bind_bone: Array = []
		for j in skin.get_bind_count():
			var bb := skin.get_bind_bone(j)
			bind_bone.append(bb if bb >= 0 else sk.find_bone(skin.get_bind_name(j)))
		for si in m.mesh.get_surface_count():
			var arr: Array = m.mesh.surface_get_arrays(si)
			var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var bones = arr[Mesh.ARRAY_BONES]
			var weights = arr[Mesh.ARRAY_WEIGHTS]
			if bones == null or weights == null or verts.is_empty():
				continue
			var per: int = bones.size() / verts.size()
			for vi in range(0, verts.size(), 2):
				var best := 0
				for k in per:
					if weights[vi * per + k] > weights[vi * per + best]:
						best = k
				var j: int = int(bones[vi * per + best])
				var b: int = bind_bone[j]
				if b < 0:
					continue
				var p: Vector3 = sk.get_bone_global_rest(b) * (skin.get_bind_pose(j) * verts[vi])
				var a: Vector3 = sk.get_bone_global_rest(b).origin
				var e: Vector3 = sk.get_bone_global_rest(child[b]).origin if child.has(b) else a
				var d := p.distance_to(Geometry3D.get_closest_point_to_segment(p, a, e))
				radius[b] = maxf(radius.get(b, 0.0), d)
	var segs: Array = []
	for b in radius:
		segs.append([b, child.get(b, -1), radius[b]])
	segs.sort_custom(func(x, y): return x[2] > y[2])
	segs = segs.slice(0, MAX_SEG)
	_radius_cache[key] = segs
	return segs


## Every frame: the capsules move with the bones, and the box the bubble is drawn in covers them.
func _follow() -> void:
	if not is_instance_valid(_skel):
		return
	var g := _skel.global_transform
	var sc := g.basis.get_scale().x
	var a: Array[Vector4] = []  # plain arrays: the OpenGL renderer drops PackedVector4Array uniforms
	var b: Array[Vector4] = []
	var box := AABB()
	for i in _segs.size():
		var s: Array = _segs[i]
		var p0: Vector3 = g * _skel.get_bone_global_pose(s[0]).origin
		var p1: Vector3 = g * _skel.get_bone_global_pose(s[1]).origin if s[1] >= 0 else p0
		var r: float = s[2] * sc
		a.append(Vector4(p0.x, p0.y, p0.z, r))
		b.append(Vector4(p1.x, p1.y, p1.z, 0.0))
		var grow := Vector3.ONE * (r + 0.5)
		var sb := AABB(p0 - grow, grow * 2.0).merge(AABB(p1 - grow, grow * 2.0))
		box = sb if i == 0 else box.merge(sb)
	_mat.set_shader_parameter("seg_a", a)
	_mat.set_shader_parameter("seg_b", b)
	_mat.set_shader_parameter("seg_n", _segs.size())
	_mat.set_shader_parameter("origin", get_parent().global_position)
	_mat.set_shader_parameter("y_min", box.position.y + 0.4)
	_mat.set_shader_parameter("y_max", box.end.y - 0.4)
	_shell.global_transform = Transform3D(Basis.from_scale(box.size), box.get_center())


## Splits the wall into n panels round the dome, each with hp of health (the ult; Preston, 2026-11-09).
func make_panels(n: int, hp: float) -> void:
	_panel_max = hp
	panel_hp.clear()
	for i in n:
		panel_hp.append(1.0)
	_mat.set_shader_parameter("panel_n", float(n))
	_mat.set_shader_parameter("panel_hp", panel_hp)


## Which panel the wall has at world point p (by its angle round the dome).
func panel_at(p: Vector3) -> int:
	var a := atan2(p.z - global_position.z, p.x - global_position.x)
	return clampi(int(floor((a + PI) / TAU * panel_hp.size())), 0, panel_hp.size() - 1)


## Whether the wall stands at world point p: false through a broken panel's gap.
func blocks_at(p: Vector3) -> bool:
	return panel_hp.is_empty() or panel_hp[panel_at(p)] > 0.0


## Effect meshes (other shields, puffs) never wear the hull.
func _is_fx(m: Node) -> bool:
	var p := m.get_parent()
	while p != null and p != get_parent():
		if p is HexShield:
			return true
		p = p.get_parent()
	return false


## The shield runs out or breaks: flash, then the shell fades.
func end() -> void:
	if _ending:
		return
	_ending = true
	var tw := create_tween()
	tw.tween_method(func(v: float): _mat.set_shader_parameter("flash", v), 0.0, 1.0, 0.08)
	tw.tween_method(func(v: float): _mat.set_shader_parameter("fade", v), 1.0, 0.0, 0.3)
	tw.tween_callback(queue_free)
