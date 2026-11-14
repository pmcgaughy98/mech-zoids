class_name DirectionalSprite3D
extends AnimatedSprite3D
## An eight-way machine sprite standing upright in the 3D world (Claude, 2026-11-04; Preston: "yes go 3D").
## Five views are drawn (s, se, e, ne, n); sw, w and nw show se, e and ne mirrored. The view shown depends on the
## machine's facing relative to the camera, rounded to 45-degree sectors: the rule Doom uses to pick a sprite
## rotation (r_things.c, studied for structure only). The sprite turns only around the vertical axis, keeps hard
## pixels (nearest filter, alpha cut) and is raised so the feet stand on the parent's origin.
## Abilities (actions) play <action>_<view> when that view is drawn. An action drawn only in front, side and back
## falls back on ACTION_VIEW: the diagonals show the side view, mirrored the same way (added for the kit,
## 2026-11-04; the own-view rule added the same day for the animation lane's se and ne action frames).
## Tilt (2026-11-04, for views drawn from the camera's angle, views_cam35): the quad faces the camera fully, leaning
## back by its pitch round the feet row, and keeps the depth an upright sprite would have (tilted_sprite_3d.gdshader).
## Off by default. tilt_to_camera tilts every animation; a SpriteFrames meta "tilt_anims" (names without the view,
## e.g. ["idle"]) tilts only those, so old-angle walks and moves stay upright. Views drawn from about 9 degrees stand.
## Planting (camera and perspective lane, 2026-11-04; Preston: the rhino's "top views look like its floating"): the
## frames are pinned on their lowest foot, but in a drawing seen from above the lowest foot is the NEAR one, so the
## body was drawn behind its own spot, up to 0.76 m in the back views. Frames with a "feet" meta (texels from the
## canvas centre column: {"front": 7, "rear": -33, "half_width": 20}) are moved toward the camera so the drawing's
## ground centre stands on the machine's spot, for this camera (plant_offset). Without the meta nothing moves.

## Sector 0..4 measured to the right of "facing away from the camera".
const VIEWS: Array[String] = ["n", "ne", "e", "se", "s"]
const ACTION_VIEW := {"n": "n", "ne": "e", "e": "e", "se": "e", "s": "s"}

## Metres per sprite texel by size class (Preston, 2026-11-04, option B; docs/art/moba/ROSTER.md "Size in the 3D
## world"). L shares the world's 50 texels per metre; M and S machines are drawn at their own texel size.
const METRES_PER_TEXEL := {"L": 0.020, "M": 0.018, "S": 0.016}
## The L rhino's canvas in metres (192 texels x 0.020): size_scale() measures other machines against it.
const REFERENCE_CANVAS_M := 3.84
## The tilted mode's material: drawn tilted, with the depth an upright sprite would have (so walls behind it can't
## cut its top). Added for Mech-Zoids' camera-angle test, 2026-11-04.
const TILT_SHADER := preload("res://scripts/moba3d/tilted_sprite_3d.gdshader")
## The pitch the views are drawn from (planting): the approved views about 9 degrees (MATCH_NOTES), the cam35 set 35.
const DRAWN_PITCH_UPRIGHT := 9.0
const DRAWN_PITCH_TILTED := 35.0

@export var canvas_height := 192 ## the frame canvas: 192 for the L machines, 160 for the M and S ones
@export var feet_edge_row := 161 ## one below the foot row: 192/160 -> 161, 160/130 -> 131, 160/140 -> 141
@export_enum("L", "M", "S") var size_class := "L": ## sets the texel size; the class is in ROSTER.md
	set(v):
		size_class = v
		if is_node_ready():
			_apply_size()

## Off: the quad stands upright and turns only round the vertical axis (the game today). On: every animation is drawn
## facing the camera, leaning back by its pitch round the feet row. The node itself never moves either way.
@export var tilt_to_camera := false:
	set(v):
		tilt_to_camera = v
		if is_node_ready():
			_apply_tilt()

