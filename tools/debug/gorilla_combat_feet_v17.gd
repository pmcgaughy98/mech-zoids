extends SkeletonModifier3D
## Moving combat layer. Hands/torso remain owned by the authored attack animation.
var driver: Node3D
var model: Node3D
var chains = []
var states = {}
var phase = .26
var strafe_mix = 0.0
var previous_speed = 0.0
var foot_log: FileAccess

func setup(d: Node3D, m: Node3D, output: String) -> void:
	driver = d
	model = m
	var sk = get_skeleton()
	for item in [["RightUpLeg","RightLeg","RightFoot",0.0,-1.0],["LeftUpLeg","LeftLeg","LeftFoot",.5,1.0]]:
		var upper = sk.find_bone(item[0])
		var lower = sk.find_bone(item[1])
		var end = sk.find_bone(item[2])
		var a = sk.global_transform*sk.get_bone_global_pose(upper)
		var e = sk.global_transform*sk.get_bone_global_pose(lower)
		var w = sk.global_transform*sk.get_bone_global_pose(end)
		var local = model.global_transform.affine_inverse()*w
		chains.append({"upper":upper,"lower":lower,"end":end,"name":item[2],"offset":item[3],"sign":item[4],"l1":a.origin.distance_to(e.origin),"l2":e.origin.distance_to(w.origin),"ready":local})
	foot_log = FileAccess.open(output+"/combat-feet.csv",FileAccess.WRITE)
	foot_log.store_line("time,bone,speed,phase,stance,anchor_error,reach_clamp,height,weight,x,z")

func _process_modification_with_delta(delta: float) -> void:
	if not driver or not driver.started: return
	var weight: float = driver.combat_weight
	if weight<.001:
		states.clear()
		phase = .26
		previous_speed = 0.0
		return
	var sk = get_skeleton()
	var world = sk.global_transform
	var inverse = world.affine_inverse()
	var velocity: Vector3 = driver.actual_velocity
	velocity.y = 0
	var speed = velocity.length()
	var moving = speed>.08
	var local_dir = model.global_basis.inverse()*velocity.normalized() if moving else Vector3.ZERO
	strafe_mix = lerpf(strafe_mix,absf(local_dir.x) if moving else 0.0,1.0-exp(-12.0*delta))
	var base_period = lerpf(.40,.35,strafe_mix)
	var cadence = maxf(.35,pow(maxf(speed/3.5,.001),.6))
	var period = base_period/cadence
	var duty = lerpf(.52,.40,strafe_mix)
	if moving: phase=fposmod(phase+delta/period,1.0)
	var before = {}
	for c in chains: before[c["name"]] = world*sk.get_bone_global_pose(c["end"])
	var hips = sk.find_bone("Hips")
	var hip_pose = world*sk.get_bone_global_pose(hips)
	var bob = -.010*(1.0-cos(TAU*2.0*phase))*.5 if moving else 0.0
	var offset = Vector3(-.012*sin(TAU*phase) if moving else 0.0,bob-.06*strafe_mix,-.10*strafe_mix)*weight
	hip_pose.origin += model.global_basis*offset
	sk.set_bone_global_pose(hips,inverse*hip_pose)
	for c in chains:
		var name: String = c["name"]
		var current: Transform3D = before[name]
		var p = fposmod(phase+float(c["offset"]),1.0)
		var center: Vector3 = c["ready"].origin
		center.x=lerpf(center.x,.35 if c["sign"]>0 else -.3412,strafe_mix)
		center.z=lerpf(center.z,-.36 if c["sign"]>0 else -.84,strafe_mix)
		var desired_center = model.global_transform*center
		var desired_basis = model.global_basis*c["ready"].basis
		if not states.has(name):
			states[name]={"anchor":current,"swing":false,"last_phase":p,"settle":0.0}
		var st: Dictionary = states[name]
		var stance = p<duty
		if moving:
			if stance and (p<float(st["last_phase"]) or float(st["last_phase"])>=duty) and st["swing"] and float(st["age"])>=float(st["duration"])*.90:
				st["anchor"] = Transform3D(st["end_basis"],st["end"])
				st["swing"] = false
			if not stance and not st["swing"]:
				_begin_swing(st,st["anchor"].origin,desired_center+velocity*(period*(1.0-p)+period*duty*.5),desired_basis,maxf(.045,period*(1.0-p)))
				st["phase_start"]=(p-duty)/(1.0-duty)
			st["last_phase"] = p
		else:
			var dist: float = st["anchor"].origin.distance_to(desired_center)
			if not st["swing"] and dist>.06:
				var other_moving = false
				for key in states:
					if key!=name and states[key]["swing"]: other_moving=true
				if not other_moving: _begin_swing(st,st["anchor"].origin,desired_center,desired_basis,.17)
		var target: Vector3 = st["anchor"].origin
		var end_basis: Basis = st["anchor"].basis
		var locked = not bool(st["swing"])
		if st["swing"]:
			st["age"] += delta
			var u = clampf(float(st["age"])/float(st["duration"]),0,1)
			if moving and u<.78:
				var remaining=maxf(0.0,float(st["duration"])-float(st["age"]))
				var planned=desired_center+velocity*(remaining+period*duty*.5)
				var hip_now: Transform3D=world*sk.get_bone_global_pose(c["upper"])
				planned=_reachable(hip_now.origin+velocity*remaining,planned,(c["l1"]+c["l2"])*.975)
				st["end"]=st["end"].lerp(planned,1.0-exp(-30.0*delta))
			var s = _smooth(u)
			target = st["start"].lerp(st["end"],s)+Vector3.UP*(.10 if moving else .055)*pow(sin(PI*u),2)
			end_basis=Basis(st["start_basis"].get_rotation_quaternion().slerp(st["end_basis"].get_rotation_quaternion(),s))
			if u>=1:
				st["anchor"]=Transform3D(st["end_basis"],st["end"])
				locked=true
				if stance or not moving: st["swing"]=false
		# Release an exhausted plant into a short corrective step, never stretch a leg.
		var a_pose: Transform3D = world*sk.get_bone_global_pose(c["upper"])
		var max_reach: float = (c["l1"]+c["l2"])*.985
		if locked and a_pose.origin.distance_to(target)>max_reach:
			var start: Vector3=st["solved"].origin if st.has("solved") else target
			start=_reachable(a_pose.origin,start,max_reach-.005)
			_begin_swing(st,start,desired_center+velocity*.075,desired_basis,.12)
			target=start+Vector3.UP*.015
			locked=false
		if not locked:target=_reachable(a_pose.origin,target,(c["l1"]+c["l2"])*.985)
		var blend_target = current.origin.lerp(target,weight)
		var blend_basis = Basis(current.basis.get_rotation_quaternion().slerp(end_basis.get_rotation_quaternion(),weight))
		var error = _solve(sk,world,inverse,c,blend_target,blend_basis)
		var solved: Transform3D = world*sk.get_bone_global_pose(c["end"])
		st["solved"]=solved
		if foot_log:
			foot_log.store_line("%.5f,%s,%.4f,%.4f,%s,%.7f,%.7f,%.5f,%.4f,%.6f,%.6f" % [driver.elapsed,name,speed,p,str(locked and weight>.99),solved.origin.distance_to(st["anchor"].origin) if locked else 0.0,error,solved.origin.y,weight,solved.origin.x,solved.origin.z])
	previous_speed=speed
	if foot_log: foot_log.flush()

