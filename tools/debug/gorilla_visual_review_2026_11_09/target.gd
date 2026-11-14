extends "victim_base.gd"
signal hurt(amount: float, by: Node3D)
var visual_fx:=true
var kind:="machine"
var bot:=true
var slowed:=0.0
var cage: Node3D
var shove_left:=0.0
var shove_motion:=Vector3.ZERO
func _ready() -> void:
	super._ready()
	add_to_group("kit_target")
	add_to_group("match_unit")
	var proxy:=Node.new()
	proxy.set_script(load("res://tools/debug/gorilla_visual_review_2026_11_09/target_proxy.gd"))
	proxy.name="Kit"
	add_child(proxy)
func take_damage(amount: float, by: Node3D=null) -> void:
	if not alive:return
	hp=maxf(0,hp-amount)
	damage_calls+=1
	flash=.12
	hurt.emit(amount,by)
	if hp<=0:alive=false
func drive_shove(motion: Vector3, pause: float) -> void:
	shove_motion=motion
	shove_left=pause+.16
func shove(_motion: Vector3, _back:=.12) -> void:pass
func taunt(_source: Node3D, _seconds: float) -> void:pass
func trap(dome: Node3D) -> void:cage=dome
func heal(amount: float) -> void:hp=minf(100,hp+amount)
func _process(delta: float) -> void:
	super._process(delta)
	if not visual_fx:material.albedo_color=Color(.70,.24,.16)
	if shove_left>0:
		shove_left=maxf(0,shove_left-delta)
		if shove_left<.16 and not held:
			global_position=ArenaMotion.slide(self,global_position,shove_motion*minf(delta/.16,1),radius())