## On: frames with a "feet" meta stand their drawn ground centre on the machine's spot (see Planting above).
@export var plant_feet := true:
	set(v):
		plant_feet = v
		if is_node_ready():
			_plant()

var view := "n"
## A short offset the hit feel adds on top of where the sprite stands (KitFeel.basic_hit: the lunge and the shove),
## in the parent's space. Setting it moves the sprite at once; _plant and _apply_size keep it.
var feel_offset := Vector3.ZERO:
	set(v):
		position += v - feel_offset
		feel_offset = v
var mirrored := false
var action := "" ## while set, the sprite plays <action>_<s|e|n> in place of the walk or idle
var hold := false ## the action is paused on one frame (brace holds its planted pose)
var hold_at := 0
## While a held action moves (braced and walking), its shuffle plays (shuffle_anim), or the walk if no shuffle is
## drawn, so the feet step instead of the planted pose sliding; it snaps back to the held frame on stopping.
var walk_while_held := true
var _cam_basis := Basis.IDENTITY ## the camera basis show_facing last saw (planting moves the sprite toward it)
var _have_cam := false
var _tilt_mat: ShaderMaterial ## this sprite's own tilted material (not copied by duplicate(): not exported)


func _ready() -> void:
	texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	shaded = false
	centered = true
	billboard = BaseMaterial3D.BILLBOARD_FIXED_Y  # upright views turn round the vertical axis; the tilt shader ignores this and does its own
	frame_changed.connect(_sync_tilt_texture)
	animation_changed.connect(_apply_tilt)
	sprite_frames_changed.connect(_apply_tilt)
	animation_changed.connect(_plant)  # after _apply_tilt: the move depends on whether the new animation is tilted
	sprite_frames_changed.connect(_plant)
	_apply_size()


## The texel size from the class, and the sprite raised so the feet stand on the parent's origin.
func _apply_size() -> void:
	pixel_size = METRES_PER_TEXEL.get(size_class, 0.020)
	position.y = (feet_edge_row - canvas_height / 2.0) * pixel_size + feel_offset.y
	_apply_tilt()
	_plant()


## Whether the animation playing now is drawn tilted.
func tilted_now() -> bool:
	if tilt_to_camera:
		return true
	if sprite_frames == null or not sprite_frames.has_meta("tilt_anims"):
		return false
	return String(animation).rsplit("_", true, 1)[0] in (sprite_frames.get_meta("tilt_anims") as Array)


## Whether any animation of this sprite can be tilted (the HUD sets bars higher over such machines, so a bar doesn't
## jump each time the machine starts or stops walking).
func tilts_any() -> bool:
	return tilt_to_camera or (sprite_frames != null and not (sprite_frames.get_meta("tilt_anims", []) as Array).is_empty())


## The machine's feet from its frames' "feet" meta, in metres: "front" and "rear" along the body from the canvas
## centre column (forward is +), "half_width" across. A machine whose front and rear pairs stand at different widths
## (the gorilla's knuckles are wider than its feet) can give "front_half_width" and "rear_half_width"; either one
## missing falls back on "half_width", and "half_width" missing becomes the wider pair. "shadow_half_width" sets the
## contact shadow's width when the wider pair would make it stick out past a narrow body (the fennec sits on wide
## haunches behind thin front legs); it falls back on "half_width". Empty without the meta.
func feet_model() -> Dictionary:
	if sprite_frames == null or not sprite_frames.has_meta("feet"):
		return {}
	var f: Dictionary = sprite_frames.get_meta("feet")
	var hw := float(f.get("half_width", maxf(float(f.get("front_half_width", 0.0)), float(f.get("rear_half_width", 0.0)))))
	return {"front": float(f["front"]) * pixel_size, "rear": float(f["rear"]) * pixel_size, "half_width": hw * pixel_size,
			"front_half_width": float(f.get("front_half_width", hw)) * pixel_size,
			"rear_half_width": float(f.get("rear_half_width", hw)) * pixel_size,
			"shadow_half_width": float(f.get("shadow_half_width", hw)) * pixel_size}


