class_name ChaseCamera3D
extends Camera3D
## Chase camera behind and above the player (Claude, 2026-11-04), after the Pokebonk reel Preston sent ("this is
## how I want the MOBA to play perspective and world wise"): perspective, low pitch, horizon in view, the player in
## the lower middle of the screen. SMITE's camera works the same way. Q and E, or right-drag, turn it.

@export var target_path: NodePath
## SMITE fit (camera lane, 2026-11-10; Preston: "Yes, switch it"), measured from SMITE 1 frames: the machine's feet
## about 71% down the screen, a 1.7 m body's head about 60%, the horizon about 30%. These three values give that at the
## match scenes' fov 60. Was distance 6.5, pitch 30, look height 1.2 (feet 63%, horizon at the top edge).
## docs/reference/smite-camera-framing-2026-11-09.md
@export var distance := 12.0 ## metres from the point it looks at
@export var pitch_degrees := 13.0 ## flat, so the far lane and the horizon are in view
@export var yaw_degrees := 0.0 ## 0 = looking toward -Z
@export var turn_speed := 90.0 ## degrees per second on Q and E
@export var look_height := 3.2 ## aims above the machine, so it sits low on screen with the ground ahead in the middle
## Half sizes (x, z) of the area the camera stays inside; zero for no limit. Near the map edge it slides along the
## limit instead of ending up behind the edge cliffs (map lane's request, 2026-11-04: a clamp, not a pull-in, so the
## framing never jumps). arena_play.gd sets it from the blockout's HALF_X and HALF_Z.
@export var bounds := Vector2.ZERO

var target: Node3D

## Per-machine framing (camera lane, 2026-11-13; Preston: "I think camera might be too zoomed out for smite perspective
## btw. Lets start upgrading camera to how we need for each creature"). Each machine is framed from its height in
## art/arena_models/roster.json so its body fills SHARE of the screen height, feet held FEET_AT down the screen (clear
## of the HUD bar at 82%). The pitch stays flat (SMITE). distance and look_height are worked out from those.
## The match scene's `machine` names the player's machine; on a change the camera reframes. Scenes without one keep
## the exported distance and look_height.
@export var per_machine := true
const FEET_AT := 0.71
const SHARE := {"S": 0.14, "M": 0.16, "L": 0.18} ## share of the screen height the body fills, by size class
const ROSTER := "res://art/arena_models/roster.json"
var machine_kind := ""
var _roster := {}


## Sets distance and look_height so a body of height metres fills share of the screen height with its feet at FEET_AT.
func frame_body(height: float, share: float) -> void:
	_frame_h = height
	_frame_share = share
	var t := tan(deg_to_rad(fov) / 2.0)
	var pitch := deg_to_rad(pitch_degrees)
	var feet := pitch + atan(2.0 * (FEET_AT - 0.5) * t)  # angle below the horizontal to the feet
	var head := pitch + atan(2.0 * (FEET_AT - share - 0.5) * t)
	var d := height / (tan(feet) - tan(head))  # metres behind, along the ground
	var up := d * tan(feet)  # camera height above the feet
	distance = d / cos(pitch)
	look_height = up - distance * sin(pitch)


## The roster's height and size class for a machine id, or {} when it isn't listed.
func roster_entry(id: String) -> Dictionary:
	if _roster.is_empty() and FileAccess.file_exists(ROSTER):
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(ROSTER))
		if data is Dictionary:
			for e in data.get("entries", []):
				_roster[str(e.get("id", ""))] = e
	return _roster.get(id, {})


