class_name BlinkFlash
extends Node3D
## The fennec's blink flash (Claude, 2026-11-05, game feel lane, effects spin-off; Preston: "Blink flash"). The blink
## is instant, so this is the light at both ends: OUT where the fennec leaves, IN where it lands. The blink gate's
## blink and recast use it now, and the 11-05 kit's pocket gates (jump through) will.
## Three parts on one timeline:
##   the ghost: the fennec's own frame drawn in light on the tilted quad (tilted_fx_3d.gdshader's tint, rim, fade and
##     scan), so it has the fennec's shape from every view and in every pose. OUT: a white flash of the shape that
##     squeezes to a sliver. IN: the shape opens out of the slit in white and fades to show the body.
##   the standing sheet (tools/art/draw_fennec_blink.py): the slit, the star at chest height, sparks and motes.
##   the floor ring, flat on the floor.
## IN hides the fennec's sprite until its ghost is full width (130 ms), so it appears out of the light, not before it.
## Made from its path by the kit (preload), and nothing here names BlinkFlash as a value: a new class_name is unknown
## until the editor or an import refreshes the class cache (ANIMATION_PLAYBOOK.md section 11).

const SCRIPT := "res://scripts/moba3d/blink_flash.gd"
const DIR := "res://art/fx/moba3d/blink_flash/"
const SHADER := preload("res://scripts/moba3d/tilted_fx_3d.gdshader")
const PX := 0.016 ## the fennec's texel
const W := 64 ## blink_sheet cells
const H := 112
const FEET_EDGE := 108 ## the floor is the top edge of this row
const FLOOR_W := 72 ## blink_floor cells
const FRAMES := 6
const OUT := 0 ## sheet rows
const IN := 1
const MS: Array = [[40, 40, 50, 60, 70, 80], [40, 40, 50, 60, 70, 80]] ## per row, ms a frame (340 ms)
const WHITE := Color(0.965, 1.0, 0.984) ## MINT_W
const PALE := Color(0.784, 1.0, 0.941) ## MINT_P
const MINT := Color(0.247, 0.910, 0.690)
## The ghost per frame: [width (1 = the body), tint white -> pale (0..1), fade, scan]; empty = no ghost that frame.
const GHOST: Array = [
	[[1.0, 0.0, 1.0, 0.0], [0.4, 1.0, 0.9, 1.0 / 3.0], [], [], [], []],
	[[], [], [0.75, 0.0, 1.0, 0.0], [1.0, 0.5, 0.8, 0.0], [1.0, 1.0, 0.4, 1.0 / 3.0], []],
]

static var _sheet_mat: ShaderMaterial
static var _floor_mat: ShaderMaterial

var row := OUT
var frame := -1
var sprite: Node3D ## the machine's DirectionalSprite3D (OUT: where it was; IN: the one to show)
var _t := 0.0
var _stand: MeshInstance3D
var _floor: MeshInstance3D
var _ghost: MeshInstance3D
var _ghost_mat: ShaderMaterial
var _ghost_at := Vector3.ZERO
var _hid := false


## A flash at pos (on the floor). kind: OUT or IN. sprite: the machine's sprite, for the ghost (OUT: call it before the
## machine moves). The node frees itself when done (340 ms).
static func play(parent: Node, pos: Vector3, kind: int, machine_sprite: Node3D = null) -> Node3D:
	var f = load(SCRIPT).new()
	f.row = kind
	f.sprite = machine_sprite
	f.name = "BlinkFlashOut" if kind == OUT else "BlinkFlashIn"
	parent.add_child(f)
	f.global_position = pos
	if kind == OUT and machine_sprite != null:
		f._make_ghost()  # now, while the sprite still stands here
	elif kind == IN and machine_sprite != null:
		machine_sprite.visible = false
		f._hid = true
	f._show(0)
	return f


