extends Node3D
## The player's machine in the 3D test slice (Claude, 2026-11-04). WASD or the arrow keys move relative to the
## camera, the machine faces where it walks, and the walk plays faster or slower with speed so the feet keep pace
## (the pattern in Shotcaller's move_action.gd, studied for structure only). No physics yet: the slice only proves
## the look, the camera, the eight-way sprite and the kit (a RhinoKit child, keys 1-4).

@export var move_speed := 3.5 ## metres per second; a placeholder, Preston sets the number
## The speed at which the walk's planted feet stay put at its authored 8 fps. The side walk's planted foot slides
## back about 3 px a frame (middle half 2 to 4): 3 px x 8 fps x 0.02 m/px = 0.48 m/s. Measured 2026-11-04 with
## tools/debug/walk_stride_measure.py; rerun it after any walk frame change.
@export var stride_speed := 0.48
## Walk playback at full move_speed (1.0 = the authored 8 fps); below full speed it stays proportional, so brace
## and partial input still slow the legs. A presentation placeholder until the stride question is settled.
@export var full_speed_walk_rate := 1.0
## Writes the machine's feet position to the global shader parameter machine_pos every frame, so the map lane's
## wall_fade shader can dither walls between the camera and the machine (agreed with the map lane, 2026-11-04).
## Declared in project.godot [shader_globals] as (0, -1000, 0), so nothing fades when no player exists.
## Walls: the walk slides along the arena's walls (ArenaMotion), as the map lane and this lane agreed (2026-11-04).
@export var publish_machine_pos := true
## Also writes machine_hidden: 1 while an arena wall crosses the line from the camera to the machine's body, 0 in plain
## view, eased over HIDDEN_EASE seconds. The map lane scales the wall cut by it, so walls never thin while the machine
## is in plain view (their request, 2026-11-04). Declared in project.godot as 1.0, so with no player the cut works as
## it did before.
const HIDDEN_HEIGHT := 1.0 ## the ray aims this far above an L machine's feet (map lane's 1 m); M and S scale down
const HIDDEN_EASE := 0.15 ## seconds from fully seen to fully hidden (map lane's figure)
@export var body_radius_l := 0.8 ## placeholder: how close an L machine's middle gets to a wall; M and S scale down
@export var camera_path: NodePath ## kept for older scenes; directions come from whichever camera is current

var facing := Vector3(0.0, 0.0, -1.0) ## away from the starting camera, so the back view shows first
var input_override: Variant = null ## a Vector2 set by checks; null reads the keyboard
@export var aim_face_time := 0.4 ## seconds a cast keeps the machine facing its aim before walking turns it again
@export var aim_stick_range := 6.0 ## metres: where a gamepad's right stick puts the aim point
var aim_screen_override: Variant = null ## a Vector2 screen point set by checks; null reads the mouse
var _aim_hold := 0.0
var _aim_ring: MeshInstance3D
var _aim_line: MeshInstance3D
var move_override: Variant = null ## a world-space Vector3 for scripted moves (the reveal); wins over input
var busy := false ## an ability owns the machine: no walking, the kit drives the sprite
var speed_mult := 1.0 ## a kit's own pace change (the rhino's brace used it until Aftershock replaced it, 2026-11-20)
var boosts := {} ## key -> [mult, seconds left]: timed speed changes (boost()); the same key refreshes, different keys multiply
var speed := 0.0
var death_hold := 0.0 ## how long the wreck stays in view after dying: its Death clip plus death_linger, 0 without one (the director hides it then)
var death_linger := 0.5
var published_pos := Vector3(0.0, -1000.0, 0.0) ## what was last written to machine_pos (the checks read it)
var machine_hidden := 1.0 ## what was last written to machine_hidden (the checks read it)
var _bases := {} ## the ground ring's and contact shadow's scales as set for the L rhino

@onready var sprite: DirectionalSprite3D = $Sprite
var react_gap := 0.6 ## seconds between two Hit_Front flinches on a 3D body
var _react_left := 0.0
var _react_blocked := false ## set by hit() for the take_damage it calls
var armour := 1.0 ## damage taken is multiplied by this: above 1 its plates were torn off, below 1 it wears stolen ones
var _armour_token := 0
var body: MechModel3D = null ## the rigged 3D body, or null while this machine is still a sprite (use_model; game feel lane, 2026-11-09)
const MECH_LOOK := preload("res://scripts/moba3d/mech_look.gd") ## the look lane's rim and outline (no class_name)


