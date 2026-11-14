class_name ArrivalShield
extends Node3D
## The fennec's arrival shield (Claude, 2026-11-05, game feel lane, effects spin-off; Preston: "Arrival shield"). The
## great gate (slot 4) carries the team to its far gate, "arriving with a short shield and a burst of speed"
## (docs/plan/moba-kits.md). This is that arrival on one machine, any ally:
##   the shell: a bell of the gate's violet light round the machine, standing on the floor (tools/art/
##     draw_fennec_arrival_shield.py). It rises up both sides from the floor and closes at the top, holds with a band
##     of light rising through it, then flickers and drifts away as motes (expire) or cracks and shatters (hit()).
##     Two sizes, each in texels and laid on at the wearer's own texel: "s" for S and M machines, "l" for L ones.
##   the ring on the floor under it.
##   the speed burst: while it lasts and the machine moves, mint afterimages of its own frame are left behind it.
## The effect only shows the shield and the speed. Their numbers (how much it absorbs, how fast, how long) belong to the
## great gate when it is built (the hub holds it): life and speed_life here are placeholders, and nothing here changes
## the machine's speed. Something that hits a shielded machine calls hit() (ArrivalShield.on(machine)).
## Made from its path (preload), and nothing here names ArrivalShield as a value: a new class_name is unknown until the
## editor or an import refreshes the class cache (ANIMATION_PLAYBOOK.md section 11).

signal ended(why: String) ## "expire" or "break", when the shell is gone (the speed afterimages may go on)

const SCRIPT := "res://scripts/moba3d/arrival_shield.gd"
const DIR := "res://art/fx/moba3d/arrival_shield/"
const SHADER := preload("res://scripts/moba3d/tilted_fx_3d.gdshader")
const COLS := 8
const ROWS := 4
const FORM := 0 ## sheet rows
const HOLD := 1
const EXPIRE := 2
const BREAK := 3
const DONE := 4
## ms a frame, per row (form 310 ms, hold a 640 ms loop, expire 300 ms, break 250 ms)
const MS: Array = [[40, 40, 40, 50, 60, 80], [80, 80, 80, 80, 80, 80, 80, 80], [60, 60, 60, 60, 60], [50, 50, 50, 50, 50]]
## Per size, in texels (draw_fennec_arrival_shield.py SIZES): cell width, height, the feet edge row, the floor cell.
const SIZES := {"s": [128, 128, 120, 96], "l": [152, 144, 136, 112]}
const NUDGE := 0.15 ## metres toward the camera, so the shell draws over the body it stands round
## Afterimages: 0.1 s apart and 0.25 s long hid behind the fennec at its walk (clip 2026-11-05), so closer and longer.
const TRAIL_EVERY := 0.065 ## seconds between afterimages while it moves (every 2nd frame at 30 fps)
const TRAIL_LIFE := 0.4
const TRAIL_FADE := 0.5 ## an afterimage's alpha as it is left
const TRAIL_BEHIND := 0.25 ## metres away from the camera: the body hides it until it walks on
const TRAIL_MIN_SPEED := 0.3 ## metres a second
const MINT := Color(0.247, 0.910, 0.690)
const MINT_W := Color(0.965, 1.0, 0.984)

static var _mats := {} ## "size texel" -> [shell, floor]
static var _floor_shader: Shader

@export var life := 2.0 ## seconds from the arrival to the expire (a placeholder: the great gate's number)
@export var speed_life := 1.2 ## seconds of afterimages (a placeholder: the great gate's number)

var machine: Node3D
var sprite: AnimatedSprite3D
var size := "s"
var px := 0.016 ## the wearer's texel
var part := FORM
var frame := -1
var trails := 0 ## afterimages left so far
var ended_by := ""
var _t := 0.0 ## seconds into the part
var _age := 0.0
var _trail_t := 0.0
var _last := Vector3.ZERO
var _shell: MeshInstance3D
var _floor: MeshInstance3D