## The view the frame on screen is drawn in: the animation's own suffix (an action falling back on ACTION_VIEW is
## drawn in that view), else the view picked last.
func drawn_view() -> String:
	var parts := String(animation).rsplit("_", true, 1)
	return parts[1] if parts.size() == 2 and parts[1] in VIEWS else view


## The way the frame on screen shows the machine facing, as a world direction for this camera: its 45-degree view,
## mirrored as drawn. The contact shadow turns to this, so it always matches the picture.
func drawn_facing(camera_basis: Basis) -> Vector3:
	var away := Vector3(-camera_basis.z.x, 0.0, -camera_basis.z.z)
	if away.length_squared() < 0.0001:  # looking straight down: the camera's up points away
		away = Vector3(camera_basis.y.x, 0.0, camera_basis.y.z)
	away = away.normalized()
	var right := Vector3(-away.z, 0.0, away.x)  # away turned 90 degrees to the screen's right
	var a := VIEWS.find(drawn_view()) * PI / 4.0 * (-1.0 if flip_h else 1.0)
	return (away * cos(a) + right * sin(a)).normalized()


## How far toward the camera the nearest foot stands from the machine's spot, in a view (0 = n, drawn facing away,
## to 4 = s, facing the camera). That foot is the drawing's lowest, the one the frame is pinned on.
static func near_foot_depth(feet: Dictionary, view_index: int) -> float:
	var a := view_index * PI / 4.0
	var forward_toward := -cos(a)  # how much of the body's forward axis points at the camera
	var across := absf(sin(a))
	var hw: float = feet.get("half_width", 0.0)
	return maxf(feet["front"] * forward_toward + float(feet.get("front_half_width", hw)) * across,
			feet["rear"] * forward_toward + float(feet.get("rear_half_width", hw)) * across)


## The move toward the camera that stands the drawing's ground centre on the machine's spot. In a view drawn from
## pitch phi the ground centre is drawn h = depth * sin(phi) above the pinned near foot. On a quad leaning back by q
## (the camera's pitch when tilted, 0 upright) seen from theta above the horizon, moving the pin d along the floor
## toward the camera moves it down the screen as much as h does when d = h * (sin q + cos q / tan theta).
## At the normal chase camera (theta about 38) that is about 0.92 x depth tilted and 0.20 x depth upright.
static func plant_offset(feet: Dictionary, view_name: String, tilted: bool, camera_basis: Basis, camera_pos: Vector3,
		machine_pos: Vector3) -> Vector3:
	var i := VIEWS.find(view_name)
	if feet.is_empty() or i < 0:
		return Vector3.ZERO
	var toward := Vector3(camera_basis.z.x, 0.0, camera_basis.z.z)
	if toward.length_squared() < 0.000001:
		return Vector3.ZERO  # straight down: the near foot is right under the spot
	toward = toward.normalized()
	var h := near_foot_depth(feet, i) * sin(deg_to_rad(DRAWN_PITCH_TILTED if tilted else DRAWN_PITCH_UPRIGHT))
	var sin_q := clampf(camera_basis.z.y, 0.0, 1.0) if tilted else 0.0
	var cos_q := sqrt(1.0 - sin_q * sin_q)
	var v := camera_pos - machine_pos
	var tan_theta := maxf(v.y / maxf(Vector2(v.x, v.z).length(), 0.001), 0.1)
	return toward * h * (sin_q + cos_q / tan_theta)


