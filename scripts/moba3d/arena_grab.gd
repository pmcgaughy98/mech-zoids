extends Node
## Real match-unit hold. Uses the measured donor phase times, never mannequin-only properties.
signal finished(reason: String)
signal caught(target: Node3D)
signal slammed(target: Node3D)
var actor: Node3D
var body: MechModel3D
var target: Node3D
var active:=false
var captured:=false
var impacted:=false
var clock:=0.0
var hold:=0.0
var original_basis:=Basis()
var anchor:=.7
var max_attachment_error:=0.0
var capture_audit: Dictionary={}
var damage:=28.0
var transition_pose: Array[Transform3D]=[]
const GRAB=.18
const IMPACT=.60
func setup(a: Node3D,b: MechModel3D) -> void:actor=a;body=b
func eligible(t: Node3D) -> bool:
	if not is_instance_valid(t) or not MatchTeams.hittable(t) or not t.has_method("toss_to") or t.has_meta("held_by"):return false
	var kit:=t.get_node_or_null("Kit")
	if t.get("busy")==true and (kit==null or not kit.has_method("abort_arena")):return false
	return MatchTeams.team_of(t)!=MatchTeams.team_of(actor) and not (t.has_method("_braced") and t._braced())
func begin(t: Node3D,blend_from_current:=false) -> bool:
	if active or not actor.alive or actor.stunned>0:return false
	transition_pose.clear()
	if blend_from_current:
		for bone in body.skeleton.get_bone_count():transition_pose.append(body.skeleton.get_bone_pose(bone))
	target=t;clock=0;hold=0;captured=false;impacted=false;active=true;max_attachment_error=0;capture_audit={}
	body.start_external("GrabSlam" if eligible(t) else "Fling_Whiff")
	return true
func tick(delta: float) -> void:
	if not active:return
	if not actor.alive or actor.stunned>0 or actor.has_meta("held_by"):
		interrupt("interrupted");return
	if captured and not impacted and (not is_instance_valid(target) or not target.alive):interrupt("target_lost");return
	var remaining:=delta
	for i in 8:
		if remaining<=.000001 or not active:break
		if hold>0:
			var step:=minf(hold,remaining);hold-=step;remaining-=step;continue
		var whiff:=body.action=="Fling_Whiff"
		var next:=GRAB if clock<GRAB-.000001 else IMPACT if not whiff and clock<IMPACT-.000001 else .55 if whiff else 1.0
		var step:=minf(remaining,next-clock);clock+=step;remaining-=step
		body.sample_external("Fling_Whiff" if whiff else "GrabSlam",clock)
		if not transition_pose.is_empty() and clock<.10:
			var weight:=smoothstep(0,.10,clock)
			for bone in transition_pose.size():body.skeleton.set_bone_pose(bone,transition_pose[bone].interpolate_with(body.skeleton.get_bone_pose(bone),weight))
			body.skeleton.force_update_all_bone_transforms()
		if absf(clock-GRAB)<.000001 and not captured and not whiff:
			capture_audit={"eligible":eligible(target),"target":str(target.global_position) if is_instance_valid(target) else "missing","grip":str(body.grip())}
			if eligible(target) and MatchTeams.clear_line(actor,actor.global_position,target.global_position) and not _cage_blocks(actor.global_position,target.global_position):
				anchor=clampf(target.body.top_height()*.5,.35,1.0) if target.get("body") is MechModel3D else .65
				capture_audit["distance"]=(target.global_position+Vector3.UP*anchor).distance_to(body.grip());capture_audit["limit"]=target.radius()+.85
				if (target.global_position+Vector3.UP*anchor).distance_to(body.grip())<=target.radius()+.85:
					if target.has_method("halt"):target.halt()
					original_basis=target.global_basis;target.set_meta("held_by",self);captured=true
					var kit:=target.get_node_or_null("Kit")
					if kit!=null and kit.has_method("abort_arena"):kit.abort_arena()
					if target.get("body") is MechModel3D:target.body.stop_action()
					caught.emit(target)
			if not captured:body.start_external("Fling_Whiff");body.sample_external("Fling_Whiff",clock)
		if captured and not impacted:
			var desired:=body.grip()-Vector3.UP*anchor
			desired.y=maxf(0,desired.y)
			var safe:=ArenaMotion.slide(target,target.global_position,desired-target.global_position,target.radius())
			if Vector2(safe.x-desired.x,safe.z-desired.z).length()>.15 or _cage_blocks(target.global_position,desired):interrupt("blocked");return
			target.global_position=Vector3(safe.x,desired.y,safe.z)
			max_attachment_error=maxf(max_attachment_error,(target.global_position+Vector3.UP*anchor).distance_to(body.grip()))
		if absf(clock-IMPACT)<.000001 and captured and not impacted:
			impacted=true;_drop()
			if target.has_method("take_damage"):target.take_damage(damage,actor)
			else:target.hit(actor)
			if target.has_method("stun"):target.stun(.35)
			if target.get("body") is MechModel3D and target.body.has_clip("Hit_Heavy"):target.body.play_action("Hit_Heavy")
			hold=.065;slammed.emit(target)
		if clock>=(.55 if body.action=="Fling_Whiff" else 1.0)-.000001:_finish("ground_slam" if impacted else "miss")
func _drop() -> void:
	if not captured or not is_instance_valid(target):return
	if not target.has_meta("held_by") or target.get_meta("held_by")!=self:return
	target.remove_meta("held_by")
	target.global_basis=original_basis;target.global_position.y=0
	if "air" in target:target.air=0
func interrupt(reason: String) -> void:
	if active:_drop();_finish(reason)
func _finish(reason: String) -> void:
	active=false;finished.emit(reason)
func _exit_tree() -> void:_drop()
func _cage_blocks(from: Vector3,to: Vector3) -> bool:
	for dome in HexShield.live_domes():
		var a:=MatchTeams.flat(from-dome.global_position)
		var v:=MatchTeams.flat(to-from)
		var aa:=v.length_squared()
		if aa<.000001:continue
		var bb: float=2*a.dot(v);var cc: float=a.length_squared()-dome.radius*dome.radius;var disc: float=bb*bb-4*aa*cc
		if disc<0:continue
		for u in [(-bb-sqrt(disc))/(2*aa),(-bb+sqrt(disc))/(2*aa)]:
			if u>.0001 and u<.9999 and dome.blocks_at(from+v*u):return true
	return false
