extends SceneTree
const OUT := "D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-cleanup-v1/"
const SOURCE := "D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-cleanup-v1/gorilla-connected-100k-2k.glb"
var vp: SubViewport
var arena: Node3D
var model: Node3D
var cam: Camera3D
var surfaces: Array = []
var records: Array = []
var material_cache := {}

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
		push_error("Cannot read current gorilla: %s" % err)
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
	if true:
		root.content_scale_size = Vector2i.ZERO
		DisplayServer.window_set_size(Vector2i(1280,720))
		var screen := TextureRect.new()
		screen.texture = vp.get_texture()
		screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		screen.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		root.add_child(screen)
		var label := Label.new()
		label.text = "GORILLA CLEANUP   1 Source   2 Selected 100k   3 Connected cleanup 100k   Left/Right Turn   Up/Down Distance   Esc Quit"
		label.position = Vector2(16,16)
		label.add_theme_font_size_override("font_size",18)
		root.add_child(label)
		var input_script := GDScript.new()
		input_script.source_code = """extends Node
var pilot
func _unhandled_key_input(event: InputEvent) -> void:
	pilot._handle_key(event)
"""
		input_script.reload()
		var input_node := Node.new()
		input_node.set_script(input_script)
		input_node.pilot = self
		root.add_child(input_node)
		model.rotation_degrees.y = 45.0
		_apply("D-refined")
		if "--preview-check" in OS.get_cmdline_user_args():
			_verify_preview.call_deferred()
		return

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
		var cache_key := variant + str(s.index)
		if material_cache.has(cache_key):
			s.mesh.set_surface_override_material(s.index,material_cache[cache_key])
			continue
		var mat := ShaderMaterial.new()
		var shader := Shader.new()
		shader.code = SHADER.replace("MODE", "diffuse_toon,specular_schlick_ggx" if variant == "D-refined" else "diffuse_toon,specular_toon")
		mat.shader = shader
		mat.set_shader_parameter("base_map",original.albedo_texture)
		mat.set_shader_parameter("normal_map",original.normal_texture)
		mat.set_shader_parameter("orm_map",original.roughness_texture)
		mat.set_shader_parameter("graphic",variant == "C-graphic")
		mat.set_shader_parameter("refined",variant == "D-refined")
		material_cache[cache_key] = mat
		s.mesh.set_surface_override_material(s.index,mat)

const SHADER := """
shader_type spatial;
render_mode MODE,cull_disabled;
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

func _verify_preview() -> void:
	for n in 10:
		await process_frame
	var original_yaw := model.rotation_degrees.y
	for code in [KEY_1,KEY_2,KEY_3,KEY_RIGHT]:
		var key := InputEventKey.new()
		key.keycode = code
		key.pressed = true
		Input.parse_input_event(key)
		await process_frame
		key = InputEventKey.new()
		key.keycode = code
		key.pressed = false
		Input.parse_input_event(key)
		await process_frame
	if absf(model.rotation_degrees.y-original_yaw-15.0) > 0.01:
		push_error("Preview keyboard rotation did not reach the input handler")
		quit(1)
		return
	model.rotation_degrees.y = original_yaw
	_swap(OUT+"gorilla-connected-100k-2k.glb")
	for n in 5:
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OUT+"interactive-preview.png")
	print("PREVIEW VERIFIED ",root.get_texture().get_size())
	quit()

func _handle_key(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed:
		return
	match event.keycode:
		KEY_ESCAPE: quit()
		KEY_1: _swap("D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-polish-v1/gorilla-source.glb")
		KEY_2: _swap("D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-optimization-v1/gorilla-100k-2k.glb")
		KEY_3: _swap(OUT+"gorilla-connected-100k-2k.glb")
		KEY_LEFT: model.rotation_degrees.y -= 15.0
		KEY_RIGHT: model.rotation_degrees.y += 15.0
		KEY_UP: model.position.z = maxf(-12.0,model.position.z-1.0)
		KEY_DOWN: model.position.z = minf(0.0,model.position.z+1.0)

func _swap(path: String) -> void:
	var previous_transform := model.transform
	var parent := model.get_parent()
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(path,state) != OK:
		push_error("Cannot load "+path)
		return
	parent.remove_child(model)
	model.queue_free()
	model = doc.generate_scene(state)
	parent.add_child(model)
	model.transform = previous_transform
	surfaces.clear()
	material_cache.clear()
	for mi in model.find_children("*","MeshInstance3D",true,false):
		for i in mi.mesh.get_surface_count():
			surfaces.append({"mesh":mi,"index":i,"original":mi.get_active_material(i)})
	_apply("D-refined")
	print("PREVIEW MODEL ",path)
