class_name SmallGate
extends Node3D
## The fennec's small gate (Claude, 2026-11-05, game feel lane, effects spin-off). One gate for the 2026-11-05 kit's
## abilities 1 (the gate the backward bolt fires from), 2 (pocket gates) and 3 (far gates): it opens, holds and closes,
## then frees itself. It knows nothing of who may use it; the kit decides that.
## Art: tools/art/draw_fennec_gate.py (art/fx/moba3d/small_gate/), in the fennec's colours at its texel (0.016 m).
## The doorway stands on a tilted quad like the machines (tilted_fx_3d.gdshader), so it faces the camera from every side
## and reads from behind the fennec too; its swirl is part see-through. The ring lies flat on the floor under it.
## Every length here is a placeholder, not a balance number.

signal opened ## fully open: a bolt or a traveller can use it from now
signal closing ## the close has started

const DIR := "res://art/fx/moba3d/small_gate/"
const SHADER := preload("res://scripts/moba3d/tilted_fx_3d.gdshader")
const PX := 0.016 ## the fennec's texel (size class S)
const W := 64
const H := 100
const FEET_EDGE := 96 ## the floor is the top edge of door row 96
const MID_UP := 0.7 ## metres from the floor to the middle of the doorway (row 52), where a bolt comes out
const FLOOR_W := 88
const OPEN_MS: Array[int] = [60, 60, 60, 60, 80, 80] ## frames 0-5: posts rise, a line of light, the oval swings open
const HOLD_MS: Array[int] = [100, 100, 100, 100, 100, 100] ## frames 6-11, looped while it holds
const CLOSE_MS: Array[int] = [60, 60, 60, 60, 80, 80] ## frames 12-17: narrows to a line, pinches to a star, sinks
const FRAME_COUNT := 18

static var _door_tex: Array[Texture2D] = []
static var _floor_tex: Array[Texture2D] = []

var hold_time := 0.8 ## seconds it holds once open; negative holds until close() is called
var phase := "open" ## "open", "hold" or "close" (the checks read it)
var frame := -1 ## the frame showing, 0-17
var _t := 0.0 ## seconds into the current phase
var _held := 0.0 ## seconds held so far
var _door_mat: ShaderMaterial
var _floor_mat: StandardMaterial3D


## A gate standing on the floor at pos. hold: seconds it stays open; negative waits for close().
static func open_at(parent: Node, pos: Vector3, hold := 0.8) -> SmallGate:
	var g := SmallGate.new()
	g.hold_time = hold
	parent.add_child(g)
	g.global_position = pos
	return g


static func _load() -> void:
	if not _door_tex.is_empty():
		return
	for i in FRAME_COUNT:
		_door_tex.append(tex_or_disk(DIR + "door_f%02d.png" % i))
		_floor_tex.append(tex_or_disk(DIR + "floor_f%02d.png" % i))


## The imported texture; before the editor has imported a newly drawn frame, the PNG read straight from disk.
static func tex_or_disk(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path)
	return ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path(path)))


func _ready() -> void:
	_load()
	var door := MeshInstance3D.new()
	door.name = "Door"
	var q := QuadMesh.new()
	q.size = Vector2(W, H) * PX
	door.mesh = q
	_door_mat = ShaderMaterial.new()
	_door_mat.shader = SHADER
	var lift := (FEET_EDGE - H / 2.0) * PX
	_door_mat.set_shader_parameter("lift", lift)
	door.material_override = _door_mat
	door.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	door.position = Vector3(0.0, lift, 0.0)
	add_child(door)
	var fl := MeshInstance3D.new()
	fl.name = "Floor"
	var pm := PlaneMesh.new()
	pm.size = Vector2.ONE * FLOOR_W * PX
	_floor_mat = StandardMaterial3D.new()
	_floor_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_floor_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_floor_mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	pm.material = _floor_mat
	fl.mesh = pm
	fl.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	fl.position = Vector3(0.0, 0.03, 0.0)
	add_child(fl)
	_show(0)


## Starts the close now (the recast, the window running out). Does nothing once closing.
func close() -> void:
	if phase == "close":
		return
	phase = "close"
	_t = 0.0
	closing.emit()


func _process(delta: float) -> void:
	_t += delta
	match phase:
		"open":
			var i := _index(OPEN_MS, _t)
			if i < 0:
				_t -= _total(OPEN_MS)
				phase = "hold"
				opened.emit()
			else:
				_show(i)
		"close":
			var i := _index(CLOSE_MS, _t)
			if i < 0:
				queue_free()
			else:
				_show(12 + i)
	if phase == "hold":
		_held += delta
		if hold_time >= 0.0 and _held >= hold_time:
			close()
			_show(12)
		else:
			_show(6 + _index(HOLD_MS, fmod(_t, _total(HOLD_MS))))


func _show(i: int) -> void:
	if i == frame:
		return
	frame = i
	_door_mat.set_shader_parameter("tex", _door_tex[i])
	_floor_mat.albedo_texture = _floor_tex[i]


static func _total(ms: Array[int]) -> float:
	var s := 0
	for m in ms:
		s += m
	return s / 1000.0


## The frame t seconds into a run of frames, or -1 once past its end.
static func _index(ms: Array[int], t: float) -> int:
	var s := 0.0
	for i in ms.size():
		s += ms[i] / 1000.0
		if t < s:
			return i
	return -1
