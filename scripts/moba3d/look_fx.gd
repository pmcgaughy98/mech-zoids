extends Node3D
## Loaded by path (preload), not by class_name: a new global class needs an editor rescan first.
## Smooth stand-ins for the shared pixel effects (look lane, 2026-11-11). Preston: "we don't want it too look like pixel
## art". Fx3D.spawn keeps its AnimatedSprite3D as an invisible carrier (same lifetime, position, scale, loop and return
## type for every caller) and parents one of these to it, so no kit code changes.
## hit_spark: warm white core and amber rays. deflect_spark: cyan-white, the shield's colour. stun_loop: three gold
## stars circling. No red anywhere: red marks enemies (mech_look rim and outline).

const SMOOTH := ["hit_spark", "deflect_spark", "stun_loop"]
static var off := false  ## true = the old pixel flipbooks (before/after tests only)
const SPARK := preload("res://shaders/look/fx_spark.gdshader")
const STAR := preload("res://shaders/look/fx_star.gdshader")

var kind := ""
var life := 0.3
var _t := 0.0
var _mats: Array[ShaderMaterial] = []
var _stars: Array[MeshInstance3D] = []


static func make(anim: String, duration: float) -> Node3D:
	var f = load("res://scripts/moba3d/look_fx.gd").new()
	f.kind = anim
	f.life = maxf(duration, 0.18)
	return f


func _ready() -> void:
	if kind == "stun_loop":
		for i in 3:
			var star_mi := _quad(STAR, 0.26)
			_mats[i].set_shader_parameter("spin", i * 1.3)
			_stars.append(star_mi)
	else:
		var m := _quad(SPARK, 1.1 if kind == "hit_spark" else 1.25)
		_mats[0].set_shader_parameter("seed", randf())
		if kind == "deflect_spark":
			_mats[0].set_shader_parameter("core_col", Color(0.8, 0.97, 1.0))
			_mats[0].set_shader_parameter("rim_col", Color(0.35, 0.78, 1.0))
			_mats[0].set_shader_parameter("rays", 9.0)
		m.rotation.z = randf() * TAU
	_process(0.0)


func _quad(sh: Shader, size_m: float) -> MeshInstance3D:
	var mat := ShaderMaterial.new()
	mat.shader = sh
	var q := QuadMesh.new()
	q.size = Vector2(size_m, size_m)
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	_mats.append(mat)
	return mi


func _process(delta: float) -> void:
	_t += delta
	if kind == "stun_loop":
		for i in _stars.size():
			var a := _t * TAU / 1.1 + i * TAU / 3.0
			_stars[i].position = Vector3(cos(a) * 0.34, 0.06 * sin(_t * 5.0 + i), sin(a) * 0.34)
			_mats[i].set_shader_parameter("spin", _t * 2.5 + i)
	else:
		_mats[0].set_shader_parameter("age", clampf(_t / life, 0.0, 1.0))
