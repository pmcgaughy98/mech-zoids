extends SceneTree
const OUT := "D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/rhino-generated/"
const SOURCE := "D:/dev/_scratch/mech-art-direction/rhino-generated/source.glb"
var vp: SubViewport
var arena: Node3D
var model: Node3D
var cam: Camera3D
var surfaces: Array = []
var records: Array = []

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
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(SOURCE,state)
	if err != OK:
		push_error("Cannot read isolated rhino: %s" % err)
		quit(1)
		return
	model = doc.generate_scene(state)
	p.add_child(model)
	# Source is approximately 0.719 m tall after its authored node rotation.
	# Uniform test scale gives a 2 m large-mech height, not an approved production scale.
	model.scale = Vector3.ONE * (2.0 / 0.719021976)
	var players := model.find_children("*","AnimationPlayer",true,false)
	if not players.is_empty():
		var ap: AnimationPlayer = players[0]
		ap.play("idle")
		ap.seek(0,true)
		ap.pause()
	for mi in model.find_children("*","MeshInstance3D",true,false):
		for i in mi.mesh.get_surface_count():
			surfaces.append({"mesh":mi,"index":i,"original":mi.get_active_material(i)})
	cam = arena.get_node("Camera")
	cam.target = p
	cam.yaw_degrees = 0.0
	cam.snap()
	RenderingServer.global_shader_parameter_set("machine_pos",p.global_position)
	RenderingServer.global_shader_parameter_set("machine_hidden",0.0)
	for resolution in [Vector2i(1280,720),Vector2i(320,180)]:
		vp.size = resolution
		for distance in [0.0,8.0]:
			for angle in [0.0,45.0,135.0,180.0]:
				if distance > 0 and angle != 135.0:
					continue
				model.position.z = -distance
				model.rotation_degrees.y = angle
				for variant in ["A-original","B-satin","C-graphic"]:
					_apply(variant)
					for n in 8:
						await process_frame
					await RenderingServer.frame_post_draw
					var stem := "%s-%dx%d-y%d-d%d" % [variant,resolution.x,resolution.y,int(angle),int(distance)]
					var im := vp.get_texture().get_image()
					im.save_png(OUT+stem+".png")
					records.append({"file":stem+".png","resolution":[resolution.x,resolution.y],"model_yaw":angle,"extra_distance":distance,"variant":variant,"camera":str(cam.global_transform),"fov":cam.fov})
					print("SAVED ",stem)
	var f := FileAccess.open(OUT+"capture-manifest.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"arena":"scenes/moba3d/arena_blockout.tscn","theme":arena.theme,"position":str(p.global_position),"pose":"source static mesh", "test_height_m":2.0, "scale_approved":false,"fog_of_war":false,"minimap":false,"geometry_changed":false, "normal_map_available":true, "body_materials":1,"captures":records},"  "))
	print("PILOT COMPLETE ",records.size()," captures")
	quit()

func _apply(variant: String) -> void:
	for s in surfaces:
		var original: StandardMaterial3D = s.original
		if variant == "A-original":
			s.mesh.set_surface_override_material(s.index,original)
			continue
		if original.albedo_texture == null:
			var eye := original.duplicate() as StandardMaterial3D
			eye.emission_energy_multiplier = 1.3 if variant == "B-satin" else 0.8
			s.mesh.set_surface_override_material(s.index,eye)
			continue
		var mat := ShaderMaterial.new()
		var shader := Shader.new()
		shader.code = SHADER.replace("MODE", "diffuse_burley,specular_schlick_ggx" if variant == "B-satin" else "diffuse_toon,specular_toon")
		mat.shader = shader
		mat.set_shader_parameter("base_map",original.albedo_texture)
		mat.set_shader_parameter("normal_map",original.normal_texture)
		mat.set_shader_parameter("orm_map",original.roughness_texture)
		mat.set_shader_parameter("graphic",variant == "C-graphic")
		s.mesh.set_surface_override_material(s.index,mat)

const SHADER := """
shader_type spatial;
render_mode MODE,cull_disabled;
uniform sampler2D base_map: source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D normal_map: hint_normal,filter_linear_mipmap_anisotropic;
uniform sampler2D orm_map: filter_linear_mipmap_anisotropic;
uniform bool graphic = false;
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
}
"""