func _ready() -> void:
	ContactShadow3D.attach(self, sprite)  # camera lane, 2026-11-04: a shadow under the drawn feet, turned with the view
	for n in ["Ring", "Shadow"]:
		var m := get_node_or_null(n) as Node3D
		if m != null:
			_bases[n] = m.scale
	apply_size_class()
	sprite.show_facing(facing, _camera_basis(), false)


## Sizes the ground ring and contact shadow to the sprite's size class (they were set for the L rhino). Call it
## again after changing sprite.size_class or sprite.canvas_height.
func apply_size_class() -> void:
	var k := sprite.size_scale()
	for n in _bases:
		var b: Vector3 = _bases[n]
		(get_node(n) as Node3D).scale = Vector3(b.x * k, b.y, b.z * k)


## Gives this machine its kind's rigged 3D body (MechModel3D.ROWS), or takes it away when the kind has no model yet,
## and the sprite shows again. The sprite keeps running hidden under a body, so a kit still timed on sprite frames
## works on. enemy picks the look's enemy rim (against the local player's team). Game feel lane, 2026-11-09.
func use_model(kind: String, enemy := false) -> void:
	set_meta("arena_machine",kind)
	body = MechModel3D.attach(self, kind)
	sprite.visible = body == null
	var sh := get_node_or_null("Shadow") as Node3D
	if sh != null:
		sh.visible = body == null  # the model casts its own shadow
	if body != null:
		body.snap_facing(facing)
		MECH_LOOK.apply_model(body.model_root(), enemy)


func _drive_body(delta: float, ground_speed: float, move := Vector3.ZERO) -> void:
	if body == null:
		return
	_react_left = maxf(_react_left - delta, 0.0)
	if ground_speed > 0.05 and body.action.begins_with("Hit_"):
		body.stop_action()  # walking off cancels a flinch, so the body never slides in a hit pose
	body.face(facing, delta)
	body.locomote(ground_speed, move)  # the direction too: facing its aim while walking elsewhere plays a strafe or backpedal


## Hit reactions on a 3D body (game feel lane, 2026-11-09). They never cut the machine's own clips (an action
## playing, or the kit owning the machine), Hit_Front only plays standing and at most every react_gap seconds,
## and a hit the kit blocked (the hex shield) gets none. Hit_Heavy comes with a stun.
func _react(clip: String, from: Node3D = null) -> void:
	var blocked := _react_blocked
	_react_blocked = false
	if body == null or blocked or not alive or busy or body.action != "" or not body.has_clip(clip):
		return
	if clip == "Hit_Front" and (speed > 0.05 or _react_left > 0.0):
		return
	_react_left = react_gap
	if clip == "Hit_Front":
		clip = _hit_side(from)
	body.play_action(clip)


## Directional light hits (gorilla lane, 2026-11-14): a body with Hit_Left / Hit_Right / Hit_Back clips flinches away
## from where the attacker stands against its facing (front 120 degrees: Hit_Front, back 90: Hit_Back, the rest: the
## sides). A body without the clip, or a hit with no attacker, plays Hit_Front as before.
func _hit_side(from: Node3D) -> String:
	if from == null or not is_instance_valid(from) or from == self:
		return "Hit_Front"
	var d := from.global_position - global_position
	d.y = 0.0
	var f := Vector3(facing.x, 0.0, facing.z)
	if d.length() < 0.01 or f.length() < 0.01:
		return "Hit_Front"
	d = d.normalized()
	f = f.normalized()
	var along := f.dot(d)
	var clip := "Hit_Front"
	if along <= -0.707:
		clip = "Hit_Back"
	elif along < 0.5:
		clip = "Hit_Left" if f.z * d.x - f.x * d.z > 0.0 else "Hit_Right"
	return clip if body.has_clip(clip) else "Hit_Front"


## A body with its own Stun clip (rhino v47) loops it, blended in, for as long as the stun lasts, in place of the one
## Hit_Heavy. Like the reactions it never cuts the kit's clips: a stun landing mid-ability starts when the kit lets go.
func _stun_pose() -> void:
	if body == null or not alive or busy or (stunned <= 0.0 and not has_meta("held_by")) or body.action == "Stun" or not body.has_clip("Stun"):
		return
	if body.action != "" and not body.action.begins_with("Hit_"):
		return
	body.play_hold("Stun", 1.0, 0.15)