## Reframes when the followed machine changes. The height used is the body as the game draws it (its model's top above
## the feet), because the drawn bodies don't follow the roster caps (2026-11-13: L and M both drawn about 1.70 m);
## the roster's height_cap is the fallback. The share still comes from the size class, so L reads bigger than M.
func _follow_machine() -> void:
	var scene := get_tree().current_scene if is_inside_tree() else null
	var m: Variant = scene.get("machine") if scene != null else null
	if not (m is String) and target != null:  # match scenes have no `machine`: ask the followed machine (game feel lane)
		m = MatchTeams.machine_kind(target)
	if not (m is String) or m == "":
		return
	_kind = m
	var key := "%s:%d" % [m, target.get_instance_id() if target != null else 0]
	if key == machine_kind:
		return
	var e := roster_entry(m)
	if e.is_empty():
		return
	var h := _drawn_height()
	if h < 0.5:  # model not built yet: use the cap for now and measure again next frame
		h = float(e.get("height_cap", 1.65))
	else:
		machine_kind = key
	frame_body(h, float(SHARE.get(str(e.get("size_class", "M")), 0.16)))


## Top of the followed machine's model above its feet, metres, or -1 when it has no model yet.
func _drawn_height() -> float:
	var body: Variant = target.get("body") if target != null else null
	if not (body is Object) or not body.has_method("model_root"):
		return -1.0
	var root: Node3D = body.model_root()
	if root == null:
		return -1.0
	var top := -1.0
	for c in root.find_children("*", "MeshInstance3D", true, false):
		var mi := c as MeshInstance3D
		if mi.mesh != null and mi.is_visible_in_tree():
			top = maxf(top, (mi.global_transform * mi.get_aabb()).end.y)
	return top - target.global_position.y if top > -1.0 else -1.0


## Mouse look (camera lane, 2026-11-13; Preston: "We're changing from aim at mouse to more like smite where camera
## moves with where you are looking"). The mouse is captured: moving it left and right turns the camera, up and down
## tilts it between PITCH_MIN and PITCH_MAX, which brings the aim nearer or further. The aim is the floor under the
## reticle at the centre of the screen. The machine stays centred (no over-the-shoulder offset), so aiming left and
## right take the same mouse travel. Esc frees the mouse; a click takes it back. mouse_look off restores the old
## aim-at-the-cursor.
@export var mouse_look := true
@export var look_sensitivity := 0.2 ## degrees of turn per screen pixel of mouse travel
@export var invert_y := false
const PITCH_MIN := 6.0
const PITCH_MAX := 30.0
const RETICLE := Vector2(0.5, 0.5) ## reticle position as a fraction of the screen
var _frame_h := 0.0
var _frame_share := 0.0
var _reticle: Control


## Where the player aims on screen: the reticle under mouse look, else the mouse cursor.
func aim_screen() -> Vector2:
	if mouse_look:
		if _ring_w > 0.0 and target != null:
			return unproject_position(_base_aim_point())
		return get_viewport().get_visible_rect().size * RETICLE
	return get_viewport().get_mouse_position()


var _force_look := false ## checks set this: headless can't capture the mouse


func _look_active() -> bool:
	return mouse_look and (_force_look or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED)


func _set_pitch(deg: float) -> void:
	pitch_degrees = clampf(deg, PITCH_MIN, PITCH_MAX)
	if _frame_h > 0.0:
		frame_body(_frame_h, _frame_share)


func _make_reticle() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 6
	add_child(layer)
	_reticle = Reticle.new()
	_reticle.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(_reticle)


## Placeholder reticle: a small open cross with a dot, dark outline under light lines so it reads on any floor.
class Reticle extends Control:
	func _process(_delta: float) -> void:
		var cam := get_viewport().get_camera_3d() as ChaseCamera3D
		visible = cam != null and cam.mouse_look
		if visible:
			position = cam.aim_screen()
		queue_redraw()

	func _draw() -> void:
		for pass_i in 2:
			var c := Color(0.05, 0.05, 0.08, 0.8) if pass_i == 0 else Color(1.0, 0.95, 0.8, 0.95)
			var w := 3.0 if pass_i == 0 else 1.0
			for d in [Vector2.RIGHT, Vector2.LEFT, Vector2.UP, Vector2.DOWN]:
				draw_line(d * 2.5, d * 6.0, c, w)
			draw_rect(Rect2(-0.5 - pass_i * 0.0, -0.5, 1.0, 1.0), c)


