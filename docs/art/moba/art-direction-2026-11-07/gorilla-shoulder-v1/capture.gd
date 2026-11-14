extends SceneTree
const OUT := "D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-shoulder-v1/"
const SOURCE := "D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-optimization-v1/gorilla-source.glb"
var vp: SubViewport
var arena: Node3D
var model: Node3D
var cam: Camera3D
var surfaces: Array = []
var records: Array = []
var material_cache := {}
var maskvp: SubViewport
var maskcam: Camera3D
var maskmodel: Node3D

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	DisplayServer.window_set_size(Vector2i(640,360))
	vp = SubViewport.new()
	vp.size = Vector2i(1280,720)
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(vp)
	arena = load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	arena.minimap = false
	arena.fog_of_war = false
	vp.add_child(arena)
	await process_frame
	arena.process_mode = Node.PROCESS_MODE_DISABLED
	var p: Node3D = arena.get_node("Player")
	p.position = Vector3(0,0,8)
	for child in p.get_children():
		if child is VisualInstance3D:
			child.hide()
	cam = arena.get_node("Camera")
	cam.target = p
	cam.yaw_degrees = 0.0
	cam.snap()
	RenderingServer.global_shader_parameter_set("machine_pos",p.global_position)
	RenderingServer.global_shader_parameter_set("machine_hidden",0.0)
	maskvp = SubViewport.new()
	maskvp.size = vp.size
	maskvp.own_world_3d = true
	maskvp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(maskvp)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color.BLACK
	maskvp.add_child(env)
	maskcam = Camera3D.new()
	maskcam.transform = cam.global_transform
	maskcam.fov = cam.fov
	maskvp.add_child(maskcam)
	maskcam.current = true
	var variants := {
		"reference":"D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-cleanup-v1/gorilla-connected-100k-2k.glb",
		"rest":OUT+"shoulder-rest-2k.glb",
		"reach":OUT+"shoulder-reach-2k.glb"
	}
	for variant in variants:
		model = _load_model(variants[variant])
		if model == null:
			quit(1)
			return
		p.add_child(model)
		model.scale = Vector3.ONE*(2.0/0.719021976)
		_apply_refined(model)
		maskmodel = _load_model(variants[variant])
		maskvp.add_child(maskmodel)
		maskmodel.scale = model.scale
		var white := StandardMaterial3D.new()
		white.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		white.albedo_color = Color.WHITE
		white.cull_mode = BaseMaterial3D.CULL_DISABLED
		for mi in maskmodel.find_children("*","MeshInstance3D",true,false):
			mi.material_override = white
		for shot in [{"yaw":0.0,"d":0.0},{"yaw":-45.0,"d":0.0},{"yaw":-90.0,"d":0.0},{"yaw":180.0,"d":0.0},{"yaw":-45.0,"d":8.0}]:
			model.position.z = -shot.d
			model.rotation_degrees.y = shot.yaw
			maskmodel.transform = model.global_transform
			for n in 5:
				await process_frame
			await RenderingServer.frame_post_draw
			var name := "%s-y%d-d%d" % [variant,int(shot.yaw),int(shot.d)]
			vp.get_texture().get_image().save_png(OUT+name+".png")
			maskvp.get_texture().get_image().save_png(OUT+name+"-mask.png")
			records.append({"name":name,"variant":variant,"file":variants[variant],"yaw":shot.yaw,"extra_distance":shot.d,"camera":str(cam.global_transform),"size":str(vp.size)})
			print("CAPTURED ",name)
		model.queue_free()
		maskmodel.queue_free()
		await process_frame
	var manifest := FileAccess.open(OUT+"capture-manifest.json",FileAccess.WRITE)
	manifest.store_string(JSON.stringify({"material":"refined D, same shader and input parameters on every variant","test_height_m":2.0,"arena":"foundry","fov":60.0,"pitch":30.0,"distance":6.5,"captures":records},"  "))
	print("OPTIMIZATION CAPTURE COMPLETE ",records.size())
	quit()

func _load_model(path: String) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(path,state) != OK:
		push_error("Cannot load "+path)
		return null
	return doc.generate_scene(state)

func _apply_refined(node: Node3D) -> void:
	var shader := Shader.new()
	shader.code = SHADER
	for mi in node.find_children("*","MeshInstance3D",true,false):
		for i in mi.mesh.get_surface_count():
			var original: StandardMaterial3D = mi.get_active_material(i)
			if original.albedo_texture == null:
				continue
			var mat := ShaderMaterial.new()
			mat.shader = shader
			mat.set_shader_parameter("base_map",original.albedo_texture)
			mat.set_shader_parameter("normal_map",original.normal_texture)
			mat.set_shader_parameter("orm_map",original.roughness_texture)
			mat.set_shader_parameter("refined",true)
			mat.set_shader_parameter("graphic",false)
			mi.set_surface_override_material(i,mat)

const SHADER := """

shader_type spatial;
render_mode diffuse_toon,specular_schlick_ggx,cull_disabled;
uniform sampler2D base_map: source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D normal_map: hint_normal,filter_linear_mipmap_anisotropic;
uniform sampler2D orm_map: filter_linear_mipmap_anisotropic;
uniform bool graphic = false;
uniform bool refined = false;
void fragment(){
 vec3 c=texture(base_map,UV).rgb;
 vec3 orm=texture(orm_map,UV).rgb;
 // Color masks are provisional. They are not authored material IDs.
 float coat=smoothstep(1.10,1.55,c.g/max(c.r,0.004))*smoothstep(1.15,1.6,c.b/max(c.r,0.004));
 float power=smoothstep(1.1,1.5,c.g/max(c.r,0.004))*smoothstep(2.0,3.5,c.r/max(c.b,0.004))*smoothstep(0.15,0.4,c.g);
 ALBEDO=mix(c*1.06,c*1.16,coat);
 METALLIC=mix(clamp(orm.b,0.55,0.85),0.15,coat);
 ROUGHNESS=mix(clamp(orm.g,0.32,0.62),0.55,coat);
 NORMAL_MAP=texture(normal_map,UV).rgb;
 NORMAL_MAP_DEPTH=0.55;
 EMISSION=c*power*0.22;
 if(graphic){
   ALBEDO=c*1.20;
   METALLIC=0.08;
   ROUGHNESS=0.75;
   NORMAL_MAP_DEPTH=0.22;
   RIM=0.14;
   RIM_TINT=0.6;
 }
 if(refined){
   float mx=max(c.r,max(c.g,c.b));
   float mn=min(c.r,min(c.g,c.b));
   float neutral=1.0-smoothstep(0.12,0.32,(mx-mn)/max(mx,0.004));
   float steel=neutral*smoothstep(0.05,0.2,mx);
   float mechanism=neutral*(1.0-smoothstep(0.06,0.18,mx));
   ALBEDO=c*mix(1.13,0.72,power);
   ALBEDO*=mix(1.0,0.87,mechanism);
   METALLIC=mix(0.12,0.78,steel);
   METALLIC=mix(METALLIC,0.42,mechanism);
   ROUGHNESS=mix(0.64,0.36,steel);
   ROUGHNESS=mix(ROUGHNESS,0.7,mechanism);
   NORMAL_MAP_DEPTH=0.38;
   EMISSION=c*power*0.12;
   RIM=0.075;
   RIM_TINT=0.55;
 }

}
"""