## Moves the sprite toward the camera by plant_offset (only sideways along the floor; the height stays the feet's).
func _plant(_a = null) -> void:
	var p := get_parent() as Node3D
	var off := Vector3.ZERO
	var feet := feet_model()
	if plant_feet and _have_cam and p != null and not feet.is_empty():
		var cam: Camera3D = get_viewport().get_camera_3d() if is_inside_tree() else null
		var cam_pos := cam.global_position if cam != null else p.global_position + _cam_basis.z * 6.5
		off = plant_offset(feet, drawn_view(), tilted_now(), _cam_basis, cam_pos, p.global_position)
	var local := off if p == null else p.global_basis.inverse() * off
	position = Vector3(local.x, (feet_edge_row - canvas_height / 2.0) * pixel_size, local.z) + feel_offset


## Swaps the tilted material on or off for the animation playing now. The shader pivots on the feet ("lift" metres
## under the node), so the node's position is the same both ways and nothing that moves it has to know.
func _apply_tilt() -> void:
	var on := tilted_now()
	if on and not _tilt_material():
		# A machine copied with duplicate() (the match's bots) arrives holding its source's material. Sharing it made
		# every copy draw from whichever sheet synced last (2026-11-05: the player's rhino drew the fennec's sheet and
		# vanished), so each sprite makes and keeps its own.
		_tilt_mat = ShaderMaterial.new()
		_tilt_mat.shader = TILT_SHADER
		material_override = _tilt_mat
	elif not on and material_override is ShaderMaterial and (material_override as ShaderMaterial).shader == TILT_SHADER:
		material_override = null
	if on:
		(material_override as ShaderMaterial).set_shader_parameter("lift", (feet_edge_row - canvas_height / 2.0) * pixel_size)
		_sync_tilt_texture()


func _tilt_material() -> bool:  ## true only for this sprite's own tilted material, never one a copy inherited
	return _tilt_mat != null and material_override == _tilt_mat


## The tilted material draws the frame's texture itself (an atlas frame's sheet: the quad's UVs are in sheet space).
func _sync_tilt_texture() -> void:
	if not _tilt_material() or sprite_frames == null or not sprite_frames.has_animation(animation):
		return
	var t := sprite_frames.get_frame_texture(animation, frame)
	while t is AtlasTexture:
		t = (t as AtlasTexture).atlas
	(material_override as ShaderMaterial).set_shader_parameter("tex", t)


## How big this machine's canvas stands in the world next to the L rhino's (1.0 for L on 192). Things sized for the
## rhino (the ground ring, the contact shadow, a hex shield) scale by it: M on 160 is 0.75, S on 160 is 0.67.
func size_scale() -> float:
	return canvas_height * METRES_PER_TEXEL.get(size_class, 0.020) / REFERENCE_CANVAS_M


## Which of the 9 sector numbers (-4..4) a facing falls in, seen from a camera with this basis.
## 0 = facing away (back view), 2 = facing screen-right (side view), +-4 = facing the camera (front view);
## negative sectors face screen-left and are drawn mirrored.
static func sector(facing: Vector3, camera_basis: Basis) -> int:
	var fwd := Vector3(-camera_basis.z.x, 0.0, -camera_basis.z.z)
	var right := Vector3(camera_basis.x.x, 0.0, camera_basis.x.z)
	var f := Vector3(facing.x, 0.0, facing.z)
	if f.length_squared() < 0.0001 or fwd.length_squared() < 0.0001:
		return 4
	f = f.normalized()
	var a := atan2(f.dot(right.normalized()), f.dot(fwd.normalized()))
	return int(round(a / (PI / 4.0)))


