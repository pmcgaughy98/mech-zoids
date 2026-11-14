extends "res://scripts/moba3d/mech_model_3d.gd"
## Static source fallback. Cosmetic root lean/hover only; never invents a skeletal gait.
const ROSTER=preload("res://scripts/moba3d/arena_roster.gd")
var visual: Node3D
var ground_speed:=0.0
var phase:=0.0
var hover:=0.0
func configure(k: String) -> bool:
	kind=k
	var row: Dictionary=ROSTER.profile(k)
	var tpl:=_template(row.glb)
	if tpl==null:return false
	_model=Node3D.new();_model.name="Model";add_child(_model)
	visual=tpl.duplicate();_model.add_child(visual)
	var box:=ROSTER.bounds(visual)
	var fit:=minf(float(row.height_cap)/maxf(box.size.y,.01),float(row.span_cap)/maxf(maxf(box.size.x,box.size.z),.01))
	visual.scale=Vector3.ONE*fit
	visual.position=-Vector3(box.get_center().x,box.position.y,box.get_center().z)*fit
	visual.rotation.y=float(row.get("forward_yaw",0))
	hover=float(row.hover)
	_model.position.y=hover
	_rest=box.size.y*fit+hover
	_row={"scale":1.0,"turn_rate":12.0}
	set_meta("readiness","base_proxy")
	return true
func locomote(speed: float, _move := Vector3.ZERO) -> void:ground_speed=speed # second argument matches MechModel3D.locomote (gorilla lane, 2026-11-10)
func _process(delta: float) -> void:
	super._process(delta)
	phase+=delta*(2.0+ground_speed)
	_model.position.y=hover+(sin(phase*2.0)*.035 if hover>0 else 0.0)
	_model.rotation.z=lerpf(_model.rotation.z,sin(phase)*.018*minf(ground_speed,1.0),1-exp(-8*delta))