## A held machine (the rhino's Tremor carry, 2026-11-11) shows it: a body with a Stun clip loops it while held (_stun_pose,
## every frame); one without plays Hit_Heavy once, here, on the catch.
func held_pose() -> void:
	if body != null and body.has_clip("Stun"):
		_stun_pose()
	else:
		_react("Hit_Heavy")


## A body with a Death clip (rhino v47) plays it and keeps its last frame (nothing drives the body while dead). Returns
## how long the wreck should stay in view; 0 without the clip, and the director hides the machine at once as before.
func _death_pose() -> float:
	if body == null or not body.has_clip("Death"):
		return 0.0
	return body.play_action("Death", 1.0, 0.1) + death_linger


func _exit_tree() -> void:
	if publish_machine_pos:  # back to the no-player default, so the next scene's walls don't fade here
		RenderingServer.global_shader_parameter_set(&"machine_pos", Vector3(0.0, -1000.0, 0.0))
		RenderingServer.global_shader_parameter_set(&"machine_hidden", 1.0)


func _camera_basis() -> Basis:
	var c := get_viewport().get_camera_3d()
	return c.global_basis if c != null else Basis()


## Where the movement keys (or a check's input_override, or a scripted move) point now: world space, flat, the stick's
## length kept (up to 1), zero when nothing is pressed. It reads the keys even while busy, so a kit can send a hop the
## way the player is walking (the squirrel's Branch Skip) and fall back to aim_dir() or facing when standing still.
func move_dir() -> Vector3:
	if move_override != null:
		return move_override
	var v: Vector2 = input_override if input_override != null else (Vector2.ZERO if bot else _keys())
	var b := _camera_basis()
	var fwd := Vector3(-b.z.x, 0.0, -b.z.z).normalized()
	var right := Vector3(b.x.x, 0.0, b.x.z).normalized()
	return right * v.x + fwd * -v.y


## A timed speed change, e.g. boost(1.3, 2.0, &"tail_ping"). The same key again refreshes it (it never stacks with
## itself); different keys multiply with each other, with speed_mult and with a slow.
func boost(mult: float, t: float, key: StringName = &"boost") -> void:
	boosts[key] = [mult, t]


## Every speed change at once: speed_mult x the timed boosts x the slow (slow_factor(); two slows do not deepen).
## Tail Ping on a slowed squirrel: 1.3 x 0.6 = 0.78.
func speed_factor() -> float:
	var f := speed_mult * slow_factor()
	for k in boosts:
		f *= float(boosts[k][0])
	return f


func _process(delta: float) -> void:
	var b := _camera_basis()
	_aim_hold = maxf(_aim_hold - delta, 0.0)
	_update_aim_marker()
	_tick_match(delta)
	if not alive:
		_publish(delta)
		return
	if body != null and (body.action == "Death" or (body.action == "Stun" and stunned <= 0.0 and not has_meta("held_by"))):
		body.stop_action()  # respawned before the Death clip ran out, or the stun is over
	if busy or stunned > 0.0 or _forced():
		sprite.show_facing(facing, b, false)
		_stun_pose()
		_drive_body(delta, 0.0)
		_publish(delta)
		return
	var dir := move_dir()
	var moving := dir.length() > 0.05
	speed = move_speed * speed_factor() * minf(dir.length(), 1.0) if moving else 0.0
	if moving:
		if _aim_hold <= 0.0:  # just after a cast the machine keeps facing its aim; it still walks where the keys say
			facing = dir.normalized()
		var prev := global_position
		var want := MatchBodies.block(self, prev, prev + dir.normalized() * speed * delta, body_radius())  # other bodies first
		global_position = ArenaMotion.slide(self, prev, want - prev, body_radius())  # then the arena walls
		_dome_walls(prev)
	if sprite.action == "" or sprite.hold:
		if not moving:
			sprite.speed_scale = 1.0
		elif sprite.hold and sprite.shuffle_anim() != &"":
			sprite.speed_scale = speed / (move_speed * speed_mult)  # the shuffle is drawn for the braced pace
		else:
			sprite.speed_scale = speed / move_speed * full_speed_walk_rate  # a held action with no shuffle walks slowly
	sprite.show_facing(facing, b, moving)
	_drive_body(delta, speed if moving else 0.0, dir)
	_publish(delta)


