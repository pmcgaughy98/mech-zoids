extends Node3D
var hp:=100.0
var alive:=true
var team:="red"
var held:=false
var controls_disabled:=false
var grounded:=false
var damage_calls:=0
var simulation_rate:=1.0
var settle_time:=0.0
var flash:=0.0
var body: Node3D
var material: StandardMaterial3D
var limbs: Dictionary={}
var label: Label3D
func radius() -> float:return .30
func box(parent: Node3D, size: Vector3, pos: Vector3) -> MeshInstance3D:
	var mesh:=MeshInstance3D.new()
	var shape:=BoxMesh.new()
	shape.size=size
	mesh.mesh=shape
	mesh.position=pos
	mesh.material_override=material
	parent.add_child(mesh)
	return mesh
func _ready() -> void:
	material=StandardMaterial3D.new()
	material.albedo_color=Color(.70,.24,.16)
	material.roughness=.65
	body=Node3D.new()
	add_child(body)
	box(body,Vector3(.58,.68,.40),Vector3(0,.72,0))
	box(body,Vector3(.46,.23,.32),Vector3(0,.35,0))
	box(body,Vector3(.32,.32,.32),Vector3(0,1.23,0))
	var visor:=box(body,Vector3(.27,.075,.025),Vector3(0,1.25,-.174))
	var dark:=StandardMaterial3D.new()
	dark.albedo_color=Color(.04,.08,.10)
	visor.material_override=dark
	for side in [-1,1]:
		var arm:=Node3D.new()
		arm.position=Vector3(side*.39,1.00,0)
		body.add_child(arm)
		box(arm,Vector3(.16,.32,.18),Vector3(0,-.16,0))
		var fore:=Node3D.new()
		fore.position.y=-.32
		arm.add_child(fore)
		box(fore,Vector3(.15,.28,.16),Vector3(0,-.14,0))
		box(fore,Vector3(.20,.15,.20),Vector3(0,-.32,0))
		var leg:=Node3D.new()
		leg.position=Vector3(side*.16,.54,0)
		body.add_child(leg)
		box(leg,Vector3(.18,.24,.22),Vector3(0,-.12,0))
		var shin:=Node3D.new()
		shin.position.y=-.24
		leg.add_child(shin)
		box(shin,Vector3(.16,.24,.18),Vector3(0,-.12,0))
		var foot:=Node3D.new()
		foot.position.y=-.24
		shin.add_child(foot)
		box(foot,Vector3(.21,.12,.27),Vector3(0,0,-.04))
		limbs[str(side)]={"arm":arm,"fore":fore,"leg":leg,"shin":shin,"foot":foot}
	label=Label3D.new()
	label.position.y=1.65
	label.font_size=38
	label.pixel_size=.004
	label.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	add_child(label)
func reset(at: Vector3) -> void:
	global_transform=Transform3D(Basis(),at)
	body.transform=Transform3D.IDENTITY
	hp=100
	alive=true
	held=false
	controls_disabled=false
	grounded=false
	damage_calls=0
	settle_time=0
	flash=0
	pose_air(0,0)
func pose_air(t: float, weight: float) -> void:
	for side in [-1,1]:
		var parts: Dictionary=limbs[str(side)]
		parts.arm.rotation=Vector3(.35*sin(t*22+side),0,side*(.18+.45*sin(t*17+side)))*weight
		parts.fore.rotation.x=(.45+.40*sin(t*20+side))*weight
		parts.leg.rotation=Vector3(.5*sin(t*18+side),0,side*.14)*weight
		parts.shin.rotation.x=(-.5-.25*sin(t*24+side))*weight
		parts.foot.rotation=Vector3.ZERO
		if held and absf(global_rotation.x)<.1:
			if global_position.y<=0:
				var bend:=acos(clampf((.48+global_position.y)/.48,.1,1))
				parts.leg.rotation=Vector3(bend,0,0)
				parts.shin.rotation=Vector3(-2*bend,0,0)
				parts.foot.rotation=Vector3(bend,0,0)
			else:
				var lift:=smoothstep(0,.16,global_position.y)
				parts.leg.rotation*=lift
				parts.shin.rotation*=lift
func impact(amount: float) -> void:
	if grounded:return
	damage_calls+=1
	hp=maxf(0,hp-amount)
	alive=hp>0
	held=false
	controls_disabled=false
	grounded=true
	settle_time=0
	flash=.14
	# Torso back is local +Z = 0.20 m. Put that visible surface on the floor.
	var trans:=body.global_transform
	trans.origin.y=maxf(trans.origin.y,.20)
	var torso_center:=trans*Vector3(0,.72,0)
	global_transform=Transform3D(Basis(),Vector3(torso_center.x,0,torso_center.z))
	body.global_transform=trans
func drop_without_damage() -> void:
	held=false
	controls_disabled=false
	grounded=true
	settle_time=0
	var trans:=body.global_transform
	trans.basis=Basis(Vector3.RIGHT,PI/2)
	trans.origin.y=.20
	var center:=trans*Vector3(0,.72,0)
	global_transform=Transform3D(Basis(),Vector3(center.x,0,center.z))
	body.global_transform=trans
func _process(delta: float) -> void:
	delta*=simulation_rate
	flash=maxf(0,flash-delta)
	material.albedo_color=Color(1.6,1.4,.9) if flash>0 else Color(.70,.24,.16)
	label.visible=not held
	label.text="TRAINING ENEMY\n%d / 100" % hp
	if grounded:
		settle_time+=delta
		var decay:=exp(-9*settle_time)
		for side in [-1,1]:
			var parts: Dictionary=limbs[str(side)]
			parts.arm.rotation=Vector3(-.12+.5*sin(settle_time*24+side)*decay,0,side*(.70+.3*sin(settle_time*18)*decay))
			parts.fore.rotation.x=-.15+.6*sin(settle_time*25+side)*decay
			parts.leg.rotation=Vector3(-.25+.25*sin(settle_time*22+side)*decay,0,side*.15)
			parts.shin.rotation.x=-.15+.3*sin(settle_time*26+side)*decay
		_ground_limbs()
		label.position.y=.8
	else:label.position.y=1.65
func chain_min_y(chain: Node3D) -> float:
	var low:=1000.0
	for n in chain.find_children("*","MeshInstance3D",true,false):
		var mesh:=n as MeshInstance3D
		var bounds:=mesh.mesh.get_aabb()
		for i in 8:low=minf(low,(mesh.global_transform*bounds.get_endpoint(i)).y)
	return low
func _ground_limbs() -> void:
	for side in [-1,1]:
		var p: Dictionary=limbs[str(side)]
		for pair in [["arm","fore"],["leg","shin"]]:
			var upper: Node3D=p[pair[0]]
			var lower: Node3D=p[pair[1]]
			if chain_min_y(upper)>=0:continue
			var a:=upper.rotation
			var b:=lower.rotation
			var lo:=0.0
			var hi:=1.0
			for i in 10:
				var mid: float=(lo+hi)/2
				upper.rotation=a*mid
				lower.rotation=b*mid
				if chain_min_y(upper)<0:hi=mid
				else:lo=mid
			upper.rotation=a*lo
			lower.rotation=b*lo
func visible_min_y() -> float:
	return chain_min_y(body)