func _begin_swing(st: Dictionary, start: Vector3, end: Vector3, basis: Basis, duration: float) -> void:
	st["swing"]=true
	st["start"]=start
	st["end"]=end
	st["start_basis"]=st["anchor"].basis
	st["end_basis"]=basis
	st["age"]=0.0
	st["duration"]=duration

func _smooth(x: float) -> float: return x*x*x*(10.0+x*(-15.0+6.0*x))

func _reachable(hip: Vector3, target: Vector3, reach: float) -> Vector3:
	var v=target-hip
	var horizontal=Vector3(v.x,0,v.z)
	var allowed=sqrt(maxf(.0001,reach*reach-v.y*v.y))
	if horizontal.length()>allowed:
		horizontal=horizontal.normalized()*allowed
		target.x=hip.x+horizontal.x
		target.z=hip.z+horizontal.z
	return target

func _solve(sk: Skeleton3D, world: Transform3D, inverse: Transform3D, c: Dictionary, target: Vector3, basis: Basis) -> float:
	var a: Transform3D=world*sk.get_bone_global_pose(c["upper"])
	var e: Transform3D=world*sk.get_bone_global_pose(c["lower"])
	var w: Transform3D=world*sk.get_bone_global_pose(c["end"])
	var l1: float=c["l1"]
	var l2: float=c["l2"]
	var v=target-a.origin
	var distance=v.length()
	var d=clampf(distance,absf(l1-l2)+.0001,l1+l2-.0001)
	var axis=v.normalized()
	var pole=model.global_basis*Vector3(float(c["sign"])*.6,0,.8)
	var bend=(pole-axis*pole.dot(axis)).normalized()
	var along=(l1*l1-l2*l2+d*d)/(2*d)
	var knee=a.origin+axis*along+bend*sqrt(maxf(0,l1*l1-along*along))
	var q=Quaternion((e.origin-a.origin).normalized(),(knee-a.origin).normalized())
	sk.set_bone_global_pose(c["upper"],inverse*Transform3D(Basis(q)*a.basis,a.origin))
	e=world*sk.get_bone_global_pose(c["lower"])
	w=world*sk.get_bone_global_pose(c["end"])
	q=Quaternion((w.origin-e.origin).normalized(),(a.origin+axis*d-e.origin).normalized())
	sk.set_bone_global_pose(c["lower"],inverse*Transform3D(Basis(q)*e.basis,e.origin))
	w=world*sk.get_bone_global_pose(c["end"])
	sk.set_bone_global_pose(c["end"],inverse*Transform3D(basis,w.origin))
	return absf(distance-d)