## Writes the feet position and machine_hidden for the map lane's wall fade, after this frame's move so the cut never
## lags a frame.
func _publish(delta: float) -> void:
	if not publish_machine_pos:
		return
	RenderingServer.global_shader_parameter_set(&"machine_pos", global_position)
	published_pos = global_position
	machine_hidden = move_toward(machine_hidden, _hidden_target(), delta / HIDDEN_EASE)
	RenderingServer.global_shader_parameter_set(&"machine_hidden", machine_hidden)


## 1 when an arena wall (ArenaMotion.wall_mask, layer 1) crosses the line from the current camera to the body, else 0.
## No camera counts as hidden, which leaves the wall cut as it was.
func _hidden_target() -> float:
	var c := get_viewport().get_camera_3d()
	if c == null:
		return 1.0
	var aim := global_position + Vector3.UP * HIDDEN_HEIGHT * sprite.size_scale()
	return 0.0 if ArenaMotion.ray(self, c.global_position, aim).is_empty() else 1.0


## How close this machine's middle gets to a wall: the L figure scaled by its size class.
func body_radius() -> float:
	return body_radius_l * sprite.size_scale()


## How many times faster the body moves than its planted feet at the current speed: 1.0 is no slide.
func foot_slide() -> float:
	var feet := stride_speed * sprite.speed_scale
	return speed / feet if feet > 0.0 and speed > 0.0 else 1.0


## Aim at the mouse (Preston, 2026-11-05: "B: aim at the mouse"; the camera lane keeps the camera). An ability key
## turns the machine to the aim point before the kit reads facing: _input runs before the kits'
## _unhandled_key_input, so no kit needed a change. A slot on cooldown, a busy or stunned machine and bots don't turn.
func _input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo or bot or not alive or busy or stunned > 0.0:
		return
	if k.physical_keycode < KEY_1 or k.physical_keycode > KEY_5:
		return
	if k.physical_keycode <= KEY_4 and has_method("slot_ready") and not call("slot_ready", str(k.physical_keycode - KEY_0)):
		return
	var d := aim_dir()
	if d == Vector3.ZERO:
		return
	facing = d
	_aim_hold = aim_face_time
	sprite.show_facing(facing, _camera_basis(), speed > 0.05)  # now, so the kit's play_action starts in the aim's view


## The point on the floor the player aims at: a gamepad's right stick when pushed, else the mouse (or a check's
## aim_screen_override) cast from the current camera onto the floor at the machine's feet.
func aim_point() -> Vector3:
	if bot:
		return global_position + facing * aim_stick_range  # a bot aims where it faces (MatchBot turns it first), never at the player's mouse (2026-11-11)
	var b := _camera_basis()
	var st := Vector2(Input.get_joy_axis(0, JOY_AXIS_RIGHT_X), Input.get_joy_axis(0, JOY_AXIS_RIGHT_Y))
	if aim_screen_override == null and st.length() > 0.35:
		var fwd := Vector3(-b.z.x, 0.0, -b.z.z).normalized()
		var right := Vector3(b.x.x, 0.0, b.x.z).normalized()
		return global_position + (right * st.x + fwd * -st.y).normalized() * aim_stick_range
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return global_position + facing
	var sp: Vector2 = aim_screen_override if aim_screen_override != null else (cam.call("aim_screen") if cam.has_method("aim_screen") else get_viewport().get_mouse_position())  # reticle under mouse look (camera lane, 2026-11-13)
	var o := cam.project_ray_origin(sp)
	var n := cam.project_ray_normal(sp)
	if n.y > -0.001:
		return global_position + facing  # at or above the horizon there is no floor point
	return o + n * ((global_position.y - o.y) / n.y)


## Flat direction from the machine to the aim point, or zero when the aim is on the machine itself.
func aim_dir() -> Vector3:
	var d := aim_point() - global_position
	d.y = 0.0
	return d.normalized() if d.length() > 0.2 else Vector3.ZERO


## Whether the floor aim marker is showing. The map lane's HUD overlay (match_hud.gd, layer 7) reads this to draw its
## own ring and line when the aim point falls under a HUD panel.
func aim_marker_visible() -> bool:
	return _aim_ring != null and _aim_ring.visible


