extends SkeletonModifier3D
## Post-animation contact correction; does not change limb length or source geometry.
var driver: Node3D
var animation_player: AnimationPlayer
var chains := []
var anchors := {}
var previous_phase := {}
var log_file: FileAccess
var last_pose := {}

func setup(owner_node: Node3D, ap: AnimationPlayer, output: String) -> void:
	driver = owner_node
	animation_player = ap
	var sk := get_skeleton()
	for item in [["RightArm","RightForeArm","RightHand",0.0],["LeftArm","LeftForeArm","LeftHand",.03],["RightUpLeg","RightLeg","RightFoot",.5],["LeftUpLeg","LeftLeg","LeftFoot",.53]]:
		chains.append({"upper":sk.find_bone(item[0]),"lower":sk.find_bone(item[1]),"end":sk.find_bone(item[2]),"name":item[2],"offset":item[3],"duty":.38 if str(item[2]).ends_with("Hand") else .20})
	log_file = FileAccess.open(output + "/turn-contacts.csv",FileAccess.WRITE)
	log_file.store_line("time,bone,phase,locked,releasing,anchor_error_m,reach_clamp_m,x,y,z")

func _process_modification_with_delta(delta: float) -> void:
	if not driver or not animation_player or not driver.started:
		return
	var sk := get_skeleton()
	if not animation_player.is_playing():
		return
	var world := sk.global_transform
	var inverse := world.affine_inverse()
	for chain in chains:
		var name: String = chain["name"]
		var phase: float = fposmod(animation_player.current_animation_position / .6 + float(chain["offset"]),1.0)
		var support: bool = phase < float(chain["duty"])
		var upper: int = chain["upper"]
		var lower: int = chain["lower"]
		var end: int = chain["end"]
		var a_pose: Transform3D = world * sk.get_bone_global_pose(upper)
		var e_pose: Transform3D = world * sk.get_bone_global_pose(lower)
		var w_pose: Transform3D = world * sk.get_bone_global_pose(end)
		var new_contact: bool = support and (not anchors.has(name) or phase < float(previous_phase.get(name,1.0)))
		if new_contact:
			anchors[name] = {"transform":w_pose,"release":-1.0}
		previous_phase[name] = phase
		if not anchors.has(name):
			continue
		var anchor: Dictionary = anchors[name]
		var locked_pose: Transform3D = anchor["transform"]
		var l1 := a_pose.origin.distance_to(e_pose.origin)
		var l2 := e_pose.origin.distance_to(w_pose.origin)
		var raw_distance := a_pose.origin.distance_to(locked_pose.origin)
		if float(anchor["release"]) < 0.0 and (not support or raw_distance > (l1+l2)*.985 or raw_distance < absf(l1-l2)+.015):
			anchor["release"] = 0.0
		var blend := 0.0
		var releasing: bool = float(anchor["release"]) >= 0.0
		if releasing:
			anchor["release"] = float(anchor["release"]) + delta
			blend = smoothstep(0.0,.085,float(anchor["release"]))
			if blend >= .999:
				anchors.erase(name)
				continue
		var target := locked_pose.origin.lerp(w_pose.origin,blend)
		if releasing and support:
			target.y += .045*sin(PI*blend)
		var end_basis := Basis(locked_pose.basis.get_rotation_quaternion().slerp(w_pose.basis.get_rotation_quaternion(),blend))
		var v := target-a_pose.origin
		var dist := v.length()
		var solved_distance := clampf(dist,absf(l1-l2)+.0001,l1+l2-.0001)
		var clamp_amount := absf(solved_distance-dist)
		var axis := v.normalized()
		var bend := e_pose.origin-a_pose.origin
		bend -= axis*bend.dot(axis)
		if bend.length_squared()<.00001:
			bend = world.basis.x-axis*world.basis.x.dot(axis)
		bend = bend.normalized()
		var along := (l1*l1-l2*l2+solved_distance*solved_distance)/(2.0*solved_distance)
		var elbow := a_pose.origin+axis*along+bend*sqrt(maxf(0.0,l1*l1-along*along))
		var upper_q := Quaternion((e_pose.origin-a_pose.origin).normalized(),(elbow-a_pose.origin).normalized())
		var new_upper := Transform3D(Basis(upper_q)*a_pose.basis,a_pose.origin)
		sk.set_bone_global_pose(upper,inverse*new_upper)
		var current_e: Transform3D = world*sk.get_bone_global_pose(lower)
		var current_w: Transform3D = world*sk.get_bone_global_pose(end)
		var desired_end := a_pose.origin+axis*solved_distance
		var lower_q := Quaternion((current_w.origin-current_e.origin).normalized(),(desired_end-current_e.origin).normalized())
		sk.set_bone_global_pose(lower,inverse*Transform3D(Basis(lower_q)*current_e.basis,current_e.origin))
		current_w = world*sk.get_bone_global_pose(end)
		sk.set_bone_global_pose(end,inverse*Transform3D(end_basis,current_w.origin))
		var result: Transform3D = world*sk.get_bone_global_pose(end)
		if log_file:
			log_file.store_line("%.5f,%s,%.5f,%s,%s,%.7f,%.7f,%.6f,%.6f,%.6f" % [driver.elapsed,name,phase,str(support and not releasing),str(releasing),result.origin.distance_to(locked_pose.origin),clamp_amount,result.origin.x,result.origin.y,result.origin.z])
	if log_file:
		log_file.flush()

