extends Node3D
## Two hand-following energy faces. Visual only; the existing Drive controller owns contact and damage.
var body: MechModel3D
var actor: Node3D
var phase:="idle"
var elapsed:=0.0
var panels: Array=[]
var offsets: Array[Vector3]=[]
var bones: Array[int]=[]
var materials: Array=[]
func setup(a: Node3D,b: MechModel3D) -> void:
	actor=a;body=b;process_priority=20
	for side in ["Left","Right"]:
		var bone:=body.skeleton.find_bone(side+"Hand")
		bones.append(bone)
		var center:=Vector3.ZERO
		var count:=0
		for mesh in body.model_root().find_children("*","MeshInstance3D",true,false):
			if mesh.mesh!=null and mesh.name.begins_with("Shield_"+side.left(1)+"_Cell"):
				center+=body.skeleton.to_local(mesh.to_global(mesh.mesh.get_aabb().get_center()));count+=1
		offsets.append(body.skeleton.get_bone_global_rest(bone).affine_inverse()*(center/count) if count>0 else Vector3.ZERO)
		var panel:=Node3D.new();panel.name=side+"BashShield";add_child(panel);panels.append(panel)
		piece(panel,.55,.028,Color(.55,1,.12,.95))
		piece(panel,.59,.009,Color(.8,1,.35,.60))
		piece(panel,.53,0,Color(.20,.85,.07,.12))
		for i in 7:
			var cell:=piece(panel,.135,.008,Color(.5,1,.15,.38))
			if i>0:cell.position=Vector3(cos(TAU*(i-1)/6),0,sin(TAU*(i-1)/6))*.245
	visible=false
func piece(parent: Node3D,radius: float,width: float,color: Color) -> MeshInstance3D:
	var mesh:=ImmediateMesh.new();mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in 6:
		var a:=Vector3(cos(TAU*i/6+PI/6),0,sin(TAU*i/6+PI/6))
		var b:=Vector3(cos(TAU*(i+1)/6+PI/6),0,sin(TAU*(i+1)/6+PI/6))
		var vertices: Array=[Vector3.ZERO,a*radius,b*radius] if width==0 else [a*radius,b*radius,a*(radius-width),b*radius,b*(radius-width),a*(radius-width)]
		for v in vertices:mesh.surface_add_vertex(v)
	mesh.surface_end()
	var mat:=StandardMaterial3D.new();mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;mat.cull_mode=BaseMaterial3D.CULL_DISABLED;mat.albedo_color=color
	materials.append([mat,color])
	var node:=MeshInstance3D.new();node.mesh=mesh;node.material_override=mat;node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF;parent.add_child(node);return node
func set_phase(value: String) -> void:
	phase=value;elapsed=0;visible=phase!="idle"
	if visible:update_faces()
func update_faces() -> void:
	if not is_instance_valid(body) or not is_instance_valid(actor):visible=false;return
	var facing:=MatchTeams.flat(actor.facing).normalized()
	if facing.length_squared()<.1:facing=Vector3.FORWARD
	for i in panels.size():
		panels[i].global_position=body.skeleton.global_transform*(body.skeleton.get_bone_global_pose(bones[i])*offsets[i])+facing*.13
		panels[i].global_basis=Basis(Quaternion(Vector3.UP,facing))
	var strength:=1.0
	var size:=1.0
	if phase=="brace":
		strength=clampf(elapsed/.12,0,1);size=lerpf(.65,1.0,strength)
	elif phase=="hit":
		strength=1.0-smoothstep(.055,.25,elapsed);size=1.0+.14*smoothstep(0,.09,elapsed)
	elif phase=="brake":strength=1.0-smoothstep(0,.20,elapsed)
	for panel in panels:panel.scale=Vector3.ONE*size
	for row in materials:
		var color: Color=row[1];color.a*=strength;row[0].albedo_color=color
func _process(delta: float) -> void:
	if not visible:return
	elapsed+=delta
	update_faces()