## A ring on the floor at the aim point and a faint line out to it, for the player's machine only. Plain placeholder
## look (the HUD and its look are the map lane's). The line shows the exact aim; the sprite only has 8 views.
func _update_aim_marker() -> void:
	var want := not bot and alive and is_inside_tree()
	var kit:=get_node_or_null("Kit")
	if kit!=null and kit.has_method("blocks_basic_input") and kit.blocks_basic_input():want=false
	if not want:
		if _aim_ring != null:
			_aim_ring.visible = false
			_aim_line.visible = false
		return
	if _aim_ring == null:
		_build_aim_marker()
	var p := aim_point()
	var d := p - global_position
	d.y = 0.0
	_aim_ring.visible = true
	_aim_ring.global_position = Vector3(p.x, global_position.y + 0.03, p.z)
	var length_m := d.length() - 0.7
	_aim_line.visible = length_m > 0.2
	if _aim_line.visible:
		var dir := d.normalized()
		var mid := global_position + dir * (0.7 + length_m * 0.5)
		_aim_line.global_transform = Transform3D(Basis(Vector3.UP.cross(dir).normalized(), Vector3.UP, dir * length_m), Vector3(mid.x, global_position.y + 0.025, mid.z))


func _build_aim_marker() -> void:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.albedo_color = Color(0.9, 0.97, 1.0, 0.8)
	var ring := TorusMesh.new()
	ring.inner_radius = 0.3
	ring.outer_radius = 0.38
	ring.rings = 32
	ring.ring_segments = 4
	_aim_ring = MeshInstance3D.new()
	_aim_ring.mesh = ring
	_aim_ring.material_override = mat
	_aim_ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_aim_ring.top_level = true
	_aim_ring.scale = Vector3(1.0, 0.25, 1.0)
	add_child(_aim_ring)
	var line_mat := mat.duplicate() as StandardMaterial3D
	line_mat.albedo_color = Color(0.9, 0.97, 1.0, 0.35)
	var box := BoxMesh.new()
	box.size = Vector3(0.05, 0.01, 1.0)
	_aim_line = MeshInstance3D.new()
	_aim_line.mesh = box
	_aim_line.material_override = line_mat
	_aim_line.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_aim_line.top_level = true
	add_child(_aim_line)


func _keys() -> Vector2:
	var v := Vector2.ZERO
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT):
		v.x -= 1.0
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT):
		v.x += 1.0
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP):
		v.y -= 1.0
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN):
		v.y += 1.0
	return v.limit_length(1.0)


# ---- the match (Claude, 2026-11-04, game feel lane): team, health, and what kits do to a machine --------------------
# Outside a match max_hp is 0 and team is "": hits only flash and nothing here changes the reveals or field tests.
# Every number is a placeholder in MatchRules.

signal damaged(amount: float, by: Node3D)
signal died(by: Node3D)
signal healed(amount: float, by: Node3D) ## heal() emits it with what was actually healed
signal respawned ## the sound lane's names; the director emits these three on the machine
signal recall_started
signal recall_finished

var team := "" ## "blue" or "red" in a match
var kind := "machine"
var bot := false ## driven by a MatchBot: the keyboard and keys 1-4 do nothing
var max_hp := 0.0
var hp := 0.0
var alive := true
var seen := true ## false while the map lane's fog hides this enemy from the player
var cooldowns := {} ## slot "1"-"4" -> seconds left; the director fills it when the kit says used(slot)
var attack_cd := 0.0 ## the stand-in basic attack's cooldown
var stunned := 0.0
var slowed := 0.0 ## seconds left of any slow (0 clears them all, as the hex shield does)
var slows := {} ## speed factor -> seconds left: each slow keeps its own strength and the strongest live one counts (slow())
var grounded := 0.0 ## seconds left of grounded (the rhino's Aftershock, 2026-11-20): MatchRules.MOBILITY slots are not ready
var taunted := 0.0
var taunted_by: Node3D = null
var cage: HexShield = null
var last_hit_by: Node3D = null
var air := 0.0 ## height while thrown
var _move_tw: Tween
var _from := Vector3.ZERO
var _to := Vector3.ZERO
var _height := 0.0
var _stars: Node3D
var _mark: Sprite3D


func radius() -> float:
	return body_radius()


func can_be_hit() -> bool:
	return alive and not _untouchable()


