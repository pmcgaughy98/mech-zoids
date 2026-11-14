extends Node3D
var enabled:=true
var log_rows: Array=[]
var cell_materials: Array=[]
var cell_weight:=0.0
var pulse_left:=0.0
var transient: Array=[]
var persistent: Array=[]
const LIME=Color(.62,1.0,.16)
const STEEL=Color(.75,.81,.72)
func setup(model: Node3D) -> void:
	for n in model.find_children("*","MeshInstance3D",true,false):
		if not (n.name.begins_with("Shield_L_Cell") or n.name.begins_with("Shield_R_Cell")):continue
		for s in n.mesh.get_surface_count():
			var original: Material=n.get_active_material(s)
			if not original is StandardMaterial3D:continue
			var copy:=original.duplicate() as StandardMaterial3D
			n.set_surface_override_material(s,copy)
			cell_materials.append([copy,copy.emission_enabled,copy.emission,copy.emission_energy_multiplier])
func mat(color: Color) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new()
	m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color=color
	m.cull_mode=BaseMaterial3D.CULL_DISABLED
	return m
func hex_mesh(radius: float, width: float) -> ImmediateMesh:
	var im:=ImmediateMesh.new()
	im.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in 6:
		var a:=TAU*i/6.0
		var b:=TAU*(i+1)/6.0
		var p:=Vector3(cos(a),0,sin(a))
		var q:=Vector3(cos(b),0,sin(b))
		for v in [p*radius,q*radius,p*(radius-width),q*radius,q*(radius-width),p*(radius-width)]:im.surface_add_vertex(v)
	im.surface_end()
	return im
func outline(at: Vector3, radius: float, width: float, color: Color, life: float, normal:=Vector3.UP) -> MeshInstance3D:
	var node:=MeshInstance3D.new()
	node.mesh=hex_mesh(radius,width)
	var m:=mat(color)
	node.material_override=m
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.global_position=at
	node.quaternion=Quaternion(Vector3.UP,normal.normalized())
	transient.append(node)
	var tw:=node.create_tween().set_parallel()
	tw.tween_property(m,"albedo_color:a",0.0,life)
	tw.tween_property(node,"scale",Vector3.ONE*1.15,life)
	tw.chain().tween_callback(node.queue_free)
	return node
func aura(parent: Node3D, radius: float) -> Node3D:
	var node:=MeshInstance3D.new()
	node.mesh=hex_mesh(radius,.014)
	node.material_override=mat(Color(.45,.75,.2,.045))
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(node)
	node.position.y=.025
	node.visible=enabled
	persistent.append(node)
	return node
func cells(seconds:=.22) -> void:
	if enabled:pulse_left=maxf(pulse_left,seconds)
func pulse(at: Vector3, radius: float, life: float) -> void:
	if not enabled:return
	outline(at+Vector3.UP*.025,radius,.025,Color(.58,1,.16,.42),life)
func chips(at: Vector3, normal: Vector3, count: int, strong: bool) -> void:
	for i in count:
		var node:=MeshInstance3D.new()
		var shape:=PrismMesh.new()
		shape.size=Vector3(.022,.035,.015)*(1.4 if strong else 1.0)
		node.mesh=shape
		var m:=mat(STEEL if i%2==0 else Color(.65,1,.14,.8))
		node.material_override=m
		node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(node)
		node.global_position=at
		transient.append(node)
		var angle:=TAU*i/maxi(1,count)
		var direction: Vector3=(normal*.65+Vector3(cos(angle)*.5,.4+float(i%3)*.1,sin(angle)*.5)).normalized()
		var tw:=node.create_tween().set_parallel()
		tw.tween_property(node,"global_position",at+direction*(.25 if strong else .13),.18 if strong else .12)
		tw.tween_property(m,"albedo_color:a",0.0,.22 if strong else .14)
		tw.chain().tween_callback(node.queue_free)
func contact(at: Vector3, normal: Vector3, strong:=false) -> void:
	if not enabled:return
	log_rows.append({"kind":"contact","position":at,"strong":strong})
	outline(at,.22 if strong else .12,.018,Color(.7,1,.35,.8),.20 if strong else .11,normal)
	chips(at,normal,8 if strong else 4,strong)
func ground(at: Vector3, size:=.6) -> void:
	if not enabled:return
	log_rows.append({"kind":"ground","position":at})
	outline(Vector3(at.x,.035,at.z),size,.028,Color(.60,1,.18,.65),.25)
	chips(at+Vector3.UP*.05,Vector3.UP,8,true)
func telegraph(at: Vector3, radius: float) -> Node3D:
	if not enabled:return null
	var node:=outline(at+Vector3.UP*.03,radius,.035,Color(.45,.9,.18,.40),1.0)
	return node
func clear_transient() -> void:
	for n in transient:
		if is_instance_valid(n):n.queue_free()
	transient.clear()
	pulse_left=0
func set_enabled(value: bool) -> void:
	enabled=value
	if not value:
		clear_transient()
		cell_weight=0
	for n in persistent:
		if is_instance_valid(n):n.visible=value
func _process(delta: float) -> void:
	pulse_left=maxf(0,pulse_left-delta)
	cell_weight=move_toward(cell_weight,1.0 if enabled and pulse_left>0 else 0.0,delta*14)
	for row in cell_materials:
		var m: StandardMaterial3D=row[0]
		m.emission_enabled=bool(row[1]) or cell_weight>.001
		m.emission=(row[2] as Color).lerp(Color(.5,1,.1),cell_weight*.7)
		m.emission_energy_multiplier=lerpf(float(row[3]),1.3,cell_weight)
	transient=transient.filter(func(n):return is_instance_valid(n))