## Puts the arrival on a machine (a Node3D with a "Sprite" child): a new one replaces one already on it.
static func play(target: Node3D, life_s := 2.0, speed_s := 1.2) -> Node3D:
	var old := on(target)
	if old != null:
		old.queue_free()
	var s = load(SCRIPT).new()
	s.machine = target
	s.sprite = target.get_node_or_null("Sprite") as AnimatedSprite3D
	s.life = life_s
	s.speed_life = speed_s
	if s.sprite != null:
		s.size = "l" if str(s.sprite.get("size_class")) == "L" else "s"
		s.px = s.sprite.pixel_size
	s.name = "ArrivalShield"
	s.set_meta("arrival_shield", true)
	target.add_child(s)
	return s


## The arrival shield on a machine now, or null.
static func on(target: Node) -> Node3D:
	for c in target.get_children():
		if c.has_meta("arrival_shield") and not c.is_queued_for_deletion():
			return c
	return null


## A hit takes the shell: it shatters. The speed afterimages go on.
func hit() -> void:
	if is_up():
		_start(BREAK)


## Ends it early: it fades as it would at the end of its life.
func end() -> void:
	if is_up():
		_start(EXPIRE)


func is_up() -> bool:
	return part == FORM or part == HOLD


func _ready() -> void:
	var cell: Array = SIZES[size]
	var w: int = cell[0]
	var h: int = cell[1]
	var fw: int = cell[3]
	var lift := (float(cell[2]) - h / 2.0) * px
	var key := "%s %.3f" % [size, px]
	if not _mats.has(key):
		var sm := ShaderMaterial.new()
		sm.shader = SHADER
		sm.set_shader_parameter("tex", SmallGate.tex_or_disk(DIR + "arrival_shield_%s.png" % size))
		sm.set_shader_parameter("lift", lift)
		if _floor_shader == null:
			_floor_shader = Shader.new()
			_floor_shader.code = """shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never;
uniform sampler2D tex : source_color, filter_nearest;
instance uniform vec4 uv_rect = vec4(0.0, 0.0, 1.0, 1.0);
void fragment() {
	vec4 c = texture(tex, uv_rect.xy + UV * uv_rect.zw);
	if (c.a < 0.02) { discard; }
	ALBEDO = c.rgb;
	ALPHA = c.a;
}
"""
		var fm := ShaderMaterial.new()
		fm.shader = _floor_shader
		fm.set_shader_parameter("tex", SmallGate.tex_or_disk(DIR + "arrival_floor_%s.png" % size))
		_mats[key] = [sm, fm]
	_shell = MeshInstance3D.new()
	_shell.name = "ArrivalShell"
	var q := QuadMesh.new()
	q.size = Vector2(w, h) * px
	_shell.mesh = q
	_shell.material_override = _mats[key][0]
	_shell.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_shell)
	_floor = MeshInstance3D.new()
	_floor.name = "ArrivalFloor"
	var pm := PlaneMesh.new()
	pm.size = Vector2.ONE * fw * px
	_floor.mesh = pm
	_floor.material_override = _mats[key][1]
	_floor.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_floor)
	_last = machine.global_position
	_place()
	_show(0)


func _process(delta: float) -> void:
	_age += delta
	_t += delta
	_place()
	_trail(delta)
	if part == HOLD and _age >= life:
		_start(EXPIRE)
	if part == DONE:
		if _age >= speed_life:
			queue_free()
		return
	var ms: Array = MS[part]
	if part == HOLD:
		_show(int(_t * 1000.0 / float(ms[0])) % ms.size())
		return
	var s := 0.0
	for i in ms.size():
		s += ms[i] / 1000.0
		if _t < s:
			_show(i)
			return
	if part == FORM:
		_start(HOLD)
	else:
		ended_by = "expire" if part == EXPIRE else "break"
		part = DONE
		_shell.visible = false
		_floor.visible = false
		ended.emit(ended_by)


func _start(p: int) -> void:
	part = p
	_t = 0.0
	frame = -1
	_show(0)


func _show(i: int) -> void:
	if i == frame or part == DONE:
		return
	frame = i
	var r := Vector4(float(i) / COLS, float(part) / ROWS, 1.0 / COLS, 1.0 / ROWS)
	_shell.set_instance_shader_parameter("uv_rect", r)
	_floor.set_instance_shader_parameter("uv_rect", r)