## The kangaroo's title bout (2026-11-11) marks the pair "untouchable" so nobody else can hit or pick them (towers, minions
## and kits all go through MatchTeams.hittable). The mark is true, or the node that set it: a node mark lapses on its own
## when that machine is gone or dead, so a bout cut short can't strand anyone.
func _untouchable() -> bool:
	if not has_meta("untouchable"):
		return false  # get_meta with a null default logs an error on every call
	var u: Variant = get_meta("untouchable")
	if u is Node:
		return is_instance_valid(u) and u.get("alive") != false
	return u == true


## Whether a key or a bot may use this slot now: alive, not stunned, off cooldown, and not a mobility slot while
## grounded (MatchRules.MOBILITY). Always true outside a match.
func slot_ready(slot: String) -> bool:
	return alive and not has_meta("held_by") and stunned <= 0.0 and float(cooldowns.get(slot, 0.0)) <= 0.0 \
			and not (grounded > 0.0 and MatchRules.is_mobility(MatchTeams.machine_kind(self), slot))


## Grounded (the rhino's Aftershock): no dashes, leaps, rolls or blinks for t seconds; walking and basic attacks still
## work, and others can still move it. A second one refreshes to the longer time left; it does not stack.
func ground(t: float) -> void:
	grounded = maxf(grounded, t)


## Off the ground: thrown (air), or mid-leap by its own kit (a kit's `airborne`, the hippo's Piston Drop and the
## kangaroo's hops). Aftershock's wave passes under it.
func is_airborne() -> bool:
	if air > 0.05:
		return true
	var kit := get_node_or_null("Kit")
	return kit != null and kit.get("airborne") == true


func set_seen(v: bool) -> void:
	seen = v
	visible = alive and seen


func _tick_match(delta: float) -> void:
	for s in cooldowns:
		cooldowns[s] = maxf(cooldowns[s] - delta, 0.0)
	attack_cd = maxf(attack_cd - delta, 0.0)
	slowed = maxf(slowed - delta, 0.0)
	if slowed <= 0.0:
		slows.clear()
	for m in slows.keys():
		slows[m] -= delta
		if slows[m] <= 0.0:
			slows.erase(m)
	grounded = maxf(grounded - delta, 0.0)
	for k in boosts.keys():
		boosts[k][1] -= delta
		if boosts[k][1] <= 0.0:
			boosts.erase(k)
	if stunned > 0.0:
		stunned -= delta
		if stunned <= 0.0 and is_instance_valid(_stars):
			_stars.queue_free()
	if taunted > 0.0:
		taunted -= delta
		if taunted <= 0.0:
			taunted_by = null
			if is_instance_valid(_mark):
				_mark.queue_free()


func _forced() -> bool:
	return has_meta("held_by") or (_move_tw != null and _move_tw.is_valid() and _move_tw.is_running())


## Healing (the hummingbird's kindred link; Preston's heals to come). Raises hp up to max_hp and returns what was
## actually healed: 0 for a dead machine, a full one, or outside a match (max_hp 0). by is the healer.
func heal(amount: float, by: Node3D = null) -> float:
	if not alive or max_hp <= 0.0 or amount <= 0.0:
		return 0.0
	var before := hp
	hp = minf(hp + amount, max_hp)
	var got := hp - before
	if got > 0.0:
		healed.emit(got, by)
	return got


## Eruption's rally (the bison's kit, game feel lane, 2026-11-14): while rallied this machine hits rally_damage harder
## (take_damage asks the attacker) and its basic cooldown is divided by rally_rate (match_director.basic_cooldown_of).
## Each hit it lands on an enemy machine stretches the rally by its stretch, up to its cap. Times are physics time
## (game_time), so headless checks at --fixed-fps agree with play.
var rally_damage := 1.0
var rally_rate := 1.0
var rally_until := 0.0
var _rally_stretch := 0.0
var _rally_cap := 0.0
var dot_tick := false ## true while a kit applies a damage-over-time tick (the bison's slag); ticks do not stretch a rally


static func game_time() -> float:
	return float(Engine.get_physics_frames()) / float(Engine.physics_ticks_per_second)


func rallied() -> bool:
	return alive and game_time() < rally_until


func set_rally(damage: float, rate: float, seconds: float, stretch := 0.0, cap := 0.0) -> void:
	var now := game_time()
	rally_damage = damage
	rally_rate = rate
	rally_until = maxf(rally_until, now + seconds)
	_rally_stretch = stretch
	_rally_cap = now + maxf(cap, seconds)