static func _sheet_material(file: String, lift: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SHADER
	m.set_shader_parameter("tex", SmallGate.tex_or_disk(DIR + file))
	m.set_shader_parameter("lift", lift)
	return m


func _ready() -> void:
	var lift := (FEET_EDGE - H / 2.0) * PX
	if _sheet_mat == null:
		_sheet_mat = _sheet_material("blink_sheet.png", lift)
		_floor_mat = ShaderMaterial.new()
		var fs := Shader.new()
		fs.code = """shader_type spatial;
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
		_floor_mat.shader = fs
		_floor_mat.set_shader_parameter("tex", SmallGate.tex_or_disk(DIR + "blink_floor.png"))
	_stand = MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(W, H) * PX
	_stand.mesh = q
	_stand.material_override = _sheet_mat
	_stand.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_stand.position = Vector3(0.0, lift, 0.0)
	add_child(_stand)
	_floor = MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2.ONE * FLOOR_W * PX
	_floor.mesh = pm
	_floor.material_override = _floor_mat
	_floor.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_floor.position = Vector3(0.0, 0.035, 0.0)
	add_child(_floor)


func _process(delta: float) -> void:
	_t += delta
	var s := 0.0
	var ms: Array = MS[row]
	for i in ms.size():
		s += ms[i] / 1000.0
		if _t < s:
			_show(i)
			return
	queue_free()


func _exit_tree() -> void:
	_unhide()
	if is_instance_valid(_ghost):
		_ghost.queue_free()


func _unhide() -> void:
	if _hid and is_instance_valid(sprite):
		sprite.visible = true
	_hid = false


func _show(i: int) -> void:
	if i == frame:
		return
	frame = i
	_stand.set_instance_shader_parameter("uv_rect", Vector4(float(i) / FRAMES, row / 2.0, 1.0 / FRAMES, 0.5))
	_floor.set_instance_shader_parameter("uv_rect", Vector4(float(i) / FRAMES, row / 2.0, 1.0 / FRAMES, 0.5))
	var g: Array = GHOST[row][i]
	if g.is_empty():
		if is_instance_valid(_ghost):
			_ghost.visible = false
		return
	if row == IN:
		if i >= 3:
			_unhide()  # under the full-width ghost; at frame 2 the narrower ghost would leave the body's edges out
		if not is_instance_valid(_ghost):
			_make_ghost()
	if not is_instance_valid(_ghost):
		return
	_ghost.visible = true
	_ghost.scale = Vector3(g[0], 1.0, 1.0)
	_ghost_mat.set_shader_parameter("tint", WHITE.lerp(PALE, g[1]))
	_ghost_mat.set_shader_parameter("fade", g[2])
	_ghost_mat.set_shader_parameter("scan", g[3])


## The ghost: the sprite's frame as it is now, drawn in light where the sprite stands. Its own node under the flash's
## parent, so it stays put when the machine moves.
func _make_ghost() -> void:
	if not is_instance_valid(sprite) or not (sprite is AnimatedSprite3D):
		return
	var spr := sprite as AnimatedSprite3D
	if spr.sprite_frames == null or not spr.sprite_frames.has_animation(spr.animation):
		return
	var tx := spr.sprite_frames.get_frame_texture(spr.animation, spr.frame)
	var atlas: Texture2D = tx
	var rect := Rect2(Vector2.ZERO, tx.get_size())
	if tx is AtlasTexture:
		atlas = (tx as AtlasTexture).atlas
		rect = (tx as AtlasTexture).region
	var size := atlas.get_size()
	var uv := Vector4(rect.position.x / size.x, rect.position.y / size.y, rect.size.x / size.x, rect.size.y / size.y)
	if spr.flip_h:
		uv = Vector4(uv.x + uv.z, uv.y, -uv.z, uv.w)
	var canvas: float = float(spr.get("canvas_height")) if spr.get("canvas_height") != null else rect.size.y
	var feet: float = float(spr.get("feet_edge_row")) if spr.get("feet_edge_row") != null else rect.size.y
	var lift := (feet - canvas / 2.0) * spr.pixel_size
	_ghost_mat = ShaderMaterial.new()
	_ghost_mat.shader = SHADER
	_ghost_mat.set_shader_parameter("tex", atlas)
	_ghost_mat.set_shader_parameter("lift", lift)
	_ghost_mat.set_shader_parameter("tint_mix", 1.0)
	_ghost_mat.set_shader_parameter("rim_mix", 1.0)
	_ghost_mat.set_shader_parameter("rim", MINT)
	_ghost = MeshInstance3D.new()
	_ghost.name = "BlinkGhostOut" if row == OUT else "BlinkGhostIn"  # two "BlinkGhost" siblings: Godot renames one
	var q := QuadMesh.new()
	q.size = rect.size * spr.pixel_size
	_ghost.mesh = q
	_ghost.material_override = _ghost_mat
	_ghost.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_ghost.set_instance_shader_parameter("uv_rect", uv)
	get_parent().add_child(_ghost)
	_ghost.global_position = spr.global_position
	_ghost.visible = false