func _ready() -> void:
	target = get_node_or_null(target_path)
	snap()
	if mouse_look and DisplayServer.get_name() != "headless":
		_make_reticle()
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _process(delta: float) -> void:
	if per_machine:
		_follow_machine()
	_update_hold(delta)
	if Input.is_physical_key_pressed(KEY_Q):
		yaw_degrees += turn_speed * delta
	if Input.is_physical_key_pressed(KEY_E):
		yaw_degrees -= turn_speed * delta
	snap()


func _unhandled_input(event: InputEvent) -> void:
	if mouse_look:
		var key := event as InputEventKey
		if key != null and key.pressed and key.physical_keycode == KEY_ESCAPE:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		elif event is InputEventMouseButton and event.pressed and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		elif event is InputEventMouseMotion and _look_active():
			var m := (event as InputEventMouseMotion).screen_relative
			yaw_degrees -= m.x * look_sensitivity
			_set_pitch(pitch_degrees + m.y * look_sensitivity * 0.5 * (-1.0 if invert_y else 1.0))
		return
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		yaw_degrees -= (event as InputEventMouseMotion).relative.x * 0.3


## Ring pull-back (camera lane, 2026-11-14; Preston picked "Ring pull-back" from the combat camera synthesis). While a
## ground ring is in play the camera eases to a frame where the whole ring sits above the HUD bar: the machine moves up
## to the middle of the screen, the camera tilts down (RING_PITCH, or ULT_PITCH for ults: Preston's 2026-11-04 rule that
## ults lift the camera to 55-60 deg) and pulls back just far enough for the ring's near edge to clear RING_BOTTOM.
## A ring centred on the machine needs the camera about three ring radii away, so big rings pull far; MAX_ARM caps it.
## The aim stays on the same spot of floor through the pull (aim_screen follows it), so a pull-back never moves a shot.
## Kits don't have to call it: the camera listens to the followed machine's kit `used(slot)` and looks the ring up in
## RING_MOMENTS (radius from the kit's export when it has one). A kit can also call hold() itself.
const RING_BOTTOM := 0.80 ## the ring's near edge stays above this share of the screen (HUD bar from 82%)
const RING_FEET := 0.5 ## the feet move to the middle of the screen during a hold
const RING_PITCH := 30.0
const ULT_PITCH := 57.0
const MAX_ARM := 20.0 ## metres from the feet: past this the near edge is allowed under the HUD
const EASE_IN := 0.12 ## seconds (time constant) into the ring frame
const EASE_OUT := 0.25 ## and back out
## kind -> slot -> [kit export holding the radius, fallback radius m, seconds held, ult]. Numbers from
## docs/reference/camera-kit-moments-2026-11-13.md; placeholders for Preston to tune.
const RING_MOMENTS := {
	"gorilla": {"2": ["taunt_radius", 3.0, 1.5, false], "4": ["ult_radius", 5.5, 2.0, true]},
	"rhino": {"2": ["pound_radius", 4.0, 2.2, false], "3": ["", 5.0, 2.0, false], "4": ["finale_radius", 3.4, 3.0, true]},
	"hippo": {"2": ["drop_radius", 3.2, 1.6, false], "4": ["lake_radius", 6.0, 4.0, true]},
	"kangaroo": {"4": ["ring_radius", 3.0, 4.0, true]},
	"pangolin": {"3": ["flare_radius", 2.5, 1.0, false], "4": ["comet_radius", 4.0, 4.0, true]},
}
var _ring_r := 0.0
var _ring_pitch := 0.0 ## radians
var _ring_w := 0.0 ## 0 = normal frame, 1 = ring frame
var _hold_left := 0.0
var _kit: Node
var _kind := ""


