class_name KitFeel
extends RefCounted
## Hit feel for the kits (game feel lane, 2026-11-05; Preston: "feels plain and can't really feel the move").
## Screen shake rides on the camera's h_offset and v_offset, which nothing else in the project sets, so it works
## under chase_camera_3d.gd without changing it (the camera lane owns that file). The kits call shake() from their
## impact signal. Hitstop is done in the kits themselves: they hold the contact frame for a moment before the target
## flies.


## Adds shake to the camera that is drawing from. 0.35 is a stomp, 0.7 a slam, 1.0 the heaviest hit.
static func shake(from: Node, strength: float) -> void:
	if from == null or not from.is_inside_tree():
		return
	var cam := from.get_viewport().get_camera_3d()
	if cam == null:
		return
	var s := cam.get_node_or_null("KitShake") as Shaker
	if s == null:
		s = Shaker.new()
		s.name = "KitShake"
		cam.add_child(s)
	s.trauma = minf(s.trauma + strength, 1.0)



## Kicks the picture a few pixels the way a hit travels (camera lane, 2026-11-06; Preston: "Kick the camera along the
## punch. A nudge of a couple of pixels in the punch's direction, rather than a random shake, reads as a hit instead of
## a rumble"). dir is the hit's world direction. Seen on screen it is turned into a screen direction, so a punch away
## from the camera kicks the picture up and one to the right kicks it right, always by px game pixels. The jump is
## immediate and eases back over time seconds. It adds to any shake running, and a new kick replaces the last.
## The picture moves with the punch, so the camera itself moves the other way: moving the camera along the punch
## would slide the target back toward the attacker. KICK_SIGN = -1.0 flips it.
const KICK_SIGN := 1.0
static func kick(from: Node, dir: Vector3, px := 2.0, time := 0.15) -> void:
	if from == null or not from.is_inside_tree():
		return
	var cam := from.get_viewport().get_camera_3d()
	if cam == null:
		return
	var on_screen := Vector2(dir.dot(cam.global_basis.x), dir.dot(cam.global_basis.y))
	if on_screen.length() < 0.0001:
		return
	var s := cam.get_node_or_null("KitShake") as Shaker
	if s == null:
		s = Shaker.new()
		s.name = "KitShake"
		cam.add_child(s)
	s.start_kick(-KICK_SIGN * on_screen.normalized() * px * metres_per_px(cam), time)


## The width of one screen pixel in metres at the point the camera looks at (the chase camera's distance, else 6.5 m).
## h_offset and v_offset shift the picture by this much per pixel there.
static func metres_per_px(cam: Camera3D) -> float:
	var d: Variant = cam.get("distance")
	var dist: float = float(d) if d != null else 6.5
	return 2.0 * dist * tan(deg_to_rad(cam.fov) / 2.0) / cam.get_viewport().get_visible_rect().size.y


## A ring that runs out along the ground from c to radius r and fades: a stomp's shock wave. It lies flat, so it
## meets the edge of the circle the ability works in at any size (the gp_ring billboard art only reaches about 0.8 m).
static func ground_wave(parent: Node, c: Vector3, r: float, time := 0.35, color := Color(1.0, 0.86, 0.55, 0.9)) -> void:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = color
	var ring := TorusMesh.new()
	ring.inner_radius = 0.92
	ring.outer_radius = 1.0
	ring.rings = 48
	ring.ring_segments = 4
	ring.material = mat
	var mi := MeshInstance3D.new()
	mi.mesh = ring
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	mi.global_position = c + Vector3.UP * 0.05
	mi.scale = Vector3(r * 0.15, 0.02, r * 0.15)
	var tw := mi.create_tween().set_parallel()
	tw.tween_property(mi, "scale", Vector3(r, 0.02, r), time).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(mat, "albedo_color:a", 0.0, time).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.chain().tween_callback(mi.queue_free)


## ---- Basic attack hit (game feel lane, 2026-11-06; Preston on the gorilla's basic: "you cant really feel when you are
## using it"). The kit calls basic_hit() once, at contact. It marks the moment on both sides: the attacker's sprite
## lunges along the strike, the target's sprite is shoved the same way and eases back, and the hit_spark shows on
## the target. Only the sprites move, never the bodies, so nothing in the match changes. Flashes are the targets' own
## (dummies and minions flash in hit(), the rhino and gorilla in take_hit). The directional camera kick is the camera lane's (Preston: "camera will do 4"): this calls
## kick(dir, strength) on the camera when it has one and the local player is the attacker or the target.
## Starting values, ours (not from any game); tune one at a time with Preston playing.
static var lunge_m := 0.2 ## the attacker's sprite jumps this far along the strike at contact
static var lunge_back := 0.16 ## and eases back over this
static var push_m := 0.15 ## the target's sprite is shoved this far along the strike
static var push_back := 0.18 ## and eases back over this