func show_facing(facing: Vector3, camera_basis: Basis, moving: bool) -> void:
	var s := sector(facing, camera_basis)
	var was_mirrored := mirrored
	view = VIEWS[absi(s)]
	mirrored = s < 0 and absi(s) < 4
	flip_h = mirrored
	_cam_basis = camera_basis
	_have_cam = true
	_plant()
	if action != "" and not (hold and moving and walk_while_held):
		_show_action(false)
		return
	var anim := StringName(("walk_" if moving else "idle_") + view)
	if action != "" and moving:  # held and moving: the action's shuffle if one is drawn, else the walk
		var sh := shuffle_anim()
		if sh != &"":
			anim = sh
	# A mirrored view (sw, w, nw) shows the far legs as the near ones, so the same frame number would put the other
	# physical foot up. A flip into or out of a mirrored view mid-walk moves half a loop on to keep the same foot up
	# (the walk lane's turn note, 2026-11-05: sw, w and nw at frame (i+4) mod 8; tools/debug/walk_turn_check.gd).
	# Only right for alternating walks. A hop (kangaroo, squirrel, if they ever hop) has no left and right halves, and
	# this would jump it from take-off to mid-air: such a machine needs an offset of 0 (a per-machine switch). Nothing
	# hops yet (walk lane via the hub, 2026-11-05).
	var half := 0
	if moving and mirrored != was_mirrored and sprite_frames.get_frame_count(anim) % 2 == 0:
		half = sprite_frames.get_frame_count(anim) >> 1
	if animation == anim and is_playing():
		if half > 0:  # e to w and back keeps the same animation; only the mirror changes
			set_frame_and_progress((frame + half) % sprite_frames.get_frame_count(anim), frame_progress)
		return
	# Turning mid-step keeps the step: the new view picks up at the same frame of the same loop, half a loop on across
	# a mirror flip.
	var same_loop := String(animation).rsplit("_", true, 1)[0] == String(anim).rsplit("_", true, 1)[0]
	var f := frame
	var p := frame_progress
	play(anim)
	if moving and same_loop:
		set_frame_and_progress((f + half) % sprite_frames.get_frame_count(anim), p)


## The held action's shuffle for this view (<action>_shuffle_<view>; se and ne fall back on e), or &"" if none is
## drawn. The rhino's brace_shuffle came from the animation lane, 2026-11-04.
func shuffle_anim() -> StringName:
	if action == "" or sprite_frames == null:
		return &""
	for v in [view, ACTION_VIEW[view]]:
		var a := StringName(action + "_shuffle_" + v)
		if sprite_frames.has_animation(a):
			return a
	return &""


## Starts an ability's animation from its first frame, in the view the camera last saw.
func play_action(action_name: String) -> void:
	action = action_name
	hold = false
	speed_scale = 1.0
	_show_action(true)


func stop_action() -> void:
	action = ""
	hold = false
	speed_scale = 1.0


## Pauses the action on frame f.
func hold_frame(f: int) -> void:
	hold = true
	hold_at = f
	set_frame_and_progress(f, 0.0)
	pause()


## Plays the action on from frame f after a hold, at speed (1.0 unless the kit passes its own: a sped-up swing
## passes its rate so the tail keeps it; the gorilla's and rhino's basics, 2026-11-05). The reset matters: during a
## brace hold the walk drives speed_scale for the shuffle, and that must not carry into the action.
## A braced machine may be mid-walk when released, so the action's own animation comes back first.
func release_from(f: int, speed := 1.0) -> void:
	hold = false
	speed_scale = speed
	var anim := action_anim()
	if animation != anim:
		play(anim)
	set_frame_and_progress(f, 0.0)
	play()


## The action's animation for the current view: its own drawing if the sheet has one, else the ACTION_VIEW fallback.
func action_anim() -> StringName:
	var own := StringName(action + "_" + view)
	if sprite_frames != null and sprite_frames.has_animation(own):
		return own
	return StringName(action + "_" + ACTION_VIEW[view])


func _show_action(restart: bool) -> void:
	var anim := action_anim()
	if animation == anim and not restart:
		return
	# Turning mid-action keeps the frame, as turning mid-walk keeps the step.
	var f := frame
	var p := frame_progress
	play(anim)
	if restart:
		set_frame_and_progress(0, 0.0)
	elif hold:
		set_frame_and_progress(hold_at, 0.0)
	else:
		set_frame_and_progress(mini(f, sprite_frames.get_frame_count(anim) - 1), p)
	if hold:
		pause()