## Pull back so a ground ring of radius metres around the machine fits above the HUD bar for seconds (ease in and out
## around it). seconds < 0 holds until release(). ult uses the steep ult tilt. A bigger ring wins over a smaller one.
func hold(radius: float, seconds: float, ult := false) -> void:
	if _ring_fits(radius):
		return
	if _hold_left <= 0.0 or radius >= _ring_r:
		_ring_r = radius
		_ring_pitch = deg_to_rad(ULT_PITCH if ult else RING_PITCH)
	_hold_left = INF if seconds < 0.0 else maxf(_hold_left, seconds)


func release() -> void:
	_hold_left = 0.0


## Horizontal distance, height and pitch (radians) of the frame that fits a ring of radius r with its near edge at
## RING_BOTTOM and the feet at RING_FEET, capped at MAX_ARM.
func _ring_frame(r: float, p: float) -> Vector3:
	var t := tan(deg_to_rad(fov) / 2.0)
	var tf := tan(p + atan(2.0 * (RING_FEET - 0.5) * t))
	var tn := tan(p + atan(2.0 * (RING_BOTTOM - 0.5) * t))
	var d := r * tn / (tn - tf)
	var h := d * tf
	var len := Vector2(d, h).length()
	if len > MAX_ARM:
		d *= MAX_ARM / len
		h *= MAX_ARM / len
	return Vector3(d, h, p)


## Whether a ring of radius r already sits above RING_BOTTOM in the normal frame.
func _ring_fits(r: float) -> bool:
	var p := deg_to_rad(pitch_degrees)
	var d := distance * cos(p)
	var h := look_height + distance * sin(p)
	if r >= d:
		return false
	var t := tan(deg_to_rad(fov) / 2.0)
	return tan(atan(h / (d - r)) - p) / (2.0 * t) + 0.5 <= RING_BOTTOM


func _update_hold(delta: float) -> void:
	_hook_kit()
	if _hold_left > 0.0:
		_hold_left -= delta
		_ring_w += (1.0 - _ring_w) * (1.0 - exp(-delta / EASE_IN))
	elif _ring_w > 0.0:
		_ring_w += (0.0 - _ring_w) * (1.0 - exp(-delta / EASE_OUT))
		if _ring_w < 0.002:
			_ring_w = 0.0


## Connects to the followed machine's kit `used` signal (a swap makes a new kit).
func _hook_kit() -> void:
	var k: Node = target.get_node_or_null("Kit") if target != null else null
	if k == _kit:
		return
	_kit = k
	if k != null and k.has_signal("used") and not k.is_connected("used", _on_kit_used):
		k.connect("used", _on_kit_used)


func _on_kit_used(slot: String) -> void:
	var row: Array = RING_MOMENTS.get(_kind, {}).get(slot, [])
	if row.is_empty():
		return
	var r: float = row[1]
	if row[0] != "" and _kit != null:
		var v: Variant = _kit.get(row[0])
		if v is float or v is int:
			r = float(v)
	hold(r, row[2], row[3])


## The floor point under the reticle in the player's own frame (no pull-back), where the aim stays during a hold.
func _base_aim_point() -> Vector3:
	var yaw := deg_to_rad(yaw_degrees)
	var p := deg_to_rad(pitch_degrees)
	var back := Vector3(sin(yaw), 0.0, cos(yaw))
	var feet := target.global_position
	var h := look_height + distance * sin(p)
	return feet + back * (distance * cos(p) - h / tan(p))


## Near a map edge or a wall the camera slides in along its line to the machine's feet and keeps its tilt, so the
## feet stay about 71% down the screen and clear of the HUD bar; the machine just reads bigger (camera lane, 2026-11-10,
## after the rhino's feet sat behind the bar at the spawn). Walls stop it like a spring arm (map lane: the base ring
## runs right behind the spawn). It never goes below MIN_HEIGHT; when a wall stops it lower it holds that height and
## tilts down, still keeping the feet where they were on screen.
const MIN_HEIGHT := 2.4 ## metres above the feet
const WALL_RADIUS := 0.3 ## the camera's sphere for the wall cast
var _cast: PhysicsShapeQueryParameters3D