static func basic_hit(attacker: Node3D, target: Node3D, dir := Vector3.ZERO, strength := 1.0, spark := true) -> void:
	if target == null or not is_instance_valid(target) or not target.is_inside_tree():
		return
	var live_attacker := attacker != null and is_instance_valid(attacker)
	var d := dir
	if d.length() < 0.01 and live_attacker:
		d = target.global_position - attacker.global_position
	d.y = 0.0
	d = d.normalized() if d.length() > 0.01 else Vector3.FORWARD
	if live_attacker and attacker.get("sprite") is DirectionalSprite3D:
		nudge(attacker.get("sprite"), d * lunge_m * strength, lunge_back)
	if target.get("sprite") is DirectionalSprite3D:
		nudge(target.get("sprite"), d * push_m * strength, push_back)
	elif target.has_method("shove"):
		target.shove(d * push_m * strength, push_back)
	var tb: Variant = target.get("body")
	if tb is MechModel3D:
		tb.nudge(d * push_m * strength, push_back)  # a 3D body takes the shove; the attacker's lunge is baked into its clips
	if spark:
		hit_spark(target, d)
	var cam := target.get_viewport().get_camera_3d()
	if cam != null and cam.has_method("kick") and (_is_local_player(attacker) or _is_local_player(target)):
		cam.kick(d, strength)


## Sets the sprite's feel_offset to world (a world-space offset) at once, then eases it back to nothing.
static func nudge(s: DirectionalSprite3D, world: Vector3, back: float) -> void:
	var p := s.get_parent() as Node3D
	var local := world if p == null else p.global_basis.inverse() * world
	var old: Variant = s.get_meta("feel_tween") if s.has_meta("feel_tween") else null  # a null default counts as none and logs an error
	if old is Tween and (old as Tween).is_valid():
		(old as Tween).kill()
	s.feel_offset = local
	var tw := s.create_tween()
	tw.tween_property(s, "feel_offset", Vector3.ZERO, back).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
	s.set_meta("feel_tween", tw)


## The project's hit_spark (Fx3D) at the near side of the target, pulled toward the camera so the target can't hide it.
## Skipped when the target's kit has take_hit: the rhino and the gorilla spawn their own spark and flash there.
static func hit_spark(target: Node3D, d: Vector3) -> Node3D:
	var kit := target.get_node_or_null("Kit")
	if kit != null and kit.has_method("take_hit"):
		return null
	var parent := target.get_parent()
	if parent == null:
		return null
	var r: float = target.radius() if target.has_method("radius") else 0.5
	var h := 0.9 if target.get("sprite") is DirectionalSprite3D else 0.5
	return Fx3D.spawn(parent, "hit_spark", target.global_position - d * r * 0.7 + Vector3.UP * h, 0.3)


static func _is_local_player(n: Node) -> bool:
	return n != null and is_instance_valid(n) and typeof(n.get("bot")) == TYPE_BOOL and not n.get("bot") and n.get_meta("is_player", true)


class Shaker extends Node:
	## At the chase camera's 6.5 m and default 75 degree field of view one pixel of the 320 x 180 screen is about
	## 0.055 m, so a full shake moves the picture up to about 7 px, a slam (0.7) about 3 px and a stomp (0.35) 1-2 px.
	var max_offset := 0.4
	var decay := 2.2 ## trauma lost per second
	var trauma := 0.0
	var _t := 0.0
	var _on := false
	var _kick := Vector2.ZERO ## the kick's full offset, metres (h, v)
	var _kick_time := 0.15
	var _kick_left := 0.0

	func start_kick(offset: Vector2, time: float) -> void:
		_kick = offset
		_kick_time = maxf(time, 0.001)
		_kick_left = _kick_time

	func _process(delta: float) -> void:
		var cam := get_parent() as Camera3D
		if cam == null:
			return
		if trauma <= 0.0 and _kick_left <= 0.0:
			if _on:
				cam.h_offset = 0.0
				cam.v_offset = 0.0
				_on = false
			return
		_on = true
		var off := Vector2.ZERO
		if trauma > 0.0:
			_t += delta
			trauma = maxf(trauma - decay * delta, 0.0)
			var a := trauma * max_offset
			off = a * Vector2(sin(_t * 47.0) * 0.6 + sin(_t * 113.0 + 1.7) * 0.4,
					sin(_t * 53.0 + 0.9) * 0.6 + sin(_t * 97.0 + 4.1) * 0.4)
		if _kick_left > 0.0:
			var k := _kick_left / _kick_time  # full on the first frame, then eases back
			off += _kick * k * k
			_kick_left = maxf(_kick_left - delta, 0.0)
		cam.h_offset = off.x
		cam.v_offset = off.y
