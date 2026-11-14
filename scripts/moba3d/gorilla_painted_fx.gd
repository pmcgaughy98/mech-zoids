extends Node3D
## One generated atlas, layered in world space. Visual only; kit signals own the timing.
const IMAGE="res://art/fx/gorilla/reactor-atlas-v1.png"
const SHADER=preload("res://shaders/gorilla_painted_fx.gdshader")
var texture: Texture2D
var kit: ApeKit
var actor: Node3D
var selection: Node3D
var decals: Array=[]
var live: Array=[]
var seal: MeshInstance3D
var direction_crest: MeshInstance3D
var selected: MeshInstance3D
var drive_wake: MeshInstance3D
var elapsed:=0.0
var release_count:=0
var ult_beats:=0
func setup(k: ApeKit,p: Node3D) -> void:
	kit=k;actor=p;texture=load(IMAGE)
	seal=piece(0);selected=piece(1);direction_crest=piece(2);drive_wake=piece(6)
	kit.shield_applied.connect(shield_release)
	kit.used.connect(func(slot):
		if slot=="4":ult_beats=0
	)
	kit.contact.connect(func(target,strong):
		if strong and is_instance_valid(target):burst(target.global_position,1,Vector2(2.7,2.7),.6,.65)
	)
func bind_actions() -> void:
	if is_instance_valid(kit.grab):kit.grab.slammed.connect(func(target):burst(target.global_position,1,Vector2(3.0,3.0),.65,.8);burst(target.global_position,5,Vector2(2.1,2.1),.25,.85))
	if is_instance_valid(kit.drive):kit.drive.collision.connect(func(target,_damage):burst(target.global_position,5,Vector2(2.2,2.2),.3,.8))
	if is_instance_valid(kit.visual_body):kit.visual_body.event.connect(func(clip,event,_damage):
		if clip=="Ult" and event=="beat":
			ult_beats+=1
			burst(actor.global_position,3,Vector2.ONE*kit.ult_radius*2.17,.55,.38)
			if ult_beats==3:
				for i in kit.ult_panels:
					var angle:=TAU*i/kit.ult_panels;var outward:=Vector3(sin(angle),0,cos(angle))
					face_burst(actor.global_position+outward*kit.ult_radius+Vector3.UP*.65,7,Vector2(1.3,1.3),.6,.65,-outward)
	)
func piece(index: int) -> MeshInstance3D:
	var node:=MeshInstance3D.new();var plane:=PlaneMesh.new();plane.size=Vector2.ONE;node.mesh=plane
	var material:=ShaderMaterial.new();material.shader=SHADER;material.set_shader_parameter("atlas",texture)
	material.set_shader_parameter("cell",Vector2(index%4,index/4));node.material_override=material
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node);node.top_level=true;node.global_transform=Transform3D.IDENTITY;node.visible=false
	decals.append(node);return node
func place(node: MeshInstance3D,at: Vector3,size: Vector2,opacity: float,yaw:=0.0) -> void:
	node.visible=opacity>.001;node.global_position=at+Vector3.UP*.065;node.rotation=Vector3(0,yaw,0);node.scale=Vector3(size.x,1,size.y)
	node.material_override.set_shader_parameter("opacity",opacity)
func burst(at: Vector3,index: int,size: Vector2,life: float,opacity: float) -> void:
	var node:=piece(index);place(node,at,size,opacity)
	live.append({"node":node,"at":at,"size":size,"time":0.0,"life":life,"alpha":opacity,"spin":.12 if index==0 else 0.0})
func shield_release(target: Node3D) -> void:
	release_count+=1;burst(target.global_position,0,Vector2(3,3),.8,.8)
	burst(target.global_position,5,Vector2(1.8,1.8),.25,.32)
	var toward:=MatchTeams.flat(actor.global_position-target.global_position).normalized()
	if toward.length_squared()<.01:toward=-actor.facing
	face_burst(target.global_position+Vector3.UP,0,Vector2(2.5,2.5),.7,.55,toward,target)
func face_burst(at: Vector3,index: int,size: Vector2,life: float,opacity: float,normal: Vector3,follow: Node3D=null) -> void:
	var node:=piece(index);node.visible=true
	live.append({"node":node,"at":at,"size":size,"time":0.0,"life":life,"alpha":opacity,"spin":0.0,"normal":normal,"follow":follow})
func _process(delta: float) -> void:
	if actor==null:return
	elapsed+=delta
	for node in [seal,selected,direction_crest,drive_wake]:node.visible=false
	selection=kit.targeting
	if is_instance_valid(selection) and selection.slot!="":
		var target: Node3D=selection.hovered
		match selection.slot:
			"1":
				if is_instance_valid(target):
					place(seal,target.global_position,Vector2(3,3),.44 if selection.valid else .23,elapsed*.06)
					seal.material_override.set_shader_parameter("tint",Color.WHITE if selection.valid else Color(1,.32,.2))
			"2":
				place(selected,kit.fault.endpoint(selection.aim()),Vector2(3.0,3.0),.35)
			"3":
				var d: Vector3=selection.direction();var travel:=5.09904
				place(direction_crest,actor.global_position+d*(travel*.5),Vector2(2.1,travel),.55,atan2(-d.x,-d.z))
			"4":
				seal.material_override.set_shader_parameter("cell",Vector2(3,0))
				seal.material_override.set_shader_parameter("tint",Color.WHITE)
				place(seal,actor.global_position,Vector2.ONE*kit.ult_radius*2.17,.32)
	if is_instance_valid(selection) and selection.slot!="4":seal.material_override.set_shader_parameter("cell",Vector2(0,0))
	if is_instance_valid(kit.drive) and kit.drive.phase=="drive":
		var d: Vector3=kit.drive.direction
		place(drive_wake,actor.global_position-d*.8,Vector2(1.8,3.4),.42,atan2(-d.x,-d.z))
	for row in live.duplicate():
		row.time+=delta
		if row.time>=row.life:
			row.node.queue_free();decals.erase(row.node);live.erase(row);continue
		var progress: float=row.time/row.life
		var size: Vector2=row.size*(.86+.2*progress)
		var alpha: float=row.alpha*(1-smoothstep(.20,1,progress))
		if row.has("normal"):
			var at: Vector3=row.follow.global_position+Vector3.UP if is_instance_valid(row.follow) else row.at
			place(row.node,at,size,alpha)
			row.node.global_basis=Basis(Quaternion(Vector3.UP,row.normal))*Basis(Vector3.UP,progress*.24)
			row.node.scale=Vector3(size.x,1,size.y)
		else:place(row.node,row.at,size,alpha,row.spin*progress)
func icon(index: int) -> AtlasTexture:
	var region:=AtlasTexture.new();region.atlas=texture
	var size:=Vector2(texture.get_width()/4.0,texture.get_height()/2.0)
	region.region=Rect2(Vector2(index%4,index/4)*size,size);return region