func snap() -> void:
	if target == null:
		return
	var yaw := deg_to_rad(yaw_degrees)
	var pitch := deg_to_rad(pitch_degrees)
	var back := Vector3(sin(yaw), 0.0, cos(yaw))
	var feet := target.global_position
	var hd := distance * cos(pitch)  # metres behind the feet, along the ground
	var hh := look_height + distance * sin(pitch)  # metres above the feet
	if _ring_w > 0.0:
		var rf := _ring_frame(_ring_r, _ring_pitch)
		hd = lerpf(hd, rf.x, _ring_w)
		hh = lerpf(hh, rf.y, _ring_w)
		pitch = lerpf(pitch, rf.z, _ring_w)
	var arm := back * hd + Vector3.UP * hh
	var share := 1.0
	if bounds.x > 0.0 and bounds.y > 0.0:
		share = minf(_fit(feet.x, arm.x, bounds.x), _fit(feet.z, arm.z, bounds.y))
	share = maxf(share, MIN_HEIGHT / arm.y)  # the floor
	# Walls only stop it once the edge has pulled it in (the base ring behind the spawn). In open ground a wall between
	# is the map lane's machine_hidden fade's job, so the camera doesn't pop in and out past every pillar.
	if share < 1.0:
		var walled := _wall_share(feet, arm * share) * share
		if walled < share:
			share = walled
	var at := feet + arm * share
	at.y = maxf(at.y, feet.y + MIN_HEIGHT)  # a wall stopped it low: hold the floor and tilt down instead
	if bounds.x > 0.0 and bounds.y > 0.0:  # only bites when the floor kept the camera back
		at.x = clampf(at.x, -bounds.x, bounds.x)
		at.z = clampf(at.z, -bounds.y, bounds.y)
	global_position = at
	# Tilt so the feet sit as far below the view's centre as they do at full distance (about 71% down the screen).
	var below := atan2(arm.y, Vector2(arm.x, arm.z).length()) - pitch
	var rel := at - feet
	var tilt := atan2(rel.y, Vector2(rel.x, rel.z).length()) - below
	global_basis = Basis.from_euler(Vector3(-tilt, yaw, 0.0))


## The largest share of a (0 to 1) that keeps p + a * share within -b..b.
static func _fit(p: float, a: float, b: float) -> float:
	if a > 0.0:
		return clampf((b - p) / a, 0.0, 1.0)
	if a < 0.0:
		return clampf((-b - p) / a, 0.0, 1.0)
	return 1.0


## How much of the line from the feet to feet + arm is free of walls (ArenaMotion.wall_mask), as a share of arm.
func _wall_share(feet: Vector3, arm: Vector3) -> float:
	if not is_inside_tree() or arm.length() < 1.0:
		return 1.0
	if _cast == null:
		_cast = PhysicsShapeQueryParameters3D.new()
		var sph := SphereShape3D.new()
		sph.radius = WALL_RADIUS
		_cast.shape = sph
		_cast.collide_with_areas = false
	_cast.collision_mask = ArenaMotion.wall_mask
	var dir := arm.normalized()
	var start := feet + dir * 0.8  # off the ground and out of the machine's own body
	_cast.transform = Transform3D(Basis.IDENTITY, start)
	_cast.motion = feet + arm - start
	var hit := get_world_3d().direct_space_state.cast_motion(_cast)
	if hit.is_empty() or hit[0] >= 1.0:
		return 1.0
	return (0.8 + hit[0] * _cast.motion.length()) / arm.length()


## Kicks the picture KICK_PX game pixels along a hit's direction and eases it back (camera lane, 2026-11-06;
## Preston: "Kick the camera along the punch"). KitFeel.basic_hit calls this when the local player lands or takes a
## basic, with strength scaling it. The work is in KitFeel.kick, which shares the shake's h_offset and v_offset.
const KICK_PX := 2.0
func kick(dir: Vector3, strength := 1.0) -> void:
	KitFeel.kick(self, dir, KICK_PX * strength)