## The machine's feet: the planted sprite's anchor, less its own lift.
func _feet() -> Vector3:
	if sprite == null:
		return machine.global_position
	var canvas: float = float(sprite.get("canvas_height")) if sprite.get("canvas_height") != null else 192.0
	var feet_row: float = float(sprite.get("feet_edge_row")) if sprite.get("feet_edge_row") != null else canvas
	return sprite.global_position - Vector3(0.0, (feet_row - canvas / 2.0) * sprite.pixel_size, 0.0)


func _place() -> void:
	if part == DONE:
		return
	var cell: Array = SIZES[size]
	var feet := _feet()
	var centre := feet + Vector3(0.0, (cell[2] - cell[1] / 2.0) * px, 0.0)
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		centre += (cam.global_position - centre).normalized() * NUDGE  # along its own sight line: same place on screen
	_shell.global_position = centre
	_floor.global_position = feet + Vector3(0.0, 0.035, 0.0)
	var shown := sprite == null or sprite.visible
	_shell.visible = shown
	_floor.visible = shown


func _trail(delta: float) -> void:
	var p := machine.global_position
	var moved := Vector2(p.x - _last.x, p.z - _last.z).length() / maxf(delta, 1e-4)
	_last = p
	if _age > speed_life or sprite == null or not sprite.visible:
		return
	_trail_t += delta
	if moved < TRAIL_MIN_SPEED or _trail_t < TRAIL_EVERY:
		return
	_trail_t = 0.0
	_afterimage()


## The sprite's frame as it is now, in mint, left where it stands and fading (the blink flash's ghost, made the same
## way). It starts behind the body on the camera's sight line, so it shows only once the machine has walked on.
func _afterimage() -> void:
	if sprite.sprite_frames == null or not sprite.sprite_frames.has_animation(sprite.animation):
		return
	var tx := sprite.sprite_frames.get_frame_texture(sprite.animation, sprite.frame)
	if tx == null:
		return
	var atlas: Texture2D = tx
	var rect := Rect2(Vector2.ZERO, tx.get_size())
	if tx is AtlasTexture:
		atlas = (tx as AtlasTexture).atlas
		rect = (tx as AtlasTexture).region
	var sz := atlas.get_size()
	var uv := Vector4(rect.position.x / sz.x, rect.position.y / sz.y, rect.size.x / sz.x, rect.size.y / sz.y)
	if sprite.flip_h:
		uv = Vector4(uv.x + uv.z, uv.y, -uv.z, uv.w)
	var canvas: float = float(sprite.get("canvas_height")) if sprite.get("canvas_height") != null else rect.size.y
	var feet_row: float = float(sprite.get("feet_edge_row")) if sprite.get("feet_edge_row") != null else rect.size.y
	var m := ShaderMaterial.new()
	m.shader = SHADER
	m.set_shader_parameter("tex", atlas)
	m.set_shader_parameter("lift", (feet_row - canvas / 2.0) * sprite.pixel_size)
	m.set_shader_parameter("tint", MINT)
	m.set_shader_parameter("tint_mix", 1.0)
	m.set_shader_parameter("rim", MINT_W)
	m.set_shader_parameter("rim_mix", 1.0)
	m.set_shader_parameter("fade", TRAIL_FADE)
	var g := MeshInstance3D.new()
	g.name = "ArrivalTrail%d" % trails  # siblings with one name get renamed (playbook section 11)
	var q := QuadMesh.new()
	q.size = rect.size * sprite.pixel_size
	g.mesh = q
	g.material_override = m
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	g.set_instance_shader_parameter("uv_rect", uv)
	g.add_to_group("arrival_trail")
	machine.get_parent().add_child(g)
	var at := sprite.global_position
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		at -= (cam.global_position - at).normalized() * TRAIL_BEHIND
	g.global_position = at
	var tw := g.create_tween()
	tw.tween_method(func(v: float) -> void: m.set_shader_parameter("fade", v), TRAIL_FADE, 0.0, TRAIL_LIFE)
	tw.tween_callback(g.queue_free)
	trails += 1