## The damage multiplier for a hit this machine lands on target; a hit on an enemy machine stretches the rally.
func rally_scale(target: Node) -> float:
	if not rallied():
		return 1.0
	if _rally_stretch > 0.0 and not dot_tick and target != null and target.has_method("rallied") and MatchTeams.is_enemy(target, self):
		rally_until = minf(rally_until + _rally_stretch, _rally_cap)
	return rally_damage


func take_damage(amount: float, by: Node3D = null) -> void:
	if not alive or max_hp <= 0.0:
		return
	amount *= armour  # the pangolin's salvage (game feel lane, 2026-11-12); 1.0 for everyone else
	if by != null and is_instance_valid(by) and by != self and by.has_method("rally_scale"):
		amount *= by.rally_scale(self)  # the bison's Eruption rally (2026-11-14); 1.0 unless the attacker is rallied
	hp = maxf(hp - amount, 0.0)
	if by != null and is_instance_valid(by) and by != self:
		last_hit_by = by
	damaged.emit(amount, by)
	if hp <= 0.0:
		alive = false
		halt()
		death_hold = _death_pose()
		died.emit(by)
	_react("Hit_Front", by)


## A kit hit (the kits call hit(player), or hit(player, scale): MatchRules.kit_hit_damage x scale, so the squirrel's
## 18-damage dart passes 18 / kit_hit_damage). The kit's own passive has the first say (rhino front plating and brace,
## gorilla hex shield and dome): a blocked hit does MatchRules.blocked_share of the damage.
func hit(by: Node3D = null, scale := 1.0) -> void:
	var blocked := false
	var kit := get_node_or_null("Kit")
	if by != null and is_instance_valid(by) and kit != null and kit.has_method("take_hit"):
		blocked = kit.take_hit(by.global_position, by) if kit.get_method_argument_count("take_hit") >= 2 else kit.take_hit(by.global_position)
	else:
		sprite.modulate = Color(2.0, 2.0, 2.0)
		create_tween().tween_property(sprite, "modulate", Color.WHITE, 0.15)
		if body != null:
			body.flash()
	if by != null and is_instance_valid(by) and by != self:
		_react_blocked = blocked
		var cover: Variant = get_meta("kangaroo_cover") if has_meta("kangaroo_cover") else null  # the kangaroo's leap to an ally covers both (kangaroo lane, 2026-11-11); get_meta with a null default logs an error
		var cut: float = (1.0 - clampf(float(cover.get("share", 0.0)), 0.0, 1.0)) if cover is Dictionary else 1.0
		take_damage(MatchRules.kit_hit_damage * scale * (MatchRules.blocked_share if blocked else 1.0) * cut, by)
		_react_blocked = false


func stun(t: float) -> void:
	if _braced():
		return  # a braced kit takes no stun (the rhino's brace, gone since 2026-11-20; no kit sets braced now)
	stunned = maxf(stunned, t)
	if body != null and body.has_clip("Stun"):
		_stun_pose()
	else:
		_react("Hit_Heavy")
	if not is_instance_valid(_stars):
		_stars = Fx3D.spawn(self, "stun_loop", global_position + Vector3.UP * (2.4 * sprite.size_scale()), 0.0, true)


## Slowed for t seconds at speed factor mult (MatchRules.slow_mult, 0.6, unless given; Aftershock's is 0.7). Each
## strength keeps its own time; while slowed the strongest live one counts, so two slows never deepen.
func slow(t: float, mult := -1.0) -> void:
	var m := MatchRules.slow_mult if mult < 0.0 else mult
	slows[m] = maxf(float(slows.get(m, 0.0)), t)
	slowed = maxf(slowed, t)


## The slow's speed factor now: 1.0 when not slowed; MatchRules.slow_mult when slowed was set directly with no
## strength (ape_reveal does that).
func slow_factor() -> float:
	if slowed <= 0.0:
		return 1.0
	if slows.is_empty():
		return MatchRules.slow_mult
	var f := 1.0
	for m in slows:
		f = minf(f, float(m))
	return f


## Forced to attack `by` (gorilla chest beat): a bot obeys; the player sees the mark.
func taunt(by: Node3D, t: float) -> void:
	taunted = maxf(taunted, t)
	taunted_by = by
	if not is_instance_valid(_mark):
		_mark = Sprite3D.new()
		_mark.texture = TrainingDummy.MARK
		_mark.pixel_size = 0.02
		_mark.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		_mark.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		_mark.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		_mark.shaded = false
		_mark.position.y = 2.9 * sprite.size_scale()
		add_child(_mark)


## Thrown in an arc (horn toss). The rhino's brace makes it immune to the throw, not the hit.
func toss_to(land: Vector3, height: float, time: float, stun_t: float, deal := true) -> void:  # deal false: the lift only (the pangolin's pop)
	if deal:
		hit(MatchTeams.caster)
	if not alive or _braced():
		return
	_from = MatchTeams.flat(global_position)
	_to = MatchTeams.flat(land)
	_height = height
	var tw := _move_tween()
	tw.tween_method(_arc_step, 0.0, 1.0, time)
	await tw.finished
	air = 0.0
	global_position.y = 0.0
	Fx3D.spawn(get_parent(), "impact_puff", global_position, 0.3)
	stun(stun_t)


## Shoved aside (stampede, bound, sonic boom).
func knock_aside(offset: Vector3, time: float, deal := true) -> void:  # deal false: the push only (rhino release)
	if deal:
		hit(MatchTeams.caster)
	if not alive or _braced():
		return
	_from = MatchTeams.flat(global_position)
	_to = _from + MatchTeams.flat(offset)
	_height = 0.5
	_move_tween().tween_method(_shove_step, 0.0, 1.0, time)


func halt() -> void:
	if _move_tw != null and _move_tw.is_valid():
		_move_tw.kill()
	air = 0.0
	if is_inside_tree():
		global_position.y = 0.0


func trap(dome: HexShield) -> void:
	cage = dome


func _braced() -> bool:
	var kit := get_node_or_null("Kit")
	return kit != null and kit.get("braced") == true  # was the rhino's brace and the bison's Freight brace; both kits keep it false now (2026-11-20)


func _move_tween() -> Tween:
	halt()
	_move_tw = create_tween()
	return _move_tw


func _arc_step(k: float) -> void:
	air = _height * 4.0 * k * (1.0 - k)
	_move_to(_from.lerp(_to, k))


func _shove_step(k: float) -> void:
	air = _height * 4.0 * k * (1.0 - k)
	_move_to(_from.lerp(_to, 1.0 - (1.0 - k) * (1.0 - k)))


func _move_to(p: Vector3) -> void:
	var prev := MatchTeams.flat(global_position)
	var want := MatchTeams.flat(p) if _forced() else MatchBodies.block(self, prev, MatchTeams.flat(p), body_radius())
	var q := ArenaMotion.slide(self, prev, want - prev, body_radius())
	global_position = Vector3(q.x, air, q.z)
	_dome_walls(prev)


## Hex domes of the other team (ApeKit tags each with its team): trapped inside one until it ends, kept out of one
## from outside. The training dummy's rule, for machines.
func _dome_walls(prev: Vector3) -> void:
	if team == "":
		return
	if cage != null and (not is_instance_valid(cage) or not cage.is_up()):
		cage = null
	var r0 := body_radius()
	for dome: HexShield in HexShield.live_domes():
		if str(dome.get_meta("team", "")) == team and not dome.cage_all:  # the ult cage holds its own side too
			continue
		var c := dome.global_position
		var was := Vector2(prev.x - c.x, prev.z - c.z).length()
		var d := Vector3(global_position.x - c.x, 0.0, global_position.z - c.z)
		var inside := dome == cage or was <= dome.radius
		var r := maxf(dome.radius - r0, 0.1) if inside else dome.radius + r0
		if (inside and d.length() <= r) or (not inside and d.length() >= r):
			continue
		if not dome.blocks_at(global_position):  # through a broken panel's gap: out of the cage for good
			if cage == dome:
				cage = null
			continue
		var n := d.normalized() if d.length() > 0.001 else Vector3.RIGHT
		global_position = Vector3(c.x + n.x * r, global_position.y, c.z + n.z * r)


## Armour torn off or worn for a while (the pangolin's salvage, game feel lane, 2026-11-12): every damage taken is
## multiplied by scale until seconds pass. A newer call replaces an older one.
func set_armour(scale: float, seconds: float) -> void:
	armour = scale
	_armour_token += 1
	var token := _armour_token
	await get_tree().create_timer(seconds).timeout
	if token == _armour_token:
		armour = 1.0
